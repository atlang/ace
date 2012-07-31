import clq
import clq.backends.opencl as ocl

OpenCL = ocl.Backend()

@clq.fn
def plus(a, b):
    return a + b

plus_ii = plus.compile(OpenCL, ocl.int, ocl.int)

@clq.fn
def plus3(a, b, c, plus):
    return plus(plus(a, b), c)

plus3_ii = plus3.compile(OpenCL, ocl.int, ocl.int, ocl.int, plus.cl_type)

print plus_ii.program_item.code
print plus3_ii.program_item.code

for item in plus3_ii.program_items:
    print item.code
