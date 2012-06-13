import clq
import clq.extensions
import clq.backends.opencl as ocl
import clq.extensions.language_types as lang #the regex types extension.
OpenCL = ocl.Backend()

#TEST: Memoizing Language based on regular expression equivalence
L1 = lang.Language.factory(OpenCL, "(.?)+")
L2 = lang.Language.factory(OpenCL, ".*")
assert L1 == L2

assert L1.is_subtype(L2)
assert L2.is_subtype(L1)
L3 = lang.Language.factory(OpenCL, ".?")
assert L1 != L3
subtype_of_l1 = lang.Language.factory(OpenCL, ".+")
assert subtype_of_l1 != L1

#TODO test to make sure memoizing is backend-specific.

#TEST: Reflection and grammar inclusion
L1 = lang.Language.factory(OpenCL,".")
L2 = lang.Language.factory(OpenCL,".+")
assert L1 != L2
assert L1.is_subtype(L1)
assert L2.is_subtype(L2)
assert L2.is_subtype(L1)


@clq.fn
def test_return(a):
    return a
test_return = test_return.compile(OpenCL, L1)
assert test_return.return_type == L1

#TEST: Function returning a Language
@clq.fn
def test(a):
    return a
test1 = test.compile(OpenCL,  L1)
assert test1.return_type == L1
L3 = lang.Language.factory(OpenCL, L1._regex)
test2 = test.compile(OpenCL, L3)
assert test2.return_type == L3

##TEST: Language factor interning. This fails b/c interning isn't working yet.
@clq.fn
def test2(a):
    return a
test2 = test2.compile(OpenCL, lang.Language.factory(OpenCL, L1._regex))
assert test2.return_type == L1

#TEST: Return type of concatenation
r_type = lang.Language.factory(OpenCL, ".")
l_type = lang.Language.factory(OpenCL, ".+")
@clq.fn
def test_concatenation(a,b):
    return a + b
test_concatenation = test_concatenation.compile(OpenCL, r_type, l_type)
expected_return_type = lang.Language.factory(OpenCL,"..+")
assert test_concatenation.return_type == lang.Language.factory(OpenCL,"..+")  

#TEST: Subtyping
super_type = lang.Language.factory(OpenCL, "a+b")
sub_type   = lang.Language.factory(OpenCL, "a?")

@clq.fn
def return_sub(x):
    return x
return_sub = return_sub.compile(OpenCL, sub_type)
assert return_sub.return_type == sub_type

@clq.fn
def return_super(a, b, return_sub):
    return return_sub(b) + a
return_super = return_super.compile(OpenCL, super_type, sub_type, return_sub.cl_type)
assert return_super.return_type == super_type
 
@clq.fn
def fail_check(a, return_sub):
    return return_sub(a) + a
try: 
    fail_check = fail_check.compile(OpenCL, super_type, return_sub.cl_type) #this should not typecheck!
    fail_check.return_type #force resolution
    assert False
except clq.TypeResolutionError:
    assert True
