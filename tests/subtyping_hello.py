import clq
import clq.extensions
import clq.backends.opencl as ocl
import clq.extensions.language_types as lang #the regex types extension.
OpenCL = ocl.Backend()

#TEST: Reflection and grammar inclusion
L1 = lang.Language.factory(OpenCL,".")
L2 = lang.Language.factory(OpenCL,".+")
assert L1.is_subtype(L1)
assert L2.is_subtype(L2)
assert L2.is_subtype(L1) #This is dependent on the regex_tests

#TEST: Function returning a Language
@clq.fn
def test(a):
    return a
test = test.compile(OpenCL,  L1)
assert test.return_type == L1

#TEST: Language factor interning. This fails b/c interning isn't working yet.
#@clq.fn
#def test(a):
#    return a
#test = test.compile(OpenCL, lang.Language.factory(OpenCL, G1._regex))
#assert test.return_type == G1


#TEST: Subtyping (this test goes all the way down the to asserts.
@clq.fn
def myFn(a):
    return a
myFn = myFn.compile(OpenCL, L1)

@clq.fn
def myFn2(a, myFn):
    return  a + myFn(a) #Note: This reads "append myFn(a) to a; meaning the type of a is preserved.
myFn2 = myFn2.compile(OpenCL, L2, myFn.cl_type)

@clq.fn
def myFn3(a, myFn):
    return  myFn(a) + a
myFn3 = myFn3.compile(OpenCL, L2, myFn.cl_type)

assert myFn2.return_type == L2
assert myFn3.return_type == L1
