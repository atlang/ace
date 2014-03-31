def sum_leaves(d):
    """Sums up the leaves of a nested dictionary."""
    sum = 0
    for value in d.itervalues():
        if isinstance(value, dict):   # TODO: use correct checks
            sum += sum_leaves(value)
        elif isinstance(value, int):  # TODO: check for numbers more generally
            sum += value
    return sum

class Corpus(object):
    """Represents the n-gram frequencies derived from some corpus."""
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data

    data = None
    """A dictionary containing counts."""

    @classmethod
    def from_cmulm_filename(cls, filename):
        return cls.from_cmulm_lines(open(filename).readlines())

    @classmethod
    def from_cmulm_lines(cls, lines, separator=" "):
        """Creates a corpus from a sequence of lines produced by the CMULM library.

        That is, files of the format:

            tokens
            count
            tokens
            count
            ...

        Where tokens is a separator-separated sequence of tokens and count is the 
        count of the sequence of tokens on the previous line.
        """
        corpus = Corpus({})

        tokens = None
        
        for line in lines:
            if tokens is None:
                tokens = line.strip().split(separator)
            else:
                count = int(line)
                corpus.set_count(tokens, count)
                assert corpus.get_count(tokens) == count
                tokens = None
                
        return corpus
        
    def set_count(self, tokens, count):
        """Sets the count of the given sequence of tokens."""
        cur = self.data
        tokens = list(tokens) # copy it so we can pop in loop
        while len(tokens) > 1:
            token = tokens.pop(0)
            try:
                cur = cur[token]
            except KeyError:
                cur[token] = { }
                cur = cur[token]
        cur[tokens[0]] = count

    def get_count(self, tokens):
        """Returns the count of the given sequence of tokens.

        Sums over the leaves if tokens is a partial sequence.
        """
        cur = self.data
        if len(tokens) == 0:
            return sum_leaves(cur)

        tokens = list(tokens) # copy it so we can pop in loop
        while len(tokens) > 1:
            token = tokens.pop(0)
            try:
                cur = cur[token]
            except KeyError:
                return 0

        try:
            c = cur[tokens[0]]
        except KeyError:
            return 0
        else:
            if isinstance(c, dict):  # TODO: use correct way of checking for dictionary
                return sum_leaves(c)
            else:
                return c

    def prob(self, token, prefix):
        """Returns the probability of the given token given the lead tokens.

            >>> corpus.prob('in', ['the', 'cat'])
            0.9

        """
        prefix_count = float(self.get_count(prefix))
        tokens = list(prefix); tokens.append(token)
        count = float(self.get_count(tokens))
        if prefix_count == 0:
            return 0
        else:
            return count / prefix_count

    def seq_prob(self, tokens, prefix):
        """Returns the probability of a given sequence given the lead tokens."""
        assert len(tokens) > 0
        prefix = list(prefix)
        p = 1.0
        for token in tokens:
            p *= self.prob(token, prefix)
            prefix.pop(0)
            prefix.append(token)
        return p

def test_filename(filename):
    corpus = Corpus.from_cmulm_filename(filename)
    print corpus.get_count(["!=", "null"])
    print corpus.prob("&&", ["!=", "null"])
    print corpus.seq_prob(["%", "ROW_MAX)", "==", "ROW_MAX", "-", "1)"], ["if", "((i"])

# TODO: pull this out into another file
#import cypy.ngram
import re, numpy

def tokenize(expr):
    return [x for x in re.split(r"(\W)", expr) if re.match(r"\w", x)]

def test_expressions(corpus_filename, test_filename):
    corpus = Corpus.from_cmulm_filename(corpus_filename)
    lines = open(test_filename).readlines()
    prob = numpy.empty((len(lines),))
    for i, line in enumerate(lines):
        try:
            prefix1, prefix2, expr = line.strip().split(" ", 2)
        except ValueError:
            print "BAD"
            prob[i] = 0.0
            continue
        prefix = [prefix1, prefix2]
        tokens = tokenize(expr)
        prob[i] = corpus.seq_prob(tokens, prefix)

    return prob

def process_flavio_data(filename, training_dir, training_out, test_out):
    lines = open(filename).readlines()
    num_training_files = int(lines[0])
    training_files = []
    for i in xrange(num_training_files):
        training_files.append(lines[i + 1].strip())
    write_training_file(training_files, training_dir, training_out)
    test_lines = lines[i + num_training_files + 1:]
    write_test_file(test_lines, test_out)

def write_training_file(training_files, training_dir, training_out):
    training = ""
    for f in training_files:
        training += open(training_dir + f).read()
    with open(training_out, 'w') as f:
        f.write(training)

def write_test_file(test_lines, test_out):
    test = "".join(test_lines)
    with open(test_out, 'w') as f:
        f.write(test)

def run_tests(n, corpus_filename_fmt, test_filename_fmt):
    probs = [ ]
    for i in xrange(n):
        prob = test_expressions(corpus_filename_fmt % i, test_filename_fmt % i)
        probs.append(numpy.mean(prob))
    print numpy.mean(probs)

if __name__ == "__main__":
    import sys
    try:
        filename = sys.argv[1]
    except:
        print "Need a filename to test with."
    else:
        test_filename(filename)
