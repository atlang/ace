import clq
import cypy
import cypy.astx as astx
import clq.extensions.regex as regex
import ast as _ast

class ConstrainedString(clq.Type):
    """"Regular expression types."""        

    def __init__(self, backend, regex):
        self._backend = backend
        self._regex = regex
        self.name = self._backend.string_t.name
    
    @classmethod
    def regex_to_name(cls, name):
        ret_val = ""
        for c in name:
            if c == ".":
                ret_val += "Dot"
            elif c == "+":
                ret_val += "Plus"
            elif c == "*":
                ret_val += "Kleene"
            elif c == "?":
                ret_val += "Question"
            elif c == "(":
                ret_val += "LP"
            elif c == ")":
                ret_val += "RP"
            else:
                ret_val += c
        return ret_val
    
    def __eq__(self, right):
        return self.includes(right) and right.includes(self)
    
    @classmethod
    def factory(cls, backend, regex_str):
        """ Returns the singleton type associated backend and regex_str. """ 
        return get_singleton_language_type(cls,backend,regex_str)
    
    def includes(self, right):
        """ Returns true iff this language includes the right language. """        
        if not isinstance(right, ConstrainedString):
            return False
        
        leftNFA  = regex.NFA.parse(regex.Pattern(self._regex).get_regex())
        rightNFA = regex.NFA.parse(regex.Pattern(right._regex).get_regex())
        return rightNFA.included_in(leftNFA)
    
    def is_subtype(self, candidate_subtype):
        if self == candidate_subtype: return True
        return self.includes(candidate_subtype)

    #generate is implemented in the backend.    
    def resolve_BinOp(self,context,node):
        if not isinstance(node.op, _ast.Add):
            raise clq.TypeResolutionError("Operation %s is not supported on " +
                                          "Strings" % str(node.op), node)
        
        right_type = node.right.unresolved_type.resolve(context)
        try:
            return self._resolve_BinOp(node.op, right_type, context.backend)
        except clq.TypeResolutionError as e:
            if e.node is None:
                e.node = e
            raise e
    
    def _resolve_BinOp(self, op, right_type, backend):
        if isinstance(right_type, ConstrainedString):
            return ConstrainedString(self._backend, "(%s)(%s)" % 
                                        (self._regex,right_type._regex))
        else:
            raise clq.TypeResolutionError("Must be a ConstrainedString",node)
        
    def coerce(self, supertype):
        if self == supertype:
            return self
        
        if(supertype.is_subtype(self)):
            new_type = ConstrainedString(self._backend, supertype._regex)
            return new_type
        else:
            return None
    
    def generate_cast(self, context, node):
        term = node.args[0].unresolved_type.resolve(context)
        type = node.args[1].unresolved_type.resolve(context)
        return self._backend.check_ConstrainedString_cast(context,node)
    
    def generate_BinOp(self,context,node):
        return self._backend.string_type()(
                self._backend.string_t).generate_BinOp(context,node)
    def resolve_Return(self,context,node):
        return self._backend.string_type()(
                self._backend.string_t).resolve_Return(context,node)
    def generate_Return(self,context,node):
        return self._backend.string_type()(
                self._backend.string_t).generate_Return(context,node)
    def validate_Assign(self,context,node):
        return self._backend.string_type()(
                self._backend.string_t).validate_Assign(context,node)
    def generate_Assign(self, context, node):
        return self._backend.string_type()(
                self._backend.string_t).generate_Assign(context,node)
cypy.intern(ConstrainedString)

  