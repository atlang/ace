import clq.backends.base_c as base_c

class C99(base_c.BaseC):
    def __init__(self):
        base_c.BaseC.__init__(self, 'C99')
        
    void_t = base_c.void
    int_t = base_c.int
    float_t = base_c.double
    string_t = base_c.char.ptr

