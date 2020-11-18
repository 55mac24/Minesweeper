from definitionsForAgent import MineSweeper
from constraintList import ListOfConstraints

class Leaf:
    def __init__(self, cell, constraints, value):
        self.cell, self.type = cell, value

        self.listOfConstraints = ListOfConstraints()

        self.clue, self.mine = None, None  # Left child, Right child

        self.clues, self.mines = None, None  # clues resolved and mines resolved at this step

        self.isValid = True

        self.initializeConstraints(constraints)

    def initializeConstraints(self, listOfConstraintsToSet):

        if type(listOfConstraintsToSet) is list:
            self.listOfConstraints.setConstraintsFromList(listOfConstraintsToSet)
        else:
            self.listOfConstraints.setConstraintsFromList(listOfConstraintsToSet.constraints)

        self.listOfConstraints.addConstraintEquation([self.cell], self.type)
        # print("-------------------- INIT CONSTRAINTS START --------------------")
        #
        # self.constraints.output_constraints()
        self.listOfConstraints.performConstraintReductions()
        self.clues, self.mines = self.listOfConstraints.markCluesAndMines()
        # print("------------------- INIT CONSTRAINT SIMPLIFY -------------------")
        # self.constraints.output_constraints()
        if self.type == MineSweeper.MINE and self.cell in self.mines:
            self.mines.remove(self.cell)
        elif self.type == MineSweeper.CLUE and self.cell in self.clues:
            self.clues.remove(self.cell)
        # print("--------------------- INIT CONSTRAINTS END ---------------------")


class Tree:
    def __init__(self, clue, constraints, cellType, minimizeCostOrRisk, resolved_paths):

        self.root = Leaf(clue, constraints, cellType)

        self.minimizeCostOrRisk = minimizeCostOrRisk

        self.cellAsClue, self.cellAsMine = {}, {}
        self.cellsDeducedIfClue, self.cellsDeducedIfMine = {}, {}

        self.paths, self.resolved_paths = [], None
        self.likelihoodOfCellAsMine, self.total = {}, {}

        self.createResolvedPathsCopy(resolved_paths)

    def createResolvedPathsCopy(self, resolved_paths):
        if not resolved_paths:
            self.resolved_paths = {}
        else:
            for path in resolved_paths:
                clues = resolved_paths[path][MineSweeper.CLUE]
                mines = resolved_paths[path][MineSweeper.MINE]
                self.resolved_paths = {path:{MineSweeper.CLUE: clues, MineSweeper.MINE: mines}}

    def getResolvedPaths(self):
        resolved_paths = {}
        for path in self.resolved_paths:
            clues = self.resolved_paths[path][MineSweeper.CLUE]
            mines = self.resolved_paths[path][MineSweeper.MINE]
            resolved_paths = {path: {MineSweeper.CLUE: clues, MineSweeper.MINE: mines}}
        return resolved_paths

    # Iteratively create Tree branch where that satisfy constraints by test binary constraint values for coordinates
    def createCSPProbabilityTree(self):
        stack = [self.root]

        while len(stack) > 0:
            node = stack.pop()
            if node.listOfConstraints.getConstraintsListLength() < 1:
                continue

            clue_cell, mine_cell = node.listOfConstraints.getRandomCellType(
                node.listOfConstraints.getConstraintList_RAW())  # node.listOfConstraints.getConstraintList(ConstraintList())

            # print("#####CSP START#####")
            # node.listOfConstraints.output_constraints()
            # print("######CSP END######")
            if not node.clue and clue_cell:
                node.clue = Leaf(cell=clue_cell, constraints=node.listOfConstraints, value=MineSweeper.CLUE)

            if not node.mine and mine_cell:
                node.mine = Leaf(cell=mine_cell, constraints=node.listOfConstraints, value=MineSweeper.MINE)

            if node.clue:
                stack.append(node.clue)
            if node.mine:
                stack.append(node.mine)

        return self.getCellTypePredictions()

    # Remove Invalid Tree Branches (Invalid branches are when a leaf with no children still has constraints to satisfy)
    def pruneCSPTree(self, node):
        if not node:
            return None
        else:
            if not node.clue and not node.mine:
                node.isValid = False if not node.listOfConstraints.checkConstraintsList() else True
                return node

            elif node.clue:
                node.clue = self.pruneCSPTree(node.clue)
                if not node.clue.isValid:
                    node.clue = None

            elif node.mine:
                node.mine = self.pruneCSPTree(node.mine)
                if not node.mine.isValid:
                    node.mine = None

            if not node.clue and not node.mine:
                node.isValid = False if not node.listOfConstraints.checkConstraintsList() else True
            return node

    def updateCellDictWithValue(self, cells, dictionary, coordinate=None, value=1):
        for cell in cells:
            if coordinate and cell == coordinate:
                continue
            dictionary[cell] = (dictionary[cell] + value) if cell in dictionary else value

    # Compute Coordinate Likelihoods as Clues and Mines Based on Tree Branches
    def getCellTypePredictions(self):
        # TO-DO: Add bottom up tree pruning method to remove subtree branches where all constraints were not satisfied
        self.pruneCSPTree(self.root)
        self.traverse([], self.root)
        # print("-------------------- TEST CELL PREDICTION START --------------------")

        if not self.resolved_paths:
            self.resolved_paths = {}
        count = len(self.resolved_paths)
        for path in self.paths:
            clues_in_path = set()
            mines_in_path = set()
            for node in path:
                (coordinate, typeOfCell, clues, mines) = node.cell, node.type, node.clues, node.mines

                # print("Cell: ", cell, "Cell Type: ", typeOfCell, "Clues:", clues, "Mines: ", mines, end='')
                # print(' --->', end='')
                if coordinate and (typeOfCell == MineSweeper.CLUE or typeOfCell == MineSweeper.MINE):
                    # print("-------------------- TEST CELL PREDICTION SUB-PATH START --------------------")
                    # print("Cell: ", cell, "Type: ", typeOfCell," | Constraints: ")
                    # node.cell_constraints.output_constraints()
                    # print("--------------------  TEST CELL PREDICTION SUB-PATH END  --------------------")


                    if typeOfCell == MineSweeper.CLUE:
                        if coordinate not in clues_in_path:
                            clues_in_path.add(coordinate)

                        if self.minimizeCostOrRisk == MineSweeper.RISK:
                            self.updateCellDictWithValue(cells=[coordinate], dictionary=self.cellsDeducedIfClue,
                                                         value=(len(clues) + len(mines)))

                    else:
                        if coordinate not in mines_in_path:
                            mines_in_path.add(coordinate)

                        if self.minimizeCostOrRisk == MineSweeper.RISK:
                            self.updateCellDictWithValue(cells=[coordinate], dictionary=self.cellsDeducedIfMine,
                                                         value=(len(clues) + len(mines)))
                    for clue in clues:
                        if clue not in clues_in_path:
                            clues_in_path.add(clue)
                    for mine in mines:
                        if mine not in mines_in_path:
                            mines_in_path.add(mine)

            doesPathExist = False
            for resolved_path in self.resolved_paths:
                check_clues = self.resolved_paths[resolved_path][MineSweeper.CLUE]
                check_mines = self.resolved_paths[resolved_path][MineSweeper.MINE]
                if clues_in_path == check_clues and mines_in_path == check_mines: # check if path was already counted
                    doesPathExist = True
                    break

            if not doesPathExist:
                self.resolved_paths[count] = {MineSweeper.CLUE: clues_in_path, MineSweeper.MINE: mines_in_path}

                print("Entry #%d" % (count) ," | Clues: ", clues_in_path, " | Mines: ", mines_in_path)
                self.updateCellDictWithValue(cells=list(clues_in_path), dictionary=self.cellAsClue)
                self.updateCellDictWithValue(cells=list(mines_in_path), dictionary=self.cellAsMine)
                print()
                count += 1
        print("Possibilities: ", count, " | ", len(self.paths))
        print("Clue Total: ", self.cellAsClue)
        print("Mine Total: ", self.cellAsMine)
        # print("--------------------  TEST CELL PREDICTION END  --------------------")

    # find all root-to-leaf paths. Each path is a potential configuration in the Minesweeper Map.
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
