from nnf import Var, true
from lib204 import Encoding

BOARD_SIZE = 8

# Battleship board variables
Ship_Segment = []
Hit = []
Destroyer_Count = 2  # Number of destroyers to place, each with length 2

# Initialize board variables
for i in range(BOARD_SIZE):
    Ship_Segment.append([])
    Hit.append([])
    for j in range(BOARD_SIZE):
        Ship_Segment[i].append(Var(f'Ship_Segment_{i},{j}'))
        Hit[i].append(Var(f'Hit_{i},{j}'))
        
        
# Board Boundary Constraint: All ship segments must be within the bounds of the game board
def board_boundary_constraints():
    constraints = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            constraints.append(Ship_Segment[i][j] | ~Ship_Segment[i][j])
    return constraints