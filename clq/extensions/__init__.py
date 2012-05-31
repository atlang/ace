import clq
import cypy

class Grammar(clq.Type):
    """ Grammar types should be created using Grammar.factory, and not instantiated directly. """
    
    @classmethod
    def factory(cls, backend, regex):
        """ This function should be interned s/t that hashing function returned based upon
            regex equivalence. """
        #make a grammar that otherwise behaves as a string. 
        GrammarType = type("Grammar[" + regex + "]", (Grammar,backend.string_type(),), {})
        
        g = GrammarType(None)
        g._backend = backend
        g._regex = regex
        g.name = backend.string_t.name

        return g
            
    @cypy.memoize
    def includes(self, right_grammar):
        """ Returns true iff this grammar includes the right_grammar. Symmetry in includes 
            implies equivalence, so that will be the test used for interning the factory method. """
        return isinstance(right_grammar, Grammar) #TODO
    
    def has_subtype(self, candidate_subtype):
        return self.includes(candidate_subtype)
    
    def coerce_to(self, supertype):
        if(supertype.has_subtype(self)):
            new_type = self
            new_type._regex = supertype._regex
            return new_type
        else:
            return None
    
    