import ast as _ast # http://docs.python.org/library/ast.html

import cypy
import cypy.astx as astx
import cl
from cl import Error

import type_inference as _type_inference
import generate_cl as _generate_cl

version = cypy.Version("cl.oquence", (("Major", 1), ("Minor", 0)), "alpha")
"""The current :class:`Version <cypy.Version>` of cl.oquence (0.1 alpha)."""

def fn(__src=None, **constants):
    """Create a generic cl.oquence function based on the provided source and 
    constant bindings. 
    
    - If provided a Python function (e.g. if used as a decorator):
    
      - The abstract syntax tree will be read via :func:`cypy.astx.infer_ast`.
      
      - The function's globals and defaults will be used.
      
    - If ``__src`` is a :class:`GenericFn` already, a new generic function with 
      additional constants will be created. It will have the same abstract 
      syntax tree, defaults and globals.

    Constants can be passed in as keyword arguments.
    
    .. WARNING:: Functions defined on the Python/iPython command line do not 
                 retain their source, so this won't work. A bug has been filed: 
                 
                 http://github.com/ipython/ipython/issues/issue/120
                 
    """
    # __src in case a variable named 'src' is defined.
    
    if __src is None:
        # support using as a decorator with constants by deferring 
        # initialization until the source is also specified, presumably
        # directly below
        return lambda __src: fn(__src, **constants)
    elif isinstance(__src, GenericFn):
        return GenericFn(__src.ast, __src.defaults, __src.globals,
                         cypy.merge_dicts(__src.constants, constants),
                         __src.size_calculator)
    else:
        ast = astx.infer_ast(__src)
        ast = astx.extract_the(ast, _ast.FunctionDef)
        globals = __src.func_globals
        defaults = __src.func_defaults
        if defaults is None: 
            # In Python, func_defaults is None if there are no defaults but 
            # I don't want to have to special case that everywhere
            defaults = ()
        return GenericFn(ast, defaults, globals, constants)
    
def from_source(source, defaults=(), globals={}, constants={}, 
                size_calculator=None):
    """Creates a :class:`GenericFn` from the provided source, with the provided
    defaults (inline defaults cannot be resolved), globals, constants and
    size calculator.
    
    Inline defaults are not evaluated and should not be used.
    """
    ast = astx.infer_ast(source)
    ast = astx.extract_the(ast, _ast.FunctionDef)
    return GenericFn(ast, defaults, globals, constants, size_calculator)

def autosized(size_calculator):
    """A modifier for a generic function which endows it with a default method
    for calculating global and local size.
    
    Should return a tuple (global_size, local_size).
    
    .. WARNING:: At the moment, the Python from_source library function is
                 buggy when used in conjunction with multiple decorators, so
                 you'll have to apply this manually.

    """
    def _defer(fn):
        if fn.size_calculator is size_calculator:
            return fn
        else:
            return GenericFn(fn.ast, fn.defaults, fn.globals, fn.constants,
                             size_calculator)
    return _defer

class GenericFn(object):
    """A generic cl.oquence function. That is, one without concrete types yet.
    
    A GenericFn consists of an abstract syntax tree, defaults, globals, 
    constants and an optional size calculator. GenericFn objects are immutable 
    and interned (cached).
    
    See :func:`fn` if you want to infer each of these things from a Python 
    function definition.
    
    In addition to the attributes below, the attributes ``__name__`` and 
    ``__doc__`` are extracted from the syntax tree on initialization, 
    corresponding to the name of the function and its docstring (or ``None``
    if not specified.)
    
    .. NOTE:: In generated code, the docstring turns into a comment. All other
              comments are stripped (the Python parser doesn't give us comments
              or parenthesis, can't do anything about that.)
    
    """
    def __init__(self, ast, defaults, globals, constants, 
                 size_calculator=None):
        self.ast = ast
        self.defaults = defaults
        self.globals = globals
        self.constants = constants
        self.size_calculator = size_calculator

    ############################################################################
    # Abstract Syntax Tree
    ############################################################################         
    @cypy.setonce(property)
    def ast(self):
        """The (untyped) Python abstract syntax tree for this GenericFn."""
        return self._ast

    @ast.setter
    def ast(self, value): #@DuplicatedSignature
        if not isinstance(value, _ast.FunctionDef):            
            raise Error("Root of ast must be a FunctionDef, but got a %s." %
                        value.__class__.__name__)
        self._ast = value
        self.__name__ = value.name
        self.__doc__ = _ast.get_docstring(value, clean=False)

    @cypy.lazy(property)
    def annotated_ast(self): 
        """An annotated copy of the abstract syntax tree for this GenericFn.
        
        - Each expression is annotated with an unresolved_type
        - Free variables, argument names and local variables are determined
        
        See "How It Works" above and the 
        :mod:`type_inference <cl.oquence.type_inference>` module.
        """
        return _type_inference.get_annotated_ast(self.ast)
    
    @cypy.lazy(property)
    def all_variables(self):
        """A tuple of all variables available in this function.
        
        Variables bound to constants are not included.
        """
        constants = self.constants
        return tuple(var for var in self.annotated_ast.all_variables
                     if var not in constants)
        
    @cypy.lazy(property)
    def free_variables(self):
        """A tuple of free variables for this function.
        
        Free variables are variables which are not arguments or local variables
        and have not been assigned to a constant.
        """
        constants = self.constants
        return tuple(var for var in self.annotated_ast.free_variables
                     if var not in constants)
    
    @cypy.lazy(property)
    def _base_arg_names(self):
        return astx.FunctionDef_co_varnames(self.ast)
    
    @cypy.lazy(property)
    def explicit_arg_names(self):
        """The list of arguments this function allows to be passed.
        
        If a specified argument is bound to a constant, that argument cannot be 
        passed.
        """
        constants = self.constants
        return tuple(arg for arg in self._base_arg_names
                     if arg not in constants)
        
    @cypy.lazy(property)
    def local_variables(self):
        return tuple(var for var in self.annotated_ast.local_variables)

    ##########################################################################
    # Defaults
    ##########################################################################
    @cypy.setonce(property)
    def defaults(self):
        """A tuple of defaults for arguments to this function.
        
        .. NOTE:: If there are no defaults, this will be an empty tuple, 
                  rather than ``None`` as for Python functions.
        
        """
        return self._defaults
    
    @defaults.setter
    def defaults(self, value): #@DuplicatedSignature
        self._defaults = value
        
    @cypy.lazy(property)
    def default_types(self):
        """A tuple containing the types of the defaults."""
        return tuple(cl.infer_cl_type(default) for default in self.defaults)
    
    ##########################################################################
    ## Globals
    ##########################################################################
    @cypy.setonce(property)
    def globals(self):
        """The dict of globals to use to bind free variables at compilation."""
        return self._globals
    
    @globals.setter
    def globals(self, globals): #@DuplicatedSignature
        self._globals = globals
        
    ##########################################################################
    ## Constants
    ##########################################################################
    @cypy.setonce(property)
    def constants(self):
        """The frozen dict of constants to use to bind arguments and free 
        variables at compile-time."""
        return self._constants
    
    @constants.setter
    def constants(self, constants): #@DuplicatedSignature
        if hasattr(constants, "__setitem__"):
            constants = cypy.frozendict(constants)
        self._constants = constants
    
    @cypy.lazy(property)
    def _all_constants(self):
        # All constants (provided constants + free variable constants).
        constants = self.constants
        globals = self.globals
        return cypy.frozendict(cypy.cons(
            constants.iteritems(),
            ((name, globals[name]) 
             for name in self.free_variables if name not in constants)
        ))
        
    ############################################################################
    ## Size Calculator
    ############################################################################
    @cypy.setonce(property)
    def size_calculator(self):
        """For kernels, this can be a function which takes the full set of
        arguments (defaults will have been applied) and returns a pair
        ``(global_size, local_size)``, which are used as defaults if the user
        does not specify these values manually.
        """
        return self._size_calculator
    
    @size_calculator.setter
    def size_calculator(self, value): #@DuplicatedSignature
        self._size_calculator = value
        
    ##########################################################################
    ## Concrete Function Production and Calling
    ##########################################################################
    def __call__(self, *args, **kwargs):
        """Calls this function with the provided arguments and keyword options.
        
        See :meth:`ConcreteFn.__call__`
        
        Internally, this creates a :class:`ConcreteFn`, which is then
        used to generate a :class:`cl.Kernel` object, which is then called.
        """
        args, arg_types = zip(*self._apply_default_args_and_types(args))
        concrete_fn = self._get_concrete_fn_final(arg_types)
        
        # determine global and local size using the size calculator if not
        # specified
        if 'global_size' not in kwargs:
            global_size, local_size = self.size_calculator(*args)
            kwargs['global_size'] = global_size
            if 'local_size' not in kwargs:
                kwargs['local_size'] = local_size
        elif 'local_size' not in kwargs:
            size_calculator = self.size_calculator
            if size_calculator is not None:
                _, local_size = size_calculator(*args)
                kwargs['local_size'] = local_size

        # determine actual arguments to pass (including implicits) and do call
        args = self._filter_args(args, concrete_fn)
        return concrete_fn._do_call(args, kwargs)
        
    def get_concrete_fn_for(self, *args):
        """Returns the concrete function, with argument types taken from the 
        provided values. Defaults are applied and the current global values of 
        remaining free variables are used.
        
        Note that these values themselves are not bound to the concrete 
        function. This is mostly useful for inspecting source code.
        
        See :meth:`get_concrete_fn` if you have the types in hand.
        """
        # to prevent unnecessary copying when passing through multiple
        # functions, the private versions of these don't take var args
        return self._get_concrete_fn_for(args)
    
    def _get_concrete_fn_for(self, args):
        arg_types = (cl.infer_cl_type(arg) for arg in args)
        arg_types = self._apply_default_types(arg_types)
        return self._get_concrete_fn_final(arg_types)
    
    def get_concrete_fn(self, *arg_types):
        """Returns a concrete function for the provided argument types.
        
        Defaults are applied and the types of the global values of free 
        variables are used. 
        
        This is mostly useful for inspecting source code.
        """
        return self._get_concrete_fn(arg_types)
    
    @cypy.memoize
    def _get_concrete_fn(self, arg_types):
        return self._get_concrete_fn_final(self._apply_default_types(arg_types))
    
    def _apply_default_args_and_types(self, args):
        # yields a full sequence of arg, arg_type pairs given args
        # does not filter out lifted constants or include implicit arguments
        
        # provided args
        for arg in args:
            arg_type = cl.infer_cl_type(arg)
            yield arg, arg_type
            
        # defaults
        n_provided = len(args)
        n_args = len(self.explicit_arg_names) # constants were filtered out in this step
        n_defaults = n_args - n_provided
        if n_defaults < 0:
            raise Error("Too many arguments were specified for %s."
                        % self.name)
        elif n_defaults > 0:
            defaults = self.defaults
            default_types = self.default_types
            for i in xrange(n_defaults):
                yield defaults[i], default_types[i]
    
    @cypy.memoize
    def _apply_default_types(self, arg_types):
        # (type-only analag of _apply_default_args_and_types above)
        
        # provided args
        for arg_type in arg_types:
            yield arg_type
            
        # defaults
        n_provided = len(arg_types)
        n_args = len(self.explicit_arg_names)
        n_defaults = n_args - n_provided
        if n_defaults < 0:
            raise Error("Too many arguments were specified for %s." %
                        self.name)
        elif n_defaults > 0:
            default_types = self.default_types
            for i in xrange(n_defaults):
                yield default_types[i]
        
    @cypy.memoize
    def _get_concrete_fn_final(self, arg_types):
        # lift arguments which must be constants to constants
        constants = dict(self._all_constants)
        arg_types = tuple(arg_types)
        if arg_types:
            # need all these conditionals because zip(*) will spit out a single 
            # empty tuple if provided an empty tuple and then Python will barf 
            # at the destructuring assignment
            filtered_arg_types = tuple(self._filter_arg_types(arg_types, 
                                                              constants))
            if filtered_arg_types:
                arg_names, arg_types = zip(*filtered_arg_types)
            else:
                arg_names, arg_types = ()
        else:
            arg_names = arg_types # empty tuple already
            
        # generate source
        visitor = _generate_cl.ProgramItemVisitor(self, arg_names, arg_types,
                                                  constants)
        visitor.visit(self.annotated_ast)
        
        # produce ConcreteFn
        return ConcreteFn(visitor)
    
    def _filter_arg_types(self, arg_types, constants):
        for arg_name, arg_type in zip(self.explicit_arg_names, arg_types):
            try:
                constant_value = arg_type.constant_value
            except AttributeError:
                yield arg_name, arg_type
            else:
                constants[arg_name] = constant_value
                
    def _filter_args(self, args, concrete_fn):
        # filter out actual arguments if that argument has become a constant
        constants = concrete_fn.constants
        for arg_name, arg in zip(self.explicit_arg_names, args):
            if not constants.has_key(arg_name):
                yield arg
        
    ##########################################################################
    # Type
    ##########################################################################
    @cypy.lazy(property)
    def cl_type(self):
        return _type_inference.GenericFnType(self)
cypy.interned(GenericFn)

class ConcreteFn(object):
    """A concrete function consists of a generic function bound to concrete 
    argument types and constant bindings.
    
    From a ConcreteFn, an OpenCL program is born.
    
    Do not initialize directly, use :meth:`GenericFn.get_concrete_fn` or 
    :meth:`GenericFn.get_concrete_fn_for`.
    """
    def __init__(self, visitor):
        self._visitor = visitor
        
    @cypy.lazy(property)
    def generic_fn(self):
        """The :class:`GenericFn` associated with this concrete function."""
        return self._visitor.generic_fn
        
    @cypy.lazy(property)
    def explicit_arg_names(self):
        """The names of all explicit arguments."""
        return self._visitor.explicit_arg_names
        
    @cypy.lazy(property)
    def explicit_arg_types(self):
        """The concrete types of all explicit arguments."""
        return self._visitor.explicit_arg_types
    
    @cypy.lazy(property)
    def implicit_args(self):
        """A sequence of implicit argument values.
        
        Implicit arguments are constants that can't be inlined, both for this
        function and downstream functions, as well as omitted defaults for
        downstream functions.
        """
        return self._visitor.implicit_args
    
    @cypy.lazy(property)
    def implicit_args_map(self):
        """A map from implicit argument values to their index in implicit_args."""
        return self._visitor.implicit_args_map
    
    @cypy.lazy(property)
    def all_arg_names(self):
        """The names of all arguments, implicit and explicit."""
        return self._visitor.all_arg_names
    
    @cypy.lazy(property)
    def all_arg_types(self):
        """The types of all arguments, implicit and explicit."""
        return self._visitor.all_arg_types
    
    @cypy.lazy(property)
    def constants(self):
        """The full set of constants, including arguments lifted to constants."""
        return self._visitor.constants
    
    @cypy.lazy(property)
    def program_items(self):
        """A list of program items. See 
        :class:`ProgramItem <cl.oquence.generate_cl.ProgramItem>`.
        """
        return tuple(self._visitor.program_items)
    
    @cypy.lazy(property)
    def program_item(self):
        """The program item corresponding to this function itself."""
        return self._visitor.program_item
    
    @cypy.lazy(property)
    def return_type(self):
        """The concrete return type of this function."""
        return self._visitor.return_type
    
    @cypy.lazy(property)
    def is_kernel(self):
        return self._visitor._is_kernel
    
    ############################################################################
    # Programs, Program Items and Source
    ############################################################################    
    @cypy.memoize
    def generate_program(self, ctx, options=""):
        """Creates an :class:`cl.Program` object for this function.""" 
        return ctx.compile(self.program_source, options)
    
    @cypy.lazy(property)
    def program_source(self):
        """The source code of the program produced by this function."""
        return "\n\n".join(item.source for item in self.program_items)
        
    @cypy.lazy(property)
    def fn_source(self):
        """The source code of this function."""
        return self.program_item.source
    
    ############################################################################
    # Naming
    ############################################################################
    @cypy.lazy(property)
    def fullname(self):
        """The fully mangled name of this function."""
        return self.program_item.name
    
    ############################################################################
    # Calling
    ############################################################################
    @cypy.memoize
    def generate_kernel(self, ctx, options=''):
        """Creates a program and extracts this function as a callable 
        :class:`cl.Kernel` object.
                        
        ``ctx``
            The :class:`cl.Context` to create the Program under. If not
            specified, the default context (cl.ctx) must be specified and 
            is used.
            
        ``options``
            The compiler options to pass to :meth:`cl.Context.compile`.
        
        """
        return getattr(self.generate_program(ctx, options), 
                       self.fullname)
        
    def __call__(self, *args, **kwargs):
        """Creates a program, extracts the kernel and calls it."""
        return self._do_call(args, kwargs)
    
    def _do_call(self, args, kwargs):
        if not self.is_kernel:
            raise Error("Cannot call a non-kernel cl.oquence function.")
        
        # include downstream implicit variables
        args = cypy.cons(args, self.implicit_args)
        
        # grab context and options
        try: ctx = kwargs.pop('ctx')
        except KeyError: ctx = cl.ctx
        options = kwargs.pop('options', '')
        
        # generate a kernel        
        kernel = self.generate_kernel(ctx, options)
        
        # send global size the way pyopencl likes it
        global_size = kwargs.pop('global_size')
        
        # get queue
        try: queue = kwargs.pop('queue')
        except KeyError: queue = ctx.queue
        
        # call the kernel
        return kernel(queue, global_size, *args, **kwargs)
    
    ############################################################################
    # Type 
    ############################################################################
    @cypy.lazy(property)
    def cl_type(self):
        return _type_inference.ConcreteFnType(self)
GenericFn._ConcreteFn = ConcreteFn

literal_suffixes = {
    'uc': cl.cl_uchar,
    'c': cl.cl_char,
    'us': cl.cl_ushort,
    's': cl.cl_short,
    'ui': cl.cl_uint,
    'i':  cl.cl_int,
    'uL': cl.cl_ulong,
    'L': cl.cl_long,
    'h': cl.cl_half,
    'f': cl.cl_float,
    'd': cl.cl_double
}
"""A map from numeric literal suffixes to their correspond 
`type <cl.ScalarType>`."""

# both modules need access to this but need to avoid circular references
_type_inference.literal_suffixes = literal_suffixes
_generate_cl.literal_suffixes = literal_suffixes

addressof = cypy.Singleton(cl_type=_type_inference.AddressofType())
"""A macro to support the '&' operator in OpenCL. 

Must import into scope of your function to use this.
"""

def _test():
    import numpy
    import numpy.linalg as la
    import cl as cl
    
    a = numpy.random.rand(50000).astype(numpy.float32)
    b = numpy.random.rand(50000).astype(numpy.float32)
    
    @cl.oquence.fn
    def ew_add(a, b, dest):
        gid = get_global_id(0)
        dest[gid] = a[gid] + b[gid]
        
    ctx = cl.ctx = cl.Context.for_device(0, 0)
    a_buf = ctx.to_device(a)
    b_buf = ctx.to_device(b)
    dest_buf = ctx.alloc(like=a)
    
    ew_add(a_buf, b_buf, dest_buf, global_size=a.shape, local_size=(1,)).wait()
    
    c = ctx.from_device(dest_buf)
    
    print la.norm(c - (a + b))
    
if __name__ == "__main__":
    _test()
