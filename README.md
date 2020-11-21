# Solving Minesweeper 
This library aims to solve the game Minesweeper as a Constraint Satisfaction Problem (CSP) by developing constraints for each cell observed adjacent to a Minesweeper clue. Furthermore, the library allows for predictive solving by creating a binary tree of potential configurations that satisfy the set of constraints.

# Using the Minesweeper Library
* Example package setup with file: test.py
```python
from pyMineSweeperSolver import MinesweeperSolver
from pyMineSweeperSolver import MINIMIZE, MineSweeper

driver = MinesweeperSolver(dimensions=16, density=0.4, minimize=MINIMIZE.COST, mode=MineSweeper.PRODUCTION_MAPS)
driver.run()
	
```
- The following variables are responsible for changing the Minesweeper map configuration along with how the agent attempts to solve the map:

| Variable Name | Type Of Value | Description
|-------------|----------|------------------------------------------------------------------------------------------|
| dimensions | int | the dimensions for the map **Note:** You must input a value for this within the range 3 <= dimensions <= 256 |
| density | float | the mine density for the map **Note:** This input must be within the range 0.01 <= density < 1 |
| density_offset | float | how much to increase the mine density after completion of a trial |
| trials | int | how many trials the agent should conduct |
| subtrials | int | how many sub-trials the agent should conduct at a particular mine density|
| minimize | int | Minesweeper.NONE solves using python random selections, and Minesweeper.COST solves by minimizing cost while Minesweeper.RISK solves by minimizing  RISK |
| copyCacheState | boolean | Saves Agent moves at each step. **Note:** this only shows the agent's move for the last trial conducted|
| mode | int | Use MineSweeper.PRODUCTION for solely seeing the agent's accuracy for solving a map or MineSweeper.PRODUCTION_MAPS to see how the agent's map updates as it solves, or receive MineSweeper.DEBUG for detailed console log of program execution|
