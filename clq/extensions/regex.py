import cypy
from itertools import *
import copy

class Pattern:
    """Regular Expressions used to specify grammar types. 

    Symbols follow (strongest to weakest binding):
        () - grouping

        . - single wild card

          - concatenation

        * - Kleene Operator
        + - shorthand; a+ = a(a*)
        ? - 0 or 1
        
            | - alternative
    """
    def __init__(self, pattern):
        self.pattern = pattern

    def included_in(self, right):
        """Returns true iff self is a sublanguage of right. """
        left_nfa = NFA.parse(self.get_regex())
        right_nfa = NFA.parse(right.get_regex())
        return left_nfa.included_in(right_nfa)
    
    def at(self, n):
        """Returns an | containing all possible characters at position n """
        nfa = NFA.parse(self.get_regex())
        return nfa.pattern_of_char_at(n)
    
    def __eq__(self, other):
        """ Equivalence is bidirectional inclusion. """ 
        return self.included_in(right) and right.included_in(self)

    def get_regex(self):
        """Gets a regular expression AST from the pattern """
        regex = RegexParser().parse(self.pattern)
        return regex

    def match(self, string):
        """Normal pattern matching """
        regex = self.get_regex()
        return regex.match(regex,string)

#######################################################
#              REGEX -> AST                           #
#######################################################
class ParserException(Exception):
    def __init__(self, msg):
        Exception.__init__(self,msg)

class RegexParser:
    """Regex -> AST"""
    def __init__(self):
        self.sym_WildCard       = "."
        self.sym_LP             = "("
        self.sym_RP             = ")"
        self.sym_Alternative    = "|"
        self.sym_Kleene         = "*"
        self.sym_AtLeastOne     = "+"
        self.sym_NoMoreThanOne  = "?"
        self.sym_Escape         = "\\"
         
    def parse(self, pattern):
        """base case. 
        
        ? and + are represented using | and *.
        """
        
        if len(pattern) == 0:
            return Empty()
        
        c = pattern[0]
        
        if c == self.sym_LP: 
            count = 1
            for i in range(len(pattern)):
                if i == 0:
                    continue
                if pattern[i] == self.sym_LP:
                    count += 1
                if pattern[i] == self.sym_RP:
                    count -= 1
                    if count == 0:                         
                        regex = self.parse(pattern[1:i])
                        if isinstance(regex, Combination):
                            regex.atomized = True
                        if len(pattern) == i+1:
                            return regex
                        else:
                            return self._parse(regex , pattern[i+1:])
        
        elif c == self.sym_RP:
            raise("Error: unmatches right paren.")
        
        elif c == self.sym_WildCard:
            return self._parse(WildCard(), pattern[1:])
        
        elif c == self.sym_Alternative or c == self.sym_AtLeastOne or  \
        c == self.sym_Kleene or c == self.sym_NoMoreThanOne:
            raise ParserException("Invalid beginning token: %s" % (c))
        
        elif c == self.sym_Escape:
            return self._parse(Character(pattern[1]), pattern[2:])
        
        else:
            return self._parse(Character(pattern[0]), pattern[1:])             
                
    def _parse(self, regex, remaining):
        """Recurrence"""
        if len(remaining) == 0:
            return regex

        #remaining = portion of the initial pattern that hasn't been matched.
        c = remaining[0] 
        if c == self.sym_Alternative:
            return Alternative(regex, self.parse(remaining[1:]))
        
        elif c == self.sym_AtLeastOne:
            if isinstance(regex,Combination) and not regex.atomized:
                #bind * before seq
                regex.right = Sequence(Repetition(regex.right), regex.right) 
            else:
                #reptetition must come first.
                regex = Sequence(Repetition(regex), regex) 
            regex.atomized = True
            
            if len(remaining) > 1:
                return self._parse(regex, remaining[1:])
            else:
                return regex
        
        
        elif c == self.sym_Kleene:
            if isinstance(regex,Combination) and not regex.atomized:
                #bind * before seq
                regex.right = Repetition(regex.right) 
            else:
                regex = Repetition(regex)
            regex.atomized = True
            
            if len(remaining) > 1:
                return self._parse(regex, remaining[1:])
            else:
                return regex
        
        elif c == self.sym_LP: 
            return Sequence(regex, self.parse(remaining))
    
        elif c == self.sym_NoMoreThanOne:
            if isinstance(regex,Combination) and not regex.atomized:
                #bind * before seq
                regex.right = Alternative(Empty(), regex.right) 
            else:
                regex = Alternative(Empty(), regex)
            regex.atomized = True
            
            if len(remaining) > 1:
                return self._parse(regex, remaining[1:])
            else:
                return regex
        
        elif c == self.sym_RP:
            return self._parse(regex, remaining[1:])
            #TODONF check to make sure we don't have extra RPs around.
            #raise ParserException("Found unmatched right paren")
        
        elif c == self.sym_WildCard:
            regex = Sequence(regex, WildCard())
            return self._parse(regex, remaining[1:])         
        
        elif c == self.sym_Escape:
            regex = Sequence(regex, Character(remaining[1]))
            return self._parse(regex, remaining[2:])
        
        else:
            regex = Sequence(regex, Character(remaining[0]))
            return self._parse(regex, remaining[1:])
            
# AST + matching
class Regex:
    """AST + Matching
    
    Avoided a bit of reinventing the wheel.
    This is the equivalence test, due to 
    http://morepypy.blogspot.com/2010/05/efficient-and-elegant-regular.html
    """
    def __init__(self, empty):
        self.marked = False
        self.empty = empty

    def gv_code(self):
        pass
    
    def reset(self):
        self.marked = False

    def shift(self,c,marked):
        self.marked = self._shift(c,marked)
        return self.marked

    def match(self,re,s):
        if not s:
            if self.empty: return True
            if isinstance(re, Combination):
                return re.left.empty and re.right.empty
            return False
        result = re.shift(s[0],True)
        for c in s[1:]:
            result = re.shift(c,False)
        re.reset()
        return result
    pass

class Character(Regex):
    
    def __init__(self, c):
        Regex.__init__(self, False)
        self.c = c

    def _shift(self,c,mark):
        return mark and c == self.c

class WildCard(Regex):
    def __init__(self):
        Regex.__init__(self, False)
    def _shift(self,c,mark):
        return mark

class Empty(Regex):
    def __init__(self):
        Regex.__init__(self,True)
    def _shift(self,c,mark):
        return False

class Combination(Regex):
    def __init__(self,left,right,empty):
        Regex.__init__(self,empty)
        self.left = left
        self.right = right
        self.atomized = False
    def reset(self):
        self.left.reset()
        self.right.reset()
        Regex.reset(self)

class Alternative(Combination):
    def __init__(self, left, right):
        empty = left.empty or right.empty
        Combination.__init__(self, left, right, empty)

    def _shift(self, c, mark):
        marked_left  = self.left.shift(c, mark)
        marked_right = self.right.shift(c, mark)
        return marked_left or marked_right

class Repetition(Regex):
    def __init__(self, re):
        Regex.__init__(self, True)
        self.re = re

    def _shift(self, c, mark):
        return self.re.shift(c, mark or self.marked)

    def reset(self):
        self.re.reset()
        Regex.reset(self)

class Sequence(Combination):
    def __init__(self, left, right):
        empty = left.empty and right.empty
        Combination.__init__(self, left, right, empty)

    def _shift(self, c, mark):
        old_marked_left = self.left.marked
        marked_left = self.left.shift(c, mark)
        marked_right = self.right.shift(
            c, old_marked_left or (mark and self.left.empty))
        return (marked_left and self.right.empty) or marked_right
    

#######################################################
#                      Inclusion                      #
#######################################################
class TransitionFunction:
    """ {state,input} -> new_state"""
    def __init__(self, state, input, new_state):
        self.state = state
        self.input = input
        self.new_state = new_state
    
class NFA:
    """NFA, regex AST -> NFA, NFA -> DFA"""
    def __init__(self):
        self.q0 = None              # start state
        self.q      = list()        # states (Q)
        self.transitions = list()   # transition function
        self.final_states = list()  # final state.
    
    def pattern_of_char_at(self, n):
        if(n == 0): return Pattern("") #base
        
        states = list()
        states.append(self.q0)
        for i in range(n-1):
            new_states = list()
            for t in self.transitions:
                if t.state in states and not t.new_state in new_states:
                    new_states.append(t.new_state)
            states = new_states
        
        possible_chars = list()
        for t in self.transitions:
            if t.state in states and not t.input in possible_chars:
                possible_chars.append(t.input)
        
        regex_str = ""
        for char in possible_chars:
            regex_str = regex_str + char + "|"
        return Pattern(regex_str[:-1])
            
    def copy(self):
        nfa = NFA()
        nfa.q0 = self.q0
        for q in self.q: nfa.q.append(q)
        for t in self.transitions: nfa.add_transition(t.state, 
                                                      t.input, 
                                                      t.new_state)
        for f in self.final_states: nfa.final_states.append(f)
        return nfa
    
        
    def gv_code(self):
        q0_printed = False
        print "digraph G {"
        for f in self.final_states:
            if f == self.q0:
                print "\t%s [peripheries=2 color=\"crimson\"];" % f
                q0_printed = True
            else:
                print "\t%s [peripheries=2];" % f
        if not q0_printed: print "\t%s [color=\"crimson\"];" % self.q0
        
        for t in self.transitions:
            print "\t%s -> %s [label=\"%s\"];" % (t.state, t.new_state, t.input)
        print "}"
    
    def pretty_printer(self,name):
        print "-- %s --" % name
        print "Initial State: %s" % self.q0
        print "Final States:"
        for s in self.final_states:
            print "\t%s" % str(s)
        print "Delta:"
        for t in self.transitions:
            print "\t%s -%s> %s" % (t.state, t.input, t.new_state)
        print "--"
        
    def largest_state(self):
        largest = 0
        for i in self.q:
            if i > largest:
                largest = i
        largest += 1
        return largest
    
    def add_transition(self, source, input, dest):
        if source == None or dest == None:
            raise Exception("Need a source and a destination.")
        self.transitions.append(TransitionFunction(source,input,dest))
    
    
    
    @classmethod
    def parse(cls, regex):
        """regex AST -> NFA"""
        if isinstance(regex,Character):
            n = NFA()
            n.q0 = 0
            n.q.append(n.q0)
            n.q.append(1)
            n.add_transition(0,regex.c,1)
            n.final_states.append(1)
            
            return n
        
        elif isinstance(regex,WildCard):
            n = NFA()
            n.q0 = 0
            n.q.append(n.q0)
            n.q.append(1)
            n.add_transition(0,None,1)
            n.final_states.append(1)
            return n
        
        elif isinstance(regex, Sequence):
            nl = NFA.parse(regex.left)  #returning this
            nr = NFA.parse(regex.right)
            
            offset = nl.largest_state() 
            #copy states
            for state in nr.q:
                nl.q.append(state + offset)
            #copy transitions
            for t in nr.transitions:
                nl.add_transition(t.state + offset, 
                                  t.input, 
                                  t.new_state + offset)
                            
            #remove the final states of nl and update
            #transitions to point to nr.q0 instead.
            for t in nl.transitions:
                if t.new_state in nl.final_states:
                    t.new_state = nr.q0 + offset
                if t.state in nl.final_states:
                    t.state = nr.q0 + offset
    
            #remove all of the left's final states.
            for f in nl.final_states:
                nl.q.remove(f)

            #update final states of nl with the final states of nr.
            nl.final_states = list()
            for f in nr.final_states:
                nl.final_states.append(f + offset)
            
            #Initial state will have been deleted if it was also a final state.
            if nl.q0 not in nl.q:
                nl.q0 = nr.q0 + offset
                    
            return nl
        
        elif isinstance(regex, Alternative):
            #replace transitions out of the 
            #right q0 with the transitions out of the right q0 
            
            nl = NFA.parse(regex.left)
            nr = NFA.parse(regex.right)
            
            new_q0 = nl.largest_state()
            offset = new_q0 + 1
            
            #copy states,transitions,finals from nr to nl
            for state in nr.q:
                nl.q.append(state + offset)
            for t in nr.transitions:
                nl.add_transition(t.state + offset, 
                                  t.input, 
                                  t.new_state + offset)
            for f in nr.final_states:
                nl.final_states.append(f + offset)
            
            #nl.q0 -> z => new_q0 -> z and similarly for nr.q0
            for t in nl.transitions:
                if t.state == nl.q0: nl.add_transition(new_q0, 
                                                       t.input, 
                                                       t.new_state)
                if t.state == nr.q0 + offset : nl.add_transition(new_q0, 
                                                                 t.input, 
                                                                 t.new_state)
            
            #make new_q0 the new initial
            if nl.q0 in nl.final_states or nr.q0 in nr.final_states: 
                nl.final_states.append(new_q0)
            nl.q.append(new_q0)
            nl.q0 = new_q0
            
            return nl        
        
        elif isinstance(regex, Repetition):
            #replace transitions to final states with
            #transitions to q0 and replace final states with q0
            n = NFA.parse(regex.re)
                
            for t in n.transitions:
                if t.state in n.final_states:
                    t.state = n.q0
                if t.new_state in n.final_states:
                    t.new_state = n.q0
            
            for f in n.final_states:
                if f != n.q0: n.q.remove(f)
            n.final_states = list()
            n.final_states.append(n.q0)
                    
            return n
        
        elif isinstance(regex, Empty):
            n = NFA()
            n.q0 = 0
            n.q.append(n.q0)
            n.final_states.append(n.q0)
            return n
                        
        else:
            raise Exception("Don't know the expression %s" % 
                            str(regex.__class__))
                
    
    def prune_unreachable_states(self):
        """Removes unreachable states from this NFA"""
        to_remove = list()
        for s in self.q:
            if not self._reachable_from(self.q0, s, list()):
                to_remove.append(s)
        
        for r in to_remove:
            self.q.remove(r)
            if r in self.final_states: self.final_states.remove(r)
            t_to_remove = list()
            for t in self.transitions:
                if t.state == r or t.new_state == r: t_to_remove.append(t)
            for t in t_to_remove: self.transitions.remove(t)

            
    def _reachable_from(self, curr_state, target_state, visited):
        """Returns true iff target_state is reachable from curr_state"""
        if curr_state == target_state: return True #q0 and loops
        
        if curr_state in visited: return False #prevent infinite recursion on loops
        visited.append(curr_state)
        
        for t in self.transitions:
            if t.state == curr_state and t.new_state == target_state:
                return True
            if t.state == curr_state:
                if self._reachable_from(t.new_state, target_state, visited):
                    return True

    def get_dfa(self):
        """NFA -> DFA.""" 
        dfa = DFA()
        state_counter = 0
        
        #symbols
        sigma = list()
        for t in self.transitions:
            if not t.input in sigma: sigma.append(t.input)
        
        nfa2dfa = dict() #{set of states in self} -> DFA state
        nfa2dfa[frozenset([self.q0])] = state_counter
        dfa.q0 = state_counter
        dfa.q.append(state_counter)
        if self.q0 in self.final_states:
            dfa.final_states.append(state_counter)
        state_counter += 1
        
        work_stack = list([frozenset([self.q0])])
        
        while len(work_stack) > 0:
            curr_state = work_stack.pop()
            
            #find the next state for each input symbol.
            for input in sigma:
                next_state = list()
                for t in self.transitions:
                    #If the input matches, the state is valid and we haven't 
                    #already appended this state, then append.
                    if t.input == input and \
                    t.state in curr_state and \
                    not t.new_state in next_state:
                        next_state.append(t.new_state)
                
                if len(next_state) == 0: continue
                
                if frozenset(next_state) not in nfa2dfa.keys():
                    nfa2dfa[frozenset(next_state)] = state_counter
                    dfa.q.append(state_counter)
                    for s in next_state:
                        if s in self.final_states:
                            dfa.final_states.append(state_counter)
                            break        
                    state_counter += 1
                    work_stack.append(frozenset(next_state))
                
                
                dfa.add_transition(nfa2dfa[curr_state], 
                                   input, 
                                   nfa2dfa[frozenset(next_state)])

        return dfa
    
    def alphabet(self):
        """A list of all non-wildcard input symbols for this FA"""
        sigma = list()
        for t in self.transitions:
            if t.input == None: continue
            if not t.input in sigma: sigma.append(t.input)
        return sigma
    
    def bind_wildcards(self, sigma):
        transitions_to_add = list()
        transitions_to_remove = list()
        for t in self.transitions:
            if t.input == None:
                transitions_to_remove.append(t)
                for s in sigma:
                    if s == None: continue
                    transitions_to_add.append(TransitionFunction(t.state,
                                                                 s,
                                                                 t.new_state))
        for t in transitions_to_remove: self.transitions.remove(t)
        for t in transitions_to_add:
            self.add_transition(t.state, t.input, t.new_state)
    
    def included_in(self, right):
        return not self.has_unshared_final_state(right, False)

    def included_in_print(self, right):
        return not self.has_unshared_final_state(right, True)
    
    def has_unshared_final_state(self, right, print_graphs=False):
        """Returns ture iff self contains a final state that is not in right.
        
        print_graphs is a debugging flag. Setting to True will print out Dot 
        source code for GraphViz graphs, which can be very useful when debugging
        """
        
        #make the alphabet
        sigma = self.alphabet()
        for s in right.alphabet():
            if not s in sigma and s != None: 
                sigma.append(s)
        
        #If wild cards are the only characters involved, then bind them.
        if len(sigma) == 0:
            sigma.append(".")
        #Add an special character to differentiate wildcards from regular 
        #sequences now that wildcards are bound.
        sigma.append("SP")
        
        #bind the NFAs    
        bound_self = self.copy()
        bound_self.bind_wildcards(sigma)
        
        bound_right = right.copy()
        bound_right.bind_wildcards(sigma)
        
        #convert NFAs to DFAs
        self_dfa = bound_self.get_dfa()
        right_dfa = bound_right.get_dfa()
        
        if print_graphs:
            self_dfa.gv_code()
            right_dfa.gv_code()
        
        return self_dfa._has_unshared_final_state(right_dfa, 
                                                  self_dfa.q0, 
                                                  right_dfa.q0, 
                                                  None, 
                                                  None, 
                                                  list(), 
                                                  True)
    
    def _has_unshared_final_state(self, right, self_state, right_state, 
                                  self_input, right_input, checked, lock_step):
        """The recursion for has_unshared_final_state.
        
        Searches all paths through self for a path that does not locakstep
        with right and results in a final state.
        """
        
        #if we found a final state on the left but not a final state in lock step on the right, 
        #then the left has an unshared state.
        if self_state in self.final_states \
        and ((not right_state in right.final_states) or not lock_step):
            return True
     
        if frozenset([self_state, 
                      right_state, 
                      self_input, 
                      right_input, 
                      lock_step]) in checked:
            return False
        #prevent recursive loops
        checked.append(frozenset([self_state, 
                                  right_state, 
                                  self_input, 
                                  right_input, 
                                  lock_step])) 

        for self_t in self.transitions:
            if self_t.state != self_state: continue
            found_lockstep = False
            
            for right_t in right.transitions:
                if right_t.state != right_state: continue
                if right_t.input == self_t.input:
                    found_lockstep = True
                    r_val = self._has_unshared_final_state(right, 
                                                           self_t.new_state, 
                                                           right_t.new_state, 
                                                           self_t.input, 
                                                           right_t.input, 
                                                           checked, 
                                                           lock_step)
                    if r_val:
                        return True    
                     
            if not found_lockstep:
                r_val = self._has_unshared_final_state(right, 
                                                       self_t.new_state, 
                                                       right_state, 
                                                       self_t.input, 
                                                       None, 
                                                       checked, 
                                                       False)
                if r_val:
                    return True 
        return False

    def get_complement(self):
        """Returns the complement of self."""
        ret_val = DFA()
        ret_val.q = self.q
        ret_val.q0 = self.q0
        ret_val.transitions = self.transitions
        for s in self.q: 
            if not s in self.final_states: ret_val.final_states.append(s)
        return ret_val
    
    def get_intersect(self, other_nfa):
        """Returns an NFA representing the intersection of self and other_nfa.
        
        Creates every pair of states; transitions are defined piecewise 
        """
        intersect = NFA()
        curr_state = 0 #current state

        # for debugging.
        large = self if len(self.q) > len(other_nfa.q) else other_nfa 
        small = self if len(self.q) <= len(other_nfa.q) else other_nfa
        
        cross = dict() # self X other_nfa -> intersect state
        cross_offset = large.largest_state() * 100 #for readability
        
        for large_s in large.q:
            for small_s in small.q:
                intersect.q.append(curr_state)
                cross[frozenset({large_s, small_s + cross_offset})] = curr_state
                
                if large_s == large.q0 and small_s == small.q0:
                    intersect.q0 = curr_state
                    
                if large_s in large.final_states and small_s in small.final_states:
                    intersect.final_states.append(curr_state)
                
                curr_state += 1
                
        #normal intersection
        for st in large.transitions:
            for ot in small.transitions:
                #wildcards
                if st.input == ot.input or st.input == None or ot.input == None: 
                    state = cross[frozenset({st.state,ot.state + cross_offset})]
                    new_state = cross[frozenset(
                                    {st.new_state,ot.new_state + cross_offset})]
                    intersect.add_transition(state, st.input, new_state)
        return intersect

class DFA(NFA):
    def add_transition(self, source, input, dest):
        for t in self.transitions:
            if t.state == source and t.input == input:
                raise Exception("DFAs have to be deterministic.")
        self.transitions.append(TransitionFunction(source,input,dest))
    
