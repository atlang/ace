class Corpus(object):
	"""Represents the n-gram frequencies derived from some corpus."""
	def __init__(self, data):
		self.data = data

	data = None
	"""A dictionary containing counts."""

	@classmethod
	def from_file(cls, file):
		# TODO: read file
		return cls.from_lines(s)

	@classmethod
	def from_lines(cls, lines):
		corpus = Corpus({})

		count = None
		tokens = None
		
	    for line in lines:
	    	if count is None:
	    		tokens = tokenize(line)
	    	else:
	    		corpus.set_count(tokens, count)
	    		count = None
	    		
	    return corpus
	    
	def set_count(self, tokens, count):
		"""Sets the count of the given sequence of tokens."""
		cur = self.data
		tokens = list(tokens) # copy it so we can pop in loop
		while len(tokens) > 1:
			token = token.pop(0)
			try:
				cur = cur[token]
			except KeyError:
				cur = cur[token] = { }

		cur[tokens[0]] = count

	def get_count(self, tokens):
		"""Returns the count of the given sequence of tokens.

		Sums over the leaves if tokens is a partial sequence.
		"""
		data = self.data
		tokens = list(tokens) # copy it so we can pop in loop
		while len(tokens) > 1:
			token = token.pop(0)
			try:
				cur = cur[token]
			except KeyError:
				return 0

		c = cur[tokens[0]]
		if isinstance(c, dict):  # TODO: use correct way of checking for dictionary
			return sum_leaves(c) # TODO: implement sum_leaves
		else:
			return c 
		return cur[tokens[0]]	

	def prob(self, token, lead_tokens):
		"""Returns the probability of the given tokens given the lead tokens.

			>>> corpus.prob('in', ['the', 'cat'])
			0.9
		"""
		lead_count = float(self.get_count(lead_tokens))
		tokens = list(lead_tokens); tokens.append(token)
		count = float(self.get_count(tokens))
		return count / lead_count

# TODO: write tests

