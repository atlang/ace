"""String-based code generation utilities."""

import re

import cypy
    
## Code generator
class CG(object):
    """Provides a simple, flexible code generator."""
    @cypy.autoinit
    def __init__(self, processor=None,
                       code_builder=cypy.new[list],
                       convert=str,
                       fix_indentation=cypy.fix_indentation,
                       indent_depth=0,
                       default_indent=4,
                       fork_arguments=("processor",
                                       "convert",
                                       "fix_indentation",
                                       "default_indent")): pass
    
        
    ## Basic API
    def append(self, code):
        """Core API method for appending to the source code stream.

        It can take the following as input.

        *Strings*
            The processor is called if specified. String values from the 
            processed stream are added after newlines are alided and indented. 
            Other values are recursed on.
            
            Multiple adjacent newlines which straddle appends are alided to 
            produce a single newline. To insert multiple newlines, they must
            be adjacent in the same string passed to append.
            
        *Callables*
            Callables taking no arguments are called and their return value
            recursed on if not ``None`` or ``self``.
            
            Callables taking one argument are called with ``self`` and their
            return value is recursed on if not ``None`` or ``self``.

        *Iterables*
            The items recursed on.

        *Expressions*
            If ``code._CG_expression`` is defined, that value is recursed on.
            
            If ``code._CG_context`` is defined, its value will be appended to
            the processor using ``append``, if possible, while recursing.

        *Convertables*
            See :data:`convert`.
            
        """
        # support one-shot push and pop of dictionaries using operators
        pop_next = self._pop_next
        if pop_next:
            self._pop_next = False

        if isinstance(code, basestring):
            # Strings are processed, then indented appropriately
            for token in self._process(code):
                prev = self.last_string
                prev_ends_with_nl = prev is None or prev.endswith('\n')
                token_starts_with_nl = token.startswith("\n")
                indent_depth = self.indent_depth
                if prev_ends_with_nl:
                    if indent_depth > 0:
                        self.code_builder.append(self.indent_str)
                    if token_starts_with_nl:
                        token = token[1:]

                if indent_depth > 0:
                    token = cypy.re_nonend_newline.sub(
                        "\n" + self.indent_str, token)

                if token != "":
                    self.code_builder.append(token)
        else: self._process_nonstrings(code)

        if pop_next:
            self.pop_context()
        return self
        
    @classmethod
    def append_once(cls, code, **kwargs):
        """One-off code generation using append.
        
        If keyword args are provided, initialized using 
        :meth:`with_id_processor`.
        """
        if kwargs:
            g = cls.with_id_processor()
            g._append_context(kwargs)
        else:
            g = cls()
        g.append(code)
        return g.code
    
    def _process_nonstrings(self, code):
        if code is not None and code is not self:
            expr = getattr(code, '_CG_expression', None)
            if expr is not None:
                # Push the value's context onto stack
                context = getattr(code, '_CG_context', None)
                if context:
                    self._append_context(context)
                else:
                    context = None

                self.append(expr)

                if context:
                    self.pop_context()
            elif cypy.is_callable(code):
                code = self._call_callable(code)
                if code is not None and code is not self:
                    self.append(code)
            elif cypy.is_iterable(code):
                for item in code:
                    self.append(item)
            else:
                self.append(self._convert(code))
    
    def extend(self, code):
        """Appends each item in code, which should be iterable.

        .. Note:: Since :meth:`append` supports iterables, you can always just
                  use that. This method is here to complete the list analogy.
        
        """
        self.append(code)
        return self

    def lines(self, code):
        """Fixes indentation for multiline strings before appending."""
        if isinstance(code, basestring):
            fix_indentation = self.fix_indentation
            if fix_indentation:
                code = fix_indentation(code)
            return self.append(code)
        else:
            return self.append(code)

    @classmethod
    def lines_once(cls, code, **kwargs):
        """One-off code generation using :meth:`lines`.
        
        If keyword args are provided, initialized using
        :meth:`with_id_processor`.
        """
        if kwargs:
            g = cls.with_id_processor()
            g._append_context(kwargs)
        else:
            g = cls()
        g.lines(code)
        return g.code
    
    fix_indentation = cypy.fix_indentation
    """Called by lines to fix indentation before passing on to append.

    Defaults to :func:`cypy.fix_indentation`. Called with the code.
    Should return a left-justified string.
    """

    processor = None
    """Called with strings to append. Should return an iterator.
    
    If not specified, acts as if it yielded the input without modification.
    """
    
    @classmethod
    def with_id_processor(cls, *args):
        """Returns a new instance with the processor set to a new instance 
        of :class:`IdentifierProcessor`, appropriately initialized to process
        non-strings appropriately.
        """
        ip = IdentifierProcessor()
        g = cls(ip, *args)
        ip.nonstring_processor = lambda _, substitution: \
            g._process_nonstrings(substitution)
        return g
       
    convert = str
    """Called on values not matching other categories in append().

    The result is recursed on if not None. Defaults to str().
    """

    code_builder = [ ]
    """The list of string appends so far."""

    @property
    def last_string(self):
        """The last entry in code_builder, or ``None`` if none so far."""
        cb = self.code_builder
        len_cb = len(cb)
        if len_cb > 0:
            return cb[len_cb - 1]
        else:
            return None

    @property
    def code(self):
        """Returns the concatenated list of strings upon access."""
        return "".join(self.code_builder)

    ## Indentation management
    indent_depth = 0
    """The current indentation depth, in spaces."""

    default_indent = 4
    """The number of spaces to indent by default. Defaults to 4."""

    @property
    def indent_str(self):
        """The current indent string. ``" "*self.indent_depth``"""
        return " "*self.indent_depth

    @staticmethod
    def tab(g):
        """A token which will increase the indent depth by the default amount 
        if added to the stream."""
        g.indent_depth += g.default_indent

    @staticmethod
    def untab(g):
        """A token which will decrease the indent depth by the default amount 
        if added to the stream"""
        g.indent_depth -= g.default_indent

    ## Internals
    def _process(self, expr):
        processor = self.processor
        if processor is not None:
            for processed in processor(expr):
                yield processed
        else:
            yield expr

    def _call_callable(self, code):
        nargs = cypy.fn_minimum_argcount(code)
        if nargs == 0:
            rv = code()
        elif nargs == 1:
            rv = code(self)
        else:
            raise ValueError("Callable must take either 0 or 1 arguments without defaults.")

        return rv

    def _convert(self, code):
        if self.convert is not None:
            return self.convert(code)

    ## Operators API
    def __lshift__(self, right):
        self.append(right)
        return self

    def __rrshift__(self, left):
        self.append(left)
        return self

    def __rshift__(self, right):
        self.lines(right)
        return self

    def __rlshift__(self, left):
        self.lines(left)
        return self

    ## Processor Contexts API [Experimental]
    def __call__(self, **context):
        if context:
            self.append_context(**context)
            self._pop_next = True
        return self
    _pop_next = False

    def append_context(self, **context):
        """Appends the provided keyword arguments to the processor."""
        self._append_context(context)
        
    def _append_context(self, context):
        processor = getattr(self, 'processor', None)
        if processor is not None:
            append_context = getattr(processor, 'append_context', None)
            if append_context is None:
                append_context = getattr(processor, 'append', None)
            if append_context is not None:
                append_context(context)

    def pop_context(self):
        """Pops the last set of keyword arguments provided to the processor."""
        processor = getattr(self, 'processor', None)
        if processor is not None:
            pop_context = getattr(processor, 'pop_context', None)
            if pop_context is None:
                pop_context = getattr(processor, 'pop', None)
            if pop_context is not None:
                return pop_context()
        if self._pop_next:
            self._pop_next = False

## Processing identifiers
class IdentifierProcessor(object):
    """Breaks a string into identifiers and replaces them using the substitutor.

        >>> ip = IdentifierProcessor(stack_lookup(stack({'chocolate': 'pudding'})))
        >>> ip('who wants chocolate?')
        'who wants pudding?'

    """
    @cypy.autoinit
    def __init__(self,
                 substitutor=cypy.new[cypy.stack_lookup],
                 recursive=False,
                 exclude=cypy.new[set],
                 nonstring_processor=None): 
        pass

    substitutor = None
    """The map to look up identifiers in for their substitution.

    KeyErrors result in the identifier being left unchanged.
    """

    recursive = True
    """If True, string substitutions are recursed on until they yield unchanged 
    values.

    The exclude stack prevents some classes of runaway recursion by excluding
    the identifier being recursed on.
    """

    exclude = None
    """The set of identifiers to exclude from replacement.

    Used internally if recursive is True.
    """
    
    nonstring_processor = None
    """The function to call on non-strings that are returned by the substitutor.
    
    Called with ``token, substitution``.
    
    If ``None``, the non-string is yielded directly.
    
    If the return value is not None, it is yielded.
    
    The result is not recursed on.
    """

    def __call__(self, code):
        recursive = self.recursive
        re_non_identifier = self.re_non_identifier
        nonstring_processor = self.nonstring_processor
        for token in re_non_identifier.split(code):
            if token in self.exclude or re_non_identifier.match(token):
                # don't molest tokens in exclude list and non-identifiers
                # (this could be more efficient if we tested the first value
                #  then alternated instead of checking each one)
                yield token
            else:
                if token == "": continue

                if recursive: cypy.include(self.exclude, token)
                try:
                    substitution = self.substitutor[token]
                except KeyError:
                    yield token
                else:
                    if recursive and isinstance(substitution, basestring):
                        for final in self(substitution):
                            yield final
                    elif substitution is not None:
                        if nonstring_processor is not None:
                            substitution = nonstring_processor(token, 
                                                               substitution)
                            if substitution is not None: yield substitution
                        else:
                            yield substitution
                    else:
                        yield token
                if recursive: cypy.remove_once(self.exclude, token)

    re_non_identifier = re.compile(r"(\W+)")
    """A regular expression to match non-identifiers for use with re.split."""

    def append(self, dict):
        """``append`` the provided ``dict`` to the ``substitutor``.
    
        Will return an AttributeError if the substitutor does not support
        append. The default substutitor, a :class:`cypy.stack_lookup`,
        does.
        """
        self.substitutor.append(dict)

    def pop(self):
        """``pop`` the last item appended to the ``substitutor``."""
        return self.substitutor.pop()

class Partitioner(object):
    """Use the code generator to create an efficient if/else if/else block
    against a numeric variable.

    Removes redundant checks against previous blocks or the min and max that
    a simple strategy might include.

    Example:

        >>> g = CG()
        >>> p = Partitioner(g.append, "rank", min_start=0, max_end=1000)
        >>> p.next(start=10, end=100, code='almost()')
        >>> p.next(move=100, code='not_bad()')
        >>> p.next(start=500, code='you_need_practice()')
        >>> print g.code
        if 10 <= rank < 100:
            almost()
        elif rank < 200:
            not_bad()
        elif rank >= 500:
            you_need_practice()

    Notes:
    
    - Ranges must be ordered (i.e. start must be >= the previous end.)
    - Ranges are checked Python style, that is against [start, end).
    
    """
    @cypy.autoinit
    def __init__(self, callback=None, var_name=None, min_start=0,
                 max_end=cypy.inf):
        pass

    callback = None
    """Callback for appends."""

    var_name = None
    """Comparison variable name."""

    min_start = None
    """The lower bound."""

    max_end = None
    """The upper bound. Use cypy.inf for none."""

    _index = 0
    _prev_end = cypy.NotInitialized

    ## Language-related
    if_start = "\nif "
    """The string which begins an if statement. Defaults to ``'\\nif '``."""
    else_if_start = "elif "
    """The string which begins an else if statement. Defaults to ``'elif '``."""
    
    guard_end = (":\n", CG.tab)
    """The string which ends a guard. Defaults to ``(":\\n", CG.tab)``."""
    
    else_start = ("else:\n", CG.tab)
    """The string which begins an else statement. Defaults to ``('else:\\n', CG.tab)``."""
    
    block_end = (CG.untab, "\n")
    """The string which ends a block. Defaults to ``(CG.untab, '\\n')``."""

    @staticmethod
    def lt(left, right):
        """Generates the expression to compare two operands using ``<``."""
        return "%s < %s" % (left, right)
    
    @staticmethod
    def gte(left, right):
        """Generates the expression to compare two operands using ``>=``."""
        return "%s >= %s" % (left, right)
    
    @staticmethod
    def range(left, middle, right):
        """Generates the expression to compare a value in a range.
        
        Defaults to ``left <= middle < right``.
        """
        return "%s <= %s < %s" % (left, middle, right)
    
    def _guard(self, code, conditional, condition):
        self.callback((conditional, condition, self.guard_end,
                       code,
                       self.block_end))

    def _else(self, code):
        self.callback((self.else_start, code, self.block_end))

    def next(self, move=None, start=None, end=None, code=None):
        if start is None: start = self._prev_end
        if move is None:
            if end is None: end = self.max_end
        else:
            assert end is None
            end = start + move

        assert start >= self.min_start
        assert end <= self.max_end

        index = self._index
        if index == 0:
            cur_conditional = self.if_start
        else:
            cur_conditional = self.else_if_start

        if self._prev_end is cypy.NotInitialized:
            self._prev_end = self.min_start

        if start == self._prev_end:
            # No first check needed
            if end == self.max_end:
                # No last check needed
                if index == 0:
                    # No block needed
                    self.callback(code)
                else:
                    # Final else
                    self._else(code)
            else:
                # Only last check needed
                self._guard(code, cur_conditional,
                            self.lt(self.var_name, str(end)))
        else:
            if end == self.max_end:
                # Only first check needed
                condition = self.gte(self.var_name, str(start))
            else:
                # Both checks needed
                condition = self.range(str(start), self.var_name, str(end))

            self._guard(code, cur_conditional, condition)

        self._index += 1
        self._prev_end = end

## Generation trees
class Node(cypy.BidirectionalTree, cypy.Naming):
    """Base node class for a generation tree.

    .. Note:: These aren't abstract syntax trees. They decribe components of 
              a program. If you want software engineering mumbo-jumbo, try to 
              read about `Frame Technology
              <http://en.wikipedia.org/wiki/Frame_Technology_%28software_engineering%29>`_.

    """
    @cypy.autoinit
    def __init__(self, parent, basename, **kwargs): #@UnusedVariable
        self.__appended_context = { }
    
    def _make_code_generator(self):
        # Simple class which maintains a list of strings to concatenate at the
        # end to produce code and provides some useful helper functions so
        # indentation isn't messed up and such.
        g = CG.with_id_processor()
        g.processor.recursive = True
        return g
    
    def trigger_cg_hook(self, name, g, header=None, *args, **kwargs):
        if header is not None:
            g << "# ___" + header + "___\n"
            
        appended_context = False
        if g not in self.__appended_context: # check so there aren't extra copies wasting time
            g._append_context(self._name_lookup)
            self.__appended_context[g] = appended_context = True
        
        method = getattr(self, name, None)
        if cypy.is_callable(method):
            method(g, *args, **kwargs)
            
        try:
            children = self.children
        except AttributeError:
            return
        else:
            if children is not None:
                for child in children:
                    method = getattr(child, 'trigger_cg_hook', None)
                    if cypy.is_callable(method):
                        method(name, g, None, *args, **kwargs)
                    else:
                        method = getattr(child, name, None)
                        if cypy.is_callable(method):
                            method(*args, **kwargs)

        if appended_context:
            g.pop_context()
            del self.__appended_context[g]

    def trigger_staged_cg_hook(self, name, g, *args, **kwargs):
        """Calls a three-staged hook:
        
        1. ``"pre_"+name``
        2. ``"in_"+name``
        3. ``"post_"+name``
        
        """
        print_hooks = self._print_hooks
        # TODO: document name lookup business
        # TODO: refactor this context stuff, its confusing
        hook_name = "pre_" + name
        printed_name = hook_name if print_hooks else None
        self.trigger_cg_hook(hook_name, g, printed_name, *args, **kwargs) # TODO: avoid copies
        
        hook_name = "in_" + name
        printed_name = hook_name if print_hooks else None
        self.trigger_cg_hook(hook_name, g, printed_name, *args, **kwargs)
        
        hook_name = "post_" + name
        printed_name = hook_name if print_hooks else None
        self.trigger_cg_hook(hook_name, g, printed_name, *args, **kwargs)
        
    _print_hooks = False
        
    @cypy.lazy(property)
    def _name_lookup(self):
        return cypy.attr_lookup(self)

class StandaloneCode(Node):
    """A node for inserting standalone code at a particular named hook."""
    @cypy.autoinit
    def __init__(self, parent, hook=None, code=None, basename="StandaloneCode"): 
        pass
    
    def __getattr__(self, name):
        if name != 'hook' and name == self.hook:
            return self.__insert_code
        raise AttributeError(name)
    
    def __insert_code(self, g):
        self.code >> g
      
class Listener(Node):
    def __init__(self, parent, hook, callback, basename="Listener"):
        Node.__init__(self, parent, basename)
        self.hook = hook
        self.callback = callback
        setattr(self, hook, callback)
