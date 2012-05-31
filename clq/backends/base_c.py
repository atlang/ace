import ast as _ast

import cypy
import cypy.astx as astx
import cypy.cg as cg

import clq
from clq import TypeResolutionError

class Backend(clq.Backend):
    """A backend that centralizes logic common to C-based languages."""
    def __init__(self, name):
        clq.Backend.__init__(self, name)
        
    def init_context(self, context):
        context.modifiers = [ "__kernel" ]
        context.declarations = [ ]
        context.end_stmt = ";\n"
        
    ######################################################################
    ## Generating Program Items
    ######################################################################
    def generate_program_item(self, context):
        g = cg.CG()
        g.append(cypy.join(cypy.cons(context.modifiers, 
                                     (context.return_type.name,)), " "))
        name = self._generate_name(context)
        g.append((" ", name, "("))
        g.append(cypy.join(self._yield_arg_str(context), ", "))
        g.append((") {\n", context.tab))
        g.append((cypy.join(context.declarations, "\n"), "\n\n"))
        g.append(context.stmts)
        g.append((context.untab, "\n}\n"))
        return clq.ProgramItem(name, g.code)
        
    def _yield_arg_str(self, context):
        concrete_fn = context.concrete_fn
        for arg_name, arg_type in zip(concrete_fn.generic_fn.arg_names, 
                                      concrete_fn.arg_types):
            if not isinstance(arg_type, clq.VirtualType):
                yield (arg_type.name, " ", arg_name)
    
    def _generate_name(self, context):
        # TODO: proper namespacing
        return context.concrete_fn.generic_fn.name
    
    def _add_declaration(self, context, id, type):
        decl = type.name + " " + id + ";"
        decls = context.declarations
        if decl not in decls:
            decls.append(decl)
            
    ######################################################################
    ## Types
    ######################################################################                            
    def void_type(self, context, node):
        return self.void_t
    
    void_t = None
    
    def bool_type(self, context, node):
        return self.bool_t
    
    bool_t = None
    
    def resolve_Num(self, context, node):
        n = node.n
        if cypy.is_int_like(n):
            return self.int_t
        else:
            return self.float_t
        
    def generate_Num(self, context, node):
        code = str(node.n)
        
        return astx.copy_node(node,
            code = code                  
        )

    int_t = None
    float_t = None
    
    def resolve_Str(self, context, node):
        return self.string_t
    
    def generate_Str(self, context, node):
        code = cypy.string_escape(node.s)
        
        return astx.copy_node(node,
            code = code)
    
    string_t = None
    
    ######################################################################
    ## Code Generation
    ######################################################################
    def generate_For(self, context, node):
        context.stmts.append("for (")
        
        orig_end_stmt = context.end_stmt
        
        context.end_stmt = "; "
        context.visit(node.init)
        init = context.body.pop()
        
        guard = context.visit(node.guard)
        context.stmts.append((guard.code, "; "))
         
        context.end_stmt = (") {\n", context.tab)
        context.visit(node.update_stmt)
        update_stmt = context.body.pop()
        
        context.end_stmt = orig_end_stmt
        
        parent_body = context.body
        body = context.body = [ ]
        for stmt in node.body:
            context.visit(stmt)
        context.body = parent_body
        
        context.stmts.append((context.untab, "}\n"))
        
        context.body.append(astx.copy_node(node,
            target=astx.deep_copy_node(node.target),
            iter=astx.copy_node(node.iter),
            body=body,
            orelse=[],
            
            init=init,
            guard=guard,
            update_stmt=update_stmt
        ))
    
    def generate_While(self, context, node):
        test = context.visit(node.test)
        context.stmts.append(("while (", test.code, ") {\n", context.tab))
        
        parent_body = context.body
        body = context.body = [ ]
        for stmt in node.body:
            context.visit(stmt)
        context.body = parent_body
        
        context.stmts.append((context.untab, "}\n"))
        
        context.body.append(astx.copy_node(node,
            test=test,
            body=body,
            orelse=[]
        ))
                            
    def generate_If(self, context, node):
        test = context.visit(node.test)
        context.stmts.append(("if (", test.code, ") {\n", context.tab))
        
        parent_body = context.body
        body = context.body = [ ]
        for stmt in node.body:
            context.visit(stmt)
        context.body = parent_body
        
        orelse = node.orelse
        num_else = len(orelse)
        if num_else == 0:
            context.stmts.append((context.untab, "}\n"))
            new_orelse = [ ]
        elif num_else == 1:
            context.stmts.append((context.untab, 
                                  "} else ", 
                                  context.tab))
            new_orelse = [context.visit(orelse[0])]
            context.stmts.append(context.untab)
        else:
            context.stmts.append((context.untab,
                                  "} else {\n", context.tab))
            new_orelse = context.body = [ ]
            for stmt in orelse:
                context.visit(stmt)
            context.body = parent_body
            context.stmts.append((context.untab, "}\n"))
            
        context.body.append(astx.copy_node(node,
            test=test,
            body=body,
            orelse=new_orelse
        ))
        
    def generate_Expr(self, context, node):
        value = context.visit(node.value)
        context.stmts.append((value.code, context.end_stmt))
        context.body.append(astx.copy_node(node,
            value=value
        ))
        
    def generate_Pass(self, context, node):
        context.stmts.append(context.end_stmt)
        context.body.append(astx.copy_node(node))
        
    def generate_Break(self, context, node):
        context.stmts.append(("break", context.end_stmt))
        context.body.append(astx.copy_node(node))
        
    def generate_Continue(self, context, node):
        context.stmts.append(("continue", context.end_stmt))
        context.body.append(astx.copy_node(node))
        
    def generate_Exec(self, context, node):
        body = node.body
        context.stmts.append((body.s, "\n"))
        context.body.append(astx.copy_node(node,
            body=astx.copy_node(body),
            globals=[],
            locals=[]
        ))
    
    ######################################################################
    ## Operator Expressions
    ######################################################################
    def generate_op(self, context, op):
        return astx.copy_node(op, code=astx.C_all_operators[type(op)])

    ######################################################################
    ## Other Expressions
    ######################################################################                    
    def generate_IfExp(self, context, node):
        test = context.visit(node.test)
        body = context.visit(node.body)
        orelse = context.visit(node.orelse)
        
        code = ("((", test.code, ") ? (",
                      body.code, ") : (",
                      orelse.code, ")")
                
        return astx.copy_node(node,
            test=test,
            body=body,
            orelse=orelse,
            
            code=code
        )
        
class Type(clq.Type):
        
    min_sizeof = None
    max_sizeof = None

    def validate_Return(self, context, node):
        return # no error = ok
    
    def generate_Return(self, context, node):
        if context.return_type == context.backend.void_type(context, node):
            value = None
            context.stmts.append((self.generate_Return_stmt(None), 
                                  context.end_stmt))
        else:
            value = context.visit(node.value)
            context.stmts.append((self.generate_Return_stmt(value.code), 
                                  context.end_stmt))
                    
        context.body.append(astx.copy_node(node,
            value=value
        ))
        
    @classmethod
    def generate_Return_stmt(cls, value_code):
        if value_code is None:
            return "return"
        else:
            return ("return ", value_code)
        
    def validate_Assign(self, context, node):
        return # no error = ok
    
    def generate_Assign(self, context, node):
        target = context.visit(node.targets[0])
        value = context.visit(node.value)
        
        # add declaration
        id = target.id
        local_variables = context.generic_fn.local_variables
        if id in local_variables:
            context.backend._add_declaration(context, 
                id, local_variables[id].resolve(context))

        context.stmts.append((self.generate_Assign_stmt(target.code, value.code), 
                              context.end_stmt))
        context.body.append(astx.copy_node(node,
            targets=[target],
            value=value
        ))
                
    @classmethod
    def generate_Assign_stmt(cls, target_code, value_code):
        return (target_code, " = ", value_code)
    
    @classmethod
    def generate_AugAssign_stmt(cls, target_code, op_code, value_code):
        return (target_code, " ", op_code, "= ", value_code)                                                              
    
class VoidType(Type):
    def __init__(self, name='void'):
        Type.__init__(self, name)
                
    min_sizeof = 0
    max_sizeof = 0
    
    def validate_Return(self, context, node):
        # Does not get called for a return statement without a value, which is
        # the correct way to return void.
        raise clq.TypeResolutionError(
            "Cannot return a value of type 'void'.", node.value)
    
    def validate_Assign(self, context, node):
        raise clq.TypeResolutionError(
            "Cannot assign to a variable of type 'void'.", node.targets[0])
    
class BoolType(Type):
    def __init__(self, name='bool'):
        Type.__init__(self, name)
        
    def resolve_BoolOp(self, context, node):
        right_type = node.values[1].unresolved_type.resolve(context)
        if not isinstance(right_type, BoolType):
            raise TypeResolutionError(
                "Cannot use a boolean operation on operands of types '%s' and '%s'." % 
                (self.name, right_type.name), node)
            
        return right_type
    
    def generate_BoolOp(self, context, node):
        left = context.visit(node.values[0])
        right = context.visit(node.values[1])
        op = context.visit(node.op)
        
        code = ("(", left.code, " ", op.code, " ", right.code, ")")
        
        return astx.copy_node(node,
            op=op,
            values=[left, right],
            
            code=code
        )
        
    def resolve_UnaryOp(self, context, node):
        if isinstance(node.op, _ast.Not):
            return self
        else:
            raise TypeResolutionError(
                "Invalid unary operation on operand of type '%s'." % 
                self.name, node.operand)
            
    def generate_UnaryOp(self, context, node):
        op = context.visit(node.op)
        operand = context.visit(node.operand)
        
        code = ("(", op.code, "(", operand.code, "))")
        return astx.copy_node(node,
            op=op,
            operand=operand,
            
            code=code
        )
    
class ScalarType(Type):
    min = None
    """The minimum value this type can take.
    
    None if device-dependent.
    """

    max = None
    """The maximum value this type can take.
    
    None if device-dependent.
    """
    
    def make_literal(self, bare_literal):
        """Converts a bare literal into an appropriately typed literal.

        Adds a suffix, if one exists. If not, uses a cast.
        """
        literal_suffix = self.literal_suffix
        bare_literal = str(bare_literal)
        if literal_suffix is None:
            return "(%s)%s" % (self.name, bare_literal)
        else:
            return "%s%s" % (bare_literal, literal_suffix)

    literal_suffix = None
    """The suffix appended to literals for this type, or None.

    (e.g. 'f' for float)

    Note that either case can normally be used. The lowercase version is
    provided here.

    Raw integer and floating point literals default to int and double,
    respectively, unless the integer exceeds the bounds for 32-bit integers
    in which case it is promoted to a long.
    """
    
    def resolve_Compare(self, context, node):
        right_type = node.comparators[0].unresolved_type.resolve(context)
        if not isinstance(right_type, ScalarType):
            raise TypeResolutionError(
                "Cannot compare values of type '%s' and '%s'." % 
                (self.name, right_type.name), node)
        
        return context.backend.bool_t
    
    def generate_Compare(self, context, node):
        left = context.visit(node.left)
        right = context.visit(node.comparators[0])
        op = context.visit(node.ops[0])
        
        code = (left.code, " ", op.code, " ", right.code)
        
        return astx.copy_node(node,
            left=left,
            ops=[op],
            comparators=[right],
            
            code=code
        )
        
    def string_name(self):
        return string_t
        
class IntegerType(ScalarType):
    unsigned = False
    """A boolean indicating whether this is an unsigned integer type."""
    
    signed_variant = None
    """If integer, this provides the signed variant of the type."""
    
    unsigned_variant = None
    """If integer, this provides the unsigned variant of the type."""
    
    def resolve_UnaryOp(self, context, node):
        op = node.op
        if isinstance(op, _ast.Not):
            raise TypeResolutionError(
                "The 'not' operator is not supported for values of type '%s'." % 
                self.name, node.operand)
        else:
            min_sizeof = self.min_sizeof
            if min_sizeof < 4:
                # chars and shorts are widened according to C99
                if self.unsigned:
                    if isinstance(node.op, _ast.USub):
                        return context.backend.int_t
                    return context.backend.uint_t
                return context.backend.int_t
            elif isinstance(op, _ast.USub):
                # unary subtraction returns a signed integer always
                return self.signed_variant
            else:
                return self
    
    def generate_UnaryOp(self, context, node):
        op = context.visit(node.op)
        operand = context.visit(node.operand)
        
        code = ("(", op.code, "(", operand.code, "))")
        
        return astx.copy_node(node,
            op=op,
            operand=operand,
            
            code=code
        )
         
    def resolve_BinOp(self, context, node):
        right_type = node.right.unresolved_type.resolve(context)
        try:
            return self._resolve_BinOp(node.op, right_type, context.backend)
        except TypeResolutionError as e:
            if e.node is None:
                e.node = node
            raise e
        
    @cypy.memoize
    def _resolve_BinOp(self, op, right_type, backend):        
        if isinstance(right_type, FloatType):
            return right_type._resolve_BinOp(op, self, backend)
        
        elif isinstance(right_type, IntegerType):
            min_sizeof = self.min_sizeof
            if min_sizeof < 4: # char, short on left
                if self.unsigned:
                    if right_type.min_sizeof >= 4:
                        return right_type.unsigned_variant
                    return backend.uint_t
                elif right_type.min_sizeof >= 4:
                    return right_type
                elif right_type.unsigned:
                    return backend.uint_t
                else:
                    return backend.int_t
            elif right_type.min_sizeof < 4:
                return right_type._resolve_BinOp(op, self, backend)
            else:
                right_max = right_type.max_sizeof
                self_max = self.max_sizeof
                
                if self.unsigned or right_type.unsigned:
                    if self_max >= right_max:
                        return self.unsigned_variant
                    else:
                        return right_type.unsigned_variant
                else:
                    if self_max >= right_max:
                        return self
                    else:
                        return right_type
                    
        # pointer arithmetic
        elif isinstance(right_type, PtrType) and isinstance(op, _ast.Add):
            return right_type
    
    def generate_BinOp(self, context, node):
        # TODO: abstract this away for all the bin op supporters
        left = context.visit(node.left)
        op = context.visit(node.op)
        right = context.visit(node.right)
        
        code = ("(", left.code, " ", op.code, " ", right.code, ")")
        
        return astx.copy_node(node,
            left=left,
            op=op,
            right=right,
            
            code=code
        )
    
    def resolve_MultipleAssignment(self, context, prev, new, node):
        new_type = new.resolve(context)
        try:
            return self._resolve_MultipleAssignment(new_type)
        except TypeResolutionError as e:
            if e.node is None:
                e.node = node
            raise e
    
    @cypy.memoize
    def _resolve_MultipleAssignment(self, new_type):
        if self == new_type:
            return new_type
        elif isinstance(new_type, FloatType):
            return new_type._resolve_MultipleAssignment(self)
        elif isinstance(new_type, IntegerType):
            new_max = new_type.max_sizeof
            self_max = self.max_sizeof
            
            if self.unsigned or new_type.unsigned:
                if new_max >= self_max:
                    return new_type.unsigned_variant
                else:
                    return self.unsigned_variant
            elif new_max >= self_max:
                return new_type
            else:
                return self
        else:
            raise TypeResolutionError(
                "Cannot assign a value of type '%s' to a variable of type '%s'." \
                % (new_type.name, self.name), None)
    
    def validate_AugAssign(self, context, node):
        # TODO: Need to check value too right?
        context.concrete_fn.generic_fn.local_variables[node.target.id].resolve(context)

    def generate_AugAssign(self, context, node):
        target = context.visit(node.target)
        value = context.visit(node.value)
        op = context.visit(node.op)
        
        # add declaration
        id = target.id
        local_variables = context.generic_fn.local_variables
        if id in local_variables:
            context.backend._add_declaration(context, 
                id, local_variables[id].resolve(context))

        # add code        
        context.stmts.append((self.generate_AugAssign_stmt(
            target.code,
            op.code,
            value.code
        ), context.end_stmt))
        
        # add node
        context.body.append(astx.copy_node(node,
            target=target,
            value=value,
            op=op
        ))
            
    #def resolve_Call(self, context, node):
        # TODO: implement this
        #pass
    
    #def generate_Call(self, context, node):
        # TODO: implement this
        #pass
    
class FloatType(ScalarType):
    @property
    def sizeof(self):
        return self.min_sizeof
    
    def resolve_UnaryOp(self, context, node):
        op = node.op
        if isinstance(op, (_ast.USub, _ast.UAdd)):
            sizeof = self.sizeof
            if sizeof < 4: # half
                return context.backend.float_t
            return self
        else:
            raise TypeResolutionError(
                "The 'not' operator is not supported for values of type '%s'." % 
                self.name, node.operand)
    
    def generate_UnaryOp(self, context, node):
        op = context.visit(node.op)
        operand = context.visit(node.operand)
        
        code = ("(", op.code, operand.code, ")")
        
        return astx.copy_node(node,
            op=op,
            operand=operand,
            
            code=code
        )
        
    def resolve_BinOp(self, context, node):
        right_type = node.right.unresolved_type.resolve(context)
        try:
            return self._resolve_BinOp(node.op, right_type, context.backend)
        except TypeResolutionError as e:
            if e.node is None:
                e.node = node
            raise e

    def _resolve_BinOp(self, op, right_type, backend):
        if isinstance(right_type, FloatType):
            self_sizeof = self.sizeof
            right_sizeof = right_type.sizeof
            
            if self_sizeof >= right_sizeof:
                if self_sizeof > 2:
                    return self
                else:
                    return backend.float_t
            elif right_sizeof > 2:
                return right_type
            else:
                return backend.float_t
        elif isinstance(right_type, IntegerType):
            if self.sizeof > 2:
                return self
            else:
                return backend.float_t    
        
    def generate_BinOp(self, context, node):
        left = context.visit(node.left)
        op = context.visit(node.op)
        right = context.visit(node.right)
        
        code = ("(", left.code, " ", op.code, " ", right.code, ")")
        
        return astx.copy_node(node,
            left=left,
            op=op,
            right=right,
            
            code=code
        )
        
    def resolve_MultipleAssignment(self, context, prev, new, node):
        new_type = new.resolve(context)
        try:
            return self._resolve_MultipleAssignment(new_type)
        except TypeResolutionError as e:
            if e.node is None:
                e.node = node
            raise e
    
    @cypy.memoize
    def _resolve_MultipleAssignment(self, new_type):
        if self == new_type:
            return new_type
        elif isinstance(new_type, FloatType):
            if new_type.sizeof > self.sizeof:
                return new_type
            else:
                return self
        elif isinstance(new_type, IntegerType):
            return self
        else:
            raise TypeResolutionError(
                "Cannot assign a value of type '%s' to a variable of type '%s'." \
                % (new_type.name, self.name), None)
            
    def validate_AugAssign(self, context, node):
        # TODO: Need to check value too right?
        context.concrete_fn.generic_fn.local_variables[node.target.id].resolve(context)
    
    def generate_AugAssign(self, context, node):
        target = context.visit(node.target)
        value = context.visit(node.value)
        op = context.visit(node.op)
        
        # TODO: I don't know whats going on here...
        # add declaration
        id = target.id
        local_variables = context.generic_fn.local_variables
        if id in local_variables:
            context.backend._add_declaration(context,
                id, local_variables[id].resolve(context))
            
        # add code
        context.stmts.append((self.generate_AugAssign_stmt(
            target.code,
            op.code,
            value.code), context.end_stmt))
        
        # add node
        context.body.append(astx.copy_node(node,
            target=target,
            value=value,
            op=op
        ))
        
    #def resolve_Call(self, context, node):
        # TODO: implement this
        #pass
    
    #def generate_Call(self, context, node):
        # TODO: implement this
        #pass
    
class PtrType(Type):
    def __init__(self, target_type):
        self.target_type = target_type
        Type.__init__(self, target_type.name + "*")
        
    target_type = None
    """The target type of the pointer."""
    
    min_sizeof = 4
    max_sizeof = 8
    
    def resolve_BinOp(self, context, node):
        right_type = node.right.unresolved_type.resolve(context)
        if isinstance(right_type, IntegerType) and isinstance(node.op, _ast.Add):
            return self
        else:
            # TODO: Pointer differences (with special OpenCL logic)
            raise TypeResolutionError(
                "Invalid binary operation with pointer.", node)
            
    def generate_BinOp(self, context, node):
        left = context.visit(node.left)
        op = context.visit(node.op)
        right = context.visit(node.right)
        
        code = ("(", left.code, " ", op.code, " ", right.code, ")")
        
        return astx.copy_node(node,
            left=left,
            op=op,
            right=right,
            
            code=code
        )

    #def resolve_BinOp(self, context, node):
        # TODO: implement this
        #pass
    
    #def generate_BinOp(self, context, node):
        # TODO: implement this
        #pass
    
    #def resolve_MultipleAssignment(self, context, node):
        # TODO: implement this
        #pass
    
    def resolve_Subscript(self, context, node):
        slice_type = node.slice.unresolved_type.resolve(context)
        if not isinstance(slice_type, IntegerType):
            raise TypeResolutionError(
                "Subscript index must be an integer, but saw a %s." %
                slice_type.name)
        else:
            return self.target_type

    def generate_Subscript(self, context, node):
        value = context.visit(node.value)
        slice = context.visit(node.slice)
        
        code = (value.code, "[", slice.code, "]")
        
        return astx.copy_node(node,
            value=value,
            slice=slice,
            
            code=code
        )
            
    def validate_AssignSubscript(self, context, node):
        # TODO: implement this
        return True

    
    def generate_AssignSubscript(self, context, node):
        target = context.visit(node.targets[0])        
        value = context.visit(node.value)
        context.stmts.append((self.generate_Assign_stmt(target.code, value.code), 
                              context.end_stmt))
        context.body.append(astx.copy_node(node,
            targets=[target],
            value=value
        ))       
    
    def validate_AugAssignSubscript(self, context, node):
        # TODO: implement this
        return True
    
    def generate_AugAssignSubscript(self, context, node):
        target = context.visit(node.target)
        value = context.visit(node.value)
        op = context.visit(node.op)
        context.stmts.append((self.generate_AugAssign_stmt(
            target.code,
            op.code,
            value.code
        ), context.end_stmt))
        context.body.append(astx.copy_node(node,
            target=target,
            value=value,
            op=op
        ))
    
class StructureType(Type):
    signature = None
    """Structure signature."""
    
    #def resolve_Attribute(self, context, node):
        # TODO: implement this
        #pass
    
    #def generate_Attribute(self, context, node):
        # TODO: implement this
        #pass
    
    #def validate_AssignAttribute(self, context, node):
        # TODO: implement this
        #pass

    def generate_AssignAttribute(self, context, node):
        target = context.visit(node.targets[0])
        value = context.visit(node.value)
        context.stmts.append((self.generate_Assign_stmt(target.code, value.code), 
                              context.end_stmt))
        context.body.append(astx.copy_node(node,
            targets=[target],
            value=value
        ))
            
    #def validate_AugAssignAttribute(self, context, node):
        # TODO: implement this
        #pass
    
    def generate_AugAssignAttribute(self, context, node):
        target = context.visit(node.target)
        value = context.visit(node.value)
        op = context.visit(node.op)
        context.stmts.append((self.generate_AugAssign_stmt(
            target.code,
            op.code,
            value.code
        ), context.end_stmt))
        context.body.append(astx.copy_node(node,
            target=target,
            value=value,
            op=op
        ))
        
keywords = (
    "auto",
    "break",
    "case",
    "char",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extern",
    "float",
    "for",
    "goto",
    "if",
    "inline",
    "int",
    "long",
    "register",
    "restrict",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "struct",
    "switch",
    "typedef",
    "union",
    "unsigned",
    "void",
    "volatile",
    "while"
    "_Bool",
    "_Complex",
    "_Imaginary"
)

