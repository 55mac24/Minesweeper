# Solving Minesweeper 
This library aims to solve the game Minesweeper as a Constraint Satisfaction Problem (CSP) by developing constraints for each cell observed adjacent to a Minesweeper clue. Furthermore, the library allows for predictive solving by incoporating a binary tree that develops potential configurations that satisfy a set of constraints to determine which coordinate to select next in the Minesweeper map traversal based on how likely the coordinate is a mine.

# Using the Minesweeper Library
* Installing Package:
	- First clone the repository into some arbitrary root directory. For this example, a directory labeled 'test' will be the root directory for installing the package, and the cloned repository path will be './test/Minesweeper'. 
	- Within the root directory (in this example, 'test') for the repository, execute ```pip install ./Minesweeper```.
		- **Note:** Be sure the ```pip``` version corresponds to Python 3. If not, execute ```pip3 install ./Minesweeper```. Furthermore, it is recommended to use a virtual environment for the package installation. 
	- The package should now be accessible within the virtual environment if the package was configured a virtual environment. 
	
* Example package usuage with filename: test.py
```python
from Minesweeper import MinesweeperSolver
from Minesweeper import MINIMIZE, MineSweeper

driver = MinesweeperSolver(dimensions=16, density=0.4, minimize=MINIMIZE.COST, mode=MineSweeper.PRODUCTION)
driver.run()
	
```
- The following variables are responsible for changing the Minesweeper map configuration along with how the agent attempts to solve the map:

| Variable Name | Type Of Value | Description
|-------------|----------|------------------------------------------------------------------------------------------|
| dimensions | int |  <ul><li>The dimensions for the map </li> <li>**Note:** you must input a value for this within the range 3 <= dimensions <= 256</li></ul> |
| density | float | <ul><li>The mine density for the map</li> <li>**Note:** this input is not required an will default to 0.1, however, if input is provided, it must be within the range 0.01 <= density < 1 otherwise it will default to 0.1</li></ul> |
| density_offset | float | How much to increase the mine density after completion of a trial |
| trials | int | How many trials the agent should conduct |
| subtrials | int | How many sub-trials the agent should conduct at a particular mine density|
| minimize | int | When the agent still has cells to discover, but the stack is empty during the traversal these are policies determine how the agent selects the next coordinate to add to the stack: <ul><li>Minesweeper.NONE solves using python random selections for picking some arbitrary unknown coordinate</li> <li>Minesweeper.COST solves by selecting a coordinate with the lowest likelihood of being a mine</li> <li>Minesweeper.RISK solves by using the following formula: <ul><li>Assume *q* is the likelihood some arbitrary coordinate is a mine, *R* is the number of squares that can be deduced if it is a mine, and *S* is the number of squares that can be deduced if it is a clue</li> <li>Then, **qR + (1 - q)S** is the risk assessment for some arbitrary coordinate</li></ul> <li> The coordinate with lowest risk is selected </li></ul>|
| copyCacheState | boolean | <ul><li>Saves agent moves at each step </li> <li>**Note:** this only shows the agent's move for the last trial conducted</li></ul>|
| mode | int | <ul><li>MineSweeper.PRODUCTION for solely seeing the agent's accuracy for solving a map</li> <li>MineSweeper.PRODUCTION_MAPS to see how the agent's map updates as it solves</li> <li>MineSweeper.DEBUG to receive a detailed console log of program execution</li></ul>|
