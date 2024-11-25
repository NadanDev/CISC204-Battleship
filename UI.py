


def showSolutions(solutions, numSolutions, hideBoundaries = True, hideUnchecked = True):

    if (solutions):
        print("\n# Solutions: ", numSolutions)
        print("\n")
        for k in solutions:
            if solutions[k]:
                if (hideBoundaries and str(k)[0] == "B"):
                    continue
                elif (hideUnchecked and str(k)[0] == "U"):
                    continue
                print(k, "\n")
    else:
        print("No solutions")