
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

from nnf import config
config.sat_backend = "kissat"

from setup import boardSetup

E = Encoding()


STATUS = [0, 1, 2]
LOCATIONS = [
    '11', '12', '13',
    '21', '22', '23',
    '31', '32', '33'
]
LOCATIONS2D = [
    ['11', '12', '13'],
    ['21', '22', '23'],
    ['31', '32', '33']
]

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class Hit(object):
    def __init__(self, status, location) -> None:
        assert status in STATUS
        assert location in LOCATIONS
        self.status = status
        self.location = location

    def _prop_name(self):
        return f"A.{self.data}"


# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
@constraint.at_least_one(E)
@proposition(E)
class FancyPropositions:

    def __init__(self, data):
        self.data = data

    def _prop_name(self):
        return f"A.{self.data}"

# Call your variables whatever you want
a = BasicPropositions("a")
b = BasicPropositions("b")   
c = BasicPropositions("c")
d = BasicPropositions("d")
e = BasicPropositions("e")
# At least one of these will be true
x = FancyPropositions("x")
y = FancyPropositions("y")
z = FancyPropositions("z")


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():

    for i in range(len(boardSetup)):
        for j in range(len(boardSetup[i])):
            if (boardSetup[i][j] == 2):
                possible=[]
                if (boardSetup[i+1][j] == 0):
                    possible.append(Hit(0, LOCATIONS2D[i+1][j]))
                if (boardSetup[i][j+1] == 0):
                    possible.append(Hit(0, LOCATIONS2D[i][j+1]))
                if (boardSetup[i-1][j] == 0):
                    possible.append(Hit(0, LOCATIONS2D[i-1][j]))
                if (boardSetup[i][j-1] == 0):
                    possible.append(Hit(0, LOCATIONS2D[i][j-1]))

                constraint.add_exactly_one(E, possible)
    return E


if __name__ == "__main__":

    T = example_theory()
    T = T.compile()

    #print("\nSatisfiable: %s" % T.satisfiable())
    #print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())
