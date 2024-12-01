# Run this file

from bauhaus import Encoding, proposition, And, Or
from bauhaus.utils import count_solutions

from nnf import config
config.sat_backend = "kissat"

from UI import showSolutions, getUserBoard, solveBoard

E = Encoding()

LOCATIONS = [] # List of possible location for assertions
LOCATIONS2D = [] # 2D list of possible locations which will be looped through
boardSetup = [] # The board that has the locations of ships

STYPES = {'des': 3, 'sub': 2} # This model only supports destroyers and submarines, but any sized board should work fine

STATUSCHECKED = ['Hit', 'Miss', 'Complete', 'Sunk', 'Cornered Hit'] # Statuses where the model is certain of something
STATUSUNCHECKED = ["Unchecked", "Unlikely Segment", "Possible Segment", "Highly Possible Segment", 'Possible Sunk'] # Statuses where the model is uncertain of something



@proposition(E) # Uncertain tile status
class Unchecked(object):
    def __init__(self, location, status) -> None:
        assert location in LOCATIONS
        self.location = location
        assert status in STATUSUNCHECKED
        self.status = status

    def _prop_name(self):
        return f"{self.status} @ ({self.location})"
    
@proposition(E) # Certain tile status
class Checked(object):
    def __init__(self, location, status) -> None:
        assert location in LOCATIONS
        self.location = location
        assert status in STATUSCHECKED
        self.status = status

    def _prop_name(self):
        return f"{self.status} @ ({self.location})"

@proposition(E) # Edge of the board
class Boundary(object):
    def __init__(self, location) -> None:
        assert location in LOCATIONS
        self.location = location

    def _prop_name(self):
        return f"Boundary({self.location})"

@proposition(E) # Used to identify a sunk ship to a certain type
class Ship(object):
    def __init__(self, location, stype, possible) -> None: # Possible means the ship most likely is sunk
        assert location in LOCATIONS
        assert stype in STYPES
        assert possible in [True, False]
        self.location = location
        self.stype = stype
        self.possible = possible

    def _prop_name(self):
        if (self.possible):
            return f"Ship {self.stype} @ ({self.location}) (Possible)"
        else:
            return f"Ship {self.stype} @ ({self.location})"
    
def theory():

    # Reset constraints for next round
    E._custom_constraints = set()
    E.clear_constraints()
    E.clear_debug_constraints()


    # ************BEGGINING BOARD************
    # Look at the given board and add constraints according to space status

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
    # Basic constraints to avoid having two unwanted statuses at the same location
    for i in range(len(LOCATIONS2D)):
        for j in range(len(LOCATIONS2D[i])):
            location = LOCATIONS2D[i][j]

            E.add_constraint(Checked(location, 'Hit') >> ~Checked(location, 'Miss'))
            E.add_constraint(Checked(location, 'Hit') >> ~Unchecked(location, 'Possible Segment'))
            E.add_constraint(Checked(location, 'Hit') >> ~Unchecked(location, 'Highly Possible Segment'))
            E.add_constraint(Checked(location, 'Hit') >> ~Unchecked(location, 'Unlikely Segment'))
            E.add_constraint(Checked(location, 'Miss') >> ~Unchecked(location, 'Possible Segment'))
            E.add_constraint(Checked(location, 'Miss') >> ~Unchecked(location, 'Highly Possible Segment'))
            E.add_constraint(Checked(location, 'Miss') >> ~Unchecked(location, 'Unlikely Segment'))

            # A boundary or unchecked spot can't have any checked status and a boundary can't have an unchecked status
            for status in STATUSCHECKED:
                E.add_constraint(Boundary(location) >> ~Checked(location, status))
                E.add_constraint(Unchecked(location, 'Unchecked') >> ~Checked(location, status))
            for status in STATUSUNCHECKED:
                E.add_constraint(Boundary(location) >> ~Unchecked(location, status))


    # Checking for possible segments and highly possible segments
    findPossibleSegments()

    # Find if a ship is sunk (surronded by misses/boundaries/hits)
    findSunkShips()

    # Sunk ships are identified by their type
    findShipType()

    return E




def findPossibleSegments():
    for i in range(1, len(LOCATIONS2D) - 1):
        for j in range(1, len(LOCATIONS2D[i]) - 1):

            # We need to check these locations
            location = LOCATIONS2D[i][j]
            right = LOCATIONS2D[i][j + 1]
            left = LOCATIONS2D[i][j - 1]
            up = LOCATIONS2D[i - 1][j]
            down = LOCATIONS2D[i + 1][j]
            # Right2, left2, up2, down2 are declared where they won't be out of bounds

            # Possible Segment (A a spot with a hit next to it)
            E.add_constraint(Unchecked(location, 'Possible Segment') >> ((Checked(right, 'Hit')) | (Checked(left, 'Hit')) | (Checked(up, 'Hit')) | (Checked(down, 'Hit'))))

            # ***This style of code will be used in all functions to avoid out of bounds errors***
            # Highly Possible Segment
            if (i == len(LOCATIONS2D) - 2): # If's used to avoid out of bounds, each section checks whether the spot is on a specific edge (ex. you cant use right2 if you are on the right edge).
                up2 = LOCATIONS2D[i - 2][j]
                if (j == 1): # j = 1 is a left edge, j = len(LOCATIONS2D[i]) - 2 is a right edge, i = 1 is a top edge, i = len(LOCATIONS2D) - 2 is a bottom edge
                    right2 = LOCATIONS2D[i][j + 2]
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(up, 'Hit') & Checked(up2, 'Hit')) | (Checked(right, 'Hit') & Checked(right2, 'Hit')))) # Two hits in a row signifies a highly possible segment next
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
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(up, 'Hit') & Checked(up2, 'Hit')) | (Checked(down, 'Hit') & Checked(down2, 'Hit')) | (Checked(left, 'Hit') & Checked(left2, 'Hit'))))
            elif (j == 1):
                if (i != 1 and i != len(LOCATIONS2D) - 2):
                    right2 = LOCATIONS2D[i][j + 2]
                    up2 = LOCATIONS2D[i - 2][j]
                    down2 = LOCATIONS2D[i + 2][j]
                    E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(down, 'Hit') & Checked(down2, 'Hit')) | (Checked(right, 'Hit') & Checked(right2, 'Hit')) | (Checked(up, 'Hit') & Checked(up2, 'Hit'))))
            if (i != 1 and i != len(LOCATIONS2D) - 2 and j != 1 and j != len(LOCATIONS2D[i]) - 2): # Not on an edge
                right2 = LOCATIONS2D[i][j + 2]
                left2 = LOCATIONS2D[i][j - 2]
                up2 = LOCATIONS2D[i - 2][j]
                down2 = LOCATIONS2D[i + 2][j]
                E.add_constraint(Unchecked(location, 'Highly Possible Segment') >> ((Checked(up, 'Hit') & Checked(up2, 'Hit')) | (Checked(down, 'Hit') & Checked(down2, 'Hit')) | (Checked(right, 'Hit') & Checked(right2, 'Hit')) | (Checked(left, 'Hit') & Checked(left2, 'Hit'))))




def findSunkShips():
    for i in range(1, len(LOCATIONS2D) - 1):
        for j in range(1, len(LOCATIONS2D[i]) - 1):

            location = LOCATIONS2D[i][j]
            right = LOCATIONS2D[i][j + 1]
            left = LOCATIONS2D[i][j - 1]
            up = LOCATIONS2D[i - 1][j]
            down = LOCATIONS2D[i + 1][j]

            # Readability (To reduce line length)
            rightSpot = [Checked(right, 'Miss'), Checked(right, 'Hit'), Boundary(right)]
            leftSpot = [Checked(left, 'Miss'),  Checked(left, 'Hit'),  Boundary(left)]
            upSpot = [Checked(up, 'Miss'),  Checked(up, 'Hit'),  Boundary(up)]
            downSpot = [Checked(down, 'Miss'),  Checked(down, 'Hit'),  Boundary(down)]

            E.add_constraint(Checked(location, 'Complete') >> ((Or(rightSpot)) & (Or(leftSpot)) & (Or(downSpot)) & (Or(upSpot)) & Checked(location, 'Hit'))) # Complete meaning not sunk but surrounded by checked spots

            # Find guaranteed sunk ships
            if (i == len(LOCATIONS2D) - 2):
                up2 = LOCATIONS2D[i - 2][j]
                if (j == 1):
                    right2 = LOCATIONS2D[i][j + 2]
                    # Sunk meaning a line of closed off hits (impossible for it to not be sunk)
                    E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(right, 'Complete')    & (Checked(right2, 'Miss') | Checked(right2, "Complete") | Boundary(right2))) | 
                                                              (Checked(up, 'Complete')       & (Checked(up2, 'Miss')    | Checked(up2, "Complete")    | Boundary(up2))))))
                elif (j == len(LOCATIONS2D[i]) - 2):
                    left2 = LOCATIONS2D[i][j - 2]
                    E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(left, 'Complete')     & (Checked(left2, 'Miss')  | Checked(left2, "Complete")  | Boundary(left2))) | 
                                                              (Checked(up, 'Complete')       & (Checked(up2, 'Miss')    | Checked(up2, "Complete")    | Boundary(up2))))))
                else:
                    right2 = LOCATIONS2D[i][j + 2]
                    left2 = LOCATIONS2D[i][j - 2]
                    E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(right, 'Complete')    & (Checked(right2, 'Miss') | Checked(right2, "Complete") | Boundary(right2))) | 
                                                              (Checked(left, 'Complete')     & (Checked(left2, 'Miss')  | Checked(left2, "Complete")  | Boundary(left2))) | 
                                                              (Checked(up, 'Complete')       & (Checked(up2, 'Miss')    | Checked(up2, "Complete")    | Boundary(up2))))))
            elif (i == 1):
                down2 = LOCATIONS2D[i + 2][j]
                if (j == 1):
                    right2 = LOCATIONS2D[i][j + 2]
                    E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(right, 'Complete')    & (Checked(right2, 'Miss') | Checked(right2, "Complete") | Boundary(right2))) | 
                                                              (Checked(down, 'Complete')     & (Checked(down2, 'Miss')  | Checked(down2, "Complete")  | Boundary(down2))))))
                elif (j == len(LOCATIONS2D[i]) - 2):
                    left2 = LOCATIONS2D[i][j - 2]
                    E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(left, 'Complete')     & (Checked(left2, 'Miss')  | Checked(left2, "Complete")  | Boundary(left2))) | 
                                                              (Checked(down, 'Complete')     & (Checked(down2, 'Miss')  | Checked(down2, "Complete")  | Boundary(down2))))))
                else:
                    right2 = LOCATIONS2D[i][j + 2]
                    left2 = LOCATIONS2D[i][j - 2]
                    E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(right, 'Complete')    & (Checked(right2, 'Miss') | Checked(right2, "Complete") | Boundary(right2))) | 
                                                              (Checked(left, 'Complete')     & (Checked(left2, 'Miss')  | Checked(left2, "Complete")  | Boundary(left2))) | 
                                                              (Checked(down, 'Complete')     & (Checked(down2, 'Miss')  | Checked(down2, "Complete")  | Boundary(down2))))))
            if (j == len(LOCATIONS2D[i]) - 2):
                if (i != 1 and i != len(LOCATIONS2D) - 2):
                    left2 = LOCATIONS2D[i][j - 2]
                    up2 = LOCATIONS2D[i - 2][j]
                    down2 = LOCATIONS2D[i + 2][j]
                    E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(left, 'Complete')     & (Checked(left2, 'Miss')  | Checked(left2, "Complete")  | Boundary(left2))) | 
                                                              (Checked(up, 'Complete')       & (Checked(up2, 'Miss')    | Checked(up2, "Complete")    | Boundary(up2))) | 
                                                              (Checked(down, 'Complete')     & (Checked(down2, 'Miss')  | Checked(down2, "Complete")  | Boundary(down2))))))
            elif (j == 1):
                if (i != 1 and i != len(LOCATIONS2D) - 2):
                    right2 = LOCATIONS2D[i][j + 2]
                    up2 = LOCATIONS2D[i - 2][j]
                    down2 = LOCATIONS2D[i + 2][j]
                    E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(right, 'Complete')    & (Checked(right2, 'Miss') | Checked(right2, "Complete") | Boundary(right2))) | 
                                                              (Checked(up, 'Complete')       & (Checked(up2, 'Miss')    | Checked(up2, "Complete")    | Boundary(up2))) | 
                                                              (Checked(down, 'Complete')     & (Checked(down2, 'Miss')  | Checked(down2, "Complete")  | Boundary(down2))))))
            if (i != 1 and i != len(LOCATIONS2D) - 2 and j != 1 and j != len(LOCATIONS2D[i]) - 2): # Not on an edge
                right2 = LOCATIONS2D[i][j + 2]
                left2 = LOCATIONS2D[i][j - 2]
                up2 = LOCATIONS2D[i - 2][j]
                down2 = LOCATIONS2D[i + 2][j]
                E.add_constraint(Checked(location, 'Sunk') >> (Checked(location, 'Complete') & (
                                                              (Checked(right, 'Complete')    & (Checked(right2, 'Miss') | Checked(right2, "Complete") | Boundary(right2))) | 
                                                              (Checked(left, 'Complete')     & (Checked(left2, 'Miss')  | Checked(left2, "Complete")  | Boundary(left2))) | 
                                                              (Checked(up, 'Complete')       & (Checked(up2, 'Miss')    | Checked(up2, "Complete")    | Boundary(up2))) | 
                                                              (Checked(down, 'Complete')     & (Checked(down2, 'Miss')  | Checked(down2, "Complete")  | Boundary(down2))))))


            

            # ***Special case to improve efficiency***
            
            # Similar to complete but it can't be next to a hit
            missOrBoundaryR = [Checked(right, 'Miss'), Boundary(right)]
            missOrBoundaryL = [Checked(left, 'Miss'), Boundary(left)]
            missOrBoundaryU = [Checked(up, 'Miss'), Boundary(up)]
            missOrBoundaryD = [Checked(down, 'Miss'), Boundary(down)]

            # To avoid the model from checking every location around a sunk ship before continuing, this constraint tells the model to move on if it's guaranteed that the ship is already sunk
            if (i == len(LOCATIONS2D) - 2):
                up2 = LOCATIONS2D[i - 2][j]
                missOrBoundaryU2 = [Checked(up2, 'Miss'), Boundary(up2)]
                if (j == 1):
                    right2 = LOCATIONS2D[i][j + 2]
                    missOrBoundaryR2 = [Checked(right2, 'Miss'), Boundary(right2)]
                    # Cornered Hit means a hit that is surrounded by misses/boundaries with only one hit next to it which means we know a ship is heading in that direction
                    E.add_constraint(Checked(location, 'Cornered Hit') >> (Checked(location, 'Hit') & (
                                                                             (Or(missOrBoundaryR) & Checked(up, 'Hit') & Or(missOrBoundaryU2)) | 
                                                                             (Or(missOrBoundaryU) & Checked(right, 'Hit') & Or(missOrBoundaryR2)))))
                elif (j == len(LOCATIONS2D[i]) - 2):
                    left2 = LOCATIONS2D[i][j - 2]
                    missOrBoundaryL2 = [Checked(left2, 'Miss'), Boundary(left2)]
                    E.add_constraint(Checked(location, 'Cornered Hit') >> (Checked(location, 'Hit') & (
                                                                             (Or(missOrBoundaryL) & Checked(up, 'Hit') & Or(missOrBoundaryU2)) | 
                                                                             (Or(missOrBoundaryU) & Checked(left, 'Hit') & Or(missOrBoundaryL2)))))
                else:
                    right2 = LOCATIONS2D[i][j + 2]
                    left2 = LOCATIONS2D[i][j - 2]
                    missOrBoundaryR2 = [Checked(right2, 'Miss'), Boundary(right2)]
                    missOrBoundaryL2 = [Checked(left2, 'Miss'), Boundary(left2)]
                    E.add_constraint(Checked(location, 'Cornered Hit') >> (Checked(location, 'Hit') & (
                                                                             (Or(missOrBoundaryR) & Or(missOrBoundaryL) & Checked(up, 'Hit') & Or(missOrBoundaryU2)) | 
                                                                             (Or(missOrBoundaryU) & Or(missOrBoundaryL) & Checked(right, 'Hit') & Or(missOrBoundaryR2)) | 
                                                                             (Or(missOrBoundaryU) & Or(missOrBoundaryR) & Checked(left, 'Hit') & Or(missOrBoundaryL2)))))
            elif (i == 1):
                down2 = LOCATIONS2D[i + 2][j]
                missOrBoundaryD2 = [Checked(down2, 'Miss'), Boundary(down2)]
                if (j == 1):
                    right2 = LOCATIONS2D[i][j + 2]
                    missOrBoundaryR2 = [Checked(right2, 'Miss'), Boundary(right2)]
                    E.add_constraint(Checked(location, 'Cornered Hit') >> (Checked(location, 'Hit') & (
                                                                             (Or(missOrBoundaryR) & Checked(down, 'Hit') & Or(missOrBoundaryD2)) | 
                                                                             (Or(missOrBoundaryD) & Checked(right, 'Hit') & Or(missOrBoundaryR2)))))
                elif (j == len(LOCATIONS2D[i]) - 2):
                    left2 = LOCATIONS2D[i][j - 2]
                    missOrBoundaryL2 = [Checked(left2, 'Miss'), Boundary(left2)]
                    E.add_constraint(Checked(location, 'Cornered Hit') >> (Checked(location, 'Hit') & (
                                                                             (Or(missOrBoundaryL) & Checked(down, 'Hit') & Or(missOrBoundaryD2)) | 
                                                                             (Or(missOrBoundaryD) & Checked(left, 'Hit') & Or(missOrBoundaryL2)))))
                else:
                    right2 = LOCATIONS2D[i][j + 2]
                    left2 = LOCATIONS2D[i][j - 2]
                    missOrBoundaryR2 = [Checked(right2, 'Miss'), Boundary(right2)]
                    missOrBoundaryL2 = [Checked(left2, 'Miss'), Boundary(left2)]
                    E.add_constraint(Checked(location, 'Cornered Hit') >> (Checked(location, 'Hit') & (
                                                                             (Or(missOrBoundaryR) & Or(missOrBoundaryL) & Checked(down, 'Hit') & Or(missOrBoundaryD2)) | 
                                                                             (Or(missOrBoundaryD) & Or(missOrBoundaryL) & Checked(right, 'Hit') & Or(missOrBoundaryR2)) | 
                                                                             (Or(missOrBoundaryD) & Or(missOrBoundaryR) & Checked(left, 'Hit') & Or(missOrBoundaryL2)))))
            if (j == len(LOCATIONS2D[i]) - 2):
                if (i != 1 and i != len(LOCATIONS2D) - 2):
                    left2 = LOCATIONS2D[i][j - 2]
                    up2 = LOCATIONS2D[i - 2][j]
                    down2 = LOCATIONS2D[i + 2][j]
                    missOrBoundaryL2 = [Checked(left2, 'Miss'), Boundary(left2)]
                    missOrBoundaryU2 = [Checked(up2, 'Miss'), Boundary(up2)]
                    missOrBoundaryD2 = [Checked(down2, 'Miss'), Boundary(down2)]
                    E.add_constraint(Checked(location, 'Cornered Hit') >> (Checked(location, 'Hit') & (
                                                                             (Or(missOrBoundaryL) & Or(missOrBoundaryU) & Checked(down, 'Hit') & Or(missOrBoundaryD2)) | 
                                                                             (Or(missOrBoundaryD) & Or(missOrBoundaryU) & Checked(left, 'Hit') & Or(missOrBoundaryL2)) | 
                                                                             (Or(missOrBoundaryD) & Or(missOrBoundaryL) & Checked(up, 'Hit') & Or(missOrBoundaryU2)))))
            elif (j == 1):
                if (i != 1 and i != len(LOCATIONS2D) - 2):
                    right2 = LOCATIONS2D[i][j + 2]
                    up2 = LOCATIONS2D[i - 2][j]
                    down2 = LOCATIONS2D[i + 2][j]
                    missOrBoundaryR2 = [Checked(right2, 'Miss'), Boundary(right2)]
                    missOrBoundaryU2 = [Checked(up2, 'Miss'), Boundary(up2)]
                    missOrBoundaryD2 = [Checked(down2, 'Miss'), Boundary(down2)]
                    E.add_constraint(Checked(location, 'Cornered Hit') >> (Checked(location, 'Hit') & (
                                                                             (Or(missOrBoundaryR) & Or(missOrBoundaryU) & Checked(down, 'Hit') & Or(missOrBoundaryD2)) | 
                                                                             (Or(missOrBoundaryD) & Or(missOrBoundaryU) & Checked(right, 'Hit') & Or(missOrBoundaryR2)) | 
                                                                             (Or(missOrBoundaryD) & Or(missOrBoundaryR) & Checked(up, 'Hit') & Or(missOrBoundaryU2)))))
            if (i != 1 and i != len(LOCATIONS2D) - 2 and j != 1 and j != len(LOCATIONS2D[i]) - 2): # Not on an edge
                right2 = LOCATIONS2D[i][j + 2]
                left2 = LOCATIONS2D[i][j - 2]
                up2 = LOCATIONS2D[i - 2][j]
                down2 = LOCATIONS2D[i + 2][j]
                missOrBoundaryR2 = [Checked(right2, 'Miss'), Boundary(right2)]
                missOrBoundaryL2 = [Checked(left2, 'Miss'), Boundary(left2)]
                missOrBoundaryU2 = [Checked(up2, 'Miss'), Boundary(up2)]
                missOrBoundaryD2 = [Checked(down2, 'Miss'), Boundary(down2)]
                E.add_constraint(Checked(location, 'Cornered Hit') >> (Checked(location, 'Hit') & (
                                                                         (Or(missOrBoundaryR) & Or(missOrBoundaryL) & Or(missOrBoundaryU) & Checked(down, 'Hit') & Or(missOrBoundaryD2)) | 
                                                                         (Or(missOrBoundaryD) & Or(missOrBoundaryL) & Or(missOrBoundaryU) & Checked(right, 'Hit') & Or(missOrBoundaryR2)) | 
                                                                         (Or(missOrBoundaryD) & Or(missOrBoundaryR) & Or(missOrBoundaryU) & Checked(left, 'Hit') & Or(missOrBoundaryL2)) | 
                                                                         (Or(missOrBoundaryD) & Or(missOrBoundaryR) & Or(missOrBoundaryL) & Checked(up, 'Hit') & Or(missOrBoundaryU2)))))
            

            adjacentCorner = [Checked(right, 'Cornered Hit'), Checked(left, 'Cornered Hit'), Checked(up, 'Cornered Hit'), Checked(down, 'Cornered Hit')] # Next to a cornered hit
            E.add_constraint(Unchecked(location, 'Possible Sunk') >> (Checked(location, 'Hit') & (Or(adjacentCorner) | Checked(location, 'Cornered Hit')))) # Possible Sunk means a hit next to a cornered hit
            # Being next to a Possible Sunk means the spot is unlikely to be part of a ship, Unlikely Segments will only be shot at as a last priority
            E.add_constraint(Unchecked(location, 'Unlikely Segment') >> ((Unchecked(right, 'Possible Sunk')) | (Unchecked(left, 'Possible Sunk')) | (Unchecked(up, 'Possible Sunk')) | (Unchecked(down, 'Possible Sunk'))))


'''
    This function combined with findSunkShips has a bug where it changes the status of Sunk sometimes (not Possible Sunk). It doesn't affect the result since Possible Sunk is the important proposition, 
    but can lead to confusing results in the solutions output. They are both very large functions so since the bug doesn't affect results I will leave it as is. They also work perfectly independently.
    Feedback on how to fix it would be appreciated, but it might not be able to fixed unless I redo both functions entirely.
'''
def findShipType():
    for i in range(1, len(LOCATIONS2D) - 1):
        for j in range(1, len(LOCATIONS2D[i]) - 1):
                
                location = LOCATIONS2D[i][j]
                right = LOCATIONS2D[i][j + 1]
                left = LOCATIONS2D[i][j - 1]
                up = LOCATIONS2D[i - 1][j]
                down = LOCATIONS2D[i + 1][j]

                # Between two Sunks or Possible Sunks
                inTheMiddleH = [Checked(right, 'Sunk'), Checked(left, 'Sunk')]
                inTheMiddleV = [Checked(up, 'Sunk'), Checked(down, 'Sunk')]
                inTheMiddleHP = [Unchecked(right, 'Possible Sunk'), Unchecked(left, 'Possible Sunk')]
                inTheMiddleVP = [Unchecked(up, 'Possible Sunk'), Unchecked(down, 'Possible Sunk')]
    
                # This also identifies possible sunk ships since the model might solve the board before being certain that the ship is sunk
                if (i == len(LOCATIONS2D) - 2):
                    up2 = LOCATIONS2D[i - 2][j]
                    if (j == 1):
                        right2 = LOCATIONS2D[i][j + 2]
                        # Sub's are sunk segments with only one sunk segment next to them, Des's are sunk segments with two sunk segments next to them
                        E.add_constraint(Ship(location, 'sub', False) >> (Checked(location, 'Sunk') & ((Checked(right, 'Sunk') & ~Checked(right2, 'Sunk')) | (Checked(up, 'Sunk') & ~Checked(up2, 'Sunk')))))
                        E.add_constraint(Ship(location, 'des', False) >> (Checked(location, 'Sunk') & ((Checked(right, 'Sunk') & Checked(right2, 'Sunk')) | (Checked(up, 'Sunk') & Checked(up2, 'Sunk')))))
                        E.add_constraint(Ship(location, 'sub', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(right, 'Possible Sunk') & ~Unchecked(right2, 'Possible Sunk')) | (Unchecked(up, 'Possible Sunk') & ~Unchecked(up2, 'Possible Sunk')))))
                        E.add_constraint(Ship(location, 'des', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(right, 'Possible Sunk') & Unchecked(right2, 'Possible Sunk')) | (Unchecked(up, 'Possible Sunk') & Unchecked(up2, 'Possible Sunk')))))
                    elif (j == len(LOCATIONS2D[i]) - 2):
                        left2 = LOCATIONS2D[i][j - 2]
                        E.add_constraint(Ship(location, 'sub', False) >> (Checked(location, 'Sunk') & ((Checked(left, 'Sunk') & ~Checked(left2, 'Sunk')) | (Checked(up, 'Sunk') & ~Checked(up2, 'Sunk')))))
                        E.add_constraint(Ship(location, 'des', False) >> (Checked(location, 'Sunk') & ((Checked(left, 'Sunk') & Checked(left2, 'Sunk')) | (Checked(up, 'Sunk') & Checked(up2, 'Sunk')))))
                        E.add_constraint(Ship(location, 'sub', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(left, 'Possible Sunk') & ~Unchecked(left2, 'Possible Sunk')) | (Unchecked(up, 'Possible Sunk') & ~Unchecked(up2, 'Possible Sunk')))))
                        E.add_constraint(Ship(location, 'des', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(left, 'Possible Sunk') & Unchecked(left2, 'Possible Sunk')) | (Unchecked(up, 'Possible Sunk') & Unchecked(up2, 'Possible Sunk')))))
                    else:
                        right2 = LOCATIONS2D[i][j + 2]
                        left2 = LOCATIONS2D[i][j - 2]

                        # There is a sunk spot only on one side of the ship (used only for subs)
                        shipRight = [Checked(right, 'Sunk'), ~Checked(right2, 'Sunk'), ~Checked(left, 'Sunk')]
                        shipLeft = [Checked(left, 'Sunk'), ~Checked(left2, 'Sunk'), ~Checked(right, 'Sunk')]
                        shipRightP = [Unchecked(right, 'Possible Sunk'), ~Unchecked(right2, 'Possible Sunk'), ~Unchecked(left, 'Possible Sunk')]
                        shipLeftP = [Unchecked(left, 'Possible Sunk'), ~Unchecked(left2, 'Possible Sunk'), ~Unchecked(right, 'Possible Sunk')]

                        E.add_constraint(Ship(location, 'sub', False) >> (Checked(location, 'Sunk') & (And(shipRight) | And(shipLeft) | (Checked(up, 'Sunk') & ~Checked(up2, 'Sunk')))))
                        E.add_constraint(Ship(location, 'des', False) >> (Checked(location, 'Sunk') & ((Checked(right, 'Sunk') & Checked(right2, 'Sunk')) | (Checked(left, 'Sunk') & Checked(left2, 'Sunk')) | (Checked(up, 'Sunk') & Checked(up2, 'Sunk')) | (And(inTheMiddleH)))))
                        E.add_constraint(Ship(location, 'sub', True) >> (Unchecked(location, 'Possible Sunk') & (And(shipRightP) | And(shipLeftP) | (Unchecked(up, 'Possible Sunk') & ~Unchecked(up2, 'Possible Sunk')))))
                        E.add_constraint(Ship(location, 'des', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(right, 'Possible Sunk') & Unchecked(right2, 'Possible Sunk')) | (Unchecked(left, 'Possible Sunk') & Unchecked(left2, 'Possible Sunk')) | (Unchecked(up, 'Possible Sunk') & Unchecked(up2, 'Possible Sunk')) | (And(inTheMiddleHP)))))
                elif (i == 1):
                    down2 = LOCATIONS2D[i + 2][j]
                    if (j == 1):
                        right2 = LOCATIONS2D[i][j + 2]
                        E.add_constraint(Ship(location, 'sub', False) >> (Checked(location, 'Sunk') & ((Checked(right, 'Sunk') & ~Checked(right2, 'Sunk')) | (Checked(down, 'Sunk') & ~Checked(down2, 'Sunk')))))
                        E.add_constraint(Ship(location, 'des', False) >> (Checked(location, 'Sunk') & ((Checked(right, 'Sunk') & Checked(right2, 'Sunk')) | (Checked(down, 'Sunk') & Checked(down2, 'Sunk')))))
                        E.add_constraint(Ship(location, 'sub', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(right, 'Possible Sunk') & ~Unchecked(right2, 'Possible Sunk')) | (Unchecked(down, 'Possible Sunk') & ~Unchecked(down2, 'Possible Sunk')))))
                        E.add_constraint(Ship(location, 'des', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(right, 'Possible Sunk') & Unchecked(right2, 'Possible Sunk')) | (Unchecked(down, 'Possible Sunk') & Unchecked(down2, 'Possible Sunk')))))
                    elif (j == len(LOCATIONS2D[i]) - 2):
                        left2 = LOCATIONS2D[i][j - 2]
                        E.add_constraint(Ship(location, 'sub', False) >> (Checked(location, 'Sunk') & ((Checked(left, 'Sunk') & ~Checked(left2, 'Sunk')) | (Checked(down, 'Sunk') & ~Checked(down2, 'Sunk')))))
                        E.add_constraint(Ship(location, 'des', False) >> (Checked(location, 'Sunk') & ((Checked(left, 'Sunk') & Checked(left2, 'Sunk')) | (Checked(down, 'Sunk') & Checked(down2, 'Sunk')))))
                        E.add_constraint(Ship(location, 'sub', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(left, 'Possible Sunk') & ~Unchecked(left2, 'Possible Sunk')) | (Unchecked(down, 'Possible Sunk') & ~Unchecked(down2, 'Possible Sunk')))))
                        E.add_constraint(Ship(location, 'des', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(left, 'Possible Sunk') & Unchecked(left2, 'Possible Sunk')) | (Unchecked(down, 'Possible Sunk') & Unchecked(down2, 'Possible Sunk')))))
                    else:
                        right2 = LOCATIONS2D[i][j + 2]
                        left2 = LOCATIONS2D[i][j - 2]

                        shipRight = [Checked(right, 'Sunk'), ~Checked(right2, 'Sunk'), ~Checked(left, 'Sunk')]
                        shipLeft = [Checked(left, 'Sunk'), ~Checked(left2, 'Sunk'), ~Checked(right, 'Sunk')]
                        shipRightP = [Unchecked(right, 'Possible Sunk'), ~Unchecked(right2, 'Possible Sunk'), ~Unchecked(left, 'Possible Sunk')]
                        shipLeftP = [Unchecked(left, 'Possible Sunk'), ~Unchecked(left2, 'Possible Sunk'), ~Unchecked(right, 'Possible Sunk')]

                        E.add_constraint(Ship(location, 'sub', False) >> (Checked(location, 'Sunk') & (And(shipRight) | And(shipLeft) | (Checked(down, 'Sunk') & ~Checked(down2, 'Sunk')))))
                        E.add_constraint(Ship(location, 'des', False) >> (Checked(location, 'Sunk') & ((Checked(right, 'Sunk') & Checked(right2, 'Sunk')) | (Checked(left, 'Sunk') & Checked(left2, 'Sunk')) | (Checked(down, 'Sunk') & Checked(down2, 'Sunk')) | (And(inTheMiddleH)))))
                        E.add_constraint(Ship(location, 'sub', True) >> (Unchecked(location, 'Possible Sunk') & (And(shipRightP) | And(shipLeftP) | (Unchecked(down, 'Possible Sunk') & ~Unchecked(down2, 'Possible Sunk')))))
                        E.add_constraint(Ship(location, 'des', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(right, 'Possible Sunk') & Unchecked(right2, 'Possible Sunk')) | (Unchecked(left, 'Possible Sunk') & Unchecked(left2, 'Possible Sunk')) | (Unchecked(down, 'Possible Sunk') & Unchecked(down2, 'Possible Sunk')) | (And(inTheMiddleHP)))))
                if (j == len(LOCATIONS2D[i]) - 2):
                    if (i != 1 and i != len(LOCATIONS2D) - 2):
                        left2 = LOCATIONS2D[i][j - 2]
                        up2 = LOCATIONS2D[i - 2][j]
                        down2 = LOCATIONS2D[i + 2][j]

                        shipDown = [Checked(down, 'Sunk'), ~Checked(down2, 'Sunk'), ~Checked(up, 'Sunk')]
                        shipUp = [Checked(up, 'Sunk'), ~Checked(up2, 'Sunk'), ~Checked(down, 'Sunk')]
                        shipDownP = [Unchecked(down, 'Possible Sunk'), ~Unchecked(down2, 'Possible Sunk'), ~Unchecked(up, 'Possible Sunk')]
                        shipUpP = [Unchecked(up, 'Possible Sunk'), ~Unchecked(up2, 'Possible Sunk'), ~Unchecked(down, 'Possible Sunk')]

                        E.add_constraint(Ship(location, 'sub', False) >> (Checked(location, 'Sunk') & ((Checked(left, 'Sunk') & ~Checked(left2, 'Sunk')) | And(shipUp) | And(shipDown))))
                        E.add_constraint(Ship(location, 'des', False) >> (Checked(location, 'Sunk') & ((Checked(left, 'Sunk') & Checked(left2, 'Sunk')) | (Checked(up, 'Sunk') & Checked(up2, 'Sunk')) | (Checked(down, 'Sunk') & Checked(down2, 'Sunk')) | (And(inTheMiddleV)))))
                        E.add_constraint(Ship(location, 'sub', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(left, 'Possible Sunk') & ~Unchecked(left2, 'Possible Sunk')) | And(shipUpP) | (And(shipDownP)))))
                        E.add_constraint(Ship(location, 'des', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(left, 'Possible Sunk') & Unchecked(left2, 'Possible Sunk')) | (Unchecked(up, 'Possible Sunk') & Unchecked(up2, 'Possible Sunk')) | (Unchecked(down, 'Possible Sunk') & Unchecked(down2, 'Possible Sunk')) | (And(inTheMiddleVP)))))
                elif (j == 1):
                    if (i != 1 and i != len(LOCATIONS2D) - 2):
                        right2 = LOCATIONS2D[i][j + 2]
                        up2 = LOCATIONS2D[i - 2][j]
                        down2 = LOCATIONS2D[i + 2][j]

                        shipDown = [Checked(down, 'Sunk'), ~Checked(down2, 'Sunk'), ~Checked(up, 'Sunk')]
                        shipUp = [Checked(up, 'Sunk'), ~Checked(up2, 'Sunk'), ~Checked(down, 'Sunk')]
                        shipDownP = [Unchecked(down, 'Possible Sunk'), ~Unchecked(down2, 'Possible Sunk'), ~Unchecked(up, 'Possible Sunk')]
                        shipUpP = [Unchecked(up, 'Possible Sunk'), ~Unchecked(up2, 'Possible Sunk'), ~Unchecked(down, 'Possible Sunk')]

                        E.add_constraint(Ship(location, 'sub', False) >> (Checked(location, 'Sunk') & ((Checked(right, 'Sunk') & ~Checked(right2, 'Sunk')) | And(shipUp) | And(shipDown))))
                        E.add_constraint(Ship(location, 'des', False) >> (Checked(location, 'Sunk') & ((Checked(right, 'Sunk') & Checked(right2, 'Sunk')) | (Checked(up, 'Sunk') & Checked(up2, 'Sunk')) | (Checked(down, 'Sunk') & Checked(down2, 'Sunk')) | (And(inTheMiddleV)))))
                        E.add_constraint(Ship(location, 'sub', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(right, 'Possible Sunk') & ~Unchecked(right2, 'Possible Sunk')) | And(shipUpP) | And(shipDownP))))
                        E.add_constraint(Ship(location, 'des', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(right, 'Possible Sunk') & Unchecked(right2, 'Possible Sunk')) | (Unchecked(up, 'Possible Sunk') & Unchecked(up2, 'Possible Sunk')) | (Unchecked(down, 'Possible Sunk') & Unchecked(down2, 'Possible Sunk')) | (And(inTheMiddleVP)))))
                if (i != 1 and i != len(LOCATIONS2D) - 2 and j != 1 and j != len(LOCATIONS2D[i]) - 2): # Not on an edge
                    right2 = LOCATIONS2D[i][j + 2]
                    left2 = LOCATIONS2D[i][j - 2]
                    up2 = LOCATIONS2D[i - 2][j]
                    down2 = LOCATIONS2D[i + 2][j]

                    shipRight = [Checked(right, 'Sunk'), ~Checked(right2, 'Sunk'), ~Checked(left, 'Sunk')]
                    shipLeft = [Checked(left, 'Sunk'), ~Checked(left2, 'Sunk'), ~Checked(right, 'Sunk')]
                    shipUp = [Checked(up, 'Sunk'), ~Checked(up2, 'Sunk'), ~Checked(down, 'Sunk')]
                    shipDown = [Checked(down, 'Sunk'), ~Checked(down2, 'Sunk'), ~Checked(up, 'Sunk')]
                    shipRightP = [Unchecked(right, 'Possible Sunk'), ~Unchecked(right2, 'Possible Sunk'), ~Unchecked(left, 'Possible Sunk')]
                    shipLeftP = [Unchecked(left, 'Possible Sunk'), ~Unchecked(left2, 'Possible Sunk'), ~Unchecked(right, 'Possible Sunk')]
                    shipUpP = [Unchecked(up, 'Possible Sunk'), ~Unchecked(up2, 'Possible Sunk'), ~Unchecked(down, 'Possible Sunk')]
                    shipDownP = [Unchecked(down, 'Possible Sunk'), ~Unchecked(down2, 'Possible Sunk'), ~Unchecked(up, 'Possible Sunk')]

                    E.add_constraint(Ship(location, 'sub', False) >> (Checked(location, 'Sunk') & (And(shipRight) | And(shipLeft) | And(shipUp) | (And(shipDown)))))
                    E.add_constraint(Ship(location, 'des', False) >> (Checked(location, 'Sunk') & ((Checked(right, 'Sunk') & Checked(right2, 'Sunk')) | (Checked(left, 'Sunk') & Checked(left2, 'Sunk')) | (Checked(up, 'Sunk') & Checked(up2, 'Sunk')) | (Checked(down, 'Sunk') & Checked(down2, 'Sunk')) | (And(inTheMiddleH) | And(inTheMiddleV)))))
                    E.add_constraint(Ship(location, 'sub', True) >> (Unchecked(location, 'Possible Sunk') & (And(shipRightP) | And(shipLeftP) | And(shipUpP) | And(shipDownP))))
                    E.add_constraint(Ship(location, 'des', True) >> (Unchecked(location, 'Possible Sunk') & ((Unchecked(right, 'Possible Sunk') & Unchecked(right2, 'Possible Sunk')) | (Unchecked(left, 'Possible Sunk') & Unchecked(left2, 'Possible Sunk')) | (Unchecked(up, 'Possible Sunk') & Unchecked(up2, 'Possible Sunk')) | (Unchecked(down, 'Possible Sunk') & Unchecked(down2, 'Possible Sunk')) | (And(inTheMiddleHP) | And(inTheMiddleVP)))))




if __name__ == "__main__":

    # Get all board information from either the user or premade boards. CompleteBoard is the board with the starting setup, boardSetup is the board that will be updated as the game progresses
    LOCATIONS, LOCATIONS2D, completeBoard, boardSetup, numSegments = getUserBoard()

    # Show the user what board is being solved
    print("Your complete board: \n")
    for i in completeBoard:
        print(i)
    print()

    # Show the user the board that the model sees
    print("Step 0:\n")
    for i in boardSetup:
        print(i)
    print()

    completed = False # Solved?
    singleStep = True # Jump to the end or go step by step
    step = 1
    while not completed:
        
        if (singleStep):
            decision = input("Press enter to continue or type 'q' to jump to the end: \n")
            if (decision == 'q'):
                singleStep = False

        print(f"Step {step}: \n")

        T = theory()
        T = T.compile()
        solutions = T.solve()

        numSolutions = count_solutions(T)
        showSolutions(solutions, numSolutions) # Show filtered/sorted solutions

        boardSetup, completed = solveBoard(boardSetup, completeBoard, numSegments, solutions) # Changes the state of the board

        step += 1