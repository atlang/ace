"""Basic unit tests for cl.oquence function definition."""
import unittest

import clq
import clq.opencl as ocl
import clq.corelib as corelib

# Need to test every language feature, every type

class IdTestInt(unittest.TestCase):
    def runTest(self):
        print corelib.identity.compile(ocl.cl_int).program_item.code == "int identity(int x) {\n    return x;\n}\n"
#    
#
#class TestType(clq.Type):
#    def __init__(self):
#        clq.Type.__init__(self, name="test")
#
#test = TestType()
#
#int = ocl.cl_int
#    
#@clq.fn
#def id(x):
#    return x
#print id.compile(int).program_item.code
#
#@clq.fn
#def id_with_assignment(x):
#    y = x
#    return y
#print id_with_assignment.compile(int).program_item.code
#
#@clq.fn
#def plus(x, y):
#    return x + y
#print plus.compile(int, int).program_item.code
#
#@clq.fn
#def subscript(x, y):
#    return x[y]
#print subscript.compile(int.global_ptr, int).program_item.code
#
#@clq.fn
#def subscript_assignment(x, y, z):
#    x[y] = z
#print subscript_assignment.compile(int.global_ptr, int, int).program_item.code
