import cl.oquence as clq

class TestType(clq.Type):
    def __init__(self):
        clq.Type.__init__(self, name="TestType")

test = TestType()

@clq.fn
def id(x):
    return x

id_tt = id.compile(test)

print id_tt.program_item.code
