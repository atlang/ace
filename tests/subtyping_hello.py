import clq
import clq.extensions
import clq.backends.opencl as ocl
import clq.extensions.language_types as lang #the regex types extension.
OpenCL = ocl.Backend()

#TEST: Memoizing Language based on regular expression equivalence
L1 = lang.ConstrainedString(OpenCL, "(.?)+")
L2 = lang.ConstrainedString(OpenCL, ".*")
assert L1 == L2

assert L1.is_subtype(L2)
assert L2.is_subtype(L1)
L3 = lang.ConstrainedString(OpenCL, ".?")
assert L1 != L3
subtype_of_l1 = lang.ConstrainedString(OpenCL, ".+")
assert subtype_of_l1 != L1

#TODO test to make sure memoizing is backend-specific.

#TEST: Reflection and grammar inclusion
L1 = lang.ConstrainedString(OpenCL,".")
L2 = lang.ConstrainedString(OpenCL,".+")
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
L3 = lang.ConstrainedString(OpenCL, L1._regex)
test2 = test.compile(OpenCL, L3)
assert test2.return_type == L3

#TEST: Language factor interning. This fails b/c interning isn't working yet.
@clq.fn
def test2(a):
    return a
test2 = test2.compile(OpenCL, lang.ConstrainedString(OpenCL, L1._regex))
assert test2.return_type == L1



# Note: rhs + lhs for Language types has type 
# Language<(rhs._regex)(lhs._regex)> and requires rhs <: lhs 
# The subtyping requirement is somewhat arbitrary.

#TEST: Return type of concatenation
sub = lang.ConstrainedString(OpenCL, ".")
super = lang.ConstrainedString(OpenCL, ".+")
@clq.fn
def test_concatenation(a,b):
    return a + b
test_concatenation = test_concatenation.compile(OpenCL, super, sub)
assert test_concatenation.return_type == lang.ConstrainedString(OpenCL,"..+")  

#TEST: Subtyping
super_type = lang.ConstrainedString(OpenCL, "a+")
sub_type   = lang.ConstrainedString(OpenCL, "a")

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
return_super = return_super.compile(OpenCL, 
                                    super_type, 
                                    sub_type, 
                                    return_sub.cl_type)
assert return_super.return_type == lang.ConstrainedString(OpenCL, "aa+")

# The example below fails because the lhs must be a subtype of the rhs.
@clq.fn
def fail_check(a, return_sub):
    return return_sub(a) + a
try: 
    fail_check = fail_check.compile(OpenCL, super_type, return_sub.cl_type)
    fail_check.return_type #force resolution
    assert False
except clq.TypeResolutionError:
    assert True


# TEST:  Casting
@clq.fn
def upcast(a,b):
    return cast(a,b)
upcast = upcast.compile(OpenCL, sub_type, super_type)
assert upcast.return_type == super_type

#@clq.fn
#def downcast(a,b):
#    return cast(a,b)
#downcast = downcast.compile(OpenCL, super_type, sub_type)
#assert downcast.return_type == sub_type

@clq.fn
def impossiblecast(a,b):
    return cast(a,b)
try:
    impossiblecast = impossiblecast.compile(OpenCL, super_type, ocl.int)
    print impossiblecast.program_item.code
    assert False
except clq.CodeGenerationError as e:
    assert True #should fail b/c ocl.int doesn't support runtime cast checks.


#this is always a downcast, so there should always be a check.
#@clq.fn
#def topcast(a):
#    return cast("some user input",a)
#topcast = topcast.compile(OpenCL, super_type)
#assert topcast.return_type == super_type

#print topcast.program_item.code

#This is always an upcast, so there should never be a check.
@clq.fn
def bottomcast(a):
    return cast(a, "string") #how to use a type variable here?
bottomcast = bottomcast.compile(OpenCL, super_type)
assert bottomcast.return_type == ocl.string

# FAIL; something's wrong with resolve_Assign.
#@clq.fn
#def assign(a,b):
#    a = b
#    return a
#try:
#    assign_if = assign.compile(OpenCL, super_type, return_sub.cl_type)
#    #should result in an error; assigning a supertype to a subtype.
#    assign_if.return_type 
#    assert False
#    #assert ocl.float.is_subtype(ocl.int)
#except clq.TypeResolutionError:
#    assert True