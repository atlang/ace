import clq
import clq.backends.opencl as ocl

OpenCL = ocl.Backend()

@clq.fn
def plus(a, b):
    return a + b

plus_ii = plus.compile(OpenCL, ocl.int, ocl.int)

print plus_ii.program_item.code
