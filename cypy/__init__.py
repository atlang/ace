"""Python utilities."""
# TODO: doctests
# TODO: license header
# TODO: automatic documentation generation
# TODO: move imports to appropriate places in file

import __builtin__
import sys as _sys
import time as _time
import inspect as _inspect
import functools as _functools
import math as _math
import re as _re

##############################################################################
## Error Handling
##############################################################################
class Error(Exception):
    """Base class for errors in the ``cypy`` package."""
    pass

##############################################################################
## Version Descriptors
##############################################################################
class Version(object):
    """Generic version descriptor.

        >>> v = Version("cypy", (('major', 1), ('minor', 0)), ('beta',))
        >>> print v
        cypy 1.0 beta

    All docstrings below refer to this example.
    """
    def __init__(self, name="", version=(('major', 0),), tags=()):
        self.name = name
        self.version = version
        self.tags = tags

    name = ""
    """The name of the entity (e.g. library, program, etc.)
    
        >>> print v.name
        cypy
        
    """

    version = ()
    """The version, as a sequence of pairs (identifier, version number).
     
        >>> print v.version
        (('major', 1), ('minor', 0))
    
    """

    @property
    def version_str(self):
        """Returns the version number as a dot-delimited string.
        
            >>> print v.version_str
            1.0
        
        """
        return ".".join((str(ver) for desc, ver in self.version))

    @property
    def version_tuple(self):
        """Returns the version number as a tuple.
        
            >>> print v.version_tuple
            (1, 0)
        
        """
        return tuple( ver for _, ver in self.version )

    @staticmethod
    def padded_tuples(ver1, ver2):
        """Given a pair of version number tuples, returns a pair of padded tuples 
        suitable for direct comparison.

            >>> Version.padded_tuples((1, 0), (1, 0, 3))
            ((1, 0, 0), (1, 0, 3))

        """
        return padded_to_same_length(ver1, ver2, 0)

    @staticmethod
    def cmp_tuples(ver1, ver2):
        """Compares two version number tuples. 
        
        Returns an integer below 0 if ver1 < ver2, 0 if ver1 == ver2 and an
        integer greater than 0 if ver2 > ver2 (cf. Python ``cmp`` function.)
        
            >>> Version.cmp_tuples((1, 0), (1, 0, 3)) < 0
            True
            >>> Version.cmp_tuples((1,), (1, 0)) == 0
            True
            >>> Version.cmp_tuples((2,), (1,5)) > 0
            True
        
        """
        return cmp(*padded_to_same_length(ver1, ver2, 0))

    def cmp(self, other):
        """Compares ``self.version_tuple`` and ``other`` using ``cmp_tuples``.

            >>> v.cmp((1,0)) == 0
            True
            >>> v.cmp((1,)) == 0
            True
            >>> v.cmp((1,1)) < 0
            True

        Standard comparison operators may be used as well.

            >>> v <= (1,0)
            True
            >>> v <= (0,9)
            False
            >>> v >= (1,0)
            True
            >>> v >= (1,1)
            False
            >>> v >= ()
            True
            >>> v >= (1,)
            True
            >>> v <= (1,)
            True
            >>> v >= (1, 0, 0, 0, 0, 0)
            True
            >>> v <= (0, 9, 9, 9)
            False

        """
        return cmp(*self.padded_tuples(self.version_tuple, other))

    def __lt__(self, other):
        return self.cmp(other) < 0

    def __eq__(self, other):
        return self.cmp(other) == 0

    def __hash__(self):
        return hash(self.version_tuple)

    def __ne__(self, other):
        return self.cmp(other) != 0

    def __gt__(self, other):
        return self.cmp(other) > 0

    def __le__(self, other):
        return self.cmp(other) <= 0

    def __ge__(self, other):
        return self.cmp(other) >= 0

    tags = ()
    """A sequence of tags associated with this version.
    
        >>> print v.tags
        ('beta',)
    
    """

    @property
    def tag_str(self):
        """Returns a space-delimited string of tags.
        
            >>> print v.tag_str
            beta
            
        """
        return " ".join(self.tags)

    def __str__(self):
        return "%s %s %s" % (self.name, self.version_str, self.tag_str)

##############################################################################
## Console Utilities
##############################################################################
ticTime = None
def tic(msg=None):
    '''Follow with toc().
    
    msg: Optionally prints the provided message when called.
    '''
    global ticTime
    if (msg != None): print msg
    ticTime = _time.time()

def toc():
    '''
    Prints the elapsed time since the last call to tic and returns the elapsed time, in seconds.
    
        >>> tic("Starting...")
        Starting...
        >>> toc()
        --> 0.01s
        
    '''
    elapsed = _time.time() - ticTime
    print "--> " + str(elapsed) + " s"
    return elapsed

_prog_iterin_loop = False
def prog_iter(bounded_iterable, delta=0.01, line_size=50):
    '''Wraps the provided sequence with an iterator that tracks its progress 
    on the console.

        >>> for i in prog_iter(xrange(100)): pass
        ..................................................
        ..................................................
         (0.000331163406372 s)
         
    More specifically, the behavior is as follows:
    
    - Produces a progress bar on stdout, at ``delta`` increments, where 
      ``delta`` is a percentage (represented as a float from 0.0 to 1.0)
    - Newline every line_size dots (defaults to 50)
    - Displays the time the loop took, as in toc() (without interfering with toc)
    - A prog_iter nested in another prog_iter will not produce any of these
      side effects. That is, only one progress bar will ever be printing at a time.
    
    '''
    # TODO: Technically, this should have a __len__.
    global _prog_iterin_loop

    if not _prog_iterin_loop:
        startTime = _time.time()
        _prog_iterin_loop = True
        length = float(len(bounded_iterable))
        _sys.stdout.write(".")
        dots = 1
        next = delta
        for i, item in enumerate(bounded_iterable):
            if (i + 1) / length >= next:
                next += delta
                dots += 1
                _sys.stdout.write(".")
                if dots % line_size == 0:
                    _sys.stdout.write("\n")
                _sys.stdout.flush()
            yield item
        print " (" + str(_time.time() - startTime) + " s)"
        _prog_iterin_loop = False
    else:
        for item in bounded_iterable:
            yield item

def prog_xrange(*args, **kwargs):
    """Equivalent to::

        prog_iter(xrange(*args), **kwargs)
    
    """
    return prog_iter(xrange(*args), **kwargs)

##############################################################################
## Collections
##############################################################################
# containers that support the 'in' operator are treated inconsistenly,
# so use this if you really want to treat something as a set but don't care
# whether it is an official set or a list or a dict.
def include(gset, elem, value=True):
    """Do whatever it takes to make ``elem in gset`` true.

        >>> L, S, D = [ ], set(), { }
        >>> include(L, "Lucy"); include(S, "Sky"); include(D, "Diamonds");
        >>> print L, S, D
        ['Lucy'] set(['Sky']) {'Diamonds': True}

    Works for sets (using ``add``), lists (using ``append``) and dicts (using
    ``__setitem__``).

    ``value``
        if ``gset`` is a dict, does ``gset[elem] = value``.

    Returns ``elem``, or raises an Error if none of these operations are supported.
    """
    add = getattr(gset, 'add', None) # sets
    if add is None: add = getattr(gset, 'append', None)  # lists
    if add is not None: add(elem)
    else: # dicts
        if not hasattr(gset, '__setitem__'):
            raise Error("gset is not a supported container.")
        gset[elem] = value
    return elem

def include_many(gset, elems, truth_value=True):
    """Do whatever it takes to make ``elem in gset`` true for each elem in ``elems``.
    
    See :func:`include`.
    """
    extend = getattr(gset, 'extend', None)
    if extend is not None:
        extend(elems)
    elif hasattr(gset, '__setitem__'):
        gset.update((elem, truth_value) for elem in elems)
    elif hasattr(gset, 'update'):
        gset.update(elems)
    else:
        raise Error("gset is not a supported container.")

def remove_once(gset, elem):
    """Remove the element from a set, lists or dict.
    
        >>> L = ["Lucy"]; S = set(["Sky"]); D = { "Diamonds": True };
        >>> remove_once(L, "Lucy"); remove_once(S, "Sky"); remove_once(D, "Diamonds");
        >>> print L, S, D
        [] set([]) {}

    Returns the element if it was removed. Raises one of the exceptions in 
    :obj:`RemoveError` otherwise.
    """
    remove = getattr(gset, 'remove', None)
    if remove is not None: remove(elem)
    else: del gset[elem]
    return elem

def remove_upto_once(gset, elem):
    """Attempt to :func:`remove_once` but doesn't raise a :obj:`RemoveError` 
    if it doesn't work.

    Returns a boolean indicating whether the removal succeeded.
    """
    try:
        remove_once(gset, elem)
    except RemoveError:
        return False
    return True

def remove_all(gset, elem):
    """Removes every occurrence of ``elem`` from ``gset``.

    Returns the number of times ``elem`` was removed.
    """
    n = 0
    while True:
        try:
            remove_once(gset, elem)
            n = n + 1
        except RemoveError:
            return n

RemoveError = (KeyError, ValueError)
"""The set of errors that can be raised by the remove family of functions."""

##############################################################################
## Iterables
##############################################################################
def is_iterable(value, include_maps=False, include_sets=True):
    """Returns whether value is iterable.
    
    ``include_maps``
        Maps are technically iterable, defaulting to their keys, but you 
        commonly want to find if it is a list-like type and leave maps alone,
        so this is False by default.
        
    ``include_sets``
        Sets are also technically iterable and can be treated like lists, but
        sometimes you don't want to include sets. Defaults to True.
        
    Strings are not considered iterable, even though you can iterate over them
    if you really want to, because the ``__iter__`` method is not defined for
    them by Python. This is usually a good thing -- you probably don't want
    to iterate over the characters of a string by accident.
    """
    if hasattr(value, '__iter__'):
        if not include_maps and hasattr(value, 'keys'):
            return False
        if not include_sets and hasattr(value, 'isdisjoint'):
            return False
        return True
    else:
        return False

def as_iterable(value, wrap_maps=True, wrap_sets=False, itertype=tuple):
    """Wraps a single non-iterable value with a tuple (or other iterable type, 
    if ``itertype`` is provided.)
    
        >>> as_iterable("abc")
        ("abc",)
        >>> as_iterable(("abc",))
        ("abc",)
        
    Equivalent to::
    
        if is_iterable(value, not wrap_maps, not wrap_sets):
            return value
        else:
            return itertype(value)
            
    """
    if is_iterable(value, not wrap_maps, not wrap_sets):
        return value
    else:
        return itertype(value)

def all_unique(seq):
    """Returns whether all the elements in the sequence ``seq`` are unique.

        >>> all_unique(())
        True
        >>> all_unique((1, 2, 3))
        True
        >>> all_unique((1, 1, 2))
        False

    Creates a set, so the elements of the sequence must be hashable (and are compared by their hash value). 
    
    Equivalent to::
    
        return len(set(seq)) == len(seq)
    
    """
    return len(set(seq)) == len(seq)

# TODO: Example here.
def flatten(iterable, check=is_iterable):
    """Produces a recursively flattened version of ``iterable``

    ``check``
        Recurses only if check(value) is true.
    """
    for value in iterable:
        if check(value):
            for flat in flatten(value, check):
                yield flat
        else:
            yield value

def ed(fn, iterable, *args, **kwargs):
    """If ``fn`` maps ``iterable`` to a generator (e.g. :func:`flatten` and
    others below), ``ed`` will consume the result and produce a tuple or list.

    If ``iterable`` has a finite length (e.g. tuples, lists), uses the
    same type to consume it. If not (e.g. generators), use a tuple.

    The cypy functions have an `ed` member to make this convenient.

    Why `ed`? Because its the past tense -- take the lazy generator and
    consume it by creating a tuple or list out of it.
    """
    if hasattr(iterable, '__len__'):
        return iterable.__class__(fn(iterable, *args, **kwargs))
    else:
        return tuple(fn(iterable, *args, **kwargs))

def _generator_producing(fn, *example, **kwargs):
    fn.ed = _functools.partial(ed, fn)
    fn.ed.__doc__ = ":func:`ed` version of :func:`%s`." % fn.__name__

    result = str(fn.ed(*example))
    if 'example_str' in kwargs:
        example_str = kwargs['example_str']
    else:
        example_str = ", ".join(str(arg) for arg in example)
    fn.__doc__ += ("\n\n    >>> %s.ed(%s)" % (fn.__name__, example_str))
    fn.__doc__ += (  "\n    %s" % result)

std_example = (1, (2, 3))

_generator_producing(flatten, std_example)

def xflatten(iterable, transform, check=is_iterable):
    """Apply a transform to iterable before flattening at each level."""
    for value in transform(iterable):
        if check(value):
            for flat in xflatten(value, transform, check):
                yield flat
        else:
            yield value
_generator_producing(xflatten, std_example, reversed,
                     example_str=str(std_example) + ", reversed")

def flatten_once(iterable, check=is_iterable):
    """Flattens only the first level."""
    for value in iterable:
        if check(value):
            for item in value:
                yield item
        else:
            yield value
_generator_producing(flatten_once, (((1, (2, 3))), ((4, 5))))

def cons(*args):
    """Concatenate the provided arguments."""
    return flatten_once(args)
def _consed(*args):
    return flatten_once.ed(args)
cons.ed = _consed

def join(iterable, sep):
    """Like str.join, but yields an iterable."""
    i = 0
    for i, item in enumerate(iterable):
        if i == 0:
            yield item
        else:
            yield sep
            yield item
_generator_producing(join, ("a", [], {}), None)

def stop_at(iterable, idx):
    """Stops iterating before yielding the specified idx."""
    for i, item in enumerate(iterable):
        if i == idx: return
        yield item
_generator_producing(stop_at, (0, 1, 2, 3, 4, 5, 6, 7, 8), 4)

def all_pairs(seq1, seq2=None):
    """Yields all pairs drawn from ``seq1`` and ``seq2``.

    If ``seq2`` is ``None``, ``seq2 = seq1``.

        >>> stop_at.ed(all_pairs(xrange(100000), xrange(100000)), 8)
        ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7))
    """
    if seq2 is None: seq2 = seq1
    for item1 in seq1:
        for item2 in seq2:
            yield (item1, item2)
_generator_producing(all_pairs, (1, 2, 3))

def yield_n(n, item):
    """``(item for i in xrange(n))``"""
    i = 0
    while i < n:
        yield item
        i += 1

def padded_to_same_length(seq1, seq2, item=0):
    """Return a pair of sequences of the same length by padding the shorter 
    sequence with ``item``.

    The padded sequence is a tuple. The unpadded sequence is returned as-is.
    """
    len1, len2 = len(seq1), len(seq2)
    if len1 == len2:
        return (seq1, seq2)
    elif len1 < len2:
        return (cons.ed(seq1, yield_n(len2-len1, item)), seq2)
    else:
        return (seq1, cons.ed(seq2, yield_n(len1-len2, item)))

bool_vals = (True, False)
"""(True, False)"""

##############################################################################
## Sequences
##############################################################################
def prepend(list, item):
    """Adds the provided item to the front of the list.""" 
    list.insert(0, item)
    
def extend_front(list, items):
    """Adds the provided items to the front of the list."""
    for item in reversed(items):
        prepend(list, item)
        
##############################################################################
## Numbers
##############################################################################
inf = float('inf')
"""float('inf')"""

nan = float('nan')
"""float("nan')"""

def is_numeric(value):
    """Returns whether value is numeric.

    .. WARNING:: Complex values are not currently handled by cypy.
    """
    # It's unclear how to best check for numerics in Python so wrapping it
    # here so if it changes, you can just change this file.
    return is_int_like(value) or is_float_like(value)

def is_int_like(value):
    """Returns whether the value can be used as a standard integer.

        >>> is_int_like(4)
        True
        >>> is_int_like(4.0)
        False
        >>> is_int_like("4")
        False
        >>> is_int_like("abc")
        False

    """
    try:
        if isinstance(value, int): return True
        return int(value) == value and str(value).isdigit()
    except:
        return False

def is_float_like(value):
    """Returns whether the value acts like a standard float.

        >>> is_float_like(4.0)
        True
        >>> is_float_like(numpy.float32(4.0))
        True
        >>> is_float_like(numpy.int32(4.0))
        False
        >>> is_float_like(4)
        False

    """
    try:
        if isinstance(value, float): return True
        return float(value) == value and not str(value).isdigit()
    except:
        return False

def ceil_int(num):
    """Returns ceil(num) as an int instead of a float."""
    return int(_math.ceil(num))

def floor_int(num):
    """Returns floor(num) as an int instead of a float."""
    return int(_math.floor(num))

def float_div(num1, num2):
    """Floating point division, even for ints: float(num1)/num2."""
    return float(num1)/num2

def int_div_round_up(num1, num2):
    """Rounds the result of float-dividing ints to the next highest int."""
    return ceil_int(float_div(num1, num2))

def prod(iterable):
    """Computes the product of all items in iterable."""
    prod = 1
    for item in iterable:
        prod *= item
    return prod

##############################################################################
## Dictionaries
##############################################################################
def merge_dicts(*dicts):
    """Merge the provided dicts into a new dict."""
    return merge_dicts_into({}, *dicts)

def merge_dicts_into(target, *dicts):
    """Merge the provided dicts into the target dict."""
    for d in dicts:
        target.update(d)
    return target

def make_symmetric(dict):
    """Makes the given dictionary symmetric. Values are assumed to be unique."""
    for key, value in dict.items():
        dict[value] = key
    return dict

no_default = object()
"""Useful semantic token to test (using `is`)

.. WARNING:: Not documented well/correctly below here.
"""


##############################################################################
## Callables
##############################################################################
def is_callable(value):
    """Returns whether the value is callable."""
    return hasattr(value, '__call__')

# ``callable`` considered harmful --
# wrappers are considered callable even if they only _can_ support calling,
# even if they don't -- because the normal builtin doesn't actually check that
# read the __call__ attribute doesn't throw an attribute error the way
# e.g. hasattr does.
__builtin__.callable = is_callable

def get_fn(callable):
    """Returns the underlying function that will be called by the () operator.

        * For regular functions, returns ``callable``
        * For bound methods, returns ``callable.im_func``
        * For unbound methods, returns ``callable.__func__``
        * For classes, returns ``callable.__init__.__func__``.
        * For callable objects, returns ``callable.__call__.im_func``.

    """
    if _inspect.isfunction(callable):
        return callable
    if _inspect.ismethod(callable):
        try:
            return callable.im_func
        except AttributeError:
            return callable.__func__
    if _inspect.isclass(callable):
        return callable.__init__.__func__
    if hasattr(callable, '__call__'):
        return callable.__call__.im_func
    return callable

def get_fn_or_method(callable):
    """Returns the underlying function or method that will be called by the () operator.

        * For regular functions and methods, returns ``callable``
        * For classes, returns ``callable.__init__``
        * For callable objects, returns ``callable.__call__``

    """
    if _inspect.isfunction(callable) or _inspect.ismethod(callable):
        return callable
    if _inspect.isclass(callable):
        return callable.__init__
    return callable.__call__

# see http://docs.python.org/reference/datamodel.html
_fn_args_flag = 0x04
fn_has_args = lambda callable: bool(get_fn(callable).func_code.co_flags
                                    & _fn_args_flag)
"""Returns whether the provided callable's underlying function takes *args."""

_fn_kwargs_flag = 0x08
fn_has_kwargs = lambda callable: bool(get_fn(callable).func_code.co_flags
                                      & _fn_kwargs_flag)
"""Returns whether the provided callable's underlying function takes **kwargs."""

_fn_generator_flag = 0x20
fn_is_generator = lambda callable: bool(get_fn(callable).func_code.co_flags
                                        & _fn_generator_flag)
"""Returns whether the provided callable's underlying function is a generator."""

_fn_future_division_flag = 0x2000
fn_uses_future_division = lambda callable: bool(get_fn(callable).func_code.co_flags
                                                & _fn_future_division_flag)
"""Returns whether the provided callable's underlying function uses future division."""

def fn_kwargs(callable):
    """Returns a dict with the kwargs from the provided function.

    Example

        >>> def x(a, b=0, *args, **kwargs): pass
        >>> func_kwargs(x) == { 'b': 0 }

    """
    fn = get_fn(callable)
    (args, _, _, defaults) = _inspect.getargspec(fn)
    if defaults is None: return { }
    return dict(zip(reversed(args), reversed(defaults)))

def fn_available_argcount(callable):
    """Returns the number of explicit non-keyword arguments that the callable
    can be called with.

    Bound methods are called with an implicit first argument, so this takes
    that into account.

    Excludes *args and **kwargs declarations.
    """
    fn = get_fn_or_method(callable)
    if _inspect.isfunction(fn):
        return fn.func_code.co_argcount
    else: # method
        if fn.im_self is None:
            return fn.im_func.func_code.co_argcount
        else:
            return fn.im_func.func_code.co_argcount - 1

def fn_minimum_argcount(callable):
    """Returns the minimum number of arguments that must be provided for the call to succeed."""
    fn = get_fn(callable)
    available_argcount = fn_available_argcount(callable)
    try:
        return available_argcount - len(fn.func_defaults)
    except TypeError:
        return available_argcount
    
def fn_argnames(callable):
    fn = get_fn(callable)
    func_code = fn.func_code
    argcount = func_code.co_argcount
    if fn_has_args(fn):
        argcount += 1
    if fn_has_kwargs(fn):
        argcount += 1
    return func_code.co_varnames[0:argcount]

def fn_signature(callable, 
                 argument_transform=(lambda name: name),
                 default_transform=(lambda name, value: "%s=%s" % 
                                                        (name, repr(value))),
                 vararg_transform=(lambda name: "*" + name),
                 kwargs_transform=(lambda name: "**" + name)):
    """Returns the signature of the provided callable as a tuple of strings."""
    signature = []
    fn = get_fn(callable)
    avail_ac = fn_available_argcount(fn)
    kwargs = fn_kwargs(fn)
    argnames = fn_argnames(fn)
    for name in stop_at(argnames, avail_ac):
        if name in kwargs:
            signature.append(default_transform(name, kwargs[name]))
        else:
            signature.append(argument_transform(name))
    if fn_has_args(fn):
        if fn_has_kwargs(fn):
            signature.append(vararg_transform(argnames[-2]))
            signature.append(kwargs_transform(argnames[-1]))
        else:
            signature.append(vararg_transform(argnames[-1]))
    elif fn_has_kwargs(fn):
        signature.append(kwargs_transform(argnames[-1]))

    return signature

_unhashable_object = object()
def fn_arg_hash_function(fn):
    """Creates a hash function which will return the same hashable value if 
    passed a set of *args and **kwargs which are equivalent from the 
    perspective of a function call.
    
    That is, the order of keyword arguments, or the fact that an argument 
    without a default was called as a kwarg, will not produce a different hash.
    
    If any arguments provided are not hashable, a TypeError is raised.
    
    *args and **kwargs are supported.
    """
    fn = get_fn(fn)
    n_explicit = fn_available_argcount(fn)
    has_args = fn_has_args(fn)
    has_kwargs = fn_has_kwargs(fn)
    default_kwargs = fn_kwargs(fn)
    for name, value in default_kwargs.iteritems():  
        # store only hashes of values to prevent memory leaks
        try: default_kwargs[name] = hash(value)
        except TypeError: default_kwargs[name] = _unhashable_object
    explicit_kwarg_args = set(default_kwargs.keys())
    n_explicit_kwargs = len(explicit_kwarg_args)
    n_explicit_args = n_explicit - n_explicit_kwargs
    def _hashes(*args, **kwargs):        
        # explicit args
        i = 0
        n_explicit_args_ = min(len(args), n_explicit_args)
        while i < n_explicit_args_:
            #print args[i], 'is an explicit arg.'            
            yield hash(args[i])
    
            i += 1
    
        # explicit kwargs
        for name in explicit_kwarg_args:
            if len(args) > i:
                #print args[i], 'is a kwarg without a default'
                yield hash(args[i])
                i += 1                
            else:
                try:
                    #print kwargs[name], 'is a kwarg taken from kwargs'
                    yield hash(kwargs[name])
                except KeyError:
                    #print default_kwargs[name], 'is a kwarg taken from defaults'
                    yield default_kwargs[name]
    
        # *args
        if has_args:
            #print args[i:], 'is *args'
            yield hash(args[i:])
    
        # **kwargs
        # NOTE: we're treating the kwargs dicts as hashable even though 
        # technically they aren't... be wary if you define **kwargs and then
        # depend on its mutable characteristics.
        if has_kwargs:
            items = frozenset(item for item in kwargs.items()
                              if item[0] not in explicit_kwarg_args)
            #print items, 'is **kwargs items'
            yield hash(items)
        
    def hash_(*args, **kwargs):
        return tuple(_hashes(*args, **kwargs))
    
    return hash_

def _generic_fn(*args, **kwargs): pass
generic_arg_hash_function = fn_arg_hash_function(_generic_fn)

def fn_get_source(callable):
    """Attempts to find the source of the provided callable.
    
    Indentation is fixed using fix_indentation before returning.
    
    .. WARNING:: Functions defined on the iPython command line do not have 
             their source saved. A bug has been filed: 
             
             http://github.com/ipython/ipython/issues/issue/120

    """
    fn = get_fn(callable)
    return fix_indentation(_inspect.getsource(fn))

##############################################################################
## Decorators
##############################################################################
def decorator(d):
    """Creates a proper decorator.

    If the default for the first (function) argument is None, creates a
    version which be invoked as either @decorator or @decorator(kwargs...).

    See examples below.
    """
    defaults = d.func_defaults
    if defaults and defaults[0] is None:
        # Can be applied as @decorator or @decorator(kwargs) because
        # first argument is None
        def decorate(fn=None, **kwargs):
            if fn is None:
                return _functools.partial(decorate, **kwargs)
            else:
                decorated = d(fn, **kwargs)
                _functools.update_wrapper(decorated, fn)
                return decorated
    else:
        # Can only be applied as @decorator
        def decorate(fn):
            decorated = d(fn)
            _functools.update_wrapper(decorated, fn)
            return decorated
    _functools.update_wrapper(decorate, d)
    return decorate


@decorator
def memoize(fn=None):
    """Caches the result of the provided function."""
    cache = { }
    arg_hash_fn = fn_arg_hash_function(fn)

    def decorated(*args, **kwargs):
        try:
            hash_ = arg_hash_fn(*args, **kwargs)
        except TypeError:
            return fn(*args, **kwargs)

        try:
            return cache[hash_]
        except KeyError:
            return_val = fn(*args, **kwargs)
            cache[hash_] = return_val
            return return_val
    _functools.update_wrapper(decorated, fn)

    return decorated

##############################################################################
## Objects
##############################################################################
class Token(object):
    __slots__ = ('name')

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s>" % self.name

    def __eq__(self, other):
        return other is self

def safe_setattr(obj, name, value):
    """Attempt to setattr but catch AttributeErrors."""
    try:
        setattr(obj, name, value)
        return True
    except AttributeError:
        return False

def method_call_if_def(obj, attr_name, m_name, default, *args, **kwargs):
    """Calls the provided method if it is defined.

    Returns default if not defined.
    """
    try:
        attr = getattr(obj, attr_name)
    except AttributeError:
        return default
    else:
        return getattr(attr, m_name)(*args, **kwargs)

def call_on_if_def(obj, attr_name, callable, default, *args, **kwargs):
    """Calls the provided callable on the provided attribute of ``obj`` if it is defined.

    If not, returns default.
    """
    try:
        attr = getattr(obj, attr_name)
    except AttributeError:
        return default
    else:
        return callable(attr, *args, **kwargs)

class Singleton(object):
    """Creates a singleton object with the attributes specified as keyword arguments."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

##############################################################################
## Properties
##############################################################################
def define_property(obj, name, fget=None, fset=None, fdel=None, doc=None):
    """Defines a @property dynamically for an instance rather than a class."""
    if hasattr(fget, '__get__'):  # can pass a property declaration too
        prop = fget
    else:
        prop = property(fget, fset, fdel, doc)
    cls = obj.__class__
    obj.__class__ = type(cls.__name__, (cls, ), {
        '__doc__': cls.__doc__,
        name: prop
    })

def define_properties(obj, props):
    """Defines multiple @properties dynamically for an instance rather than a class."""
    cls = obj.__class__
    dct = {
        '__doc__': cls.__doc__
    }

    for name, defn in props.iteritems():
        if is_callable(defn):
            defn = property(defn)
        elif not hasattr(defn, '__get__'):
            defn = property(*defn)
        dct[name] = defn

    obj.__class__ = type(cls.__name__, (cls, ), dct)

class _descriptor_modifier(object):
    #__slots__ = ('_parent', '__doc__')

    def __init__(self, parent, doc):
        self._parent = parent
        self.__doc__ = doc

    # all descriptor properties are inherited from the parent
    # e.g. if the parent is property, this allows getter, setter and deleter
    # to continue to work even for modified versions of the descriptor
    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if name != "__set__" and name != "__delete__":
                # if we didn't define __set__ and __delete__ we meant not to,
                # so don't defer those.
                return getattr(self._parent, name)
            else: raise

    def __setattr__(self, name, value):
        try:
            object.__setattr__(self, name, value)
        except AttributeError:
            setattr(self._parent, name, value)

    def __delattr__(self, name):
        try:
            object.__delattr__(self, name)
        except AttributeError:
            setattr(self._parent, name)

    # this is a bit of a hack to support getter/setter/deleter syntax
    # post-wrapping
    
    @property
    def getter(self):
        if hasattr(self._parent, 'getter'):
            return self.__getter
                    
    def __getter(self, fn):
        rv = self._parent.getter(fn)
        self._parent = rv
        return self
        
    @property
    def setter(self):
        if hasattr(self._parent, 'setter'):
            return self.__setter
        
    def __setter(self, fn):
        rv = self._parent.setter(fn)
        self._parent = rv
        return self
        
    @property
    def deleter(self):
        if hasattr(self._parent, 'deleter'):
            return self.__deleter
        
    def __deleter(self, fn):
        rv = self._parent.deleter(fn)
        self._parent = rv
        return self

class _wrap_data_descriptor(object):
    """
    convenient base class for modifiers which inherit their parent's 
    __set__ and __delete__ functionality
    """
    def __set__(self, instance, value):
        self._parent.__set__(instance, value)

    def __delete__(self, instance):
        self._parent.__delete__(instance)

def replaceable(decorator):
    """A descriptor modifier which allows a setattr to succeed even if __get__ is defined.
    
    Formally, this turns a data descriptor into a non-data descriptor. Discards
    the implementation of __set__ and __delete__ if it exists, so be wary when
    not using with ``property``.
    """
    def decorate(fn, *args, **kwargs):
        parent = decorator(fn, *args, **kwargs)
        #doc = _add_msg(getattr(parent, '__doc__', None), '*@replaceable*')
        doc = getattr(parent, '__doc__', None)
        return _replaceable(parent, doc)
    return decorate

class _replaceable(_descriptor_modifier):
    def __get__(self, instance, owner):
        return self._parent.__get__(instance, owner)

def lazy(decorator):
    """A descriptor modifier which caches the result of __get__."""
    def decorate(fn, *args, **kwargs):
        name = fn.__name__
        parent = decorator(fn, *args, **kwargs)
        #doc = _add_msg(getattr(parent, '__doc__', None), '*@lazy*')
        doc = getattr(parent, '__doc__', None)
        if hasattr(parent, '__set__') or hasattr(parent, '__delete__'):
            return _lazy_data(name, parent, doc)
        else:
            return _lazy_nondata(name, parent, doc)
    return decorate

class _named_descriptor_modifier(_descriptor_modifier):
    """
    convenient base class for modifiers which need to store some metadata with
    the object according to the name of the attribute they are assigned to.
    """
    def __init__(self, name, parent, doc):
        _descriptor_modifier.__init__(self, parent, doc)
        object.__setattr__(self, '_name', name)
        object.__setattr__(self, '_valattr', mangle(self.__class__, 
                                                    name))

class _lazy_nondata(_named_descriptor_modifier):
    def __get__(self, instance, owner):
        _valattr = self._valattr
        try: return getattr(instance, _valattr)
        except AttributeError:
            if instance is not None:
                val = self._parent.__get__(instance, owner)
                setattr(instance, _valattr, val)
                return val
            else:
                return self

class _lazy_data(_lazy_nondata, _wrap_data_descriptor): pass

def setonce(decorator):
    """A descriptor modifier which allows __set__ to be called at most once."""
    def decorate(fn, *args, **kwargs):
        parent = decorator(fn, *args, **kwargs)
        #doc = _add_msg(getattr(parent, '__doc__', None), '*@setonce*')
        doc = getattr(parent, '__doc__', None)
        assert hasattr(parent, "__set__") # don't use for non-data descriptors!
        return _setonce(fn.__name__, parent, doc)
    return decorate

class _setonce(_named_descriptor_modifier):
    def __get__(self, instance, owner):
        parent = self._parent
        return_val = parent.__get__(instance, owner)
        if return_val is parent: return self
        return return_val

    def __set__(self, instance, value):
        _valattr = self._valattr
        if not getattr(instance, _valattr, False):
            setattr(instance, _valattr, True)
            self._parent.__set__(instance, value)
        else:
            raise AttributeError("Cannot set " + self._name + " more than once.")

    def __delete__(self, instance):
        # not sure if this is the right way to handle __delete__?
        _valattr = self._valattr
        if not getattr(instance, _valattr, False):
            setattr(instance, _valattr, True)
            self._parent.__delete__(instance)
        else:
            raise AttributeError("Cannot delete " + self._name + " after it has been set once.")

##############################################################################
## Classes and Metaclasses
##############################################################################
@decorator
def autoinit(fn):
    """Automates initialization so things are more composable.

    * All specified kwargs in the class and all autoinit classes in
    inheritance hierarchy will be setattr'd at the end of initialization,
    with defaults derived from the inheritance hierarchy as well.
    * If **kwargs is explicitly specified, the __init__ method will be called.
    * If a default is specified as a new[class name] then a default instance
    of that class will be initialized as the value.

        class Base(object):
            @autoinit
            def __init__(self, a="A", **kwargs):
                print "In Base."

        class Base2(object):
            @autoinit
            def __init__(self, a="A2"):
                print "In Base2."

        class T(Base, Base2):
            @autoinit
            def __init__(self, b=new[list], **kwargs):
                print "In T."
        t = T()
        print t.a, t.b
        t = T(['x'])
        print t.a, t.b

    """
    if fn is None:
        fn = _empty_init

    if fn_has_args(fn):
        raise Error("*args support is not available in autoinit.")
        # its pretty hard to support this, though doable if really needed...

    __defaults = fn_kwargs(fn)

    avail_ac = fn_available_argcount(fn)
    avail_args = list(fn.func_code.co_varnames[1:avail_ac])

    signature = fn_signature(fn,
        argument_transform=(lambda name: name),
        default_transform=(lambda name, _: "%s=__defaults['%s']" % (name,name)),
        vararg_transform=None,
        kwargs_transform=(lambda _: "**__kwargs"))
    signature[0] = "self"
    
    call_signature = fn_signature(fn,
        argument_transform=(lambda name: "%s=%s" % (name, name)),
        default_transform=(lambda name, _: "%s=%s" % (name,name)),
        vararg_transform=None,
        kwargs_transform=(lambda _: "**__kwargs"))
    call_signature[0] = "self"

    if not fn_has_kwargs(fn):
        signature.append("**__kwargs")
        call_signature.append("**__kwargs")

    signature = ", ".join(signature)
    call_signature = ", ".join(call_signature)
    avail_args = repr(tuple(avail_args))
    
    code = '''def __init__(%(signature)s):
    __cls = self.__class__
    __mro = tuple(__cls.mro())

    # call up the mro
    for __base in __mro:
        if __base is object: continue
        try:
            __wrapped_init = __base.__init__.__wrapped_init
        except AttributeError:
            # not an autoinit class
            pass
        else:
            # **kwargs signals that the initializer wants to be called
            if __wrapped_init and fn_has_kwargs(__wrapped_init):
                __wrapped_init(%(call_signature)s)

    # get defaults from hierarchy
    __update_kwargs = { }
    for __base in reversed(__mro):
        if __base is __cls or __base is object: continue
        try:
            __defaults = __base.__init__.__defaults
        except AttributeError:
            # not an autoinit class
            pass
        else:
            for __name, __val in __defaults.iteritems():
                if __val is not Default:
                    __update_kwargs[__name] = __val

    # get locally passed arguments into __update_kwargs
    __locals = locals()
    for __name in %(avail_args)s:
        __val = __locals[__name]
        if __val is Default:
            if __name not in __update_kwargs:
                raise Error("Must specify argument " + __name)
        else:
            __update_kwargs[__name] = __val
            
    for __name, __val in __kwargs.iteritems():
        if __val is Default:
            if __name not in __update_kwargs:
                raise Error("Must specify argument " + __name)
        else:
            __update_kwargs[__name] = __val

    # set attributes according to kwargs
    for __name, __val in __update_kwargs.iteritems():
        if isinstance(__val, _new_initializer):
            setattr(self, __name, __val())
        else:
            setattr(self, __name, __val)
''' % locals()
    exec code in globals(), locals()
    #
    # i know, exec -- no other way to get the signature to match it seems
    # unless i build it out of an abstract syntax tree or something, which 
    # seems excessive. or i could inspect the signature and do stuff dynamically
    # but that is troublesome and the documentation generators won't like it
    #
    # if you want to try to fix it to not use exec but retain the semantics
    # please do.
    #
    # -cyrus
    
    __init__.__wrapped_init = fn #@UndefinedVariable
    __init__.__defaults = __defaults #@UndefinedVariable
    _functools.update_wrapper(__init__, fn) #@UndefinedVariable
    return __init__ #@UndefinedVariable
def _empty_init(self): pass

class _new_initializer(object):
    def __init__(self, cls):
        self.__cls = cls

    def __call__(self, *args, **kwargs):
        return self.__cls(*args, **kwargs)

    def __str__(self):
        return "<new %s>" % self.__cls

    def __repr__(self):
        return str(self)

class _new(object):
    _defaults = { }

    def __getitem__(self, cls):
        _defaults = self._defaults
        if _defaults.has_key(cls):
            return _defaults[cls]
        else:
            default = _new_initializer(cls)
            _defaults[cls] = default
            return default

    def __setitem__(self, key, value):
        self._defaults[key] = value

    def __delitem__(self, key):
        del self._defaults[key]

new = _new()
NotInitialized = Token("NotInitialized")
Default = Token("Default")

# see http://docs.python.org/reference/expressions.html#atom-identifiers
def mangle(cls, name):
    """Applies Python name mangling using the provided class and name."""
    return "_" + cls.__name__ + "__" + name

def unmangle(cls, name):
    """Given a name mangled using cls unmangles it.
    
    Undefined output (probably an empty string or an error) if it is not a
    mangled name or wasn't mangled using cls.
    """
    return name[3+len(cls.__name__):]

def is_senior_subclass(obj, cls, testcls):
    """Determines whether the cls is the senior subclass of basecls for obj.

    The most senior subclass is the first class in the mro which is a subclass
    of testcls.

    Use for inheritance schemes where a method should only be called once by the
    most senior subclass.

    Don't use if it is optional to call the base method!

    In that case, the most reasonable way to do it is to ensure the method is
    idempotent and deal with the hopefully small inefficiency of calling it
    multiple times. Doing a hasattr check in these implementations should be
    relatively efficient.

    In particular, __init__ for mixins tends to act like this.
    """
    for base in obj.__class__.mro():
        if base is cls:
            return True
        else:
            if issubclass(base, testcls):
                return False
            
class intern(object):  
    # a class just so the name mangling mechanisms are invoked, deleted below
    
    @staticmethod
    def intern(cls_):
        """Transforms the provided class into an interned class.
        
        That is, initializing the class multiple times with the same arguments 
        (even if in a different order if using keyword arguments) should 
        always produce the same object, and __init__ should only be called the 
        first time for each unique set of arguments.
        
        This means that mutations will effectively be shared by all "instances" 
        of the class which shared initialization arguments. This might be 
        useful for storing metadata, for example.
        
            >>> class N(object):
            ...     def __init__(self, n):
            ...         self.n = n
            >>> N = intern(N)
            >>> five = N(5)
            >>> five2 = N(5)
            >>> five is five2
            True
            >>> five.is_odd = True
            >>> five2.is_odd
            True
            
        To enforce immutability of particular attributes, see the setonce 
        property modifier.
            
        The use of the term "intern" comes from the practice of string 
        interning used widely in programming languages, including Python. Look 
        it up.
        
        Can be used as a class decorator in Python 2.6+. Otherwise, use like 
        this:
        
            >>> class Test(object): pass
            >>> Test = intern(Test)
        
        .. Note:: Subclassing of intern classes with different __init__
                  arguments is tricky and probably should not be done if you 
                  don't understand precisely how this works.
                  
                  If you subclass with the same __init__ arguments (preferably
                  the same __init__) it will use the SAME pool. This can be used
                  to automate adding metadata as above, though you should 
                  probably just do that with a function.

        .. Note:: You can override the hash function used by providing a value
                  for __init__._intern__hash_function. This should take None
                  as the first argument (substituting for self) and then *args
                  and **kwargs (or your particular signature for __init__) and
                  produce a hash or hashable value.
                  
                  The default implementation is provided by fn_arg_hash_function
                  applied to __init__, or generic_arg_hash_function if that 
                  doesn't work.
        
        """
        cls_.__pool = { }
        
        __init__ = cls_.__init__
        try:
            __init__.im_func.__hash_function
        except AttributeError:
            try:
                __init__.im_func.__hash_function = \
                        fn_arg_hash_function(__init__)
            except (AttributeError, TypeError): pass
            
        # define an override for __new__ which looks in the cache first
        def __new__(cls, *args, **kwargs):
            """Override used by cypy.intern to cache instances of this class."""
            
            # check cache
            __init__ = cls.__init__
            try:
                hash_function = __init__.im_func.__hash_function
            except AttributeError:
                try:
                    hash_function = __init__.im_func.__hash_function = \
                                  fn_arg_hash_function(__init__)
                except (AttributeError, TypeError):
                    hash_function = generic_arg_hash_function
            
            try:
                # look-up object
                hash = hash_function(None, *args, **kwargs)  # none because self is not created yet
                obj = cls_.__pool[hash]
            except (TypeError, KeyError) as e:
                # if arguments not hashable or object not found, need to 
                # make a new object
                
                # restore the original new temporarily, if it existed
                orig_new = __new__.orig
                if orig_new is _NotDefined: del cls_.__new__
                else: cls_.__new__ = orig_new
                
                # create new object
                obj = cls(*args, **kwargs)
                
                # put it in ze pool
                if isinstance(e, KeyError):
                    cls_.__pool[hash] = obj
                
                # re-override __new__
                cls_.__new__ = __static_new__
                                
            # Return the instance but don't call __init__ since it was done 
            # when it was created the first time, see below for how this is 
            # done
            try: cls.__old_init = cls.__dict__['__init__']
            except KeyError: cls.__old_init = _NotDefined            
            cls.__init__ = _dummy_init
                
            return obj
            
        # save original __new__
        try: __new__.orig = staticmethod(cls_.__dict__['__new__'])
        except KeyError: 
            if cls_.__new__ is object.__new__:
                __new__.orig = _null_new
            else:
                __new__.orig = _NotDefined
        
        __static_new__ = staticmethod(__new__)
        cls_.__static_new__ = __static_new__
        cls_.__new__ = __static_new__
        return cls_
intern = intern.intern
def _dummy_init(self, *args, **kwargs): #@UnusedVariable
    """Prevents __init__ from being called if returning a obj copy."""
    cls = type(self)
    old_init = cls._intern__old_init
    if old_init is _NotDefined:
        del cls.__init__
    else:
        cls.__init__ = old_init
    del cls._intern__old_init
    
@staticmethod
def _null_new(cls, *args, **kwargs): #@UnusedVariable
    # deprecation warning if you don't do this
    return object.__new__(cls)
_NotDefined = object() # sentinel for when __new__ or __init__ are not defined

##############################################################################
## Strings and Regular Expressions
##############################################################################
def string_escape(string, delimiter='"'):
    """Turns special characters into escape sequences in the provided string.

    Supports both byte strings and unicode strings properly. Any other values
    will produce None.

    Example:
    >>> string_escape("a line\t")
    "a line\\t"
    >>> string_escape(u"some fancy character: \u9999")
    u"\\u9999"
    >>> string_escape(5)
    None
    """
    if isinstance(string, str):
        escaped = string.encode("string-escape")
    elif isinstance(string, unicode):
        escaped = unicode(string.encode("unicode-escape"))
    else:
        raise Error("Unexpected string type.")
    return delimiter + escape_quotes(escaped, delimiter) + delimiter

def escape_quotes(string, quote_type='"'):
    if isinstance(string, str):
        return string.replace(quote_type, "\\" + quote_type)
    elif isinstance(string, unicode):
        return string.replace(quote_type, unicode("\\") + quote_type)
    else:
        raise Error("Unexpected string type.")
    
def to_file(str, filename, mode='w'):
    f = open(filename, mode)
    f.write(str)
    f.close()

re_inner_newline = _re.compile(r"(?<!^)\n(?!$)")
re_nonend_newline = _re.compile(r"\n(?!$)")
re_opt_spaces = _re.compile("( *)")
re_opt_initial_indentation = _re.compile("^( *)")
include_final_suffix = {
    True: r"",
    False: r"(?!$)"
}
include_first_nl_prefix = {
    True: r"(\n|^)",
    False: r"(?<=\n)"
}

## Processing triple quotes
# Everything assumes you're using spaces.
def re_line_and_indentation(base_indentation,
                            modifiers=(True, True)):
    """Returns a re matching newline + base_indentation.

    modifiers is a tuple, (include_first, include_final).

    If include_first, matches indentation at the beginning of the string.
    If include_final, matches indentation at the end of the string.

    Cached.
    """
    cache = re_line_and_indentation.cache[modifiers]
    compiled = cache.get(base_indentation, None)
    if compiled is None:
        [prefix, suffix] = re_line_and_indentation.tuple[modifiers]
        compiled = cache[modifiers] = \
            _re.compile(prefix + base_indentation + suffix)
    return compiled
_ = re_line_and_indentation
_truth_table = tuple(all_pairs(bool_vals))
_.cache = dict((pair, {}) for pair in _truth_table)
_.tuple = dict((pair, (include_first_nl_prefix[pair[0]],
                       include_final_suffix[pair[1]]))
                        for pair in _truth_table)

def get_initial_indentation(code):
    return re_opt_spaces.match(code).string

re_new_line_indentation = {
    True: _re.compile(r"(?:\n|^)+( *)(?=[^ ])"),
    False: _re.compile(r"\n+( *)(?=[^ ])")
}
def get_base_indentation(code, include_start=False):
    """Heuristically extracts the base indentation from the provided code.

    Finds the smallest indentation following a newline not at the end of the
    string.
    """
    new_line_indentation = re_new_line_indentation[include_start].finditer(code)
    new_line_indentation = tuple(m.groups(0)[0] for m in new_line_indentation)
    if new_line_indentation:
        return min(new_line_indentation, key=len)
    else:
        return ""

re_final_indentation = _re.compile("( +)$")
def get_final_indentation(code):
    """Heuristically extracts the final indentation of the provided code."""
    match = re_final_indentation.findall(code)
    if match:
        return match[0]
    else:
        return ""

def fix_indentation(code, base_indentation=None, correct_indentation="",
                    modifiers=(True, True)):
    """Replaces base_indentation at beginning of lines with correct_indentation.

    If base_indentation is None, tries to find it using get_base_indentation.
    modifiers are passed to re_line_and_indentation. See there for doc.
    """
    if base_indentation is None:
        base_indentation = get_base_indentation(code, modifiers[0])
    return re_line_and_indentation(base_indentation, modifiers).sub(
        "\n" + correct_indentation, code)

################################################################################
# Dictionaries of various sorts
################################################################################
class attr_lookup(object):
    """Redirects item lookups to the attributes of the provided object.

    The main use is to allow the % operator to be used with objects, e.g.

        >>> class Test:
        ...     a = 'A'
        ...     b = 'B'
        ...
        ...     @property
        ...     def c(self): return 'C'
        >>> o = Test()
        >>> print "%(a)d, %(b)s, %(c)s" % attr_lookup(o)
        A, B, C

    A KeyError is raised if not found.
    """
    def __init__(self, obj, default=no_default):
        self.obj = obj
        if default is not no_default:
            self.default = default

    obj = None
    _has_default = False

    def _get_default(self):
        return self._default

    def _set_default(self, value):
        self._default = value
        self._has_default = True

    def _del_default(self):
        if self._has_default:
            self._has_default = False
            self._default = None

    default = property(_get_default, _set_default, _del_default)

    def __getitem__(self, key):
        try:
            if self._has_default:
                return getattr(self.obj, key, self.default)
            else:
                return getattr(self.obj, key)
        except AttributeError:
            raise KeyError(key)

class KeyCache(object):
    """A mutable map which calls self.compile(key) if it is not found on lookup.

    No default self.compile is provided.
    """
    def __init__(self):
        self.dict = { }

    def __getitem__(self, key):
        val = self.dict.get(key, None)
        if val is None:
            val = self.dict[key] = self.compile(key)
        return val

    def __setitem__(self, key, val):
        self.dict[key] = val

    def __delitem__(self, key):
        del self.dict[key]    

class frozendict(dict):
    def __new__(cls, *args, **kwargs):
        obj = dict.__new__(cls)
        dict.__init__(obj, *args, **kwargs)
        return obj
    
    def __init__(self, *args, **kwargs):
        # covered in __new__
        pass
    
    def __hash__(self):
        return hash(frozenset(self.iteritems()))

    def __repr__(self):
        return "frozendict(%s)" % dict.__repr__(self)

    @property
    def _NO_BAD(self):
        raise AttributeError("Cannot modify a frozendict.")
    
    __delitem__ = __setitem__ = clear = pop = popitem = setdefault = update = \
        _NO_BAD
        
class stack(list):
    """A stack is a list which iterates in reverse by default.
    
        >>> x = stack(xrange(10))
        >>> for i in x:
        ...     print i,
        9 8 7 6 5 4 3 2 1 0
        
    """
    def __new__(cls, *args, **kwargs):
        obj = list.__new__(cls)
        list.__init__(obj, *args, **kwargs)
        return obj
    
    def __init__(self, *args, **kwargs):
        # covered in __new__
        pass
    
    def __iter__(self):
        return reversed(self)
    
class SetList(list):
    """A list where each element appears only once, in the position it was 
    originally inserted."""
    def __new__(cls, *args, **kwargs):
        obj = list.__new__(cls)
        list.__init__(obj, *args, **kwargs)
        return obj
    
    def __init__(self, *args, **kwargs):
        # covered in __new__
        pass
    
    def append(self, x):
        if x not in self:
            super(SetList, self).append(x)
        
    def extend(self, L):
        for item in L:
            self.append(item)
            
    def insert(self, i, x):
        if x not in self:
            super(SetList, self).insert(i, x)
        
class stack_lookup(object):
    """Looks up keys from a stack of dictionaries.
    
        >>> lookup = stack_lookup(stack({'b': "A"}, {'b': "B"}))
        >>> lookup['b'] == "B"
        True
        
    """
    @autoinit
    def __init__(self, dict_stack=new[stack]): pass
            
    _has_default = False
    @property
    def has_default(self):
        return self._has_default
    
    def _get_default(self):
        return self._default
    
    def _set_default(self, value):
        self._default = value
        self._has_default = True
        
    def _del_default(self):
        if self._has_default:
            self._has_default = False
            self._default = None
    _doc_default = """If not found in stack, the default will be returned if 
    defined. If not, a KeyError is raised."""
    default = property(_get_default, _set_default, _del_default, _doc_default)
    
    def __getitem__(self, key):
        for dict in self.dict_stack:
            try:
                return dict[key]
            except KeyError: pass
            
        if self.has_default:
            return self.default
        else:
            raise KeyError(key)
        
    def append(self, dict):
        """Convenience method for appending a dictionary to the stack."""
        self.dict_stack.append(dict)
        
    def pop(self):
        """Convenience method for popping a dictionary from the stack."""
        return self.dict_stack.pop()

# Copyright (C) 2009 Raymond Hettinger

#                          *** MIT License ***
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

## {{{ http://code.activestate.com/recipes/576694/ (r7)
import collections

KEY, PREV, NEXT = range(3)

class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[PREV]
            curr[NEXT] = end[PREV] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[NEXT] = next
            next[PREV] = prev

    def __iter__(self):
        end = self.end
        curr = end[NEXT]
        while curr is not end:
            yield curr[KEY]
            curr = curr[NEXT]

    def __reversed__(self):
        end = self.end
        curr = end[PREV]
        while curr is not end:
            yield curr[KEY]
            curr = curr[PREV]

    def pop(self, last=True):
        # changed default to last=False - by default, treat as queue.
        if not self:
            raise KeyError('set is empty')
        key = next(reversed(self)) if last else next(iter(self))
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

    def __del__(self):
        self.clear()                    # remove circular references
# END {{{ http://code.activestate.com/recipes/576694/ (r7)

from collections import MutableMapping

class OrderedDict(dict, MutableMapping):

    # Methods with direct access to underlying attributes

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at 1 argument, got %d', len(args))
        if not hasattr(self, '_keys'):
            self._keys = []
        self.update(*args, **kwds)

    def clear(self):
        del self._keys[:]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            self._keys.append(key)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __iter__(self):
        return iter(self._keys)

    def __reversed__(self):
        return reversed(self._keys)

    def popitem(self):
        if not self:
            raise KeyError
        key = self._keys.pop()
        value = dict.pop(self, key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        inst_dict = vars(self).copy()
        inst_dict.pop('_keys', None)
        return (self.__class__, (items,), inst_dict)

    # Methods with indirect access via the above methods

    setdefault = MutableMapping.setdefault
    update = MutableMapping.update
    pop = MutableMapping.pop
    keys = MutableMapping.keys
    values = MutableMapping.values
    items = MutableMapping.items

    def __repr__(self):
        pairs = ', '.join(map('%r: %r'.__mod__, self.items()))
        return '%s({%s})' % (self.__class__.__name__, pairs)

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d
    
##############################################################################
## Naming
##############################################################################
class Naming(object):
    """A mixin to provide naming operations to an object with a parent."""
    @autoinit
    def __init__(self, basename, **kwargs): #@UnusedVariable
        self.__counts = { }
        
    @setonce(property)
    def basename(self):
        """The base name specified for this object. May not be unique."""
        return self.__basename
    
    @basename.setter
    def basename(self, value): #@DuplicatedSignature
        self.__basename = value
        
    @lazy(property)
    def name(self):
        """The unique name of this object, relative to the parent."""
        basename = self.basename
        if basename is None:
            return None
        
        parent = self.Naming_parent
        if parent is None:
            return basename
        else:    
            return parent.generate_unique_name(basename)
        
    @property
    def Naming_parent(self):
        """The parent object to use for generating a unique name.
        
        Defaults to ``self.parent`` if defined and if it has a 
        ``generate_unique_name`` attribute. Use with a tree mixin below for
        best results.
        """
        try:
            parent = self.parent
        except AttributeError:
            return None
        else:
            if hasattr(parent, 'generate_unique_name'):
                return parent
            return None
        
    def generate_unique_name(self, basename):
        """Generates a unique name for a child given a base name."""
        counts = self.__counts
        try:
            count = counts[basename]
            counts[basename] += 1
        except KeyError:
            count = 0
            counts[basename] = 1
            
        prefix = self.Naming_prefix

        if count == 0:
            name = prefix + basename
        else:
            name = prefix + basename + "_" + str(count)
            
        if prefix != "" or count != 0:
            try:
                count = counts[name]
                return self.generate_unique_name(name)
            except KeyError:
                # wasn't already used so return it
                counts[name] = 1
        return name
        
    @property
    def Naming_prefix(self):
        """The prefix to use when generating a unique name for a child.
        
        Defaults to ``self.name + "_"`` if ``self.name`` is not ``None``, or 
        an empty string if it is.
        """
        name = self.name
        if name is None:
            return ""
        else:
            return name + "_"
        
##############################################################################
## Trees
##############################################################################
class UpTree(object):
    """A node in a tree containing a reference to its parent."""
    @autoinit
    def __init__(self, parent=None, auto_manage_parent=True): pass
    
    __parent = None
    
    @property
    def parent(self):
        """The parent node."""
        return self.__parent
    
    @parent.setter
    def parent(self, value): #@DuplicatedSignature
        if self.auto_manage_parent:
            self.remove_from_parent()
            self.__parent = value
            self.add_to_parent()
        else:
            self.__parent = value
            
    @parent.deleter
    def parent(self): #@DuplicatedSignature
        if self.auto_manage_parent:
            self.remove_from_parent()
        del self.__parent
        
    __auto_manage_parent = False # so initial set is direct
    @property
    def auto_manage_parent(self):
        """If true, setting :data:`parent` will cause the parent's ``children``
        collection to be updated automatically if it exists."""
        return self.__auto_manage_parent
    
    @auto_manage_parent.setter
    def auto_manage_parent(self, value): #@DuplicatedSignature
        self.__auto_manage_parent = value
        if value:
            self.add_to_parent()
            
    def add_to_parent(self):
        """Adds this node to the parent's ``children`` collection if it exists."""
        parent = self.parent
        if parent is not None:
            try:
                children = parent.children
            except AttributeError: pass
            else:
                include(children, self)
        
    def remove_from_parent(self):
        """Removes this node from the parent's ``children`` collection if it exists."""
        parent = self.parent
        if parent is not None:
            try:
                children = parent.children
            except AttributeError: pass
            else:
                remove_upto_once(children, self)
                
    def iter_up(self, include_self=True):
        """Iterates up the tree to the root."""
        if include_self: yield self
        parent = self.parent
        while parent is not None:
            yield parent
            try:
                parent = parent.parent
            except AttributeError:
                return
            
    @property
    def root(self):
        """The root of the tree."""
        for node in self.iter_up():
            cur_node = node
        return cur_node
    
    def getrec(self, name, include_self=True, *default):
        """Look up an attribute in the path to the root."""
        for node in self.iter_up(include_self):
            try:
                return getattr(node, name)
            except AttributeError: pass
            
        if default:
            return default[0]
        else:
            raise AttributeError(name)
        
    def hasrec(self, name, include_self=True):
        try:
            self.getrec(name, include_self)
            return True
        except:
            return False
        
class DownTree(object):
    """A node in a tree referencing only its children."""
    @autoinit
    def __init__(self, children=new[list]): pass
    
    children = None
    """The collection of children (a list or set)."""
    
    def trigger_hook(self, name, *args, **kwargs):
        """Recursively call a method named ``name`` with the provided args and
        keyword args if defined."""
        method = getattr(self, name, None)
        if is_callable(method):
            method(*args, **kwargs)
            
        try:
            children = self.children
        except AttributeError:
            return
        else:
            if children is not None:
                for child in children:
                    method = getattr(child, 'trigger_hook', None)
                    if is_callable(method):
                        method(name, *args, **kwargs)
                    else:
                        method = getattr(child, name, None)
                        if is_callable(method):
                            method(*args, **kwargs)

    def trigger_staged_hook(self, name, *args, **kwargs):
        """Calls a three-staged hook:
        
        1. ``"pre_"+name``
        2. ``"_on_"+name``
        3. ``"post_"+name``
        
        """
        self.trigger_hook("pre_" + name, *args, **kwargs)
        self.trigger_hook("on_" + name, *args, **kwargs)
        self.trigger_hook("post_" + name, *args, **kwargs)

class BidirectionalTree(UpTree, DownTree):
    """:class:`UpTree` and :class:`DownTree` combined."""
    @autoinit
    def __init__(self, parent=Default, children=Default): pass

################################################################################
# Misc.
################################################################################
class Accumulator(object):
    """Accumulates a ``value`` using the += operator."""
    def __init__(self, initial=0.0):
        self.value = initial
        
    def __iadd__(self, value):
        self.value += value
