import clq
import cypy
import cypy.astx as astx
      
class Grammar(clq.Type):
    """ Grammar types should be created using Grammar.factory, and not instantiated directly. """
    
    @classmethod
    def regex_to_name(cls, name):
        ret_val = ""
        for c in name:
            if c == ".":
                ret_val += "Dot"
            if c == "+":
                ret_val += "Plus"
            if c == "*":
                ret_val += "Kleene"
        return ret_val
    
    @classmethod
    @cypy.intern
    def factory(cls, backend, regex):
        """ This function should be interned s/t that hashing function returned based upon
            regex equivalence. """
        #inherit from grammar and string.
        GrammarType = type("Grammar_" + Grammar.regex_to_name(regex), (Grammar,backend.string_type(),), {})
        
        g = GrammarType(None)
        g._backend = backend
        g._regex = regex
        #g.name = backend.string_t.name
        g.name = Grammar.regex_to_name(g._regex)

        return g
            
    @cypy.memoize
    def includes(self, right_grammar):
        """ Returns true iff this grammar includes the right_grammar. Symmetry in includes 
            implies equivalence, so that will be the test used for interning the factory method. """
        return isinstance(right_grammar, Grammar) #TODO
    
    def has_subtype(self, candidate_subtype):
        return self.includes(candidate_subtype)

    def coerce_to(self, supertype):
        if self == supertype:
            return self
        
        if(supertype.has_subtype(self)):
            new_type = Grammar.factory(self._backend, supertype._regex)
            return new_type
        else:
            return None
