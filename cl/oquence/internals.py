import ast as _ast # http://docs.python.org/library/ast.html

import cypy
import cypy.cg as cg
import cypy.astx as astx
from cl.oquence import InvalidOperationError, void, is_valid_varname,\
    ConcreteTypeError, Type, Error, ProgramItem

class GenericFnVisitor(_ast.NodeVisitor):
    """A visitor that produces a copy of a cl.oquence function's syntax tree 
    annotated with additional information:
    
    - unresolved types for each expression (the ``unresolved_type`` attribute)
    - maps from variable names to their unresolved types
    """
    def __init__(self):
        # variable name => unresolved type
        self.all_variables = { }
        
        # argument name => unresolved type
        self.arguments = { }
        
        # local variable name => unresolved type
        self.local_variables = { }        
        
        # free variable name => unresolved type
        self.free_variables = { }

        # The unresolved return type of this function
        self.return_type = None
        
        # used internally to prevent nested function declarations
        self._in_function = False
    
    def generic_visit(self, n):
        raise InvalidOperationError(
            type(n).__name__ + " is an unsupported operation.", n)
        
    ######################################################################
    ## Statements
    ######################################################################
    def visit_FunctionDef(self, n):
        # can't nest functions
        if self._in_function:
            raise InvalidOperationError(
                "Inner function definitions are not supported.", n)
        self._in_function = True
        
        # do all the work
        args = self.visit(n.args)
        body = [ self.visit(stmt) for stmt in n.body ]
        return_type = self.return_type
        if return_type is None:
            return_type = void

        # return a copy of the root node with all the information as 
        # attributes
        return astx.copy_node(n, 
            name=n.name,
            args=args,
            body=body,
            return_type=return_type,
            all_variables=cypy.frozendict(self.all_variables),
            arguments=cypy.frozendict(self.arguments),
            local_variables=cypy.frozendict(self.local_variables),
            free_variables=cypy.frozendict(self.free_variables)
        )
    
    def visit_arguments(self, n):
        # check for invalid arguments
        if n.vararg is not None:
            raise InvalidOperationError(
                "Variable arguments are not supported.", n)
        if n.kwarg is not None:
            raise InvalidOperationError(
                "Keyword arguments are not supported.", n)

        # TODO: what are we flattening?
        args = cypy.flatten_once.ed([ self.visit(arg) for arg in n.args #@UndefinedVariable (ed)
                                      if arg is not None ])
        return _ast.arguments(
            args=args, 
            vararg=None, 
            kwarg=None, 
            defaults=[]
        )
    
    def visit_Return(self, n):
        value = n.value
        if value is None:
            value = None
            return_type = void
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
                                                     return_type)
        
        return astx.copy_node(n, 
            value=value
        )
    
    def visit_Assign(self, n):
        value = self.visit(n.value)
        # cur_assignment_type tells visit_Name about the type of the assignment
        self.cur_assignment_type = value.unresolved_type
        targets = n.targets
        if len(targets) != 1:
            raise InvalidOperationError("Multiple assignment targets not supported.")
        targets = [ self.visit(targets[0]) ]
        self.cur_assignment_type = None
        
        return astx.copy_node(n,
            targets=targets,
            value=value
        )
    
    def visit_AugAssign(self, n):
        target = n.target
        op = n.op
        value = n.value
        
        # We temporarily turn augmented assignments into the equivalent binary 
        # operation to determine the unresolved type.
        orig_ctx = target.ctx 
        target.ctx = _ast.Load()
        tmp_value = self.visit(_ast.BinOp(left=target, 
                                          op=op, 
                                          right=value))
        target.ctx = orig_ctx
        
        # visit the target
        # see visit_Assign
        self.cur_assignment_type = tmp_value.unresolved_type
        target = self.visit(target)
        self.cur_assignment_type = None
        
        return astx.copy_node(n,
            target=tmp_value.target,
            op=tmp_value.op,
            value=tmp_value.right
        )
        
    def visit_For(self, n):
        if n.orelse:
            raise InvalidOperationError(
               "else clauses on for loops are not supported.", n)
        
        # We only support the standard for x in ([start, ]stop[, step]) syntax
        # with positive step sizes.
        
        # insert missing iteration bounds if not specified
        iter = n.iter
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
                   "Invalid number of elements specified in for-loop index.", n)
        else:
            start = _ast.Num(n=0)
            stop = iter
            step = _ast.Num(n=1)
        
        # visit target
        target = n.target
        init = self.visit(_ast.Assign(targets=[target], value=start))
        
        # to create the guard operation, we need a Load version of the target
        target_load = astx.copy_node(target,
                                      ctx=self._Load)
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
        
        return astx.copy_node(n,
            init=init,
            guard=guard,
            update_stmt=update_stmt,
            body=[self.visit(stmt) for stmt in n.body],
            orelse=[]
        )

    def visit_While(self, n):
        if n.orelse:
            raise InvalidOperationError(
                "else clauses on while loops are not supported.", n)
        
        return astx.copy_node(n,
            test=self.visit(n.test),
            body=[self.visit(stmt) for stmt in n.body],
            orelse=[]
        )
    
    def visit_If(self, n):
        return astx.copy_node(n,
            test=self.visit(n.test),
            body=[self.visit(stmt) for stmt in n.body],
            orelse=[self.visit(stmt) for stmt in n.orelse]
        )
    
    def visit_Expr(self, n):
        return astx.copy_node(n,
            value=self.visit(n.value)
        )
    
    def visit_Pass(self, n):
        return astx.copy_node(n)
    
    def visit_Break(self, n):
        return astx.copy_node(n)
    
    def visit_Continue(self, n):
        return astx.copy_node(n)
    
    def visit_Exec(self, n):
        if n.globals:
            raise InvalidOperationError(
                "Cannot specify globals with `exec`.", n.globals[0])
        if n.locals:
            raise InvalidOperationError(
                "Cannot specify locals with `exec`.", n.locals[0])
            
        return astx.copy_node(n,
            globals=[],
            locals=[]
        )
    
    ######################################################################
    ## Supported Operators
    ######################################################################
    def _visit_op(self, n):
        # all operators are just copied directly
        return astx.copy_node(n)
    
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
    def visit_UnaryOp(self, n):
        operand = self.visit(n.operand)
        op = self.visit(n.op)
        
        return astx.copy_node(n,
            op=op,
            operand=operand,
            unresolved_type=UnaryOpURT(op, operand)
        )
    
    def visit_BinOp(self, n):
        left = self.visit(n.left)
        op = self.visit(n.op)
        right = self.visit(n.right)
        
        return astx.copy_node(n,
            left=left,
            op=op,
            right=right,
            unresolved_type=BinOpURT(op, left, right)
        )
    
    def visit_Compare(self, n):
        left = self.visit(n.left)
        ops = [self.visit(op) for op in n.ops]
        comparators = [self.visit(expr) for expr in n.comparators]
        
        return astx.copy_node(n,
            left=left,
            ops=ops,
            comparators=comparators,
            unresolved_type=CompareURT(left, ops, comparators)
        )

    def visit_BoolOp(self, n):
        op = self.visit(n.op)
        values = [self.visit(expr) for expr in n.values]
        
        return astx.copy_node(n,
            op=op,
            values=values,
            unresolved_type=BoolOpURT(op, values)  
        )
    
    ######################################################################
    ## Other Expressions
    ######################################################################                
    def visit_IfExp(self, n):
        test = self.visit(n.test)
        body = self.visit(n.body)
        orelse = self.visit(n.orelse)
        
        return astx.copy_node(n,
            test=test,
            body=body,
            orelse=orelse,
            unresolved_type=MultipleAssignmentURT(body.unresolved_type, 
                                                   orelse.unresolved_type)
        )

    def visit_Call(self, n):                                                     
        if n.keywords:
            raise InvalidOperationError(
                "Keyword arguments in concrete_fn calls are not supported.", n)
        if n.starargs:
            raise InvalidOperationError(
                "Starred arguments in concrete_fn calls are not supported.", n)
        if n.kwargs:
            raise InvalidOperationError(
                "kwargs in concrete_fn calls are not supported.", n)
        
        func = self.visit(n.func)
        
        if isinstance(func, _ast.Num):
            # support for suffixes on number literal (e.g. 1.0(f))
            args = n.args 
            if (len(args) != 1 and not isinstance(args[0], _ast.Name)):
                raise InvalidOperationError(
                    "Invalid number literal suffix.", n)
            
            #clq_type = literal_suffixes[args[0].id]
            #unresolved_type = InlineConstantURT(func.n, clq_type)
            raise NotImplementedError()
        else:
            args = [ self.visit(arg) for arg in n.args ]
            unresolved_type = CallURT(func, args)
            
        return astx.copy_node(n,
            func=func, 
            args=args, 
            keywords=[], 
            starargs=None, 
            kwargs=None, 
            unresolved_type=unresolved_type
        )
    
    def visit_Attribute(self, n):
        value = self.visit(n.value)
        ctx = self.visit(n.ctx)
        
        return astx.copy_node(n,
            value=value, 
            attr=n.attr, 
            ctx=ctx, 
            unresolved_type=AttributeURT(value, n.attr)
        )
    
    def visit_Subscript(self, n):
        value = self.visit(n.value)
        slice = self.visit(n.slice)
        ctx = self.visit(n.ctx)
        
        return astx.copy_node(n,
            value=value, 
            slice=slice, 
            ctx=ctx,
            unresolved_type=SubscriptURT(value, slice)
        )
    
    def visit_Ellipsis(self, n):
        # here in case a custom type wants to support it
        return astx.copy_node(n)
    
    def visit_Slice(self, n):
        # here in case a custom type wants to support it
        
        lower = n.lower
        if lower is not None:
            lower = self.visit(lower)
            
        upper = n.upper
        if upper is not None:
            upper = self.visit(upper)
            
        step = n.step
        if step is not None:
            step = self.visit(step)
            
        return astx.copy_node(n,
            lower=lower,
            upper=upper,
            step=step
        )
    
    def visit_ExtSlice(self, n):
        dims = n.dims
        if dims:
            dims = [self.visit(dim) for dim in dims]
            
        return astx.copy_node(n, 
            dims=dims
        )
    
    def visit_Index(self, n):
        value = self.visit(n.value)
        
        return astx.copy_node(n,
            value=value,
            unresolved_type=value.unresolved_type
        )
        
    def visit_Load(self, n):
        return astx.copy_node(n)
    
    def visit_Store(self, n):
        return astx.copy_node(n)
    
    def visit_Param(self, n):
        return astx.copy_node(n)
    
    def visit_Name(self, n):
        id = n.id
        ctx = self.visit(n.ctx)
        ctx_t = type(ctx)
        unresolved_type = NameURT(id)
        
        if ctx_t is _ast.Load:
            if not is_valid_varname(id):
                raise InvalidOperationError(
                    "Invalid variable name.", n)

            if id not in self.all_variables:
                # new free variable
                self.all_variables[id] = self.free_variables[id] = \
                    unresolved_type
                
        elif ctx_t is _ast.Store:
            try:
                current_type = self.all_variables[id]
            except KeyError:
                # new local variable
                is_valid_varname(id)
                self.all_variables[id] = self.local_variables[id] = \
                    self.cur_assignment_type                     
                
            else:
                if id in self.local_variables:
                    # multiple assignment of a local variable
                    self.local_variables[id] = MultipleAssignmentURT(
                        current_type, self.cur_assignment_type)
                elif id in self.free_variables:
                    raise InvalidOperationError(
                        "Free variables cannot be assigned to.", n)
                else:
                    # assignments are ok to params but won't change their type
                    pass
        
        elif ctx_t is _ast.Param:
            # TODO: rename 'arguments' in documentation to 'parameters' to
            # be consistent with Python usage (check this)
            self.all_variables[id] = self.arguments[id] = \
                unresolved_type
            
        return astx.copy_node(n,
            ctx=ctx,
            unresolved_type=unresolved_type
        )
        
    def visit_Num(self, n):
        num = n.n
        
        return astx.copy_node(n,
            unresolved_type=InlineConstantURT(num, infer_clq_type(num)))
    
    def visit_Str(self, n):
        # TODO: fix dependence on cl
        return astx.copy_node(n,
            unresolved_type=InlineConstantURT(n.s, cl.cl_char.private_ptr))  
    
##############################################################################
## Unresolved Types
##############################################################################
class UnresolvedType(object):
    """Abstract base class for unresolved types."""
    pass

class InlineConstantURT(UnresolvedType):
    """Represents the unresolved type of an inline constant."""
    def __init__(self, constant, clq_type):
        self.constant = constant
        self.clq_type = clq_type
        
    def __repr__(self):
        return self.clq_type.name
    
    @cypy.memoize
    def _resolve(self, visitor):
        return self.clq_type

class NameURT(UnresolvedType):
    """The unresolved type of variables."""
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return "`%s`" % self.name
    
    @cypy.memoize
    def _resolve(self, visitor):
        name = self.name
        
        try:
            # is it an argument?
            return visitor.concrete_fn.arg_map[name]
        except KeyError:
            # no? then it must be a local variable
            try:
                var = visitor._resolve_type(visitor.concrete_fn.generic_fn.local_variables[name])
            except KeyError:
                raise ConcreteTypeError("Invalid name." % name)
            
            # lets downstream multiple assignment types know we're 
            # resolving this name so it doesn't loop infinitely
            prev_resolving_name = visitor._resolving_name
            visitor._resolving_name = name
            
            clq_type = visitor._resolve_type(var)
             
            visitor._resolving_name = prev_resolving_name
            
            return clq_type

class AttributeURT(UnresolvedType):
    """The unresolved type of attribute expressions."""
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr
        
    def __repr__(self):
        return "%s.%s" % (`self.value.unresolved_type`, self.attr)
    
    @cypy.memoize
    def _resolve(self, visitor):
        obj = self.obj
        unresolved_type = obj.unresolved_type
        obj_type = visitor._resolve_type(unresolved_type)
            
        # protocol for attribute lookup
        try:
            # if _resolve_Attr is defined, call that
            _resolve_Attr = obj_type._resolve_Attr
        except AttributeError:
            # TODO: otherwise, try to resolve the attribute in the globals
            raise
        else:
            clq_type = _resolve_Attr(visitor, obj, self.attr)
            if clq_type is None:
                raise ConcreteTypeError("Invalid attribute.")
            return clq_type    

class SubscriptURT(UnresolvedType):
    """The unresolved type of subscript expressions."""
    def __init__(self, value, slice):
        self.value = value
        self.slice = slice
        
    def __repr__(self):
        return "%s[%s]" % (`self.value.unresolved_type`, 
                           `self.slice.unresolved_type`)
    
    @cypy.memoize
    def _resolve(self, visitor):
        value = self.value
        unresolved_type = value.unresolved_type
        value_type = visitor._resolve_type(unresolved_type)
        try:
            _resolve_Subscript = value_type._resolve_Subscript
        except AttributeError:
            raise ConcreteTypeError("Subscripting is not supported.")
        else:
            clq_type = _resolve_Subscript(visitor, value, self.slice)
            if clq_type is None:
                raise ConcreteTypeError("Subscripting is not supported.") 
            return clq_type
    
class UnaryOpURT(UnresolvedType):
    """The unresolved type of unary operator expressions."""
    def __init__(self, op, left):
        self.op = op
        self.left = left
        
    def __repr__(self):
        return "(%s %s)" % (astx.C_all_operators[type(self.op)], 
                            `self.left.unresolved_type`)
    
    @cypy.memoize
    def _resolve(self, visitor):
        left = self.left
        op = self.op
        left_unresolved_type = left.unresolved_type
        left_type = visitor._resolve_type(left_unresolved_type)
        try:
            _resolve_UnaryOp = left_type._resolve_UnaryOp
        except AttributeError:
            raise ConcreteTypeError("Unary operation is not supported.")
        else:
            clq_type = _resolve_UnaryOp(self, op, left)
            if clq_type is None:
                raise ConcreteTypeError("Unary operation is not supported.")
            return clq_type

class BinOpURT(UnresolvedType):
    """The unresolved type of binary operator expressions."""
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
        
    def __repr__(self):
        return "(%s %s, %s)" % (astx.C_all_operators[type(self.op)], 
                                `self.left.unresolved_type`, 
                                `self.right.unresolved_type`)
        
    @cypy.memoize
    def _resolve(self, visitor):
        left = self.left
        op = self.op
        right = self.right
        
        left_unresolved_type = left.unresolved_type
        left_type = visitor._resolve_type(left_unresolved_type)
        _resolve_BinOp = None
        # TODO: clean this up
        try:
            _resolve_BinOp = left_type._resolve_BinOp_left
        except AttributeError:
            right_unresolved_type = right.unresolved_type
            right_type = visitor._resolve_type(right_unresolved_type)
            try:                
                _resolve_BinOp = right_type._resolve_BinOp_right
            except AttributeError:
                raise ConcreteTypeError("Binary operation is not supported.")
        else:
            clq_type = _resolve_BinOp(visitor, left, op, right)
            if clq_type is None:
                right_unresolved_type = right.unresolved_type
                right_type = visitor._resolve_type(right_unresolved_type)
                try:
                    _resolve_BinOp = right_type._resolve_BinOp_right
                except AttributeError:
                    raise ConcreteTypeError("Unary operation is not supported.")
                else:
                    clq_type = _resolve_BinOp(visitor, left, op, right)
                    if clq_type is None:
                        raise ConcreteTypeError("Unary operation is not supported.")
            
            return clq_type

class CompareURT(UnresolvedType):
    """The unresolved type of comparison operations."""
    def __init__(self, left, ops, comparators):
        self.left = left
        self.ops = ops
        self.comparators = comparators
        
    def __repr__(self):
        left = self.left
        yield `left.unresolved_type`
        for op, right in zip(self.ops, self.comparators):
            yield (" ", astx.C_all_operators[type(op)], " ", 
                   `right.unresolved_type`)
            
    @cypy.memoize
    def _resolve(self, visitor):
        _resolve_type = visitor._resolve_type
        
        left = self.left
        ops = self.ops
        comparators = self.comparators
        
        cur = left
        iter = comparators.__iter__()
        position = 0
        # TODO: clean this up
        while True:
            cur_type = _resolve_type(cur.unresolved_type)
            try:
                _resolve = cur_type._resolve_Compare
            except AttributeError:
                pass
            else:
                clq_type = _resolve(visitor, left, ops, comparators, position)
                if clq_type is not None:
                    self.position = position
                    return clq_type
            try:
                cur = iter.next()
                position += 1
            except StopIteration:
                break
            
        raise ConcreteTypeError(
            "Comparison operation is not supported.")

class BoolOpURT(UnresolvedType):
    """The unresolved type of boolean operations."""
    def __init__(self, op, values):
        self.op = op
        self.values = values
        
    @cypy.memoize
    def _resolve(self, visitor):
        _resolve_type = visitor._resolve_type
        
        op = self.op
        values = self.values
        
        for position, value in enumerate(values):
            value_type = _resolve_type(value.unresolved_type)
            try:
                _resolve = value_type._resolve_BoolOp
            except AttributeError: pass
            else:
                clq_type = _resolve(visitor, op, values, position)
                if clq_type is not None:
                    self.position = position
                    return clq_type
        
        raise ConcreteTypeError(
            "Boolean operation is not supported.")
        
class MultipleAssignmentURT(UnresolvedType):
    """The unresolved type of variables that have been assigned to multiple 
    times."""
    def __init__(self, prev, new):
        self.prev = prev
        self.new = new
        
    def __repr__(self):
        return "%s <=> %s" % (`self.prev.unresolved_type`, 
                              `self.new.unresolved_type`)
        
    @cypy.memoize
    def _resolve(self, visitor):
        prev = self.prev
        new = self.new

        prev_type = visitor._resolve_type(prev)
        _resolving_name = visitor._resolving_name
        if _resolving_name:
            visitor.local_variables[_resolving_name] = prev_type
        new_type = visitor._resolve_type(new)
        if _resolving_name:
            visitor.local_variables[_resolving_name] = self
            
        _resolve = None
        try:
            _resolve = prev_type._resolve_MultipleAssignment_prev
        except AttributeError:
            try:
                _resolve = new_type._resolve_MultipleAssignment_new
            except AttributeError: pass
        else:
            clq_type = _resolve(new_type)
            if clq_type is not None:
                return clq_type
            else:
                try:
                    _resolve = new_type._resolve_MultipleAssignment_new
                except AttributeError: pass
        if _resolve is not None:
            clq_type = _resolve(prev_type)
            if clq_type is not None:
                return clq_type
        
        raise ConcreteTypeError(
            "Incompatible assignment types %s and %s." % 
            (prev_type.name, new_type.name))
        
class CallURT(UnresolvedType):
    """The unresolved type of call expressions."""
    def __init__(self, func, args):
        self.func = func
        self.args = args
        
    def __repr__(self):
        return "%s(%s)" % (self.func.unresolved_type, 
                           ", ".join(`arg.unresolved_type` 
                                     for arg in self.args))
    
    @cypy.memoize
    def _resolve(self, visitor):
        func = self.func
        args = self.args
        
        func_unresolved_type = func.unresolved_type
        func_type = visitor._resolve_type(func_unresolved_type)
        try: _resolve = func_type._resolve_Call
        except AttributeError: pass
        else:
            clq_type = _resolve(visitor, func, args)
            if clq_type is not None:
                return clq_type
            
        raise ConcreteTypeError("Type '%s' is not callable." % func_type.name)

##############################################################################
## Concrete Function Visitor
##############################################################################
class ConcreteFnVisitor(_ast.NodeVisitor):
    """A visitor that produces a copy of a cl.oquence concrete function's 
    syntax tree annotated with concrete types.
    
    These types are provided in the clq_type attribute.
    """
    def __init__(self, concrete_fn):
        self.concrete_fn = concrete_fn
        
        # used to provide base case for resolving multiple assignments
        self._resolving_name = None
        
    def visit_FunctionDef(self, generic_fn):
        self.generic_fn = generic_fn
        self.modifiers = [ ]
        self.program_items = [ ]
        
        self.return_type = self._resolve_type(generic_fn.return_type)
        self.args = self.visit(generic_fn.args)
        body = [ ]
        self.body_code = [ ]
        for stmt in generic_fn.body:
            body.append(self.visit(stmt))
            
        self.declarations = self._generate_declarations()
        name = self.name = self._generate_name()
        self.program_item = self._generate_program_item()
        self.program_items.append(self.program_item)
        
        return astx.copy_node(generic_fn,
            generic_fn=generic_fn,
            
            name=name,
            args=self.args,
            body=body,
            body_code=self.body_code,
            
            return_type=self.return_type,
            modifiers=self.modifiers,
            
            program_items=self.program_items,
            program_item=self.program_item
        )
        
    def _resolve_type(self, unresolved_type):
        """Resolves an unresolved type."""
        if isinstance(unresolved_type, Type):
            return unresolved_type
        else:
            try:
                _resolve = unresolved_type._resolve
            except AttributeError:
                raise Error("Unexpected unresolved type.")
            else:
                return _resolve(self)

    def _observe(self, clq_type):
        # Call a method when a clq_type is observed
        try:
            _observe = clq_type._observe
        except AttributeError: pass
        else:
            _observe(self)
        
        return clq_type
        
    tab = staticmethod(cg.CG.tab)
    untab = staticmethod(cg.CG.untab)
            
    def _generate_name(self):
        # TODO name mangling
        return self.generic_fn.name
    
    def _generate_declarations(self):
        local_variables = self.generic_fn.local_variables
        def _generate():
            for name, unresolved_type in local_variables.iteritems():
                clq_type = self._resolve_type(unresolved_type)
                yield (clq_type.name, " ", name, ";\n")
        return tuple(_generate())
    
    def visit_arguments(self, n):
        return _ast.arguments(
            args=[self.visit(arg) for arg in n.args],
            vararg=None,
            kwarg=None,
            defaults=[]
        )
    
    def _yield_arg_str(self):
        concrete_fn = self.concrete_fn
        for arg_name, arg_type in zip(concrete_fn.generic_fn.arg_names, concrete_fn.arg_types):
            yield (arg_type.name, " ", arg_name)      
    
    def _generate_program_item(self):
        g = cg.CG()
        g.append(cypy.join(cypy.cons(self.modifiers, (self.return_type.name,)), " "))
        g.append((" ", self.name, "("))
        g.append(cypy.join(self._yield_arg_str(), ", "))
        g.append((") {\n", self.tab))
        g.append(cypy.join(self.declarations, "\n"))
        g.append(self.body_code)
        g.append((self.untab, "\n}\n"))
        return ProgramItem(self.name, g.code)

    #########################################################################
    ## Statements
    ##########################################################################
    def visit_Return(self, n):
        if self.return_type is void:
            self.body_code.append("return;\n")
        else:
            value = n.value
            self.body_code.append(("return ", self.visit(value).code, ";\n"))

        return astx.copy_node(n,
            value=value
        )
        
    def visit_Assign(self, n):
        value = self.visit(n.value)
        target = astx.copy_node(n.targets[0])
        if isinstance(target, _ast.Name):
            target_type = self._resolve_type(target.unresolved_type)
            try:
                _generate = target_type._generate_Assign
            except AttributeError:
                raise InvalidOperationError(
                    "Type does not support assignment.", n)               
        elif isinstance(target, _ast.Attribute):
            obj_type = self._resolve_type(target.value.unresolved_type)
            try:
                _generate = obj_type._generate_Assign_Attr
            except AttributeError:
                raise InvalidOperationError(
                    "Type does not support attribute assignment.", n)
        elif isinstance(target, _ast.Subscript):
            arr_type = self._resolve_type(target.value.unresolved_type)
            try:
                _generate = arr_type._generate_Assign_Subscript
            except AttributeError:
                raise InvalidOperationError(
                    "Type does not support subscript assignment.", n)
        
        _generate(self, target, value)
        
        return astx.copy_node(n,
            targets=[target],
            value=value
        )
        
    def visit_AugAssign(self, n):
        value = self.visit(n.value)
        target = astx.copy_node(n.target)
        op = astx.copy_node(n.op)
        
        if isinstance(target, _ast.Name):
            target_type = self._resolve_type(target.unresolved_type)
            try:
                _generate = target_type._generate_AugAssign
            except AttributeError:
                raise InvalidOperationError(
                    "Type does not support augmented assignment.")
        elif isinstance(target, _ast.Attribute):
            obj_type = self._resolve_type(target.value.unresolved_type)
            try:
                _generate = obj_type._generate_AugAssign_Attr
            except AttributeError:
                raise InvalidOperationError(
                    "Type does not support augmented attribute assignment.")
        elif isinstance(target, _ast.Subscript):
            arr_type = self._resolve_type(target.value.unresolved_type)
            try:
                _generate = arr_type._generate_AugAssign_Subscript
            except AttributeError:
                raise InvalidOperationError(
                    "Type does not support augmented subscript assignment.")
            
        _generate(self, target, op, value)
    
        return astx.copy_node(n,
            target=target,
            op=op,
            value=value
        )
        
    def visit_For(self, n):
        init = n.init
        var = init.targets[0].id
        init_value = self.visit(init.value)
        init_code = (var, " = ", init_value.code)
        
        guard = self.visit(n.guard) 
        
        update_stmt = n.update_stmt
        update_value = self.visit(update_stmt.value)
        update_code = (var, " += ", update_value.code)
        
        self.body_code.append(
            ("for (", init_code, "; ", 
                      guard.code, "; ", 
                      update_code, ") {\n", self.tab)
        )
        
        body = [ ]
        for stmt in n.body:
            body.append(self.visit(stmt))
            
        self.body_code.append(
            (self.untab, "}\n")
        )
        
        return astx.copy_node(n,
            var=var,
            init_value=init_value,
            guard=guard,
            update_value=update_value,
            body=body,
            orelse=[]
        )
        
    def visit_While(self, n):
        test = self.visit(n.test)
        
        self.body_code.append(("while (", test.code, ") {\n", self.tab))
        
        body = [ ]
        for stmt in n.body:
            body.append(self.visit(stmt))
            
        self.body_code.append((self.untab, "}\n"))
        
        return astx.copy_node(n,
            test=test,
            body=body,
            orelse=[]
        )
        
    def visit_If(self, n):
        test = self.visit(n.test)
        
        self.body_code.append(("if (", test.code, ") {\n", self.tab))
        
        body = [ ]
        for stmt in n.body:
            body.append(self.visit(stmt))
            
        orelse = n.orelse
        num_else = len(orelse)
        if num_else == 0:
            self.body_code.append((self.untab, "}\n"))
            orelse = [ ]
        elif num_else == 1:
            self.body_code.append(" else ")
            orelse = [self.visit(orelse[0])]
        else:
            self.body_code.append((" else {\n", self.tab))
            orelse = [ ]
            for stmt in n.orelse:
                orelse.append(self.visit(stmt))
            self.body_code.append((self.untab, "}\n"))
        
        return astx.copy_node(n,
            test=test,
            body=body,
            orelse=orelse
        )
    
    def visit_Expr(self, n):
        value = self.visit(n.value)
        self.body_code.append((value.code, ";\n"))
        
        return astx.copy_node(n,
            value=value
        )
        
    def visit_Pass(self, n):
        self.body_code.append(";\n")
        return astx.copy_node(n)
    
    def visit_Break(self, n):
        self.body_code.append("break;\n")
        return astx.copy_node(n)
        
    def visit_Continue(self, n):
        self.body_code.append("continue;\n")
        return astx.copy_node(n)
    
    def visit_Exec(self, n):
        self.body_code.append(n.body.s)
        return astx.copy_node(n,
            body=astx.copy_node(n.body),
            globals=[],
            locals=[]
        )
    
    ######################################################################
    ## Supported Operators
    ######################################################################
    def _visit_op(self, n):
        return astx.copy_node(n,
            code=astx.C_all_operators[type(n)]
        )
    
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
    def visit_UnaryOp(self, n):
        clq_type = self._resolve_type(n.operand.unresolved_type)
        try:
            _generate_UnaryOp = clq_type._generate_UnaryOp
        except AttributeError:
            raise InvalidOperationError(
                "Type does not support unary operations.")
        
        node = _generate_UnaryOp(self, n)
        clq_type = self._resolve_type(n.unresolved_type)
        node.clq_type = self._observe(clq_type)
        return node
        
    def visit_BinOp(self, n):
        clq_type = self._resolve_type(n.left.unresolved_type)
        try:
            _generate_BinOp = clq_type._generate_BinOp
        except AttributeError:
            raise InvalidOperationError(
                "Type does not support binary operations.")
        
        # TODO: two sided
        # TODO: check consistency with _resolve_BinOp
        node = _generate_BinOp(self, n)
        clq_type = self._resolve_type(n.unresolved_type)
        node.clq_type = self._observe(clq_type)
        return node
    
    def visit_Compare(self, n):
        clq_type = self._resolve_type(n.left.unresolved_type)
        try:
            _generate_Compare = clq_type._generate_Compare
        except AttributeError:
            raise InvalidOperationError(
                "Type does not support compare operations.")
        
        # TODO: many-sided?
        node = _generate_Compare(self, n)
        clq_type = self._resolve_type(n.unresolved_type)
        node.clq_type = self._observe(clq_type)
        return node
        
    def visit_BoolOp(self, n):
        clq_type = self._resolve_type(n.values[0].unresolved_type)
        try:
            _generate_BoolOp = clq_type._generate_BoolOp
        except AttributeError:
            raise InvalidOperationError(
                "Type does not support boolean operations.")

        # TODO: many-sided
        node = _generate_BoolOp(self, n)
        clq_type = self._resolve_type(n.unresolved_type)
        node.clq_type = self._observe(clq_type)
        return node
    
    ######################################################################
    ## Other Expressions
    ######################################################################                
    def visit_IfExp(self, n):
        test = self.visit(n.test)
        body = self.visit(n.body)
        orelse = self.visit(n.orelse)
        
        code = ("((", test.code, ") ? (", 
                      body.code, ") : (", 
                      orelse.code, ")")
        clq_type = self._resolve_type(n.unresolved_type)
        
        return astx.copy_node(n,
            test=test,
            body=body,
            orelse=orelse,
            
            code=code,
            clq_type=self._observe(clq_type)
        )
        
    def visit_Call(self, n):
        clq_type = self._resolve_type(n.func.unresolved_type)
        try:
            _generate_Call = clq_type._generate_Call
        except AttributeError:
            raise InvalidOperationError("Type does not support call operation.")
        
        node = _generate_Call(self, n)
        clq_type = self._resolve_type(n.unresolved_type)
        node.clq_type = self._observe(clq_type)
        return node
    
    def visit_Attribute(self, n):
        clq_type = self._resolve_type(n.value.unresolved_type)
        try:
            _generate_Attribute = clq_type._generate_Attribute
        except AttributeError:
            raise InvalidOperationError("Type does not support attribute access operation.")
        
        node = _generate_Attribute(self, n)
        clq_type = self._resolve_type(n.unresolved_type)
        node.clq_type = self._observe(clq_type)
        return node
    
    def visit_Subscript(self, n):
        clq_type = self._resolve_type(n.value.unresolved_type)
        try:
            _generate_Subscript = clq_type._generate_Subscript
        except AttributeError:
            raise InvalidOperationError("Type does not support subscript access operation.")
        
        node = _generate_Subscript(self, n)
        clq_type = self._resolve_type(n.unresolved_type)
        node.clq_type = self._observe(clq_type)
        return node
    
    def visit_Index(self, n):
        value = self.visit(n.value)
        return astx.copy_node(n,
            value=value,
            code=value.code,
            clq_type=value.clq_type
        )
        
    def visit_Name(self, n):
        return astx.copy_node(n,
            code=n.id,
            clq_type=self._observe(self._resolve_type(n.unresolved_type))
        )
        
    def visit_Num(self, n):
        # TODO: use proper conversion function (cl.to_cl_numeric_literal)
        return astx.copy_node(n,
            code=str(n.n),
            clq_type=self._observe(self._resolve_type(n.unresolved_type))
        )
        
    def visit_Str(self, n):
        # TODO: use proper conversion function (cl.to_cl_string_literal)
        return astx.copy_node(n,
            code=('"', n.s, '"'),
            clq_type=self._observe(self._resolve_type(n.unresolved_type))
        )
    
#class ExtensionItem(ProgramItem):
#    """Represents an extension."""
#    def __init__(self, extension):
#        self.extension = extension
#        
#    @cypy.lazy(property)
#    def source(self):
#        return self.extension.pragma_str
#cypy.interned(ExtensionItem)
#_cl_khr_fp64_item = ExtensionItem(cl.cl_khr_fp64)
#_cl_khr_fp16_item = ExtensionItem(cl.cl_khr_fp16)
#_cl_khr_byte_addressable_store = ExtensionItem(cl.cl_khr_byte_addressable_store)
#
#class ProgramItemVisitor(_ast.NodeVisitor):
#    """Visits an annotated ast to produce program items and metadata."""
#    def __init__(self, generic_fn, explicit_arg_names, explicit_arg_types, 
#                 constants):
#        self.generic_fn = generic_fn
#        self.explicit_arg_names = explicit_arg_names
#        self.explicit_arg_types = explicit_arg_types
#        self.explicit_arg_map = cypy.frozendict(zip(explicit_arg_names, 
#                                                   explicit_arg_types))
#        self.constants = constants
#        self.local_variables = dict(generic_fn.annotated_ast.local_variables)
#        self.all_variables = generic_fn.all_variables
#        
#        self.implicit_args = [ ]
#        self.implicit_args_map = { }
#        
#        self._resolving_name = None
#        
#        # a list of program items needed by this concrete function
#        self.program_items = [ ]
#        
#        self.gamma = { }
#        self.delta_r = { }
#        self.delta_w = { }
#                
#    def _resolve_type(self, unresolved_type):
#        if isinstance(unresolved_type, cl.Type):
#            # pre-resolved (e.g. boolean expressions)          
#            return unresolved_type
#        else:
#            try:
#                _resolve = unresolved_type._resolve
#            except AttributeError:
#                # should never happen
#                raise Error("Unexpected unresolved type: %s" % 
#                            str(unresolved_type))
#            else:
#                return _resolve(self)                
#    
#    ############################################################################
#    # FunctionDef
#    ############################################################################
#    def visit_FunctionDef(self, n):
#        body = self.body = self._generate_body(n)
#        signature = self.signature = self._generate_signature()
#        modifiers = self.modifiers = self._determine_modifiers(n)
#        name = self.name = self._generate_name(n.name)
#
#        code = self.code = "%s %s(%s) %s" % (modifiers, name, signature, body)
#        
#        # create a program item
#        self.program_item = program_item = ProgramItem(name, code)
#        self.program_items.append(program_item)
#    
#    def _generate_body(self, n):
#        # produce the code for the body and in the process, determine all the
#        # necessary implicit arguments needed for downstream functions
#        g = cg.CG(processor=None)
#        self.tab = g.tab
#        self.untab = g.untab
#        declarations = self._visit_declarations()
#        body = self._visit_body(n.body)
#        docstring = self._docstring
#        ("{\n", g.tab, docstring, declarations, body, g.untab, "\n}") >> g
#        return g.code
#
#    def _visit_declarations(self):
#        yield "// Automatically generated local variable declarations\n"
#        for name, unresolved_type in self.local_variables.iteritems():
#            clq_type = self._resolve_type(unresolved_type)
#            yield (clq_type.name, " ", name, ";\n")
#        yield "\n\n"
#        
#    def _visit_body(self, body):
#        docstring = self._docstring = self._determine_docstring(body)
#        if docstring is not None: body = body[1:]          
#        return cypy.join((self.visit(stmt) for stmt in body), "\n")
#    
#    @staticmethod
#    def _determine_docstring(body):
#        if body:
#            docstring = body[0]
#            if isinstance(docstring, _ast.Expr):
#                docstring = docstring.value
#                if isinstance(docstring, _ast.Str):
#                    # issue 168: if docstring contains "*/" this will break
#                    docstring = "\n/* %s */\n" % docstring.s
#                    body = body[1:]
#                else:
#                    docstring = None
#            else:
#                docstring = None
#        else:
#            docstring = None
#        return docstring
#    
#    def _determine_modifiers(self, n):
#        # determine return type and whether to add a __kernel modifier
#        self.return_type = return_type = self._resolve_type(n.return_type)
#        if self._is_kernel: 
#            modifiers = "__kernel void"
#        else:
#            modifiers = return_type.name
#        return modifiers
#    
#    @cypy.lazy(property)
#    def _is_kernel(self):
#        if self.return_type is not cl.cl_void:
#            # Section 6.8j
#            return False
#        
#        for arg_type in self.all_arg_types:
#            if isinstance(arg_type, cl.ScalarType):
#                # Section 6.8i
#                if arg_type.min_sizeof != arg_type.max_sizeof:
#                    return False
#                
#                if arg_type == cl.cl_half:
#                    return False
#            
#            if isinstance(arg_type, cl.PtrType):
#                # Section 6.8a
#                if isinstance(arg_type, cl.PrivatePtrType):
#                    return False
#                if isinstance(arg_type.target_type, cl.PtrType):
#                    return False
#                
#            if arg_type is cl.cl_event_t:
#                # Section 6.8n
#                return False
#                
#        return True
#
#    @staticmethod
#    def _generate_name(basename):
#        try:
#            name_count = _function_name_counts[basename]
#            _function_name_counts[basename] = name_count + 1
#        except KeyError:
#            _function_name_counts[basename] = 1
#            return basename
#        return basename + "___" + str(name_count)
#
#    @cypy.lazy(property)
#    def all_arg_names(self):
#        return cypy.cons.ed(self.explicit_arg_names, self.implicit_arg_names) #@UndefinedVariable
#    
#    @cypy.lazy(property)
#    def all_arg_types(self):
#        return cypy.cons.ed(self.explicit_arg_types, self.implicit_arg_types) #@UndefinedVariable
#    
#    @cypy.lazy(property)
#    def implicit_arg_names(self):
#        return tuple("__implicit__" + str(idx) 
#                     for idx in xrange(len(self.implicit_args)))
#        
#    @cypy.lazy(property)
#    def implicit_arg_types(self):
#        return tuple(infer_clq_type(value) for value in self.implicit_args)
#
#    def _generate_signature(self):
#        return ", ".join(self._yield_signature_items())
#    
#    def _yield_signature_items(self):
#        for arg_name, arg_type in zip(self.all_arg_names, self.all_arg_types):
#            self._process_stack_type(arg_type)
#            yield arg_type.name + " " + arg_name
#    
#    def _process_stack_type(self, clq_type):
#        # infers extensions that relate to stack variable types
#        if clq_type is cl.cl_double:
#            self._add_program_item(_cl_khr_fp64_item)
#        if clq_type is cl.cl_half:
#            self._add_program_item(_cl_khr_fp16_item)
#        if isinstance(clq_type, cl.ScalarType) and clq_type.min_sizeof < 4:
#            # Not sure if this is necessary for half, but probably doesn't
#            # matter.
#            self._add_program_item(_cl_khr_byte_addressable_store)
#
#    ############################################################################
#    # Statements 
#    ############################################################################
#    def visit_Return(self, n):
#        value = n.value
#        if value is None:
#            return "return;"
#        else:
#            return ("return ", self.visit(value), ";")
#        
#    def visit_Assign(self, n):
#        return self._visit_targets(n)
#           
#    def _visit_targets(self, n): 
#        value = n.value
#        for target in n.targets:
#            found = False
#            if isinstance(target, _ast.Name):
#                clq_type = self._resolve_type(target.unresolved_type)
#                try:
#                    _generate = clq_type._generate_Assign
#                except AttributeError: pass
#                else:
#                    found = True
#                    yield _generate(self, target, value)
#            elif isinstance(target, _ast.Attribute):
#                clq_type = self._resolve_type(target.value.unresolved_type)
#                try:
#                    _generate = clq_type._generate_AssignAttribute
#                except AttributeError: pass
#                else:
#                    found = True
#                    yield _generate(self, target.value, target.identifier, 
#                                    value)
#            elif isinstance(target, _ast.Subscript):
#                clq_type = self._resolve_type(target.value.unresolved_type)
#                try:
#                    _generate = clq_type._generate_AssignSubscript
#                except AttributeError: pass
#                else:
#                    found = True
#                    yield _generate(self, target.value, target.slice, value)
#
#            if not found:
#                raise CompileTimeError("Invalid assignment.", n)
#            
#    def visit_AugAssign(self, n):
#        target = n.target
#        op = n.op
#        value = n.value
#        
#        if isinstance(target, _ast.Name):
#            clq_type = self._resolve_type(target.unresolved_type)
#            try:
#                _generate = clq_type._generate_AugAssign
#            except AttributeError: pass
#            else:
#                return _generate(self, target, op, value)
#        elif isinstance(target, _ast.Attribute):
#            clq_type = self._resolve_type(target.value.unresolved_type)
#            try:
#                _generate = clq_type._generate_AugAssignAttribute
#            except AttributeError: pass
#            else:
#                return _generate(self, target.value, target.identifier, op, 
#                                 value)
#        elif isinstance(target, _ast.Subscript):
#            clq_type = self._resolve_type(target.value.unresolved_type)
#            try:
#                _generate = clq_type._generate_AugAssignSubscript
#            except AttributeError: pass
#            else:
#                return _generate(self, target.value, target.slice, op, value)
#            
#        raise CompileTimeError("Invalid augmented assignment.", n)
#        
#    def visit_For(self, n):
#        # visit parts of update statement manually to avoid inserting the
#        # trailing semicolon
#        update_stmt = n.update_stmt
#        update_code = (self.visit(update_stmt.target), " += ", 
#                       self.visit(update_stmt.value))
#        
#        return ("for (", self.visit(n.init), " ", # the ';' comes from the stmt
#                self.visit(n.guard), "; ",
#                update_code, ") {\n", self.tab, 
#                self._visit_body(n.body), self.untab, "\n}")
#        
#    def visit_While(self, n):
#        return ("while (", self.visit(n.test), ") {\n", 
#                self.tab, self._visit_body(n.body), self.untab,
#                "\n}")
#        
#    def visit_If(self, n):
#        return ("if (", self.visit(n.test), ") {\n", self.tab,
#                self._visit_body(n.body), self.untab, "\n}",
#                self._visit_orelse(n.orelse))
#        
#    def _visit_orelse(self, orelse):
#        num = len(orelse)
#        if num == 0:
#            return
#        elif num == 1:
#            # covers the else if case
#            return (" else ", self.visit(orelse[0]))
#        else:
#            return (" else {\n", self.tab, self._visit_body(orelse),
#                    self.untab, "\n}")
#    
#    def visit_Expr(self, n):
#        return (self.visit(n.value), ";")
#        
#    def visit_Pass(self, _):
#        pass
#        
#    def visit_Break(self, _):
#        return "break;"
#        
#    def visit_Continue(self, _):
#        return "continue;"
#    
#    def visit_Exec(self, n):
#        # shorthand for inserting raw OpenCL code / pre-processor macros / etc.
#        return n.body.s
#        
#    ######################################################################
#    ## Supported Operators
#    ######################################################################
#    def _visit_op(self, n):
#        return astx.C_all_operators[type(n)]
#    
#    visit_Add = _visit_op
#    visit_Sub = _visit_op
#    visit_Mult = _visit_op
#    visit_Div = _visit_op
#    visit_Pow = _visit_op
#    visit_LShift = _visit_op
#    visit_RShift = _visit_op
#    visit_BitOr = _visit_op
#    visit_BitXor = _visit_op
#    visit_BitAnd = _visit_op
#    visit_FloorDiv = _visit_op
#    visit_BitAnd = _visit_op
#    visit_FloorDiv = _visit_op
#    visit_Invert = _visit_op
#    visit_Not = _visit_op
#    visit_UAdd = _visit_op
#    visit_USub = _visit_op
#    visit_Eq = _visit_op
#    visit_NotEq = _visit_op
#    visit_Lt = _visit_op
#    visit_LtE = _visit_op
#    visit_Gt = _visit_op
#    visit_GtE = _visit_op
#    visit_And = _visit_op
#    visit_Or = _visit_op
#    
#    ######################################################################
#    ## Operator Expressions
#    ######################################################################
#    def _process_expr(self, n):
#        clq_type = self._resolve_type(n.unresolved_type)
#        # checks for any extensions that must be enabled due to introduction
#        # of stuff
#        self._process_stack_type(clq_type)
#                        
#    def visit_UnaryOp(self, n):
#        self._process_expr(n)
#        
#        clq_type = self._resolve_type(n.unresolved_type)
#        return clq_type._generate_UnaryOp(self, n.op, n.operand)
#    
#    def visit_BinOp(self, n):
#        self._process_expr(n)
#        
#        left = n.left
#        op = n.op
#        right = n.right
#        
#        left_clq_type = self._resolve_type(left.unresolved_type)
#        try:
#            code = left_clq_type._generate_BinOp_left(self, left, op, right)
#            if code is not NotImplemented:
#                return code
#        except AttributeError: pass
#        else:
#            right_clq_type = self._resolve_type(right.unresolved_type)
#            return right_clq_type._generate_BinOp_right(self, left, op, right)
#            
#    def visit_Compare(self, n):
#        self._process_expr(n)
#        left = n.left
#        comparators = n.comparators
#        ops = n.ops
#        
#        position = n.unresolved_type.position
#        if position == 0:
#            value = left
#        else:
#            value = comparators[position - 1]
#            
#        clq_type = self._resolve_type(value.unresolved_type)
#        try:
#            _generate = clq_type._generate_Compare
#        except AttributeError:
#            raise CompileTimeError(
#                "Comparison is not supported for specified value types.", n)
#        else:
#            return _generate(self, left, ops, comparators, position)
#
#    def visit_BoolOp(self, n):
#        self._process_expr(n)
#        values = n.values
#        op = n.op
#
#        position = n.unresolved_type.position
#        value = values[position]
#        
#        clq_type = self._resolve_type(value.unresolved_type)
#        try:
#            _generate = clq_type._generate_BoolOp
#        except AttributeError:
#            raise CompileTimeError(
#                "Boolean operations are not supported for specified value types.")
#        else:
#            return _generate(self, op, values, position)
#                
#    ######################################################################
#    ## Expressions
#    ######################################################################                
#    def visit_IfExp(self, n):
#        self._process_expr(n)
#        
#        return (self.visit(n.test), " ? ", self.visit(n.body), " : ", 
#                self.visit(n.orelse))
#    
#    def visit_Call(self, n):
#        self._process_expr(n)
#        
#        func_clq_type = self._resolve_type(n.func.unresolved_type)
#        return func_clq_type._generate_Call(self, n.func, n.args)
#    
#    def _add_implicit(self, value):
#        # add an implicit value, returning its index
#        implicit_args_map = self.implicit_args_map
#        try:
#            return implicit_args_map[value]
#        except KeyError:
#            implicit_args = self.implicit_args
#            n_implicit = len(implicit_args)
#            implicit_args_map[value] = n_implicit
#            implicit_args.append(value)
#            return n_implicit
#        
#    def _add_program_item(self, program_item):
#        program_items = self.program_items
#        if program_item not in program_items:
#            program_items.append(program_item)
#
#    def visit_Attribute(self, n):
#        self._process_expr(n)
#        
#        value_clq_type = self._resolve_type(n.value.unresolved_type)
#        return value_clq_type._generate_Attribute(self, n.value, n.identifier)
#    
#    def visit_Subscript(self, n):
#        self._process_expr(n)
#        
#        value_clq_type = self._resolve_type(n.value.unresolved_type)
#        return value_clq_type._generate_Subscript(self, n.value, n.slice)
#        #return (self.visit(n.value), "[", self.visit(n.slice), "]")
#    
#    def visit_Index(self, n):
#        self._process_expr(n)
#        
#        return self.visit(n.value)
#    
#    def visit_Name(self, n):
#        self._process_expr(n)
#        
#        id = n.id
#        if id in cl.builtins:
#            return id
#        
#        try:
#            constant = self.constants[id]
#        except KeyError:
#            if id in self.all_variables:
#                return id
#        else:
#            if isinstance(n.ctx, _ast.Store):
#                raise CompileTimeError("Cannot assign to constant %s." % id, n)
#            
#            # inline constants
#            if isinstance(constant, basestring):
#                return cl.to_cl_string_literal(constant)
#            clq_type = infer_clq_type(constant)
#            if isinstance(clq_type, cl.PtrType):
#                return "__implicit__" + str(self._add_implicit(constant))
#            else:
#                return clq_type.make_literal(constant)
#    
#    def visit_Num(self, n):
#        self._process_expr(n)
#        
#        return cl.to_cl_numeric_literal(n.n)
#    
#    def visit_Str(self, n):
#        self._process_expr(n)
#        
#        return cl.to_cl_string_literal(n.s)
#    
#
#
#################################################################################
## Vector type code generation
#################################################################################
#cl.VectorType._generate_AugAssign = _scalar_generate_AugAssign
#cl.VectorType._generate_Compare = _scalar_generate_Compare
#cl.VectorType._generate_BoolOp = _scalar_generate_BoolOp
#cl.VectorType._generate_UnaryOp = _scalar_generate_UnaryOp
#
## TODO: make generate use same selection as inference
#def _vec_generate_BinOp_left(self, visitor, left, op, right):
#    visit = visitor.visit
#    
#    if isinstance(op, _ast.Pow):
#        return ("pow(", visit(left), ", ", visit(right), ")")
#    elif isinstance(op, _ast.FloorDiv):
#        if isinstance(self.base_type, cl.IntegerType):
#            return ("(", visit(left), "/", visit(right), ")")
#        else:
#            return ("floor(", visit(left), "/", visit(right), ")")
#    else:
#        return ("(", visit(left), " ", visit(op), " ", visit(right), ")")
#cl.VectorType._generate_BinOp_left = _vec_generate_BinOp_left
#
## TODO: Are these being generated correctly?
#def _vec_generate_Attribute(self, visitor, obj, attr):
#    visit = visitor.visit
#    return (visit(obj), ".", attr)
#cl.VectorType._generate_Attribute = _vec_generate_Attribute
#
#def _vec_generate_AssignAttribute(self, visitor, obj, attr, value):
#    visit = visitor.visit
#    return (visit(obj), ".", attr, " = ", visit(value), ";")
#cl.VectorType._generate_AssignAttribute = _vec_generate_AssignAttribute
#
#def _vec_generate_AugAssignAttribute(self, visitor, obj, attr, op, value):
#    visit = visitor.visit
#    return (visit(obj), ".", attr, " ", visit(op), "= ", visit(value), ";")
#cl.VectorType._generate_AugAssignAttribute = _vec_generate_AugAssignAttribute
#
## TODO: vector literals
## TODO: builtins
## TODO: documentation
#
#################################################################################
## Function type code generation
#################################################################################
#def _generic_fn_generate_Call(self, visitor, func, args): #@UnusedVariable
#    arg_types = tuple(visitor._resolve_type(arg.unresolved_type) 
#                      for arg in args)
#    generic_fn = self.generic_fn
#    concrete_fn = generic_fn._get_concrete_fn(arg_types)
#    name = concrete_fn.fullname
#    
#    # insert program items
#    add_program_item = visitor._add_program_item
#    for program_item in concrete_fn.program_items:
#        add_program_item(program_item)
#
#    # add defaults
#    n_provided = len(args)
#    n_args = len(generic_fn.explicit_arg_names)
#    n_default = n_args - n_provided
#    if n_default < 0:
#        raise CompileTimeError("Too many arguments were specified for %s." %
#                               name)
#    defaults = generic_fn.defaults[0:n_default]    
#    
#    all_args = _yield_args(visitor, args, arg_types, defaults, 
#                            concrete_fn.implicit_args)
#    return (name, "(", all_args, ")")
#_type_inference.GenericFnType._generate_Call = _generic_fn_generate_Call
#
#def _concrete_fn_generate_Call(self, visitor, func, args): #@UnusedVariable
#    concrete_fn = self.concrete_fn
#    name = concrete_fn.fullname
#    
#    # insert program items
#    add_program_item = visitor._add_program_item
#    for program_item in concrete_fn.program_items:
#        add_program_item(program_item)
#    
#    arg_types = (visitor._resolve_type(arg.unresolved_type) 
#                 for arg in args)
#    all_args = _yield_args(visitor, args, arg_types, (), 
#                                      concrete_fn.implicit_args)
#    return (name, "(", all_args, ")")
#_type_inference.ConcreteFnType._generate_Call = _concrete_fn_generate_Call
#
#def _yield_args(visitor, args, arg_types, defaults, implicit_args):
#    visit = visitor.visit
#    for arg, arg_type in zip(args, arg_types):
#        if not hasattr(arg_type, 'constant_value'):
#            yield visit(arg)
#            
#    add_implicit = visitor._add_implicit
#    for implicit in cypy.cons(defaults, implicit_args):
#        yield "__implicit__" + str(add_implicit(implicit))
#        
#def _builtin_fn_generate_Call(self, visitor, func, args): #@UnusedVariable
#    builtin = self.builtin
#    
#    # extension inference
#    requires_extensions = builtin.requires_extensions
#    if requires_extensions is not None:
#        resolve_type = visitor._resolve_type
#        arg_types = (resolve_type(arg.unresolved_type) 
#                     for arg in args)
#        add_program_item = visitor._add_program_item
#        for extension in requires_extensions(*arg_types):
#            add_program_item(ExtensionItem(extension))
#        
#    visit = visitor.visit
#    all_args = cypy.join((visit(arg) for arg in args), ", ")
#    return (builtin.name, "(", all_args, ")")
#_type_inference.BuiltinFnType._generate_Call = _builtin_fn_generate_Call
#
#################################################################################
## Type type code generation
#################################################################################
#def _type_generate_Call(self, visitor, func, args):
#    func_type = visitor._resolve_type(func.unresolved_type).type
#    arg = args[0]
#    if isinstance(arg, _ast.Num):
#        # special casing this so double literals are used in casts
#        arg = arg.n
#    else:
#        arg = visitor.visit(arg)
#    return ("(", func_type.name, ")(", arg, ")")
#_type_inference.TypeType._generate_Call = _type_generate_Call
#
#################################################################################
## Addressof macro code generation
#################################################################################
#def _addressof_generate_Call(self, visitor, func, args): #@UnusedVariable
#    return ("&", visitor.visit(args[0]))
#_type_inference.AddressofType._generate_Call = _addressof_generate_Call
#
###################################
#
#class GID(Type):
#    def __init__(self, a, b):
#        self.a = a
#        self.b = b
#        
#    def _resolve_BinOp(self, visitor, left, op, right):
#        right_type = visitor.resolve(right)
#        if isinstance(right_type, GID):
#            a_new = None
#            b_new = None
#            if (isinstance(op, _ast.Add)):
#                a_new = self.a + right_type.a
#                b_new = self.b + right_type.b
#                
#            if (isinstance(op, _ast.Mul)):
#                a = self.a
#                if a == 0:
#                    a = right_type.a
#                    b = right_type.b
#                    c = self.b
#                else:
#                    a = right_type.a
#                    if a == 0:
#                        a = self.a
#                        b = self.b
#                        c = right_type.b
#                    else:
#                        a = None
#                        
#                if a is not None:
#                    a_new = a * c
#                    b_new = b * c
#                    
#            if a_new is not None and b_new is not None:
#                return GID(a_new, b_new)
#
#        elif isinstance(right_type, IntegerType) and right_type.unsigned:
#            # TODO
#            pass
#        
