# TODO: License header
# TODO: Module documentation

from pyopencl import *
import pyopencl as _cl
import numpy as _numpy
import cypy

class Error(Error):
    """Base class for errors in ``cl``. Extends :class:`pyopencl.Error`."""
    pass

#############################################################################
## Platform
#############################################################################
class Platform(Platform):
    """Represents an OpenCL platform.
    
    In OpenCL, a platform consists of the compilers and other tools that 
    implement the OpenCL interface. For example, on OS X 10.6+, the `Apple` 
    platform supports OpenCL. On other systems, NVidia, AMD and IBM provide 
    platforms for their respective devices.
    """
    @classmethod
    def get_platforms(cls):
        """Returns a tuple of available platforms on this system."""
        return tuple(get_platforms())
            
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

#############################################################################
## Versions
#############################################################################
OpenCL_1_0 = cypy.Version("OpenCL", [("major", 1), ("minor", 0)])
"""A :class:`Version <cypy.Version>` descriptor representing OpenCL version 1.0."""

#############################################################################
## OpenCL Extension descriptors
#############################################################################
class Extension(object):
    """An OpenCL extension descriptor.
    
    .. Note:: The list of extensions defined below is not comprehensive. Feel 
              free to add additional ones that you know about.
    """
    def __init__(self, name):
        self.name = name

    @property
    def pragma_str(self):
        """Returns the pragma needed to enable this extension."""
        return "\n#pragma extension %s : enable\n" % self.name
cypy.interned(Extension)

cl_khr_fp64 = Extension("cl_khr_fp64")
"""Standard 64-bit floating point extension.

*See section 9.3 in the spec.*
"""

cl_khr_fp16 = Extension("cl_khr_fp16")
"""Standard extension supporting use of the half type as a full type. 

*See section 9.10 in the spec.*
"""

cl_khr_global_int32_base_atomics = Extension("cl_khr_global_int32_base_atomics")
"""Standard 32-bit base atomic operations for global memory.

*See section 9.5 in the spec.*
"""

cl_khr_global_int32_extended_atomics = \
    Extension("cl_khr_global_int32_extended_atomics")
"""Standard 32-bit extended atomic operations for global memory.

*See section 9.5 in the spec.*
"""

cl_khr_local_int32_base_atomics = Extension("cl_khr_local_int32_base_atomics")
"""Standard 32-bit base atomic operations for local memory.

*See section 9.6 in the spec.*
"""

cl_khr_local_int32_extended_atomics = \
    Extension("cl_khr_local_int32_extended_atomics")
"""Standard 32-bit extended atomic operations for local memory.

*See section 9.6 in the spec.*
"""

int32_global_atomics_extensions = (cl_khr_global_int32_base_atomics,
                                   cl_khr_global_int32_extended_atomics)
"""Tuple containing both the base and extended 32-bit base atomic extensions."""

int32_local_atomics_extensions = (cl_khr_local_int32_base_atomics,
                                  cl_khr_local_int32_extended_atomics)
"""Tuple containing both the base and extended 32-bit base atomic extensions."""

int32_atomics_extensions = (cl_khr_global_int32_base_atomics,
                            cl_khr_global_int32_extended_atomics,
                            cl_khr_local_int32_base_atomics,
                            cl_khr_local_int32_extended_atomics)
"""Tuple containing all 32-bit atomics extensions."""

cl_khr_int64_base_atomics = Extension("cl_khr_int64_base_atomics")
"""Standard 64-bit base atomic operations.

*See section 9.7 in the spec.*
"""

cl_khr_int64_extended_atomics = Extension("cl_khr_int64_extended_atomics")
"""Standard 64-bit extended atomic operations.

*See section 9.7 in the spec.*
"""

int64_atomics_extensions = (cl_khr_int64_base_atomics,
                            cl_khr_int64_extended_atomics)
"""Tuple containing all 64-bit atomics extensions."""

cl_khr_byte_addressable_store = Extension("cl_khr_byte_addressable_store")
"""Standard extension to support byte addressable arrays.

*See section 9.9 in the spec.*
"""

cl_khr_3d_image_writes = Extension("cl_khr_3d_image_writes")
"""Standard extension to support 3D image memory objects.

*See section 9.8 in the spec.*
"""

khr_extensions = cypy.cons.ed(int32_atomics_extensions,                           #@UndefinedVariable
                             int64_atomics_extensions, 
                             (cl_khr_byte_addressable_store,))

cl_APPLE_gl_sharing = Extension("cl_APPLE_gl_sharing")
"""Apple extension for OpenGL sharing."""

cl_APPLE_SetMemObjectDestructor = Extension("cl_APPLE_SetMemObjectDestructor")
"""Apple SetMemObjectDestructor extension."""

cl_APPLE_ContextLoggingFunctions = Extension("cl_APPLE_ContextLoggingFunctions")
"""Apple ContextLoggingFunctions extension."""

APPLE_extensions = (cl_APPLE_gl_sharing, 
                    cl_APPLE_SetMemObjectDestructor,
                    cl_APPLE_ContextLoggingFunctions)
"""Tuple containing all Apple extensions."""

#############################################################################
## Data type descriptors
#############################################################################
class Type(object):
    """Base class for descriptors for OpenCL data types.
    
    Do not initialize this or any subclasses directly -- singletons have 
    already been defined below.
    """
    def __init__(self, name):
        self.name = name
        type_names[name] = self
        
    name = None
    """The name of the type."""
    
    def __str__(self):
        return "<cl.Type <%s>>" % self.name

    def __repr__(self): 
        return str(self)
        
    @property
    def _CG_expression(self):
        """cypy.cg.CG uses this."""
        return self.name
    
    version = None
    """The first OpenCL :class:`Version <cypy.Version>` this type is 
    available in."""
    
    min_sizeof = None
    """The minimum size, in bytes, of this type, independent of device."""
    
    max_sizeof = None
    """The maximum size, in bytes, of this type, independent of device."""    

    def sizeof_for(self, device):
        """Returns the size of this type on the specified device."""
        min_sizeof = self.min_sizeof
        if min_sizeof == self.max_sizeof:
            return min_sizeof
        else:
            return device.address_bits / 8
        
    @cypy.lazy(property)
    def global_ptr(self):
        """The :class:`GlobalPtrType` corresponding to this type."""
        name = GlobalPtrType.address_space + " " + self.name + "*"
        obj = GlobalPtrType(name)
        obj.target_type = self
        return obj
    
    @cypy.lazy(property)
    def local_ptr(self):
        """The :class:`LocalPtrType` corresponding to this type."""
        name = LocalPtrType.address_space + " " + self.name + "*"
        obj = LocalPtrType(name)
        obj.target_type = self
        return obj
    
    @cypy.lazy(property)
    def constant_ptr(self):
        """The :class:`ConstantPtrType` corresponding to this type."""
        name = ConstantPtrType.address_space + " " + self.name + "*"
        obj = ConstantPtrType(name)
        obj.target_type = self
        return obj
    
    @cypy.lazy(property)
    def private_ptr(self):
        """The :class:`PrivatePtrType` corresponding to this type."""
        name = PrivatePtrType.address_space + " " + self.name + "*"
        obj = PrivatePtrType(name)
        obj.target_type = self
        return obj
cypy.interned(Type)
type_names = { }

class BuiltinType(Type):
    """Base class for descriptors for OpenCL builtin types."""    
    pass

class ScalarType(BuiltinType):
    """Base class for descriptors for OpenCL scalar types.
    
    Calling a type descriptor will produce an appropriate numpy scalar suitable
    for calling into a kernel with:
    
        >>> cl_int(10).__class__
        <type 'numpy.int32'>
    
    """
    
    dtype_name = None
    """A string representing the unqualified name of the numpy dtype 
    corresponding to this scalar type, or None if unsupported by numpy.
    """
    
    dtype = None
    """The numpy dtype corresponding to this scalar type.
    
    None if unsupported by numpy.
    """
    
    min = None
    """The minimum value this type can take.
    
    None if device-dependent.
    """

    max = None
    """The maximum value this type can take.
    
    None if device-dependent.
    """
    
    def make_literal(self, bare_literal):
        """Converts a bare literal into an appropriately typed literal.

        Adds a suffix, if one exists. If not, uses a cast.
        """
        literal_suffix = self.literal_suffix
        bare_literal = str(bare_literal)
        if literal_suffix is None:
            return "(%s)%s" % (self.name, bare_literal)
        else:
            return "%s%s" % (bare_literal, literal_suffix)

    literal_suffix = None
    """The suffix appended to literals for this type, or None.

    (e.g. 'f' for float)

    Note that either case can normally be used. The lowercase version is
    provided here.

    Raw integer and floating point literals default to int and double,
    respectively, unless the integer exceeds the bounds for 32-bit integers
    in which case it is promoted to a long.
    """
    
    def __call__(self, n):
        return self.dtype.type(n)
        
class IntegerType(ScalarType):
    """Base class for descriptors for OpenCL scalar integer types."""    
    unsigned = False
    """A boolean indicating whether this is an unsigned integer type."""
    
    signed_variant = None
    """If integer, this provides the signed variant of the type."""
    
    unsigned_variant = None
    """If integer, this provides the unsigned variant of the type."""

class FloatType(ScalarType):
    """Base class for descriptors for OpenCL scalar float types."""

to_cl_type = { }
"""A map from numpy.dtype descriptors to :class:`ScalarType` descriptors."""

def _define_scalar_type(name,
                        dtype_name, 
                        sizeof, 
                        min, max, 
                        literal_suffix,
                        integer=False, signed_variant=None,
                        float=False,
                        version=OpenCL_1_0, 
                        required_extension=None):
    """shortcut for defining the scalar types with a buncha metadata"""
    if dtype_name is not None:
        try:
            dtype = _numpy.dtype(dtype_name)
            assert dtype.itemsize == sizeof
        except TypeError:
            dtype = None
    else:
        dtype = None
        
    if integer:
        cl_type = IntegerType(name)
    elif float:
        cl_type = FloatType(name)
    else:
        cl_type = ScalarType(name)
    cl_type.version = version
    cl_type.required_extension = required_extension
    cl_type.dtype_name = dtype
    cl_type.dtype = dtype
    cl_type.min_sizeof = sizeof
    cl_type.max_sizeof = sizeof 
    cl_type.min = min
    cl_type.max = max
    cl_type.literal_suffix = literal_suffix
    if integer:        
        if signed_variant is None:
            cl_type.unsigned = False
            cl_type.signed_variant = cl_type
        else:
            cl_type.unsigned = True
            cl_type.signed_variant = signed_variant
            cl_type.unsigned_variant = cl_type
            signed_variant.unsigned_variant = cl_type
            
    if dtype is not None:
        to_cl_type[dtype] = cl_type
        if hasattr(_numpy, dtype_name):
            # numpy.int32 is not numpy.dtype(numpy.int32), e.g.
            # but can often be used interchangeably
            to_cl_type[getattr(_numpy, dtype_name)] = cl_type

    return cl_type

cl_char = _define_scalar_type(name="char", dtype_name="int8", sizeof=1,
                              min=-(2**7), max=2**7-1, literal_suffix=None,
                              integer=True)
"""8-bit signed integer type."""
i8 = cl_char
"""Short name for cl_char.

.. Note:: These short names are non-standard.
"""

cl_uchar = _define_scalar_type(name="uchar", dtype_name="uint8", sizeof=1,
                               min=0, max=2**8-1, literal_suffix=None,
                               integer=True, signed_variant=cl_char)
"""8-bit unsigned integer type."""
ui8 = cl_uchar
"""Short name for cl_uchar."""

cl_short = _define_scalar_type(name="short", dtype_name="int16", sizeof=2,
                               min=-(2**15), max=2**15-1, literal_suffix=None,
                               integer=True)
"""16-bit signed integer type."""
i16 = cl_short
"""Short name for cl_short."""

cl_ushort = _define_scalar_type(name="ushort", dtype_name="uint16", sizeof=2,
                                min=0, max=2**16-1, literal_suffix=None,
                                integer=True, signed_variant=cl_short)
"""16-bit unsigned integer type."""
ui16 = cl_ushort
"""Short name for cl_ushort."""

cl_int = _define_scalar_type(name="int", dtype_name="int32", sizeof=4,
                             min=-(2**31), max=2**31-1, literal_suffix=None,
                             integer=True)
"""32-bit signed integer type."""
# override default behavior
cl_int.make_literal = lambda literal: str(int(literal))
i32 = cl_int
"""Short name for cl_int."""

cl_uint = _define_scalar_type(name="uint", dtype_name="uint32", sizeof=4, 
                              min=0, max=2**32-1, literal_suffix="u", # u?
                              integer=True, signed_variant=cl_int)
"""32-bit unsigned integer type."""
ui32 = cl_uint
"""Short name for cl_uint."""

cl_long = _define_scalar_type(name="long", dtype_name="int64", sizeof=8,
                              min=-(2**63), max=2**63-1, literal_suffix="L",
                              integer=True)
"""64-bit signed integer type."""
i64 = cl_long
"""Short name for cl_long."""

cl_ulong = _define_scalar_type(name="ulong", dtype_name="uint64", sizeof=8,
                              min=0, max=2**64-1, literal_suffix="uL",
                              integer=True, signed_variant=cl_long)
"""64-bit unsigned integer type."""
ui64 = cl_ulong
"""Short name for cl_ulong."""

# half is not quite a scalar type in that you cannot have half values as a local
# variable without enabling an extension, but you can use half arrays with
# special functions without enabling it, so yeah, need to special case this
# in various places.
# 
# also, numpy doesn't have a float16 type, though there is some movement
# towards implementing basic support for it...
cl_half = _define_scalar_type(name="half", dtype_name=None, sizeof=2,
                              min=float("5.96046448e-08"), 
                              max=float("65504.0"), 
                              literal_suffix=None, 
                              float=True)
"""16-bit floating point type.

See the spec if you intend to use this, its complicated.
"""
f16 = cl_half
"""Short name for cl_half."""

cl_float = _define_scalar_type(name="float", dtype_name="float32", sizeof=4,
                               min=float("-3.402823466E38"),  
                               max=float("3.402823466E38"),
                               literal_suffix="f",
                               float=True)
"""32-bit floating point type."""
cl_float.min_positive = float("1.1754945351E-38")
f32 = cl_float
"""Short name for cl_float."""

cl_double = _define_scalar_type(name="double", dtype_name="float64", sizeof=8,
                                min=float("-1.7976931348623158E308"), 
                                max=float("1.7976931348623158E308"),
                                literal_suffix="d",
                                float=True)
"""64-bit floating point type."""
cl_double.min_positive = float("2.2250738585072014E-308"),
cl_double.make_literal = lambda literal: str(float(literal))
f64 = cl_double
"""Short name for cl_double."""

cl_bool = cl_int
"""cl_bool is cl_int"""

cl_void = Type("void")
"""The void type.

Can only be used as the return type of a function or the target type of a 
pointer.
"""

cl_intptr_t = _define_scalar_type(name="intptr_t", dtype_name=None, sizeof=None,
                                  min=None, max=None, literal_suffix=None,
                                  integer=True)
"""Signed-integer type with size equal to ``Device.address_bits``."""
cl_intptr_t.min_sizeof = 4
cl_intptr_t.max_sizeof = 8
iptr = cl_intptr_t
"""Short name for cl_intptr_t."""

cl_uintptr_t = _define_scalar_type(name="uintptr_t", dtype_name=None, 
                                   sizeof=None, min=None, max=None, 
                                   literal_suffix=None, integer=True, 
                                   signed_variant=cl_intptr_t)
"""Unsigned integer type with size equal to ``Device.address_bits``."""
cl_uintptr_t.min_sizeof = 4
cl_uintptr_t.max_sizeof = 8
uiptr = cl_uintptr_t
"""Short name for cl_uintptr_t."""

cl_ptrdiff_t = _define_scalar_type(name="ptrdiff_t", dtype_name=None,
                                   sizeof=None, min=None, max=None,
                                   literal_suffix=None, integer=True)
"""Signed integer type large enough to hold the result of subtracting pointers."""
cl_ptrdiff_t.min_sizeof = 4
cl_ptrdiff_t.max_sizeof = 8
ptrdiff_t = cl_ptrdiff_t
"""Short name for cl_ptrdiff_t."""

cl_size_t = _define_scalar_type(name="size_t", dtype_name=None,
                                sizeof=None, min=None, max=None,
                                literal_suffix=None, integer=True,
                                signed_variant=cl_ptrdiff_t)
"""Unsigned integer type large enough to hold the maximum length of a buffer."""
cl_size_t.min_sizeof = 4
cl_size_t.max_sizeof = 8
size_t = cl_size_t
"""Short name for cl_size_t."""

class PtrType(Type):
    """Base class for descriptors for OpenCL pointer types."""
    address_space = None
    """The address space the pointer refers to, e.g. "__global"."""
    
    short_address_space = None
    """The short name of the address space, e.g. "global"."""
    
    @cypy.lazy(property)
    def suffix_name(self):
        return "_" + self.short_address_space + self.target_type.name + "ptr" + "_"
    
    @cypy.lazy(property)
    def version(self):
        return self.target_type.version
    
    min_sizeof = 4
    max_sizeof = 8
    
class GlobalPtrType(PtrType):
    """Base class for descriptors for OpenCL pointers to global memory."""
    address_space = "__global"
    short_address_space = "global"
    
class LocalPtrType(PtrType):
    """Base class for descriptors for OpenCL pointers to local memory."""
    address_space = "__local"
    short_address_space = "local"
        
class ConstantPtrType(PtrType):
    """Base class for descriptors for OpenCL pointers to constant memory."""
    address_space = "__constant"
    short_address_space = "constant"
        
class PrivatePtrType(PtrType):
    """Base class for descriptors for OpenCL pointers to private memory."""
    address_space = "__private"
    short_address_space = ""
    
class VectorType(BuiltinType):
    """Abstract base type for vector types."""
    
    n = None
    """The size of the vector type."""
    
    base_type = None
    """The base scalar type for this vector type."""
    
    @cypy.lazy(property)
    def version(self):
        return self.base_type.version
    
    @cypy.lazy(property)
    def min_sizeof(self):
        return self.base_type.min_sizeof * self.n
    
    @cypy.lazy(property)
    def max_sizeof(self):
        return self.base_type.max_sizeof * self.n

vector_valid_n = (2, 4, 8, 16)
"""Valid values of ``n`` for vector types."""

vector_base_types = (cl_char, cl_uchar, cl_short, cl_ushort, cl_int, cl_uint,
                     cl_long, cl_ulong, cl_float, cl_double)
# TODO: enable double extensions if doublen is used

vector_types = { }
"""Allows lookup of a vector type by name or by [base type][n]"""

for base_type in vector_base_types:
    vector_types_base = vector_types[base_type] = { }
    for n in vector_valid_n:
        base_name = base_type.name
        name = base_name + str(n)
        cl_type = VectorType(name)
        cl_type.n = n
        cl_type.base_type = base_type
        vector_types[name] = cl_type
        vector_types_base[n] = cl_type
# TODO: How to introduce name to module dictionary?
# TODO: How to initialize values of this type?
        
# TODO: what are the possible sizes for these types? restrictions?
cl_event_t = event_t = Type("event_t")
cl_image2d_t = image2d_t = Type("image2d_t")
cl_image3d_t = image3d_t = Type("image3d_t")
cl_sampler_t = sampler_t = Type("sampler_t")

def to_cl_string_literal(value):
    """Produces an OpenCL string literal from a string value."""
    return '"%s"' % cypy.string_escape(value)

def to_cl_numeric_literal(value, unsigned=False, report_type=False):
    """Produces an OpenCL numeric literal from a number-like value heuristically.

    ``unsigned``
        If True, returns unsigned variant for integers. Ignored for floats.

    ``report_type``
        If True, returns (OpenCL type descriptor, literal).
        If False, returns the literal aone.

    See source for full algorithm.

        >>> to_cl_numeric_literal(4)
        "4"

        >>> to_cl_numeric_literal(4.0)
        "4.0f"

        >>> to_cl_numeric_literal(4, report_type=True)
        (<cl.Type <int>>, "4")

        >>> to_cl_numeric_literal(4.0, report_type=True)
        (<cl.Type <float>>, "4.0f")

        >>> to_cl_numeric_literal(2**50, report_type=True)
        (<cl.Type <long>>, "1125899906842624L")

        >>> to_cl_numeric_literal(2**50, unsigned=True, report_type=True)
        (<cl.Type <ulong>>, "1125899906842624uL")

        >>> to_cl_numeric_literal(cl_double.max, report_type=True)
        (<cl.Type <double>>, "1.79769313486e+308")

    Non-numeric values will throw AssertionErrors.

    See also: :meth:`ScalarType.make_literal` to specify the type explicitly.
    """
    cl_type = to_cl_numeric_type(value, unsigned)
    
    ## Add appropriate suffix / cast
    str_rep = str(value)
    cl_literal = cl_type.make_literal(str_rep)
    
    if report_type:
        return (cl_type, cl_literal)
    else:
        return cl_literal

def to_cl_numeric_type(value, unsigned=False):
    """Produces a Type descriptor from a number-like value heuristically.
    
    See examples in :func:`to_cl_numeric_literal`, which calls this function.
    """
    is_numpy = hasattr(value, "dtype") and value.dtype in to_cl_type
    if is_numpy:
        return to_cl_type[value.dtype]
    else:
        if value is True or value is False:
            value = int(value)
            
        if cypy.is_int_like(value):
            value = long(value)
            if unsigned:
                assert value > 0
                if value <= cl_uint.max:
                    return cl_uint
                else:
                    assert value <= cl_ulong.max
                    return cl_ulong
            else:
                if cl_int.min <= value <= cl_int.max:
                    return cl_int
                else:
                    assert cl_long.min <= value <= cl_long.max
                    return cl_long
        else:
            assert cypy.is_float_like(value)
            value = float(value)
            if cl_float.min <= value <= cl_float.max:
                return cl_float
            else:
                assert cl_double.min <= value <= cl_double.max
                return cl_double

def infer_cl_type(value):
    """Infers a Type descriptor for the provided value heuristically."""
    try:
        return value.cl_type
    except AttributeError:
        try:
            return to_cl_type[value.dtype]
        except AttributeError:
            if cypy.is_numeric(value):
                return to_cl_numeric_type(value, False)
            elif isinstance(value, basestring):
                return cl_char.private_ptr
            raise Error("Cannot infer cl_type of " + str(value))

##############################################################################
# Built-ins 
##############################################################################
class BuiltinFn(object):
    """A stub for built-in functions avaiable to OpenCL kernels."""
    def __init__(self, name, return_type_fn):
        self.name = name
        self.return_type_fn = return_type_fn
        builtins[name] = self  
        
    name = None
    """The name of the function."""
    
    return_type_fn = None
    """A function which, when provided the types of the input arguments, gives
    you the return type of the builtin function, or raises an :class:`Error`
    if the types are invalid."""
    
    requires_extensions = None
    """If not None, returns a tuple of extensions required for arguments of 
    the specified types."""

class BuiltinConstant(object):
    """A descriptor for builtin constants available to OpenCL kernels."""
    def __init__(self, name, cl_type):
        self.name = name
        self.cl_type = cl_type
        builtins[name] = self
        
class ReservedKeyword(object):
    """A descriptor for OpenCL reserved keywords."""
    def __init__(self, name):
        self.name = name
        builtins[name] = self

builtins = { }
"""A map from built-in and reserved names to their corresponding descriptor."""

# Work-Item Built-in Functions [6.11.1]
get_work_dim = BuiltinFn("get_work_dim", lambda D: cl_uint)
"""The ``get_work_dim`` builtin function."""
get_global_size = BuiltinFn("get_global_size", lambda D: cl_size_t)
"""The ``get_global_size`` builtin function."""
get_global_id = BuiltinFn("get_global_id", lambda D: cl_size_t)
"""The ``get_global_id`` builtin function."""
get_local_size = BuiltinFn("get_local_size", lambda D: cl_size_t)
"""The ``get_local_size`` builtin function."""
get_local_id = BuiltinFn("get_local_id", lambda D: cl_size_t)
"""The ``get_local_id`` builtin function."""
get_num_groups = BuiltinFn("get_num_groups", lambda D: cl_size_t)
"""The ``get_num_groups`` builtin function."""
get_group_id = BuiltinFn("get_group_id", lambda D: cl_size_t)
"""The ``get_group_id`` builtin function."""

# Integer Built-in Functions [6.11.3]
abs = BuiltinFn("abs", lambda x: x.unsigned_variant)
"""The ``abs`` builtin function."""
abs_diff = BuiltinFn("abs_diff", lambda x, y: x.unsigned_variant)
"""The ``abs_diff`` builtin function."""
add_sat = BuiltinFn("add_sat", lambda x, y: x)
"""The ``add_sat`` builtin function."""
hadd = BuiltinFn("hadd", lambda x, y: x)
"""The ``hadd`` builtin function."""
rhadd = BuiltinFn("rhadd", lambda x, y: x)
"""The ``rhadd`` builtin function."""
clz = BuiltinFn("clz", lambda x: x)
"""The ``clz`` builtin function."""
mad_hi = BuiltinFn("mad_hi", lambda a, b, c: a)
"""The ``mad_hi`` builtin function."""
mad24 = BuiltinFn("mad24", lambda a, b, c: a)
"""The ``mad24`` builtin function."""
mad_sat = BuiltinFn("mad_sat", lambda a, b, c: a)
"""The ``mad_sat`` builtin function."""
max = BuiltinFn("max", lambda x, y: x)
"""The ``max`` builtin function."""
min = BuiltinFn("min", lambda x, y: x)
"""The ``min`` builtin function."""
mul_hi = BuiltinFn("mul_hi", lambda x, y: x)
"""The ``mul_hi`` builtin function."""
mul24 = BuiltinFn("mul24", lambda a, b: a)
"""The ``mul24`` builtin function."""
rotate = BuiltinFn("rotate", lambda v, i: v)
"""The ``rotate`` builtin function."""
sub_sat = BuiltinFn("sub_sat", lambda x, y: x)
"""The ``sub_sat`` builtin function."""

def _upsample_return_type_fn(hi, lo):
    # TODO: don't use is
    if hi is cl_char and lo is cl_uchar:
        return cl_short
    if hi is cl_uchar and lo is cl_uchar:
        return cl_ushort
    if hi is cl_short and lo is cl_ushort:
        return cl_int
    if hi is cl_ushort and lo is cl_short:
        return cl_uint
    if hi is cl_int and lo is cl_int:
        return cl_long
    if hi is cl_uint and lo is cl_uint:
        return cl_ulong
    
    raise Error()
upsample = BuiltinFn("upsample", _upsample_return_type_fn)
"""The ``upsample`` builtin function."""

# Common Built-in Functions [6.11.4]
clamp = BuiltinFn("clamp", lambda x, min, max: x)
"""The ``clamp`` builtin function."""
degrees = BuiltinFn("degrees", lambda radians: radians)
"""The ``degrees`` builtin function."""
mix = BuiltinFn("mix", lambda x, y: x)
"""The ``mix`` builtin function."""
radians = BuiltinFn("radians", lambda degrees: degrees)
"""The ``radians`` builtin function."""
step = BuiltinFn("step", lambda edge, x: x)
"""The ``step`` builtin function."""
smoothstep = BuiltinFn("smoothstep", lambda edge0, edge1, x: x)
"""The ``smoothstep`` builtin function."""
sign = BuiltinFn("sign", lambda x: x)
"""The ``sign`` builtin function."""

# Math Built-in Functions [6.11.2]
acos = BuiltinFn("acos", lambda x: x)
"""The ``acos`` builtin function."""
acosh = BuiltinFn("acosh", lambda x: x)
"""The ``acosh`` builtin function."""
acospi = BuiltinFn("acospi", lambda x: x)
"""The ``acospi`` builtin function."""
asin = BuiltinFn("asin", lambda x: x)
"""The ``asin`` builtin function."""
asinh = BuiltinFn("asinh", lambda x: x)
"""The ``asinh`` builtin function."""
asinpi = BuiltinFn("asinpi", lambda x: x)
"""The ``asinpi`` builtin function."""
atan = BuiltinFn("atan", lambda y_over_x: y_over_x)
"""The ``atan`` builtin function."""
atan2 = BuiltinFn("atan2", lambda y, x: y)
"""The ``atan2`` builtin function."""
atanh = BuiltinFn("atanh", lambda x: x)
"""The ``atanh`` builtin function."""
atanpi = BuiltinFn("atanpi", lambda x: x)
"""The ``atanpi`` builtin function."""
atan2pi = BuiltinFn("atan2pi", lambda x, y: x)
"""The ``atan2pi`` builtin function."""
cbrt = BuiltinFn("cbrt", lambda x: x)
"""The ``cbrt`` builtin function."""
ceil = BuiltinFn("ceil", lambda x: x)
"""The ``ceil`` builtin function."""
copysign = BuiltinFn("copysign", lambda x, y: x)
"""The ``copysign`` builtin function."""
cos = BuiltinFn("cos", lambda x: x)
"""The ``cos`` builtin function."""
half_cos = BuiltinFn("half_cos", lambda x: x)
"""The ``half_cos`` builtin function."""
native_cos = BuiltinFn("native_cos", lambda x: x)
"""The ``native_cos`` builtin function."""
cosh = BuiltinFn("cosh", lambda x: x)
"""The ``cosh`` builtin function."""
cospi = BuiltinFn("cospi", lambda x: x)
"""The ``cospi`` builtin function."""
half_divide = BuiltinFn("half_divide", lambda x, y: x)
"""The ``half_divide`` builtin function."""
native_divide = BuiltinFn("native_divide", lambda x, y: x)
"""The ``native_divide`` builtin function."""
erfc = BuiltinFn("erfc", lambda x, y: x)
"""The ``erfc`` builtin function."""
erf = BuiltinFn("erf", lambda x: x)
"""The ``erf`` builtin function."""
exp = BuiltinFn("exp", lambda x: x)
"""The ``exp`` builtin function."""
half_exp = BuiltinFn("half_exp", lambda x: x)
"""The ``half_exp`` builtin function."""
native_exp = BuiltinFn("native_exp", lambda x: x)
"""The ``native_exp`` builtin function."""
exp2 = BuiltinFn("exp2", lambda x: x)
"""The ``exp2`` builtin function."""
half_exp2 = BuiltinFn("half_exp2", lambda x: x)
"""The ``half_exp2`` builtin function."""
native_exp2 = BuiltinFn("native_exp2", lambda x: x)
"""The ``native_exp2`` builtin function."""
exp10 = BuiltinFn("exp10", lambda x: x)
"""The ``exp10`` builtin function."""
half_exp10 = BuiltinFn("half_exp10", lambda x: x)
"""The ``half_exp10`` builtin function."""
native_exp10 = BuiltinFn("native_exp10", lambda x: x)
"""The ``native_exp10`` builtin function."""
expm1 = BuiltinFn("expm1", lambda x: x)
"""The ``expm1`` builtin function."""
fabs = BuiltinFn("fabs", lambda x: x)
"""The ``fabs`` builtin function."""
fdim = BuiltinFn("fdim", lambda x, y: x)
"""The ``fdim`` builtin function."""
floor = BuiltinFn("floor", lambda x: x)
"""The ``floor`` builtin function."""
fma = BuiltinFn("fma", lambda a, b, c: a)
"""The ``fma`` builtin function."""
fmax = BuiltinFn("fmax", lambda x, y: x)
"""The ``fmax`` builtin function."""
fmin = BuiltinFn("fmin", lambda x, y: x)
"""The ``fmin`` builtin function."""
fmod = BuiltinFn("fmod", lambda x, y: x)
"""The ``fmod`` builtin function."""
fract = BuiltinFn("fract", lambda x, iptr: x)
"""The ``fract`` builtin function."""
frexp = BuiltinFn("frexp", lambda x, exp: x)
"""The ``frexp`` builtin function."""
hypot = BuiltinFn("hypot", lambda x, y: x)
"""The ``hypot`` builtin function."""
ilogb = BuiltinFn("ilogb", lambda x: x)
"""The ``ilogb`` builtin function."""
ldexp = BuiltinFn("ldexp", lambda x, n: x)
"""The ``ldexp`` builtin function."""
lgamma = BuiltinFn("lgamma", lambda x: x)
"""The ``lgamma`` builtin function."""
lgamma_r = BuiltinFn("lgamma_r", lambda x, signp: x)
"""The ``lgamma_r`` builtin function."""
log = BuiltinFn("log", lambda x: x)
"""The ``log`` builtin function."""
half_log = BuiltinFn("half_log", lambda x: x)
"""The ``half_log`` builtin function."""
native_log = BuiltinFn("native_log", lambda x: x)
"""The ``native_log`` builtin function."""
log2 = BuiltinFn("log2", lambda x: x)
"""The ``log2`` builtin function."""
half_log2 = BuiltinFn("half_log2", lambda x: x)
"""The ``half_log2`` builtin function."""
native_log2 = BuiltinFn("native_log2", lambda x: x)
"""The ``native_log2`` builtin function."""
log10 = BuiltinFn("log10", lambda x: x)
"""The ``log10`` builtin function."""
half_log10 = BuiltinFn("half_log10", lambda x: x)
"""The ``half_log10`` builtin function."""
native_log10 = BuiltinFn("native_log10", lambda x: x)
"""The ``native_log10`` builtin function."""
log1p = BuiltinFn("log1p", lambda x: x)
"""The ``log1p`` builtin function."""
logb = BuiltinFn("logb", lambda x: x)
"""The ``logb`` builtin function."""
mad = BuiltinFn("mad", lambda a, b, c: a)
"""The ``mad`` builtin function."""
modf = BuiltinFn("modf", lambda x, iptr: x)
"""The ``modf`` builtin function."""
nextafter = BuiltinFn("nextafter", lambda x, y: x)
"""The ``nextafter`` builtin function."""
pow = BuiltinFn("pow", lambda x, y: x)
"""The ``pow`` builtin function."""
pown = BuiltinFn("pown", lambda x, y: x)
"""The ``pown`` builtin function."""
powr = BuiltinFn("powr", lambda x, y: x)
"""The ``powr`` builtin function."""
half_powr = BuiltinFn("half_powr", lambda x, y: x)
"""The ``half_powr`` builtin function."""
native_powr = BuiltinFn("native_powr", lambda x, y: x)
"""The ``native_powr`` builtin function."""
half_recip = BuiltinFn("half_recip", lambda x: x)
"""The ``half_recip`` builtin function."""
native_recip = BuiltinFn("native_recip", lambda x: x)
"""The ``native_recip`` builtin function."""
remainder = BuiltinFn("remainder", lambda x, y: x)
"""The ``remainder`` builtin function."""
remquo = BuiltinFn("remquo", lambda x, y, n: x)
"""The ``remquo`` builtin function."""
rint = BuiltinFn("rint", lambda x: x)
"""The ``rint`` builtin function."""
rootn = BuiltinFn("rootn", lambda x, y: x)
"""The ``rootn`` builtin function."""
round = BuiltinFn("round", lambda x: x)
"""The ``round`` builtin function."""
rsqrt = BuiltinFn("rsqrt", lambda x: x)
"""The ``rsqrt`` builtin function."""
native_rsqrt = BuiltinFn("native_rsqrt", lambda x: x)
"""The ``native_rsqrt`` builtin function."""
half_rsqrt = BuiltinFn("half_rsqrt", lambda x: x)
"""The ``half_rsqrt`` builtin function."""
sin = BuiltinFn("sin", lambda x: x)
"""The ``sin`` builtin function."""
native_sin = BuiltinFn("native_sin", lambda x: x)
"""The ``native_sin`` builtin function."""
half_sin = BuiltinFn("half_sin", lambda x: x)
"""The ``half_sin`` builtin function."""
sincos = BuiltinFn("sincos", lambda x, cosval: x)
"""The ``sincos`` builtin function."""
sinh = BuiltinFn("sinh", lambda x: x)
"""The ``sinh`` builtin function."""
sinpi = BuiltinFn("sinpi", lambda x: x)
"""The ``sinpi`` builtin function."""
sqrt = BuiltinFn("sqrt", lambda x: x)
"""The ``sqrt`` builtin function."""
half_sqrt = BuiltinFn("half_sqrt", lambda x: x)
"""The ``half_sqrt`` builtin function."""
native_sqrt = BuiltinFn("native_sqrt", lambda x: x)
"""The ``native_sqrt`` builtin function."""
tan = BuiltinFn("tan", lambda x: x)
"""The ``tan`` builtin function."""
half_tan = BuiltinFn("half_tan", lambda x: x)
"""The ``half_tan`` builtin function."""
native_tan = BuiltinFn("native_tan", lambda x: x)
"""The ``native_tan`` builtin function."""
tanh = BuiltinFn("tanh", lambda x: x)
"""The ``tanh`` builtin function."""
tanpi = BuiltinFn("tanpi", lambda x: x)
"""The ``tanpi`` builtin function."""
tgamma = BuiltinFn("tgamma", lambda x: x)
"""The ``tgamma`` builtin function."""
trunc = BuiltinFn("trunc", lambda x: x)
"""The ``trunc`` builtin function."""

# Geometric Built-in Functions [6.11.5]
dot = BuiltinFn("dot", lambda p0, p1: p0)
"""The ``dot`` builtin function."""
distance = BuiltinFn("distance", lambda p0, p1: p0)
"""The ``distance`` builtin function."""
length = BuiltinFn("length", lambda p: p)
"""The ``length`` builtin function."""
normalize = BuiltinFn("normalize", lambda p: p)
"""The ``normalize`` builtin function."""
fast_distance = BuiltinFn("fast_distance", lambda p0, p1: cl_float)
"""The ``fast_distance`` builtin function."""
fast_length = BuiltinFn("fast_length", lambda p: cl_float)
"""The ``fast_length`` builtin function."""
fast_normalize = BuiltinFn("fast_normalize", lambda p: cl_float)
"""The ``fast_normalize`` builtin function."""

# Relational Built-in Functions [6.11.6]
isequal = BuiltinFn("isequal", lambda x, y: cl_int)
"""The ``isequal`` builtin function."""
isnotequal = BuiltinFn("isnotequal", lambda x, y: cl_int)
"""The ``isnotequal`` builtin function."""
isgreater = BuiltinFn("isgreater", lambda x, y: cl_int)
"""The ``isgreater`` builtin function."""
isgreaterequal = BuiltinFn("isgreaterequal", lambda x, y: cl_int)
"""The ``isgreaterequal`` builtin function."""
isless = BuiltinFn("isless", lambda x, y: cl_int)
"""The ``isless`` builtin function."""
islessequal = BuiltinFn("islessequal", lambda x, y: cl_int)
"""The ``islessequal`` builtin function."""
islessgreater = BuiltinFn("islessgreater", lambda x, y: cl_int)
"""The ``islessgreater`` builtin function."""
isfinite = BuiltinFn("isfinite", lambda x: cl_int)
"""The ``isfinite`` builtin function."""
isinf = BuiltinFn("isinf", lambda x: cl_int)
"""The ``isinf`` builtin function."""
isnan = BuiltinFn("isnan", lambda x: cl_int)
"""The ``isnan`` builtin function."""
isnormal = BuiltinFn("isnormal", lambda x: cl_int)
"""The ``isnormal`` builtin function."""
isordered = BuiltinFn("isordered", lambda x, y: cl_int)
"""The ``isordered`` builtin function."""
isunordered = BuiltinFn("isunordered", lambda x, y: cl_int)
"""The ``isunordered`` builtin function."""
signbit = BuiltinFn("signbit", lambda x: cl_int)
"""The ``signbit`` builtin function."""
any = BuiltinFn("any", lambda x: cl_int)
"""The ``any`` builtin function."""
all = BuiltinFn("all", lambda x: cl_int)
"""The ``all`` builtin function."""
bitselect = BuiltinFn("bitselect", lambda a, b, c: a)
"""The ``bitselect`` builtin function."""
select = BuiltinFn("select", lambda a, b, c: a)
"""The ``select`` builtin function."""

# Base Atomic Functions [9.5]
atom_add = BuiltinFn("atom_add", lambda p, val: val)
"""The ``atom_add`` builtin function."""
atom_sub = BuiltinFn("atom_sub", lambda p, val: val)
"""The ``atom_sub`` builtin function."""
atom_xchg = BuiltinFn("atom_xchg", lambda p, val: val)
"""The ``atom_xchg`` builtin function."""
atom_inc = BuiltinFn("atom_inc", lambda p: p.target_type)
"""The ``atom_inc`` builtin function."""
atom_dec = BuiltinFn("atom_dec", lambda p: p.target_type)
"""The ``atom_dec`` builtin function."""
atom_cmpxchg = BuiltinFn("atom_cmpxchg", lambda p, cmp, val: val)
"""The ``atom_cmpxchg`` builtin function."""
base_atomics = (atom_add, atom_sub, atom_xchg, atom_inc, atom_dec, atom_cmpxchg)

def _base_atomic_extension_inference(p, *args): #@UnusedVariable
    target_type = p.target_type
    if target_type is cl_int or target_type is cl_uint:
        if p.address_space == "__global":
            return (cl_khr_global_int32_base_atomics,)
        return (cl_khr_local_int32_base_atomics,)
    return (cl_khr_int64_base_atomics,)
    
for fn in base_atomics:
    fn.requires_extensions = _base_atomic_extension_inference
    
# Extended Atomic Functions [9.5]
atom_min = BuiltinFn("atom_min", lambda p, val: val)
"""The ``atom_min`` builtin function."""
atom_max = BuiltinFn("atom_max", lambda p, val: val)
"""The ``atom_max`` builtin function."""
atom_and = BuiltinFn("atom_and", lambda p, val: val)
"""The ``atom_and`` builtin function."""
atom_or = BuiltinFn("atom_or", lambda p, val: val)
"""The ``atom_or`` builtin function."""
atom_xor = BuiltinFn("atom_xor", lambda p, val: val)
"""The ``atom_xor`` builtin function."""
extended_atomics = (atom_min, atom_max, atom_and, atom_or, atom_xor)

def _extended_atomic_extension_inference(p):
    target_type = p.target_type
    if target_type is cl_int or target_type is cl_uint:
        if p.address_space == "__global":
            return (cl_khr_global_int32_extended_atomics,)
        return (cl_khr_local_int32_extended_atomics,)
    return (cl_khr_int64_extended_atomics,)

for fn in extended_atomics:
    fn.requires_extensions = _extended_atomic_extension_inference

# Vector Data Load/Store Built-in Functions [6.11.7]
vload_half = BuiltinFn("vload_half", lambda offset, p: cl_float)
"""The ``vload_half`` builtin function."""
vstore_half = BuiltinFn("vstore_half", lambda data, offset, p: cl_void)
"""The ``vstore_half`` builtin function."""

sizeof = BuiltinFn("sizeof", lambda x: cl_size_t)
"""The ``sizeof`` builtin operator."""

# Built-in constants
true = BuiltinConstant("true", cl_int)
false = BuiltinConstant("false", cl_int)
NULL = BuiltinConstant("NULL", cl_intptr_t)

# Reserved keywords
reserved_keywords = ["auto", "break", "case", "char", "const", "continue", 
                     "default", "do", "double", "else", "enum", "extern", 
                     "float", "for", "goto", "if", "inline", "int", "long", 
                     "register", "restrict", "return", "short", "signed", 
                     "sizeof", "static", "struct", "switch", "typedef",
                     "union", "unsigned", "void", "volatile", "while", "_Bool",
                     "_Complex", "_Imaginary", "char", "uchar", "short", 
                     "ushort", "int", "uint", "long", "ulong", "float",
                     "half", "double", "bool", "quad", "complex", "imaginary",
                     "image2d_t", "image3d_t", "sampler_t", "event_t",
                     "__global", "global", "__local", "local", "__private",
                     "private", "__constant", "constant", "__kernel", "kernel",
                     "__read_only", "read_only", "__write_only", "write_only",
                     "__read_write", "read_write", "__attribute__"]
scalar_types = ("char", "uchar", "short", "ushort", "int", "uint", "long",
                "ulong", "float", "half", "double", "bool", "quad")
vector_type_sizes = (2, 3, 4, 8, 16)
for type in scalar_types:
    for size in vector_type_sizes:
        reserved_keywords.append(type + str(size))
reserved_keywords = tuple(reserved_keywords)
reserved_keyword_descriptors = tuple(ReservedKeyword(kw) 
                                     for kw in reserved_keywords)
