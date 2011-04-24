import ast as _ast

import cypy
import cypy.cg as cg
import cypy.astx as astx
import cl
import type_inference as _type_inference
from cl import Error

class CompileTimeError(Error):
    def __init__(self, message, node):
        self.message = message
        self.node = node

class ProgramItem(object):
    """Represents an item in an OpenCL program."""
    def __init__(self, name, source):
        self.name = name
        self.source = source
        
    name = None
    """The name of the item, if it has a name, or None."""
    
    source = None
    """The OpenCL source code associated with this item."""
    
class ExtensionItem(ProgramItem):
    """Represents an extension."""
    def __init__(self, extension):
        self.extension = extension
        
    @cypy.lazy(property)
    def source(self):
        return self.extension.pragma_str
cypy.interned(ExtensionItem)

_cl_khr_fp64_item = ExtensionItem(cl.cl_khr_fp64)
_cl_khr_fp16_item = ExtensionItem(cl.cl_khr_fp16)
_cl_khr_byte_addressable_store = ExtensionItem(cl.cl_khr_byte_addressable_store)

class ProgramItemVisitor(_ast.NodeVisitor):
    """Visits an annotated ast to produce program items and metadata."""
    def __init__(self, generic_fn, explicit_arg_names, explicit_arg_types, 
                 constants):
        self.generic_fn = generic_fn
        self.explicit_arg_names = explicit_arg_names
        self.explicit_arg_types = explicit_arg_types
        self.explicit_arg_map = cypy.frozendict(zip(explicit_arg_names, 
                                                   explicit_arg_types))
        self.constants = constants
        self.local_variables = dict(generic_fn.annotated_ast.local_variables)
        self.all_variables = generic_fn.all_variables
        
        self.implicit_args = [ ]
        self.implicit_args_map = { }
        
        self._resolving_name = None
        
        # a list of program items needed by this concrete function
        self.program_items = [ ]
                
    def _resolve_type(self, unresolved_type):
        if isinstance(unresolved_type, cl.Type):
            # pre-resolved (e.g. boolean expressions)          
            return unresolved_type
        else:
            try:
                _resolve = unresolved_type._resolve
            except AttributeError:
                # should never happen
                raise Error("Unexpected unresolved type: %s" % 
                            str(unresolved_type))
            else:
                return _resolve(self)                
    
    ############################################################################
    # FunctionDef
    ############################################################################
    def visit_FunctionDef(self, n):
        body = self.body = self._generate_body(n)
        signature = self.signature = self._generate_signature()
        modifiers = self.modifiers = self._determine_modifiers(n)
        name = self.name = self._generate_name(n.name)

        code = self.code = "%s %s(%s) %s" % (modifiers, name, signature, body)
        
        # create a program item
        self.program_item = program_item = ProgramItem(name, code)
        self.program_items.append(program_item)
    
    def _generate_body(self, n):
        # produce the code for the body and in the process, determine all the
        # necessary implicit arguments needed for downstream functions
        g = cg.CG(processor=None)
        self.tab = g.tab
        self.untab = g.untab
        declarations = self._visit_declarations()
        body = self._visit_body(n.body)
        docstring = self._docstring
        ("{\n", g.tab, docstring, declarations, body, g.untab, "\n}") >> g
        return g.code

    def _visit_declarations(self):
        yield "// Automatically generated local variable declarations\n"
        for name, unresolved_type in self.local_variables.iteritems():
            cl_type = self._resolve_type(unresolved_type)
            yield (cl_type.name, " ", name, ";\n")
        yield "\n\n"
        
    def _visit_body(self, body):
        docstring = self._docstring = self._determine_docstring(body)
        if docstring is not None: body = body[1:]          
        return cypy.join((self.visit(stmt) for stmt in body), "\n")
    
    @staticmethod
    def _determine_docstring(body):
        if body:
            docstring = body[0]
            if isinstance(docstring, _ast.Expr):
                docstring = docstring.value
                if isinstance(docstring, _ast.Str):
                    # issue 168: if docstring contains "*/" this will break
                    docstring = "\n/* %s */\n" % docstring.s
                    body = body[1:]
                else:
                    docstring = None
            else:
                docstring = None
        else:
            docstring = None
        return docstring
    
    def _determine_modifiers(self, n):
        # determine return type and whether to add a __kernel modifier
        self.return_type = return_type = self._resolve_type(n.return_type)
        if self._is_kernel: 
            modifiers = "__kernel void"
        else:
            modifiers = return_type.name
        return modifiers
    
    @cypy.lazy(property)
    def _is_kernel(self):
        if self.return_type is not cl.cl_void:
            # Section 6.8j
            return False
        
        for arg_type in self.all_arg_types:
            if isinstance(arg_type, cl.ScalarType):
                # Section 6.8i
                if arg_type.min_sizeof != arg_type.max_sizeof:
                    return False
                
                if arg_type == cl.cl_half:
                    return False
            
            if isinstance(arg_type, cl.PtrType):
                # Section 6.8a
                if isinstance(arg_type, cl.PrivatePtrType):
                    return False
                if isinstance(arg_type.target_type, cl.PtrType):
                    return False
                
            if arg_type is cl.cl_event_t:
                # Section 6.8n
                return False
                
        return True

    @staticmethod
    def _generate_name(basename):
        try:
            name_count = _function_name_counts[basename]
            _function_name_counts[basename] = name_count + 1
        except KeyError:
            _function_name_counts[basename] = 1
            return basename
        return basename + "___" + str(name_count)

    @cypy.lazy(property)
    def all_arg_names(self):
        return cypy.cons.ed(self.explicit_arg_names, self.implicit_arg_names) #@UndefinedVariable
    
    @cypy.lazy(property)
    def all_arg_types(self):
        return cypy.cons.ed(self.explicit_arg_types, self.implicit_arg_types) #@UndefinedVariable
    
    @cypy.lazy(property)
    def implicit_arg_names(self):
        return tuple("__implicit__" + str(idx) 
                     for idx in xrange(len(self.implicit_args)))
        
    @cypy.lazy(property)
    def implicit_arg_types(self):
        return tuple(cl.infer_cl_type(value) for value in self.implicit_args)

    def _generate_signature(self):
        return ", ".join(self._yield_signature_items())
    
    def _yield_signature_items(self):
        for arg_name, arg_type in zip(self.all_arg_names, self.all_arg_types):
            self._process_stack_type(arg_type)
            yield arg_type.name + " " + arg_name
    
    def _process_stack_type(self, cl_type):
        # infers extensions that relate to stack variable types
        if cl_type is cl.cl_double:
            self._add_program_item(_cl_khr_fp64_item)
        if cl_type is cl.cl_half:
            self._add_program_item(_cl_khr_fp16_item)
        if isinstance(cl_type, cl.ScalarType) and cl_type.min_sizeof < 4:
            # Not sure if this is necessary for half, but probably doesn't
            # matter.
            self._add_program_item(_cl_khr_byte_addressable_store)

    ############################################################################
    # Statements 
    ############################################################################
    def visit_Return(self, n):
        value = n.value
        if value is None:
            return "return;"
        else:
            return ("return ", self.visit(value), ";")
        
    def visit_Assign(self, n):
        return self._visit_targets(n)
           
    def _visit_targets(self, n): 
        value = n.value
        for target in n.targets:
            found = False
            if isinstance(target, _ast.Name):
                cl_type = self._resolve_type(target.unresolved_type)
                try:
                    _generate = cl_type._generate_Assign
                except AttributeError: pass
                else:
                    found = True
                    yield _generate(self, target, value)
            elif isinstance(target, _ast.Attribute):
                cl_type = self._resolve_type(target.value.unresolved_type)
                try:
                    _generate = cl_type._generate_AssignAttribute
                except AttributeError: pass
                else:
                    found = True
                    yield _generate(self, target.value, target.identifier, 
                                    value)
            elif isinstance(target, _ast.Subscript):
                cl_type = self._resolve_type(target.value.unresolved_type)
                try:
                    _generate = cl_type._generate_AssignSubscript
                except AttributeError: pass
                else:
                    found = True
                    yield _generate(self, target.value, target.slice, value)

            if not found:
                raise CompileTimeError("Invalid assignment.", n)
            
    def visit_AugAssign(self, n):
        target = n.target
        op = n.op
        value = n.value
        
        if isinstance(target, _ast.Name):
            cl_type = self._resolve_type(target.unresolved_type)
            try:
                _generate = cl_type._generate_AugAssign
            except AttributeError: pass
            else:
                return _generate(self, target, op, value)
        elif isinstance(target, _ast.Attribute):
            cl_type = self._resolve_type(target.value.unresolved_type)
            try:
                _generate = cl_type._generate_AugAssignAttribute
            except AttributeError: pass
            else:
                return _generate(self, target.value, target.identifier, op, 
                                 value)
        elif isinstance(target, _ast.Subscript):
            cl_type = self._resolve_type(target.value.unresolved_type)
            try:
                _generate = cl_type._generate_AugAssignSubscript
            except AttributeError: pass
            else:
                return _generate(self, target.value, target.slice, op, value)
            
        raise CompileTimeError("Invalid augmented assignment.", n)
        
    def visit_For(self, n):
        # visit parts of update statement manually to avoid inserting the
        # trailing semicolon
        update_stmt = n.update_stmt
        update_code = (self.visit(update_stmt.target), " += ", 
                       self.visit(update_stmt.value))
        
        return ("for (", self.visit(n.init), " ", # the ';' comes from the stmt
                self.visit(n.guard), "; ",
                update_code, ") {\n", self.tab, 
                self._visit_body(n.body), self.untab, "\n}")
        
    def visit_While(self, n):
        return ("while (", self.visit(n.test), ") {\n", 
                self.tab, self._visit_body(n.body), self.untab,
                "\n}")
        
    def visit_If(self, n):
        return ("if (", self.visit(n.test), ") {\n", self.tab,
                self._visit_body(n.body), self.untab, "\n}",
                self._visit_orelse(n.orelse))
        
    def _visit_orelse(self, orelse):
        num = len(orelse)
        if num == 0:
            return
        elif num == 1:
            # covers the else if case
            return (" else ", self.visit(orelse[0]))
        else:
            return (" else {\n", self.tab, self._visit_body(orelse),
                    self.untab, "\n}")
    
    def visit_Expr(self, n):
        return (self.visit(n.value), ";")
        
    def visit_Pass(self, _):
        pass
        
    def visit_Break(self, _):
        return "break;"
        
    def visit_Continue(self, _):
        return "continue;"
    
    def visit_Exec(self, n):
        # shorthand for inserting raw OpenCL code / pre-processor macros / etc.
        return n.body.s
        
    ######################################################################
    ## Supported Operators
    ######################################################################
    def _visit_op(self, n):
        return astx.C_all_operators[type(n)]
    
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
    visit_FloorDiv = _visit_op
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
    def _process_expr(self, n):
        cl_type = self._resolve_type(n.unresolved_type)
        # checks for any extensions that must be enabled due to introduction
        # of stuff
        self._process_stack_type(cl_type)
                        
    def visit_UnaryOp(self, n):
        self._process_expr(n)
        
        cl_type = self._resolve_type(n.unresolved_type)
        return cl_type._generate_UnaryOp(self, n.op, n.operand)
    
    def visit_BinOp(self, n):
        self._process_expr(n)
        
        left = n.left
        op = n.op
        right = n.right
        
        left_cl_type = self._resolve_type(left.unresolved_type)
        try:
            code = left_cl_type._generate_BinOp_left(self, left, op, right)
            if code is not NotImplemented:
                return code
        except AttributeError: pass
        else:
            right_cl_type = self._resolve_type(right.unresolved_type)
            return right_cl_type._generate_BinOp_right(self, left, op, right)
            
    def visit_Compare(self, n):
        self._process_expr(n)
        left = n.left
        comparators = n.comparators
        ops = n.ops
        
        position = n.unresolved_type.position
        if position == 0:
            value = left
        else:
            value = comparators[position - 1]
            
        cl_type = self._resolve_type(value.unresolved_type)
        try:
            _generate = cl_type._generate_Compare
        except AttributeError:
            raise CompileTimeError(
                "Comparison is not supported for specified value types.", n)
        else:
            return _generate(self, left, ops, comparators, position)

    def visit_BoolOp(self, n):
        self._process_expr(n)
        values = n.values
        op = n.op

        position = n.unresolved_type.position
        value = values[position]
        
        cl_type = self._resolve_type(value.unresolved_type)
        try:
            _generate = cl_type._generate_BoolOp
        except AttributeError:
            raise CompileTimeError(
                "Boolean operations are not supported for specified value types.")
        else:
            return _generate(self, op, values, position)
                
    ######################################################################
    ## Expressions
    ######################################################################                
    def visit_IfExp(self, n):
        self._process_expr(n)
        
        return (self.visit(n.test), " ? ", self.visit(n.body), " : ", 
                self.visit(n.orelse))
    
    def visit_Call(self, n):
        self._process_expr(n)
        
        func_cl_type = self._resolve_type(n.func.unresolved_type)
        return func_cl_type._generate_Call(self, n.func, n.args)
    
    def _add_implicit(self, value):
        # add an implicit value, returning its index
        implicit_args_map = self.implicit_args_map
        try:
            return implicit_args_map[value]
        except KeyError:
            implicit_args = self.implicit_args
            n_implicit = len(implicit_args)
            implicit_args_map[value] = n_implicit
            implicit_args.append(value)
            return n_implicit
        
    def _add_program_item(self, program_item):
        program_items = self.program_items
        if program_item not in program_items:
            program_items.append(program_item)

    def visit_Attribute(self, n):
        self._process_expr(n)
        
        value_cl_type = self._resolve_type(n.value.unresolved_type)
        return value_cl_type._generate_Attribute(self, n.value, n.identifier)
    
    def visit_Subscript(self, n):
        self._process_expr(n)
        
        value_cl_type = self._resolve_type(n.value.unresolved_type)
        return value_cl_type._generate_Subscript(self, n.value, n.slice)
        #return (self.visit(n.value), "[", self.visit(n.slice), "]")
    
    def visit_Index(self, n):
        self._process_expr(n)
        
        return self.visit(n.value)
    
    def visit_Name(self, n):
        self._process_expr(n)
        
        id = n.id
        if id in cl.builtins:
            return id
        
        try:
            constant = self.constants[id]
        except KeyError:
            if id in self.all_variables:
                return id
        else:
            if isinstance(n.ctx, _ast.Store):
                raise CompileTimeError("Cannot assign to constant %s." % id, n)
            
            # inline constants
            if isinstance(constant, basestring):
                return cl.to_cl_string_literal(constant)
            cl_type = cl.infer_cl_type(constant)
            if isinstance(cl_type, cl.PtrType):
                return "__implicit__" + str(self._add_implicit(constant))
            else:
                return cl_type.make_literal(constant)
    
    def visit_Num(self, n):
        self._process_expr(n)
        
        return cl.to_cl_numeric_literal(n.n)
    
    def visit_Str(self, n):
        self._process_expr(n)
        
        return cl.to_cl_string_literal(n.s)

_function_name_counts = { }

################################################################################
# Scalar type code generation
################################################################################
def _type_generate_Assign(self, visitor, target, value):
    visit = visitor.visit
    return (visit(target), " = ", visit(value), ";")
cl.Type._generate_Assign = _type_generate_Assign

def _scalar_generate_AugAssign(self, visitor, target, op, value):
    visit = visitor.visit
    if isinstance(op, (_ast.FloorDiv, _ast.Pow)):
        return (visit(target), " = ",
                self._generate_BinOp_left(visitor, target, op, value), ";\n")
    return (visit(target), " ", visit(op), "= ", visit(value), ";")
cl.ScalarType._generate_AugAssign = _scalar_generate_AugAssign

def _scalar_generate_Compare(self, visitor, left, ops, comparators, position): #@UnusedVariable
    visit = visitor.visit
    return ("(", 
            cypy.join(_yield_Compare_terms(visit, left, comparators, ops), 
                     " && "), 
           ")")
cl.ScalarType._generate_Compare = _scalar_generate_Compare

def _yield_Compare_terms(visit, left, comparators, ops):
    for op, right in zip(ops, comparators):
        yield (visit(left), " ", visit(op), " ", visit(right))
        left = right

def _scalar_generate_BoolOp(self, visitor, op, values, position): #@UnusedVariable
    visit = visitor.visit
    return cypy.join((value for value in values), visit(op))
cl.ScalarType._generate_BoolOp = _scalar_generate_BoolOp

def _scalar_generate_UnaryOp(self, visitor, op, operand):
    return (visitor.visit(op), visitor.visit(operand))
cl.ScalarType._generate_UnaryOp = _scalar_generate_UnaryOp

################################################################################
# Integer type code generation
################################################################################
def _integer_generate_BinOp_left(self, visitor, left, op, right):
    visit = visitor.visit
    if isinstance(op, _ast.Pow):
        # pow is a function
        return ("pow(", visit(left), ", ", visit(right), ")")
    elif isinstance(op, _ast.FloorDiv):
        # floor div differs in implementation depending on types
        right_type = visitor._resolve_type(right.unresolved_type)
        if isinstance(right_type, cl.FloatType):
            # if either are floats, need to do a floor afterwards
            return ("floor(", visit(left), " / ", visit(right), ")")
        else:
            # if both are ints, use regular division
            return ("(", visit(left), " / ", visit(right), ")")
    else:
        return ("(", visit(left), " ", visit(op), " ", visit(right), ")")
cl.IntegerType._generate_BinOp_left = _integer_generate_BinOp_left

def _integer_generate_Call(self, visitor, func, args):
    # implements literal suffixes
    if isinstance(func, _ast.Num):
        identifier = args[0].id
        return ("(", literal_suffixes[identifier].name, ")(", #@UndefinedVariable
                visitor.visit(func), ")")
cl.IntegerType._generate_Call = _integer_generate_Call

################################################################################
# Float type code generation
################################################################################
def _float_generate_UnaryOp(self, visitor, op, operand):
    return (visitor.visit(op), visitor.visit(operand))
cl.FloatType._generate_UnaryOp = _float_generate_UnaryOp

def _float_generate_BinOp_left(self, visitor, left, op, right):
    visit = visitor.visit
    if isinstance(op, _ast.Pow):
        # pow is a function
        return ("pow(", visit(left), ", ", visit(right), ")")
    elif isinstance(op, _ast.FloorDiv):
        return ("floor(", visit(left), " / ", visit(right), ")")
    else:
        return ("(", visit(left), " ", visit(op), " ", visit(right), ")")
cl.FloatType._generate_BinOp_left = _float_generate_BinOp_left

def _float_generate_Call(self, visitor, func, args): #@UnusedVariable
    if isinstance(func, _ast.Num):
        identifier = args[0].id
        cl_type = literal_suffixes[identifier] #@UndefinedVariable
        if cl_type is cl.cl_double:
            return str(func.n)
        else:
            return ("(", cl_type.name, ")(", str(func.n), ")")
cl.FloatType._generate_Call = _float_generate_Call

################################################################################
# Pointer type code generation
################################################################################
def _ptr_generate_BinOp_left(self, visitor, left, op, right):
    visit = visitor.visit
    return ("(", visit(left), " ", visit(op), " ", visit(right), ")")
cl.PtrType._generate_BinOp_left = _ptr_generate_BinOp_left

def _ptr_generate_Subscript(self, visitor, value, slice):
    visit = visitor.visit
    return (visit(value), "[", visit(slice), "]")
cl.PtrType._generate_Subscript = _ptr_generate_Subscript

def _ptr_generate_AssignSubscript(self, visitor, obj, slice, value):
    visit = visitor.visit
    return (visit(obj), "[", visit(slice), "] = ", visit(value), ";")
cl.PtrType._generate_AssignSubscript = _ptr_generate_AssignSubscript

def _ptr_generate_AugAssignSubscript(self, visitor, obj, slice, op, value):
    visit = visitor.visit
    return (visit(obj), "[", visit(slice), "] ", visit(op), "= ", visit(value), 
            ";")
cl.PtrType._generate_AugAssignSubscript = _ptr_generate_AugAssignSubscript

################################################################################
# Vector type code generation
################################################################################
cl.VectorType._generate_AugAssign = _scalar_generate_AugAssign
cl.VectorType._generate_Compare = _scalar_generate_Compare
cl.VectorType._generate_BoolOp = _scalar_generate_BoolOp
cl.VectorType._generate_UnaryOp = _scalar_generate_UnaryOp

# TODO: make generate use same selection as inference
def _vec_generate_BinOp_left(self, visitor, left, op, right):
    visit = visitor.visit
    
    if isinstance(op, _ast.Pow):
        return ("pow(", visit(left), ", ", visit(right), ")")
    elif isinstance(op, _ast.FloorDiv):
        if isinstance(self.base_type, cl.IntegerType):
            return ("(", visit(left), "/", visit(right), ")")
        else:
            return ("floor(", visit(left), "/", visit(right), ")")
    else:
        return ("(", visit(left), " ", visit(op), " ", visit(right), ")")
cl.VectorType._generate_BinOp_left = _vec_generate_BinOp_left

# TODO: Are these being generated correctly?
def _vec_generate_Attribute(self, visitor, obj, attr):
    visit = visitor.visit
    return (visit(obj), ".", attr)
cl.VectorType._generate_Attribute = _vec_generate_Attribute

def _vec_generate_AssignAttribute(self, visitor, obj, attr, value):
    visit = visitor.visit
    return (visit(obj), ".", attr, " = ", visit(value), ";")
cl.VectorType._generate_AssignAttribute = _vec_generate_AssignAttribute

def _vec_generate_AugAssignAttribute(self, visitor, obj, attr, op, value):
    visit = visitor.visit
    return (visit(obj), ".", attr, " ", visit(op), "= ", visit(value), ";")
cl.VectorType._generate_AugAssignAttribute = _vec_generate_AugAssignAttribute

# TODO: vector literals
# TODO: builtins
# TODO: documentation

################################################################################
# Function type code generation
################################################################################
def _generic_fn_generate_Call(self, visitor, func, args): #@UnusedVariable
    arg_types = tuple(visitor._resolve_type(arg.unresolved_type) 
                      for arg in args)
    generic_fn = self.generic_fn
    concrete_fn = generic_fn._get_concrete_fn(arg_types)
    name = concrete_fn.fullname
    
    # insert program items
    add_program_item = visitor._add_program_item
    for program_item in concrete_fn.program_items:
        add_program_item(program_item)

    # add defaults
    n_provided = len(args)
    n_args = len(generic_fn.explicit_arg_names)
    n_default = n_args - n_provided
    if n_default < 0:
        raise CompileTimeError("Too many arguments were specified for %s." %
                               name)
    defaults = generic_fn.defaults[0:n_default]    
    
    all_args = _yield_args(visitor, args, arg_types, defaults, 
                            concrete_fn.implicit_args)
    return (name, "(", all_args, ")")
_type_inference.GenericFnType._generate_Call = _generic_fn_generate_Call

def _concrete_fn_generate_Call(self, visitor, func, args): #@UnusedVariable
    concrete_fn = self.concrete_fn
    name = concrete_fn.fullname
    
    # insert program items
    add_program_item = visitor._add_program_item
    for program_item in concrete_fn.program_items:
        add_program_item(program_item)
    
    arg_types = (visitor._resolve_type(arg.unresolved_type) 
                 for arg in args)
    all_args = _yield_args(visitor, args, arg_types, (), 
                                      concrete_fn.implicit_args)
    return (name, "(", all_args, ")")
_type_inference.ConcreteFnType._generate_Call = _concrete_fn_generate_Call

def _yield_args(visitor, args, arg_types, defaults, implicit_args):
    visit = visitor.visit
    for arg, arg_type in zip(args, arg_types):
        if not hasattr(arg_type, 'constant_value'):
            yield visit(arg)
            
    add_implicit = visitor._add_implicit
    for implicit in cypy.cons(defaults, implicit_args):
        yield "__implicit__" + str(add_implicit(implicit))
        
def _builtin_fn_generate_Call(self, visitor, func, args): #@UnusedVariable
    builtin = self.builtin
    
    # extension inference
    requires_extensions = builtin.requires_extensions
    if requires_extensions is not None:
        resolve_type = visitor._resolve_type
        arg_types = (resolve_type(arg.unresolved_type) 
                     for arg in args)
        add_program_item = visitor._add_program_item
        for extension in requires_extensions(*arg_types):
            add_program_item(ExtensionItem(extension))
        
    visit = visitor.visit
    all_args = cypy.join((visit(arg) for arg in args), ", ")
    return (builtin.name, "(", all_args, ")")
_type_inference.BuiltinFnType._generate_Call = _builtin_fn_generate_Call

################################################################################
# Type type code generation
################################################################################
def _type_generate_Call(self, visitor, func, args):
    func_type = visitor._resolve_type(func.unresolved_type).type
    arg = args[0]
    if isinstance(arg, _ast.Num):
        # special casing this so double literals are used in casts
        arg = arg.n
    else:
        arg = visitor.visit(arg)
    return ("(", func_type.name, ")(", arg, ")")
_type_inference.TypeType._generate_Call = _type_generate_Call

################################################################################
# Addressof macro code generation
################################################################################
def _addressof_generate_Call(self, visitor, func, args): #@UnusedVariable
    return ("&", visitor.visit(args[0]))
_type_inference.AddressofType._generate_Call = _addressof_generate_Call
