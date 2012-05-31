import clq
import clq.extensions
import clq.backends.opencl as ocl
import clq.extensions.grammar as grammars #the grammars extension.
OpenCL = ocl.Backend()

#t1 -- G1 <: G2
G1 = grammars.Grammar.factory(OpenCL,".")
G2 = grammars.Grammar.factory(OpenCL,".+")
assert G2.has_subtype(G1)

#t2 -- Grammar
@clq.fn
def test(a):
    return a
test = test.compile(OpenCL, grammars.Grammar.factory(OpenCL, "."))
print test.program_item.code


#t3 -- Subtyping. THIS SHOULD FAIL.
@clq.fn
def myFn(a):
    pass #...
myFn = myFn.compile(OpenCL, G1)

@clq.fn
def myFn2(a, myFn):
    myFn(a)
myFn2 = myFn2.compile(OpenCL, G2, myFn.cl_type)

print myFn2.program_item.code