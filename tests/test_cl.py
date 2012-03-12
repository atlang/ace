'''Automatically generated unit tests for the cl.oquence OpenCL backend.

>>> DO NOT MODIFY DIRECTLY <<<
See generate_test_cl.py.
'''
import unittest
import ast as _ast

import clq
import clq.backends.opencl as ocl

OpenCL = ocl.Backend()

#===============================================================================
# Docstring
#===============================================================================
@clq.fn
def docstring_test():
    '''This is a docstring.'''

class DocstringTest(unittest.TestCase):
    def runTest(self):
        print docstring_test.compile(OpenCL).program_item.code
        
#===============================================================================
# Return
#===============================================================================
@clq.fn
def identity(x):
    return x

class ReturnTest_intptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_short(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_ulong(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_uchar(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_double(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_ushort(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_uintptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_long(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_ptrdiff_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_char(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_int(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_float(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_uint(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_half(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        print identity.compile(OpenCL, ocl_type).program_item.code

class ReturnTest_size_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        print identity.compile(OpenCL, ocl_type).program_item.code

#===============================================================================
# Globals
#===============================================================================
@clq.fn
def call_identity(x):
    return identity(x)
    
class GlobalsTest_intptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_short(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_ulong(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_uchar(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_double(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_ushort(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_uintptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_long(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_ptrdiff_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_char(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_int(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_float(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_uint(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_half(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        print identity.compile(OpenCL, ocl_type).program_item.code
        
class GlobalsTest_size_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        print identity.compile(OpenCL, ocl_type).program_item.code
        
#===============================================================================
# Void
#===============================================================================
@clq.fn
def return_void():
    return

class VoidTest(unittest.TestCase):
    def runTest(self):
        print return_void.compile(OpenCL).program_item.code
        
@clq.fn
def return_return_void():
    return return_void()
     
class VoidReturnTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.TypeResolutionError, 
            return_return_void.compile, OpenCL)

#===============================================================================
# Assign
#===============================================================================
@clq.fn
def identity_assign(x):
    y = x
    return y

class AssignTest_intptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_short(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_ulong(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_uchar(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_double(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_ushort(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_uintptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_long(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_ptrdiff_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_char(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_int(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_float(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_uint(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_half(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
class AssignTest_size_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        print identity_assign.compile(OpenCL, ocl_type).program_item.code
        
@clq.fn
def assign_void():
    y = return_void()
    return y
    
class VoidAssignTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.TypeResolutionError,
            assign_void.compile, OpenCL)

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
    
class KeywordTest_assign_type(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, assign_type.compile, OpenCL)
        
class KeywordTest_double(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, double.compile, OpenCL)
        
class KeywordTest_assign_address_space(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, assign_address_space.compile, OpenCL)
        
class KeywordTest___global(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, __global.compile, OpenCL)
        
class KeywordTest_assign_function_qualifier(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, assign_function_qualifier.compile, OpenCL)
        
class KeywordTest_kernel(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, kernel.compile, OpenCL)
        
class KeywordTest_assign_access_qualifier(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, assign_access_qualifier.compile, OpenCL)
        
class KeywordTest_read_write(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, read_write.compile, OpenCL)
        
class KeywordTest_assign_other(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, assign_other.compile, OpenCL)
        
class KeywordTest___attribute__(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, __attribute__.compile, OpenCL)
        
class KeywordTest_assign_vector_type(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, assign_vector_type.compile, OpenCL)
        
class KeywordTest_double4(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, double4.compile, OpenCL)
        
class KeywordTest_assign_other_type(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, assign_other_type.compile, OpenCL)
        
class KeywordTest_event_t(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError, event_t.compile, OpenCL)
        
#===============================================================================
# Literals
#===============================================================================
@clq.fn
def int_literal():
    return 0

class IntLiteralTest(unittest.TestCase):    
    def runTest(self):
        print int_literal.compile(OpenCL).program_item.code
        
@clq.fn
def float_literal():
    return 0.0
    
class FloatLiteralTest(unittest.TestCase):    
    def runTest(self):
        print float_literal.compile(OpenCL).program_item.code
        
@clq.fn
def str_literal():
    return "Test"
    
@clq.fn
def true_literal():
    return True
    
class TrueLiteralTest(unittest.TestCase):    
    def runTest(self):
        print true_literal.compile(OpenCL).program_item.code
    
@clq.fn
def false_literal():
    return False
    
class FalseLiteralTest(unittest.TestCase):    
    def runTest(self):
        print false_literal.compile(OpenCL).program_item.code
        
@clq.fn
def none_literal():
    return None
    
class NoneLiteralTest(unittest.TestCase):    
    def runTest(self):
        print none_literal.compile(OpenCL).program_item.code
        
#===============================================================================
# Constants
#===============================================================================
_k = 0
@clq.fn
def constant_test():
    return _k

class ConstantTest(unittest.TestCase):    
    def runTest(self):
        print constant_test.compile(OpenCL).program_item.code
    
class A(object):
    k = 0.0
a = A()

@clq.fn
def constant_attr_test():
    return a.k
    
class ConstantAttrTest(unittest.TestCase):
    def runTest(self):
        print constant_attr_test.compile(OpenCL).program_item.code
        
b = { 'k': 'test' }
@clq.fn
def constant_subscript_test():
    return b['k']
    
class ConstantSubscriptTest(unittest.TestCase):
    def runTest(self):
        print constant_subscript_test.compile(OpenCL).program_item.code
        
def f_k():
    return True
    
@clq.fn
def constant_function_test():
    return f_k()
    
class ConstantFunctionTest(unittest.TestCase):
    def runTest(self):
        print constant_function_test.compile(OpenCL).program_item.code
        
@clq.fn
def constant_expr_test():
    return a.k + b['k']
    
class ConstantExprTest(unittest.TestCase):
    def runTest(self):
        print constant_expr_test.compile(OpenCL).program_item.code
        
#===============================================================================
# Defaults
#===============================================================================
@clq.fn
def default_constant_test(k=0):
    return k
    
class DefaultConstantTest(unittest.TestCase):
    def runTest(self):
        print default_constant_test.compile(OpenCL).program_item.code
        
@clq.fn
def default_value_test(k=_k):
    return k
    
class DefaultValueTest(unittest.TestCase):
    def runTest(self):
        print default_value_test.compile(OpenCL).program_item.code
    
a = { 'k': 0 }    
@clq.fn
def default_expr_test(k=a['k']):
    return k
    
class DefaultExprTest(unittest.TestCase):
    def runTest(self):
        print default_expr_test.compile(OpenCL).program_item.code

@clq.fn
def nested_default_test():
    return default_expr_test()
    
class NestedDefaultTest(unittest.TestCase):
    def runTest(self):
        print nested_default_test.compile(OpenCL).program_item.code
        
class NestedDefaultConcreteTest(unittest.TestCase):
    def runTest(self):
        default_expr_test_concrete = default_expr_test.compile(OpenCL)
        @clq.fn
        def nested_default_concrete_test():
            return default_expr_test_concrete()
            
        print nested_default_concrete_test.compile(OpenCL).program_item.code
        
#===============================================================================
# Higher Order Functions
#===============================================================================
@clq.fn
def higher_order(fn, x):
    return fn(x)

class GenericHigherOrderFunctionTest_intptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_intptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_short(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_short(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_ulong(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_ulong(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_uchar(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_uchar(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_double(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_double(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_ushort(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_ushort(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_uintptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_uintptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_long(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_long(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_ptrdiff_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_ptrdiff_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_char(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_char(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_int(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_int(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_float(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_float(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_uint(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_uint(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_half(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_half(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

class GenericHigherOrderFunctionTest_size_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        hi_id = higher_order.compile(OpenCL, identity.clq_type, ocl_type)
        print hi_id.code

class ConcreteHigherOrderFunctionTest_size_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        id = identity.compile(OpenCL, ocl_type)
        hi_id = higher_order.compile(OpenCL, id.clq_type, ocl_type)
        print hi_id.code

#===============================================================================
# Casts
#===============================================================================
class CastTest_intptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_short(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_ulong(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_uchar(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_double(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_half(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_ushort(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_uintptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_long(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_char(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_int(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_float(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_uint(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_ptrdiff_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

class CastTest_size_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        @clq.fn
        def cast_test():
            return ocl_type(0)
        print cast_test.compile(OpenCL).program_item.code

#===============================================================================
# Higher-Order Types
#===============================================================================
@clq.fn
def hot_test(type):
    return type(0)
    
class HOTTest_intptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_short(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_ulong(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_uchar(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_double(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_half(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_ushort(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_uintptr_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_long(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_char(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_int(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_float(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_uint(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_ptrdiff_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
class HOTTest_size_t(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        print hot_test.compile(OpenCL, ocl_type.clq_type).program_item.code
        
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

class ForTest(unittest.TestCase):
    def runTest(self):          
        print for_test.compile(OpenCL).program_item.code

#===============================================================================
# Exec
#===============================================================================
@clq.fn
def exec_test():
    i = 0
    exec "// This is a test."
    return i
    
class ExecTest(unittest.TestCase):
    def runTest(self):
        print exec_test.compile(OpenCL).program_item.code

#===============================================================================
# Pass
#===============================================================================
@clq.fn
def pass_test():
    i = 0
    pass
    return i
    
class PassTest(unittest.TestCase):
    def runTest(self):
        print pass_test.compile(OpenCL).program_item.code

#===============================================================================
# Expr
#===============================================================================
@clq.fn
def expr_test():
    i = 0
    i + i
    return i
    
class ExprTest(unittest.TestCase):
    def runTest(self):
        print expr_test.compile(OpenCL).program_item.code

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

#===============================================================================
# IfExp
#===============================================================================
@clq.fn
def ifexp_test():
    return 1 if True else 0.0
    
class IfExpTest(unittest.TestCase):
    def runTest(self):
        print ifexp_test.compile(OpenCL).program_item.code
        
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
    
class AddressSpaceTest_intptr_t_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.intptr_t.ptr_global,
                        ocl.PtrType))

class GetSubTest_intptr_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_intptr_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_intptr_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_intptr_t_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.intptr_t.ptr_local,
                        ocl.PtrType))

class GetSubTest_intptr_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_intptr_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_intptr_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_intptr_t_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.intptr_t.ptr_private,
                        ocl.PtrType))

class GetSubTest_intptr_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_intptr_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_intptr_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_intptr_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.intptr_t.ptr_constant,
                        ocl.PtrType))

class GetSubTest_intptr_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_intptr_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_intptr_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_short_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.short.ptr_global,
                        ocl.PtrType))

class GetSubTest_short_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_short_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_short_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_short_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.short.ptr_local,
                        ocl.PtrType))

class GetSubTest_short_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_short_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_short_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_short_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.short.ptr_private,
                        ocl.PtrType))

class GetSubTest_short_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_short_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_short_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_short_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.short.ptr_constant,
                        ocl.PtrType))

class GetSubTest_short_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_short_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_short_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ulong_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ulong.ptr_global,
                        ocl.PtrType))

class GetSubTest_ulong_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ulong_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ulong_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ulong_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ulong.ptr_local,
                        ocl.PtrType))

class GetSubTest_ulong_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ulong_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ulong_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ulong_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ulong.ptr_private,
                        ocl.PtrType))

class GetSubTest_ulong_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ulong_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ulong_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ulong_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ulong.ptr_constant,
                        ocl.PtrType))

class GetSubTest_ulong_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ulong_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ulong_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uchar_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uchar.ptr_global,
                        ocl.PtrType))

class GetSubTest_uchar_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uchar_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uchar_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uchar_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uchar.ptr_local,
                        ocl.PtrType))

class GetSubTest_uchar_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uchar_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uchar_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uchar_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uchar.ptr_private,
                        ocl.PtrType))

class GetSubTest_uchar_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uchar_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uchar_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uchar_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uchar.ptr_constant,
                        ocl.PtrType))

class GetSubTest_uchar_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uchar_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uchar_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_double_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.double.ptr_global,
                        ocl.PtrType))

class GetSubTest_double_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_double_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_double_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_double_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.double.ptr_local,
                        ocl.PtrType))

class GetSubTest_double_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_double_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_double_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_double_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.double.ptr_private,
                        ocl.PtrType))

class GetSubTest_double_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_double_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_double_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_double_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.double.ptr_constant,
                        ocl.PtrType))

class GetSubTest_double_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_double_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_double_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ushort_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ushort.ptr_global,
                        ocl.PtrType))

class GetSubTest_ushort_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ushort_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ushort_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ushort_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ushort.ptr_local,
                        ocl.PtrType))

class GetSubTest_ushort_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ushort_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ushort_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ushort_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ushort.ptr_private,
                        ocl.PtrType))

class GetSubTest_ushort_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ushort_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ushort_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ushort_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ushort.ptr_constant,
                        ocl.PtrType))

class GetSubTest_ushort_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ushort_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ushort_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uintptr_t_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uintptr_t.ptr_global,
                        ocl.PtrType))

class GetSubTest_uintptr_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uintptr_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uintptr_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uintptr_t_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uintptr_t.ptr_local,
                        ocl.PtrType))

class GetSubTest_uintptr_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uintptr_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uintptr_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uintptr_t_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uintptr_t.ptr_private,
                        ocl.PtrType))

class GetSubTest_uintptr_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uintptr_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uintptr_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uintptr_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uintptr_t.ptr_constant,
                        ocl.PtrType))

class GetSubTest_uintptr_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uintptr_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uintptr_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_long_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.long.ptr_global,
                        ocl.PtrType))

class GetSubTest_long_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_long_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_long_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_long_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.long.ptr_local,
                        ocl.PtrType))

class GetSubTest_long_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_long_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_long_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_long_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.long.ptr_private,
                        ocl.PtrType))

class GetSubTest_long_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_long_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_long_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_long_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.long.ptr_constant,
                        ocl.PtrType))

class GetSubTest_long_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_long_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_long_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ptrdiff_t_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ptrdiff_t.ptr_global,
                        ocl.PtrType))

class GetSubTest_ptrdiff_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ptrdiff_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ptrdiff_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ptrdiff_t_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ptrdiff_t.ptr_local,
                        ocl.PtrType))

class GetSubTest_ptrdiff_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ptrdiff_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ptrdiff_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ptrdiff_t_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ptrdiff_t.ptr_private,
                        ocl.PtrType))

class GetSubTest_ptrdiff_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ptrdiff_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ptrdiff_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_ptrdiff_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.ptrdiff_t.ptr_constant,
                        ocl.PtrType))

class GetSubTest_ptrdiff_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_ptrdiff_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_ptrdiff_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_char_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.char.ptr_global,
                        ocl.PtrType))

class GetSubTest_char_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_char_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_char_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_char_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.char.ptr_local,
                        ocl.PtrType))

class GetSubTest_char_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_char_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_char_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_char_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.char.ptr_private,
                        ocl.PtrType))

class GetSubTest_char_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_char_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_char_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_char_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.char.ptr_constant,
                        ocl.PtrType))

class GetSubTest_char_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_char_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_char_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_int_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.int.ptr_global,
                        ocl.PtrType))

class GetSubTest_int_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_int_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_int_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_int_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.int.ptr_local,
                        ocl.PtrType))

class GetSubTest_int_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_int_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_int_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_int_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.int.ptr_private,
                        ocl.PtrType))

class GetSubTest_int_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_int_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_int_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_int_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.int.ptr_constant,
                        ocl.PtrType))

class GetSubTest_int_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_int_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_int_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_float_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.float.ptr_global,
                        ocl.PtrType))

class GetSubTest_float_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_float_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_float_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_float_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.float.ptr_local,
                        ocl.PtrType))

class GetSubTest_float_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_float_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_float_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_float_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.float.ptr_private,
                        ocl.PtrType))

class GetSubTest_float_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_float_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_float_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_float_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.float.ptr_constant,
                        ocl.PtrType))

class GetSubTest_float_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_float_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_float_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uint_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uint.ptr_global,
                        ocl.PtrType))

class GetSubTest_uint_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uint_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uint_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uint_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uint.ptr_local,
                        ocl.PtrType))

class GetSubTest_uint_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uint_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uint_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uint_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uint.ptr_private,
                        ocl.PtrType))

class GetSubTest_uint_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uint_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uint_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_uint_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.uint.ptr_constant,
                        ocl.PtrType))

class GetSubTest_uint_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_uint_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_uint_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_half_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.half.ptr_global,
                        ocl.PtrType))

class GetSubTest_half_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_half_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_half_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_half_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.half.ptr_local,
                        ocl.PtrType))

class GetSubTest_half_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_half_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_half_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_half_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.half.ptr_private,
                        ocl.PtrType))

class GetSubTest_half_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_half_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_half_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_half_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.half.ptr_constant,
                        ocl.PtrType))

class GetSubTest_half_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_half_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_half_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_size_t_ptr_global(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.size_t.ptr_global,
                        ocl.PtrType))

class GetSubTest_size_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_global
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_size_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_global
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_size_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_global
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_size_t_ptr_local(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.size_t.ptr_local,
                        ocl.PtrType))

class GetSubTest_size_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_local
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_size_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_local
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_size_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_local
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_size_t_ptr_private(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.size_t.ptr_private,
                        ocl.PtrType))

class GetSubTest_size_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_private
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_size_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_private
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_size_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_private
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
class AddressSpaceTest_size_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        self.assertTrue(isinstance(ocl.size_t.ptr_constant,
                        ocl.PtrType))

class GetSubTest_size_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_constant
        print get_sub_test.compile(OpenCL, ocl_type).program_item.code
        
class SetSubTest_size_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_constant
        print set_sub_test.compile(OpenCL, ocl_type).program_item.code

class SetSubTestWithCast_size_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t.ptr_constant
        print set_sub_test_with_cast.compile(OpenCL, ocl_type).program_item.code
    
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
    
class LocTest_intptr_t_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.intptr_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_intptr_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_intptr_t_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.intptr_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_intptr_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_intptr_t_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.intptr_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_intptr_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_intptr_t_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.intptr_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_intptr_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.intptr_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_short_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.short
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_short_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_short_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.short
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_short_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_short_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.short
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_short_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_short_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.short
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_short_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.short
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ulong_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ulong
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ulong_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ulong_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ulong
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ulong_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ulong_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ulong
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ulong_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ulong_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ulong
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ulong_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ulong
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uchar_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uchar
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uchar_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uchar_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uchar
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uchar_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uchar_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uchar
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uchar_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uchar_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uchar
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uchar_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uchar
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_double_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.double
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_double_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_double_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.double
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_double_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_double_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.double
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_double_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_double_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.double
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_double_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.double
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ushort_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ushort
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ushort_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ushort_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ushort
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ushort_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ushort_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ushort
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ushort_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ushort_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ushort
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ushort_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ushort
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uintptr_t_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uintptr_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uintptr_t_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uintptr_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uintptr_t_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uintptr_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uintptr_t_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uintptr_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uintptr_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_long_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.long
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_long_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_long_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.long
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_long_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_long_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.long
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_long_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_long_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.long
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_long_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.long
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ptrdiff_t_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ptrdiff_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ptrdiff_t_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ptrdiff_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ptrdiff_t_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ptrdiff_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_ptrdiff_t_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_ptrdiff_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.ptrdiff_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_char_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.char
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_char_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_char_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.char
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_char_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_char_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.char
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_char_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_char_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.char
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_char_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.char
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_int_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.int
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_int_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_int_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.int
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_int_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_int_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.int
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_int_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_int_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.int
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_int_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.int
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_float_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.float
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_float_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_float_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.float
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_float_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_float_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.float
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_float_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_float_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.float
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_float_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.float
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uint_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uint
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uint_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uint_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uint
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uint_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uint_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uint
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uint_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_uint_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.uint
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_uint_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.uint
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_half_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.half
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_half_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_half_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.half
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_half_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_half_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.half
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_half_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_half_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.half
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_half_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.half
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_size_t_ptr_global(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.size_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_size_t_ptr_global(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_size_t_ptr_local(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.size_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_size_t_ptr_local(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_size_t_ptr_private(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.size_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_size_t_ptr_private(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

class LocTest_size_t_ptr_constant(unittest.TestCase): 
    def runTest(self):
        ocl_type = ocl.size_t
        print loc_test.compile(OpenCL, ocl_type).program_item.code
        
class ValTest_size_t_ptr_constant(unittest.TestCase):
    def runTest(self):
        ocl_type = ocl.size_t
        print val_test.compile(OpenCL, ocl_type).program_item.code

#===============================================================================
# Invalid Operations
#===============================================================================
@clq.fn
def for_orelse_test(x):
    for i in (0, 10, 1):
        pass
    else:
        pass
    
class For_orelseTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          for_orelse_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def slice_test(x):
    x[1:2]
    
class SliceTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          slice_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def raise_test(x):
    raise x
    
class RaiseTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          raise_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def list_test(x):
    [1, 2]
    
class ListTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          list_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def while_orelse_test(x):
    while x:
        pass
    else:
        pass
    
class While_orelseTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          while_orelse_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def yield_test(x):
    yield x
    
class YieldTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          yield_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def call_keywords_test(x):
    identity(x=0)
    
class Call_keywordsTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          call_keywords_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def slice_ellipsis_test(x):
    x[...]
    
class Slice_EllipsisTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          slice_ellipsis_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def dict_test(x):
    { 'a': 'A' }
    
class DictTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          dict_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def call_kwargs_test(x):
    identity(**x)
    
class Call_kwargsTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          call_kwargs_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def isnot_test(x):
    x is not 0
    
class IsNotTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          isnot_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def nestedfunction_test(x):
    def nested():
        return
    
class NestedFunctionTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          nestedfunction_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def print_test(x):
    print x
    
class PrintTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          print_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def import_test(x):
    import clq
    
class ImportTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          import_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def assert_msg_test(x):
    assert x, 'msg'
    
class Assert_msgTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          assert_msg_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def tryexcept_test(x):
    try:
        pass
    except:
        pass
    else:
        pass
    
class TryExceptTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          tryexcept_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def delete_test(x):
    del x
    
class DeleteTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          delete_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def slice_multi_test(x):
    x[1:2:3]
    
class Slice_multiTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          slice_multi_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def nestedclass_test(x):
    class nested():
        pass
    
class NestedClassTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          nestedclass_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def call_starargs_test(x):
    identity(*x)
    
class Call_starargsTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          call_starargs_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def tuple_test(x):
    (1, 2)
    
class TupleTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          tuple_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def notin_test(x):
    0 not in x
    
class NotInTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          notin_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def generatorexp_test(x):
    (i for i in (0, 1, 2))
    
class GeneratorExpTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          generatorexp_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def is_test(x):
    x is 0
    
class IsTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          is_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def global_test(x):
    global _k
    
class GlobalTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          global_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def assert_test(x):
    assert x
    
class AssertTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          assert_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def importfrom_test(x):
    from clq import fn
    
class ImportFromTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          importfrom_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def tryfinally_test(x):
    try:
        pass
    except:
        pass
    else:
        pass
    finally:
        pass
    
class TryFinallyTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          tryfinally_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def in_test(x):
    0 in x
    
class InTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          in_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def compare_multi_test(x):
    0 < x < 1
    
class Compare_multiTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          compare_multi_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def lambda_test(x):
    lambda x: x
    
class LambdaTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          lambda_test.compile, OpenCL, ocl.int)
 
 
@clq.fn
def with_test(x):
    with x:
        pass
    
class WithTest(unittest.TestCase):
    def runTest(self):
        self.assertRaises(clq.InvalidOperationError,
                          with_test.compile, OpenCL, ocl.int)
 
 
#===============================================================================
# t(test)
#===============================================================================
class TypeFnTest_intptr_t(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("intptr_t"), ocl.intptr_t)
        self.assertEqual(ocl.t("__global intptr_t*"), 
                         ocl.intptr_t.ptr_global)
        self.assertEqual(ocl.t("__global intptr_t**"), 
                         ocl.intptr_t.ptr_global.ptr)
        self.assertEqual(ocl.t("global  intptr_t *   "), 
                         ocl.intptr_t.ptr_global)
        self.assertEqual(ocl.t("__local  intptr_t *"), 
                         ocl.intptr_t.ptr_local)
        self.assertEqual(ocl.t("__local  intptr_t **"), 
                         ocl.intptr_t.ptr_local.ptr)
        self.assertEqual(ocl.t("local  intptr_t *"), 
                         ocl.intptr_t.ptr_local)
        self.assertEqual(ocl.t("__private  intptr_t*"), 
                                 ocl.intptr_t.ptr_private)
        self.assertEqual(ocl.t("__private  intptr_t**"), 
                                 ocl.intptr_t.ptr_private.ptr)
        self.assertEqual(ocl.t("private intptr_t*"), 
                                 ocl.intptr_t.ptr_private)
        self.assertEqual(ocl.intptr_t.ptr_private, ocl.intptr_t.ptr)
        self.assertEqual(ocl.t("__constant intptr_t*"), 
                         ocl.intptr_t.ptr_constant)
        self.assertEqual(ocl.t("__private  intptr_t**"), 
                                 ocl.intptr_t.ptr_private.ptr)
        self.assertEqual(ocl.t("constant intptr_t*"), 
                                ocl.intptr_t.ptr_constant)
    
class TypeFnTest_short(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("short"), ocl.short)
        self.assertEqual(ocl.t("__global short*"), 
                         ocl.short.ptr_global)
        self.assertEqual(ocl.t("__global short**"), 
                         ocl.short.ptr_global.ptr)
        self.assertEqual(ocl.t("global  short *   "), 
                         ocl.short.ptr_global)
        self.assertEqual(ocl.t("__local  short *"), 
                         ocl.short.ptr_local)
        self.assertEqual(ocl.t("__local  short **"), 
                         ocl.short.ptr_local.ptr)
        self.assertEqual(ocl.t("local  short *"), 
                         ocl.short.ptr_local)
        self.assertEqual(ocl.t("__private  short*"), 
                                 ocl.short.ptr_private)
        self.assertEqual(ocl.t("__private  short**"), 
                                 ocl.short.ptr_private.ptr)
        self.assertEqual(ocl.t("private short*"), 
                                 ocl.short.ptr_private)
        self.assertEqual(ocl.short.ptr_private, ocl.short.ptr)
        self.assertEqual(ocl.t("__constant short*"), 
                         ocl.short.ptr_constant)
        self.assertEqual(ocl.t("__private  short**"), 
                                 ocl.short.ptr_private.ptr)
        self.assertEqual(ocl.t("constant short*"), 
                                ocl.short.ptr_constant)
    
class TypeFnTest_ulong(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("ulong"), ocl.ulong)
        self.assertEqual(ocl.t("__global ulong*"), 
                         ocl.ulong.ptr_global)
        self.assertEqual(ocl.t("__global ulong**"), 
                         ocl.ulong.ptr_global.ptr)
        self.assertEqual(ocl.t("global  ulong *   "), 
                         ocl.ulong.ptr_global)
        self.assertEqual(ocl.t("__local  ulong *"), 
                         ocl.ulong.ptr_local)
        self.assertEqual(ocl.t("__local  ulong **"), 
                         ocl.ulong.ptr_local.ptr)
        self.assertEqual(ocl.t("local  ulong *"), 
                         ocl.ulong.ptr_local)
        self.assertEqual(ocl.t("__private  ulong*"), 
                                 ocl.ulong.ptr_private)
        self.assertEqual(ocl.t("__private  ulong**"), 
                                 ocl.ulong.ptr_private.ptr)
        self.assertEqual(ocl.t("private ulong*"), 
                                 ocl.ulong.ptr_private)
        self.assertEqual(ocl.ulong.ptr_private, ocl.ulong.ptr)
        self.assertEqual(ocl.t("__constant ulong*"), 
                         ocl.ulong.ptr_constant)
        self.assertEqual(ocl.t("__private  ulong**"), 
                                 ocl.ulong.ptr_private.ptr)
        self.assertEqual(ocl.t("constant ulong*"), 
                                ocl.ulong.ptr_constant)
    
class TypeFnTest_uchar(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("uchar"), ocl.uchar)
        self.assertEqual(ocl.t("__global uchar*"), 
                         ocl.uchar.ptr_global)
        self.assertEqual(ocl.t("__global uchar**"), 
                         ocl.uchar.ptr_global.ptr)
        self.assertEqual(ocl.t("global  uchar *   "), 
                         ocl.uchar.ptr_global)
        self.assertEqual(ocl.t("__local  uchar *"), 
                         ocl.uchar.ptr_local)
        self.assertEqual(ocl.t("__local  uchar **"), 
                         ocl.uchar.ptr_local.ptr)
        self.assertEqual(ocl.t("local  uchar *"), 
                         ocl.uchar.ptr_local)
        self.assertEqual(ocl.t("__private  uchar*"), 
                                 ocl.uchar.ptr_private)
        self.assertEqual(ocl.t("__private  uchar**"), 
                                 ocl.uchar.ptr_private.ptr)
        self.assertEqual(ocl.t("private uchar*"), 
                                 ocl.uchar.ptr_private)
        self.assertEqual(ocl.uchar.ptr_private, ocl.uchar.ptr)
        self.assertEqual(ocl.t("__constant uchar*"), 
                         ocl.uchar.ptr_constant)
        self.assertEqual(ocl.t("__private  uchar**"), 
                                 ocl.uchar.ptr_private.ptr)
        self.assertEqual(ocl.t("constant uchar*"), 
                                ocl.uchar.ptr_constant)
    
class TypeFnTest_double(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("double"), ocl.double)
        self.assertEqual(ocl.t("__global double*"), 
                         ocl.double.ptr_global)
        self.assertEqual(ocl.t("__global double**"), 
                         ocl.double.ptr_global.ptr)
        self.assertEqual(ocl.t("global  double *   "), 
                         ocl.double.ptr_global)
        self.assertEqual(ocl.t("__local  double *"), 
                         ocl.double.ptr_local)
        self.assertEqual(ocl.t("__local  double **"), 
                         ocl.double.ptr_local.ptr)
        self.assertEqual(ocl.t("local  double *"), 
                         ocl.double.ptr_local)
        self.assertEqual(ocl.t("__private  double*"), 
                                 ocl.double.ptr_private)
        self.assertEqual(ocl.t("__private  double**"), 
                                 ocl.double.ptr_private.ptr)
        self.assertEqual(ocl.t("private double*"), 
                                 ocl.double.ptr_private)
        self.assertEqual(ocl.double.ptr_private, ocl.double.ptr)
        self.assertEqual(ocl.t("__constant double*"), 
                         ocl.double.ptr_constant)
        self.assertEqual(ocl.t("__private  double**"), 
                                 ocl.double.ptr_private.ptr)
        self.assertEqual(ocl.t("constant double*"), 
                                ocl.double.ptr_constant)
    
class TypeFnTest_ushort(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("ushort"), ocl.ushort)
        self.assertEqual(ocl.t("__global ushort*"), 
                         ocl.ushort.ptr_global)
        self.assertEqual(ocl.t("__global ushort**"), 
                         ocl.ushort.ptr_global.ptr)
        self.assertEqual(ocl.t("global  ushort *   "), 
                         ocl.ushort.ptr_global)
        self.assertEqual(ocl.t("__local  ushort *"), 
                         ocl.ushort.ptr_local)
        self.assertEqual(ocl.t("__local  ushort **"), 
                         ocl.ushort.ptr_local.ptr)
        self.assertEqual(ocl.t("local  ushort *"), 
                         ocl.ushort.ptr_local)
        self.assertEqual(ocl.t("__private  ushort*"), 
                                 ocl.ushort.ptr_private)
        self.assertEqual(ocl.t("__private  ushort**"), 
                                 ocl.ushort.ptr_private.ptr)
        self.assertEqual(ocl.t("private ushort*"), 
                                 ocl.ushort.ptr_private)
        self.assertEqual(ocl.ushort.ptr_private, ocl.ushort.ptr)
        self.assertEqual(ocl.t("__constant ushort*"), 
                         ocl.ushort.ptr_constant)
        self.assertEqual(ocl.t("__private  ushort**"), 
                                 ocl.ushort.ptr_private.ptr)
        self.assertEqual(ocl.t("constant ushort*"), 
                                ocl.ushort.ptr_constant)
    
class TypeFnTest_uintptr_t(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("uintptr_t"), ocl.uintptr_t)
        self.assertEqual(ocl.t("__global uintptr_t*"), 
                         ocl.uintptr_t.ptr_global)
        self.assertEqual(ocl.t("__global uintptr_t**"), 
                         ocl.uintptr_t.ptr_global.ptr)
        self.assertEqual(ocl.t("global  uintptr_t *   "), 
                         ocl.uintptr_t.ptr_global)
        self.assertEqual(ocl.t("__local  uintptr_t *"), 
                         ocl.uintptr_t.ptr_local)
        self.assertEqual(ocl.t("__local  uintptr_t **"), 
                         ocl.uintptr_t.ptr_local.ptr)
        self.assertEqual(ocl.t("local  uintptr_t *"), 
                         ocl.uintptr_t.ptr_local)
        self.assertEqual(ocl.t("__private  uintptr_t*"), 
                                 ocl.uintptr_t.ptr_private)
        self.assertEqual(ocl.t("__private  uintptr_t**"), 
                                 ocl.uintptr_t.ptr_private.ptr)
        self.assertEqual(ocl.t("private uintptr_t*"), 
                                 ocl.uintptr_t.ptr_private)
        self.assertEqual(ocl.uintptr_t.ptr_private, ocl.uintptr_t.ptr)
        self.assertEqual(ocl.t("__constant uintptr_t*"), 
                         ocl.uintptr_t.ptr_constant)
        self.assertEqual(ocl.t("__private  uintptr_t**"), 
                                 ocl.uintptr_t.ptr_private.ptr)
        self.assertEqual(ocl.t("constant uintptr_t*"), 
                                ocl.uintptr_t.ptr_constant)
    
class TypeFnTest_long(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("long"), ocl.long)
        self.assertEqual(ocl.t("__global long*"), 
                         ocl.long.ptr_global)
        self.assertEqual(ocl.t("__global long**"), 
                         ocl.long.ptr_global.ptr)
        self.assertEqual(ocl.t("global  long *   "), 
                         ocl.long.ptr_global)
        self.assertEqual(ocl.t("__local  long *"), 
                         ocl.long.ptr_local)
        self.assertEqual(ocl.t("__local  long **"), 
                         ocl.long.ptr_local.ptr)
        self.assertEqual(ocl.t("local  long *"), 
                         ocl.long.ptr_local)
        self.assertEqual(ocl.t("__private  long*"), 
                                 ocl.long.ptr_private)
        self.assertEqual(ocl.t("__private  long**"), 
                                 ocl.long.ptr_private.ptr)
        self.assertEqual(ocl.t("private long*"), 
                                 ocl.long.ptr_private)
        self.assertEqual(ocl.long.ptr_private, ocl.long.ptr)
        self.assertEqual(ocl.t("__constant long*"), 
                         ocl.long.ptr_constant)
        self.assertEqual(ocl.t("__private  long**"), 
                                 ocl.long.ptr_private.ptr)
        self.assertEqual(ocl.t("constant long*"), 
                                ocl.long.ptr_constant)
    
class TypeFnTest_ptrdiff_t(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("ptrdiff_t"), ocl.ptrdiff_t)
        self.assertEqual(ocl.t("__global ptrdiff_t*"), 
                         ocl.ptrdiff_t.ptr_global)
        self.assertEqual(ocl.t("__global ptrdiff_t**"), 
                         ocl.ptrdiff_t.ptr_global.ptr)
        self.assertEqual(ocl.t("global  ptrdiff_t *   "), 
                         ocl.ptrdiff_t.ptr_global)
        self.assertEqual(ocl.t("__local  ptrdiff_t *"), 
                         ocl.ptrdiff_t.ptr_local)
        self.assertEqual(ocl.t("__local  ptrdiff_t **"), 
                         ocl.ptrdiff_t.ptr_local.ptr)
        self.assertEqual(ocl.t("local  ptrdiff_t *"), 
                         ocl.ptrdiff_t.ptr_local)
        self.assertEqual(ocl.t("__private  ptrdiff_t*"), 
                                 ocl.ptrdiff_t.ptr_private)
        self.assertEqual(ocl.t("__private  ptrdiff_t**"), 
                                 ocl.ptrdiff_t.ptr_private.ptr)
        self.assertEqual(ocl.t("private ptrdiff_t*"), 
                                 ocl.ptrdiff_t.ptr_private)
        self.assertEqual(ocl.ptrdiff_t.ptr_private, ocl.ptrdiff_t.ptr)
        self.assertEqual(ocl.t("__constant ptrdiff_t*"), 
                         ocl.ptrdiff_t.ptr_constant)
        self.assertEqual(ocl.t("__private  ptrdiff_t**"), 
                                 ocl.ptrdiff_t.ptr_private.ptr)
        self.assertEqual(ocl.t("constant ptrdiff_t*"), 
                                ocl.ptrdiff_t.ptr_constant)
    
class TypeFnTest_char(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("char"), ocl.char)
        self.assertEqual(ocl.t("__global char*"), 
                         ocl.char.ptr_global)
        self.assertEqual(ocl.t("__global char**"), 
                         ocl.char.ptr_global.ptr)
        self.assertEqual(ocl.t("global  char *   "), 
                         ocl.char.ptr_global)
        self.assertEqual(ocl.t("__local  char *"), 
                         ocl.char.ptr_local)
        self.assertEqual(ocl.t("__local  char **"), 
                         ocl.char.ptr_local.ptr)
        self.assertEqual(ocl.t("local  char *"), 
                         ocl.char.ptr_local)
        self.assertEqual(ocl.t("__private  char*"), 
                                 ocl.char.ptr_private)
        self.assertEqual(ocl.t("__private  char**"), 
                                 ocl.char.ptr_private.ptr)
        self.assertEqual(ocl.t("private char*"), 
                                 ocl.char.ptr_private)
        self.assertEqual(ocl.char.ptr_private, ocl.char.ptr)
        self.assertEqual(ocl.t("__constant char*"), 
                         ocl.char.ptr_constant)
        self.assertEqual(ocl.t("__private  char**"), 
                                 ocl.char.ptr_private.ptr)
        self.assertEqual(ocl.t("constant char*"), 
                                ocl.char.ptr_constant)
    
class TypeFnTest_int(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("int"), ocl.int)
        self.assertEqual(ocl.t("__global int*"), 
                         ocl.int.ptr_global)
        self.assertEqual(ocl.t("__global int**"), 
                         ocl.int.ptr_global.ptr)
        self.assertEqual(ocl.t("global  int *   "), 
                         ocl.int.ptr_global)
        self.assertEqual(ocl.t("__local  int *"), 
                         ocl.int.ptr_local)
        self.assertEqual(ocl.t("__local  int **"), 
                         ocl.int.ptr_local.ptr)
        self.assertEqual(ocl.t("local  int *"), 
                         ocl.int.ptr_local)
        self.assertEqual(ocl.t("__private  int*"), 
                                 ocl.int.ptr_private)
        self.assertEqual(ocl.t("__private  int**"), 
                                 ocl.int.ptr_private.ptr)
        self.assertEqual(ocl.t("private int*"), 
                                 ocl.int.ptr_private)
        self.assertEqual(ocl.int.ptr_private, ocl.int.ptr)
        self.assertEqual(ocl.t("__constant int*"), 
                         ocl.int.ptr_constant)
        self.assertEqual(ocl.t("__private  int**"), 
                                 ocl.int.ptr_private.ptr)
        self.assertEqual(ocl.t("constant int*"), 
                                ocl.int.ptr_constant)
    
class TypeFnTest_float(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("float"), ocl.float)
        self.assertEqual(ocl.t("__global float*"), 
                         ocl.float.ptr_global)
        self.assertEqual(ocl.t("__global float**"), 
                         ocl.float.ptr_global.ptr)
        self.assertEqual(ocl.t("global  float *   "), 
                         ocl.float.ptr_global)
        self.assertEqual(ocl.t("__local  float *"), 
                         ocl.float.ptr_local)
        self.assertEqual(ocl.t("__local  float **"), 
                         ocl.float.ptr_local.ptr)
        self.assertEqual(ocl.t("local  float *"), 
                         ocl.float.ptr_local)
        self.assertEqual(ocl.t("__private  float*"), 
                                 ocl.float.ptr_private)
        self.assertEqual(ocl.t("__private  float**"), 
                                 ocl.float.ptr_private.ptr)
        self.assertEqual(ocl.t("private float*"), 
                                 ocl.float.ptr_private)
        self.assertEqual(ocl.float.ptr_private, ocl.float.ptr)
        self.assertEqual(ocl.t("__constant float*"), 
                         ocl.float.ptr_constant)
        self.assertEqual(ocl.t("__private  float**"), 
                                 ocl.float.ptr_private.ptr)
        self.assertEqual(ocl.t("constant float*"), 
                                ocl.float.ptr_constant)
    
class TypeFnTest_uint(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("uint"), ocl.uint)
        self.assertEqual(ocl.t("__global uint*"), 
                         ocl.uint.ptr_global)
        self.assertEqual(ocl.t("__global uint**"), 
                         ocl.uint.ptr_global.ptr)
        self.assertEqual(ocl.t("global  uint *   "), 
                         ocl.uint.ptr_global)
        self.assertEqual(ocl.t("__local  uint *"), 
                         ocl.uint.ptr_local)
        self.assertEqual(ocl.t("__local  uint **"), 
                         ocl.uint.ptr_local.ptr)
        self.assertEqual(ocl.t("local  uint *"), 
                         ocl.uint.ptr_local)
        self.assertEqual(ocl.t("__private  uint*"), 
                                 ocl.uint.ptr_private)
        self.assertEqual(ocl.t("__private  uint**"), 
                                 ocl.uint.ptr_private.ptr)
        self.assertEqual(ocl.t("private uint*"), 
                                 ocl.uint.ptr_private)
        self.assertEqual(ocl.uint.ptr_private, ocl.uint.ptr)
        self.assertEqual(ocl.t("__constant uint*"), 
                         ocl.uint.ptr_constant)
        self.assertEqual(ocl.t("__private  uint**"), 
                                 ocl.uint.ptr_private.ptr)
        self.assertEqual(ocl.t("constant uint*"), 
                                ocl.uint.ptr_constant)
    
class TypeFnTest_half(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("half"), ocl.half)
        self.assertEqual(ocl.t("__global half*"), 
                         ocl.half.ptr_global)
        self.assertEqual(ocl.t("__global half**"), 
                         ocl.half.ptr_global.ptr)
        self.assertEqual(ocl.t("global  half *   "), 
                         ocl.half.ptr_global)
        self.assertEqual(ocl.t("__local  half *"), 
                         ocl.half.ptr_local)
        self.assertEqual(ocl.t("__local  half **"), 
                         ocl.half.ptr_local.ptr)
        self.assertEqual(ocl.t("local  half *"), 
                         ocl.half.ptr_local)
        self.assertEqual(ocl.t("__private  half*"), 
                                 ocl.half.ptr_private)
        self.assertEqual(ocl.t("__private  half**"), 
                                 ocl.half.ptr_private.ptr)
        self.assertEqual(ocl.t("private half*"), 
                                 ocl.half.ptr_private)
        self.assertEqual(ocl.half.ptr_private, ocl.half.ptr)
        self.assertEqual(ocl.t("__constant half*"), 
                         ocl.half.ptr_constant)
        self.assertEqual(ocl.t("__private  half**"), 
                                 ocl.half.ptr_private.ptr)
        self.assertEqual(ocl.t("constant half*"), 
                                ocl.half.ptr_constant)
    
class TypeFnTest_size_t(unittest.TestCase):
    def runTest(self):
        self.assertEqual(ocl.t("size_t"), ocl.size_t)
        self.assertEqual(ocl.t("__global size_t*"), 
                         ocl.size_t.ptr_global)
        self.assertEqual(ocl.t("__global size_t**"), 
                         ocl.size_t.ptr_global.ptr)
        self.assertEqual(ocl.t("global  size_t *   "), 
                         ocl.size_t.ptr_global)
        self.assertEqual(ocl.t("__local  size_t *"), 
                         ocl.size_t.ptr_local)
        self.assertEqual(ocl.t("__local  size_t **"), 
                         ocl.size_t.ptr_local.ptr)
        self.assertEqual(ocl.t("local  size_t *"), 
                         ocl.size_t.ptr_local)
        self.assertEqual(ocl.t("__private  size_t*"), 
                                 ocl.size_t.ptr_private)
        self.assertEqual(ocl.t("__private  size_t**"), 
                                 ocl.size_t.ptr_private.ptr)
        self.assertEqual(ocl.t("private size_t*"), 
                                 ocl.size_t.ptr_private)
        self.assertEqual(ocl.size_t.ptr_private, ocl.size_t.ptr)
        self.assertEqual(ocl.t("__constant size_t*"), 
                         ocl.size_t.ptr_constant)
        self.assertEqual(ocl.t("__private  size_t**"), 
                                 ocl.size_t.ptr_private.ptr)
        self.assertEqual(ocl.t("constant size_t*"), 
                                ocl.size_t.ptr_constant)
    
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
        
