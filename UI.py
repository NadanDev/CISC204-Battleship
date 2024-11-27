import random

from CompleteBoards import boards3x3, boards4x4, boards5x5

def showSolutions(solutions, numSolutions, hideBoundaries = True, hideUnchecked = True):

    if (solutions):
        print("\n# Solutions: ", numSolutions)
        toPrint = []
        for k in solutions:
            if solutions[k]:
                if (hideBoundaries and str(k)[0] == "B"):
                    continue
                elif (hideUnchecked and str(k)[0] == "U"):
                    continue
                toPrint.append(str(k))
        
        toPrint.sort()
        for i in range(len(toPrint)):
            if (toPrint[i][0] != toPrint[i-1][0] or toPrint[i][2] != toPrint[i-1][2]):
                print("\n")
            print(toPrint[i])

    else:
        print("No solutions")




def solveBoard(boardSetup, complete, numSegments, solutions):
    possibleChoices = []
    highlyPossibleChoices = []
    for k in solutions:
        if (solutions[k]):
            if (str(k)[0] == "P"):
                possibleChoices.append([int(str(k)[21]) - 1, int(str(k)[22]) - 1])
            elif (str(k)[0] == "H" and str(k)[2] == "g"):
                highlyPossibleChoices.append([int(str(k)[28]) - 1, int(str(k)[29]) - 1])
        
    if (len(highlyPossibleChoices) > 0):
        choice = random.randrange(0, len(highlyPossibleChoices))
        if (complete[highlyPossibleChoices[choice][0]][highlyPossibleChoices[choice][1]] == 2):
            print(f"Almost certain hit at: L{highlyPossibleChoices[choice][0]}{highlyPossibleChoices[choice][1]}, and it hit!\n")
            boardSetup[highlyPossibleChoices[choice][0]][highlyPossibleChoices[choice][1]] = 2
        else:
            print(f"Almost certain hit at: L{highlyPossibleChoices[choice][0]}{highlyPossibleChoices[choice][1]}, and it missed!\n")
            boardSetup[highlyPossibleChoices[choice][0]][highlyPossibleChoices[choice][1]] = 1
    elif (len(possibleChoices) > 0):
        choice = random.randrange(0, len(possibleChoices))
        if (complete[possibleChoices[choice][0]][possibleChoices[choice][1]] == 2):
            print(f"Some chance hit at: L{possibleChoices[choice][0]}{possibleChoices[choice][1]}, and it hit!\n")
            boardSetup[possibleChoices[choice][0]][possibleChoices[choice][1]] = 2
        else:
            print(f"Some chance hit at: L{possibleChoices[choice][0]}{possibleChoices[choice][1]}, and it missed!\n")
            boardSetup[possibleChoices[choice][0]][possibleChoices[choice][1]] = 1
    else:
        spotsLeft = []
        for i in range(len(boardSetup)):
            for j in range(len(boardSetup[i])):
                if (boardSetup[i][j] == 0):
                    spotsLeft.append([i, j])
            
        choice = random.randrange(0, len(spotsLeft))
        if (complete[spotsLeft[choice][0]][spotsLeft[choice][1]] == 2):
            print(f"Random guess at: L{spotsLeft[choice][0]}{spotsLeft[choice][1]}, and it hit!\n")
            boardSetup[spotsLeft[choice][0]][spotsLeft[choice][1]] = 2
        else:
            print(f"Random guess at: L{spotsLeft[choice][0]}{spotsLeft[choice][1]}, and it missed!\n")
            boardSetup[spotsLeft[choice][0]][spotsLeft[choice][1]] = 1

    count = 0
    for i in range(len(complete)):
        for j in range(len(complete[i])):
            if (complete[i][j] == 2 and boardSetup[i][j] == 2):
                count += 1

    for i in boardSetup:
        print(i)
    print("\n")

    if (count == numSegments):

        print("Board Solved!\n")

        return boardSetup, True
    
    return boardSetup, False




def getUserBoard():

    numSegments = 0

    userChoice = input("Would you like to make your own completed board? (y/n): ")

    if (userChoice == 'y'):
        userBoardStr = input("Enter your board, rows seperated by commas and spaces seperated by spaces (ex. 1 2 1, 0 2 1, 0 0 0): ")

        if (str(len(userBoardStr)) not in ['19', '34', '53']):
            print("Invalid board setup (length)")
            exit()

        counter = 0
        boardSize = 0
        userBoard = []
        row = []
        for char in userBoardStr:
            if (char not in ['0', '1', '2', ' ', ',']):
                print("Invalid board setup (characters)")
                exit()

            if (char != ' '):
                if (char == ',' and counter != 0):
                    if (boardSize == 0):
                        boardSize = counter
                    userBoard.append(row)
                    row = []
                else:
                    row.append(int(char))
                    counter += 1
        userBoard.append(row)
        for i in range(len(userBoard)):
            for j in range(len(userBoard[i])):
                if (userBoard[i][j] == 2):
                    numSegments += 1
    elif (userChoice == 'n'):
        boardSize = int(input("Enter the size of the pre-made board (3, 4, 5): "))

        if (boardSize not in [3, 4, 5]):
            print("Invalid board size")
            exit()

        randomBoard = random.randrange(0, 10)
        if (boardSize == 3):
            userBoard = boards3x3[randomBoard]
        elif (boardSize == 4):
            userBoard = boards4x4[randomBoard]
        elif (boardSize == 5):
            userBoard = boards5x5[randomBoard]

        for i in range(len(userBoard)):
            for j in range(len(userBoard[i])):
                if (userBoard[i][j] == 2):
                    numSegments += 1
    else:
        print("Invalid choice")
        exit()

    if (boardSize == 3):
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