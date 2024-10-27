
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

@proposition(E)
class Hit(object):
    def __init__(self, status, location) -> None:
        assert status in STATUS
        assert location in LOCATIONS
        self.status = status
        self.location = location

    def _prop_name(self):
        return f"Hit({self.status}={self.location})"

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
