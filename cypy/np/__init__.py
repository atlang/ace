"""Utility functions related to numerics and the numpy package."""

import random

import numpy
import cypy as py

int_sizeof = numpy.dtype("int").itemsize
"""The size of the int type in bytes."""

int_size_bits = int_sizeof * 8
"""The size of the int type in bits."""

float_sizeof = numpy.dtype("float").itemsize
"""The size of the float type in bytes."""

float_size_bits = float_sizeof * 8
"""The size of the float type in bits."""

## Matrix stuff
class JaggedMatrix(list):
    def __init__(self, n_rows=0):
        super(JaggedMatrix, self).__init__()
        self.append_rows(n_rows)

    row_type = list

    def append_row(self):
        self.append(self.row_type())

    def append_rows(self, n):
        if n > 0: self.extend(self.row_type() for _ in xrange(n))

class DirectedAdjacencyMatrix(JaggedMatrix):
    def __init__(self, n_rows=0, dtype=numpy.int32, *args, **kwargs):
        JaggedMatrix.__init__(self, n_rows, *args, **kwargs)
        self.dtype = dtype

    def connect_randomly(self, p, (src_start, src_end)=(0, None),
                                  (target_start, target_end)=(0, None)):
        rows = len(self)
        if src_end is None: src_end = rows
        if target_end is None: target_end = rows

        assert 0 <= src_start <= src_end <= rows
        assert 0 <= target_start <= target_end <= rows
        assert 0.0 <= p <= 1.0

        src_num = src_end - src_start
        target_num = target_end - target_start

        degree = numpy.random.binomial(target_num, p, src_num)

        for i in py.prog_iter(xrange(src_num)):
            sample = random.sample(xrange(target_start, target_end), degree[i])
            py.include_many(self[src_start + i], sample)

    @property
    def packed(self):
        """
        each row is placed side-by-side with the length of the row interlaced
        the head of the packed matrix contains offsets to this length
        e.g. [[11, 22, 33], [44, 55], []] => [3, 7, 10, 3, 11, 22, 33, 2, 44, 55, 0]
        """
        # not the most efficient implementation atm but whatever
        n_rows = len(self)
        size = len(self)*2 + self.n_edges
        packed = numpy.empty(size, self.dtype)
        offset = n_rows
        for r, row in enumerate(self):
            packed[r] = offset
            n_edges = len(row)
            packed[offset] = n_edges
            packed[(offset+1):(offset+1+n_edges)] = numpy.fromiter(row,
                                                                   self.dtype)
            offset += 1 + n_edges
        return packed
    
    def reversed(self):
        """Create a connectivity matrix where each incoming edge becomes outgoing."""
        n_rows = len(self)
        reversed = DirectedAdjacencyMatrix(n_rows, self.dtype)
        for r, row in enumerate(py.prog_iter(self)):
            for c in row:
                reversed[c].append(r)
                
        return reversed
    
    @property
    def degrees(self):
        return (len(x) for x in self)

    @property
    def n_edges(self):
        return sum(self.degrees)

if __name__ == "__main__":
    # GENERATE CONNECTIVITY MATRIX
    N = 4000 # number of neurons
    Ne = 3200 # number of exc. neurons
    Ni = N - Ne # number of inh. neurons
    rangee = (0, Ne)
    rangei = (Ne, N)
    pee, pei, pie, pii = 0.15, 0.4, 0.4, 0.4

    cm = DirectedAdjacencyMatrix(N)
    cm.connect_randomly(pee, rangee, rangee)
    cm.connect_randomly(pei, rangee, rangei)
    cm.connect_randomly(pie, rangei, rangee)
    cm.connect_randomly(pii, rangei, rangei)
    packed_cm = cm.packed()
    print packed_cm
