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
