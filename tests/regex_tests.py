import clq.extensions.regex as r

################################################################################
#                            Pattern Matching                                  #
################################################################################
#Kleene
a = r.Pattern("a*")
assert a.match("aa")
assert not a.match("b")
assert not a.match("bab")
assert not a.match("aba")

#At most 1
a = r.Pattern("a?")
assert a.match("a")
assert not a.match("ab")
assert not a.match("aa")
assert a.match("")

#At least 1
a = r.Pattern("a+")
assert a.match("a")
assert not a.match("ab")
assert a.match("aa")
assert a.match("aaaa")
assert not a.match("")

#or
a = r.Pattern("a|b")
assert a.match("a")
assert a.match("b")
assert not a.match("")
assert not a.match("ab")

#Parens
a = r.Pattern("(a|b)")
assert a.match("a")
assert a.match("b")
assert not a.match("ab")
assert not a.match("bab")
assert not a.match("aba")

#Double parens
a = r.Pattern("(a)(b)")
assert a.match("ab")
assert not a.match("b")
assert not a.match("bab")
assert not a.match("aba")


#Nested parens
a = r.Pattern("((a)b)")
assert a.match("ab")
assert not a.match("b")
assert not a.match("bab")
assert not a.match("aba")

#escapes.
a = r.Pattern("(a|b)c")
assert a.match("ac")
assert a.match("bc")
assert not a.match("ad")
assert not a.match("cc")
assert not a.match("c")
assert not a.match("abc")

a = r.Pattern("(nfutlon|cryus)@cmu\.edu")
assert a.match("nfutlon@cmu.edu")
assert a.match("cryus@cmu.edu")
assert not a.match("nfutlon@andrew.cmu.edu")
assert not a.match("jonhathan.adlirch@cmu.edu")
assert not a.match("ncryus@cmu.edu")


a = r.Pattern("(nfutlon|cryus)@(andrew\.)?cmu\.edu")
assert not a.match("nfutlon@cmuxedu")
assert a.match("nfutlon@cmu.edu")
assert a.match("cryus@cmu.edu")
assert a.match("nfutlon@andrew.cmu.edu")
assert a.match("cryus@andrew.cmu.edu")
assert not a.match("jonhathan.adlirch@cmu.edu")
assert not a.match("ncryus@cmu.edu")



#wild cards
a = r.Pattern(".")
assert a.match("a")
assert not a.match("ab")

a = r.Pattern(".a")
assert a.match("ba")
assert not a.match("ab")

a = r.Pattern("a.")
assert a.match("aa")
assert a.match("ab")
assert not a.match("aba")

a = r.Pattern("a.a")
assert a.match("aaa")
assert a.match("aba")
assert not a.match("abba")
assert not a.match("baa")
assert not a.match("aab")

#at most and at least
a = r.Pattern("(1|2)+")
assert a.match("1212121222111")
assert not a.match("123")
assert not a.match("")

a = r.Pattern("(1|2)+(3|4)+")
assert a.match("12121212221113434343434")
assert not a.match("12345")
assert not a.match("12")
assert not a.match("34")

a = r.Pattern("(1|2|3|4|5|6|7|8|9|0)+\.(0|1|2|3|4|5|6|7|8|9|A|B|C|D|E|F)?")
assert a.match("1.A")
assert a.match("101.A")
assert not a.match("A.1")
assert a.match("1.")

#Order of operations
a = r.Pattern("a*b")
assert a.match("ab")

a = r.Pattern("ab*")
assert a.match("a")
assert a.match("ab")
assert a.match("abbbbbbbb")
assert not a.match("bbbb")

a = r.Pattern("a*a|b")
assert not a.match("ab")
assert a.match("b")
assert a.match("a")
assert a.match("aaa")
assert not a.match("")

a = r.Pattern("(ab)*")
assert a.match("ab")
assert a.match("abab")
assert not a.match("aba")
assert a.match("")

a = r.Pattern("a*(a|b)?")
assert a.match("ab")
assert a.match("b")
assert a.match("a")
assert a.match("aaa")
assert a.match("")

a = r.Pattern("a*a|b?")
assert not a.match("ab")
assert a.match("b")
assert a.match("a")
assert a.match("aaa")
assert a.match("")

a = r.Pattern("a+b*")
assert a.match("a")
assert a.match("abbb")
assert a.match("aabbb")
assert not a.match("b")
assert not a.match("")


a = r.Pattern("b.*")
assert a.match("babcdefghijklmnosqrstuvwxyz")
assert a.match("b")


a = r.Pattern("(a*|b*)c")
assert a.match("c")
assert a.match("aaac")
assert a.match("bbbc")

a = r.Pattern("..+")
assert not a.match("a")
assert a.match("ab")
assert a.match("abc")

a = r.Pattern("(a+|b+)c")
assert a.match("aaaaac")
assert a.match("bbbbbc")
assert not a.match("c")

a = r.Pattern("(n+|c+|d?)s")
assert a.match("ns")
assert a.match("nnns")
assert a.match("cs")
assert a.match("cccs")
assert a.match("ds")
assert not a.match("ddds")
assert a.match("s")


a = r.Pattern("ba*")
assert a.match("baaa")
assert not a.match("aaab")

a = r.Pattern("a+|b+")
assert a.match("aaaa")
assert a.match("bbbb")
assert not a.match("aba")
assert not a.match("abaa")

a = r.Pattern("(a?)|b")
assert a.match("")
assert a.match("a")
assert a.match("b")
assert not a.match("ab")

a = r.Pattern("a?|b")
assert a.match("")
assert a.match("a")
assert a.match("b")
assert not a.match("ab")


###############################################
#            Regex->NFAs,Inclusion            #
###############################################

def print_nfa(pattern):
    n = get_nfa(pattern)
    n.gv_code()
def get_nfa(pattern):
    return r.NFA.parse(r.Pattern(pattern).get_regex())

n1 = get_nfa("a+")
assert n1.included_in(n1)


n1 = get_nfa("a+")
n2 = get_nfa("a|b")
assert not n1.included_in(n2)
assert not n2.included_in(n1)


n1 = get_nfa("(a?)+")
n2 = get_nfa("a*")
assert n1.included_in(n2)
assert n2.included_in(n1)
assert not n1.included_in(get_nfa("a+"))

n1 = get_nfa(".+")
assert n1.included_in(n1)

n1 = get_nfa("a.")
n2 = get_nfa("ab")
assert n2.included_in(n1)
assert not n1.included_in(n2)
n2 = get_nfa("a")
assert not n1.included_in(n2)


n1 = get_nfa(".?.*")
n2 = get_nfa(".*")
assert n1.included_in(n2)
assert n2.included_in(n1)

n1 = get_nfa("a?")
n2 = get_nfa("a")
assert n2.included_in(n1)
assert not n1.included_in(n2)

n1 = get_nfa("a+b")
n2 = get_nfa("a?")
assert not n2.included_in(n1)

n1 = get_nfa("za?b")
n2 = get_nfa("zab")
assert n2.included_in(n1)
assert not n1.included_in(n2)

n1 = get_nfa("a|b")
n2 = get_nfa("a")
assert n2.included_in(n1)
assert not n1.included_in(n2)

n1 = get_nfa(".")
n2 = get_nfa(".+")
assert n1.included_in(n2)

n1 = get_nfa("(.)(.+)")
n2 = get_nfa("..+")
assert n2.included_in(n1)
assert n1.included_in(n2)

n1 = get_nfa("a+b")
n2 = get_nfa("(a?)a+b")
assert n2.included_in(n1)
assert n1.included_in(n2)

n1 = get_nfa(".?")
n2 = get_nfa("a?")
assert not (n2.included_in(n1) and n1.included_in(n2))


n1 = get_nfa("aa?")
n2 = get_nfa("a*")
assert n1.included_in(n2)
assert not n2.included_in(n1)

n1 = get_nfa("(nf|cy)@cmu1")
n2 = get_nfa("(nf|cy)@(andrew)?cmu1")
assert n1.included_in(n2)
assert not n2.included_in(n1)

n1 = get_nfa("(nf|cy)@cmu\.edu")
n2 = get_nfa("(nf|cy)@(andrew\.)?cmu\.edu")
assert n1.included_in(n2)
assert not n2.included_in(n1)

#Non-mechanized tests
#these tests are useful for finding errors, but if the above inclusion tests work then translation
#probable works as well.
#print_nfa("a")
#print_nfa("a*")
#print_nfa("ab")
#print_nfa("a|b")
#print_nfa("a+")
#print_nfa("a?")
#print_nfa("aa?")
#print_nfa("ab(cd)?wx(yz)?")
#print_nfa("a+|b+")
#print_nfa("b+|d?")
#print_nfa("(a+|b+|d?|abd)s*")
#print_nfa("(nf|cy)@(andrew\.)?cmu\.edu")