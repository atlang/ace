"""Generates unit tests for the cl.oquence OpenCL backend."""
import ast as _ast

import cypy.cg as cg
import cypy.astx as astx
import clq.backends.opencl as ocl

# TODO: builtin functions
# TODO: extension inference
# TODO: kernel inference
# TODO: vector types
# TODO: image and event types
# TODO: local array initializers
# TODO: unique naming
# TODO: extern

g = cg.CG()
"""
'''Automatically generated unit tests for the cl.oquence OpenCL backend.

>>> DO NOT MODIFY DIRECTLY <<<
See generate_test_cl.py.
'''
import unittest
import ast as _ast

import clq
import clq.backends.opencl as ocl

OpenCL = ocl.Backend()

""" << g

ocl_int_type_names = ocl.int_types.keys()
ocl_float_type_names = ocl.float_types.keys()
ocl_scalar_type_names = ocl.scalar_types.keys()
ocl_base_type_names = ocl.base_types.keys()

"""
#===============================================================================
# Docstring
#===============================================================================
@clq.fn
def docstring_test():
    '''This is a docstring.'''

docstring_test_expected = '''
kernel void docstring_test() {
    /* This is a docstring. */
}

'''

class DocstringTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(docstring_test.compile(OpenCL).program_item.code,
                         docstring_test_expected)
        
""" << g

"""
#===============================================================================
# Return
#===============================================================================
@clq.fn
def identity(x):
    return x

def identity_expected(type):
    return '''
kernel %(type)s identity(%(type)s x) {
    return x;
}
''' % { 'type': type.name }

""" << g

for type in ocl_base_type_names:
    ("""
    class ReturnTest_%(type)s(unittest.TestCase):
        def runTest(self):
            ocl_type = ocl.%(type)s
            self.assertEqual(identity.compile(OpenCL, ocl_type).program_item.code,
                             identity_expected(type))
    
    """ % {'type': type}) << g
    
"""
#===============================================================================
# Globals
#===============================================================================
@clq.fn
def call_identity(x):
    return identity(x)
    
def call_identity_expected(type):
    return '''
kernel %(type)s call_identity(%(type)s x) {
    return identity(x);
}
''' % { 'type': type.name }

""" << g

for type in ocl_base_type_names:
    ("""
    class GlobalsTest_%(type)s(unittest.TestCase):
        def runTest(self):
            ocl_type = ocl.%(type)s
            concrete_fn = identity.compile(OpenCL, ocl_type)
            self.assertEqual(concrete_fn.program_item.code,
                             call_identity_expected(ocl_type))
            self.assertEqual(concrete_fn.program_items[0].code,
                             identity_expected(ocl_type))
            self.assertEqual(concrete_fn.program_items[1],
                             concrete_fn.program_item)
                             
    """ % {'type': type}) << g

"""
#===============================================================================
# Void
#===============================================================================
@clq.fn
def return_void():
    return
    
return_void_expected = '''
kernel void return_void() {
    return;
}
'''

class VoidTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(return_void.compile(OpenCL).program_item.code,
                         return_void_expected)
        
@clq.fn
def return_return_void():
    return return_void()
     
class VoidReturnTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.TypeResolutionError, 
            return_return_void.compile, OpenCL)

""" << g

"""
#===============================================================================
# Assign
#===============================================================================
@clq.fn
def identity_assign(x):
    y = x
    return y

def identity_assign_expected(type):
    return '''
kernel %(type)s identity_assign(%(type)s x) {
    %(type)s y;
    y = x;
    return y;
}
''' % {'type': type.name}

""" << g

for type in ocl_base_type_names:
    ("""
    class AssignTest_%(type)s(unittest.TestCase):
        def runTest(self):
            ocl_type = ocl.%(type)s
            print identity_assign.compile(OpenCL, ocl_type).program_item.code
            
    """ % {'type': type}) << g

"""
@clq.fn
def assign_void():
    y = return_void()
    return y
    
class VoidAssignTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.TypeResolutionError,
            assign_void.compile, OpenCL)

""" << g

"""
#===============================================================================
# Reserved Names
#===============================================================================
@clq.fn
def assign_type():
    int = 5
    
@clq.fn
def double():
    return
    
@clq.fn
def assign_address_space():
    __global = 5
    private = 5
    return private
    
@clq.fn
def __global():
    return
    
@clq.fn
def assign_function_qualifier():
    __kernel = 5
    kernel = 5
    return kernel
    
@clq.fn
def kernel():
    return
    
@clq.fn
def assign_access_qualifier():
    __read_only = 5
    read_only = 5
    return read_only
    
@clq.fn
def read_write():
    return
    
@clq.fn
def assign_other():
    __attribute__ = 5
    
@clq.fn
def __attribute__():
    return
    
@clq.fn
def assign_vector_type():
    int4 = 5
    return int4
    
@clq.fn
def double4():
    return
    
@clq.fn
def assign_other_type():
    event_t = 5
    return event_t
    
@clq.fn
def event_t():
    return
    
""" << g 

for func in ('assign_type', 'double', 
             'assign_address_space', '__global', 
             'assign_function_qualifier', 'kernel', 
             'assign_access_qualifier', 'read_write',
             'assign_other', '__attribute__',
             'assign_vector_type', 'double4',
             'assign_other_type', 'event_t'):
    ("""
    class KeywordTest_%(func)s(unittest.TestCase):
        def runTest(self):
            self.assertRaises(clq.InvalidOperationError, %(func)s.compile, OpenCL)
            
    """ % {'func': func}) << g 

"""
#===============================================================================
# Literals
#===============================================================================
@clq.fn
def int_literal():
    return 0

int_literal_expected = '''
int int_literal() {
    return 0;
}
'''

class IntLiteralTest(unittest.TestCase):    
    def runTest(self):
        self.assertEqual(int_literal.compile(OpenCL).program_item.code,
                          int_literal_expected)
        
@clq.fn
def float_literal():
    return 0.0
    
float_literal_expected = '''
float float_literal() {
    return 0.0f;
}
'''
 
class FloatLiteralTest(unittest.TestCase):    
    def runTest(self):
        self.assertEqual(float_literal.compile(OpenCL).program_item.code,
                         float_literal_expected)
        
@clq.fn
def str_literal():
    return "Test"
    
str_literal_expected = '''
char* str_literal() {
    return "Test";
}
'''

class StrLiteralTest(unittest.TestCase):
    def runTest(self):    
        self.assertEqual(str_literal.compile(OpenCL).program_item.code,
                         str_literal_expected)

@clq.fn
def true_literal():
    return True
    
true_literal_expected = '''
bool true_literal() {
    return true;
}
'''

class TrueLiteralTest(unittest.TestCase):    
    def runTest(self):
        self.assertEqual(true_literal.compile(OpenCL).program_item.code,
                         true_literal_expected)
    
@clq.fn
def false_literal():
    return False
    
bool_literal_expected = '''
bool false_literal() {
    return false;
}
'''

class FalseLiteralTest(unittest.TestCase):    
    def runTest(self):
        self.assertEqual(false_literal.compile(OpenCL).program_item.code,
                         false_literal_expected)
                         
@clq.fn
def none_literal():
    return None
    
class NoneLiteralTest(unittest.TestCase):    
    def runTest(self):
        self.assertRaises(TypeResolutionError,
                          true_literal.compile, OpenCL)
                                 
""" << g

"""
#===============================================================================
# Constants
#===============================================================================
_k = 0
@clq.fn
def constant_test():
    return _k
    
constant_test_expected = '''
int constant_test() {
    return 0;
}
'''

class ConstantTest(unittest.TestCase):    
    def runTest(self):
        self.assertEqual(constant_test.compile(OpenCL).program_item.code,
                         constant_test_expected)
    
class A(object):
    k = 0.0
a = A()

@clq.fn
def constant_attr_test():
    return a.k
    
constant_attr_test_expected = '''
float constant_attr_test() {
    return 0.0f;
}
'''
    
class ConstantAttrTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(constant_attr_test.compile(OpenCL).program_item.code,
                         constant_attr_test_expected)
        
b = { 'k': 'test' }
@clq.fn
def constant_subscript_test():
    return b['k']
    
constant_subscript_test_expected = '''
char* constant_subscript_test() {
    return "test";
}
'''
   
class ConstantSubscriptTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(constant_subscript_test.compile(OpenCL).program_item.code,
                         constant_subscript_test_expected)
        
def f_k():
    return True
    
@clq.fn
def constant_function_test():
    return f_k()
    
constant_function_test_expected = '''
bool constant_function_test() {
    return true;
}
'''
 
class ConstantFunctionTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(constant_function_test.compile(OpenCL).program_item.code,
                         constant_subscript_test_expected)
        
@clq.fn
def constant_expr_test():
    return a.k + _k;
    
constant_expr_test_expected = '''
float constant_expr_test():
    return 0.0;
}
'''
    
class ConstantExprTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(constant_expr_test.compile(OpenCL).program_item.code,
                         constant_expr_test_expected)
        
""" << g

#"""
##===============================================================================
## Defaults
##===============================================================================
#@clq.fn
#def default_constant_test(k=0):
#    return k
#    
#default_constant_test.expected = '''
#int default_constant_test() {
#    
#    
#class DefaultConstantTest(unittest.TestCase):
#    def runTest(self):
#        print default_constant_test.compile(OpenCL).program_item.code
#        
#@clq.fn
#def default_value_test(k=_k):
#    return k
#    
#class DefaultValueTest(unittest.TestCase):
#    def runTest(self):
#        print default_value_test.compile(OpenCL).program_item.code
#    
#a = { 'k': 0 }    
#@clq.fn
#def default_expr_test(k=a['k']):
#    return k
#    
#class DefaultExprTest(unittest.TestCase):
#    def runTest(self):
#        print default_expr_test.compile(OpenCL).program_item.code
#
#@clq.fn
#def nested_default_test():
#    return default_expr_test()
#    
#class NestedDefaultTest(unittest.TestCase):
#    def runTest(self):
#        print nested_default_test.compile(OpenCL).program_item.code
#        
#class NestedDefaultConcreteTest(unittest.TestCase):
#    def runTest(self):
#        default_expr_test_concrete = default_expr_test.compile(OpenCL)
#        @clq.fn
#        def nested_default_concrete_test():
#            return default_expr_test_concrete()
#            
#        print nested_default_concrete_test.compile(OpenCL).program_item.code
#        
#""" << g 

"""
#===============================================================================
# Higher Order Functions
#===============================================================================
@clq.fn
def higher_order(fn, x):
    return fn(x)

def higher_order_expected(type):
    return '''
%(type)s higher_order(%(type)s x) {
    return identity(x);
}''' % { 'type': type.name }

""" << g

for type in ocl_base_type_names:
    ("""
    class GenericHigherOrderFunctionTest_%(type)s(unittest.TestCase):
        def runTest(self):
            ocl_type = ocl.%(type)s
            hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
            self.assertEqual(hi_id.program_item.code, higher_order_expected(ocl_type))
            self.assertEqual(hi_id.program_items[0].code, identity_expected(ocl_type))
    
    class ConcreteHigherOrderFunctionTest_%(type)s(unittest.TestCase):
        def runTest(self):
            ocl_type = ocl.%(type)s
            id = identity.compile(OpenCL, ocl_type)
            hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
            self.assertEqual(hi_id.program_item.code, higher_order_expected(ocl_type))
            self.assertEqual(hi_id.program_items[0].code, identity_expected(ocl_type))

    """ % {'type': type}) << g
    
"""
#===============================================================================
# Casts
#===============================================================================
def cast_test_expected(type):
    return '''
%(type)s cast_test() {
    return (%(type)s)0;
}
''' % {'type': type.name}

""" << g

for type in ocl_scalar_type_names:
    ("""
    class CastTest_%(type)s(unittest.TestCase):
        def runTest(self):
            ocl_type = ocl.%(type)s
            @clq.fn
            def cast_test():
                return ocl_type(0)
            self.assertEqual(cast_test.compile(OpenCL).program_item.code,
                             cast_test_expected(ocl_type))
    
    """ % {'type': type}) << g

"""
#===============================================================================
# Higher-Order Types
#===============================================================================
@clq.fn
def hot_test(type):
    return type(0)
    
def hot_test_expected(type):
    return '''
%(type)s hot_test() {
    return (%(type)s)0;
}
''' % { 'type': type.name }

""" << g

for type in ocl_scalar_type_names:
    ("""
    class HOTTest_%(type)s(unittest.TestCase):
        def runTest(self):
            ocl_type = ocl.%(type)s
            self.assertEqual(hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code,
                             hot_test_expected(ocl_type))
            
    """ % {'type': type}) << g
    
"""
#===============================================================================
# For
#===============================================================================
@clq.fn
def for_test():
    for i in 0, 10, 1:
        a = i
        break

    for j in 0, 10:
        b = j
        continue

for_test_expected = '''
kernel void for_test() {
    int i;
    int a;
    int j;
    int b;
    
    for (i = 0; i < 10; i += 1) {
        a = i;
        break;
    }
    for (j = 0; j < 10; j += 1) {
        b = j;
        break;
    }
}
'''

class ForTest(unittest.TestCase):
    def runTest(self):          
        self.assertEqual(for_test.compile(OpenCL).program_item.code,
                         for_test_expected)

""" << g

"""
#===============================================================================
# Exec
#===============================================================================
@clq.fn
def exec_test():
    i = 0
    exec "// This is a test."
    return i
    
exec_test_expected = '''
int exec_test() {
    int i;
    
    i = 0;
    // This is a test.
    return i;
}
'''

class ExecTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(exec_test.compile(OpenCL).program_item.code,
                         exec_test_expected)

""" << g

"""
#===============================================================================
# Pass
#===============================================================================
@clq.fn
def pass_test():
    i = 0
    pass
    return i
    
pass_test_expected = '''
int pass_test() {
    int i;
    
    i = 0;
    ;
    return i;
}
'''
    
class PassTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(pass_test.compile(OpenCL).program_item.code,
                         pass_test_expected)

""" << g    

#===============================================================================
# Binary Operators
#===============================================================================
op_pairs = {
    ('uchar', 'uchar'): 'uint',
    ('uchar', 'char'): 'uint',
    ('uchar', 'ushort'): 'uint',
    ('uchar', 'short'): 'uint',
    ('uchar', 'uint'): 'uint',
    ('uchar', 'int'): 'uint',
    ('uchar', 'ulong'): 'uint',
    ('uchar', 'long'): 'ulong',
    ('uchar', 'half'): 'float',
    ('uchar', 'float'): 'float',
    ('uchar', 'double'): 'double',
    ('uchar', 'uintptr_t'): 'uintptr_t',
    ('uchar', 'intptr_t'): 'uintptr_t',
    ('uchar', 'size_t'): 'size_t',
    ('uchar', 'ptrdiff_t'): 'size_t',
    
    ('char', 'uchar'): 'uint',
    ('char', 'char'): 'int',
    ('char', 'ushort'): 'uint',
    ('char', 'short'): 'int',
    ('char', 'uint'): 'uint',
    ('char', 'int'): 'int',
    ('char', 'ulong'): 'ulong',
    ('char', 'long'): 'long',
    ('char', 'half'): 'float',
    ('char', 'float'): 'float',
    ('char', 'double'): 'double',
    ('char', 'uintptr_t'): 'uintptr_t',
    ('char', 'intptr_t'): 'intptr_t',
    ('char', 'size_t'): 'size_t',
    ('char', 'ptrdiff_t'): 'ptrdiff_t',
    
    ('ushort', 'uchar'): 'uint',
    ('ushort', 'char'): 'uint',
    ('ushort', 'ushort'): 'uint',
    ('ushort', 'short'): 'uint',
    ('ushort', 'uint'): 'uint',
    ('ushort', 'int'): 'uint',
    ('ushort', 'ulong'): 'uint',
    ('ushort', 'long'): 'ulong',
    ('ushort', 'half'): 'float',
    ('ushort', 'float'): 'float',
    ('ushort', 'double'): 'double',
    ('ushort', 'uintptr_t'): 'uintptr_t',
    ('ushort', 'intptr_t'): 'uintptr_t',
    ('ushort', 'size_t'): 'size_t',
    ('ushort', 'ptrdiff_t'): 'size_t',
    
    ('short', 'uchar'): 'uint',
    ('short', 'char'): 'int',
    ('short', 'ushort'): 'uint',
    ('short', 'short'): 'int',
    ('short', 'uint'): 'uint',
    ('short', 'int'): 'int',
    ('short', 'ulong'): 'ulong',
    ('short', 'long'): 'long',
    ('short', 'half'): 'float',
    ('short', 'float'): 'float',
    ('short', 'double'): 'double',
    ('short', 'uintptr_t'): 'uintptr_t',
    ('short', 'intptr_t'): 'intptr_t',
    ('short', 'size_t'): 'size_t',
    ('short', 'ptrdiff_t'): 'ptrdiff_t',
    
    ('uint', 'uchar'): 'uint',
    ('uint', 'char'): 'uint',
    ('uint', 'ushort'): 'uint',
    ('uint', 'short'): 'uint',
    ('uint', 'uint'): 'uint',
    ('uint', 'int'): 'uint',
    ('uint', 'ulong'): 'ulong',
    ('uint', 'long'): 'ulong',
    ('uint', 'half'): 'float',
    ('uint', 'float'): 'float',
    ('uint', 'double'): 'double',
    ('uint', 'uintptr_t'): 'uintptr_t',
    ('uint', 'intptr_t'): 'uintptr_t',
    ('uint', 'size_t'): 'size_t',
    ('uint', 'ptrdiff_t'): 'size_t',
    
    ('int', 'uchar'): 'uint',
    ('int', 'char'): 'int',
    ('int', 'ushort'): 'uint',
    ('int', 'short'): 'int',
    ('int', 'uint'): 'uint',
    ('int', 'int'): 'int',
    ('int', 'ulong'): 'ulong',
    ('int', 'long'): 'long',
    ('int', 'half'): 'float',
    ('int', 'float'): 'float',
    ('int', 'double'): 'double',
    ('int', 'uintptr_t'): 'uintptr_t',
    ('int', 'intptr_t'): 'intptr_t',
    ('int', 'size_t'): 'size_t',
    ('int', 'ptrdiff_t'): 'ptrdiff_t',
    
    ('ulong', 'uchar'): 'ulong',
    ('ulong', 'char'): 'ulong',
    ('ulong', 'ushort'): 'ulong',
    ('ulong', 'short'): 'ulong',
    ('ulong', 'uint'): 'ulong',
    ('ulong', 'int'): 'ulong',
    ('ulong', 'ulong'): 'ulong',
    ('ulong', 'long'): 'ulong',
    ('ulong', 'half'): None,
    ('ulong', 'float'): 'float',
    ('ulong', 'double'): 'double',
    ('ulong', 'uintptr_t'): 'ulong',
    ('ulong', 'intptr_t'): 'ulong',
    ('ulong', 'size_t'): 'ulong',
    ('ulong', 'ptrdiff_t'): 'ulong',
    
    ('long', 'uchar'): 'ulong',
    ('long', 'char'): 'long',
    ('long', 'ushort'): 'ulong',
    ('long', 'short'): 'long',
    ('long', 'uint'): 'ulong',
    ('long', 'int'): 'long',
    ('long', 'ulong'): 'ulong',
    ('long', 'long'): 'long',
    ('long', 'half'): None,
    ('long', 'float'): 'float',
    ('long', 'double'): 'double',
    ('long', 'uintptr_t'): 'ulong',
    ('long', 'intptr_t'): 'long',
    ('long', 'size_t'): 'ulong',
    ('long', 'ptrdiff_t'): 'long',
    
    ('half', 'uchar'): 'float',
    ('half', 'char'): 'float',
    ('half', 'ushort'): 'float',
    ('half', 'short'): 'float',
    ('half', 'uint'): 'float',
    ('half', 'int'): 'float',
    ('half', 'ulong'): None,
    ('half', 'long'): None,
    ('half', 'half'): 'float',
    ('half', 'float'): 'float',
    ('half', 'double'): 'double',
    ('half', 'uintptr_t'): None,
    ('half', 'intptr_t'): None,
    ('half', 'size_t'): None,
    ('half', 'ptrdiff_t'): None,
    
    ('float', 'uchar'): 'float',
    ('float', 'char'): 'float',
    ('float', 'ushort'): 'float',
    ('float', 'short'): 'float',
    ('float', 'uint'): 'float',
    ('float', 'int'): 'float',
    ('float', 'ulong'): 'float',
    ('float', 'long'): 'float',
    ('float', 'half'): 'float',
    ('float', 'float'): 'float',
    ('float', 'double'): 'double',
    ('float', 'uintptr_t'): 'float',
    ('float', 'intptr_t'): 'float',
    ('float', 'size_t'): 'float',
    ('float', 'ptrdiff_t'): 'float',
        
    ('double', 'uchar'): 'double',
    ('double', 'char'): 'double',
    ('double', 'ushort'): 'double',
    ('double', 'short'): 'double',
    ('double', 'uint'): 'double',
    ('double', 'int'): 'double',
    ('double', 'ulong'): 'double',
    ('double', 'long'): 'double',
    ('double', 'half'): 'double',
    ('double', 'float'): 'double',
    ('double', 'double'): 'double',
    ('double', 'uintptr_t'): 'double',
    ('double', 'intptr_t'): 'double',
    ('double', 'size_t'): 'double',
    ('double', 'ptrdiff_t'): 'double',
    
    ('uintptr_t', 'uchar'): 'uintptr_t',
    ('uintptr_t', 'char'): 'uintptr_t',
    ('uintptr_t', 'ushort'): 'uintptr_t',
    ('uintptr_t', 'short'): 'uintptr_t',
    ('uintptr_t', 'uint'): 'uintptr_t',
    ('uintptr_t', 'int'): 'uintptr_t',
    ('uintptr_t', 'ulong'): 'ulong',
    ('uintptr_t', 'long'): 'ulong',
    ('uintptr_t', 'half'): None,
    ('uintptr_t', 'float'): 'float',
    ('uintptr_t', 'double'): 'double',
    ('uintptr_t', 'uintptr_t'): 'uintptr_t',
    ('uintptr_t', 'intptr_t'): 'uintptr_t',
    ('uintptr_t', 'size_t'): 'uintptr_t',   
    ('uintptr_t', 'ptrdiff_t'): 'uintptr_t',
    
    ('intptr_t', 'uchar'): 'uintptr_t',
    ('intptr_t', 'char'): 'intptr_t',
    ('intptr_t', 'ushort'): 'uintptr_t',
    ('intptr_t', 'short'): 'intptr_t',
    ('intptr_t', 'uint'): 'uintptr_t',
    ('intptr_t', 'int'): 'intptr_t',
    ('intptr_t', 'ulong'): 'ulong',
    ('intptr_t', 'long'): 'long',
    ('intptr_t', 'half'): None,
    ('intptr_t', 'float'): 'float',
    ('intptr_t', 'double'): 'double',
    ('intptr_t', 'uintptr_t'): 'uintptr_t',
    ('intptr_t', 'intptr_t'): 'intptr_t',
    ('intptr_t', 'size_t'): 'uintptr_t',
    ('intptr_t', 'ptrdiff_t'): 'intptr_t',
    
    ('size_t', 'uchar'): 'size_t',
    ('size_t', 'char'): 'size_t',
    ('size_t', 'ushort'): 'size_t',
    ('size_t', 'short'): 'size_t',
    ('size_t', 'uint'): 'size_t',
    ('size_t', 'int'): 'size_t',
    ('size_t', 'ulong'): 'ulong',
    ('size_t', 'long'): 'ulong',
    ('size_t', 'half'): None,
    ('size_t', 'float'): 'float',
    ('size_t', 'double'): 'double',
    ('size_t', 'uintptr_t'): 'uintptr_t',
    ('size_t', 'intptr_t'): 'uintptr_t',
    ('size_t', 'size_t'): 'size_t',   
    ('size_t', 'ptrdiff_t'): 'size_t',
    
    ('ptrdiff_t', 'uchar'): 'size_t',
    ('ptrdiff_t', 'char'): 'ptrdiff_t',
    ('ptrdiff_t', 'ushort'): 'size_t',
    ('ptrdiff_t', 'short'): 'ptrdiff_t',
    ('ptrdiff_t', 'uint'): 'size_t',
    ('ptrdiff_t', 'int'): 'ptrdiff_t',
    ('ptrdiff_t', 'ulong'): 'ulong',
    ('ptrdiff_t', 'long'): 'long',
    ('ptrdiff_t', 'half'): None,
    ('ptrdiff_t', 'float'): 'float',
    ('ptrdiff_t', 'double'): 'double',
    ('ptrdiff_t', 'uintptr_t'): 'uintptr_t',
    ('ptrdiff_t', 'intptr_t'): 'intptr_t',
    ('ptrdiff_t', 'size_t'): 'size_t',   
    ('ptrdiff_t', 'ptrdiff_t'): 'ptrdiff_t',
}

def _generate_binary_header(ast_class):
    return """
    #===============================================================================
    # %(ast_class)s
    #===============================================================================
    @clq.fn
    def %(ast_lc)s_test(a, b):
        return a %(ast_op)s b
    
    def %(ast_lc)s_test_expected(left_type, right_type, return_type):
        return '''
\%(return_type)s %(ast_lc)s_test(\%(left_type)s a, \%(right_type)s b) {
    return a %(ast_op)s b;
}''' % { 'left_type': left_type, 
         'right_type': right_type, 
         'return_type': return_type }

    """ % {
        'ast_class': ast_class.__name__,
        'ast_lc': ast_class.__name__.lower(),
        'ast_op': astx.all_operators[ast_class]
    }

def _generate_binary_test(ast_class, left_type, right_type, return_type=None):
    return """
    class %(ast_class)sTest_%(left_type)s_%(right_type)s(unittest.TestCase):
        def runTest():
            left_type = ocl.%(left_type)s
            right_type = ocl.%(right_type)s
            concrete_fn = %(ast_lc)s_test.compile(OpenCL, left_type, right_type)
            self.assertEqual(concrete_fn.program_item.code,
                             %(ast_lc)s_test_expected(left_type.name, 
                                                      right_type.name, 
                                                      '%(return_type)s'))
            
    """ % {
       'left_type': left_type,
       'right_type': right_type,
       'return_type': return_type if return_type is not None \
                      else op_pairs[(left_type, right_type)],
       'ast_class': ast_class.__name__,
       'ast_lc': ast_class.__name__.lower()
    }
    
def _generate_binary_fail_test(ast_class, left_type, right_type):
    return """
    class %(ast_class)sTest_%(left_type)s_%(right_type)s(unittest.TestCase):
        def runTest():
            left_type = ocl.%(left_type)s
            right_type = ocl.%(right_type)s
            self.assertRaises(clq.TypeResolutionError, %(ast_lc)s_test.compile, 
                              OpenCL, left_type, right_type)
                              
    """ % {
        'left_type': left_type,
        'right_type': right_type,
        'ast_class': ast_class.__name__,
        'ast_lc': ast_class.__name__.lower()
    } 

integer_ops = astx.C_integer_binary_operators.keys()
for ast_class in astx.C_binary_operators.iterkeys():
    if not isinstance(ast_class, _ast.AST):
        # its symmetric so ignore the string keys
        continue
    
    _generate_binary_header(ast_class) << g
    
    # for every pair, generate the appropriate test
    for left_type in ocl_scalar_type_names:
        for right_type in ocl_scalar_type_names:
            # integer ops only valid if both operands are integers
            if ast_class in integer_ops and (
                (left_type in ocl_float_type_names) or 
                (right_type in ocl_float_type_names)):
                _generate_binary_fail_test(ast_class, left_type, right_type) << g
            else:
                _generate_binary_test(ast_class, left_type, right_type) << g
            
    # bool
    _generate_binary_fail_test(ast_class, 'bool', 'int') << g 
    _generate_binary_fail_test(ast_class, 'int', 'bool') << g 
    _generate_binary_fail_test(ast_class, 'bool', 'bool') << g 
            
for ast_class in astx.C_boolean_operators.keys():
    if not isinstance(ast_class, _ast.AST):
        continue
    
    _generate_binary_header(ast_class) << g
    
    _generate_binary_test(ast_class, "bool", "bool", "bool") << g
    _generate_binary_fail_test(ast_class, 'bool', 'int') << g
    _generate_binary_fail_test(ast_class, 'int', 'int') << g
    _generate_binary_fail_test(ast_class, 'int', 'bool') << g
        
for ast_class in astx.C_comparison_operators.keys():
    if not isinstance(ast_class, _ast.AST):
        continue
    
    _generate_binary_header(ast_class) << g
    for left_type in ocl_scalar_type_names:
        for right_type in ocl_scalar_type_names:
            _generate_binary_test(ast_class, left_type, right_type, "bool") << g 
            
    if ast_class == _ast.Eq or ast_class == _ast.NotEq:
        _generate_binary_test(ast_class, "bool", "int", "bool") << g
        _generate_binary_test(ast_class, "bool", "bool", "bool") << g 
        _generate_binary_test(ast_class, "int", "bool", "bool") << g 
    else:
        _generate_binary_fail_test(ast_class, 'bool', 'int') << g
        _generate_binary_fail_test(ast_class, 'bool', 'bool') << g
        _generate_binary_fail_test(ast_class, 'int', 'bool') << g
    
#===============================================================================
# Unary Operators
#===============================================================================
unary_op_pairs = {
    ('uchar', _ast.UAdd): 'uchar',
    ('uchar', _ast.USub): 'char',
    ('uchar', _ast.Invert): 'uchar',
    ('uchar', _ast.Not): None,
    
    ('char', _ast.UAdd): 'char',
    ('char', _ast.USub): 'char',
    ('char', _ast.Invert): 'char',
    ('char', _ast.Not): None,
    
    ('ushort', _ast.UAdd): 'ushort',
    ('ushort', _ast.USub): 'short',
    ('ushort', _ast.Invert): 'ushort',
    ('ushort', _ast.Not): None,
    
    ('short', _ast.UAdd): 'short',
    ('short', _ast.USub): 'short',
    ('short', _ast.Invert): 'short',
    ('short', _ast.Not): None,
    
    ('uint', _ast.UAdd): 'uint',
    ('uint', _ast.USub): 'int',
    ('uint', _ast.Invert): 'uint',
    ('uint', _ast.Not): None,
    
    ('int', _ast.UAdd): 'int',
    ('int', _ast.USub): 'int',
    ('int', _ast.Invert): 'int',
    ('int', _ast.Not): None,
    
    ('ulong', _ast.UAdd): 'ulong',
    ('ulong', _ast.USub): 'long',
    ('ulong', _ast.Invert): 'ulong',
    ('ulong', _ast.Not): None,
    
    ('long', _ast.UAdd): 'long',
    ('long', _ast.USub): 'long',
    ('long', _ast.Invert): 'long',
    ('long', _ast.Not): None,
    
    ('uintptr_t', _ast.UAdd): 'uintptr_t',
    ('uintptr_t', _ast.USub): 'intptr_t',
    ('uintptr_t', _ast.Invert): 'uintptr_t',
    ('uintptr_t', _ast.Not): None,
    
    ('intptr_t', _ast.UAdd): 'intptr_t',
    ('intptr_t', _ast.USub): 'intptr_t',
    ('intptr_t', _ast.Invert): 'intptr_t',
    ('intptr_t', _ast.Not): None,
    
    ('size_t', _ast.UAdd): 'size_t',
    ('size_t', _ast.USub): 'ptrdiff_t',
    ('size_t', _ast.Invert): 'size_t',
    ('size_t', _ast.Not): None,
    
    ('ptrdiff_t', _ast.UAdd): 'ptrdiff_t',
    ('ptrdiff_t', _ast.USub): 'ptrdiff_t',
    ('ptrdiff_t', _ast.Invert): 'ptrdiff_t',
    ('short', _ast.Not): None,
    
    ('half', _ast.UAdd): 'float',
    ('half', _ast.USub): 'float',
    ('half', _ast.Invert): None,
    ('half', _ast.Not): None,
    
    ('float', _ast.UAdd): 'float',
    ('float', _ast.USub): 'float',
    ('float', _ast.Invert): None,
    ('float', _ast.Not): None,
    
    ('double', _ast.UAdd): 'double',
    ('double', _ast.USub): 'double',
    ('double', _ast.Invert): None,
    ('double', _ast.Not): None,
    
    ('bool', _ast.UAdd): None,
    ('bool', _ast.USub): None,
    ('bool', _ast.Invert): None,
    ('bool', _ast.Not): 'bool'
}

def _generate_unary_header(ast_class):
    return """
    #===============================================================================
    # %(ast_class)s
    #===============================================================================
    @clq.fn
    def %(ast_lc)s_test(a):
        return %(ast_op) a
    
    def %(ast_lc)s_test_expected(operand_type, return_type):
        return '''
\%(return_type)s %(ast_lc)s_test(\%(operand_type)s a) {
    return (%(ast_op)a);
}
''' % { 'operand_type': operand_type, 'return_type': return_type }

    """ % {
        'ast_class': ast_class.__name__,
        'ast_lc': ast_class.__name__.lower(),
        'ast_op': astx.all_operators[ast_class]
    }
    
def _generate_unary_test(ast_class, type, return_type=None):
    return """
    class %(ast_class)sTest_%(type)s(unittest.TestCase):
        def runTest():
            type = ocl.%(type)s
            concrete_fn = %(ast_lc)s_test.compile(OpenCL, type)
            self.assertEqual(concrete_fn.program_item.code,
                             %(ast_lc)s_test_expected(type.name,
                                                      '%(return_type)s')
            
    """ % {
       'type': type,
       'return_type': return_type if return_type is not None \
                      else unary_op_pairs[(type, ast_class)],
       'ast_class': ast_class.__name__,
       'ast_lc': ast_class.__name__.lower()
    }
    
def _generate_unary_fail_test(ast_class, type):
    return """
    class %(ast_class)sTest_%(type)s(unittest.TestCase)s:
        def runTest():
            type = ocl.%(type)s
            concrete_fn = %(ast_lc)s_test.compile(OpenCL, type)
            self.assertRaises(clq.TypeResolutionError,
                              %(ast_lc)s_test.compile, OpenCL, type)

    """ % {
       'type': type,
       'ast_class': ast_class.__name__,
       'ast_lc': ast_class.__name__.lower()
    }
    
for ast_class in astx.C_unary_operators.keys():
    if not isinstance(ast_class, _ast.AST):
        continue
    
    _generate_unary_header(ast_class) << g
    
    for type in ocl_scalar_type_names:
        return_type = unary_op_pairs[(type, ast_class)]
        if return_type is None:
            _generate_unary_fail_test(ast_class, type) << g
        else:
            _generate_unary_test(ast_class, type, return_type) << g

"""
#===============================================================================
# Expr
#===============================================================================
@clq.fn
def expr_test():
    i = 0
    i + i
    return i
    
expr_test_expected = '''
int expr_test() {
    int i;
    
    i = 0;
    i + i;
    return i;
}
'''
    
class ExprTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(expr_test.compile(OpenCL).program_item.code,
                         expr_test_expected)

""" << g

"""
#===============================================================================
# While
#===============================================================================
@clq.fn
def while_test():
    i = 0
    while True:
        i = i + 1

class WhileTest(unittest.TestCase):
    def runTest(self):
        print while_test.compile(OpenCL).program_item.code
 
""" << g 

"""
#===============================================================================
# If
#===============================================================================
@clq.fn
def if_test():
    i = 0
    if True:
        return
    elif False:
        return
    elif i < 100:
        return
    elif i < 100 and i < 101:
        return
    else:
        return

class IfTest(unittest.TestCase):
    def runTest(self):
        print if_test.compile(OpenCL).program_item.code

""" << g

"""
#===============================================================================
# IfExp
#===============================================================================
@clq.fn
def ifexp_test():
    return 1 if True else 0.0
    
class IfExpTest(unittest.TestCase):
    def runTest(self):
        print ifexp_test.compile(OpenCL).program_item.code
        
""" << g

"""
#===============================================================================
# Subscript 
#===============================================================================
@clq.fn
def get_sub_test(x):
    return x[0]
    
@clq.fn
def set_sub_test(x):
    x[0] = x[0]
    
@clq.fn
def set_sub_test_with_cast(x):
    x[0] = 0
    
""" << g

ocl_address_spaces = ("ptr_global", "ptr_local", "ptr_private", "ptr_constant")

for type in ocl_base_type_names:
    for address_space in ocl_address_spaces:
        ("""
        class AddressSpaceTest_%(type)s_%(address_space)s(unittest.TestCase):
            def runTest(self):
                self.assertTrue(isinstance(ocl.%(type)s.%(address_space)s,
                                ocl.PtrType))
        
        class GetSubTest_%(type)s_%(address_space)s(unittest.TestCase):
            def runTest(self):
                ocl_type = ocl.%(type)s.%(address_space)s
                print get_sub_test.compile(OpenCL, ocl_type).program_item.code
                
        class SetSubTest_%(type)s_%(address_space)s(unittest.TestCase):
            def runTest(self):
                ocl_type = ocl.%(type)s.%(address_space)s
                print set_sub_test.compile(OpenCL, ocl_type).program_item.code
        
        """ % {
            'type': type,
            'address_space': address_space
        }) << g
        
        if type in ocl_scalar_type_names:
            ("""
            class SetSubTestWithCast_%(type)s_%(address_space)s(unittest.TestCase):
                def runTest(self):
                    ocl_type = ocl.%(type)s.%(address_space)s
                    print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
                
            """ % {
                'type': type,
                'address_space': address_space
            }) << g


"""
#===============================================================================
# loc and val
#===============================================================================
loc = ocl.loc
@clq.fn
def loc_test(x):
    return loc(x)
    
@clq.fn
def val_test(x):
    y = loc(x)
    return y.val
    
""" << g

for type in ocl_base_type_names:
    for address_space in ocl_address_spaces:
        ("""
        class LocTest_%(type)s_%(address_space)s(unittest.TestCase): 
            def runTest(self):
                ocl_type = ocl.%(type)s
                print loc_test.compile(OpenCL, ocl_type).program_item.code
                
        class ValTest_%(type)s_%(address_space)s(unittest.TestCase):
            def runTest(self):
                ocl_type = ocl.%(type)s
                print val_test.compile(OpenCL, ocl_type).program_item.code
        
        """ % {
            'type': type,
            'address_space': address_space
        }) << g
        
# TODO: pointer arithmetic

"""
#===============================================================================
# Invalid Operations
#===============================================================================
""" << g 
invalid_operations = {
    'NestedFunction': 
        '''
        def nested():
            return
        ''',
    
    'NestedClass':
        '''
        class nested():
            pass
        ''',
    'Delete': 
        '''
        del x
        ''',
    'Print':
        '''
        print x
        ''',
    'For_orelse':
        '''
        for i in (0, 10, 1):
            pass
        else:
            pass
        ''',
    'While_orelse':
        '''
        while x:
            pass
        else:
            pass
        ''',
    'With':
        '''
        with x:
            pass
        ''',
    'Raise':
        '''
        raise x
        ''',
    'TryExcept':
        '''
        try:
            pass
        except:
            pass
        else:
            pass
        ''',
    'TryFinally':
        '''
        try:
            pass
        except:
            pass
        else:
            pass
        finally:
            pass
        ''',
    'Assert':
        '''
        assert x
        ''',
    'Assert_msg':
        '''
        assert x, 'msg'
        ''',
    'Import':
        '''
        import clq
        ''',
    'ImportFrom':
        '''
        from clq import fn
        ''',
    'Global':
        '''
        global _k
        ''',
    'Lambda':
        '''
        lambda x: x
        ''',
    'Dict':
        '''
        { 'a': 'A' }
        ''',
    'Tuple':
        '''
        (1, 2)
        ''',
    'List':
        '''
        [1, 2]
        ''',
    'GeneratorExp':
        '''
        (i for i in (0, 1, 2))
        ''',
    'Yield':
        '''
        yield x
        ''',
    'Compare_multi':
        '''
        0 < x < 1
        ''',
    'Call_keywords':
        '''
        identity(x=0)
        ''',
    'Call_starargs':
        '''
        identity(*x)
        ''',
    'Call_kwargs':
        '''
        identity(**x)
        ''',
    'Slice_Ellipsis':
        '''
        x[...]
        ''',
    'Slice':
        '''
        x[1:2]
        ''',
    'Slice_multi':
        '''
        x[1:2:3]
        ''',
    'Is':
        '''
        x is 0
        ''',
    'IsNot':
        '''
        x is not 0
        ''',
    'In':
        '''
        0 in x
        ''',
    'NotIn':
        '''
        0 not in x
        ''',
    'Pow':
        '''
        x ** 2
        ''',
    'FloorDiv':
        '''
        x // 2
        '''
}

for op, code in invalid_operations.iteritems():
    ("""
    @clq.fn
    def %(op_lc)s_test(x):%(code)s
    class %(op)sTest(unittest.TestCase):
        def runTest(self):
            self.assertRaises(clq.InvalidOperationError,
                              %(op_lc)s_test.compile, OpenCL, ocl.int)
     
     """ % {
        'op_lc': op.lower(),
        'op': op,
        'code': code
    }) << g
      
"""
#===============================================================================
# t(test)
#===============================================================================
""" << g 

for type in ocl_base_type_names:
    ("""
    class TypeFnTest_%(type)s(unittest.TestCase):
        def runTest(self):
            self.assertEqual(ocl.t("%(type)s"), ocl.%(type)s)
            self.assertEqual(ocl.t("__global %(type)s*"), 
                             ocl.%(type)s.ptr_global)
            self.assertEqual(ocl.t("__global %(type)s**"), 
                             ocl.%(type)s.ptr_global.ptr)
            self.assertEqual(ocl.t("global  %(type)s *   "), 
                             ocl.%(type)s.ptr_global)
            self.assertEqual(ocl.t("__local  %(type)s *"), 
                             ocl.%(type)s.ptr_local)
            self.assertEqual(ocl.t("__local  %(type)s **"), 
                             ocl.%(type)s.ptr_local.ptr)
            self.assertEqual(ocl.t("local  %(type)s *"), 
                             ocl.%(type)s.ptr_local)
            self.assertEqual(ocl.t("__private  %(type)s*"), 
                                     ocl.%(type)s.ptr_private)
            self.assertEqual(ocl.t("__private  %(type)s**"), 
                                     ocl.%(type)s.ptr_private.ptr)
            self.assertEqual(ocl.t("private %(type)s*"), 
                                     ocl.%(type)s.ptr_private)
            self.assertEqual(ocl.%(type)s.ptr_private, ocl.%(type)s.ptr)
            self.assertEqual(ocl.t("__constant %(type)s*"), 
                             ocl.%(type)s.ptr_constant)
            self.assertEqual(ocl.t("__private  %(type)s**"), 
                                     ocl.%(type)s.ptr_private.ptr)
            self.assertEqual(ocl.t("constant %(type)s*"), 
                                    ocl.%(type)s.ptr_constant)
        
    """ % {'type': type}) << g
    
"""
#===============================================================================
# GenericFn API
#===============================================================================
class FromSourceTest(unittest.TestCase):
    def runTest(self):
        identity_src = clq.fn.from_source('''
            def identity(x):
                return x
        ''')
        print identity_src.compile(OpenCL, ocl.int).program_item.code
    
class FromASTTest(unittest.TestCase):
    def runTest(self):
        identity_ast = clq.fn.from_ast(_ast.parse('''
            def identity(x):
                return x
        '''))
        print identity_ast.compile(OpenCL, ocl.int).program_item.code
        
class GenericOriginalASTTest(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(identity.original_ast, _ast.AST))
        
class GenericAnnotatedASTTest(unittest.TestCase):
    def runTest(self):
        annotated_ast = identity.annotated_ast
        self.assertTrue(isinstance(annotated_ast, _ast.AST))
        
class GenericArgNamesTest(unittest.TestCase):
    def runTest(self):
        arg_names = identity.arg_names
        self.assertEqual(arg_names, ('x',))

class GenericLocalVariablesTest(unittest.TestCase):
    def runTest(self):
        local_variables = identity_assign.local_variables
        self.assertEqual(local_variables, ('y',))
        
class GenericNameTest(unittest.TestCase):
    def runTest(self):
        name = identity.name
        self.assertEqual(name, 'identity')
        
class CompileNoBackendTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.Error, identity.compile, ocl.int)
        
class CompileMissingTypeTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.Error, identity.compile, OpenCL)
        
class CompileTooManyTypesTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.Error, identity.compile, OpenCL, ocl.int, ocl.int)

class CompileNotTypeTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.Error, identity.compile, OpenCL, "int")

""" << g 

"""
#===============================================================================
# ConcreteFn API
#===============================================================================
class ConcreteFnTest(unittest.TestCase):
    def setUp(self):
        self.concrete_fn = identity_assign.compile(OpenCL, ocl.int)
        
class ConcreteFnGenericFnTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(self.concrete_fn.generic_fn, identity_assign)
        
class ConcreteFnBackendTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual(self.concrete_fn.backend, OpenCL)
        
class ConcreteOriginalASTTest(ConcreteFnTest):
    def runTest(self):
        self.assertTrue(isinstance(self.concrete_fn.original_ast, _ast.AST))
        
class ConcreteAnnotatedASTTest(ConcreteFnTest):
    def runTest(self):
        annotated_ast = self.concrete_fn.annotated_ast
        self.assertTrue(isinstance(annotated_ast, _ast.AST))
        
class ConcreteTypedASTTest(ConcreteFnTest):
    def runTest(self):
        typed_ast = self.concrete_fn.typed_ast
        self.assertTrue(isinstance(typed_ast, _ast.AST))
        
class ConcreteArgNamesTest(ConcreteFnTest):
    def runTest(self):
        arg_names = self.concrete_fn.arg_names
        self.assertEqual(arg_names, ('x',))

class ConcreteArgTypesTest(ConcreteFnTest):
    def runTest(self):
        arg_types = self.concrete_fn.arg_types
        self.assertEqual(arg_types, (ocl.int,))

class ConcreteLocalVariablesTest(ConcreteFnTest):
    def runTest(self):
        local_variables = self.concrete_fn.local_variables
        self.assertEqual(local_variables, ('y',))
        
""" << g 

# Done!
test_cl = g.code

if __name__ == "__main__":
    f = open('test_cl.py', 'w')
    f.write(test_cl)
    f.close()
    
    print test_cl
    