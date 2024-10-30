from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

from nnf import config
config.sat_backend = "kissat"

BOARD_SIZE = 3
E = Encoding()

# Battleship board variables
Ship_Segment = []
Hit = []
Destroyer_Count = 2  # Number of destroyers to place, each with length 2

# Initialize board variables
for i in range(BOARD_SIZE):
    Ship_Segment.append([])
    Hit.append([])
    for j in range(BOARD_SIZE):
        Ship_Segment[i].append(proposition(E)(f'Ship_Segment_{i},{j}'))
        Hit[i].append(proposition(E)(f'Hit_{i},{j}'))
        
        
# Board Boundary Constraint: All ship segments must be within the bounds of the game board
def hit_constraint():
    constraint = []
    for i in range(1, BOARD_SIZE -1):
        for j in range(1, BOARD_SIZE -1):
            constraint.append(Hit[i][j] >> Ship_Segment[i][j])
    return constraint

# 0 - No checked  1 - Ship, 2 - Hit water, 3 - Hit ship
boardSetup = [
    2, 3, 2,
    0, 1, 0,
    0, 0, 0
]

def dedcution_constraint():
    constraints = []
    for i in range(1, BOARD_SIZE -1):
        for j in range(1, BOARD_SIZE -1):
            constraints.append(Hit[i][j] & ~Hit [i+1][j] & ~Hit [i][j+1] & ~Hit [i-1][j] >> Hit[i][j-1])
    return constraints

def findShipType():
    checked = []
    for i in range(1, len(LOCATIONS2D) - 1):
        for j in range(1, len(LOCATIONS2D[i]) - 1):
            location = LOCATIONS2D[i][j]

            if boardSetup[i - 1][j - 1] == 2 and location not in checked:
                horizontalHits = [location]
                verticalHits = [location]

                # Check horizontal hits
                incr = 1
                while j + incr < len(LOCATIONS2D[i]) - 1 and boardSetup[i - 1][j - 1 + incr] == 2:
                    horizontalHits.append(LOCATIONS2D[i][j + incr])
                    incr += 1

                incr = 1
                while j - incr > 0 and boardSetup[i - 1][j - 1 - incr] == 2:
                    horizontalHits.append(LOCATIONS2D[i][j - incr])
                    incr += 1

                # Check vertical hits
                incr = 1
                while i + incr < len(LOCATIONS2D) - 1 and boardSetup[i - 1 + incr][j - 1] == 2:
                    verticalHits.append(LOCATIONS2D[i + incr][j])
                    incr += 1

                incr = 1
                while i - incr > 0 and boardSetup[i - 1 - incr][j - 1] == 2:
                    verticalHits.append(LOCATIONS2D[i - incr][j])
                    incr += 1

                # Assign ship type depending on the number of hits in a row
                if len(horizontalHits) == STYPES['des']:
                    for loc in horizontalHits:
                        E.add_constraint(Ship(loc, 'des'))
                elif len(verticalHits) == STYPES['des']:
                    for loc in verticalHits:
                        E.add_constraint(Ship(loc, 'des'))
                elif len(horizontalHits) == STYPES['sub']:
                    for loc in horizontalHits:
                        E.add_constraint(Ship(loc, 'sub'))
                elif len(verticalHits) == STYPES['sub']:
                    for loc in verticalHits:
                        E.add_constraint(Ship(loc, 'sub'))

                # Mark these locations as checked
                checked = checked + horizontalHits + verticalHits


def theory():
    # ************HITS************
    for i in range(len(boardSetup)):
        for j in range(len(boardSetup[i])):
            if boardSetup[i][j] == 2:
                E.add_constraint(Hit(LOCATIONS2D[i + 1][j + 1]))
                possibleShip = [
                    Hit(LOCATIONS2D[i + 2][j + 1]),
                    Hit(LOCATIONS2D[i + 1][j + 2]),
                    Hit(LOCATIONS2D[i][j + 1]),
                    Hit(LOCATIONS2D[i + 1][j])
                ]
                constraint.add_exactly_one(E, possibleShip)

    for i in range(len(boardSetup)):  # No hit and miss in the same spot
        for j in range(len(boardSetup[i])):
            if boardSetup[i][j] == 1:
                E.add_constraint(~Hit(LOCATIONS2D[i + 1][j + 1]))

    # ************BOUNDARY************
    for i in range(len(LOCATIONS2D)):
        for j in range(len(LOCATIONS2D[i])):
            if LOCATIONS2D[i][j][0] == 'B':
                E.add_constraint(Boundary(LOCATIONS2D[i][j]))
                E.add_constraint(~(Boundary(LOCATIONS2D[i][j]) & Hit(LOCATIONS2D[i][j])))

    # Find and assign ship types based on hits
    findShipType()

    return E