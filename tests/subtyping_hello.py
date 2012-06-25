import clq
import clq.extensions
import clq.backends.opencl as ocl
import clq.extensions.language_types as lang #the regex types extension.
OpenCL = ocl.Backend()

#TEST: Memoizing Language based on regular expression equivalence
L1 = lang.ConstrainedString.factory(OpenCL, "(.?)+")
L2 = lang.ConstrainedString.factory(OpenCL, ".*")
assert L1 == L2

assert L1.is_subtype(L2)
assert L2.is_subtype(L1)
L3 = lang.ConstrainedString.factory(OpenCL, ".?")
assert L1 != L3
subtype_of_l1 = lang.ConstrainedString.factory(OpenCL, ".+")
assert subtype_of_l1 != L1

#TODO test to make sure memoizing is backend-specific.

#TEST: Reflection and grammar inclusion
L1 = lang.ConstrainedString.factory(OpenCL,".")
L2 = lang.ConstrainedString.factory(OpenCL,".+")
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
L3 = lang.ConstrainedString.factory(OpenCL, L1._regex)
test2 = test.compile(OpenCL, L3)
assert test2.return_type == L3

#TEST: Language factor interning. This fails b/c interning isn't working yet.
@clq.fn
def test2(a):
    return a
test2 = test2.compile(OpenCL, lang.ConstrainedString.factory(OpenCL, L1._regex))
assert test2.return_type == L1



## Note: rhs + lhs for Language types has type Language<(rhs._regex)(lhs._regex)> and requires rhs <: lhs 
## The subtyping requirement is somewhat arbitrary.

#TEST: Return type of concatenation
sub = lang.ConstrainedString.factory(OpenCL, ".")
super = lang.ConstrainedString.factory(OpenCL, ".+")
@clq.fn
def test_concatenation(a,b):
    return a + b
test_concatenation = test_concatenation.compile(OpenCL, super, sub)
assert test_concatenation.return_type == lang.ConstrainedString.factory(OpenCL,"..+")  

#TEST: Subtyping
super_type = lang.ConstrainedString.factory(OpenCL, "a+b")
sub_type   = lang.ConstrainedString.factory(OpenCL, "a")

@clq.fn
def return_sub(x):
    return x
return_sub = return_sub.compile(OpenCL, sub_type)
assert return_sub.return_type == sub_type

@clq.fn
def assign_to_sub(x,y):
    x = y
    return x
assign_to_sub = assign_to_sub.compile(OpenCL, super_type, sub_type)
assert assign_to_sub.return_type == super_type

@clq.fn
def return_super(a, b, return_sub):
    return return_sub(b) + a
return_super = return_super.compile(OpenCL, super_type, sub_type, return_sub.cl_type)
assert return_super.return_type == lang.ConstrainedString   .factory(OpenCL, "aa+b")
print return_super.program_item.code

#The example below fails because the lhs must be a subtype of the rhs.
@clq.fn
def fail_check(a, return_sub):
    return return_sub(a) + a
try: 
    fail_check = fail_check.compile(OpenCL, super_type, return_sub.cl_type)
    fail_check.return_type #force resolution
    assert False
except clq.TypeResolutionError:
    assert True

# The failure of this test is unrelated to subtyping, but is an error in Ace's typing that came up while
# testing subtyping:
#@clq.fn
#def assign(a,b):
#    a = b
#    return a
#try:
#    assign_if = assign.compile(OpenCL, ocl.int, ocl.float)
#    assign_if.return_type #should result in an error; assigning a flaot to an int.
#    assert ocl.float.is_subtype(ocl.int)
#except clq.TypeResolutionError:
#    assert True