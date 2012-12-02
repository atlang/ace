def sum_leaves(d):
    """Sums up the leaves of a nested dictionary."""
    sum = 0
    for value in d.itervalues():
        if isinstance(value, dict):   # TODO: use correct checks
            sum += sum_leaves(value)
        elif isinstance(value, int):
            sum += value
    return sum

class Corpus(object):
    """Represents the n-gram frequencies derived from some corpus."""
    def __init__(self, data):
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

        c = cur[tokens[0]]
        if isinstance(c, dict):  # TODO: use correct way of checking for dictionary
            return sum_leaves(c)
        else:
            return c

    def prob(self, token, lead_tokens):
        """Returns the probability of the given tokens given the lead tokens.

            >>> corpus.prob('in', ['the', 'cat'])
            0.9

        """
        lead_count = float(self.get_count(lead_tokens))
        tokens = list(lead_tokens); tokens.append(token)
        count = float(self.get_count(tokens))
        return count / lead_count

def test_filename(filename):
    lines = open(filename).readlines()
    corpus = Corpus.from_cmulm_lines(lines)
    print corpus.get_count(["!=", "null"])
    print corpus.prob("&&", ["!=", "null"])

if __name__ == "__main__":
    import sys
    try:
        filename = sys.argv[1]
    except:
        print "Need a filename to test with."
    else:
        test_filename(filename)
