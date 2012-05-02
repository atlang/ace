# TODO: License header
# TODO: Module documentation

import cypy
import numpy as _numpy
import pyopencl as _cl
from pyopencl import * #@UnusedWildImport

class Error(Error): 
    """Base class for errors in ``cl.oquence.pyopencl``. 
    
    Extends :class:`pyopencl.Error`.
    """
    pass

#############################################################################
## Platform
#############################################################################
class Platform(Platform):
    """An OpenCL platform.
    
    In OpenCL, a platform consists of the compilers and other tools that 
    implement the OpenCL interface. For example, on OS X 10.6+, the `Apple` 
    platform implements OpenCL for all GPUs and CPUs that Apple computers 
    support. On other systems, NVidia, AMD, Intel, IBM and others provide 
    platforms that support their respective devices.
    """
    @classmethod
    def get_platforms(cls):
        """Returns a tuple of available platforms on this system."""
        return tuple(_cl.get_platforms())
            
    @classmethod
    def print_list(cls):
        """Prints a numbered list of available platforms on this system."""
        platforms = cls.get_platforms()
        for i, pf in enumerate(platforms):
            print "[%d] %s" % (i, pf)
            
    @classmethod
    def get(cls, idx=None):
        """Returns the platform instance with the provided index.

        If provided an instance of Platform, returns it. Otherwise, raises an 
        :class:`Error`.
        """
        if hasattr(idx, 'get_devices'): # Already a Platform
            return idx
        elif cypy.is_numeric(idx):
            return cls.get_platforms()[idx]
        else:
            raise Error("Invalid idx provided to Platform.get.")
            
    @classmethod
    def get_somehow(cls, interactive=True):
        """Returns a Platform instance somehow.

        - If ``interactive``, prompts on stdin.
        - If not, returns a Platform in an implementation-defined manner (at
          the moment, just the 0th indexed Platform.)
        
        """
        return cls.get(cls.get_idx_somehow(interactive))
        
    @classmethod
    def get_idx_somehow(cls, interactive=True):
        """Returns a platform index somehow. See :meth:`get_somehow`."""
        platforms = cls.get_platforms()
        n_platforms = len(platforms)
        if n_platforms == 0:
            raise Error("No OpenCL platforms available.")
        elif n_platforms == 1 or not interactive:
            platform_idx = 0
        else:
            print "Please choose a platform:"
            cls.print_list(platforms)
            platform_idx = raw_input("[0]: ")
            if not platform_idx:
                platform_idx = 0
            else:
                platform_idx = int(platform_idx)
        return platform_idx
        
    @property
    def devices(self):
        """A tuple of Devices available for this Platform."""
        return tuple(self.get_devices(device_type.ALL))
    
    # adding properties doesn't seem to work on derived classes due to 
    # how boost creates these wrappers, so workaround:
    _cl.Platform.devices = devices  
_cl.Platform = Platform

#############################################################################
## Device
#############################################################################
class Device(Device):
    """Represents a single OpenCL-capable device."""
    
    @classmethod
    def print_list(cls, platform=None):
        """Prints a numbered list of available devices.

        - If ``platform`` is a platform index or Platform instance, prints 
          only devices for that platform.
        - Otherwise, prints all devices for all platforms, grouped by 
          Platform.

        """
        if platform is None:
            for i, platform in enumerate(Platform.get_platforms()):
                print "Platform [%d]: %s" % (i, str(platform))
                platform.print_list()
        else:
            platform = Platform.get(platform)
            devices = platform.get_devices()
            if len(devices) == 0:
                print "No devices available."
            else:
                for i, device in enumerate(devices):
                    print "[%d] %s" % (i, str(device))
                    
    @classmethod
    def get(cls, idx, platform):
        """Returns the device with the provided index in the provided platform.

        ``platform`` can be a platform index or Platform instance.
        """
        return Platform.get(platform).devices[idx]
        
    @classmethod
    def get_somehow(cls, interactive=True, platform=None):
        """Returns a Device instance somehow.

        - If ``interactive``, prompts on stdin.
        - If not, returns a Device in a heuristic manner (at the moment, just 
          the 0th index Device in the provided Platform, or in the default 
          Platform if not specified.)
        """
        return cls.get(*cls.get_idx_somehow(interactive, platform))
        
    @classmethod
    def get_idx_somehow(cls, interactive=True, platform=None):
        """Returns a tuple (device index, platform instance) somehow.

        - If ``interactive``, prompts on stdin.
        - If not, returns indices in a heuristic manner (at the moment, 
          just the 0th index of the provided platform, or the default Platform
          if not specified.)
        """
        if platform is None:
            platform = Platform.get_somehow(interactive)
        else:
            platform = platform.get(platform)

        devices = platform.get_devices()
        n_devices = len(devices)
        if n_devices == 0:
            raise Error("No devices available.")
        elif n_devices == 1:
            return devices[0]
        else:
            print "Please choose a device:"
            cls.print_list(platform)
            device_idx = raw_input("[0]: ")
            if not device_idx: return (0, platform)
            else: return (int(device_idx), platform)
            
    @property
    def max_work_items(self):
        """Returns the maximum number of work items that can be enqueued on 
        this device.
        """
        return cypy.prod(self.max_work_item_sizes)
    
    _cl.Device.max_work_items = max_work_items 
    
_cl.Device = Device

#############################################################################
## Context
#############################################################################
_orig__init_Context = _cl.Context.__init__
class Context(Context):
    """Represents an OpenCL context."""
    def __init__(self, devices=None, properties=None, dev_type=None):
        _orig__init_Context(self, devices, properties, dev_type)
        self.devices = devices
        self.properties = properties
        self.dev_type = dev_type
        
    @classmethod
    def get_somehow(cls, interactive=True, platform=None):
        """Creates an instance of :class:`Context` bound to one device, somehow.

        See :meth:`Device.get_somehow`.
        """
        device = Device.get_somehow(interactive, platform)
        return cls((device,))
        
    @classmethod
    def for_device(cls, device_idx, platform):
        """Creates an instance of Context for the specified device and platform.

        ``platform`` can be a Platform instance or index.
        """
        device = Device.get(device_idx, Platform.get(platform))
        return cls((device,))
        
    @property
    def queue(self):
        """Provides a default CommandQueue for this context.
        
        If multiple devices are bound to the Context, raises an 
        :class:`Error`.
        
        """
        if self._queue is None:
            self._queue = CommandQueue(self, self.device)
        return self._queue
    _queue = None
    
    @property
    def device(self):
        """Returns the device bound to this Context.

        If multiple devices are bound to the Context, raises an 
        :class:`Error`.
        
        """
        if len(self.devices) > 1:
            raise Error("Multiple devices bound to Context.")
        return self.devices[0]
        
    def alloc(self, shape=None, cl_dtype=None, order="C", 
              like=None, flags=mem_flags.READ_WRITE):
        """Allocates an uninitialized :class:`Buffer` with provided metadata.

        ``shape``, ``cl_dtype`` and ``order``
            See :class:`Buffer` for descriptions of these. 
            
        ``like``
            If ``like`` is specified, any of the parameters ``shape``, 
            ``cl_dtype`` or ``order`` that are not explicitly specified are 
            taken from the referenced array or Buffer.
            
        ``flags``
            One or more :class:`mem_flags`. Defaults to 
            ``mem_flags.READ_WRITE``.            
        """
        if cypy.is_int_like(shape):
            shape = (shape,)
        elif shape is None:
            shape = Buffer.infer_shape(like)
            
        if cl_dtype is None:
            if like is None:
                cl_dtype = cl_float
            else:
                cl_dtype = Buffer.infer_cl_dtype(like)
                
        if order is None:
            if like is None:
                order = "C"
            else:
                order = Buffer.infer_order(like)

        return Buffer.shaped(self, shape, cl_dtype, order, flags)

    def copy(self, src, dest, block=True, wait_for=None, queue=None):
        """Copies the ``src`` buffer/array to the ``dest`` buffer/array.

        Supports host-device, device-host and device-device copies. Host-host
        memory copies are not currently supported (use numpy's methods.)

        ``block``
            If True, does not return until the transfer is complete.
            
        ``wait_for``
            A list of :class:`Event` instances to block on before copying, or
            None.

        ``queue``
            The :class:`CommandQueue` to issue the copy command over. If not
            specified, uses the Context's default queue.
            
        Returns an :class:`Event` instance.        
        """
        if queue is None:
            queue = self.queue
            
        if isinstance(dest, Buffer):
            if isinstance(src, Buffer):
                # device to device
                event = enqueue_copy_buffer(queue, src, dest, 
                                            wait_for=wait_for,
                                            is_blocking=block)
            else:
                # host to device
                event = enqueue_write_buffer(queue, dest, src, 
                                             wait_for=wait_for, 
                                             is_blocking=block)
        else:
            if isinstance(src, Buffer):
                # device to host
                event = enqueue_read_buffer(queue, src, dest,
                                            wait_for=wait_for,
                                            is_blocking=block)
            else:
                # host to host
                raise NotImplementedError(
                    "Host to host transfers are not currently supported.")
                
        if block: event.wait()
        
        return event
    
    def to_device(self, src, flags=mem_flags.READ_WRITE, wait_for=None, 
                  queue=None):
        """Copies the src array to a new :class:`Buffer` synchronously."""
        buffer = self.alloc(like=src, flags=flags)
        self.copy(src, buffer, block=True, wait_for=wait_for, queue=queue).wait()
        return buffer

    def from_device(self, src, shape=None, dtype=None, order=None, like=None,
                    wait_for=None, queue=None):
        """Copies the ``src`` buffer to a new array synchronously.

        If not explicitly specified, the ``shape``, ``dtype`` and ``order`` of
        the resulting array are inferred from the ``src`` buffer if possible, 
        or ``like`` if not.
        
        ``wait_for`` can be specified as a list of :class:`Event` instances to
        block on before copying.
        
        If ``queue`` is not specified, uses the default queue.
        """
        if cypy.is_int_like(shape):
            shape = (shape,)
        elif shape is None:
            try:
                shape = Buffer.infer_shape(src)
            except Error:
                shape = Buffer.infer_shape(like)

        if dtype is None:
            try:
                dtype = Buffer.infer_dtype(src)
            except Error:
                dtype = Buffer.infer_dtype(like)

        if order is None:
            try:
                order = Buffer.infer_order(src)
            except Error:
                try:
                    order = Buffer.infer_order(like)
                except:
                    order = "C"

        dest = _numpy.empty(shape, dtype, order=order)
        self.copy(src, dest, block=True, wait_for=wait_for, queue=queue).wait()
        return dest

    def In(self, src):
        """Copies the provided ``src`` host buffer to the device for read-only
        access."""
        return self.to_device(src, mem_flags.READ_ONLY)

    def Out(self, dest):
        """Allocates an empty device buffer on the device for writing only, and 
        copies the result into the provided host buffer ``dest`` after each 
        kernel call to which it is passed."""
        return _Out(self, dest)

    def InOut(self, src):
        """:meth:`In` and :meth:`Out` combined."""
        return _InOut(self, src)
    
    def compile(self, source, options=""):
        """Returns a Program built from the provided ``source``.
        
        The compiler options can be provided as a single string or a sequence 
        of strings.
        """
        if cypy.is_iterable(options):
            options = " ".join(options)
        return Program(self, source).build(options)
_cl.Context = Context

ctx = None
"""The process-wide default context to use. None until set explicitly."""

def _Out(ctx, dest):
    buffer = ctx.alloc(flags=mem_flags.WRITE_ONLY, like=dest)
    buffer.post_kernel_hook = _Out_post_kernel_hook
    buffer._dest = dest
    return buffer

def _InOut(ctx, src):
    buffer = ctx.to_device(src)
    buffer.post_kernel_hook = _Out_post_kernel_hook
    buffer._dest = src
    return buffer

def _Out_post_kernel_hook(context, buffer, event):
    event.wait()
    context.copy(buffer, buffer._dest, block=True)

#############################################################################
## Memory Objects
#############################################################################
_orig__init_Buffer = _cl.Buffer.__init__
class Buffer(Buffer):
    """Represents a buffer in global memory."""
    def __init__(self, context, flags, size=0, hostbuf=None):
        """Creates a Buffer without saving any metadata (pyopencl default.)"""
        _orig__init_Buffer(self, context, flags, size, hostbuf)
        self.context = context
        self.flags = flags
        self.size = size
        
    @classmethod
    def shaped(cls, ctx, shape=None, cl_dtype=None, order=None,
               flags=mem_flags.READ_WRITE, hostbuf=None, constant=False):
        """Creates a Buffer with shape, element type and order metadata.        
        
        - If ``hostbuf`` is provided, it will be synchronously copied to the 
          device.
        - If mem_flags.USE_HOST_PTR is not included and a ``hostbuf`` is 
          specified, it will be added automatically.
        - Metadata will be inferred from ``hostbuf`` if not explicitly provided.
    
        ``shape``
            If an int is provided, converted to a one-dimensional tuple. 
            Dimensions be positive integers (arr). 
    
        It is highly recommended that you use the methods available in
        :class:`Context` to create buffers rather than doing so explicitly.
        """
        if cypy.is_int_like(shape):
            shape = (shape,)
        if hostbuf is not None:
            if shape is None:
                shape = cls.infer_shape(hostbuf)
            if cl_dtype is None:
                cl_dtype = cls.infer_cl_dtype(hostbuf)
            if order is None:
                try:
                    order = cls.infer_order(hostbuf)
                except Error:
                    order = "C"
            flags |= mem_flags.USE_HOST_PTR
        size = cl_dtype.sizeof_for(ctx.device)
        size *= cypy.prod(shape)
        if size <= 0:
            raise Error("Invalid buffer size %s." % str(size))
        assert size > 0
        buffer = cls(ctx, flags, size, hostbuf)
        buffer.shape = shape
        buffer.cl_dtype = cl_dtype
        buffer.order = order
        buffer.constant = constant
        return buffer
    
    shape = None
    """A tuple specifying the dimensions of the memory object.
    
    See :class:`numpy.ndarray`.
    """

    def __len__(self):
        """The length of the memory object, including all dimensions."""
        return self.size/self.cl_dtype.sizeof_for(self.context.device)

    @cypy.lazy(property)
    def cl_type(self):
        """A :class:`GlobalPtrType` descriptor for this Buffer."""
        if self.constant:
            return self.cl_dtype.constant_ptr
        else:
            return self.cl_dtype.global_ptr

    cl_dtype = None
    """A :class:`Type` descriptor for the *elements* of the memory object."""
    
    order = "C"
    """The order of the dimensions of the array in memory.

    - If 'C' (default), the array will be in C-contiguous order (last-index
      varies the fastest,e.g. row-major order if the first dimension is
      thought of as rows.)

    - If 'F', the array will be in Fortran-contiguous order (first-index
      variest the fastest, e.g. column-major order if the first dimension is
      thought of as rows.)

    - If 'A', then the array may be in any order or even discontiguous. May
      not be fully supported.

    See :class:`numpy.array`.
    """
    
    constant = False
    """Whether to place this argument in constant memory when passed to a 
    cl.oquence function."""
    
    def from_device(self, wait_for=None, queue=None):
        """Retrieves this buffer from the device."""
        return self.context.from_device(self, wait_for=wait_for, queue=queue)
    
    def copy_from(self, src, block=True, wait_for=None, queue=None):
        """Copies from a src array or buffer to this buffer."""
        return self.context.copy(src, self, block=block, wait_for=wait_for, 
                                   queue=queue)
        
    def copy_to(self, dest, block=True, wait_for=None, queue=None):
        """Copies to a destination array or buffer from this buffer."""
        return self.context.copy(self, dest, block=block, wait_for=wait_for,
                                   queue=queue)
    
    @classmethod
    def infer_shape(cls, src):
        """Infers a shape from the provided Python object.
        
        - If ``src`` has a ``shape`` attribute, it is used.
        - If not, and it has a length, that is used.
        - Otherwise, an :class:`Error` is raised.
        
        """ 
        try:
            return src.shape
        except AttributeError:
            try:
                return (len(src),)
            except TypeError:
                raise Error("No shape can be inferred from src.")
            
    @classmethod
    def infer_cl_dtype(cls, src):
        """Attempts to infer a cl_dtype for the source buffer.
    
        If a ``cl_dtype`` attribute is defined, uses that. If not, but a 
        ``dtype`` is defined, uses :obj:`to_cl_type` to look it up.
    
        Raises an :class:`Error` if not able to infer a cl_dtype.
        """
        try:
            return src.cl_dtype
        except AttributeError:
            try:
                return to_cl_type[src.dtype]
            except (KeyError, AttributeError):
                raise Error("No cl_dtype can be inferred from src.")
    
    @classmethod
    def infer_dtype(cls, src):
        """Attempts to infer a numpy dtype corresponding to ``src``.
    
        If a ``dtype`` attribute is defined, uses that. If not, but a 
        ``cl_dtype`` is defined, uses its corresponding dtype.
    
        Raises an :class:`Error` if not able to infer a dtype.
        """
        try:
            return src.dtype
        except AttributeError:
            try:
                dtype = src.cl_dtype.dtype
                if dtype is not None:
                    return dtype
                else:
                    raise
            except AttributeError:
                raise Error("No dtype can be inferred from src.")

    @classmethod
    def infer_order(cls, src):
        """Attempts to infer an order corresponding to ``src``.
    
        Raises an :class:`Error` if not able to infer an order.
        """
        try:
            return src.order
        except AttributeError:
            try:
                if src.flags.c_contiguous:
                    return "C"
                elif src.flags.f_contiguous:
                    return "F"
                else:
                    return "A"
            except AttributeError:
                raise Error("No order can be inferred from src.")
_cl.Buffer = Buffer

class LocalMemory(LocalMemory):
    """Represents an allocation in local memory."""
    @classmethod
    def shaped(cls, ctx, shape, cl_dtype, order="C"):
        """Creates a LocalMemory instance with shape, type and order metadata.

        See :meth:`Buffer.shaped` for an explanation of the arguments.
        """
        size = cl_dtype.sizeof_for(ctx.device) * cypy.prod(shape)
        if size <= 0:
            raise Error("Invalid local memory size: %s." % str(size))
        local_mem = LocalMemory(size)
        local_mem.shape = shape
        local_mem.cl_dtype = cl_dtype
        local_mem.order = order
    
    shape = None
    """A tuple specifying the dimensions of the memory object.
    
    See :class:`numpy.ndarray`.
    """

    def __len__(self):
        """The length of the memory object, including all dimensions."""
        return self.size/self.cl_dtype.sizeof_for(self.context.device)

    cl_dtype = None
    """A :class:`Type` descriptor for the *elements* of the memory object."""
    
    @cypy.lazy(property)
    def cl_type(self):
        """Returns a :class:`LocalPtrType` descriptor for this object."""
        return self.cl_dtype.local_ptr    
        
    order = "C"
    """The order of the dimensions of the array in memory.

    - If 'C' (default), the array will be in C-contiguous order (last-index
      varies the fastest,e.g. row-major order if the first dimension is
      thought of as rows.)

    - If 'F', the array will be in Fortran-contiguous order (first-index
      variest the fastest, e.g. column-major order if the first dimension is
      thought of as rows.)

    - If 'A', then the array may be in any order or even discontiguous. May
      not be fully supported.

    See :class:`numpy.array`.
    """
_cl.LocalMemory = LocalMemory

#############################################################################
## Program
#############################################################################
_orig__init_Program = _cl.Program.__init__
class Program(Program):
    """Represents an OpenCL program."""
    def __init__(self, context, *args, **kwargs):
        _orig__init_Program(self, context, *args, **kwargs)
        self.context = context
_cl.Program = Program

#############################################################################
## Kernel
#############################################################################
_orig__init_Kernel = _cl.Kernel.__init__
_orig__call_Kernel = _cl.Kernel.__call__
class Kernel(Kernel):
    """Represents an OpenCL kernel."""
    
    def __init__(self, program, name):
        """Extended to save ``program``, ``name``, ``context`` and
        the default ``queue`` as attributes."""
        _orig__init_Kernel(self, program, name)
        self.program = program
        self.context = program.context
        self.queue = program.context.queue
        self.name = name

    def __call__(self, *args, **kwargs):
        """
        Extended to use the default queue if the first argument is
        not a :class:`CommandQueue` and the shape of the first kernel
        argument as the ``global_size`` if not explicitly specified.

        Also provides support for :meth:`Context.Out` and :meth:`Context.InOut`.
        
        Python ints and floats are converted to numpy ints and floats 
        automatically. The default floating point data type is ``float``, not
        ``double``, which is only used if the number cannot fit into the range
        of the float. The default integer data type is ``int``, with ``long``
        being used if the number is out of range of ``int``.
        """
        queue = args[0]
        if not isinstance(queue, CommandQueue):
            queue = kwargs.pop('queue', None)
            if queue is None:
                queue = self.queue
        else:
            args = args[1:]

        global_size = args[0]
        if not cypy.is_iterable(global_size):
            try:
                global_size = global_size.shape
                args = args[1:]
            except AttributeError:
                if global_size is None:
                    global_size = kwargs.pop('global_size')
        else:
            args = args[1:]

        args = tuple(self._process_args(args))

        event = _orig__call_Kernel(self, queue, global_size, *args, **kwargs)
        
        for arg in args:
            hook = getattr(arg, 'post_kernel_hook', None)
            if hook is not None:
                hook(self.program.context, arg, event)

        return event
    
    def _process_args(self, args):
        for arg in args:
            if isinstance(arg, (_numpy.number, MemoryObject)):
                yield arg
            else:
                yield self.convert_arg(arg)
    
    @classmethod
    def convert_arg(cls, arg):
        if cypy.is_int_like(arg):
            if cl_int.min <= arg <= cl_int.max:
                yield _numpy.int32(arg)
            elif cl_long.min <= arg <= cl_long.max:
                yield _numpy.int64(arg)
            else:
                raise Error("Integer-like number is out of range of long: %s" %
                            str(arg))
        elif cypy.is_float_like(arg):
            if cl_float.min <= arg <= cl_float.max:
                yield _numpy.float32(arg)
            elif cl_float.min <= arg <= cl_float.max:
                yield _numpy.float64(arg)
            else:
                raise Error("Float-like number is out of range of double: %s" %
                            str(arg))
        else:
            raise Error("Invalid argument: %s" % str(arg))
_cl.Kernel = Kernel
