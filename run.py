from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

from nnf import config
config.sat_backend = "kissat"

E = Encoding()

STYPES = ['des', 'sub']

# 0 - Not Checked
# 1 - Miss
# 2 - Hit
# Does not include boundaries
boardSetup = [
    [1, 0, 0],
    [2, 0, 0],
    [1, 0, 0]
]

LOCATIONS = [ # B spaces are boundaries, L spaces are playable
    'B00', 'B10', 'B20', 'B30', 'B40',
    'B01', 'L11', 'L12', 'L13', 'B01',
    'B02', 'L21', 'L22', 'L23', 'B02',
    'B03', 'L31', 'L32', 'L33', 'B03',
    'B04', 'B14', 'B24', 'B34', 'B44'
]

LOCATIONS2D = [
    ['B00', 'B10', 'B20', 'B30', 'B40'],
    ['B01', 'L11', 'L12', 'L13', 'B01'],
    ['B02', 'L21', 'L22', 'L23', 'B02'],
    ['B03', 'L31', 'L32', 'L33', 'B03'],
    ['B04', 'B14', 'B24', 'B34', 'B44']
]



@proposition(E)
class Hit(object):
    def __init__(self, location) -> None:
        assert location in LOCATIONS
        self.location = location

    def _prop_name(self):
        return f"Hit({self.location})"

@proposition(E)
class Boundary(object):
    def __init__(self, location) -> None:
        assert location in LOCATIONS
        self.location = location

    def _prop_name(self):
        return f"Boundary({self.location})"

@proposition(E)
class Ship(object):
    def __init__(self, location, stype) -> None:
        assert location in LOCATIONS
        assert stype in STYPES
        self.location = location
        self.stype = stype;

    def _prop_name(self):
        return f"Ship({self.location}={self.stype})"
        

def theory():

    # ************HITS************
    for i in range(len(boardSetup)):
        for j in range(len(boardSetup[i])):
            if (boardSetup[i][j] == 2):
                possibleShip=[Hit(LOCATIONS2D[i+2][j+1]), Hit(LOCATIONS2D[i+1][j+2]), Hit(LOCATIONS2D[i][j+1]), Hit(LOCATIONS2D[i+1][j])]
                constraint.add_exactly_one(E, possibleShip)

    for i in range(len(boardSetup)): # No hit and miss in same spot
        for j in range(len(boardSetup[i])):
            if (boardSetup[i][j] == 1):
                E.add_constraint(~Hit(LOCATIONS2D[i+1][j+1]))
                


    # ************BOUNDARY************
    for i in range(len(LOCATIONS2D)):
        for j in range(len(LOCATIONS2D[i])):
            if (LOCATIONS2D[i][j][0] == 'B'):
                E.add_constraint(Boundary(LOCATIONS2D[i][j]))
                E.add_constraint(~(Boundary(LOCATIONS2D[i][j]) & Hit(LOCATIONS2D[i][j])))



    # ************SHIPS************ (WIP)
    # for i in range(len(LOCATIONS2D)):
    #     for j in range(len(LOCATIONS2D[i])):
    #         E.add_constraint(~(Boundary(LOCATIONS2D[i][j]) & Ship(LOCATIONS2D[i][j], 'des')))
    #         E.add_constraint(Hit(LOCATIONS2D[i][j]) >> Ship(LOCATIONS2D[i][j], 'des'))

    return E


if __name__ == "__main__":

    T = theory()
    T = T.compile()

    #print("\nSatisfiable: %s" % T.satisfiable())

    showOnlyHits = True

    solutions = T.solve()
    if (solutions):
        print("\n# Solutions: %d" % count_solutions(T))
        print("\n")
        for k in solutions:
            if solutions[k]:
                if (showOnlyHits and str(k)[0] == "B"):
                    continue
                print(k, "\n")
    else:
        print("No solutions")
