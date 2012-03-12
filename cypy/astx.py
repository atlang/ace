"""Utilities for working with the python ast module."""

import ast as _ast 

import cypy

def init_node(cls, *args, **kwargs):
    """Initializes an ast node with the provided attributes.
    
    Python 2.6+ supports this in the node class initializers, but Python 2.5 
    does not, so this is intended to be an equivalent.
    """
    node = cls()
    for name, value in zip(cls._fields, args):
        setattr(node, name, value)
    for name, value in kwargs:
        setattr(node, name, value)
    return node

def copy_node(node, *args, **kwargs):
    cls = node.__class__
    new_node = cls()
    return copy_node_into(node, new_node, *args, **kwargs)
        
def copy_node_into(node, new_node, *args, **kwargs):
    for name, value in node.__dict__.iteritems():
        setattr(new_node, name, value)            
    
    cls = node.__class__
    for name, value in zip(cls._fields, args):
        setattr(new_node, name, value)
        
    for name, value in kwargs.iteritems():
        setattr(new_node, name, value)
        
    return new_node

def deep_copy_node(node, *args, **kwargs):
    cls = node.__class__
    new_node = cls()
    return deep_copy_node_into(node, new_node, *args, **kwargs)

def deep_copy_node_into(node, new_node, *args, **kwargs):
    for name, value in node.__dict__.iteritems():
        if isinstance(value, _ast.AST):
            value = deep_copy_node(value)
        setattr(new_node, name, value)
        
    cls = node.__class__
    for name, value in zip(cls._fields, args):
        setattr(new_node, name, value)
        
    for name, value in kwargs.iteritems():
        setattr(new_node, name, value)
        
    return new_node

def infer_ast(src):
    """Attempts to infer an abstract syntax tree from the provided value.
    
    - Python ast.AST instances are passed through.
    - Strings are parsed. A SyntaxError is raised if invalid.
    - Functions are sent through cypy.fn_get_source to get a source
      string, then parsed. If the source can't be a found, an exception is 
      raised by fn_get_source.
      
    .. WARNING:: Functions defined on the iPython command line do not have 
                 their source saved. A bug has been filed: 
                 
                 http://github.com/ipython/ipython/issues/issue/120
    """
    if isinstance(src, _ast.AST):
        return src
    elif isinstance(src, basestring):
        return _ast.parse(src)
    else:
        # if a function instance is passed in, it's source is found
        # and parsed. note that finding source can be precarious for
        # functions defined on the command line. If you get an error
        # you'll have to use strings instead of regular function
        # definitions
        src = cypy.fn_get_source(src)
        return _ast.parse(src)

def extract_the(node, node_type):
    """Extracts the node of type node_type from the provided node.
    
    - If the node is itself of node_type, returns node.
    - If the node is a suite, it must contain exactly one node of the provided
      type in its body.
    
    """
    if isinstance(node, node_type):
        return node
    try:
        body = node.body
    except AttributeError:
        raise cypy.Error(
            "Expecting suite containing a single %s, or a %s, but got %s." %
            (node_type.__name__, node_type.__name__, type(node).__name__))
    
    if len(body) != 1 or not isinstance(body[0], node_type):
        raise cypy.Error(
            "The body must contain exactly one node of type %s." %
            node_type.__name__)
    return body[0]

def FunctionDef_co_varnames(fd):
    assert isinstance(fd, _ast.FunctionDef)
    return tuple(arg.id for arg in fd.args.args)

unary_operators = cypy.make_symmetric({
    _ast.Invert: '~',
    _ast.Not: 'not',
    _ast.UAdd: '+',
    _ast.USub: '-',
})

integer_binary_operators = cypy.make_symmetric({
    _ast.LShift: '<<',
    _ast.RShift: '>>',
    _ast.BitOr: '|',
    _ast.BitXor: '^',
    _ast.Mod: '%'
})

non_integer_binary_operators = cypy.make_symmetric({
    _ast.Add: '+',
    _ast.Sub: '-',
    _ast.Mult: '*',
    _ast.Div: '/',
    _ast.Pow: '**',    
    _ast.FloorDiv: '//'
})

binary_operators = cypy.merge_dicts(
    integer_binary_operators,
    non_integer_binary_operators
)

boolean_operators = cypy.make_symmetric({
    _ast.And: "and",
    _ast.Or: "or",
})

comparison_operators = cypy.make_symmetric({
    _ast.Eq: '==',
    _ast.NotEq: '!=',
    _ast.Lt: '<',
    _ast.LtE: '<=',
    _ast.Gt: '>',
    _ast.GtE: '>=',
    _ast.Is: 'is',
    _ast.IsNot: 'is not',
    _ast.In: 'in',
    _ast.NotIn: 'not in',
})

all_operators = cypy.merge_dicts(unary_operators, 
                                 binary_operators,
                                 boolean_operators, 
                                 comparison_operators)

C_unary_operators = dict(unary_operators)
C_unary_operators[_ast.Not] = "!"
C_unary_operators["!"] = _ast.Not

C_integer_binary_operators = dict(integer_binary_operators)
C_non_integer_binary_operators = dict(non_integer_binary_operators)
del C_non_integer_binary_operators[_ast.Pow]
del C_non_integer_binary_operators["**"]
del C_non_integer_binary_operators[_ast.FloorDiv]
del C_non_integer_binary_operators["//"]

C_binary_operators = cypy.merge_dicts(C_integer_binary_operators,
                                      C_non_integer_binary_operators)

C_boolean_operators = cypy.make_symmetric({
    _ast.And: "&&",
    _ast.Or: "||",
})

C_comparison_operators = cypy.make_symmetric({
    _ast.Eq: "==",
    _ast.NotEq: "!=",
    _ast.Lt: "<",
    _ast.LtE: "<=",
    _ast.Gt: ">",
    _ast.GtE: ">=",
})

C_all_operators = cypy.merge_dicts(C_unary_operators,
                                   C_binary_operators,
                                   C_boolean_operators,
                                   C_comparison_operators)
