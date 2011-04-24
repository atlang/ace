# All content Copyright 2010 Cyrus Omar <cyrus.omar@gmail.com> unless otherwise
# specified.
#
# Contributors:
#     Cyrus Omar <cyrus.omar@gmail.com>
#
# This file is part of, and licensed under the terms of, the atomic-hedgehog
# package.
#
# The atomic-hedgehog package is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# The atomic-hedgehog package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with the atomic-hedgehog package. If not, see <http://www.gnu.org/licenses/>.
"""Type inference."""
import ast as _ast # http://docs.python.org/library/ast.html

import cypy
import cypy.astx as astx
import cl
from cl import Error

class InvalidOperationError(Error):
    def __init__(self, message, node):
        self.message = message
        self.node = node

##############################################################################
## Type Annotation
##############################################################################
@cypy.memoize
def get_annotated_ast(ast):
    return Annotator().visit(ast)

class Annotator(_ast.NodeVisitor):
    def __init__(self):
        # map from all variables to their unresolved types
        self.all_variables = { }
        
        # map from argument variables to their unresolved types
        self.argument_variables = { }
        
        # map from local variables to their unresolved types
        self.local_variables = { }        
        
        # map from free variables to their unresolved types
        self.free_variables = { }

        # The (unresolved) return type of this function
        self.return_type = None
        
        # used to prevent nested functions
        self.in_function = False
    
    def generic_visit(self, n):
        raise InvalidOperationError(
            type(n).__name__ + " is an unsupported operation.", n)
        
    ######################################################################
    ## Statements
    ######################################################################
    def visit_FunctionDef(self, n):
        if self.in_function:
            raise NotImplementedError(
                "Inner concrete_fn definitions are not supported.")
        self.in_function = True
        
        args = self.visit(n.args)
        body = [ self.visit(stmt) for stmt in n.body ]
        return_type = self.return_type
        if return_type is None:
            return_type = cl.cl_void

        return astx.copy_node(n, 
            name=n.name,
            args=args,
            body=body,
            return_type=return_type,
            all_variables=cypy.frozendict(self.all_variables),
            argument_variables=cypy.frozendict(self.argument_variables),
            local_variables=cypy.frozendict(self.local_variables),
            free_variables=cypy.frozendict(self.free_variables)
        )
    
    def visit_arguments(self, n):
        if n.vararg is not None:
            raise InvalidOperationError("Variable arguments are not supported.", n)
        if n.kwarg is not None:
            raise InvalidOperationError("Keyword arguments are not supported.", n)

        args = cypy.flatten_once.ed([ self.visit(arg) for arg in n.args          #@UndefinedVariable
                                     if arg is not None ])
        return _ast.arguments(args=args, 
                              vararg=None, kwarg=None, defaults=[])
    
    def visit_Return(self, n):
        n_value = n.value
        if n_value is None:
            value = None
            return_type = cl.cl_void
        else:
            value = self.visit(n_value)
            return_type = value.unresolved_type
            
        cur_return_type = self.return_type
        if cur_return_type is None:
            self.return_type = return_type
        else:
            self.return_type = MultipleAssignmentType(cur_return_type, 
                                                      return_type)
        
        return astx.copy_node(n, value=value)
    
    def visit_Assign(self, n):
        value = self.visit(n.value)
        # cur_assignment_type communicates with visit_Name
        self.cur_assignment_type = value.unresolved_type
        targets = [ self.visit(target) for target in n.targets ]
        self.cur_assignment_type = None
        
        return astx.copy_node(n,
            targets=targets,
            value=value
        )
    
    _Load = _ast.Load()  # dummy Load used below
    def visit_AugAssign(self, n):
        # We temporarily turn it into the equivalent binary operation to 
        # determine the unresolved type.
        # 1. have to temporarily turn the target from a store to a load
        target = n.target
        orig_ctx = target.ctx 
        target.ctx = self._Load
        # 2. visit the binary operation
        value = self.visit(_ast.BinOp(left=target, op=n.op, right=n.value))
        # 3. restore original ctx 
        target.ctx = orig_ctx
        
        # cur_assignment_type as in Assign
        self.cur_assignment_type = value.unresolved_type
        new = astx.copy_node(n, 
                              target=self.visit(target), 
                              op=value.op, 
                              value=value.right)
        self.cur_assignment_type = None
        
        return new
    
    def visit_For(self, n):
        orelse = n.orelse
        if orelse:
            raise InvalidOperationError(
               "else clauses on for loops are not supported.", n)
        
        # This is a fairly limited form of the for-loop, not even the 
        # complete xrange syntax (negative steps will blow your code up)
        # so we probably want to expand on this somehow. I'm open to
        # ideas. Or just wait till I implement full-blown range support.
        #
        # In the meantime, you can use while loops instead.
        
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
        
        target_store = n.target
        init = self.visit(_ast.Assign(targets=[target_store], value=start))
        
        # to create the guard operation, we need a Load version of the target
        target_load = astx.copy_node(target_store,
                                      ctx=self._Load)
        guard = self.visit(_ast.Compare(left=target_load, comparators=[stop], 
                                        ops=[_ast.Lt()]))
        
        update_stmt = self.visit(_ast.AugAssign(target=target_store, 
                                                op=_ast.Add(), 
                                                value=step))
        
        return astx.copy_node(n,
                               init=init,
                               guard=guard,
                               update_stmt=update_stmt,
                               body=[self.visit(stmt) for stmt in n.body],
                               orelse=[]
                              )

    def visit_While(self, n):
        orelse = n.orelse
        if orelse:
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
            raise InvalidOperationError("Cannot specify globals with `exec`.",
                                   n.globals[0])
        if n.locals:
            raise InvalidOperationError("Cannot specify locals with `exec`.", 
                                   n.locals[0])
        return astx.copy_node(n,
            globals=[],
            locals=[])
    
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
            unresolved_type=UnaryOpType(op, operand)
        )
    
    def visit_BinOp(self, n):
        left = self.visit(n.left)
        op = self.visit(n.op)
        right = self.visit(n.right)
        return astx.copy_node(n,
            left=left,
            op=op,
            right=right,
            unresolved_type=BinOpType(op, left, right)
        )
    
    def visit_Compare(self, n):
        left = self.visit(n.left)
        ops = [self.visit(op) for op in n.ops]
        comparators = [self.visit(expr) for expr in n.comparators]
        
        return astx.copy_node(n,
            left=left,
            ops=ops,
            comparators=comparators,
            unresolved_type=CompareType(left, ops, comparators)
        )

    def visit_BoolOp(self, n):
        op = self.visit(n.op)
        values = [self.visit(expr) for expr in n.values]
        return astx.copy_node(n,
            op=op,
            values=values,
            unresolved_type=BoolOpType(op, values)  
        )
    
    ######################################################################
    ## Expressions
    ######################################################################                
    def visit_IfExp(self, n):
        test = self.visit(n.test)
        body = self.visit(n.body)
        orelse = self.visit(n.orelse)
        
        return astx.copy_node(n,
            test=test,
            body=body,
            orelse=orelse,
            unresolved_type=MultipleAssignmentType(body.unresolved_type, 
                                                   orelse.unresolved_type)
        )

    def visit_Call(self, n):                                                     
        if n.keywords:
            raise InvalidOperationError(
                "Keyword arguments in concrete_fn calls are not supported.", 
                n)
        if n.starargs:
            raise InvalidOperationError(
                "Starred arguments in concrete_fn calls are not supported.",
                n)
        if n.kwargs:
            raise InvalidOperationError(
                "kwargs in concrete_fn calls are not supported.",
                n)
        
        func = self.visit(n.func)
        
        if isinstance(func, _ast.Num):
            # for number literals
            # (special cased because number values should not function this way,
            #  just literals.)
            args = n.args 
            cl_type = literal_suffixes[args[0].id] #@UndefinedVariable
            unresolved_type = InlineConstantType(func.n, cl_type)
        else:
            args = [ self.visit(arg) for arg in n.args ]
            unresolved_type = CallType(func, args)
            
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
            unresolved_type=AttributeType(value, n.attr)
        )
    
    def visit_Subscript(self, n):
        value = self.visit(n.value)
        slice = self.visit(n.slice)
        ctx = self.visit(n.ctx)
        
        return astx.copy_node(n,
            value=value, 
            slice=slice, 
            ctx=ctx,
            unresolved_type=SubscriptType(value, slice)
        )
    
    def visit_Ellipsis(self, n):
        # here in case a virtual type wants to support it
        return astx.copy_node(n)
    
    def visit_Slice(self, n):
        # here in case a virtual type wants to support it
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
            step=step)
    
    def visit_ExtSlice(self, n):
        dims = n.dims
        if dims:
            dims = [self.visit(dim) for dim in dims]
        return astx.copy_node(n, dims=dims)
    
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
        unresolved_type = NameType(id)
        
        if ctx_t is _ast.Load:
            try:
                _check_valid_varname(id)
            except: pass
            else:
                if id not in self.all_variables:
                    # new free variable
                    self.all_variables[id] = self.free_variables[id] = \
                        unresolved_type
                
        elif ctx_t is _ast.Store:
            try:
                current_type = self.all_variables[id]
            except KeyError:
                # new local variable
                _check_valid_varname(id)
                self.all_variables[id] = self.local_variables[id] = \
                    self.cur_assignment_type                     
                
            else:
                if id in self.local_variables:
                    # multiple assignment of a local variable
                    self.local_variables[id] = MultipleAssignmentType(
                        current_type, self.cur_assignment_type)
                elif id in self.free_variables:
                    raise InvalidOperationError(
                        "Free variable %s cannot be assigned to." % id, n)
                # assignment is ok to arguments but it won't change its type
        
        elif ctx_t is _ast.Param:
            self.all_variables[id] = self.argument_variables[id] = \
                unresolved_type
            
        return astx.copy_node(n,
                               id=id,
                               ctx=ctx,
                               unresolved_type=unresolved_type)
        
    def visit_Num(self, n):
        num = n.n
        return astx.copy_node(n,
            unresolved_type=InlineConstantType(num, cl.infer_cl_type(num)))
    
    def visit_Str(self, n):
        return astx.copy_node(n,
            unresolved_type=InlineConstantType(n.s, cl.cl_char.private_ptr))  
    
def _check_valid_varname(id):
    if id in cl.builtins:
        raise InvalidOperationError("Invalid variable name: %s." % id)

##############################################################################
## Unresolved Types
##############################################################################
class InvalidTypeError(Error):
    pass

class UnresolvedType(object):
    """Abstract base class for unresolved types."""

class InlineConstantType(UnresolvedType):
    """Represents the type of an inline constant (strings and numbers)."""
    def __init__(self, constant, cl_type):
        self.constant = constant
        self.cl_type = cl_type
        
    def __repr__(self):
        return self.cl_type.name
    
    @cypy.memoize
    def _resolve(self, visitor): #@UnusedVariable
        return self.cl_type

class NameType(UnresolvedType):
    """The type should be that of the provided named free variable."""
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return "`%s`" % self.name
    
    @cypy.memoize
    def _resolve(self, visitor):
        name = self.name
        
        try: 
            # is it a type name?
            return cl.type_names[name].cl_type
        except KeyError:
            try:
                # is it a built-in?
                return cl.builtins[name].cl_type                
            except KeyError:
                try:
                    # is it a (non-inlined) constant?
                    return cl.infer_cl_type(visitor.constants[name])
                except KeyError:
                    try:
                        # is it an argument?
                        return visitor.explicit_arg_map[name]
                    except KeyError:
                        # it must be a local variable
                        try:
                            value = visitor.local_variables[name]
                        except KeyError:
                            raise InvalidTypeError("Invalid name %s." % name)
                        
                        # let downstream multiple assignment types know we're 
                        # resolving this name so it can maintain a stack
                        prev_resolving_name = visitor._resolving_name
                        visitor._resolving_name = name
                        cl_type = visitor._resolve_type(value) 
                        visitor._resolving_name = prev_resolving_name
                        return cl_type
                    
    def _resolve_value(self, visitor):
        # returns the value associated with the provided name
        name = self.name
        
        try:
            # is it a type name?
            return cl.type_names[name]
        except KeyError:
            try:
                # is it a built-in?
                return cl.builtins[name].cl_type
            except KeyError:
                try:
                    # is it a (non-inlined) constant?
                    return visitor.constants[name]
                except KeyError:
                    raise InvalidTypeError("Invalid name %s." % name)

class AttributeType(UnresolvedType):
    """The type should be that of the provided attribute of the provided value.
    
    A type can implement the _resolve_Attr(visitor, value, attr) method to 
    specify the type of an attribute lookup (in a Load context). If not 
    defined or returns None, an InvalidTypeError is raised.
    
    If this is not defined, the value is looked up, its attribute is looked up
    and its cl_type is inferred.
    """
    def __init__(self, value, attr):
        self.value = value
        self.attr = attr
        
    def __repr__(self):
        return "%s.%s" % (`self.value.unresolved_type`, self.attr)
    
    @cypy.memoize
    def _resolve(self, visitor):
        value = self.value
        unresolved_type = value.unresolved_type
        try:
            value_type = visitor._resolve_type(unresolved_type)
        except Error:
            value_type = None
            
        # protocol for attribute lookup
        try:
            # if _resolve_Attr is defined, call that
            _resolve_Attr = value_type._resolve_Attr
        except AttributeError:
            try:
                # otherwise, try to resolve the attribute itself and 
                # get its cl_type
                _resolve_value = unresolved_type._resolve_value
            except AttributeError: pass
            else:
                value = _resolve_value(visitor)
                attr = self.attr
                try:
                    attr_value = getattr(value, attr)
                except AttributeError: pass
                else:
                    try:
                        return cl.infer_cl_type(attr_value)
                    except cl.Error: pass
        else:
            cl_type = _resolve_Attr(visitor, value, self.attr)
            if cl_type is not None:
                return cl_type
        
        if value_type is None:
            raise InvalidTypeError("Attribute '%s' could not be found." 
                                   % self.attr)
        else:
            raise InvalidTypeError(
                "Attribute '%s' is invalid for object of type %s." %
                (self.attr, value_type.name))
        
    def _resolve_value(self, visitor):
        value = self.value._resolve_value(visitor)
        attr = self.attr
        try:
            return getattr(value, attr)
        except AttributeError:
            raise InvalidTypeError("Attribute '%s' could not be found." % attr)

class SubscriptType(UnresolvedType):
    """The type should be that of the provided subscript of the provided value.
    
    A type can implement the _resolve_Subscript(visitor, value, slice) method 
    to specify the type of a subscript lookup (in a Load context.)
    """
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
        except AttributeError: pass
        else:
            cl_type = _resolve_Subscript(visitor, value, self.slice)
            if cl_type is not None:
                return cl_type
        raise InvalidTypeError(
            "Subscript access is not defined for values of type %s." 
            % value_type.name)
    
class UnaryOpType(UnresolvedType):
    """The type should be that of the provided unary operator applied to the 
    provided value.
    
    A type can implement the _resolve_UnaryOp(visitor, op, left) method to 
    specify the type of a unary operator application. 
    
    If not specified or it returns None, an InvalidTypeError is raised.
    """
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
        except AttributeError: pass
        else:
            cl_type = _resolve_UnaryOp(self, op, left)
            if cl_type is not None:
                return cl_type
        raise InvalidTypeError(
           "Unary %s is not valid for values of type %s." % 
           (astx.C_all_operators[type(op)], left_type.name))

class BinOpType(UnresolvedType):
    """The type should be that of the provided binary operator applied to the
    two provided values.
    
    A type can implement the _resolve_BinOp_left(visitor, left, op, right)
    method to specify the type of a binary operator application where it is 
    present on the left side.
    
    If not specified, or this returns None, a type can implement the 
    _resolve_BinOp_right(visitor, left, op, right) method to specify the
    type of a binary operator application where it is present on the right
    side.
    
    If it returns None or is not specified, an InvalidTypeError is raised.
    """
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
        try:
            _resolve_BinOp = left_type._resolve_BinOp_left
        except AttributeError:
            right_unresolved_type = right.unresolved_type
            right_type = visitor._resolve_type(right_unresolved_type)
            try:                
                _resolve_BinOp = right_type._resolve_BinOp_right
            except AttributeError: pass
        else:
            cl_type = _resolve_BinOp(visitor, left, op, right)
            if cl_type is not None:
                return cl_type
            else:
                right_unresolved_type = right.unresolved_type
                right_type = visitor._resolve_type(right_unresolved_type)
                try:
                    _resolve_BinOp = right_type._resolve_BinOp_right
                except AttributeError: pass
        if _resolve_BinOp is not None:
            cl_type = _resolve_BinOp(visitor, left, op, right)
            if cl_type is not None:
                return cl_type            
        raise InvalidTypeError(
            "Binary %s operation is not valid for values of type %s and %s." %
            (astx.C_all_operators[type(op)], left_type.name, right_type.name))

class CompareType(UnresolvedType):
    """The type should be the resulting type of a comparison operation.
    
    Any of the types in the chain can implement the _resolve_Comparison(visitor,
    left, ops, comparators, position) method to determine the return type of 
    the comparison. See the Python ast module documentation for a description
    of why this is somewhat unintuitive (to support constructs like a < b < c).
    The position argument gives the position of the operand for which dispatch
    operates on, where 0 is ``left`` and 1 and higher are in ``comparators``.
    
    If none of the operated types implement comparison or they returned None,
    an InvalidTypeError is raised.
    """
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
        while True:
            cur_type = _resolve_type(cur.unresolved_type)
            try:
                _resolve = cur_type._resolve_Compare
            except AttributeError:
                pass
            else:
                cl_type = _resolve(visitor, left, ops, comparators, position)
                if cl_type is not None:
                    self.position = position
                    return cl_type
            try:
                cur = iter.next()
                position += 1
            except StopIteration:
                break
            
        raise InvalidTypeError(
            "Comparisons are not supported for specified value types.")

class BoolOpType(UnresolvedType):
    """The type should be the result of applying the sequence of boolean ops.
    
    Any type in the chain can implement the _resolve_BoolOp(visitor, ops, 
    values, position) method to determine the return type of the boolean op.
    The position argument gives the position of the operand for which dispatch
    operates on.
    
    If none of the values implement boolean ops or they returned None, an 
    InvalidTypeError is raised.
    """
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
                cl_type = _resolve(visitor, op, values, position)
                if cl_type is not None:
                    self.position = position
                    return cl_type
        
        raise InvalidTypeError(
            "Boolean operations are not supported for specified value types.")
        
class MultipleAssignmentType(UnresolvedType):
    """The type should be the dominant type for a variable assigned with an
    expression of type ``prev`` and an expression of type ``new``.
    
    A previous type can implement the _resolve_MultipleAssignment_left(new_type) 
    method to specify the resulting type. If not specified or returns None, the 
    new can specify the _resolve_MultipleAssignment_new(prev_type) method. If
    this is not specified or returns None, an InvalidTypeError is raised.
    
    Note that fully resolved types are passed as arguments rather than 
    ast nodes to these functions.
    """
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
            cl_type = _resolve(new_type)
            if cl_type is not None:
                return cl_type
            else:
                try:
                    _resolve = new_type._resolve_MultipleAssignment_new
                except AttributeError: pass
        if _resolve is not None:
            cl_type = _resolve(prev_type)
            if cl_type is not None:
                return cl_type
        
        raise InvalidTypeError(
            "Incompatible assignment types %s and %s." % 
            (prev_type.name, new_type.name))
        
class CallType(UnresolvedType):
    """The type should the return type of the function specified by the name 
    type passed with arguments of the specified types.
    
    A callable type can implement the _resolve_Call(visitor, func, args) method
    to specify the resulting type of the call. If not specified or returns
    None, an InvalidTypeError is raised.
    """
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
            cl_type = _resolve(visitor, func, args)
            if cl_type is not None:
                return cl_type
            
        raise InvalidTypeError("Type '%s' is not callable." % func_type.name)
    
################################################################################
# General type resolution
################################################################################
@cypy.memoize
def _type_resolve_Compare(self, visitor, left, ops, comparators, position): #@UnusedVariable
    resolve = visitor._resolve_type
    left_type = resolve(left.unresolved_type)
    if not isinstance(left_type, cl.ScalarType):
        return
    
    for right in comparators:
        right_type = resolve(right.unresolved_type)
        if not isinstance(right_type, cl.ScalarType):
            return

    return cl.cl_bool
cl.ScalarType._resolve_Compare = _type_resolve_Compare

@cypy.memoize
def _type_resolve_BoolOp(self, visitor, op, values, position): #@UnusedVariable
    resolve = visitor._resolve_type
    for value in values:
        value_type = resolve(value.unresolved_type)
        if not isinstance(value_type, cl.BuiltinType):
            return
    
    return cl.cl_bool
cl.ScalarType._resolve_BoolOp = _type_resolve_BoolOp
    
################################################################################
# Integer type resolution
################################################################################
@cypy.memoize
def _integer_resolve_UnaryOp(self, visitor, op, left): #@UnusedVariable
    min_sizeof = self.min_sizeof
    if min_sizeof < 4: # char, shorts are widened according to C99
        if self.unsigned:
            if isinstance(op, _ast.USub):
                return cl.cl_int
            return cl.cl_uint
        return cl.cl_int
    
    if isinstance(op, _ast.USub):
        return self.signed_variant
    return self
cl.IntegerType._resolve_UnaryOp = _integer_resolve_UnaryOp

@cypy.memoize
def _integer_resolve_BinOp_left(self, visitor, left, op, right):
    right_type = visitor._resolve_type(right.unresolved_type)
    if isinstance(right_type, cl.FloatType):
        return right_type._resolve_BinOp_left(visitor, right, op, left)
    
    if isinstance(right_type, cl.IntegerType):
        min_sizeof = self.min_sizeof
        if min_sizeof < 4: # char, short on the left
            if self.unsigned:
                if right_type.min_sizeof >= 4:
                    return right_type.unsigned_variant
                return cl.cl_uint
            if right_type.min_sizeof >= 4:
                return right_type
            if right_type.unsigned:
                return cl.cl_uint
            return cl.cl_int
        
        if right_type.min_sizeof < 4: # char, short on the right, recurse
            return right_type._resolve_BinOp_left(visitor, right, op, left)
        
        right_mso = right_type.max_sizeof
        self_mso = self.max_sizeof
        
        if self.unsigned or right_type.unsigned:
            if self_mso >= right_mso:
                return self.unsigned_variant
            return right_type.unsigned_variant
        else:
            if self_mso >= right_mso:
                return self
            return right_type
        
    # pointer arithmetic
    if isinstance(op, _ast.Add) and isinstance(right_type, cl.PtrType):
        return right_type
cl.IntegerType._resolve_BinOp_left = \
    _integer_resolve_BinOp_left

@cypy.memoize
def _integer_resolve_MultipleAssignment_prev(self, new):
    if self is new:
        return self
    
    if isinstance(new, cl.FloatType):
        return new._resolve_MultipleAssignment_prev(self)
    
    if isinstance(new, cl.IntegerType):
        new_mso = new.max_sizeof
        self_mso = self.max_sizeof
        
        if self.unsigned or new.unsigned:
            if new_mso >= self_mso:
                return new.unsigned_variant
            return self.unsigned_variant
        if new_mso >= self_mso:
            return new
        return self
cl.IntegerType._resolve_MultipleAssignment_prev = \
    _integer_resolve_MultipleAssignment_prev

################################################################################
# Float type resolution
################################################################################
@cypy.memoize
def _float_resolve_UnaryOp(self, visitor, op, left): #@UnusedVariable
    if isinstance(op, (_ast.USub, _ast.UAdd)):    
        if self.min_sizeof < 4: # half
            return cl.cl_float
        return self
cl.FloatType._resolve_UnaryOp = _float_resolve_UnaryOp

@cypy.memoize
def _float_resolve_BinOp_left(self, visitor, left, op, right): #@UnusedVariable
    right_type = visitor._resolve_type(right.unresolved_type)
    
    if isinstance(right_type, cl.FloatType):
        self_sizeof = self.min_sizeof
        right_sizeof = right_type.min_sizeof
        if self_sizeof >= right_sizeof:
            if self_sizeof > 2:
                return self
            return cl.cl_float
        if right_sizeof > 2:
            return right_type
        return cl.cl_float
    
    if isinstance(right_type, cl.IntegerType):
        if self.min_sizeof > 2:
            return self
        return cl.cl_float
cl.FloatType._resolve_BinOp_left = _float_resolve_BinOp_left

@cypy.memoize
def _float_resolve_MultipleAssignment_prev(self, new):
    if isinstance(new, cl.FloatType):
        if new.min_sizeof >= self.min_sizeof:
            return new
        return self
    if isinstance(new, cl.IntegerType):
        return self
cl.FloatType._resolve_MultipleAssignment_prev = \
    _float_resolve_MultipleAssignment_prev
    
################################################################################
# Pointer type resolution
################################################################################
@cypy.memoize
def _ptr_resolve_Subscript(self, visitor, value, slice): #@UnusedVariable
    slice_type = visitor._resolve_type(slice.unresolved_type)
    if not isinstance(slice_type, cl.IntegerType):
        raise InvalidTypeError(
            "Subscript index must be an integer, but saw a %s." 
            % slice_type.name)
    return self.target_type
cl.PtrType._resolve_Subscript = _ptr_resolve_Subscript
    
@cypy.memoize
def _ptr_resolve_BinOp_left(self, visitor, left, op, right): #@UnusedVariable
    right_type = visitor._resolve_type(right.unresolved_type)
    
    if isinstance(op, _ast.Sub) and isinstance(right_type, self.__class__):
        return cl.cl_ptrdiff_t
    
    if isinstance(right_type, cl.IntegerType) and \
       isinstance(op, (_ast.Add, _ast.Sub)):
        return self
cl.PtrType._resolve_BinOp_left = _ptr_resolve_BinOp_left

@cypy.memoize
def _ptr_resolve_MultipleAssignment_prev(self, new):
    if self is new:
        return self
    
    if isinstance(new, cl.PtrType) and new.address_space == self.address_space:
        if self.target_type is cl.cl_void:
            return new
        if new.target_type is cl.cl_void:
            return self
        
    if isinstance(new, cl.IntegerType): 
        # mostly for NULL pointers but any integer can be assigned to 
        # a pointer variable
        return self
cl.PtrType._resolve_MultipleAssignment_prev = \
    _ptr_resolve_MultipleAssignment_prev
    
################################################################################
# Vector type resolution
################################################################################
@cypy.memoize
def _vec_resolve_UnaryOp(self, visitor, op, operand):
    base_type = self.base_type
    if isinstance(base_type, cl.IntegerType):
        if isinstance(op, _ast.USub) and not base_type.unsigned:
            return self
        return self

    elif isinstance(base_type, cl.FloatType):
        if isinstance(op, (_ast.UAdd, _ast.USub)):
            return self
cl.VectorType._resolve_UnaryOp = _vec_resolve_UnaryOp

@cypy.memoize
def _vec_resolve_BinOp(self, visitor, right):
    resolve = visitor._resolve_type
    right_type = resolve(right)
    if right_type is self:
        return self
    
    base_type = self.base_type
    if isinstance(right_type, cl.IntegerType) \
       and isinstance(base_type, cl.IntegerType):
        if right_type.max_sizeof <= base_type.min_sizeof:
            return self
        
    if isinstance(right_type, cl.FloatType) \
       and isinstance(base_type, cl.FloatType):
        if right_type.max_sizeof <= base_type.min_sizeof:
            return self
cl.VectorType._resolve_BinOp_left = lambda self, visitor, left, op, right: \
    _vec_resolve_BinOp(self, visitor, right)
cl.VectorType._resolve_BinOp_right = lambda self, visitor, left, op, right: \
    _vec_resolve_BinOp(self, visitor, left)
    
@cypy.memoize
def _vec_resolve_Attribute(self, visitor, obj, attr):
    if attr == "lo" or attr == "hi" or attr == "even" or attr == "odd":
        return cl.vector_types[self.base_type][self.n / 2]
    
    if attr[0] == "s" and len(attr) == 2:
        try:
            idx = int(attr[1], 16)
        except ValueError: pass
        else:
            if idx <= self.n:
                return self.base_type
    else:
        ok = True
        acceptable = ("x", "y", "z", "w")[0:(self.n+1)]
        for idx in attr:
            if idx not in acceptable:
                ok = False
                break
            
        if ok:
            if len(attr) == 1:
                return self.base_type
            else:
                try:
                    return cl.vector_types[self.base_type][len(attr)]
                except KeyError: pass
cl.VectorType._resolve_Attribute = _vec_resolve_Attribute

# TODO: this isn't being called correctly
@cypy.memoize
def _vec_resolve_AssignAttribute(self, visitor, obj, attr, value):
    n = None
    
    if attr == "lo" or attr == "hi" or attr == "even" or attr == "odd":
        n = self.n / 2
        
    if attr[0] == "s" and len(attr) == 2:
        try:
            idx = int(attr[1], 16)
        except ValueError: pass
        else:
            if idx <= self.n:
                n = 1
                
    else:
        ok = True
        acceptable = ("x", "y", "z", "w")[0:(self.n+1)]
        accepted = set()
        for idx in attr:
            if idx not in acceptable:
                ok = False
                break
            elif idx in accepted:
                ok = False
                break
            else:
                accepted.add(idx)
        
        if ok:
            n = len(attr)
            
    if n is not None:
        value_type = visitor._resolve_type(value)
        if n == 1:
            required_type = self.base_type
        else:
            required_type = cl.vector_types[self.base_type][n]
        
        if value_type is required_type:
            return True

        base_type = self.base_type
        if isinstance(value_type, cl.IntegerType) \
           and isinstance(base_type, cl.IntegerType) \
           and base_type.min_sizeof <= value_type.max_sizeof:
            return True
        
        elif isinstance(value_type, cl.FloatType) \
             and isinstance(base_type, cl.FloatType) \
             and base_type.min_sizeof <= value_type.max_sizeof:
            return True
cl.VectorType._resolve_AssignAttribute = _vec_resolve_AssignAttribute

@cypy.memoize
def _vec_resolve_AugAssignAttribute(self, visitor, obj, attr, op, value):
    return _vec_resolve_AssignAttribute(self, visitor, obj, attr, value)
cl.VectorType._resolve_AugAssignAttribute = _vec_resolve_AugAssignAttribute

# TODO: multiple assignment

##############################################################################
# Generic multiple assignment 
##############################################################################
@cypy.memoize
def _generic_resolve_MultipleAssignment_prev(self, new):
    if self is new: return self
cl.Type._resolve_MultipleAssignment_prev = \
    _generic_resolve_MultipleAssignment_prev

##############################################################################
## Virtual Types
##############################################################################
class VirtualType(object):
    """Base class for virtual cl.oquence types.
    
    That is, types that don't correspond directly to OpenCL types, and are 
    only meaningful in cl.oquence code. They will be translated into code 
    which only uses OpenCL types.
    """
    constant_value = None
    """The constant value associated with this virtual type, or None."""

class FnType(VirtualType):
    """Base class for cl.oquence function types of various sorts."""
    pass

class GenericFnType(FnType):
    """The type of cl.oquence GenericFn's."""
    def __init__(self, generic_fn):
        self.generic_fn = self.constant_value = generic_fn
        
    def __repr__(self):
        return self.generic_fn.__name__
    
    @cypy.memoize
    def _resolve_Call(self, visitor, func, args): #@UnusedVariable
        explicit_arg_types = tuple(visitor._resolve_type(arg.unresolved_type) 
                                   for arg in args)
        return self.generic_fn._get_concrete_fn(explicit_arg_types).return_type    
cypy.interned(GenericFnType)

class ConcreteFnType(FnType):
    """The type of cl.oquence ConcreteFn's."""
    def __init__(self, concrete_fn):
        self.concrete_fn = self.constant_value = concrete_fn
        
    def __repr__(self):
        return self.concrete_fn.full_name
    
    @cypy.memoize
    def _resolve_Call(self, visitor, func, args): #@UnusedVariable
        concrete_fn = self.concrete_fn
        explicit_arg_types = concrete_fn.explicit_arg_types
        arg_types = tuple(visitor._resolve_type(arg.unresolved_type) 
                          for arg in args)
        if arg_types != explicit_arg_types:
            raise InvalidTypeError(
                "Argument types are not compatible. Got %s, expected %s." % 
                (arg_types, explicit_arg_types))
        return self.concrete_fn.return_type
cypy.interned(ConcreteFnType)
    
class BuiltinFnType(FnType):
    """The type of OpenCL builtin function stubs (:class:`cl.BuiltinFn`)."""
    def __init__(self, builtin):
        self.builtin = self.constant_value = builtin
        
    def __repr__(self):
        return self.builtin.name
    
    @cypy.memoize
    def _resolve_Call(self, visitor, func, args): #@UnusedVariable
        builtin = self.builtin
        arg_types = tuple(visitor._resolve_type(arg.unresolved_type) 
                          for arg in args)
        return builtin.return_type_fn(*arg_types)
cypy.interned(BuiltinFnType)

@property
def _builtin_cl_type(self):
    return BuiltinFnType(self)
cl.BuiltinFn.cl_type = _builtin_cl_type

class AddressofType(object):
    """The type of the addressof macro.
    
    (addressof is a macro because addressof(x[y]) should have the type of the 
     pointer x, it cannot simply evaluate the type of x[y] and then make it 
     into a pointer because that would be ambiguous wrt address space.)
    """
    def _resolve_Call(self, visitor, func, args): #@UnusedVariable
        if len(args) != 1:
            raise InvalidTypeError(
                "The addressof operator only takes one argument.")
        
        arg = args[0]
        # even if its a subscript, we want to make sure it typechecks
        arg_type = visitor._resolve_type(arg.unresolved_type)
        if isinstance(arg, _ast.Subscript):
            return visitor._resolve_type(arg.value.unresolved_type)
        return arg_type.private_ptr
# injected as cl_type in __init__ to avoid circular reference problems
    
class TypeType(VirtualType):
    """Base class for the types of types."""
    def __init__(self, type):
        self.type = type
        
    @cypy.memoize
    def _resolve_Call(self, visitor, func, args): #@UnusedVariable
        # for type cast syntax
        if len(args) == 1:
            arg = args[0]
            arg_type = visitor._resolve_type(arg.unresolved_type) #@UnusedVariable
            if not isinstance(arg_type, (cl.ScalarType, cl.PtrType)):
                raise InvalidTypeError("Cannot cast a %s to a %s." % 
                                       (arg_type.name, self.name))
            return self.type
        else:
            raise InvalidTypeError("Casts can only take one argument.")
    
@property
def _type_cl_type(self):
    return TypeType(self)
cl.Type.cl_type = _type_cl_type

