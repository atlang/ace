import clq
import clq.extensions
import clq.backends.opencl as ocl
import clq.extensions.language_types as lang #the regex types extension.
OpenCL = ocl.Backend()

#These tests all work, except for a weird error possibly due to 
#the way that language types are being stored.
#commenting out this function declaration makes L1==L2 (as it should.)
def test_concatenation(a,b):
    pass


#TEST: Memoizing Language based on regular expression equivalence
L1 = lang.Language.factory(OpenCL, "(.?)+")
L2 = lang.Language.factory(OpenCL, ".*")
assert L1 == L2


#assert L1.is_subtype(L2)
#assert L2.is_subtype(L1)
#L3 = lang.Language.factory(OpenCL, ".?")
#assert L1 != L3
#subtype_of_l1 = lang.Language.factory(OpenCL, ".+")
#assert subtype_of_l1 != L1
#
##TODO test to make sure memoizing is backend-specific.
#
##TEST: Reflection and grammar inclusion
#L1 = lang.Language.factory(OpenCL,".")
#L2 = lang.Language.factory(OpenCL,".+")
#assert L1 != L2
#assert L1.is_subtype(L1)
#assert L2.is_subtype(L2)
#assert L2.is_subtype(L1)


#@clq.fn
#def test_return(a):
#    return a
#test_return = test_return.compile(OpenCL, L1)
#assert test_return.return_type == L1



#r_type = lang.Language.factory(OpenCL, ".")
#l_type = lang.Language.factory(OpenCL, ".+")
#@clq.fn
#def test_concatenation(a,b):
#    return a + b
#test_concatenation = test_concatenation.compile(OpenCL, r_type, l_type)
#assert test_concatenation.return_type == lang.Language.factory(OpenCL,"..+")

##TEST: Function returning a Language
#@clq.fn
#def test(a):
#    return a
#test1 = test.compile(OpenCL,  L1)
#assert test1.return_type == L1
#L3 = lang.Language.factory(OpenCL, L1._regex)
#test2 = test.compile(OpenCL, L3)
#assert test2.return_type == L3
#
###TEST: Language factor interning. This fails b/c interning isn't working yet.
##L1 = lang.Language.factory(OpenCL,"a")
##L2 = lang.Language.factory(OpenCL,"a+")
#@clq.fn
#def test2(a):
#    return a
#test2 = test2.compile(OpenCL, lang.Language.factory(OpenCL, L1._regex))
#assert test2.return_type == L1


##TEST: Subtyping
#super_type = lang.Language.factory(OpenCL, "a+b")
#sub_type   = lang.Language.factory(OpenCL, "a")
#
#@clq.fn
#def return_sub(x):
#    return x
#return_sub = return_sub.compile(OpenCL, sub_type)
#assert return_sub.return_type == sub_type
#
#@clq.fn
#def return_super(a, return_sub):
#    return a + return_sub(a) #Because a is left-hand, the type of a should be preserved.
#return_super = return_super.compile(OpenCL, super_type, return_sub.cl_type)
#assert return_super.return_type == super_type
# 
#@clq.fn
#def fail_check(a, return_sub):
#    return return_sub(a) + a
#try: 
#    return_sub2 = return_sub2.compile(OpenCL, super_type, return_sub.cl_type) #this should not typecheck!
#    assert False
#except Exception:
#    assert True
