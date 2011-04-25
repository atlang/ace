import numpy
import numpy.linalg as la
import cl
import cl.oquence

a = numpy.random.rand(50000).astype(numpy.float32)
b = numpy.random.rand(50000).astype(numpy.float32)

@cl.oquence.fn
def ew_add(a, b, dest):
    gid = get_global_id(0)
    dest[gid] = a[gid] + b[gid]
    
ctx = cl.ctx = cl.Context.for_device(0, 0)
a_buf = ctx.to_device(a)
b_buf = ctx.to_device(b)
dest_buf = ctx.alloc(like=a)

ew_add(a_buf, b_buf, dest_buf, global_size=a.shape, local_size=(1,)).wait()

c = ctx.from_device(dest_buf)

print la.norm(c - (a + b))
