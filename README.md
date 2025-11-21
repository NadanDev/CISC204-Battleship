# CISC/CMPE 204 Modelling Project Group 1 : BATTLESHIP

Our project will solve a game of battleship given a user-created board or a pre-made board. The model will run until every ship segment on the board is hit.

HOW TO RUN: 
* Build image with "docker build -t battleship ."
* Run in container using "docker run -it -v $(pwd):/PROJECT battleship /bin/bash"
* Run "python run.py"

Options outside of running the program are changing the hideBoundaries and hideUnchecked arguments in the showSolutions function in UI.py (though these don't reveal anything helpful). All pre-made boards
are stored in CompleteBoards.py and can easily be added to, but custom boards are more easily created from running the program itself.

## Structure

* `documents`: Contains folders for both of your draft and final submissions. README.md files are included in both.
* `run.py`: General wrapper script that you can choose to use or not. Only requirement is that you implement the one function inside of there for the auto-checks.
* `test.py`: Run this file to confirm that your submission has everything required. This essentially just means it will check for the right files and sufficient theory size.