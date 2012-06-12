import clq
import cypy
import cypy.astx as astx
import clq.extensions.regex as regex
      
class Language(clq.Type):
    """ Langauge types should be created using Language.factory, and not instantiated directly. """
    
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
        #inherit from Language and string.
        LangType = type("Lang_" + Language.regex_to_name(regex), (Language,backend.string_type(),), {})
        
        g = LangType(None)
        g._backend = backend
        g._regex = regex
        g.name = Language.regex_to_name(g._regex)

        return g
            
    def includes(self, right):
        """ Returns true iff this language includes the right language. """
        if not isinstance(right, Language):
            return False
        
        leftNFA  = regex.NFA.parse(regex.Pattern(self._regex).get_regex())
        rightNFA = regex.NFA.parse(regex.Pattern(right._regex).get_regex())
        return rightNFA.included_in(leftNFA)
    
    def is_subtype(self, candidate_subtype):
        return self.includes(candidate_subtype)

    def get_coerced(self, supertype):
        if self == supertype:
            return self
        
        if(supertype.is_subtype(self)):
            new_type = Language.factory(self._backend, supertype._regex)
            return new_type
        else:
            return None
