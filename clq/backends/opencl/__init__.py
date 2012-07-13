import ast as _ast

import cypy
import cypy.astx as astx
import clq
from clq import TypeResolutionError
import clq.backends.base_c as base_c
import clq.extensions.language_types as cstrings

_globals = globals() # used to create lists of types below

################################################################################
# Types
################################################################################
class Type(base_c.Type):
    def sizeof_for(self, device):
        # TODO: Implement this
        return self.max_sizeof

class ScalarType(base_c.ScalarType, Type):
    ptr = None
    
    @cypy.lazy(property)
    def ptr_global(self):
        return GlobalPtrType(self)
    
    @cypy.lazy(property)
    def ptr_shared(self):
        return SharedPtrType(self)
    
    @cypy.lazy(property)
    def ptr_private(self):
        return PrivatePtrType(self)
    
    @cypy.lazy(property)
    def ptr_constant(self):
        return ConstantPtrType(self)

class VoidType(base_c.VoidType, Type):
    ptr = None
    
    @cypy.lazy(property)
    def ptr_global(self):
        return GlobalPtrType(self)
    
    @cypy.lazy(property)
    def ptr_shared(self):
        return SharedPtrType(self)
    
    @cypy.lazy(property)
    def ptr_private(self):
        return PrivatePtrType(self)
    
    @cypy.lazy(property)
    def ptr_constant(self):
        return ConstantPtrType(self)

void = VoidType()

class BoolType(base_c.BoolType, Type):
    ptr = None
    
    @cypy.lazy(property)
    def ptr_global(self):
        return GlobalPtrType(self)
    
    @cypy.lazy(property)
    def ptr_shared(self):
        return SharedPtrType(self)
    
    @cypy.lazy(property)
    def ptr_private(self):
        return PrivatePtrType(self)
    
    @cypy.lazy(property)
    def ptr_constant(self):
        return ConstantPtrType(self)

bool = BoolType()

#===============================================================================
# Strings
#===============================================================================
class StrType(Type):
    @classmethod
    def _make_type(cls, name):
        s = StrType(name)
        return s
    
    def is_subtype(self, candidate_type):
        """Implements subtype reflection and Constrained String Top rules."""
        if isinstance(candidate_type, cstrings.ConstrainedString):
            return True
        else:
            return candidate_type == StrType
    
    def resolve_BinOp(self,context,node):
        if not isinstance(node.op, _ast.Add):
            raise clq.TypeResolutionError(
                                "Operation %s is not supported on Strings" % 
                                str(node.op), node)
        right_type = node.right.unresolved_type.resolve(context)
        
        try:
            return self._resolve_BinOp(node.op, right_type, context.backend)
        except TypeResolutionError as e:
            if e.node is None:
                e.node = node
            raise e
    
    def _resolve_BinOp(self,op,right_type,backend):
        if(isinstance(right_type, StrType)):
            return StrType
        else:
            raise clq.TypeResolutionError("Must be a string",node)
    
    def generate_BinOp(self, context, node):
        left = context.visit(node.left)
        op = context.visit(node.op)
        right = context.visit(node.right)
        
        code = ("strcat" , "(", left.code, "," , right.code, ")")
        
        return astx.copy_node(node,
            left=left,
            op=op,
            right=right,
            
            code=code
        )
    

string = StrType._make_type('char*') # TODO: char.private_ptr

#===============================================================================
# Integers
#===============================================================================
class IntegerType(base_c.IntegerType, ScalarType):
    # TODO: Did we get all the properties?
    
    @classmethod
    def _make_pair(cls, name, sizeof):
        uname = "u" + name
        
        signed = IntegerType(name)
        unsigned = IntegerType(uname)
        
        signed.min_sizeof = signed.max_sizeof = sizeof
        unsigned.min_sizeof = unsigned.max_sizeof = sizeof
            
        signed.unsigned = False
        signed.unsigned_variant = unsigned
        signed.signed_variant = signed
        
        unsigned.unsigned = True
        unsigned.unsigned_variant = unsigned
        unsigned.signed_variant = signed
        
        return signed, unsigned

# Machine-independent integers
#===============================================================================
char, uchar = IntegerType._make_pair('char', 1)
short, ushort = IntegerType._make_pair('short', 2)
int, uint = IntegerType._make_pair('int', 4)
long, ulong = IntegerType._make_pair('long', 8)

machine_independent_int_types = dict(
    (name, _globals[name]) for name in 
    ('char', 'uchar', 'short', 'ushort', 'int', 'uint', 'long', 'ulong'))

try:
    import numpy
except ImportError:
    pass
else:
    char.np_dtype = numpy.dtype('int8')
    uchar.np_dtype = numpy.dtype('uint8')
    short.np_dtype = numpy.dtype('int16')
    ushort.np_dtype = numpy.dtype('uint16')
    int.np_dtype = numpy.dtype('int32')
    uint.np_dtype = numpy.dtype('uint32')
    long.np_dtype = numpy.dtype('int64')
    ulong.np_dtype = numpy.dtype('uint64')
    
    to_cl_type = { }
    for cl_type in machine_independent_int_types.itervalues():
        to_cl_type[cl_type.np_dtype] = cl_type

# Machine-dependent integers
#===============================================================================
size_t = IntegerType("size_t")
ptrdiff_t = IntegerType("ptrdiff_t")

size_t.unsigned = True
size_t.min_sizeof = 4
size_t.max_sizeof = 8
size_t.signed_variant = ptrdiff_t
size_t.unsigned_variant = size_t

ptrdiff_t.unsigned = False
ptrdiff_t.min_sizeof = 4
ptrdiff_t.max_sizeof = 8
ptrdiff_t.signed_variant = ptrdiff_t
ptrdiff_t.unsigned_variant = size_t

intptr_t = IntegerType("intptr_t")
uintptr_t = IntegerType("uintptr_t")

intptr_t.unsigned = False
intptr_t.min_sizeof = 4
intptr_t.max_sizeof = 8
intptr_t.signed_variant = intptr_t
intptr_t.unsigned_variant = uintptr_t

uintptr_t.unsigned = True
uintptr_t.min_sizeof = 4
uintptr_t.max_sizeof = 8
uintptr_t.signed_variant = intptr_t
uintptr_t.unsigned_variant = uintptr_t

machine_dependent_int_types = dict(
    (name, _globals[name]) for name in 
    ('size_t', 'ptrdiff_t', 'intptr_t', 'uintptr_t')
)

int_types = cypy.merge_dicts(machine_independent_int_types,
                             machine_dependent_int_types)

#===============================================================================
# Floating-point numbers
#===============================================================================
class FloatType(base_c.FloatType, ScalarType):
    pass

half = FloatType("half")
half.min_sizeof = half.max_sizeof = 2

float = FloatType("float")
float.min_sizeof = float.max_sizeof = 4

double = FloatType("double")
double.min_sizeof = double.max_sizeof = 8

float_types = dict((name, _globals[name]) for name in 
    ('half', 'float', 'double'))

try:
    import numpy
except ImportError:
    pass
else:
    half.np_dtype = None
    float.np_dtype = numpy.dtype('float32')
    double.np_dtype = numpy.dtype('float64')
    
    for cl_type in float_types.itervalues():
        np_dtype = cl_type.np_dtype
        if np_dtype is not None:
            to_cl_type[np_dtype] = cl_type   

scalar_types = cypy.merge_dicts(int_types,
                                float_types)

#===============================================================================
# Vector Types
#===============================================================================
vector_type_sizes = (2, 3, 4, 8, 16)

class VectorType(Type):
    pass

vector_types = { }
#base_types['bool'] = bool

#===============================================================================
# Pointers
#===============================================================================
class PtrType(base_c.PtrType, Type):
    def __init__(self, target_type, address_space):
        self.target_type = target_type
        self.address_space = address_space
        # TODO: pointers to pointers (does OpenCL actually support that?)
        Type.__init__(self, "%s %s*" % (address_space, 
                                        target_type.name))
        
    target_type = None
    address_space = None
    
    ptr = None
    
class GlobalPtrType(PtrType):
    def __init__(self, target_type):
        PtrType.__init__(self, target_type, "__global")
        
class ConstantPtrType(PtrType):
    def __init__(self, target_type):
        PtrType.__init__(self, target_type, "__constant")
        
class PrivatePtrType(PtrType):
    def __init__(self, target_type):
        PtrType.__init__(self, target_type, "__private")
        
class SharedPtrType(PtrType):
    def __init__(self, target_type):
        PtrType.__init__(self, target_type, "__shared")
        
loc = None

#===============================================================================
# Structs and Unions
#===============================================================================
class StructureType(base_c.StructureType, Type):
    pass

#===============================================================================
# Other
#===============================================================================
# TODO: other types
other_types = { }

#===============================================================================
# Summary collections
#===============================================================================
address_space_qualifiers = (
    '__global', 'global',
    '__constant', 'constant', 
    '__private', 'private',
    '__shared', 'shared'
)
                        
function_qualifiers = ('__kernel', 'kernel') 

access_qualifiers = (
    '__read_only', 'read_only', 
    '__write_only', 'write_only', 
    '__read_write', 'read_write'
)

other_keywords = ('__attribute__')

keywords = tuple(cypy.cons(
    base_c.keywords,
    address_space_qualifiers,
    function_qualifiers,
    access_qualifiers,
    other_keywords,
    vector_types.keys(),
    other_types.keys()
))

base_types = cypy.merge_dicts(scalar_types, vector_types)

#===============================================================================
# Type parser
#===============================================================================
def t(name):
    return None

#===============================================================================
# OpenCL Backend
#===============================================================================
class Backend(base_c.Backend):   
    def __init__(self):
        base_c.Backend.__init__(self, "OpenCL")
        
    def string_type(self):
        return StrType

    def check_ConstrainedString_cast(self,context,node):
        """Generates code for downcasts to ConstrainedString types.
        
        Dynamic checking for downcasts to ConstrainedStrings is 
        not supported by the openCL backend because no regex library
        exists. 
        """
        raise clq.CodeGenerationError("Checking for constrained string " +
                        "downcasting unimplemented for the OpenCL bakcend.",
                        None)
    
    void_t = void
    int_t = int
    uint_t = uint
    float_t = float
    bool_t = bool
    string_t = string

#############################################################################
## OpenCL Extension descriptors
#############################################################################
class Extension(object):
    """An OpenCL extension descriptor.
    
    .. Note:: Not all known OpenCL extensions have been defined below. The
              ones defined in the OpenCL spec are given, as well as a few 
              others, but please feel free to contribute others. 
    """
    def __init__(self, name):
        self.name = name

    @property
    def pragma_str(self):
        """Returns the pragma needed to enable this extension."""
        return "#pragma extension %s : enable" % self.name
cypy.intern(Extension)

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
    
    @cypy.lazy(property)
    def cl_type(self):
        return BuiltinFnType(self)

class BuiltinFnType(Type, clq.VirtualType):
    """The type of OpenCL builtin function stubs (:class:`BuiltinFn`)."""
    def __init__(self, builtin):
        Type.__init__(self, "BuiltinFnType(%s)" % builtin.name)
        self.builtin = builtin
        
    def resolve_Call(self, context, node):
        arg_types = tuple(arg.unresolved_type.resolve(context)
                          for arg in node.args)
        return self.builtin.return_type_fn(*arg_types)
    
    def generate_Call(self, context, node):
        return clq._generic_generate_Call(context, node)
cypy.intern(BuiltinFnType)

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

# TODO: These don't actually do any error checking
# Work-Item Built-in Functions [6.11.1]
get_work_dim = BuiltinFn("get_work_dim", lambda D: uint)
"""The ``get_work_dim`` builtin function."""
get_global_size = BuiltinFn("get_global_size", lambda D: size_t)
"""The ``get_global_size`` builtin function."""
get_global_id = BuiltinFn("get_global_id", lambda D: size_t)
"""The ``get_global_id`` builtin function."""
get_local_size = BuiltinFn("get_local_size", lambda D: size_t)
"""The ``get_local_size`` builtin function."""
get_local_id = BuiltinFn("get_local_id", lambda D: size_t)
"""The ``get_local_id`` builtin function."""
get_num_groups = BuiltinFn("get_num_groups", lambda D: size_t)
"""The ``get_num_groups`` builtin function."""
get_group_id = BuiltinFn("get_group_id", lambda D: size_t)
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
    if hi is char and lo is uchar:
        return short
    if hi is uchar and lo is uchar:
        return ushort
    if hi is short and lo is ushort:
        return int
    if hi is ushort and lo is short:
        return uint
    if hi is int and lo is int:
        return long
    if hi is uint and lo is uint:
        return ulong
    
    raise TypeResolutionError(
        "Invalid argument types for upsample built-in: %s and %s." % 
        (hi.name, lo.name))
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
fast_distance = BuiltinFn("fast_distance", lambda p0, p1: float)
"""The ``fast_distance`` builtin function."""
fast_length = BuiltinFn("fast_length", lambda p: float)
"""The ``fast_length`` builtin function."""
fast_normalize = BuiltinFn("fast_normalize", lambda p: float)
"""The ``fast_normalize`` builtin function."""

# Relational Built-in Functions [6.11.6]
isequal = BuiltinFn("isequal", lambda x, y: int)
"""The ``isequal`` builtin function."""
isnotequal = BuiltinFn("isnotequal", lambda x, y: int)
"""The ``isnotequal`` builtin function."""
isgreater = BuiltinFn("isgreater", lambda x, y: int)
"""The ``isgreater`` builtin function."""
isgreaterequal = BuiltinFn("isgreaterequal", lambda x, y: int)
"""The ``isgreaterequal`` builtin function."""
isless = BuiltinFn("isless", lambda x, y: int)
"""The ``isless`` builtin function."""
islessequal = BuiltinFn("islessequal", lambda x, y: int)
"""The ``islessequal`` builtin function."""
islessgreater = BuiltinFn("islessgreater", lambda x, y: int)
"""The ``islessgreater`` builtin function."""
isfinite = BuiltinFn("isfinite", lambda x: int)
"""The ``isfinite`` builtin function."""
isinf = BuiltinFn("isinf", lambda x: int)
"""The ``isinf`` builtin function."""
isnan = BuiltinFn("isnan", lambda x: int)
"""The ``isnan`` builtin function."""
isnormal = BuiltinFn("isnormal", lambda x: int)
"""The ``isnormal`` builtin function."""
isordered = BuiltinFn("isordered", lambda x, y: int)
"""The ``isordered`` builtin function."""
isunordered = BuiltinFn("isunordered", lambda x, y: int)
"""The ``isunordered`` builtin function."""
signbit = BuiltinFn("signbit", lambda x: int)
"""The ``signbit`` builtin function."""
any = BuiltinFn("any", lambda x: int)
"""The ``any`` builtin function."""
all = BuiltinFn("all", lambda x: int)
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
    if target_type is int or target_type is uint:
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
    if target_type is int or target_type is uint:
        if p.address_space == "__global":
            return (cl_khr_global_int32_extended_atomics,)
        return (cl_khr_local_int32_extended_atomics,)
    return (cl_khr_int64_extended_atomics,)

for fn in extended_atomics:
    fn.requires_extensions = _extended_atomic_extension_inference

# Vector Data Load/Store Built-in Functions [6.11.7]
vload_half = BuiltinFn("vload_half", lambda offset, p: float)
"""The ``vload_half`` builtin function."""
vstore_half = BuiltinFn("vstore_half", lambda data, offset, p: void)
"""The ``vstore_half`` builtin function."""

sizeof = BuiltinFn("sizeof", lambda x: size_t)
"""The ``sizeof`` builtin operator."""

# Built-in constants
true = BuiltinConstant("true", int)
false = BuiltinConstant("false", int)
NULL = BuiltinConstant("NULL", intptr_t)

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

#############################################################################
## Versions
#############################################################################
#OpenCL_1_0 = cypy.Version("OpenCL", [("major", 1), ("minor", 0)])
#"""A :class:`Version <cypy.Version>` descriptor representing OpenCL 1.0."""
#

##############################################################################
### Data type descriptors
##############################################################################
#class Type(clq.Type):
#    """Base class for descriptors for OpenCL types.
#    
#    Do not initialize directly -- singletons have already been defined below.
#    """
#    def __init__(self, name):
#        clq.Type.__init__(self, name)
#        cl_types[name] = self
#        
#    name = None
#    """The name of the type."""
#    
#    def __str__(self):
#        return "<clq.opencl.Type <%s>>" % self.name
#
#    def __repr__(self): 
#        return str(self)
#        
#    @property
#    def _CG_expression(self):
#        """cypy.cg.CG uses this."""
#        return self.name
#    
#    version = None
#    """The first OpenCL :class:`Version <cypy.Version>` this type is 
#    available in."""
#    
#    min_sizeof = None
#    """The minimum size, in bytes, of this type, independent of device."""
#    
#    max_sizeof = None
#    """The maximum size, in bytes, of this type, independent of device."""    
#
#    def sizeof_for(self, device):
#        """Returns the size of this type on the specified device."""
#        min_sizeof = self.min_sizeof
#        if min_sizeof == self.max_sizeof:
#            return min_sizeof
#        else:
#            return device.address_bits / 8
#        
#    @cypy.lazy(property)
#    def global_ptr(self):
#        """The :class:`GlobalPtrType` corresponding to this type."""
#        name = GlobalPtrType.address_space + " " + self.name + "*"
#        obj = GlobalPtrType(name)
#        obj.target_type = self
#        return obj
#    
#    @cypy.lazy(property)
#    def local_ptr(self):
#        """The :class:`LocalPtrType` corresponding to this type."""
#        name = LocalPtrType.address_space + " " + self.name + "*"
#        obj = LocalPtrType(name)
#        obj.target_type = self
#        return obj
#    
#    @cypy.lazy(property)
#    def constant_ptr(self):
#        """The :class:`ConstantPtrType` corresponding to this type."""
#        name = ConstantPtrType.address_space + " " + self.name + "*"
#        obj = ConstantPtrType(name)
#        obj.target_type = self
#        return obj
#    
#    @cypy.lazy(property)
#    def private_ptr(self):
#        """The :class:`PrivatePtrType` corresponding to this type."""
#        name = PrivatePtrType.address_space + " " + self.name + "*"
#        obj = PrivatePtrType(name)
#        obj.target_type = self
#        return obj
#cypy.interned(Type)
#cl_types = { }
#
#class VoidType(Type):
#    """The type of :obj:`void`."""
#    def __init__(self):
#        Type.__init__(self, "void")
#cypy.interned(VoidType)
#
#void = VoidType()
#"""Functions that do not return a value are given the ``void`` return type."""
#    
#class ScalarType(Type):
#    """Base class for descriptors of OpenCL scalar types.
#    
#    Calling a type descriptor will produce an appropriate numpy scalar 
#    suitable for calling into a kernel with:
#    
#        >>> cl_int(10).__class__
#        <type 'numpy.int32'>
#    
#    """
#    
#    dtype_name = None
#    """A string representing the unqualified name of the numpy dtype 
#    corresponding to this scalar type, or None if unsupported by numpy.
#    """
#    
#    dtype = None
#    """The numpy dtype corresponding to this scalar type.
#    
#    None if unsupported by numpy.
#    """
#    
#    min = None
#    """The minimum value this type can take.
#    
#    None if device-dependent.
#    """
#
#    max = None
#    """The maximum value this type can take.
#    
#    None if device-dependent.
#    """
#    
#    def make_literal(self, bare_literal):
#        """Converts a bare literal into an appropriately typed literal.
#
#        Adds a suffix, if one exists. If not, uses a cast.
#        """
#        literal_suffix = self.literal_suffix
#        bare_literal = str(bare_literal)
#        if literal_suffix is None:
#            return "(%s)%s" % (self.name, bare_literal)
#        else:
#            return "%s%s" % (bare_literal, literal_suffix)
#
#    literal_suffix = None
#    """The suffix appended to literals for this type, or None.
#
#    (e.g. 'f' for float)
#
#    Note that either case can normally be used. The lowercase version is
#    provided here.
#
#    Raw integer and floating point literals default to int and double,
#    respectively, unless the integer exceeds the bounds for 32-bit integers
#    in which case it is promoted to a long.
#    """
#    
#    def __call__(self, n):
#        return self.dtype.type(n)
#    
#    def _resolve_Compare(self, visitor, left, ops, comparators, position): 
#        resolve = visitor._resolve_type
#        left_type = resolve(left.unresolved_type)
#        if not isinstance(left_type, ScalarType):
#            return
#        
#        for right in comparators:
#            right_type = resolve(right.unresolved_type)
#            if not isinstance(right_type, ScalarType):
#                return
#    
#        return cl_bool
#        
#    def _resolve_BoolOp(self, visitor, op, values, position):
#        resolve = visitor._resolve_type
#        for value in values:
#            value_type = resolve(value.unresolved_type)
#            if not isinstance(value_type, ScalarType):
#                return
#        
#        return cl_bool
#    
#    def _generate_AugAssign(self, visitor, node):
#        # TODO: handle floordiv and pow
#        visit = visitor.visit
#        visitor.stmts.append((
#            visit(node.value).code,
#            " ", visit(node.op).code, "= ",
#            visit(node.backend).code, ";\n"
#        ))
#        
#    def _generate_Compare(self, visitor, node):
#        # TODO: comparisons
#        pass
#    
#    #def _scalar_generate_Compare(self, visitor, left, ops, comparators, position): #@UnusedVariable
#    #    visit = visitor.visit
#    #    return ("(", 
#    #            cypy.join(_yield_Compare_terms(visit, left, comparators, ops), 
#    #                     " && "), 
#    #           ")")
#    #
#    #def _yield_Compare_terms(visit, left, comparators, ops):
#    #    for op, right in zip(ops, comparators):
#    #        yield (visit(left), " ", visit(op), " ", visit(right))
#    #        left = right
#
#    def _generate_BoolOp(self, visitor, node):
#        # TODO: bool ops
#        pass
#    
#    #def _scalar_generate_BoolOp(self, visitor, op, values, position): #@UnusedVariable
#    #    visit = visitor.visit
#    #    return cypy.join((value for value in values), visit(op))
#    
#    def _generate_UnaryOp(self, visitor, node):
#        visit = visitor.visit
#        op = visit(node.op)
#        operand = visit(node.operand)
#        code = ("(", op.code, operand.code, ")")
#        return astx.copy_node(node,
#            op=op,
#            operand=operand,
#            code=code)
#        
#class IntegerType(ScalarType):
#    """Base class for descriptors of OpenCL scalar integer types."""    
#    unsigned = False
#    """A boolean indicating whether this is an unsigned integer type."""
#    
#    signed_variant = None
#    """If integer, this provides the signed variant of the type."""
#    
#    unsigned_variant = None
#    """If integer, this provides the unsigned variant of the type."""
#    
#    def _resolve_UnaryOp(self, visitor, op, left):
#        min_sizeof = self.min_sizeof
#        if min_sizeof < 4: # char, shorts are widened according to C99
#            if self.unsigned:
#                if isinstance(op, _ast.USub):
#                    return cl_int
#                return cl_uint
#            return cl_int
#        
#        if isinstance(op, _ast.USub):
#            return self.signed_variant
#        return self
#
#    def _resolve_BinOp_left(self, visitor, left, op, right):
#        right_type = visitor._resolve_type(right.unresolved_type)
#        
#        if isinstance(right_type, FloatType):
#            return right_type._resolve_BinOp_left(visitor, right, op, left)
#        
#        if isinstance(right_type, IntegerType):
#            min_sizeof = self.min_sizeof
#            if min_sizeof < 4: # char, short on the left
#                if self.unsigned:
#                    if right_type.min_sizeof >= 4:
#                        return right_type.unsigned_variant
#                    return cl_uint
#                if right_type.min_sizeof >= 4:
#                    return right_type
#                if right_type.unsigned:
#                    return cl_uint
#                return cl_int
#            
#            if right_type.min_sizeof < 4: # char, short on the right, recurse
#                return right_type._resolve_BinOp_left(visitor, right, op, left)
#            
#            right_mso = right_type.max_sizeof
#            self_mso = self.max_sizeof
#            
#            if self.unsigned or right_type.unsigned:
#                if self_mso >= right_mso:
#                    return self.unsigned_variant
#                return right_type.unsigned_variant
#            else:
#                if self_mso >= right_mso:
#                    return self
#                return right_type
#            
#        # pointer arithmetic
#        if isinstance(op, _ast.Add) and isinstance(right_type, PtrType):
#            return right_type
#        
#    def _resolve_MultipleAssignment_prev(self, new):
#        if self is new:
#            return self
#        
#        if isinstance(new, FloatType):
#            return new._resolve_MultipleAssignment_prev(self)
#        
#        if isinstance(new, IntegerType):
#            new_mso = new.max_sizeof
#            self_mso = self.max_sizeof
#            
#            if self.unsigned or new.unsigned:
#                if new_mso >= self_mso:
#                    return new.unsigned_variant
#                return self.unsigned_variant
#            if new_mso >= self_mso:
#                return new
#            return self
#    
#    def _generate_BinOp(self, visitor, node):
#        # TODO: handle pow and floordiv
#        visit = visitor.visit
#        left = visit(node.left)
#        op = visit(node.op)
#        right = visit(node.right)
#        code = ("(", left.code, " ", op.code, " ", right.code, ")")
#        return astx.copy_node(node,
#            left=left,
#            op=op,
#            right=right,
#            code=code
#        )
#        
#    def _generate_Call(self, visitor, node):
#        # TODO: implement literal suffixes
#        pass
#
#    #def _integer_generate_BinOp_left(self, visitor, left, op, right):
#    #    visit = visitor.visit
#    #    if isinstance(op, _ast.Pow):
#    #        # pow is a function
#    #        return ("pow(", visit(left), ", ", visit(right), ")")
#    #    elif isinstance(op, _ast.FloorDiv):
#    #        # floor div differs in implementation depending on types
#    #        right_type = visitor._resolve_type(right.unresolved_type)
#    #        if isinstance(right_type, cl.FloatType):
#    #            # if either are floats, need to do a floor afterwards
#    #            return ("floor(", visit(left), " / ", visit(right), ")")
#    #        else:
#    #            # if both are ints, use regular division
#    #            return ("(", visit(left), " / ", visit(right), ")")
#    #    else:
#    #        return ("(", visit(left), " ", visit(op), " ", visit(right), ")")
#    #cl.IntegerType._generate_BinOp_left = _integer_generate_BinOp_left
#    #
#    #def _integer_generate_Call(self, visitor, func, args):
#    #    # implements literal suffixes
#    #    if isinstance(func, _ast.Num):
#    #        identifier = args[0].id
#    #        return ("(", literal_suffixes[identifier].name, ")(", #@UndefinedVariable
#    #                visitor.visit(func), ")")
#    #cl.IntegerType._generate_Call = _integer_generate_Call
#
#class FloatType(ScalarType):
#    """Base class for descriptors for OpenCL scalar float types."""
#    def _resolve_UnaryOp(self, visitor, op, left):
#        if isinstance(op, (_ast.USub, _ast.UAdd)):    
#            if self.min_sizeof < 4: # half
#                return cl_float
#            return self
#    
#    def _resolve_BinOp_left(self, visitor, left, op, right):
#        right_type = visitor._resolve_type(right.unresolved_type)
#        
#        if isinstance(right_type, FloatType):
#            self_sizeof = self.min_sizeof
#            right_sizeof = right_type.min_sizeof
#            if self_sizeof >= right_sizeof:
#                if self_sizeof > 2:
#                    return self
#                return cl_float
#            if right_sizeof > 2:
#                return right_type
#            return cl_float
#        
#        if isinstance(right_type, IntegerType):
#            if self.min_sizeof > 2:
#                return self
#            return cl_float
#    
#    def _float_resolve_MultipleAssignment_prev(self, new):
#        if isinstance(new, FloatType):
#            if new.min_sizeof >= self.min_sizeof:
#                return new
#            return self
#        if isinstance(new, IntegerType):
#            return self
#
#    def _generate_BinOp(self, visitor, node):
#        # TODO: handle pow and floordiv
#        visit = visitor.visit
#        left = visit(node.left)
#        op = visit(node.op)
#        right = visit(node.right)
#        code = ("(", left.code, " ", op.code, " ", right.code, ")")
#        return astx.copy_node(node,
#            left=left,
#            op=op,
#            right=right,
#            code=code
#        )
#    
#    def _generate_Call(self, visitor, node):
#        # implement literal suffixes
#        pass
#    
#    #def _float_generate_BinOp_left(self, visitor, left, op, right):
#    #    visit = visitor.visit
#    #    if isinstance(op, _ast.Pow):
#    #        # pow is a function
#    #        return ("pow(", visit(left), ", ", visit(right), ")")
#    #    elif isinstance(op, _ast.FloorDiv):
#    #        return ("floor(", visit(left), " / ", visit(right), ")")
#    #    else:
#    #        return ("(", visit(left), " ", visit(op), " ", visit(right), ")")
#    #
#    #def _float_generate_Call(self, visitor, func, args): #@UnusedVariable
#    #    if isinstance(func, _ast.Num):
#    #        identifier = args[0].id
#    #        clq_type = literal_suffixes[identifier] #@UndefinedVariable
#    #        if clq_type is cl.cl_double:
#    #            return str(func.n)
#    #        else:
#    #            return ("(", clq_type.name, ")(", str(func.n), ")")
# 
#to_cl_type = { }
#"""A map from numpy.dtype descriptors to :class:`ScalarType` descriptors."""
#
#def _define_scalar_type(name,
#                        dtype_name, 
#                        sizeof, 
#                        min, max, 
#                        literal_suffix,
#                        integer=False, signed_variant=None,
#                        float=False,
#                        version=OpenCL_1_0, 
#                        required_extension=None):
#    """shortcut for defining the scalar types with a buncha metadata"""
#    if dtype_name is not None:
#        try:
#            dtype = _numpy.dtype(dtype_name)
#            assert dtype.itemsize == sizeof
#        except TypeError:
#            dtype = None
#    else:
#        dtype = None
#        
#    if integer:
#        cl_type = IntegerType(name)
#    elif float:
#        cl_type = FloatType(name)
#    else:
#        cl_type = ScalarType(name)
#    cl_type.version = version
#    cl_type.required_extension = required_extension
#    cl_type.dtype_name = dtype
#    cl_type.dtype = dtype
#    cl_type.min_sizeof = sizeof
#    cl_type.max_sizeof = sizeof 
#    cl_type.min = min
#    cl_type.max = max
#    cl_type.literal_suffix = literal_suffix
#    if integer:        
#        if signed_variant is None:
#            cl_type.unsigned = False
#            cl_type.signed_variant = cl_type
#        else:
#            cl_type.unsigned = True
#            cl_type.signed_variant = signed_variant
#            cl_type.unsigned_variant = cl_type
#            signed_variant.unsigned_variant = cl_type
#            
#    if dtype is not None:
#        to_cl_type[dtype] = cl_type
#        if hasattr(_numpy, dtype_name):
#            # numpy.int32 is not numpy.dtype(numpy.int32), e.g.
#            # but can often be used interchangeably
#            to_cl_type[getattr(_numpy, dtype_name)] = cl_type
#
#    return cl_type
#
#cl_char = _define_scalar_type(name="char", dtype_name="int8", sizeof=1,
#                              min=-(2**7), max=2**7-1, literal_suffix=None,
#                              integer=True)
#"""8-bit signed integer type."""
#
#cl_uchar = _define_scalar_type(name="uchar", dtype_name="uint8", sizeof=1,
#                               min=0, max=2**8-1, literal_suffix=None,
#                               integer=True, signed_variant=cl_char)
#"""8-bit unsigned integer type."""
#
#cl_short = _define_scalar_type(name="short", dtype_name="int16", sizeof=2,
#                               min=-(2**15), max=2**15-1, literal_suffix=None,
#                               integer=True)
#"""16-bit signed integer type."""
#
#cl_ushort = _define_scalar_type(name="ushort", dtype_name="uint16", sizeof=2,
#                                min=0, max=2**16-1, literal_suffix=None,
#                                integer=True, signed_variant=cl_short)
#"""16-bit unsigned integer type."""
#
#cl_int = _define_scalar_type(name="int", dtype_name="int32", sizeof=4,
#                             min=-(2**31), max=2**31-1, literal_suffix=None,
#                             integer=True)
#"""32-bit signed integer type."""
## override default behavior
#cl_int.make_literal = lambda literal: str(int(literal))
#
#cl_uint = _define_scalar_type(name="uint", dtype_name="uint32", sizeof=4, 
#                              min=0, max=2**32-1, literal_suffix="u", # u?
#                              integer=True, signed_variant=cl_int)
#"""32-bit unsigned integer type."""
#
#cl_long = _define_scalar_type(name="long", dtype_name="int64", sizeof=8,
#                              min=-(2**63), max=2**63-1, literal_suffix="L",
#                              integer=True)
#"""64-bit signed integer type."""
#
#cl_ulong = _define_scalar_type(name="ulong", dtype_name="uint64", sizeof=8,
#                              min=0, max=2**64-1, literal_suffix="uL",
#                              integer=True, signed_variant=cl_long)
#"""64-bit unsigned integer type."""
#
## half is not quite a scalar type in that you cannot have half values as a local
## variable without enabling an extension, but you can use half arrays with
## special functions without enabling it, so yeah, need to special case this
## in various places.
## 
## also, numpy doesn't have a float16 type, though there is some movement
## towards implementing basic support for it...
#cl_half = _define_scalar_type(name="half", dtype_name=None, sizeof=2,
#                              min=float("5.96046448e-08"), 
#                              max=float("65504.0"), 
#                              literal_suffix=None, 
#                              float=True)
#"""16-bit floating point type.
#
#See the spec if you intend to use this, its complicated.
#"""
#
#cl_float = _define_scalar_type(name="float", dtype_name="float32", sizeof=4,
#                               min=float("-3.402823466E38"),  
#                               max=float("3.402823466E38"),
#                               literal_suffix="f",
#                               float=True)
#"""32-bit floating point type."""
#cl_float.min_positive = float("1.1754945351E-38")
#
#cl_double = _define_scalar_type(name="double", dtype_name="float64", sizeof=8,
#                                min=float("-1.7976931348623158E308"), 
#                                max=float("1.7976931348623158E308"),
#                                literal_suffix="d",
#                                float=True)
#"""64-bit floating point type."""
#cl_double.min_positive = float("2.2250738585072014E-308"),
#cl_double.make_literal = lambda literal: str(float(literal))
#
#cl_bool = cl_int
#"""cl_bool is cl_int"""
#
#cl_void = Type("void")
#"""The void type.
#
#Can only be used as the return type of a function or the backend type of a 
#pointer.
#"""
#
#cl_intptr_t = _define_scalar_type(name="intptr_t", dtype_name=None, sizeof=None,
#                                  min=None, max=None, literal_suffix=None,
#                                  integer=True)
#"""Signed-integer type with size equal to ``Device.address_bits``."""
#cl_intptr_t.min_sizeof = 4
#cl_intptr_t.max_sizeof = 8
#
#cl_uintptr_t = _define_scalar_type(name="uintptr_t", dtype_name=None, 
#                                   sizeof=None, min=None, max=None, 
#                                   literal_suffix=None, integer=True, 
#                                   signed_variant=cl_intptr_t)
#"""Unsigned integer type with size equal to ``Device.address_bits``."""
#cl_uintptr_t.min_sizeof = 4
#cl_uintptr_t.max_sizeof = 8
#
#cl_ptrdiff_t = _define_scalar_type(name="ptrdiff_t", dtype_name=None,
#                                   sizeof=None, min=None, max=None,
#                                   literal_suffix=None, integer=True)
#"""Signed integer type large enough to hold the result of subtracting pointers."""
#cl_ptrdiff_t.min_sizeof = 4
#cl_ptrdiff_t.max_sizeof = 8
#
#cl_size_t = _define_scalar_type(name="size_t", dtype_name=None,
#                                sizeof=None, min=None, max=None,
#                                literal_suffix=None, integer=True,
#                                signed_variant=cl_ptrdiff_t)
#"""Unsigned integer type large enough to hold the maximum length of a buffer."""
#cl_size_t.min_sizeof = 4
#cl_size_t.max_sizeof = 8
#
#class PtrType(Type):
#    """Base class for descriptors for OpenCL pointer types."""
#    address_space = None
#    """The address space the pointer refers to, e.g. "__global"."""
#    
#    short_address_space = None
#    """The short name of the address space, e.g. "global"."""
#    
#    @cypy.lazy(property)
#    def version(self):
#        return self.target_type.version
#    
#    min_sizeof = 4
#    max_sizeof = 8
#    
#    def _resolve_Subscript(self, visitor, value, slice):
#        slice_type = visitor._resolve_type(slice.unresolved_type)
#        
#        #if isinstance(slice_type, GID):
#        #    visitor.delta_r[value].push(slice_type)
#            
#        if not isinstance(slice_type, IntegerType):
#            raise TypeResolutionError(
#                "Subscript index must be an integer, but saw a %s." 
#                % slice_type.name)
#        return self.target_type
#
#    def _resolve_BinOp_left(self, visitor, left, op, right):
#        right_type = visitor._resolve_type(right.unresolved_type)
#        
#        if (isinstance(op, _ast.Sub) 
#            and isinstance(right_type, self.__class__)):
#            return cl_ptrdiff_t
#        
#        if isinstance(right_type, IntegerType) and \
#           isinstance(op, (_ast.Add, _ast.Sub)):
#            return self
#
#    def _resolve_MultipleAssignment_prev(self, new):
#        if self is new:
#            return self
#        
#        if isinstance(new, PtrType) and new.address_space == self.address_space:
#            if self.target_type is cl_void:
#                return new
#            if new.target_type is cl_void:
#                return self
#            
#        if isinstance(new, IntegerType): 
#            # mostly for NULL pointers but any integer can be assigned to 
#            # a pointer variable
#            return self
#
#    #def _ptr_resolve_SubscriptAssignment(self, visitor, arr, slice, val):
#    #    slice_type = visitor._resolve_type(slice.unresolved_type)
#        
#    #    if isinstance(slice_type, GID):
#    #        visitor.delta_w[value].push(slice_type)
#    #    TODO resolve subscript assignment business
#    
#    def _generate_BinOp(self, visitor, node):
#        visit = visitor.visit
#        left = visit(node.left)
#        op = visit(node.op)
#        right = visit(node.right)
#        code = ("(", left.code, " ", op.code, " ", right.code, ")")
#        return astx.copy_node(node,
#            left=left,
#            op=op,
#            right=right,
#            code=code
#        )
#
#    def _generate_Subscript(self, visitor, node):
#        visit = visitor.visit
#        value = visit(node.value)
#        slice = visit(node.slice)
#        code = (value.code, "[", slice.code, "]")
#        return astx.copy_node(node,
#            value=value,
#            slice=slice,
#            code=code
#        )
#        
#    def _generate_Assign_Subscript(self, visitor, target, value):
#        visit = visitor.visit
#        visitor.stmts.append((visit(backend).code, " = ", 
#                                  visit(value).code, ";\n"))
#        
#    def _generate_AugAssign_Subscript(self, visitor, target, op, value):
#        visit = visitor.visit
#        visitor.stmts.append((visit(backend).code, " ",
#                                  visit(op).code, "= ",
#                                  visit(value).code, ";\n"))
#        
#class GlobalPtrType(PtrType):
#    """Base class for descriptors for OpenCL pointers to global memory."""
#    address_space = "__global"
#    short_address_space = "global"
#    
#class LocalPtrType(PtrType):
#    """Base class for descriptors for OpenCL pointers to local memory."""
#    address_space = "__local"
#    short_address_space = "local"
#        
#class ConstantPtrType(PtrType):
#    """Base class for descriptors for OpenCL pointers to constant memory."""
#    address_space = "__constant"
#    short_address_space = "constant"
#        
#class PrivatePtrType(PtrType):
#    """Base class for descriptors for OpenCL pointers to private memory."""
#    address_space = "__private"
#    short_address_space = ""
#    
##class VectorType(Type):
##    """Abstract base type for vector types."""
##    
##    n = None
##    """The size of the vector type."""
##    
##    base_type = None
##    """The base scalar type for this vector type."""
##    
##    @cypy.lazy(property)
##    def version(self):
##        return self.base_type.version
##    
##    @cypy.lazy(property)
##    def min_sizeof(self):
##        return self.base_type.min_sizeof * self.n
##    
##    @cypy.lazy(property)
##    def max_sizeof(self):
##        return self.base_type.max_sizeof * self.n
##
##vector_valid_n = (2, 4, 8, 16)
##"""Valid values of ``n`` for vector types."""
##
##vector_base_types = (cl_char, cl_uchar, cl_short, cl_ushort, cl_int, cl_uint,
##                     cl_long, cl_ulong, cl_float, cl_double)
### TODO: enable double extensions if doublen is used
##
##vector_types = { }
##"""Allows lookup of a vector type by name or by [base type][n]"""
##
##for base_type in vector_base_types:
##    vector_types_base = vector_types[base_type] = { }
##    for n in vector_valid_n:
##        base_name = base_type.name
##        name = base_name + str(n)
##        cl_type = VectorType(name)
##        cl_type.n = n
##        cl_type.base_type = base_type
##        vector_types[name] = cl_type
##        vector_types_base[n] = cl_type
### TODO: How to introduce name to module dictionary?
### TODO: How to initialize values of this type?
##        
### TODO: what are the possible sizes for these types? restrictions?
##cl_event_t = event_t = Type("event_t")
##cl_image2d_t = image2d_t = Type("image2d_t")
##cl_image3d_t = image3d_t = Type("image3d_t")
##cl_sampler_t = sampler_t = Type("sampler_t")
#
#def to_cl_string_literal(value):
#    """Produces an OpenCL string literal from a string value."""
#    return '"%s"' % cypy.string_escape(value)
#
#def to_cl_numeric_literal(value, unsigned=False, report_type=False):
#    """Produces an OpenCL numeric literal from a number-like value heuristically.
#
#    ``unsigned``
#        If True, returns unsigned variant for integers. Ignored for floats.
#
#    ``report_type``
#        If True, returns (OpenCL type descriptor, literal).
#        If False, returns the literal aone.
#
#    See source for full algorithm.
#
#        >>> to_cl_numeric_literal(4)
#        "4"
#
#        >>> to_cl_numeric_literal(4.0)
#        "4.0f"
#
#        >>> to_cl_numeric_literal(4, report_type=True)
#        (<Type <int>>, "4")
#
#        >>> to_cl_numeric_literal(4.0, report_type=True)
#        (<Type <float>>, "4.0f")
#
#        >>> to_cl_numeric_literal(2**50, report_type=True)
#        (<Type <long>>, "1125899906842624L")
#
#        >>> to_cl_numeric_literal(2**50, unsigned=True, report_type=True)
#        (<Type <ulong>>, "1125899906842624uL")
#
#        >>> to_cl_numeric_literal(cl_double.max, report_type=True)
#        (<Type <double>>, "1.79769313486e+308")
#
#    Non-numeric values will throw AssertionErrors.
#
#    See also: :meth:`ScalarType.make_literal` to specify the type explicitly.
#    """
#    cl_type = to_cl_numeric_type(value, unsigned)
#    
#    ## Add appropriate suffix / cast
#    str_rep = str(value)
#    cl_literal = cl_type.make_literal(str_rep)
#    
#    if report_type:
#        return (cl_type, cl_literal)
#    else:
#        return cl_literal
#
#def to_cl_numeric_type(value, unsigned=False):
#    """Produces a Type descriptor from a number-like value heuristically.
#    
#    See examples in :func:`to_cl_numeric_literal`, which calls this function.
#    """
#    is_numpy = hasattr(value, "dtype") and value.dtype in to_cl_type
#    if is_numpy:
#        return to_cl_type[value.dtype]
#    else:
#        if value is True or value is False:
#            value = int(value)
#            
#        if cypy.is_int_like(value):
#            value = long(value)
#            if unsigned:
#                assert value > 0
#                if value <= cl_uint.max:
#                    return cl_uint
#                else:
#                    assert value <= cl_ulong.max
#                    return cl_ulong
#            else:
#                if cl_int.min <= value <= cl_int.max:
#                    return cl_int
#                else:
#                    assert cl_long.min <= value <= cl_long.max
#                    return cl_long
#        else:
#            assert cypy.is_float_like(value)
#            value = float(value)
#            if cl_float.min <= value <= cl_float.max:
#                return cl_float
#            else:
#                assert cl_double.min <= value <= cl_double.max
#                return cl_double
#
#def infer_cl_type(value):
#    """Infers a Type descriptor for the provided value heuristically."""
#    try:
#        return value.cl_type
#    except AttributeError:
#        try:
#            return to_cl_type[value.dtype]
#        except AttributeError:
#            if cypy.is_numeric(value):
#                return to_cl_numeric_type(value, False)
#            elif isinstance(value, basestring):
#                return cl_char.private_ptr
#            raise Error("Cannot infer cl_type of " + str(value))
#

#
##################################################################################
### Vector type code generation
##################################################################################
##cl.VectorType._generate_AugAssign = _scalar_generate_AugAssign
##cl.VectorType._generate_Compare = _scalar_generate_Compare
##cl.VectorType._generate_BoolOp = _scalar_generate_BoolOp
##cl.VectorType._generate_UnaryOp = _scalar_generate_UnaryOp
##
### TODO: make generate use same selection as inference
##def _vec_generate_BinOp_left(self, visitor, left, op, right):
##    visit = visitor.visit
##    
##    if isinstance(op, _ast.Pow):
##        return ("pow(", visit(left), ", ", visit(right), ")")
##    elif isinstance(op, _ast.FloorDiv):
##        if isinstance(self.base_type, cl.IntegerType):
##            return ("(", visit(left), "/", visit(right), ")")
##        else:
##            return ("floor(", visit(left), "/", visit(right), ")")
##    else:
##        return ("(", visit(left), " ", visit(op), " ", visit(right), ")")
##cl.VectorType._generate_BinOp_left = _vec_generate_BinOp_left
##
### TODO: Are these being generated correctly?
##def _vec_generate_Attribute(self, visitor, obj, attr):
##    visit = visitor.visit
##    return (visit(obj), ".", attr)
##cl.VectorType._generate_Attribute = _vec_generate_Attribute
##
##def _vec_generate_AssignAttribute(self, visitor, obj, attr, value):
##    visit = visitor.visit
##    return (visit(obj), ".", attr, " = ", visit(value), ";")
##cl.VectorType._generate_AssignAttribute = _vec_generate_AssignAttribute
##
##def _vec_generate_AugAssignAttribute(self, visitor, obj, attr, op, value):
##    visit = visitor.visit
##    return (visit(obj), ".", attr, " ", visit(op), "= ", visit(value), ";")
##cl.VectorType._generate_AugAssignAttribute = _vec_generate_AugAssignAttribute
##
### TODO: vector literals
### TODO: builtins
### TODO: documentation
##
##################################################################################
### Function type code generation
##################################################################################
##def _generic_fn_generate_Call(self, visitor, func, args): #@UnusedVariable
##    arg_types = tuple(visitor._resolve_type(arg.unresolved_type) 
##                      for arg in args)
##    generic_fn_ast = self.generic_fn_ast
##    concrete_fn = generic_fn_ast._get_concrete_fn(arg_types)
##    name = concrete_fn.fullname
##    
##    # insert program items
##    add_program_item = visitor._add_program_item
##    for program_item in concrete_fn.program_items:
##        add_program_item(program_item)
##
##    # add defaults
##    n_provided = len(args)
##    n_args = len(generic_fn_ast.explicit_arg_names)
##    n_default = n_args - n_provided
##    if n_default < 0:
##        raise CompileTimeError("Too many arguments were specified for %s." %
##                               name)
##    defaults = generic_fn_ast.defaults[0:n_default]    
##    
##    all_args = _yield_args(visitor, args, arg_types, defaults, 
##                            concrete_fn.implicit_args)
##    return (name, "(", all_args, ")")
##_type_inference.GenericFnType._generate_Call = _generic_fn_generate_Call
##
##def _concrete_fn_generate_Call(self, visitor, func, args): #@UnusedVariable
##    concrete_fn = self.concrete_fn
##    name = concrete_fn.fullname
##    
##    # insert program items
##    add_program_item = visitor._add_program_item
##    for program_item in concrete_fn.program_items:
##        add_program_item(program_item)
##    
##    arg_types = (visitor._resolve_type(arg.unresolved_type) 
##                 for arg in args)
##    all_args = _yield_args(visitor, args, arg_types, (), 
##                                      concrete_fn.implicit_args)
##    return (name, "(", all_args, ")")
##_type_inference.ConcreteFnType._generate_Call = _concrete_fn_generate_Call
##
##def _yield_args(visitor, args, arg_types, defaults, implicit_args):
##    visit = visitor.visit
##    for arg, arg_type in zip(args, arg_types):
##        if not hasattr(arg_type, 'constant_value'):
##            yield visit(arg)
##            
##    add_implicit = visitor._add_implicit
##    for implicit in cypy.cons(defaults, implicit_args):
##        yield "__implicit__" + str(add_implicit(implicit))
##        
##def _builtin_fn_generate_Call(self, visitor, func, args): #@UnusedVariable
##    builtin = self.builtin
##    
##    # extension inference
##    requires_extensions = builtin.requires_extensions
##    if requires_extensions is not None:
##        resolve_type = visitor._resolve_type
##        arg_types = (resolve_type(arg.unresolved_type) 
##                     for arg in args)
##        add_program_item = visitor._add_program_item
##        for extension in requires_extensions(*arg_types):
##            add_program_item(ExtensionItem(extension))
##        
##    visit = visitor.visit
##    all_args = cypy.join((visit(arg) for arg in args), ", ")
##    return (builtin.name, "(", all_args, ")")
##_type_inference.BuiltinFnType._generate_Call = _builtin_fn_generate_Call
##
##################################################################################
### Type type code generation
##################################################################################
##def _type_generate_Call(self, visitor, func, args):
##    func_type = visitor._resolve_type(func.unresolved_type).type
##    arg = args[0]
##    if isinstance(arg, _ast.Num):
##        # special casing this so double literals are used in casts
##        arg = arg.n
##    else:
##        arg = visitor.visit(arg)
##    return ("(", func_type.name, ")(", arg, ")")
##_type_inference.TypeType._generate_Call = _type_generate_Call
##
##################################################################################
### Addressof macro code generation
##################################################################################
##def _addressof_generate_Call(self, visitor, func, args): #@UnusedVariable
##    return ("&", visitor.visit(args[0]))
##_type_inference.AddressofType._generate_Call = _addressof_generate_Call
##
####################################
##
##class GID(Type):
##    def __init__(self, a, b):
##        self.a = a
##        self.b = b
##        
##    def _resolve_BinOp(self, visitor, left, op, right):
##        right_type = visitor.resolve(right)
##        if isinstance(right_type, GID):
##            a_new = None
##            b_new = None
##            if (isinstance(op, _ast.Add)):
##                a_new = self.a + right_type.a
##                b_new = self.b + right_type.b
##                
##            if (isinstance(op, _ast.Mul)):
##                a = self.a
##                if a == 0:
##                    a = right_type.a
##                    b = right_type.b
##                    c = self.b
##                else:
##                    a = right_type.a
##                    if a == 0:
##                        a = self.a
##                        b = self.b
##                        c = right_type.b
##                    else:
##                        a = None
##                        
##                if a is not None:
##                    a_new = a * c
##                    b_new = b * c
##                    
##            if a_new is not None and b_new is not None:
##                return GID(a_new, b_new)
##
##        elif isinstance(right_type, IntegerType) and right_type.unsigned:
##            # TODO
##            pass
##        
#################################################################################
## Vector type resolution
#################################################################################
##@cypy.memoize
##def _vec_resolve_UnaryOp(self, visitor, op, operand):
##    base_type = self.base_type
##    if isinstance(base_type, IntegerType):
##        if isinstance(op, _ast.USub) and not base_type.unsigned:
##            return self
##        return self
##
##    elif isinstance(base_type, FloatType):
##        if isinstance(op, (_ast.UAdd, _ast.USub)):
##            return self
##VectorType._resolve_UnaryOp = _vec_resolve_UnaryOp
##
##@cypy.memoize
##def _vec_resolve_BinOp(self, visitor, right):
##    resolve = visitor._resolve_type
##    right_type = resolve(right)
##    if right_type is self:
##        return self
##    
##    base_type = self.base_type
##    if isinstance(right_type, IntegerType) \
##       and isinstance(base_type, IntegerType):
##        if right_type.max_sizeof <= base_type.min_sizeof:
##            return self
##        
##    if isinstance(right_type, FloatType) \
##       and isinstance(base_type, FloatType):
##        if right_type.max_sizeof <= base_type.min_sizeof:
##            return self
##VectorType._resolve_BinOp_left = lambda self, visitor, left, op, right: \
##    _vec_resolve_BinOp(self, visitor, right)
##VectorType._resolve_BinOp_right = lambda self, visitor, left, op, right: \
##    _vec_resolve_BinOp(self, visitor, left)
##    
##@cypy.memoize
##def _vec_resolve_Attribute(self, visitor, obj, attr):
##    if attr == "lo" or attr == "hi" or attr == "even" or attr == "odd":
##        return vector_types[self.base_type][self.n / 2]
##    
##    if attr[0] == "s" and len(attr) == 2:
##        try:
##            idx = int(attr[1], 16)
##        except ValueError: pass
##        else:
##            if idx <= self.n:
##                return self.base_type
##    else:
##        ok = True
##        acceptable = ("x", "y", "z", "w")[0:(self.n+1)]
##        for idx in attr:
##            if idx not in acceptable:
##                ok = False
##                break
##            
##        if ok:
##            if len(attr) == 1:
##                return self.base_type
##            else:
##                try:
##                    return vector_types[self.base_type][len(attr)]
##                except KeyError: pass
##VectorType._resolve_Attribute = _vec_resolve_Attribute
##
### TODO: this isn't being called correctly
##@cypy.memoize
##def _vec_resolve_AssignAttribute(self, visitor, obj, attr, value):
##    n = None
##    
##    if attr == "lo" or attr == "hi" or attr == "even" or attr == "odd":
##        n = self.n / 2
##        
##    if attr[0] == "s" and len(attr) == 2:
##        try:
##            idx = int(attr[1], 16)
##        except ValueError: pass
##        else:
##            if idx <= self.n:
##                n = 1
##                
##    else:
##        ok = True
##        acceptable = ("x", "y", "z", "w")[0:(self.n+1)]
##        accepted = set()
##        for idx in attr:
##            if idx not in acceptable:
##                ok = False
##                break
##            elif idx in accepted:
##                ok = False
##                break
##            else:
##                accepted.add(idx)
##        
##        if ok:
##            n = len(attr)
##            
##    if n is not None:
##        value_type = visitor._resolve_type(value)
##        if n == 1:
##            required_type = self.base_type
##        else:
##            required_type = vector_types[self.base_type][n]
##        
##        if value_type is required_type:
##            return True
##
##        base_type = self.base_type
##        if isinstance(value_type, IntegerType) \
##           and isinstance(base_type, IntegerType) \
##           and base_type.min_sizeof <= value_type.max_sizeof:
##            return True
##        
##        elif isinstance(value_type, FloatType) \
##             and isinstance(base_type, FloatType) \
##             and base_type.min_sizeof <= value_type.max_sizeof:
##            return True
##VectorType._resolve_AssignAttribute = _vec_resolve_AssignAttribute
##
##@cypy.memoize
##def _vec_resolve_AugAssignAttribute(self, visitor, obj, attr, op, value):
##    return _vec_resolve_AssignAttribute(self, visitor, obj, attr, value)
##VectorType._resolve_AugAssignAttribute = _vec_resolve_AugAssignAttribute
##
### TODO: multiple assignment
#    
##class AddressofType(object):
##    """The type of the addressof macro.
##    
##    (addressof is a macro because addressof(x[y]) should have the type of the 
##     pointer x, it cannot simply evaluate the type of x[y] and then make it 
##     into a pointer because that would be ambiguous wrt address space.)
##    """
##    def _resolve_Call(self, visitor, func, args): #@UnusedVariable
##        if len(args) != 1:
##            raise InvalidTypeError(
##                "The addressof operator only takes one argument.")
##        
##        arg = args[0]
##        # even if its a subscript, we want to make sure it typechecks
##        arg_type = visitor._resolve_type(arg.unresolved_type)
##        if isinstance(arg, _ast.Subscript):
##            return visitor._resolve_type(arg.value.unresolved_type)
##        return arg_type.private_ptr
### injected as clq_type in __init__ to avoid circular reference problems
##addressof = cypy.Singleton(cl_type=AddressofType())
##"""A macro to support the '&' operator in OpenCL. 
##
##Must import into scope of your function to use this.
##"""
##
##class TypeType(VirtualType):
##    """Base class for the types of types."""
##    def __init__(self, type):
##        self.type = type
##        
##    @cypy.memoize
##    def _resolve_Call(self, visitor, func, args): #@UnusedVariable
##        # for type cast syntax
##        if len(args) == 1:
##            arg = args[0]
##            arg_type = visitor._resolve_type(arg.unresolved_type) #@UnusedVariable
##            if not isinstance(arg_type, (ScalarType, PtrType)):
##                raise InvalidTypeError("Cannot cast a %s to a %s." % 
##                                       (arg_type.name, self.name))
##            return self.type
##        else:
##            raise InvalidTypeError("Casts can only take one argument.")
##    
##@property
##def _type_clq_type(self):
##    return TypeType(self)
##Type.clq_type = _type_clq_type
#
#
##    ##########################################################################
##    ## Concrete Function Production and Calling
##    ##########################################################################
##    def __call__(self, *args, **kwargs):
##        """Calls this function with the provided arguments and keyword options.
##        
##        See :meth:`ConcreteFn.__call__`
##        
##        Internally, this creates a :class:`ConcreteFn`, which is then
##        used to generate a :class:`cl.Kernel` object, which is then called.
##        """
##        args, arg_types = zip(*self._apply_default_args_and_types(args))
##        concrete_fn = self._get_concrete_fn_final(arg_types)
##        
##        # determine global and local size using the size calculator if not
##        # specified
##        if 'global_size' not in kwargs:
##            global_size, local_size = self.size_calculator(*args)
##            kwargs['global_size'] = global_size
##            if 'local_size' not in kwargs:
##                kwargs['local_size'] = local_size
##        elif 'local_size' not in kwargs:
##            size_calculator = self.size_calculator
##            if size_calculator is not None:
##                _, local_size = size_calculator(*args)
##                kwargs['local_size'] = local_size
##
##        # determine actual arguments to pass (including implicits) and do call
##        args = self._filter_args(args, concrete_fn)
##        return concrete_fn._do_call(args, kwargs)
##        
##    def get_concrete_fn_for(self, *args):
##        """Returns the concrete function, with argument types taken from the 
##        provided values. Defaults are applied and the current global values of 
##        remaining free variables are used.
##        
##        Note that these values themselves are not bound to the concrete 
##        function. This is mostly useful for inspecting source code.
##        
##        See :meth:`get_concrete_fn` if you have the types in hand.
##        """
##        # to prevent unnecessary copying when passing through multiple
##        # functions, the private versions of these don't take var args
##        return self._get_concrete_fn_for(args)
##    
##    def _get_concrete_fn_for(self, args):
##        arg_types = (infer_clq_type(arg) for arg in args)
##        arg_types = self._apply_default_types(arg_types)
##        return self._get_concrete_fn_final(arg_types)
##    
##    def get_concrete_fn(self, *arg_types):
##        """Returns a concrete function for the provided argument types.
##        
##        Defaults are applied and the types of the global values of free 
##        variables are used. 
##        
##        This is mostly useful for inspecting source code.
##        """
##        return self._get_concrete_fn(arg_types)
##    
##    @cypy.memoize
##    def _get_concrete_fn(self, arg_types):
##        return self._get_concrete_fn_final(self._apply_default_types(arg_types))
##    
##    def _apply_default_args_and_types(self, args):
##        # yields a full sequence of arg, arg_type pairs given args
##        # does not filter out lifted constants or include implicit arguments
##        
##        # provided args
##        for arg in args:
##            arg_type = infer_clq_type(arg)
##            yield arg, arg_type
##            
##        # defaults
##        n_provided = len(args)
##        n_args = len(self.explicit_arg_names) # constants were filtered out in this step
##        n_defaults = n_args - n_provided
##        if n_defaults < 0:
##            raise Error("Too many arguments were specified for %s."
##                        % self.name)
##        elif n_defaults > 0:
##            defaults = self.defaults
##            default_types = self.default_types
##            for i in xrange(n_defaults):
##                yield defaults[i], default_types[i]
##    
##    @cypy.memoize
##    def _apply_default_types(self, arg_types):
##        # (type-only analag of _apply_default_args_and_types above)
##        
##        # provided args
##        for arg_type in arg_types:
##            yield arg_type
##            
##        # defaults
##        n_provided = len(arg_types)
##        n_args = len(self.explicit_arg_names)
##        n_defaults = n_args - n_provided
##        if n_defaults < 0:
##            raise Error("Too many arguments were specified for %s." %
##                        self.name)
##        elif n_defaults > 0:
##            default_types = self.default_types
##            for i in xrange(n_defaults):
##                yield default_types[i]
##        
##    @cypy.memoize
##    def _get_concrete_fn_final(self, arg_types):
##        # lift arguments which must be constants to constants
##        constants = dict(self._all_constants)
##        arg_types = tuple(arg_types)
##        if arg_types:
##            # need all these conditionals because zip(*) will spit out a single 
##            # empty tuple if provided an empty tuple and then Python will barf 
##            # at the destructuring assignment
##            filtered_arg_types = tuple(self._filter_arg_types(arg_types, 
##                                                              constants))
##            if filtered_arg_types:
##                arg_names, arg_types = zip(*filtered_arg_types)
##            else:
##                arg_names, arg_types = ()
##        else:
##            arg_names = arg_types # empty tuple already
##            
##        # generate source
##        visitor = _generate_cl.ProgramItemVisitor(self, arg_names, arg_types,
##                                                  constants)
##        visitor.visit(self.annotated_ast)
##        
##        # produce ConcreteFn
##        return ConcreteFn(visitor)
##    
##    def _filter_arg_types(self, arg_types, constants):
##        for arg_name, arg_type in zip(self.explicit_arg_names, arg_types):
##            try:
##                constant_value = arg_type.constant_value
##            except AttributeError:
##                yield arg_name, arg_type
##            else:
##                constants[arg_name] = constant_value
##                
##    def _filter_args(self, args, concrete_fn):
##        # filter out actual arguments if that argument has become a constant
##        constants = concrete_fn.constants
##        for arg_name, arg in zip(self.explicit_arg_names, args):
##            if not constants.has_key(arg_name):
##                yield arg
##        
################################################################################
##    ############################################################################
##    # Programs, Program Items and Source
##    ############################################################################    
##    @cypy.memoize
##    def generate_program(self, ctx, options=""):
##        """Creates an :class:`cl.Program` object for this function.""" 
##        return ctx.compile(self.program_source, options)
##    
##    @cypy.lazy(property)
##    def program_source(self):
##        """The source code of the program produced by this function."""
##        return "\n\n".join(item.source for item in self.program_items)
##        
##    @cypy.lazy(property)
##    def fn_source(self):
##        """The source code of this function."""
##        return self.program_item.source
##    
##    ############################################################################
##    # Calling
##    ############################################################################
##    @cypy.memoize
##    def generate_kernel(self, ctx, options=''):
##        """Creates a program and extracts this function as a callable 
##        :class:`cl.Kernel` object.
##                        
##        ``ctx``
##            The :class:`cl.Context` to create the Program under. If not
##            specified, the default context (cl.ctx) must be specified and 
##            is used.
##            
##        ``options``
##            The compiler options to pass to :meth:`cl.Context.compile`.
##        
##        """
##        return getattr(self.generate_program(ctx, options), 
##                       self.fullname)
##        
##    def __call__(self, *args, **kwargs):
##        """Creates a program, extracts the kernel and calls it."""
##        return self._do_call(args, kwargs)
##    
##    def _do_call(self, args, kwargs):
##        if not self.is_kernel:
##            raise Error("Cannot call a non-kernel cl.oquence function.")
##        
##        # include downstream implicit variables
##        args = cypy.cons(args, self.implicit_args)
##        
##        # grab context and options
##        try: ctx = kwargs.pop('ctx')
##        except KeyError: ctx = cl.ctx
##        options = kwargs.pop('options', '')
##        
##        # generate a kernel        
##        kernel = self.generate_kernel(ctx, options)
##        
##        # send global size the way pyopencl likes it
##        global_size = kwargs.pop('global_size')
##        
##        # get queue
##        try: queue = kwargs.pop('queue')
##        except KeyError: queue = ctx.queue
##        
##        # call the kernel
##        return kernel(queue, global_size, *args, **kwargs)
##    
#
#literal_suffixes = {
#    'uc': cl_uchar,
#    'c': cl_char,
#    'us': cl_ushort,
#    's': cl_short,
#    'ui': cl_uint,
#    'i':  cl_int,
#    'uL': cl_ulong,
#    'L': cl_long,
#    'h': cl_half,
#    'f': cl_float,
#    'd': cl_double
#}
#"""A map from numeric literal suffixes to their correspond 
#`type <cl.ScalarType>`."""
