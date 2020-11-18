from generateMineSweeperMap import GenerateMineSweeperMap
from constraintList import ListOfConstraints
from definitionsForAgent import MineSweeper
from random import randint
from createProbabilityTree import CreateProbabilityTree


class Agent(GenerateMineSweeperMap):
    def __init__(self, dimensions, mines, startingCoordinate, isMapPassed, minimizeCostOrRisk):
        super().__init__(dimensions, mines, startingCoordinate, isMapPassed)

        self.createMineSweeperMap() # Initialize Map To Solve
        self.print_hidden_map() # Print Map Hidden From Agent

        self.minimizeCostOrRisk = minimizeCostOrRisk

        self.startingCoordinate = startingCoordinate

        self.agentCurrentLocation = self.startingCoordinate
        self.agentStateCache, self.agentCorrectlyIdentified, self.agentIncorrectlyIdentified = [], [], []

        self.isVisited = {}

        self.flagged, self.known = [], []

        # self.output_agent_map()

        self.listOfConstraints = None
        self.initializeAgentParams()
        self.solve()

    def initializeAgentParams(self):
        for x_o in range(self.dimensions):
            for y_o in range(self.dimensions):
                coordinate = (x_o, y_o)
                self.isVisited[coordinate] = False
        self.listOfConstraints = ListOfConstraints()

    def updateLocalMap(self, coordinate):
        (x, y) = coordinate

        if self.agent_map[x][y] == MineSweeper.FLAG:
            self.setAgentsCurrentState(agentCorrectlyIdentified=coordinate)
            return MineSweeper.FLAG
        else:
            value, didAgentDie = self.updateAgentMap(coordinate)
            if didAgentDie:

                self.setAgentsCurrentState(agentIncorrectlyIdentified=coordinate)
            else:
                self.setAgentsCurrentState(agentCorrectlyIdentified=coordinate)

            return value

    # Perform Basic Minesweeper Logic to Reduce Constraint Equations List
    def basicMineSweeperLogicReductions(self, coordinate):

        (x, y) = coordinate

        cells_to_uncover = []
        neighbors = self.adjacent_cells_agent_map(coordinate)

        # If coordinate is not a Clue Cell, Return Nothing to Uncover
        if self.agent_map[x][y] == MineSweeper.UNKNOWN_CELL or self.agent_map[x][y] == MineSweeper.FLAG:
            return cells_to_uncover, neighbors

        if self.agent_map[x][y] == 0:  # If Clue Coordinate is equal to zero, uncover all neighbors
            cells_to_uncover = neighbors
        else:
            knowns = list(filter(self.isKnown, neighbors))
            flags, unknowns = list(filter(self.isFlagged, neighbors)), list(filter(self.isUnknown, neighbors))
            numOfFlags, numOfAdjUnknowns, numOfAdjKnowns = len(flags), len(unknowns), len(knowns)

            # If Coordinate's Clue Value - # of Adj. Flags = # Of Adj. Unknowns, then all Unknowns are Mines
            if self.agent_map[x][y] - numOfFlags == numOfAdjUnknowns:
                self.updateAgentKnowledge(unknowns, isMineUpdate=True)

            # If Max # Adj. Neighbors (8) - Coordinate's Clue Value - # Adj. Known Cells = # Adj. Unknowns,
            # then all Unknowns are Clues
            elif (MineSweeper.MAX_NEIGHBORS - self.agent_map[x][y]) - numOfAdjKnowns == numOfAdjUnknowns:
                cells_to_uncover.extend(unknowns)

        return cells_to_uncover, neighbors

    def updateAgentKnowledge(self, uncover, isMineUpdate=False):
        extend_stack = []
        clues, mines = [], []
        for coordinate in uncover:

            if not isMineUpdate:
                isClueOrMine = self.updateLocalMap(coordinate)
            else:
                isClueOrMine = MineSweeper.FLAG

            (x, y) = coordinate
            if isClueOrMine == MineSweeper.FLAG:
                self.agent_map[x][y] = MineSweeper.FLAG
                mines.append(coordinate)
                if coordinate not in self.flagged:
                    self.flagged.append(coordinate)
                    self.isVisited[coordinate] = True
            else:
                self.agent_map[x][y] = isClueOrMine
                clues.append(coordinate)
                self.createConstraintEquationForCoordinate(coordinate)
                if not self.isVisited[coordinate]:
                    self.known.append(coordinate)
                    extend_stack.append(coordinate)
        if len(clues) > 0:
            self.updateConstraintEquations(clues, MineSweeper.CLUE)
        if len(mines) > 0:
            self.updateConstraintEquations(mines, MineSweeper.MINE)
        return extend_stack

    ############################################################
    #                                                          #
    #          Agent Constraint Function Helpers               #
    #                                                          #
    ############################################################

    def updateConstraintEquations(self, coordinates, typeOfUpdate):
        for coordinate in coordinates:
            self.listOfConstraints.updateConstraintEquations(coordinate, typeOfUpdate)

    def createConstraintEquationForCoordinate(self, coordinate):
        neighbors = self.adjacent_cells_agent_map(coordinate)
        unknowns, flagged = list(filter(self.isUnknown, neighbors)), list(filter(self.isFlagged, neighbors))
        if len(unknowns) == 0:
            return
        (x, y) = coordinate
        coordinatesClueValue = self.agent_map[x][y]
        # Determine # of Neighboring Mines
        numOfNeighboringMines = coordinatesClueValue - len(flagged)
        self.listOfConstraints.addConstraintEquation(unknowns, numOfNeighboringMines)

    def simplifyConstraintEquations(self):
        self.listOfConstraints.performConstraintReductions()
        # print("-------------------- CONSTRAINTS SIMPLIFY START --------------------")
        # self.output_constraints()
        # print("--------------------- CONSTRAINTS SIMPLIFY END ---------------------")
        self.deduceClueAndMines()

    def deduceClueAndMines(self):
        clues, mines = self.listOfConstraints.markCluesAndMines()
        self.updateAgentKnowledge(clues)
        self.updateAgentKnowledge(mines, isMineUpdate=True)

    def testPossibleConfigurations(self, unknowns):
        TestConfigs = CreateProbabilityTree(self.minimizeCostOrRisk)
        self.output_agent_map()
        nextCoordinateToVisit = TestConfigs.testPossibleConfigurations(self.listOfConstraints)
        if nextCoordinateToVisit is not None:
            # print("~~~~~Test Prob: ", nextCoordinateToVisit, "~~~~~")
            return nextCoordinateToVisit
        else:
            return None

    ############################################################
    #                                                          #
    #              Agent Primary Solving Function              #
    #                                                          #
    ############################################################
    def solve(self):

        stack = [self.startingCoordinate]
        restartCoordinates = []
        randomSelect = []
        predictionCoordinates = []
        while len(stack) > 0:
            # print("-------------------- CONSTRAINTS BEFORE START --------------------")
            # self.output_constraints()
            # print("--------------------- CONSTRAINTS BEFORE END ---------------------")
            coordinate = stack.pop()
            self.resetAgentsCurrentState()
            self.setAgentsCurrentState(agentLocation=coordinate)

            # print("Mines: ",self.flagged)
            # print("Coordinate: ", coordinate)
            # print("Stack: ", stack)

            (x, y) = coordinate

            if self.agent_map[x][y] != MineSweeper.FLAG and self.agent_map[x][y] != MineSweeper.UNKNOWN_CELL:
                self.createConstraintEquationForCoordinate(coordinate)
                self.simplifyConstraintEquations()

            # print("-------------------- CONSTRAINTS AFTER START --------------------")
            # self.output_constraints()
            # print("--------------------- CONSTRAINTS AFTER END ---------------------")

            if not self.isVisited[coordinate]:
                self.isVisited[coordinate] = True

            else:
                self.deduceClueAndMines()

            uncover, neighbors = self.basicMineSweeperLogicReductions(coordinate)
            unknowns = list(filter(self.isUnknown, neighbors))
            if len(uncover) == 0:

                if len(unknowns) == 1:
                    uncover.append(unknowns[0])
                else:
                    if self.minimizeCostOrRisk == MineSweeper.COST or self.minimizeCostOrRisk == MineSweeper.RISK:
                        minimumProbCoordinate = self.testPossibleConfigurations(unknowns)
                        if minimumProbCoordinate is not None:
                            uncover.append(minimumProbCoordinate)
                            predictionCoordinates.append(uncover[-1])
                        else:
                            uncover.append(self.forceRestart())
                            restartCoordinates.append(uncover[-1])
                    else:
                        knowns = list(filter(self.isKnown, neighbors))
                        numOfAdjUnknowns, numOfAdjKnowns = len(unknowns), len(knowns)
                        if numOfAdjKnowns < 2 and len(uncover) == 0 and numOfAdjUnknowns > 1:
                            uncover.append(self.random_select(unknowns))
                            randomSelect.append(uncover[-1])
            self.output_agent_map()
            if len(uncover) > 0:
                stack.extend(self.updateAgentKnowledge(uncover))

            if len(stack) == 0 and len(self.flagged) < self.numberOfMines:
                if self.minimizeCostOrRisk == MineSweeper.COST or self.minimizeCostOrRisk == MineSweeper.RISK:
                    minimumProbCoordinate = self.testPossibleConfigurations(unknowns)
                    if minimumProbCoordinate is not None:
                        predictionCoordinates.append(minimumProbCoordinate)
                        stack.append(minimumProbCoordinate)
                    else:
                        stack.append(self.forceRestart())
                        restartCoordinates.append(stack[-1])
                else:
                    stack.append(self.forceRestart()) # Force Restart
                    restartCoordinates.append(stack[-1])


        self.output_agent_map()
        print("Restart: ", restartCoordinates)
        print("Random Select: ", randomSelect)
        print("Prediction Coordinates: ", predictionCoordinates)

        incorrect = []
        for mine in self.flagged:
            if mine in predictionCoordinates:
                incorrect.append(mine)
        print("Prediction Mines: ", incorrect)
    def forceRestart(self):
        unobservedCoordinates = []
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                if not self.isVisited[(x, y)]:
                    unobservedCoordinates.append((x, y))

        while len(unobservedCoordinates) > 1:

            index = randint(0, len(unobservedCoordinates) - 1)
            visitCoordinate = unobservedCoordinates[index]
            (x, y) = visitCoordinate

            isClueOrMine = self.updateLocalMap(visitCoordinate)
            self.agent_map[x][y] = isClueOrMine

            if isClueOrMine == MineSweeper.FLAG:
                self.updateConstraintEquations([visitCoordinate], MineSweeper.MINE)
                if visitCoordinate not in self.flagged:
                    self.flagged.append(visitCoordinate)
            else:
                self.updateConstraintEquations([visitCoordinate], MineSweeper.CLUE)
                if visitCoordinate not in self.known:
                    self.known.append(visitCoordinate)
                return visitCoordinate

        if len(unobservedCoordinates) == 1:
            return unobservedCoordinates[0]
        else:
            return self.startingCoordinate # should never execute

    # Randomly Select From List
    def random_select(self, neighbors):
        if len(neighbors) == 0:
            return []
        elif len(neighbors) == 1:
            return neighbors[0]
        else:
            index = randint(0, len(neighbors) - 1)
            return neighbors[index]

    ############################################################
    #                                                          #
    #           Agent Knowledge Helper Functions               #
    #         (Knowledge Derived From Agent's Map)             #
    #                                                          #
    ############################################################

    def isKnown(self, coordinate):
        (x, y) = coordinate
        return self.agent_map[x][y] != MineSweeper.UNKNOWN_CELL and self.agent_map[x][y] != MineSweeper.FLAG

    def isUnknown(self, coordinate):
        (x, y) = coordinate
        return self.agent_map[x][y] == MineSweeper.UNKNOWN_CELL

    def isFlagged(self, coordinate):
        (x, y) = coordinate
        return self.agent_map[x][y] == MineSweeper.FLAG

    def adjacent_cells_agent_map(self, coordinate):
        (x, y) = coordinate
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                     (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        neighbors = list(filter(self.isCellInMap, neighbors))
        return neighbors

    ############################################################
    #                                                          #
    #         Maintain Agent's Knowledge For Each Step         #
    #                                                          #
    ############################################################

    def setAgentsCurrentState(self, agentLocation=None, agentIncorrectlyIdentified=None, agentCorrectlyIdentified=None):

        if agentLocation:
            self.agentCurrentLocation = agentLocation

        if agentIncorrectlyIdentified:
            self.agentIncorrectlyIdentified.append(agentIncorrectlyIdentified)

        if agentCorrectlyIdentified:
            self.agentCorrectlyIdentified.append(agentCorrectlyIdentified)

    def resetAgentsCurrentState(self):
        oldAgentState = {

            'agent-location': self.agentCurrentLocation,
            'agentIncorrectlyIdentified': self.agentIncorrectlyIdentified.copy(),
            'agentCorrectlyIdentified': self.agentCorrectlyIdentified.copy(),
            }
        self.agentStateCache.append(oldAgentState)
        self.agentCorrectlyIdentified = []
        self.agentIncorrectlyIdentified = []

    ############################################################
    #                                                          #
    #                Print To STDOUT Functions                 #
    #                                                          #
    ############################################################
    def output_agent_map(self):
        print(" ------------- AGENTS MAP ------------- ")
        print("|---|", end = '')
        for x in range(self.dimensions):
            print( "  %d|" % x, end='')
        print()
        for x in range(self.dimensions):
            print("| %d " % x, end='')
            for y in range(self.dimensions):
                print("| ", self.agent_map[x][y], end='')
            print("|", end='')
            print()
        print(" ------------- END OF MAP ------------- ")

    def output_constraints(self):
        self.listOfConstraints.output_constraints()