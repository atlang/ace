"""The cl.oquence kernel programming language."""

import ast as _ast # http://docs.python.org/library/ast.html

import cypy
import cypy.astx as astx

class Error(Exception):
    """Base class for errors in cl.oquence."""
    
version = cypy.Version("cl.oquence", (("Major", 1), ("Minor", 0)), "alpha")
"""The current :class:`Version <cypy.Version>` of cl.oquence (1.0 alpha)."""

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
    form::
    
        clq.fn.from_source('''
        def sum(a, b, dest):
            gid = get_global_id(0)
            dest[gid] = a[gid] + b[gid]
        ''')
        
    To create a generic function from an abstract syntax tree, use the 
    ``fn.from_ast`` form::
    
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
    
def _from_source(src):
    ast = astx.infer_ast(src)
    ast = astx.extract_the(ast, _ast.FunctionDef)
    return GenericFn(ast)
fn.from_source = _from_source

def _from_ast(ast):
    return GenericFn(ast)
fn.from_ast = _from_ast

class GenericFn(object):
    """A generic cl.oquence function. 
    
    It is generic in the sense that its arguments have not yet been assigned 
    concrete types.
    
    Generic functions are immutable and interned.
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
            "Root of original_ast must be a FunctionDef, but got a %s." %
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
        """A tuple of strings containing all the arguments named by this  
        generic function."""
        return astx.FunctionDef_co_varnames(self.original_ast) 
        
    @cypy.lazy(property)
    def local_variables(self):
        """A tuple of strings containing all the local variables named in
        this generic function."""
        return self.annotated_ast.local_variables

    @cypy.lazy(property)
    def all_variables(self):
        """A tuple of strings containing all the variables (both arguments and
        local variables) named by or in this function::
        
            self.all_variables == cons.ed(self.arg_names, self.local_variables)
            
        """
        return self.annotated_ast.all_variables

    def compile(self, *arg_types):
        """Creates a :class:`concrete function <ConcreteFn>` with the provided
        argument types."""
        return ConcreteFn(self, arg_types)
        
    @cypy.lazy(property)
    def clq_type(self):
        return GenericFnType(self)
cypy.interned(GenericFn)

class ConcreteFn(object):
    """A concrete function is made from a generic function by binding the 
    arguments to concrete types.
    
    Concrete functions are immutable and interned.
    """
    def __init__(self, generic_fn, arg_types):
        self.generic_fn = generic_fn
        self.arg_types = arg_types
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
        
    @cypy.lazy(property)
    def typed_ast(self):
        """The typed abstract syntax tree for this function."""
        visitor = self._visitor = internals.ConcreteFnVisitor(self)
        return visitor.visit(self._generic_fn.annotated_ast)
    
    @cypy.lazy(property)
    def program_items(self):
        """A list of all program items needed by this concrete function."""
        return tuple(self.typed_ast.program_items)
    
    @cypy.lazy(property)
    def program_item(self):
        """The program item corresponding to this function."""
        return self.typed_ast.program_item
    
    @cypy.lazy(property)
    def return_type(self):
        """The return type of this function."""
        return self.typed_ast.return_type
    
    @cypy.lazy(property)
    def name(self):
        """The fully-mangled name of this function."""
        return self.program_item.name
    
    @cypy.lazy(property)
    def clq_type(self):
        return ConcreteFnType(self)
cypy.interned(ConcreteFn)

class Type(object):
    """Base class for cl.oquence types."""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "<clq.Type <%s>>" % self.name
    
    def __repr__(self):
        return str(self)
    
    # TODO: remove _ before these
    # TODO: list all possibilities here
    
    def _generate_Assign(self, context, target, value):
        context.body_code.append((context.visit(target).code, " = ",
                                  context.visit(value).code, ";\n"))
    
    def _resolve_MultipleAssignment_prev(self, context, new):
        if self is new: return self

class VoidType(Type):
    """The type of :obj:`void`."""
    def __init__(self):
        Type.__init__(self, "void")
cypy.interned(VoidType)

void = VoidType()
"""Functions that do not return a value are given the ``void`` return type."""
    
class GenericFnType(Type):
    """Each generic function has a corresponding instance of GenericFnType."""
    def __init__(self, generic_fn):
        Type.__init__(self, generic_fn.name)
        self.generic_fn = generic_fn
         
    def _resolve_Call(self, context, func, args):
        arg_types = tuple(context._resolve_type(arg.unresolved_type)
                          for arg in args)
        concrete_fn = self.generic_fn.compile(*arg_types)
        return concrete_fn.return_type
cypy.interned(GenericFnType)

class ConcreteFnType(Type):
    """Each concrete function uniquely inhabits a ConcreteFnType."""
    def __init__(self, concrete_fn):
        Type.__init__(self, concrete_fn.name)
        self.concrete_fn = concrete_fn
        
    def _resolve_Call(self, context, func, args):
        concrete_fn = self.concrete_fn
        
        # check argument types
        fn_arg_types = concrete_fn.arg_types
        provided_arg_types = tuple(context._resolve_type(arg.unresolved_type)
                                   for arg in args)
        if fn_arg_types != provided_arg_types:
            raise ConcreteTypeError(
                "Argument types are not compatible. Got %s, expected %s." % 
                (str(fn_arg_types), str(provided_arg_types)))
        
        # everything looks okay, return 
        return concrete_fn.return_type
cypy.interned(ConcreteFnType)

class InvalidOperationError(Error):
    """Raised if an invalid operation is observed in a generic function."""
    def __init__(self, message, node):
        self.message = message
        self.node = node

class ConcreteTypeError(Error):
    """Raised to indicate a type error in a concrete cl.oquence function."""
    def __init__(self, message):
        self.message = message

def is_valid_varname(id):
    """Returns a boolean indicating whether id can be used as a variable name 
    in cl.oquence code."""
    return True

class ProgramItem(object):
    """Represents a top-level item in the target program."""
    def __init__(self, name, code):
        self.name = name
        self.code = code
        
    name = None
    """The name of the item, if it has a name, or None."""
    
    code = None
    """The source code associated with this item."""

# placed at the end because the internals use the definitions above
import internals 
