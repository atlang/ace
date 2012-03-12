import clq.backends.base_c as base_c

class C99(base_c.BaseC):
    def __init__(self):
        base_c.BaseC.__init__(self, 'C99')
        
    void_t = void
    int_t = int
    float_t = double
    string_t = char.ptr

