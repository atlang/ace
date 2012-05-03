"""Core library for cl.oquence."""

import clq

@clq.fn
def identity(x):
    #"""The identity function."""
    return x

@clq.fn
def plus(a, b):
    #"""The binary plus operator."""
    return a + b

@clq.fn
def minus(a, b):
    #"""The binary minus operator."""
    return a - b

@clq.fn
def mul(a, b):
    #"""The binary multiplication operator."""
    return a * b

@clq.fn
def div(a, b):
    #"""The binary division operator."""
    return a / b

################################################################################
# Random Number Generation
################################################################################
@clq.fn
def simple_randf(state):
    """A simple random number generator."""
    gid = get_global_id(0)
    x = state[gid] * 0xFD43FD + 0xC39EC3
    state[gid] = x
    return (x*.000000000465662+1.0000012)*0.5

def _simple_randf_initializer(size):
    import numpy
    return numpy.random.random_integers(16777215, size=size).astype(numpy.int32)
simple_randf.initializer = _simple_randf_initializer
    
@clq.fn
def randexp(state, randf=simple_randf):
    """Generates an exponential random number."""
    return -log(randf(state)) #@UndefinedVariable

@clq.fn
def randn(state, randf=simple_randf):
    """Generates a normal random number."""
    u1 = randf(state)
    u2 = randf(state)
    r = sin(6.28318531*u2)*sqrt(-2.0*log(u1)) #@UndefinedVariable
    if r > 6.0 or isnan(r): #@UndefinedVariable
        return 6.0
    else:
        return r
