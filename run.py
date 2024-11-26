from bauhaus import Encoding, proposition, constraint, And, Or
from bauhaus.utils import count_solutions, likelihood

from nnf import config
config.sat_backend = "kissat"

from boards import boardSetup, LOCATIONS, LOCATIONS2D
from UI import showSolutions

E = Encoding()


STYPES = {'des': 3, 'sub': 2}
STATUSCHECKED = ['Hit', 'Miss', 'Complete', 'Sunk']
STATUSUNCHECKED = ["Unchecked", "Possible Segment", "Highly Possible Segment"]


@proposition(E)
class Unchecked(object):
    def __init__(self, location, status) -> None:
        assert location in LOCATIONS
        self.location = location
        assert status in STATUSUNCHECKED
        self.status = status

    def _prop_name(self):
        return f"{self.status} @ ({self.location})"
    
@proposition(E)
class Checked(object):
    def __init__(self, location, status) -> None:
        assert location in LOCATIONS
        self.location = location
        assert status in STATUSCHECKED
        self.status = status

    def _prop_name(self):
        return f"{self.status} @ ({self.location})"

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
    

def example_theory():

    # ************BEGGINING BOARD************

    # Hits
    for i in range(len(boardSetup)):
        for j in range(len(boardSetup[i])):
            location = LOCATIONS2D[i+1][j+1]

            if (boardSetup[i][j] == 1):
                E.add_constraint(Checked(location, 'Miss'))
            elif (boardSetup[i][j] == 2):
                E.add_constraint(Checked(location, 'Hit'))
            else:
                E.add_constraint(Unchecked(location, 'Unchecked'))

    # Boundary
    for i in range(len(LOCATIONS2D)):
        for j in range(len(LOCATIONS2D[i])):
            if (LOCATIONS2D[i][j][0] == 'B'):
                E.add_constraint(Boundary(LOCATIONS2D[i][j]))

    

    # ************CONSTRAINTS************

    # Basic constraints to to avoid having two different statuses at the same location
    for i in range(len(LOCATIONS2D)):
        for j in range(len(LOCATIONS2D[i])):
            location = LOCATIONS2D[i][j]

            E.add_constraint(Checked(location, 'Hit') >> ~Checked(location, 'Miss'))
            E.add_constraint(Checked(location, 'Hit') >> ~Unchecked(location, 'Possible Segment'))
            E.add_constraint(Checked(location, 'Hit') >> ~Unchecked(location, 'Highly Possible Segment'))
            E.add_constraint(Checked(location, 'Miss') >> ~Unchecked(location, 'Possible Segment'))
            E.add_constraint(Checked(location, 'Miss') >> ~Unchecked(location, 'Highly Possible Segment'))

            for status in STATUSCHECKED:
                E.add_constraint(Boundary(location) >> ~Checked(location, status))
                E.add_constraint(Unchecked(location, 'Unchecked') >> ~Checked(location, status))
            for status in STATUSUNCHECKED:
                E.add_constraint(Boundary(location) >> ~Unchecked(location, status))

    # Checking for possible segments and highly possible segments
    for i in range(1, len(LOCATIONS2D) - 1):
        for j in range(1, len(LOCATIONS2D[i]) - 1):
            location = LOCATIONS2D[i][j]
            right = LOCATIONS2D[i][j + 1]
            left = LOCATIONS2D[i][j - 1]
            up = LOCATIONS2D[i - 1][j]
            down = LOCATIONS2D[i + 1][j]

            # Possible Segment
            E.add_constraint(Unchecked(location, 'Possible Segment') >> (Checked(right, 'Hit') | Checked(left, 'Hit') | Checked(up, 'Hit') | Checked(down, 'Hit')))

            # Highly Possible Segment
            if (i == len(LOCATIONS2D) - 2): # If's used to avoid out of bounds
                up2 = LOCATIONS2D[i - 2][j]
                if (j == 1):
                    right2 = LOCATIONS2D[i][j + 2]
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(up, 'Hit') & Checked(up2, 'Hit')) | (Checked(right, 'Hit') & Checked(right2, 'Hit'))))
                elif (j == len(LOCATIONS2D[i]) - 2):
                    left2 = LOCATIONS2D[i][j - 2]
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(up, 'Hit') & Checked(up2, 'Hit')) | (Checked(left, 'Hit') & Checked(left2, 'Hit'))))
                else:
                    right2 = LOCATIONS2D[i][j + 2]
                    left2 = LOCATIONS2D[i][j - 2]
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(up, 'Hit') & Checked(up2, 'Hit')) | (Checked(right, 'Hit') & Checked(right2, 'Hit')) | (Checked(left, 'Hit') & Checked(left2, 'Hit'))))
            elif (i == 1):
                down2 = LOCATIONS2D[i + 2][j]
                if (j == 1):
                    right2 = LOCATIONS2D[i][j + 2]
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(down, 'Hit') & Checked(down2, 'Hit')) | (Checked(right, 'Hit') & Checked(right2, 'Hit'))))
                elif (j == len(LOCATIONS2D[i]) - 2):
                    left2 = LOCATIONS2D[i][j - 2]
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(down, 'Hit') & Checked(down2, 'Hit')) | (Checked(left, 'Hit') & Checked(left2, 'Hit'))))
                else:
                    right2 = LOCATIONS2D[i][j + 2]
                    left2 = LOCATIONS2D[i][j - 2]
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(down, 'Hit') & Checked(down2, 'Hit')) | (Checked(right, 'Hit') & Checked(right2, 'Hit')) | (Checked(left, 'Hit') & Checked(left2, 'Hit'))))
            if (j == len(LOCATIONS2D[i]) - 2):
                if (i != 1 and i != len(LOCATIONS2D) - 2):
                    left2 = LOCATIONS2D[i][j - 2]
                    up2 = LOCATIONS2D[i - 2][j]
                    down2 = LOCATIONS2D[i + 2][j]
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(up, 'Hit') & Checked(up2, 'Hit')) | (Checked(right, 'Hit') & Checked(right2, 'Hit')) | (Checked(left, 'Hit') & Checked(left2, 'Hit'))))
            elif (j == 1):
                if (i != 1 and i != len(LOCATIONS2D) - 2):
                    right2 = LOCATIONS2D[i][j + 2]
                    left2 = LOCATIONS2D[i][j - 2]
                    down2 = LOCATIONS2D[i + 2][j]
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(down, 'Hit') & Checked(down2, 'Hit')) | (Checked(right, 'Hit') & Checked(right2, 'Hit')) | (Checked(left, 'Hit') & Checked(left2, 'Hit'))))
            if (i != 1 and i != len(LOCATIONS2D) - 2 and j != 1 and j != len(LOCATIONS2D[i]) - 2):
                right2 = LOCATIONS2D[i][j + 2]
                left2 = LOCATIONS2D[i][j - 2]
                up2 = LOCATIONS2D[i - 2][j]
                down2 = LOCATIONS2D[i + 2][j]
                E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(up, 'Hit') & Checked(up2, 'Hit')) | (Checked(down, 'Hit') & Checked(down2, 'Hit')) | (Checked(right, 'Hit') & Checked(right2, 'Hit')) | (Checked(left, 'Hit') & Checked(left2, 'Hit'))))


    # Find if a ship is sunk (surronded by misses/boundaries/hits)
    for i in range(1, len(LOCATIONS2D) - 1):
        for j in range(1, len(LOCATIONS2D[i]) - 1):
            location = LOCATIONS2D[i][j]
            right = LOCATIONS2D[i][j + 1]
            left = LOCATIONS2D[i][j - 1]
            up = LOCATIONS2D[i - 1][j]
            down = LOCATIONS2D[i + 1][j]

            # Readability
            rightSpot = [Checked(right, 'Miss') | Checked(right, 'Hit') | Boundary(right)]
            leftSpot = [Checked(left, 'Miss') | Checked(left, 'Hit') | Boundary(left)]
            upSpot = [Checked(up, 'Miss') | Checked(up, 'Hit') | Boundary(up)]
            downSpot = [Checked(down, 'Miss') | Checked(down, 'Hit') | Boundary(down)]

            E.add_constraint(Checked(location, 'Complete') >> ((Or(rightSpot)) & (Or(leftSpot)) & (Or(downSpot)) & (Or(upSpot)) & Checked(location, 'Hit'))) # Complete meaning not sunk but surrounded by checked spots


            if (i == len(LOCATIONS2D) - 2 and j == len(LOCATIONS2D[i]) - 2):
                E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (Checked(left, 'Sunk') | Checked(up, 'Sunk'))))
            elif (i == len(LOCATIONS2D) - 2):
                right2 = LOCATIONS2D[i][j + 2]
                E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(right, 'Complete')    & (Checked(right2, 'Miss') | Checked(right2, "Complete") | Boundary(right2))) | 
                                                               Checked(left, 'Sunk') | Checked(up, 'Sunk'))))
            elif (j == len(LOCATIONS2D[i]) - 2):
                down2 = LOCATIONS2D[i + 2][j]
                E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(down, 'Complete')    & (Checked(down2, 'Miss') | Checked(down2, "Complete") | Boundary(down2))) | 
                                                               Checked(left, 'Sunk') | Checked(up, 'Sunk'))))
            else:
                right2 = LOCATIONS2D[i][j + 2]
                down2 = LOCATIONS2D[i + 2][j]
                E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(right, 'Complete')    & (Checked(right2, 'Miss') | Checked(right2, "Complete") | Boundary(right2))) | 
                                                              (Checked(down, 'Complete')    & (Checked(down2, 'Miss') | Checked(down2, "Complete") | Boundary(down2))) | 
                                                               Checked(left, 'Sunk') | Checked(up, 'Sunk'))))

    # Will only print the ship if it's shown in boardSetup with a row of 2's
    findShipType()

    return E

# TODO: Change to logic instead of normal python
def findShipType():
    checked=[] # Locations that have been checked
    for i in range(1, len(LOCATIONS2D) - 1):
        for j in range(1, len(LOCATIONS2D[i]) - 1):
            location = LOCATIONS2D[i][j]
            
            if (boardSetup[i - 1][j - 1] == 2 and location not in checked):
                horizontalHits = [location] # Hits that are part of a horizontal ship
                verticalHits = [location] # Hits that are part of a vertical ship


                # Horizontal
                cont = True
                incr=1
                while cont:
                    cont = False
                    if (j + 1 < len(LOCATIONS2D[i]) - 1 and boardSetup[i - 1][j - 1 + incr] == 2): # Check if there is a hit to the right
                        horizontalHits.append(LOCATIONS2D[i][j + incr])
                        cont = True
                        if (j + incr < 3): # Check if we are at the end of the board
                            incr += 1
                        else:
                            break
                

                # Vertical
                cont = True
                incr=1
                while cont:
                    cont = False
                    if (i + 1 < len(LOCATIONS2D) - 1 and boardSetup[i - 1 + incr][j - 1] == 2): # Check if there is a hit below
                        verticalHits.append(LOCATIONS2D[i + incr][j])
                        cont = True
                        if (i + incr < 3): # Check if we are at the end of the board
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

    solutions = T.solve()
    numSolutions = count_solutions(T)
    showSolutions(solutions, numSolutions)

