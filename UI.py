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




def getUserBoard():

    # 0 - Not Checked
    # 1 - Miss
    # 2 - Hit

    # DEFAULT BOARD SETUP
    boardSetup = [
            [0, 0, 0],
            [2, 0, 0],
            [0, 0, 0]
        ]

        # 3x3 board
    LOCATIONS = [  # B spaces are boundaries, L spaces are playable
            'B00', 'B10', 'B20', 'B30', 'B40',
            'B01', 'L11', 'L21', 'L31', 'B41',
            'B02', 'L12', 'L22', 'L32', 'B42',
            'B03', 'L13', 'L23', 'L33', 'B43',
            'B04', 'B14', 'B24', 'B34', 'B44'
        ]

    LOCATIONS2D = [
            ['B00', 'B10', 'B20', 'B30', 'B40'],
            ['B01', 'L11', 'L21', 'L31', 'B41'],
            ['B02', 'L12', 'L22', 'L32', 'B42'],
            ['B03', 'L13', 'L23', 'L33', 'B43'],
            ['B04', 'B14', 'B24', 'B34', 'B44']
        ]
    


    userChoice = input("Would you like to make your own board setup? (y/n): ")

    if (userChoice == 'y'):
        pass
    elif (userChoice == 'n'):
        return LOCATIONS, LOCATIONS2D, boardSetup
    else:
        print("Invalid choice")
        exit()
    
    userBoardStr = input("Enter your board setup, rows seperated by commas and spaces seperated by spaces (ex. 1 2 1, 0 2 1, 0 0 0): ")

    if (str(len(userBoardStr)) not in ['19', '34', '53']):
        print("Invalid board setup (length)")
        exit()

    counter = 0
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

    if (boardSize == 4):
        # 4x4 board
        LOCATIONS = [
            'B00', 'B10', 'B20', 'B30', 'B40', 'B50',
            'B01', 'L11', 'L21', 'L31', 'L41', 'B51',
            'B02', 'L12', 'L22', 'L32', 'L42', 'B52',
            'B03', 'L13', 'L23', 'L33', 'L43', 'B53',
            'B04', 'L14', 'L24', 'L34', 'L44', 'B54',
            'B05', 'B15', 'B25', 'B35', 'B45', 'B55'
        ]

        LOCATIONS2D = [
            ['B00', 'B10', 'B20', 'B30', 'B40', 'B50'],
            ['B01', 'L11', 'L21', 'L31', 'L41', 'B51'],
            ['B02', 'L12', 'L22', 'L32', 'L42', 'B52'],
            ['B03', 'L13', 'L23', 'L33', 'L43', 'B53'],
            ['B04', 'L14', 'L24', 'L34', 'L44', 'B54'],
            ['B05', 'B15', 'B25', 'B35', 'B45', 'B55']
        ]
    elif (boardSize == 5):
        # 5x5 board
        LOCATIONS = [
            'B00', 'B10', 'B20', 'B30', 'B40', 'B50', 'B60',
            'B01', 'L11', 'L21', 'L31', 'L41', 'L51', 'B61',
            'B02', 'L12', 'L22', 'L32', 'L42', 'L52', 'B62',
            'B03', 'L13', 'L23', 'L33', 'L43', 'L53', 'B63',
            'B04', 'L14', 'L24', 'L34', 'L44', 'L54', 'B64',
            'B05', 'L15', 'L25', 'L35', 'L45', 'L55', 'B65',
            'B06', 'B16', 'B26', 'B36', 'B46', 'B56', 'B66'
        ]

        LOCATIONS2D = [
            ['B00', 'B10', 'B20', 'B30', 'B40', 'B50', 'B60'],
            ['B01', 'L11', 'L21', 'L31', 'L41', 'L51', 'B61'],
            ['B02', 'L12', 'L22', 'L32', 'L42', 'L52', 'B62'],
            ['B03', 'L13', 'L23', 'L33', 'L43', 'L53', 'B63'],
            ['B04', 'L14', 'L24', 'L34', 'L44', 'L54', 'B64'],
            ['B05', 'L15', 'L25', 'L35', 'L45', 'L55', 'B65'],
            ['B06', 'B16', 'B26', 'B36', 'B46', 'B56', 'B66']
        ]

    return LOCATIONS, LOCATIONS2D, userBoard