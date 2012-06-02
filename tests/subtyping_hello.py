import clq
import clq.extensions
import clq.backends.opencl as ocl
import clq.extensions.grammar as grammars #the grammars extension.
OpenCL = ocl.Backend()

#TEST: G1 <: G2
G1 = grammars.Grammar.factory(OpenCL,".")
G2 = grammars.Grammar.factory(OpenCL,".+")
assert G2.has_subtype(G1)

#TEST: Function returning a grammar
@clq.fn
def test(a):
    return a
test = test.compile(OpenCL,  G1)
assert test.return_type == G1

#TEST: Grammar factor interning. This fails b/c interning isn't working yet.
#@clq.fn
#def test(a):
#    return a
#test = test.compile(OpenCL, grammars.Grammar.factory(OpenCL, G1._regex))
#assert test.return_type == G1


#TEST: Subtyping (this test goes all the way down the to asserts.
@clq.fn
def myFn(a):
    return a
myFn = myFn.compile(OpenCL, G1)

@clq.fn
def myFn2(a, myFn):
    return  a + myFn(a) #Note: This reads "append myFn(a) to a; meaning the type of a is preserved.
myFn2 = myFn2.compile(OpenCL, G2, myFn.cl_type)

@clq.fn
def myFn3(a, myFn):
    return  myFn(a) + a
myFn3 = myFn3.compile(OpenCL, G2, myFn.cl_type)

assert myFn2.return_type == G2
assert myFn3.return_type == G1
