"""The cl.oquence kernel programming language."""
import ast as _ast # http://docs.python.org/library/ast.html

import cypy
import cypy.astx as astx
import cypy.cg as cg

version = cypy.Version("cl.oquence", (("Major", 1), ("Minor", 0)), "alpha")
"""The current :class:`version <cypy.Version>` of cl.oquence (1.0 alpha)."""

def fn(decl):
    """Create a :class:`generic cl.oquence function <GenericFn>` from a 
    Python function declaration.
    
    Typical usage is as a decorator::
    
        @clq.fn
        def sum(a, b, dest):
            gid = get_global_id(0)
            dest[gid] = a[gid] + b[gid]
            
    As with any decorator, the above is Python syntactic sugar for::
    
        def sum(a, b, dest):
            gid = get_global_id(0)
            dest[gid] = a[gid] + b[gid]
        sum = clq.fn(sum)
        
    .. WARNING:: Functions defined on the ``python`` or ``ipython`` command 
                 line do not retain their source, so this won't work. A bug 
                 has been filed, and has been resolved in version 0.11 of 
                 ipython.
                 
                   http://github.com/ipython/ipython/issues/issue/120
                   
                 A workaround for earlier versions of ipython is to use the 
                 fn.from_source form described below.

    To create a generic function from a string, use the ``fn.from_source``
    function::
    
        clq.fn.from_source('''
        def sum(a, b, dest):
            gid = get_global_id(0)
            dest[gid] = a[gid] + b[gid]
        ''')
        
    To create a generic function from an abstract syntax tree, use the 
    ``fn.from_ast`` function::
    
        clq.fn.from_ast(ast.parse('''
        def sum(a, b, dest):
            gid = get_global_id(0)
            dest[gid] = a[gid] + b[gid]
        '''))

    See the :mod:`ast` module in the Python standard library for more 
    information on manipulating Python syntax trees. The :mod:`cypy.astx`
    module provides several convenience functions for working with Python 
    ASTs as well.
    """
    ast = astx.infer_ast(decl)
    ast = astx.extract_the(ast, _ast.FunctionDef)
    return GenericFn(ast)
    
def from_source(src):
    ast = astx.infer_ast(src)
    ast = astx.extract_the(ast, _ast.FunctionDef)
    return GenericFn(ast)
fn.from_source = from_source

def from_ast(ast):
    return GenericFn(ast)
fn.from_ast = from_ast

class GenericFn(object):
    """A generic cl.oquence function. 
    
    It is generic in the sense that its arguments have not yet been assigned 
    concrete types.
    
    Generic functions are immutable and intern.
    """
    def __init__(self, ast):
        self.original_ast = ast

    ###########################################################################
    # Abstract Syntax Tree
    ###########################################################################         
    @cypy.setonce(property)
    def original_ast(self):
        """The original, unannotated Python abstract syntax tree for this 
        generic function."""
        return self._ast

    @original_ast.setter
    def original_ast(self, value):
        if not isinstance(value, _ast.FunctionDef):            
            raise Error(
            "Root node of ast must be a FunctionDef, but got a %s." %
                value.__class__.__name__)
        self._ast = value
        self.__name__ = value.name
        self.__doc__ = _ast.get_docstring(value, clean=False)

    @cypy.lazy(property)
    def annotated_ast(self): 
        """An annotated copy of the abstract syntax tree for this GenericFn.
        
        See :class:`internals.GenericFnVisitor`.
        """
        visitor = self._visitor = internals.GenericFnVisitor()
        return visitor.visit(self.original_ast)
    
    @cypy.lazy(property)
    def arg_names(self):
        """A tuple of strings containing the names of the arguments."""
        return astx.FunctionDef_co_varnames(self.original_ast) 
        
    @cypy.lazy(property)
    def local_variables(self):
        """A tuple of strings containing the names of the local variables."""
        return self.annotated_ast.local_variables

    @cypy.lazy(property)
    def all_variables(self):
        """A tuple of strings containing the names of all variables (both 
        arguments and local variables)."""
        return self.annotated_ast.all_variables
    
    @cypy.lazy(property)
    def name(self):
        """The function's name."""
        return self.annotated_ast.name

    def compile(self, target, *arg_types):
        """Creates a :class:`concrete function <ConcreteFn>` with the provided
        argument types."""
        return ConcreteFn(self, arg_types, target)
        
    @cypy.lazy(property)
    def cl_type(self):
        return self.Type(self)
cypy.intern(GenericFn)
        
class ConcreteFn(object):
    """A concrete function is made from a generic function by binding the 
    arguments to concrete types.
    
    Concrete functions are immutable and intern.
    """
    # TODO: review this
    def __init__(self, generic_fn, arg_types, backend):
        self.generic_fn = generic_fn
        self.arg_types = arg_types
        self.backend = backend
        
        self.arg_map = cypy.frozendict(zip(generic_fn.arg_names, arg_types))
        
    @cypy.setonce(property)
    def generic_fn(self):
        """The generic function that this concrete function is derived from."""
        return self._generic_fn
    
    @generic_fn.setter
    def generic_fn(self, val):
        self._generic_fn = val
        
    @cypy.setonce(property)
    def arg_types(self):
        """A sequence of types for each of the arguments to this function."""
        return self._arg_types
    
    @arg_types.setter
    def arg_types(self, val):
        self._arg_types = val
        
    @cypy.setonce(property)
    def backend(self):
        """The backend language."""
        return self._backend
    
    @backend.setter
    def backend(self, val):
        self._backend = val
        
    @cypy.lazy(property)
    def typed_ast(self):
        """The typed abstract syntax tree for this function."""
        backend = self.backend
        visitor = self._visitor = internals.ConcreteFnVisitor(self, backend)
        return visitor.visit(self._generic_fn.annotated_ast)
    
    @cypy.lazy(property)
    def program_items(self):
        """A list of all program items needed by this concrete function."""
        return tuple(self.typed_ast.context.program_items)
    
    @cypy.lazy(property)
    def program_item(self):
        """The program item corresponding to this function."""
        return self.typed_ast.context.program_item
    
    @cypy.lazy(property)
    def return_type(self):
        """The return type of this function."""
        return self.typed_ast.context.return_type
    
    @cypy.lazy(property)
    def name(self):
        """The fully-mangled name of this function."""
        return self.program_item.name
    
    @cypy.lazy(property)
    def cl_type(self):
        return self.Type(self)
cypy.intern(ConcreteFn)

class Type(object):
    """Base class for cl.oquence types."""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "<clq.Type <%s>>" % self.name
    
    def __repr__(self):
        return str(self)
    
    def is_subtype(self, candidate_subtype):
        """Returns true if candidate_subtype is a subtype of self 
        
        Or, is_subtype -> True iff candidate <: self. 
        For example, if A <: B and !(B <: A) then: 
        B.is_subtype(A) == True
        A.is_subtype(B) == False
        The default behavior for this rule implements reflection for subtyping (A <: A). 
        """
        return self == candidate_subtype
    
    def coerce(self, supertype):
        """Defines the coercion function on the derivation of a rule.
        
        Defines the coercion function on the derivation of the rule with the 
        conclusion class <: supertype. 
        This method should return a type equiv to supertype or None if no
        coercion exists. 
        """
        if self == supertype:
            return self
        else:
            return None
    
    def observe(self, context, node):
        """Called when this type has been assigned to an expression, given by 
        ``node``."""
        pass
    
    def resolve_Attribute(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support attribute access." %  
            self.name, node.value)
        
    def generate_Attribute(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support attribute access." % 
            self.name, node.value) 
        
    def resolve_Subscript(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support subscript access." % 
            self.name, node.value)
        
    def generate_Subscript(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support subscript access." % 
            self.name, node.value)
        
    def resolve_UnaryOp(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support any unary operations." % 
            self.name, node.operand)
        
    def generate_UnaryOp(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support any unary operations." % 
            self.name, node.operand)
    
    def resolve_BinOp(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support any binary operations." %
            self.name, node.left)
        
    def generate_BinOp(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support any binary operations." %
            self.name, node.left)
        
    def resolve_Compare(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support comparisons." % 
            self.name, node.left)
        
    def generate_Compare(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support comparisons." %
            self.name, node.left)
        
    def resolve_BoolOp(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support any boolean operations." % 
            self.name, node.values[0])
        
    def generate_BoolOp(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support any boolean operations." %
            self.name, node.values[0])
        
    def resolve_Call(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support the call operation." % 
            self.name, node.func)
        
    def generate_Call(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support the call operation." % 
            self.name, node.func)
        
    def validate_Return(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support the 'return' statement." % 
            self.name, node.value)
        
    def generate_Return(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support the 'return' statement." % 
            self.name, node)
        
    def resolve_MultipleAssignment(self, context, prev, new, node):
        new_type = new.resolve(context)
        if self == new_type:
            return new_type
        else:
            raise TypeResolutionError(
                "Multiple assignment with incompatible types: %s, %s." % 
                (self.name, new_type.name), node)
            
    def validate_Assign(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support assignment to an identifier." % 
            self.name, node.target)
        
    def generate_Assign(self, context, node):
        context.backend.generate_Assign(context, node)
        
    def validate_AssignAttribute(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support assignment to an attribute." % 
            self.name, node.targets[0].value)

    def generate_AssignAttribute(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support assignment to an attribute." % 
            self.name, node.targets[0].value)
        
    def validate_AssignSubscript(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support assignment to a subscript." % 
            self.name, node.targets[0].value)
        
    def generate_AssignSubscript(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support assignment to a subscript." % 
            self.name, node.targets[0].value)

    def validate_AugAssign(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support augmented assignment to an identifier." % 
            self.name, node.target)

    def generate_AugAssign(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support augmented assignment to an identifier." %
            self.name, node.target)

    def validate_AugAssignAttribute(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support augmented assignment to an attribute." % 
            self.name, node.target.value)
  
    def generate_AugAssignAttribute(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support augmented assignment to an attribute." % 
            self.name, node.target.value)
        
    def validate_AugAssignSubscript(self, context, node):
        raise TypeResolutionError(
            "Type '%s' does not support augmented assignment to a subscript." % 
            self.name, node.target.value)
        
    def generate_AugAssignSubscript(self, context, node):
        raise CodeGenerationError(
            "Type '%s' does not support augmented assignment to a subscript." % 
            self.name, node.target.value)

    def generate_cast(self, context, node):
        """Generates code for checking a cast."""
        raise CodeGenerationError("Type does not support runtime cast checks", 
                                  node)
        
    def resolve_Cast(self,context,node):
        raise CodeGenerationError(
            "Type '%s' does not support augmented assignment to a subscript." % 
            self.name, node.target.value)

    def generate_Cast(self,context,node):
        """Generates code for checking a cast."""
        raise CodeGenerationError("Type does not support runtime cast checks", 
                                  node)

    def resolve_Call(self, context, node):
        raise TypeResolutionError("Could not resolve that call.", node.func)
    
    def generate_Call(self, context, node):
        raise CodeGenerationError(
                                  "Type '%s' does not support the call operation." % 
                                  self.name, node.func)


class CastType(Type):
    """Implements the dispatch protocol for the cast function.
    
    Calling cast(v,new_type) in Ace casts v to new_type. The value (v)
    is responisble for implementing downcast checks, and also defining what 
    casts are valid. 
    """
    def resolve_Call(self,context,node):
        return self.resolve_Cast(context, node)
    
    def generate_Call(self,context,node):
        return self.generate_Cast(context,node)
        
        
class VirtualType(Type):
    """Designates a type that does not have a concrete representation (e.g. 
    singleton function types)."""

def _generic_generate_Call(context, node):
    arg_types = tuple(arg.unresolved_type.resolve(context)
                      for arg in node.args)
    args = tuple(context.visit(arg)
                 for i, arg in enumerate(node.args)
                 if not isinstance(arg_types[i], VirtualType))
    func = context.visit(node.func)
    
    code = (func.code, "(",
            cypy.join((arg.code for arg in args), ", "),
            ")")
    
    return astx.copy_node(node,
        args=args,
        func=func,
        
        code=code) 

class GenericFnType(VirtualType):
    """Each generic function uniquely inhabits a GenericFnType."""
    def __init__(self, generic_fn):
        VirtualType.__init__(self, generic_fn.name)
        self.generic_fn = generic_fn
         
    def resolve_Call(self, context, node):
        arg_types = tuple(arg.unresolved_type.resolve(context)
                          for arg in node.args)
        concrete_fn = self.generic_fn.compile(context.backend, *arg_types)
        return concrete_fn.return_type
    
    def generate_Call(self, context, node):
        return _generic_generate_Call(context, node)

cypy.intern(GenericFnType)
GenericFn.Type = GenericFnType

class CastFnType(CastType):
    """A cast function"""
    def __init__(self, name):
        CastType.__init__(self,name)
        
    def resolve_Cast(self, context, node):
        """Casting using cast()."""
        term = node.args[0]
        type = node.args[1]
        
        term_type = term.unresolved_type.resolve(context)
        type_type = type.unresolved_type.resolve(context)
        
        return type_type
    
    def generate_Cast(self, context, node):
        """Inserts runtime checks on downcasts."""
        #casting term to type.
        term = node.args[0].unresolved_type.resolve(context)
        type = node.args[1].unresolved_type.resolve(context)
        
        retval = term.generate_cast(context,node)
        return context.visitor.visit(node.args[0]) if retval == None else retval
cypy.intern(CastFnType)
CastFnType.Type = CastFnType


        
        
class ConcreteFnType(VirtualType):
    """Each concrete function uniquely inhabits a ConcreteFnType."""
    def __init__(self, concrete_fn):
        VirtualType.__init__(self, concrete_fn.name)
        self.concrete_fn = concrete_fn

    def resolve_Call(self, context, node):
        arg_types = tuple(arg.unresolved_type.resolve(context)
                          for arg in node.args)
        concrete_fn = self.concrete_fn
        fn_arg_types = concrete_fn.arg_types

        #Ensure that each type is a subtype of the expected type.
        for arg,arg_type in zip(arg_types, fn_arg_types):
            if not arg.is_subtype(arg_type): #S <: S
                raise TypeResolutionError(
                    "Argument types are not compatible. Got %s, expected %s." %
                    (str(arg), str(arg_type)), node)

        return concrete_fn.return_type
    
    def generate_Call(self, context, node):
        """Appllies coercion semantics and then generates code."""
        #These are the arg types we should coerce to
        expected_arg_types = self.concrete_fn._arg_types
        
        #These are the arg types we really have.
        arg_types = list()
        for i in range(len(node.args)):
            #Get the actual argument type for this argument
            arg_type = node.args[i].unresolved_type.resolve(context)
            
            #Do coercion if necessary.
            arg_type = arg_type.coerce(expected_arg_types[i])
            if arg_type == None:
                raise TypeResolutionError("Couldn't coerce types",node)
            
            #add to the arg_types list.
            arg_types.append(arg_type)
        
        #visit the arguments
        args = list()
        for arg,arg_type in zip(node.args,arg_types):
            if isinstance(arg_type, VirtualType):
                continue
            args.append(context.visit(arg))
            
        func = context.visit(node.func)
        
        code = (func.code, "(",
                cypy.join((arg.code for arg in args), ", "),
                ")")
        
        return astx.copy_node(node,
            args=args,
            func=func,
            code=code)  
cypy.intern(ConcreteFnType)
ConcreteFn.Type = ConcreteFnType

class Backend(object):
    """Abstract base class for a backend language specification."""
    def __init__(self, name):
        self.name = name
                
    def init_context(self, context):
        """Initializes a :class:`context <Context>`."""
        pass
    
    def generate_program_item(self, context):
        """Called to generate a :class:`program item <ProgramItem>` for a 
        completed concrete function described by the provided context.
        
        The return value is automatically added assigned to the 
        context.program_item attribute and added to context.program_items.
        """
        raise Error("Backend must provide a method to generate program items.")
        
    def void_type(self, context, node):
        raise TypeResolutionError(
            "Backend does not specify a void type.", node) 
        
    def resolve_Num(self, context, node):
        raise TypeResolutionError(
            "Backend cannot handle raw numeric literals.", node)
        
    def generate_Num(self, context, node):
        raise CodeGenerationError(
            "Backend cannot handle raw numeric literals.", node)
        
    def resolve_Str(self, context, node):
        raise TypeResolutionError(
            "Backend cannot handle raw string literals.", node)
    
    def generate_Str(self, context, node):
        raise CodeGenerationError(
            "Backend cannot handle raw string literals.", node)
    
    def generate_For(self, context, node):
        raise CodeGenerationError(
            "Backend does not support 'for' loops.", node)
        
    def generate_While(self, context, node):
        raise CodeGenerationError(
            "Backend does not support 'while' loops.", node)
        
    def generate_If(self, context, node):
        raise CodeGenerationError(
            "Backend does not support 'if' statements.", node)
        
    def generate_IfExp(self, context, node):
        raise CodeGenerationError(
            "Backend does not support 'if' expressions.", node)
    
    def generate_Expr(self, context, node):
        raise CodeGenerationError(
            "Backend does not support standalone expressions.", node)
        
    def generate_Pass(self, context, node):
        raise CodeGenerationError(
            "Backend does not support the 'pass' statement.", node)
        
    def generate_Break(self, context, node):
        raise CodeGenerationError(
            "Backend does not support the 'break' statement.", node)
        
    def generate_Continue(self, context, node):
        raise CodeGenerationError(
            "Backend does not support the 'continue' statement.", node)
        
    def generate_Exec(self, context, node):
        raise CodeGenerationError(
            "Backend does not support the 'exec' statement.", node)
        
    def generate_op(self, context, node):
        raise CodeGenerationError(
            "Backend does not support operators.", node)
    
    ## Defined interfaces for extensions
    def string_type(self):
        raise Error("This backend does not support string types")
    string_t = None

class Context(object):
    """Contains contextual information that is used during type resolution 
    and code generation. 
    
    User-defined types may read and write to the context, although care should 
    be taken to ensure that naming conflicts do not arise.
    """
    def __init__(self, visitor, concrete_fn, backend):
        self.visitor = visitor
        self.concrete_fn = concrete_fn
        self.backend = backend

        self.generic_fn = concrete_fn.generic_fn
        
        self.body = [ ]
        self.stmts = [ ]
        self.program_items = [ ]
                
        # used to provide base case for resolving multiple assignments
        self._resolving_name = None
        self._multiple_assignment_prev = { }
        
        backend.init_context(self)
        
    def visit(self, node):
        return self.visitor.visit(node)
    
    def observe(self, clq_type, node):
        clq_type.observe(self, node)
        return clq_type
        
    tab = staticmethod(cg.CG.tab)
    untab = staticmethod(cg.CG.untab)

class ProgramItem(object):
    """Represents a top-level item in the generated source code."""
    def __init__(self, name, code):
        self.name = name
        self.code = code
        
    name = None
    """The name of the item, if it has a name, or None."""
    
    code = None
    """The source code associated with this item."""

class Error(Exception):
    """Base class for errors in cl.oquence."""
    
class InvalidOperationError(Error):
    """Raised if an invalid operation is observed in a generic function."""
    def __init__(self, message, node):
        self.message = message
        self.node = node

class TypeResolutionError(Error):
    """Raised to indicate an error during type resolution."""
    def __init__(self, message, node):
        self.message = message
        self.node = node
        
class CodeGenerationError(Error):
    """Raised to indicate an error during code generation."""
    def __init__(self, message, node):
        self.message = message
        self.node = node

# placed at the end because the internals use the definitions above
import internals 
