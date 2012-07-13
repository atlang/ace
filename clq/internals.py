import ast as _ast # http://docs.python.org/library/ast.html
import clq
import cypy
import cypy.astx as astx

from clq import (InvalidOperationError, TypeResolutionError, Context)

class GenericFnVisitor(_ast.NodeVisitor):
    """A visitor that produces a copy of a generic function's abstract syntax 
    tree annotated with the following additional information:
    
    - :class:`unresolved types <UnresolvedType>` for each expression (in the 
      ``unresolved_type`` attribute)
    - maps from variable names to their unresolved types
    
    """
    def __init__(self):
        self.all_variables = { }
        """variable name => unresolved type"""
        
        self.arguments = { }
        """argument name => unresolved type"""
        
        self.local_variables = { }        
        """local variable name => unresolved type"""
        
        self.free_variables = { }
        """free variable name => unresolved type"""
        
        self.return_type = None
        """The unresolved return type of this function"""
        
        # used internally to prevent nested function declarations
        self._in_function = False
    
    def generic_visit(self, node):
        raise InvalidOperationError(
            "Unsupported operation: " + type(node).__name__, node)
        
    ######################################################################
    ## Statements
    ######################################################################
    def visit_FunctionDef(self, node):
        # can't nest functions
        if self._in_function:
            raise InvalidOperationError(
                "Nested function definitions are not supported.", node)
        self._in_function = True
        
        # do all the work
        self.return_type = None
        args = self.visit(node.args)
        body = [ self.visit(stmt) for stmt in node.body ]
        if self.return_type is None:
            self.return_type = VoidURT(node)
        
        # return a copy of the root node with all the information as 
        # attributes
        return astx.copy_node(node, 
            name=node.name,
            args=args,
            body=body,
            decorator_list=[],
            return_type=self.return_type,
            all_variables=cypy.frozendict(self.all_variables),
            arguments=cypy.frozendict(self.arguments),
            local_variables=cypy.frozendict(self.local_variables),
            free_variables=cypy.frozendict(self.free_variables)
        )
    
    def visit_arguments(self, node):
        # check for invalid arguments
        if node.vararg is not None:
            raise InvalidOperationError(
                "Variable arguments are not supported.", node)
        if node.kwarg is not None:
            raise InvalidOperationError(
                "Keyword arguments are not supported.", node)

        args = [self.visit(arg) for arg in node.args if arg is not None]
        return _ast.arguments(
            args=args, 
            vararg=None, 
            kwarg=None, 
            defaults=[]
        )
    
    def visit_Return(self, node):
        value = node.value
        if value is None:
            return_type = VoidURT()
        else:
            value = self.visit(value)
            return_type = value.unresolved_type
            
        cur_return_type = self.return_type
        if cur_return_type is None:
            self.return_type = return_type
        else:
            # can think of the return value as just another value that
            # is being assigned to implicitly.
            self.return_type = MultipleAssignmentURT(cur_return_type, 
                                                     return_type, node)
        
        return astx.copy_node(node, 
            value=value
        )
    
    def visit_Assign(self, node):
        value = self.visit(node.value)
        # cur_assignment_type tells visit_Name about the type of the assignment
        self.cur_assignment_type = value.unresolved_type
        targets = node.targets
        if len(targets) != 1:
            raise InvalidOperationError("Multiple assignment targets not supported.")
        targets = [ self.visit(targets[0]) ]
        self.cur_assignment_type = None
        
        return astx.copy_node(node,
            targets=targets,
            value=value
        )
    
    def visit_AugAssign(self, node):
        target = node.target
        op = node.op
        value = node.value
        
        # We temporarily turn augmented assignments into the equivalent binary 
        # operation to determine the unresolved type.
        orig_ctx = target.ctx 
        target.ctx = _ast.Load()
        tmp_binop = self.visit(_ast.BinOp(left=target, 
                                          op=op, 
                                          right=value))
        target.ctx = orig_ctx
        
        # visit the target
        # see visit_Assign
        self.cur_assignment_type = tmp_binop.unresolved_type
        target = self.visit(target)
        self.cur_assignment_type = None
        
        return astx.copy_node(node,
            target=tmp_binop.left,
            op=tmp_binop.op,
            value=tmp_binop.right
        )
        
    def visit_For(self, node):
        if node.orelse:
            raise InvalidOperationError(
               "else clauses on for loops are not supported.", node)
        
        # We only support the standard for x in ([start, ]stop[, step]) syntax
        # with positive step sizes.
        
        # insert missing iteration bounds if not specified
        iter = astx.deep_copy_node(node.iter)
        if isinstance(iter, _ast.Tuple):
            elts = iter.elts
            n_elts = len(elts)
            if n_elts == 1:
                start = _ast.Num(n=0)
                stop = elts[0]
                step = _ast.Num(n=1)
            elif n_elts == 2:
                start = elts[0]
                stop = elts[1]
                step = _ast.Num(n=1)
            elif n_elts == 3:
                start = elts[0]
                stop = elts[1]
                step = elts[2]
            else:
                raise InvalidOperationError(
                   "Invalid number of elements specified in for-loop index.", node)
        else:
            start = _ast.Num(n=0)
            stop = iter
            step = _ast.Num(n=1)
        
        # visit target
        target = node.target
        if not isinstance(target, _ast.Name):
            raise InvalidOperationError(
                "Invalid target -- only named variables are supported.")
            
        target = astx.copy_node(target)
        init = self.visit(_ast.Assign(targets=[target], value=start))
        
        # to create the guard operation, we need a Load version of the target
        target_load = astx.copy_node(target, ctx=_ast.Load())
        guard = self.visit(_ast.Compare(left=target_load, comparators=[stop], 
                                        ops=[_ast.Lt()]))
        
        # Create an update statement
        update_stmt = self.visit(
            _ast.AugAssign(
                target=target, 
                op=_ast.Add(), 
                value=step
            )
        )
        
        return astx.copy_node(node,
            target=target,
            iter=iter,
            body=[self.visit(stmt) for stmt in node.body],
            orelse=[],
            
            init=init,
            guard=guard,
            update_stmt=update_stmt
        )

    def visit_While(self, node):
        if node.orelse:
            raise InvalidOperationError(
                "else clauses on while loops are not supported.", node)
        
        return astx.copy_node(node,
            test=self.visit(node.test),
            body=[self.visit(stmt) for stmt in node.body],
            orelse=[]
        )
    
    def visit_If(self, node):
        return astx.copy_node(node,
            test=self.visit(node.test),
            body=[self.visit(stmt) for stmt in node.body],
            orelse=[self.visit(stmt) for stmt in node.orelse]
        )
    
    def visit_Expr(self, node):
        return astx.copy_node(node,
            value=self.visit(node.value)
        )
    
    def visit_Pass(self, node):
        return astx.copy_node(node)
    
    def visit_Break(self, node):
        return astx.copy_node(node)
    
    def visit_Continue(self, node):
        return astx.copy_node(node)
    
    def visit_Exec(self, node):
        if node.globals:
            raise InvalidOperationError(
                "Cannot specify globals with `exec`.", node.globals[0])
        if node.locals:
            raise InvalidOperationError(
                "Cannot specify locals with `exec`.", node.locals[0])
            
        return astx.copy_node(node,
            globals=None,
            locals=None
        )
    
    ######################################################################
    ## Supported Operators
    ######################################################################
    def _visit_op(self, node):
        # all operators are just copied directly
        return astx.copy_node(node)
    
    visit_Add = _visit_op
    visit_Sub = _visit_op
    visit_Mult = _visit_op
    visit_Div = _visit_op
    visit_Pow = _visit_op
    visit_LShift = _visit_op
    visit_RShift = _visit_op
    visit_BitOr = _visit_op
    visit_BitXor = _visit_op
    visit_BitAnd = _visit_op
    visit_FloorDiv = _visit_op
    visit_BitAnd = _visit_op
    visit_Invert = _visit_op
    visit_Not = _visit_op
    visit_UAdd = _visit_op
    visit_USub = _visit_op
    visit_Eq = _visit_op
    visit_NotEq = _visit_op
    visit_Lt = _visit_op
    visit_LtE = _visit_op
    visit_Gt = _visit_op
    visit_GtE = _visit_op
    visit_And = _visit_op
    visit_Or = _visit_op
    
    ######################################################################
    ## Operator Expressions
    ######################################################################                
    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op = self.visit(node.op)
        
        new_node = astx.copy_node(node,
            op=op,
            operand=operand)
        new_node.unresolved_type = UnaryOpURT(new_node)
        return new_node
    
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        op = self.visit(node.op)
        right = self.visit(node.right)
        
        new_node = astx.copy_node(node,
            left=left,
            op=op,
            right=right)
        new_node.unresolved_type = BinOpURT(new_node)
        return new_node
    
    def visit_BoolOp(self, node):
        op = self.visit(node.op)
        values = [self.visit(expr) for expr in node.values]
        
        new_node = astx.copy_node(node,
            op=op,
            values=values)
        new_node.unresolved_type = BoolOpURT(new_node)
        return new_node  
    
    def visit_Compare(self, node):
        comparators = node.comparators
        if len(comparators) != 1:
            raise InvalidOperationError(
                "Chained comparators are not supported.", node)
            
        left = self.visit(node.left)
        ops = [self.visit(node.ops[0])]
        comparators = [self.visit(comparators[0])]
            
        new_node = astx.copy_node(node,
            left=left,
            ops=ops,
            comparators=comparators)
        new_node.unresolved_type=CompareURT(new_node)
        return new_node

    ######################################################################
    ## Other Expressions
    ######################################################################                
    def visit_IfExp(self, node):
        test = self.visit(node.test)
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)
        
        new_node = astx.copy_node(node,
            test=test,
            body=body,
            orelse=orelse)
        new_node.unresolved_type=MultipleAssignmentURT(body.unresolved_type, 
                                                       orelse.unresolved_type, 
                                                       new_node)
        return new_node

    def visit_Call(self, node):                                                     
        if node.keywords:
            raise InvalidOperationError(
                "Keyword arguments in concrete_fn calls are not supported.", node)
        if node.starargs:
            raise InvalidOperationError(
                "Starred arguments in concrete_fn calls are not supported.", node)
        if node.kwargs:
            raise InvalidOperationError(
                "kwargs in concrete_fn calls are not supported.", node)
        
        func = self.visit(node.func)        
        args = [ self.visit(arg) for arg in node.args ]
        
        new_node = astx.copy_node(node,
            func=func, 
            args=args, 
            keywords=[], 
            starargs=None, 
            kwargs=None)
        new_node.unresolved_type = CallURT(new_node)
        return new_node
    
    def visit_Attribute(self, node):
        value = self.visit(node.value)
        ctx = self.visit(node.ctx)
        
        new_node = astx.copy_node(node,
            value=value, 
            attr=node.attr, 
            ctx=ctx)
        new_node.unresolved_type=AttributeURT(new_node)
        return new_node
    
    def visit_Subscript(self, node):
        value = self.visit(node.value)
        slice = self.visit(node.slice)
        ctx = self.visit(node.ctx)
        
        new_node = astx.copy_node(node,
            value=value, 
            slice=slice, 
            ctx=ctx)
        new_node.unresolved_type=SubscriptURT(new_node)
        return new_node
    
    def visit_Ellipsis(self, node):
        # here in case a custom type wants to support it
        return astx.copy_node(node)
    
    def visit_Slice(self, node):
        # here in case a custom type wants to support it
        lower = node.lower
        if lower is not None:
            lower = self.visit(lower)
            
        upper = node.upper
        if upper is not None:
            upper = self.visit(upper)
            
        step = node.step
        if step is not None:
            step = self.visit(step)
            
        return astx.copy_node(node,
            lower=lower,
            upper=upper,
            step=step
        )
    
    def visit_ExtSlice(self, node):
        dims = node.dims
        if dims:
            dims = [self.visit(dim) for dim in dims]
            
        return astx.copy_node(node, 
            dims=dims
        )
    
    def visit_Index(self, node):
        value = self.visit(node.value)
        
        new_node = astx.copy_node(node,
            value=value)
        new_node.unresolved_type=value.unresolved_type
        return new_node
        
    def visit_Load(self, node):
        return astx.copy_node(node)
    
    def visit_Store(self, node):
        return astx.copy_node(node)
    
    def visit_Param(self, node):
        return astx.copy_node(node)
    
    def visit_Name(self, node):
        id = node.id
        ctx = self.visit(node.ctx)
        ctx_t = type(ctx)
        name = astx.copy_node(node,
            ctx=ctx
        )
        unresolved_type = NameURT(name)
        name.unresolved_type = unresolved_type
        
        if ctx_t is _ast.Load:
            if id not in self.all_variables:
                # new free variable
                self.all_variables[id] = self.free_variables[id] = \
                    unresolved_type
                
        elif ctx_t is _ast.Store:
            try:
                current_type = self.all_variables[id]
            except KeyError:
                # new local variable
                self.all_variables[id] = self.local_variables[id] = \
                    self.cur_assignment_type                     
                
            else:
                if id in self.local_variables:
                    # multiple assignment of a local variable
                    self.local_variables[id] = MultipleAssignmentURT(
                        current_type, self.cur_assignment_type, name)
                elif id in self.free_variables:
                    raise InvalidOperationError(
                        "Free variables cannot be assigned to.", node)
                else:
                    # assignments are ok to params but won't change their type
                    pass
        
        elif ctx_t is _ast.Param:
            # TODO: rename 'arguments' in documentation to 'parameters' to
            # be consistent with Python usage (check this)
            self.all_variables[id] = self.arguments[id] = \
                unresolved_type
            
        return name
        
    def visit_Num(self, node):
        new_node = astx.copy_node(node)
        new_node.unresolved_type = NumURT(node)
        return new_node
    
    def visit_Str(self, node):
        new_node = astx.copy_node(node)
        new_node.unresolved_type = StrURT(node)
        return new_node
    
##############################################################################
## Unresolved Types
##############################################################################
class UnresolvedType(object):
    """Abstract base class for unresolved types."""
    def __init__(self, node):
        self.node = node

class VoidURT(UnresolvedType):
    """Represents the void return type."""
    def __str__(self):
        return "<void>"
    
    def __repr__(self):
        return "Void()"
    
    @cypy.memoize
    def resolve(self, context):
        return context.backend.void_type(context, self.node)

class NumURT(UnresolvedType):
    """Represents the unresolved type of a numeric literal."""
    def __str__(self):
        return self.node.n
    
    def __repr__(self):
        return "Num(%s)" % str(self.node.n)
    
    @cypy.memoize
    def resolve(self, context):
        return context.backend.resolve_Num(context, self.node)
    
class StrURT(UnresolvedType):
    """Represents the unresolved type of a string literal."""
    def __str__(self):
        return '"' + self.node.s + '"'
    
    def __repr__(self):
        return "Str('''%s''')" % self.node.s
    
    @cypy.memoize
    def resolve(self, context):
        return context.backend.resolve_Str(context, self.node)
    
class AttributeURT(UnresolvedType):
    """The unresolved type of attribute expressions."""
    def __str__(self):
        node = self.node
        return "%s.%s" % (str(node.value.unresolved_type), node.attr)
    
    def __repr__(self):
        node = self.node
        return "Attribute(%s, %s)" % (repr(node.value.unresolved_type),
                                      node.attr)
    
    @cypy.memoize
    def resolve(self, context):
        node = self.node
        value_type = node.value.unresolved_type.resolve(context)            
        return value_type.resolve_Attribute(context, node)

class SubscriptURT(UnresolvedType):
    """The unresolved type of subscript expressions."""
    def __str__(self):
        node = self.node
        return "%s[%s]" % (str(node.value.unresolved_type), 
                           str(node.slice.unresolved_type))
        
    def __repr__(self):
        node = self.node
        return "Subscript(%s, %s)" % (repr(node.value.unresolved_type),
                                      repr(node.slice.unresolved_type))
        
    @cypy.memoize
    def resolve(self, context):
        node = self.node
        value_type = node.value.unresolved_type.resolve(context)
        return value_type.resolve_Subscript(context, node)
    
class UnaryOpURT(UnresolvedType):
    """The unresolved type of unary operator expressions."""
    def __str__(self):
        node = self.node
        return "(%s %s)" % (astx.all_operators[type(node.op)], 
                            str(node.operand.unresolved_type))
    
    def __repr__(self):
        node = self.node
        return "UnaryOp(%s, %s)" % (type(node.op).__name__,
                                      repr(node.operand.unresolved_type))
        
    @cypy.memoize
    def resolve(self, context):
        node = self.node
        operand_type = node.operand.unresolved_type.resolve(context)
        return operand_type.resolve_UnaryOp(context, node)
    
class BinOpURT(UnresolvedType):
    """The unresolved type of binary operator expressions."""
    def __str__(self):
        node = self.node
        return "(%s %s %s)" % (astx.all_operators[type(node.op)], 
                               str(node.left.unresolved_type), 
                               str(node.right.unresolved_type))
        
    def __repr__(self):
        node = self.node
        return "BinOp(%s, %s, %s)" % (repr(node.left.unresolved_type),
                                        type(node.op).__name__,
                                        repr(node.right.unresolved_type))
        
    @cypy.memoize
    def resolve(self, context):
        node = self.node
        left_type = node.left.unresolved_type.resolve(context)
        return left_type.resolve_BinOp(context, node)

class CompareURT(UnresolvedType):
    """The unresolved type of comparison operations."""
    def __str__(self):
        node = self.node
        return "(%s %s %s)" % (astx.all_operators[type(node.op)],
                               str(node.left.unresolved_type),
                               str(node.comparators[0].unresolved_type))
        
    def __repr__(self):
        node = self.node
        return "Compare(%s, %s, %s)" % (repr(node.left.unresolved_type),
                                        type(node.op).__name__,
                                        repr(node.comparators[0].unresolved_type))
            
    @cypy.memoize
    def resolve(self, context):
        node = self.node
        left_type = node.left.unresolved_type.resolve(context)
        return left_type.resolve_Compare(context, node)  

class BoolOpURT(UnresolvedType):
    """The unresolved type of boolean operations."""
    def __str__(self):
        node = self.node
        return "(%s %s)" % (astx.all_operators[type(node.op)],
                            " ".join(str(value.unresolved_type) 
                                      for value in node.values))
            
    def __repr__(self):
        node = self.node
        return "BoolOp(%s, %s)" % (type(node.op).__name__,
                                   ", ".join(repr(value.unresolved_type)
                                             for value in node.values))
            
    @cypy.memoize
    def resolve(self, context):
        node = self.node
        left_type = node.values[0].unresolved_type.resolve(context)
        return left_type.resolve_BoolOp(context, node)
       
class NameURT(UnresolvedType):
    """The unresolved type of variables."""
    def __str__(self):
        return "`%s" % self.node.id
    
    def __repr__(self):
        return "Name('%s')" % self.node.id
    
    @cypy.memoize
    def resolve(self, context):
        node = self.node
        id = node.id
        
        
        # handle special cases
        if id == "cast":
            return clq.CastType("")
        
        # handle non-special cases
        try:
            # is it an argument?
            return context.concrete_fn.arg_map[id]
        except KeyError:
            # no? then it must be a local variable
            
            try:
                return context._multiple_assignment_prev[id]
            except KeyError:
                # we have to assign it a type
                try:
                    var = context.generic_fn.local_variables[id]
                except KeyError:
                    raise TypeResolutionError(
                        "Definition for name could not be found: %s." % id, node)
                
                #
                # Have to keep a stack for multiple assignments to be handled
                # correctly when they are recursive, e.g.
                #
                #    i = 0
                #    i = i + 1.0
                #
                # Here, i has unresolved type:
                #    
                #    i: 0 <=> `i + 1.0
                #
                # If we didn't keep track of what name we're currently 
                # working on, multiple assignment resolution would loop 
                # forever when it saw the nested `i term.
                #
                 
                prev_resolving_name = context._resolving_name
                context._resolving_name = id

                resolved_type = var.resolve(context)
                
                context._resolving_name = prev_resolving_name
            
                return resolved_type
        
class MultipleAssignmentURT(UnresolvedType):
    """The unresolved type of variables that have been assigned to multiple 
    times."""
    def __init__(self, prev, new, node):
        UnresolvedType.__init__(self, node)
        self.prev = prev
        self.new = new
        assert isinstance(prev, UnresolvedType)
        assert isinstance(new, UnresolvedType)
        
    def __str__(self):
        return "%s <=> %s" % (str(self.prev.unresolved_type), 
                              str(self.new.unresolved_type))
        
    def __repr__(self):
        return "MultipleAssignment(%s, %s)" % (repr(self.prev.unresolved_type),
                                               repr(self.new.unresolved_type))
        
    @cypy.memoize
    def resolve(self, context):
        prev, new, node = self.prev, self.new, self.node
        prev_type = prev.resolve(context)
        
        _resolving_name = context._resolving_name
        if _resolving_name:
            context._multiple_assignment_prev[_resolving_name] = prev_type
            
        resolved_type = prev_type.resolve_MultipleAssignment(context, prev, new, node)
        
        if _resolving_name:
            del context._multiple_assignment_prev[_resolving_name]
            
        return resolved_type
        
class CallURT(UnresolvedType):
    """The unresolved type of call expressions."""
    def __str__(self):
        node = self.node
        return "%s(%s)" % (str(node.func.unresolved_type), 
                           ", ".join(str(arg.unresolved_type) 
                                     for arg in node.args))
    
    def __repr__(self):
        node = self.node
        return "Call(%s, %s)" % (repr(node.func.unresolved_type),
                                 ", ".join(repr(arg.unresolved_type)
                                           for arg in node.args))
        
    @cypy.memoize
    def resolve(self, context):
        node = self.node
        func_type = node.func.unresolved_type.resolve(context)
        return func_type.resolve_Call(context, node)

##############################################################################
## Concrete Function Visitor
##############################################################################
class ConcreteFnVisitor(_ast.NodeVisitor):
    """A visitor that produces a copy of a cl.oquence concrete function's 
    syntax tree annotated with concrete types and code.
    
    The types are provided in the clq_type attribute and the code is provided
    in the code attribute.
    """
    def __init__(self, concrete_fn, backend):
        self.concrete_fn = concrete_fn
        self.backend = backend
        
    def visit_FunctionDef(self, node):
        # create context
        context = self.context = Context(self, self.concrete_fn, self.backend)
        
        # resolve return type
        context.return_type = node.return_type.resolve(context)
        
        # visit arguments
        args = self.visit(node.args)
        
        # visit body
        for stmt in node.body:
            self.visit(stmt)
            
        # generate program item
        program_item = context.backend.generate_program_item(context)
        context.program_item = program_item
        context.program_items.append(program_item)
        
        # return final AST
        return astx.copy_node(node,
            name=program_item.name,
            args=args,
            body=context.body,
            
            context=context
        )
        
    def visit_arguments(self, node):
        return _ast.arguments(
            args=[self.visit(arg) for arg in node.args],
            vararg=None,
            kwarg=None,
            defaults=[]
        )
    
    #########################################################################
    ## Statements
    ##########################################################################
    def visit_Return(self, node):
        context = self.context
        context.return_type.generate_Return(context, node)
        
    def visit_Assign(self, node):
        context = self.context
        target = node.targets[0]
        if isinstance(target, _ast.Name):
            target_type = target.unresolved_type.resolve(context)
            target_type.validate_Assign(context, node)
            target_type.generate_Assign(context, node)
        elif isinstance(target, _ast.Attribute):
            value_type = target.value.unresolved_type.resolve(context)
            value_type.validate_AssignAttribute(context, node)
            value_type.generate_AssignAttribute(context, node)
        elif isinstance(target, _ast.Subscript):
            value_type = target.value.unresolved_type.resolve(context)
            value_type.validate_AssignSubscript(context, node)
            value_type.generate_AssignSubscript(context, node)
        else:
            raise TypeResolutionError("Unexpected assignment target.", target)
        
    def visit_AugAssign(self, node):
        context = self.context
        target = node.target
        
        if isinstance(target, _ast.Name):
            target_type = target.unresolved_type.resolve(context)
            target_type.validate_AugAssign(context, node)
            target_type.generate_AugAssign(context, node)
        elif isinstance(target, _ast.Attribute):
            value_type = target.value.unresolved_type.resolve(context)
            value_type.validate_AugAssignAttribute(context, node)
            value_type.generate_AugAssignAttribute(context, node)
        elif isinstance(target, _ast.Subscript):
            value_type = target.value.unresolved_type.resolve(context)
            value_type.validate_AugAssignSubscript(context, node)
            value_type.generate_AugAssignSubscript(context, node)
        else:
            raise TypeResolutionError("Unexpected augmented assignment target.", 
                                      target)
        
    def visit_For(self, node):
        context = self.context
        context.backend.generate_For(context, node)
                
    def visit_While(self, node):
        context = self.context
        context.backend.generate_While(context, node)
        
    def visit_If(self, node):
        context = self.context
        context.backend.generate_If(context, node)
    
    def visit_Expr(self, node):
        context = self.context
        context.backend.generate_Expr(context, node)
        
    def visit_Pass(self, node):
        context = self.context
        context.backend.generate_Pass(context, node)

    def visit_Break(self, node):
        context = self.context
        context.backend.generate_Break(context, node)
        
    def visit_Continue(self, node):
        context = self.context
        context.backend.generate_Continue(context, node)
    
    def visit_Exec(self, node):
        context = self.context
        context.backend.generate_Exec(context, node)
    
    ######################################################################
    ## Supported Operators
    ######################################################################
    def _visit_op(self, node):
        context = self.context
        return context.backend.generate_op(context, node)
    
    visit_Add = _visit_op
    visit_Sub = _visit_op
    visit_Mult = _visit_op
    visit_Div = _visit_op
    visit_Pow = _visit_op
    visit_LShift = _visit_op
    visit_RShift = _visit_op
    visit_BitOr = _visit_op
    visit_BitXor = _visit_op
    visit_BitAnd = _visit_op
    visit_FloorDiv = _visit_op
    visit_BitAnd = _visit_op
    visit_Invert = _visit_op
    visit_Not = _visit_op
    visit_UAdd = _visit_op
    visit_USub = _visit_op
    visit_Eq = _visit_op
    visit_NotEq = _visit_op
    visit_Lt = _visit_op
    visit_LtE = _visit_op
    visit_Gt = _visit_op
    visit_GtE = _visit_op
    visit_And = _visit_op
    visit_Or = _visit_op
    
    ######################################################################
    ## Operator Expressions
    ######################################################################
    def visit_UnaryOp(self, node):
        context = self.context
        clq_type = node.unresolved_type.resolve(context)
        operand_type = node.operand.unresolved_type.resolve(context)
        new = operand_type.generate_UnaryOp(context, node)
        new.clq_type = context.observe(clq_type, node)
        return new
    
    def visit_BinOp(self, node):
        context = self.context
        clq_type = node.unresolved_type.resolve(context)
        left_type = node.left.unresolved_type.resolve(context)
        new = left_type.generate_BinOp(context, node)
        new.clq_type = context.observe(clq_type, node)
        return new
    
    def visit_Compare(self, node):
        context = self.context
        clq_type = node.unresolved_type.resolve(context)
        left_type = node.left.unresolved_type.resolve(context)
        new = left_type.generate_Compare(context, node)
        new.clq_type = context.observe(clq_type, node)
        return new
    
    def visit_BoolOp(self, node):
        context = self.context
        clq_type = node.unresolved_type.resolve(context)
        left_type = node.values[0].unresolved_type.resolve(context)
        new = left_type.generate_BoolOp(context, node)
        new.clq_type = context.observe(clq_type, node)
        return new
            
    ######################################################################
    ## Other Expressions
    ######################################################################                
    def visit_IfExp(self, node):
        context = self.context
        new = context.backend.generate_IfExp(context, node)
        clq_type = node.unresolved_type.resolve(context)
        new.clq_type = context.observe(clq_type, node)
        return new
    
    def visit_Call(self, node):
        context = self.context
        func_type = node.func.unresolved_type.resolve(context)
        new = func_type.generate_Call(context, node)
        clq_type = node.unresolved_type.resolve(context)
        new.clq_type = context.observe(clq_type, node)
        return new
    
    def visit_Attribute(self, node):
        context = self.context
        value_type = node.value.unresolved_type.resolve(context)
        new = value_type.generate_Attribute(context, node)
        clq_type = node.unresolved_type.resolve(context)
        new.clq_type = context.observe(clq_type, node)
        return new
    
    def visit_Subscript(self, node):
        context = self.context
        value_type = node.value.unresolved_type.resolve(context)
        new = value_type.generate_Subscript(context, node)
        clq_type = node.unresolved_type.resolve(context)
        new.clq_type = context.observe(clq_type, node)
        return new
    
    def visit_Index(self, node):
        value = self.visit(node.value)
        return astx.copy_node(node,
            value=value,
            code=value.code,
            clq_type=value.clq_type
        )
        
    def visit_Name(self, node):
        context = self.context
        return astx.copy_node(node,
            code=node.id,
            clq_type=context.observe(node.unresolved_type.resolve(context), node)
        )
        
    def visit_Num(self, node):
        context = self.context
        new = context.backend.generate_Num(context, node)
        clq_type = node.unresolved_type.resolve(context)
        new.clq_type = context.observe(clq_type, node)
        return new
    
    def visit_Str(self, node):
        context = self.context
        new = context.backend.generate_Str(context, node)
        clq_type = node.unresolved_type.resolve(context)
        new.clq_type = context.observe(clq_type, node)
        return new
