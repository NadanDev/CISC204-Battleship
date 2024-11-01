from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

from nnf import config
config.sat_backend = "kissat"

from boards import boardSetup, LOCATIONS, LOCATIONS2D
from UI import showSolutions

E = Encoding()

STYPES = {'des': 3, 'sub': 2}



@proposition(E)
class Hit(object):
    def __init__(self, location) -> None:
        assert location in LOCATIONS
        self.location = location

    def _prop_name(self):
        return f"Hit @ ({self.location})"

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
        self.stype = stype

    def _prop_name(self):
        return f"Ship @ ({self.location}={self.stype})"

@proposition(E)
class PossibleSegment(object):
    def __init__(self, location) -> None:
        assert location in LOCATIONS
        self.location = location

    def _prop_name(self):
        return f"Possible segment @ ({self.location})"
        

def example_theory():

    # ************HITS************
    possibleShip=[]
    for i in range(len(boardSetup)): # Find hit locations and possible hit locations
        for j in range(len(boardSetup[i])):
            if (boardSetup[i][j] == 2):
                E.add_constraint(Hit(LOCATIONS2D[i+1][j+1]))
                E.add_constraint(~PossibleSegment(LOCATIONS2D[i+1][j+1]))
                possibleShip = possibleShip + [PossibleSegment(LOCATIONS2D[i+2][j+1]), PossibleSegment(LOCATIONS2D[i+1][j+2]), PossibleSegment(LOCATIONS2D[i][j+1]), PossibleSegment(LOCATIONS2D[i+1][j])]
    constraint.add_at_least_one(E, possibleShip)

    for i in range(len(boardSetup)): # No hit and miss in same spot
        for j in range(len(boardSetup[i])):
            if (boardSetup[i][j] == 1):
                E.add_constraint(~PossibleSegment(LOCATIONS2D[i+1][j+1]))
                E.add_constraint(~Hit(LOCATIONS2D[i+1][j+1]))
                


    # ************BOUNDARY************
    for i in range(len(LOCATIONS2D)):
        for j in range(len(LOCATIONS2D[i])):
            if (LOCATIONS2D[i][j][0] == 'B'):
                E.add_constraint(Boundary(LOCATIONS2D[i][j]))
                E.add_constraint(~(Boundary(LOCATIONS2D[i][j]) & PossibleSegment(LOCATIONS2D[i][j])))


    
    # Will only print the ship if it's shown in boardSetup with a row of 2's
    findShipType()

    return E


def findShipType():
    checked=[]
    for i in range(1, len(LOCATIONS2D) - 1):
        for j in range(1, len(LOCATIONS2D[i]) - 1):
            location = LOCATIONS2D[i][j]
            
            if (boardSetup[i - 1][j - 1] == 2 and location not in checked):
                horizontalHits = [location]
                verticalHits = [location]

                cont = True
                incr=1

                # Horizontal
                while cont:
                    cont = False
                    if (j + 1 < len(LOCATIONS2D[i]) - 1 and boardSetup[i - 1][j - 1 + incr] == 2):
                        horizontalHits.append(LOCATIONS2D[i][j + incr])
                        cont = True
                        if (incr + 1 < 3):
                            incr += 1
                        else:
                            break
                cont = True
                incr=1
                while cont:
                    cont = False
                    if (j - 1 > 0 and boardSetup[i - 1][j - 1 - incr] == 2):
                        horizontalHits.append(LOCATIONS2D[i][j - incr])
                        cont = True
                        if (incr + 1 < 3):
                            incr += 1
                        else:
                            break
                
                # Vertical
                cont = True
                incr=1
                while cont:
                    print("Hey")
                    cont = False
                    if (i + 1 < len(LOCATIONS2D) - 1 and boardSetup[i - 1 + incr][j - 1] == 2):
                        verticalHits.append(LOCATIONS2D[i + incr][j])
                        cont = True
                        if (incr + 1 < 3):
                            incr += 1
                        else:
                            break
                cont = True
                incr=1
                while cont:
                    cont = False
                    if (i - 1 > 0 and boardSetup[i - 1 - incr][j - 1] == 2):
                        verticalHits.append(LOCATIONS2D[i - incr][j])
                        cont = True
                        if (incr + 1 < 3):
                            incr += 1
                        else:
                            break
                
                # Assign ship name depending on hits in a row
                if (len(horizontalHits) == STYPES['des']):
                    for loc in horizontalHits:
                        E.add_constraint(Ship(loc, 'des'))
                elif (len(verticalHits) == STYPES['des']):
                    for loc in verticalHits:
                        E.add_constraint(Ship(loc, 'des'))
                elif (len(horizontalHits) == STYPES['sub']):
                    for loc in horizontalHits:
                        E.add_constraint(Ship(loc, 'sub'))
                elif (len(verticalHits) == STYPES['sub']):
                    for loc in verticalHits:
                        E.add_constraint(Ship(loc, 'sub'))

                checked += horizontalHits + verticalHits




if __name__ == "__main__":

    T = example_theory()
    T = T.compile()

    #print("\nSatisfiable: %s" % T.satisfiable())

    solutions = T.solve()
    numSolutions = count_solutions(T)
    showSolutions(solutions, numSolutions)

