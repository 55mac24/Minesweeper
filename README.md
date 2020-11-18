# Solving Minesweeper 
This library aims to solve the game Minesweeper as a Constraint Satisfaction Problem (CSP) by developing constraints for each cell observed adjacent to a Minesweeper clue. Furthermore, the library allows for predictive solving by creating a binary tree of potential configurations that satisfy the set of constraints.

# Using the Minesweeper Library

As of right now, the code works for solving Minesweeper solely as a Constraint Satisfaction Problem. Predictive solving is still in beta.

 ## Executing the Library
Run ```> python driver.py```
- **Note:** To change the map configurations, edit variables within the driver.py file. 

### driver.py
- This file is responsible for running trials to test the Agent.
	- Basic command-line parsing is provided in the file minesweeperArgParser.py, but the file has yet to be integrated with the existing code. This will be fixed in a later update.
- The following variables are responsible for changing the Minesweeper map configuration along with how the agent attempts to solve the map:

| Variable Name | Type Of Value | Description
|-------------|----------|------------------------------------------------------------------------------------------|
| dimensions | int | the dimensions for the map |
| density | float | the mine density for the map |
| density_offset | float | how much to increase the mine density after completion of a trial |
| trials | int | how many trials the agent should conduct |
| subtrials | int | how many sub-trials the agent should conduct at a particular mine density|
| minimize | int | Minesweeper.NONE solves without predictions, and Minesweeper.COST solves by minimizing cost while Minesweeper.RISK solves by minimizing  RISK |
| copyCacheState | boolean | Saves Agent moves at each step. **Note:** this only shows the agent's move for the last trial conducted|
