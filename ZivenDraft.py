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

