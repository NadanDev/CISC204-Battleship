# CISC/CMPE 204 Modelling Project : BATTLESHIP

Our project (currently) will solve a single scenario of a battleship board. Given hits, misses, and empty spaces on a board, the computer will determine where possible ships are
located and what type each ship is.

HOW TO RUN: 
* Run "Dockerfile" to avoid any errors.
* Run "run.py"

Currently the project does allow the user to change the board setup, but not in a user-friendly way. "boards.py" has a boardSetup array that can manipulated to set up any scenario. 
"UI.py" currently only has a showSolutions function which has a hideBoundaries boolean and be changed to show boundary solutions (which are not that interesting).

## Structure

* `documents`: Contains folders for both of your draft and final submissions. README.md files are included in both.
* `run.py`: General wrapper script that you can choose to use or not. Only requirement is that you implement the one function inside of there for the auto-checks.
* `test.py`: Run this file to confirm that your submission has everything required. This essentially just means it will check for the right files and sufficient theory size.