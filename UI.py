import random

from CompleteBoards import boards3x3, boards4x4, boards5x5

def showSolutions(solutions, numSolutions, hideBoundaries = True, hideUnchecked = True): # Change hideBoundaries and hideUnchecked to show them but it just makes it look messy

    if (solutions):
        print("\n# Solutions: ", numSolutions)

        toPrint = [] # List of solutions to print (will be sorted)
        for k in solutions:
            if solutions[k]:
                if (hideBoundaries and str(k)[0] == "B"): # Hide boundaries
                    continue
                elif (hideUnchecked and str(k)[0] == "U" and str(k)[2] == "c"): # Hide unchecked
                    continue
                toPrint.append(str(k)) # Add everything else to the list
        
        toPrint.sort()
        for i in range(len(toPrint)):
            if (toPrint[i][0] != toPrint[i-1][0] or toPrint[i][2] != toPrint[i-1][2] or (toPrint[i][10] != toPrint[i-1][10] and toPrint[i][0] != "M" and toPrint[i][0] != "S")): # Add spaces between different types of solutions
                print()
            print(toPrint[i])
        print('\n')

    else:
        print("No solutions")




def solveBoard(boardSetup, complete, numSegments, solutions):

    # What will affect choices more
    possibleChoices = []
    highlyPossibleChoices = []
    unlikelyChoices = []

    for k in solutions:
        if (solutions[k]):
            if (str(k)[0] == "P" and str(k)[10] != "u"): # If it's a possible segment
                possibleChoices.append([int(str(k)[21]) - 1, int(str(k)[22]) - 1]) # Add the location
            elif (str(k)[0] == "H" and str(k)[2] == "g"): # If it's a highly possible segment
                highlyPossibleChoices.append([int(str(k)[28]) - 1, int(str(k)[29]) - 1])
            elif (str(k)[0] == "U" and str(k)[2] == "l"): # If it's an unlikely segment
                unlikelyChoices.append([int(str(k)[21]) - 1, int(str(k)[22]) - 1])

    for i in range(len(unlikelyChoices)):
        if (unlikelyChoices[i] in possibleChoices):
            possibleChoices.remove(unlikelyChoices[i]) # Remove possible choices that are unlikely
        
    if (len(highlyPossibleChoices) > 0): # Always choose highly possible choices first
        choice = random.randrange(0, len(highlyPossibleChoices)) # Choose a random highly possible choice
        if (complete[highlyPossibleChoices[choice][0]][highlyPossibleChoices[choice][1]] == 2): # Check the starting board and see if the choice is correct
            print(f"Almost certain hit at: L{highlyPossibleChoices[choice][0] + 1}{highlyPossibleChoices[choice][1] + 1}, and it hit!\n")
            boardSetup[highlyPossibleChoices[choice][0]][highlyPossibleChoices[choice][1]] = 2
        else:
            print(f"Almost certain hit at: L{highlyPossibleChoices[choice][0] + 1}{highlyPossibleChoices[choice][1] + 1}, and it missed!\n")
            boardSetup[highlyPossibleChoices[choice][0]][highlyPossibleChoices[choice][1]] = 1
    elif (len(possibleChoices) > 0): # Choose possible choices if there are no highly possible choices
        choice = random.randrange(0, len(possibleChoices))
        if (complete[possibleChoices[choice][0]][possibleChoices[choice][1]] == 2):
            print(f"Some chance hit at: L{possibleChoices[choice][0] + 1}{possibleChoices[choice][1] + 1}, and it hit!\n")
            boardSetup[possibleChoices[choice][0]][possibleChoices[choice][1]] = 2
        else:
            print(f"Some chance hit at: L{possibleChoices[choice][0] + 1}{possibleChoices[choice][1] + 1}, and it missed!\n")
            boardSetup[possibleChoices[choice][0]][possibleChoices[choice][1]] = 1
    else: # If there are no possible choices, choose a random spot on the board
        spotsLeft = []
        onlyUnlikely = True # If there are only unlikely choices left

        for i in range(len(boardSetup)):
            for j in range(len(boardSetup[i])):
                if (boardSetup[i][j] == 0):
                    spotsLeft.append([i, j])
        
        for i in range(len(spotsLeft)):
            if (spotsLeft[i] not in unlikelyChoices): # Check if there are any spots left that aren't unlikely
                onlyUnlikely = False
                break

        if (not onlyUnlikely):
            for i in range(len(unlikelyChoices)):
                if (unlikelyChoices[i] in spotsLeft):
                    spotsLeft.remove(unlikelyChoices[i]) # Remove unlikely choices from spots left
        
        choice = random.randrange(0, len(spotsLeft))
        if (complete[spotsLeft[choice][0]][spotsLeft[choice][1]] == 2): # Check if the random shot is correct
            print(f"Random guess at: L{spotsLeft[choice][0] + 1}{spotsLeft[choice][1] + 1}, and it hit!\n")
            boardSetup[spotsLeft[choice][0]][spotsLeft[choice][1]] = 2
        else:
            print(f"Random guess at: L{spotsLeft[choice][0] + 1}{spotsLeft[choice][1] + 1}, and it missed!\n")
            boardSetup[spotsLeft[choice][0]][spotsLeft[choice][1]] = 1

    # Compare hits on the board to the complete board
    count = 0
    for i in range(len(complete)):
        for j in range(len(complete[i])):
            if (complete[i][j] == 2 and boardSetup[i][j] == 2):
                count += 1

    for i in boardSetup:
        print(i)
    print("\n")

    if (count == numSegments): # If the counts for both boards are the same then the board is solved

        print("Board Solved!\n")

        return boardSetup, True
    
    return boardSetup, False # Not solved



# Ask the user for a board setup
def getUserBoard():

    numSegments = 0

    userChoice = input("Would you like to make your own completed board? (y/n): ") # Premade or no

    if (userChoice == 'y'):
        userBoardStr = input("Enter your board, rows seperated by commas and spaces seperated by spaces (ex. 0 2 0, 0 2 0, 0 0 0): ") # Ask user for board

        if (str(len(userBoardStr)) not in ['19', '34', '53']): # If it's not a 3x3, 4x4, or 5x5 board
            print("Invalid board setup (length)")
            exit()

        counter = 0
        boardSize = 0
        userBoard = []
        row = []
        for char in userBoardStr:
            if (char not in ['0', '2', ' ', ',']): # Only characters that should be entered
                print("Invalid board setup (characters)")
                exit()

            if (char != ' '): # Skip spaces
                if (char == ',' and counter != 0): # If we've reached the end of one row
                    if (boardSize == 0):
                        boardSize = counter # Set the board size
                    
                    # Add the row to the board and reset the row
                    userBoard.append(row)
                    row = []
                else:
                    row.append(int(char))
                    counter += 1
        userBoard.append(row) # Add the last row

        for i in range(len(userBoard)):
            for j in range(len(userBoard[i])):
                if (userBoard[i][j] == 2):
                    numSegments += 1 # Count the number of segments
    elif (userChoice == 'n'): # Premade board
        boardSize = int(input("Enter the size of the pre-made board (3, 4, 5): ")) # Choose a size

        if (boardSize not in [3, 4, 5]):
            print("Invalid board size")
            exit()

        randomBoard = random.randrange(0, 10) # 10 of each size of board
        if (boardSize == 3):
            userBoard = boards3x3[randomBoard]
        elif (boardSize == 4):
            userBoard = boards4x4[randomBoard]
        elif (boardSize == 5):
            userBoard = boards5x5[randomBoard]

        for i in range(len(userBoard)):
            for j in range(len(userBoard[i])):
                if (userBoard[i][j] == 2):
                    numSegments += 1 # Count the number of segments
    else:
        print("Invalid choice")
        exit()

    if (boardSize == 3): # Depending on the board size, grab the correct board setup
        # 0 - Not Checked
        # 1 - Miss
        # 2 - Hit

        # 3x3 board
        boardSetup = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]

        LOCATIONS = [  # B spaces are boundaries, L spaces are playable
                'B00', 'B01', 'B02', 'B03', 'B04',
                'B10', 'L11', 'L12', 'L13', 'B14',
                'B20', 'L21', 'L22', 'L23', 'B24',
                'B30', 'L31', 'L32', 'L33', 'B34',
                'B40', 'B41', 'B42', 'B43', 'B44'
            ]

        LOCATIONS2D = [
                ['B00', 'B01', 'B02', 'B03', 'B04'],
                ['B10', 'L11', 'L12', 'L13', 'B14'],
                ['B20', 'L21', 'L22', 'L23', 'B24'],
                ['B30', 'L31', 'L32', 'L33', 'B34'],
                ['B40', 'B41', 'B42', 'B43', 'B44']
            ]
    elif (boardSize == 4):
        # 4x4 board
        boardSetup = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]

        LOCATIONS = [
            'B00', 'B01', 'B02', 'B03', 'B04', 'B05',
            'B10', 'L11', 'L12', 'L13', 'L14', 'B15',
            'B20', 'L21', 'L22', 'L23', 'L24', 'B25',
            'B30', 'L31', 'L32', 'L33', 'L34', 'B35',
            'B40', 'L41', 'L42', 'L43', 'L44', 'B45',
            'B50', 'B51', 'B52', 'B53', 'B54', 'B55'
        ]

        LOCATIONS2D = [
            ['B00', 'B01', 'B02', 'B03', 'B04', 'B05'],
            ['B10', 'L11', 'L12', 'L13', 'L14', 'B15'],
            ['B20', 'L21', 'L22', 'L23', 'L24', 'B25'],
            ['B30', 'L31', 'L32', 'L33', 'L34', 'B35'],
            ['B40', 'L41', 'L42', 'L43', 'L44', 'B45'],
            ['B50', 'B51', 'B52', 'B53', 'B54', 'B55']
        ]
    elif (boardSize == 5):
        # 5x5 board
        boardSetup = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
            
        LOCATIONS = [
            'B00', 'B01', 'B02', 'B03', 'B04', 'B05', 'B06',
            'B10', 'L11', 'L12', 'L13', 'L14', 'L15', 'B16',
            'B20', 'L21', 'L22', 'L23', 'L24', 'L25', 'B26',
            'B30', 'L31', 'L32', 'L33', 'L34', 'L35', 'B36',
            'B40', 'L41', 'L42', 'L43', 'L44', 'L45', 'B46',
            'B50', 'L51', 'L52', 'L53', 'L54', 'L55', 'B56',
            'B60', 'B61', 'B62', 'B63', 'B64', 'B65', 'B66'
        ]

        LOCATIONS2D = [
            ['B00', 'B01', 'B02', 'B03', 'B04', 'B05', 'B06'],
            ['B10', 'L11', 'L12', 'L13', 'L14', 'L15', 'B16'],
            ['B20', 'L21', 'L22', 'L23', 'L24', 'L25', 'B26'],
            ['B30', 'L31', 'L32', 'L33', 'L34', 'L35', 'B36'],
            ['B40', 'L41', 'L42', 'L43', 'L44', 'L45', 'B46'],
            ['B50', 'L51', 'L52', 'L53', 'L54', 'L55', 'B56'],
            ['B60', 'B61', 'B62', 'B63', 'B64', 'B65', 'B66']
        ]

    return LOCATIONS, LOCATIONS2D, userBoard, boardSetup, numSegments