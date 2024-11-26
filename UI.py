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