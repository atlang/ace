import pyopencl as cl 
import cypy.cg
import numpy

op_pairs = {
    ('uchar', 'uchar'): 'uint',
    ('uchar', 'char'): 'uint',
    ('uchar', 'ushort'): 'uint',
    ('uchar', 'short'): 'uint',
    ('uchar', 'uint'): 'uint',
    ('uchar', 'int'): 'uint',
    ('uchar', 'ulong'): 'uint',
    ('uchar', 'long'): 'ulong',
    ('uchar', 'half'): 'float',
    ('uchar', 'float'): 'float',
    ('uchar', 'double'): 'double',
    ('uchar', 'uintptr_t'): 'uintptr_t',
    ('uchar', 'intptr_t'): 'uintptr_t',
    ('uchar', 'size_t'): 'size_t',
    ('uchar', 'ptrdiff_t'): 'size_t',
    
    ('char', 'uchar'): 'uint',
    ('char', 'char'): 'int',
    ('char', 'ushort'): 'uint',
    ('char', 'short'): 'int',
    ('char', 'uint'): 'uint',
    ('char', 'int'): 'int',
    ('char', 'ulong'): 'ulong',
    ('char', 'long'): 'long',
    ('char', 'half'): 'float',
    ('char', 'float'): 'float',
    ('char', 'double'): 'double',
    ('char', 'uintptr_t'): 'uintptr_t',
    ('char', 'intptr_t'): 'intptr_t',
    ('char', 'size_t'): 'size_t',
    ('char', 'ptrdiff_t'): 'ptrdiff_t',
    
    ('ushort', 'uchar'): 'uint',
    ('ushort', 'char'): 'uint',
    ('ushort', 'ushort'): 'uint',
    ('ushort', 'short'): 'uint',
    ('ushort', 'uint'): 'uint',
    ('ushort', 'int'): 'uint',
    ('ushort', 'ulong'): 'uint',
    ('ushort', 'long'): 'ulong',
    ('ushort', 'half'): 'float',
    ('ushort', 'float'): 'float',
    ('ushort', 'double'): 'double',
    ('ushort', 'uintptr_t'): 'uintptr_t',
    ('ushort', 'intptr_t'): 'uintptr_t',
    ('ushort', 'size_t'): 'size_t',
    ('ushort', 'ptrdiff_t'): 'size_t',
    
    ('short', 'uchar'): 'uint',
    ('short', 'char'): 'int',
    ('short', 'ushort'): 'uint',
    ('short', 'short'): 'int',
    ('short', 'uint'): 'uint',
    ('short', 'int'): 'int',
    ('short', 'ulong'): 'ulong',
    ('short', 'long'): 'long',
    ('short', 'half'): 'float',
    ('short', 'float'): 'float',
    ('short', 'double'): 'double',
    ('short', 'uintptr_t'): 'uintptr_t',
    ('short', 'intptr_t'): 'intptr_t',
    ('short', 'size_t'): 'size_t',
    ('short', 'ptrdiff_t'): 'ptrdiff_t',
    
    ('uint', 'uchar'): 'uint',
    ('uint', 'char'): 'uint',
    ('uint', 'ushort'): 'uint',
    ('uint', 'short'): 'uint',
    ('uint', 'uint'): 'uint',
    ('uint', 'int'): 'uint',
    ('uint', 'ulong'): 'ulong',
    ('uint', 'long'): 'ulong',
    ('uint', 'half'): 'float',
    ('uint', 'float'): 'float',
    ('uint', 'double'): 'double',
    ('uint', 'uintptr_t'): 'uintptr_t',
    ('uint', 'intptr_t'): 'uintptr_t',
    ('uint', 'size_t'): 'size_t',
    ('uint', 'ptrdiff_t'): 'size_t',
    
    ('int', 'uchar'): 'uint',
    ('int', 'char'): 'int',
    ('int', 'ushort'): 'uint',
    ('int', 'short'): 'int',
    ('int', 'uint'): 'uint',
    ('int', 'int'): 'int',
    ('int', 'ulong'): 'ulong',
    ('int', 'long'): 'long',
    ('int', 'half'): 'float',
    ('int', 'float'): 'float',
    ('int', 'double'): 'double',
    ('int', 'uintptr_t'): 'uintptr_t',
    ('int', 'intptr_t'): 'intptr_t',
    ('int', 'size_t'): 'size_t',
    ('int', 'ptrdiff_t'): 'ptrdiff_t',
    
    ('ulong', 'uchar'): 'ulong',
    ('ulong', 'char'): 'ulong',
    ('ulong', 'ushort'): 'ulong',
    ('ulong', 'short'): 'ulong',
    ('ulong', 'uint'): 'ulong',
    ('ulong', 'int'): 'ulong',
    ('ulong', 'ulong'): 'ulong',
    ('ulong', 'long'): 'ulong',
    ('ulong', 'half'): None,
    ('ulong', 'float'): 'float',
    ('ulong', 'double'): 'double',
    ('ulong', 'uintptr_t'): 'ulong',
    ('ulong', 'intptr_t'): 'ulong',
    ('ulong', 'size_t'): 'ulong',
    ('ulong', 'ptrdiff_t'): 'ulong',
    
    ('long', 'uchar'): 'ulong',
    ('long', 'char'): 'long',
    ('long', 'ushort'): 'ulong',
    ('long', 'short'): 'long',
    ('long', 'uint'): 'ulong',
    ('long', 'int'): 'long',
    ('long', 'ulong'): 'ulong',
    ('long', 'long'): 'long',
    ('long', 'half'): None,
    ('long', 'float'): 'float',
    ('long', 'double'): 'double',
    ('long', 'uintptr_t'): 'ulong',
    ('long', 'intptr_t'): 'long',
    ('long', 'size_t'): 'ulong',
    ('long', 'ptrdiff_t'): 'long',
    
    ('half', 'uchar'): 'float',
    ('half', 'char'): 'float',
    ('half', 'ushort'): 'float',
    ('half', 'short'): 'float',
    ('half', 'uint'): 'float',
    ('half', 'int'): 'float',
    ('half', 'ulong'): None,
    ('half', 'long'): None,
    ('half', 'half'): 'float',
    ('half', 'float'): 'float',
    ('half', 'double'): 'double',
    ('half', 'uintptr_t'): None,
    ('half', 'intptr_t'): None,
    ('half', 'size_t'): None,
    ('half', 'ptrdiff_t'): None,
    
    ('float', 'uchar'): 'float',
    ('float', 'char'): 'float',
    ('float', 'ushort'): 'float',
    ('float', 'short'): 'float',
    ('float', 'uint'): 'float',
    ('float', 'int'): 'float',
    ('float', 'ulong'): 'float',
    ('float', 'long'): 'float',
    ('float', 'half'): 'float',
    ('float', 'float'): 'float',
    ('float', 'double'): 'double',
    ('float', 'uintptr_t'): 'float',
    ('float', 'intptr_t'): 'float',
    ('float', 'size_t'): 'float',
    ('float', 'ptrdiff_t'): 'float',
        
    ('double', 'uchar'): 'double',
    ('double', 'char'): 'double',
    ('double', 'ushort'): 'double',
    ('double', 'short'): 'double',
    ('double', 'uint'): 'double',
    ('double', 'int'): 'double',
    ('double', 'ulong'): 'double',
    ('double', 'long'): 'double',
    ('double', 'half'): 'double',
    ('double', 'float'): 'double',
    ('double', 'double'): 'double',
    ('double', 'uintptr_t'): 'double',
    ('double', 'intptr_t'): 'double',
    ('double', 'size_t'): 'double',
    ('double', 'ptrdiff_t'): 'double',
    
    ('uintptr_t', 'uchar'): 'uintptr_t',
    ('uintptr_t', 'char'): 'uintptr_t',
    ('uintptr_t', 'ushort'): 'uintptr_t',
    ('uintptr_t', 'short'): 'uintptr_t',
    ('uintptr_t', 'uint'): 'uintptr_t',
    ('uintptr_t', 'int'): 'uintptr_t',
    ('uintptr_t', 'ulong'): 'ulong',
    ('uintptr_t', 'long'): 'ulong',
    ('uintptr_t', 'half'): None,
    ('uintptr_t', 'float'): 'float',
    ('uintptr_t', 'double'): 'double',
    ('uintptr_t', 'uintptr_t'): 'uintptr_t',
    ('uintptr_t', 'intptr_t'): 'uintptr_t',
    ('uintptr_t', 'size_t'): 'uintptr_t',   
    ('uintptr_t', 'ptrdiff_t'): 'uintptr_t',
    
    ('intptr_t', 'uchar'): 'uintptr_t',
    ('intptr_t', 'char'): 'intptr_t',
    ('intptr_t', 'ushort'): 'uintptr_t',
    ('intptr_t', 'short'): 'intptr_t',
    ('intptr_t', 'uint'): 'uintptr_t',
    ('intptr_t', 'int'): 'intptr_t',
    ('intptr_t', 'ulong'): 'ulong',
    ('intptr_t', 'long'): 'long',
    ('intptr_t', 'half'): None,
    ('intptr_t', 'float'): 'float',
    ('intptr_t', 'double'): 'double',
    ('intptr_t', 'uintptr_t'): 'uintptr_t',
    ('intptr_t', 'intptr_t'): 'intptr_t',
    ('intptr_t', 'size_t'): 'uintptr_t',
    ('intptr_t', 'ptrdiff_t'): 'intptr_t',
    
    ('size_t', 'uchar'): 'size_t',
    ('size_t', 'char'): 'size_t',
    ('size_t', 'ushort'): 'size_t',
    ('size_t', 'short'): 'size_t',
    ('size_t', 'uint'): 'size_t',
    ('size_t', 'int'): 'size_t',
    ('size_t', 'ulong'): 'ulong',
    ('size_t', 'long'): 'ulong',
    ('size_t', 'half'): None,
    ('size_t', 'float'): 'float',
    ('size_t', 'double'): 'double',
    ('size_t', 'uintptr_t'): 'uintptr_t',
    ('size_t', 'intptr_t'): 'uintptr_t',
    ('size_t', 'size_t'): 'size_t',   
    ('size_t', 'ptrdiff_t'): 'size_t',
    
    ('ptrdiff_t', 'uchar'): 'size_t',
    ('ptrdiff_t', 'char'): 'ptrdiff_t',
    ('ptrdiff_t', 'ushort'): 'size_t',
    ('ptrdiff_t', 'short'): 'ptrdiff_t',
    ('ptrdiff_t', 'uint'): 'size_t',
    ('ptrdiff_t', 'int'): 'ptrdiff_t',
    ('ptrdiff_t', 'ulong'): 'ulong',
    ('ptrdiff_t', 'long'): 'long',
    ('ptrdiff_t', 'half'): None,
    ('ptrdiff_t', 'float'): 'float',
    ('ptrdiff_t', 'double'): 'double',
    ('ptrdiff_t', 'uintptr_t'): 'uintptr_t',
    ('ptrdiff_t', 'intptr_t'): 'intptr_t',
    ('ptrdiff_t', 'size_t'): 'size_t',   
    ('ptrdiff_t', 'ptrdiff_t'): 'ptrdiff_t',
}

types = ("uchar", "char",
         "ushort", "short",
         "uint", "int",
         "ulong", "long",
         "uintptr_t", "intptr_t",
         "size_t", "ptrdiff_t",
         "half", "float", "double")

g = cypy.cg.CG()
"""
__kernel void test_sizeof(__global int* out) {
#pragma extension cl_khr_fp64 : enable
#pragma extension cl_khr_fp16 : enable

""" << g

i = 0
items = op_pairs.items()
for (type_left, type_right), out_type in items:
        ("""
        out[%(i)s] = sizeof(((%(type_left)s)0)+((%(type_right)s)0));
        """ % {'i': i, 'type_left': type_left, 'type_right': type_right}) << g
        i += 1
"""
}
""" << g 
code = g.code
print code

ctx = cl.Context([cl.get_platforms()[0].get_devices()[1]])
queue = cl.CommandQueue(ctx)

prg = cl.Program(ctx, code).build()

mf = cl.mem_flags
out_buf = cl.Buffer(ctx, mf.WRITE_ONLY, len(types)*len(types)*4)

prg.test_sizeof(queue, (1,),
     None, out_buf)

out = numpy.empty((len(types)*len(types),
    ),
     dtype=numpy.int32)
cl.enqueue_read_buffer(queue, out_buf, out)

print dict(
    ((type_left, type_right),
     (out_type, out[i])) for \
    i, ((type_left, type_right),
     out_type) in \
    enumerate(items)
)

#
#prg = cl.Program(ctx, 
#"""
#__kernel void test_sizeof(__global int* out) {
#    out[
#    out[0] = sizeof((char)0);
#}
#""").build()
#
#ctx = cl.create_some_context()
#queue = cl.CommandQueue(ctx)
#
#mf = cl.mem_flags
#out_buf = cl.Buffer(ctx, mf.WRITE_ONLY, 4)
#
#
#ctx = cl.create_some_context()
#queue = cl.CommandQueue(ctx)
#
#mf = cl.mem_flags
#a_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
#b_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b)
#dest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, b.nbytes)
#
#prg = cl.Program(ctx, """
#    __kernel void sum(__global const float *a,
#    __global const float *b, __global float *c)
#    {
#      int gid = get_global_id(0);
#      c[gid] = a[gid] + b[gid];
#    }
#    """).build()
#
#prg.sum(queue, a.shape, None, a_buf, b_buf, dest_buf)

