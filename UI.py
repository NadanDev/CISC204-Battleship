


def showSolutions(solutions, numSolutions, showOnlyHits = True):

    if (solutions):
        print("\n# Solutions: ", numSolutions)
        print("\n")
        for k in solutions:
            if solutions[k]:
                if (showOnlyHits and str(k)[0] == "B"):
                    continue
                print(k, "\n")
    else:
        print("No solutions")