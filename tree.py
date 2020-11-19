from definitionsForAgent import MineSweeper, VALUE, MINIMIZE
from constraintList import ListOfConstraints


class Leaf:
    def __init__(self, coordinate, constraints, value):

        self.coordinate, self.type = coordinate, value
        self.listOfConstraints = ListOfConstraints()

        self.clue, self.mine = None, None  # Left child, Right child

        self.clues, self.mines = [], []  # clues and mines resolved at this step
        self.isValid = True

        self.initializeConstraints(constraints)

    def initializeConstraints(self, listOfConstraintsToSet):

        if type(listOfConstraintsToSet) is list:
            self.listOfConstraints.set(listOfConstraintsToSet)
        else:
            self.listOfConstraints.set(listOfConstraintsToSet.constraints)

        self.listOfConstraints.add([self.coordinate], self.type)

        while True:
            self.listOfConstraints.reduce()
            temp_clues, temp_mines = self.listOfConstraints.deduce()
            if len(temp_clues) > 0 or len(temp_mines) > 0:
                if len(temp_clues) > 0:
                    self.clues.extend(temp_clues)
                if len(temp_mines) > 0:
                    self.mines.extend(temp_mines)
            else:
                break

        if self.type == VALUE.MINE and self.coordinate in self.mines:
            self.mines.remove(self.coordinate)
        elif self.type == VALUE.CLUE and self.coordinate in self.clues:
            self.clues.remove(self.coordinate)


def updateCellDictWithValue(cells, dictionary, coordinate=None, value=1):
    for cell in cells:
        if coordinate and cell == coordinate:
            continue
        dictionary[cell] = (dictionary[cell] + value) if cell in dictionary else value


class Tree:
    def __init__(self, clue, constraints, cellType, minimizeCostOrRisk, MODE):

        self.root = Leaf(clue, constraints, cellType)

        self.minimizeCostOrRisk = minimizeCostOrRisk
        self.MODE = MODE

        self.cellAsClue, self.cellAsMine = {}, {}
        self.cellsDeducedIfClue, self.cellsDeducedIfMine = {}, {}

        self.paths = []
        self.likelihoodOfCellAsMine, self.total = {}, {}

    # Iteratively create Tree branch where that satisfy constraints by test binary constraint values for coordinates
    def create(self):
        stack = [self.root]

        while len(stack) > 0:
            node = stack.pop()
            if node.listOfConstraints.length() < 1:
                continue

            clue_cell, mine_cell = self.getRandomCellType(node.listOfConstraints.get())

            if not node.clue and clue_cell:
                node.clue = Leaf(coordinate=clue_cell, constraints=node.listOfConstraints, value=VALUE.CLUE)

            if not node.mine and mine_cell:
                node.mine = Leaf(coordinate=mine_cell, constraints=node.listOfConstraints, value=VALUE.MINE)

            if node.clue:
                stack.append(node.clue)
            if node.mine:
                stack.append(node.mine)

    def prune(self):
        self.prune_(self.root)

    # Remove Invalid Tree Branches (Invalid branches are when a leaf with no children still has constraints to satisfy)
    def prune_(self, node):
        if not node:
            return None
        else:
            if node.clue:
                node.clue = self.prune_(node.clue)
                if not node.clue.isValid:
                    node.clue = None
            if node.mine:
                node.mine = self.prune_(node.mine)
                if not node.mine.isValid:
                    node.mine = None

            if not node.clue and not node.mine:
                node.isValid = node.listOfConstraints.check()

            if not node.isValid:
                node.cell = (None, None)
                node = None

            return node

    # Compute Coordinate Likelihoods as Clues and Mines Based on Tree Branches
    def predict(self):
        self.traverse([], self.root)
        count = 0
        if self.MODE == MineSweeper.DEBUG:
            print("-------------------- TEST CELL PREDICTION START --------------------")
        for path in self.paths:
            clues_in_path, mines_in_path = set(), set()
            temp_deduced_clues, temp_deduced_mines = {}, {}
            isValidConfiguration = True
            for node in path:
                (coordinate, typeOfCell, clues, mines) = node.coordinate, node.type, node.clues, node.mines
                if not node.isValid:
                    isValidConfiguration = False
                    break

                if coordinate and (typeOfCell == VALUE.CLUE or typeOfCell == VALUE.MINE):
                    if typeOfCell == VALUE.CLUE:
                        if coordinate not in clues_in_path:
                            clues_in_path.add(coordinate)
                        if self.minimizeCostOrRisk == MINIMIZE.RISK:
                            temp_deduced_clues[coordinate] = len(clues) + len(mines)

                    else:
                        if coordinate not in mines_in_path:
                            mines_in_path.add(coordinate)
                        if self.minimizeCostOrRisk == MINIMIZE.RISK:
                            temp_deduced_mines[coordinate] = len(clues) + len(mines)

                    for clue in clues:
                        if clue not in clues_in_path:
                            clues_in_path.add(clue)

                    for mine in mines:
                        if mine not in mines_in_path:
                            mines_in_path.add(mine)

            if isValidConfiguration:

                for coordinate in temp_deduced_clues:
                    updateCellDictWithValue(cells=[coordinate], dictionary=self.cellsDeducedIfClue,
                                                 value=(temp_deduced_clues[coordinate]))
                for coordinate in temp_deduced_mines:
                    updateCellDictWithValue(cells=[coordinate], dictionary=self.cellsDeducedIfMine,
                                            value=(temp_deduced_mines[coordinate]))

                updateCellDictWithValue(cells=list(clues_in_path), dictionary=self.cellAsClue)
                updateCellDictWithValue(cells=list(mines_in_path), dictionary=self.cellAsMine)

                if self.MODE == MineSweeper.DEBUG:
                    print("Entry #%d" % count, " | Clues: ", clues_in_path, " | Mines: ", mines_in_path)
                    count += 1

        if self.MODE == MineSweeper.DEBUG:
            print("Possibilities: ", count, " | ", len(self.paths))
            print("Clue Total: ", self.cellAsClue)
            print("Mine Total: ", self.cellAsMine)
            print("--------------------  TEST CELL PREDICTION END  --------------------")

    # Find all root-to-leaf paths. Each path is a potential configuration in the Minesweeper Map.
    def traverse(self, stack, node):
        if node is None:
            return
        stack.append(node)
        if not node.clue and not node.mine:
            self.paths.append(stack[:])
        else:
            self.traverse(stack, node.clue)
            self.traverse(stack, node.mine)
        stack.pop()

    def COMPUTE(self):
        self.create()
        self.prune()
        self.predict()

    def test(self, coordinate, constraint_list):

        clue_list = ListOfConstraints()
        clue_list.set(constraint_list)
        clue_list.update(coordinate, VALUE.CLUE)
        clue_list.reduce()

        mine_list = ListOfConstraints()
        mine_list.set(constraint_list)
        mine_list.update(coordinate, VALUE.MINE)
        mine_list.reduce()

        return clue_list.check(False), mine_list.check(False)

    # Get a Random Coordinate and Cell Type it (Mine or Clue) satisfies from the Constraint List of Equations
    def getRandomCellType(self, constraint_list):
        for eq_i in constraint_list:
            if len(eq_i.constraint) < 1:
                continue
            for coordinate in eq_i.constraint:

                potentialClueCell, potentialMineCell = self.test(coordinate=coordinate, constraint_list=constraint_list)

                if potentialClueCell and potentialMineCell:
                    return coordinate, coordinate

                elif potentialClueCell:
                    return coordinate, None

                elif potentialMineCell:
                    return None, coordinate

        return None, None
