from .generateMineSweeperMap import GenerateMineSweeperMap
from .constraintList import ListOfConstraints
from .definitionsForAgent import MineSweeper, VALUE, TYPE, MINIMIZE, SELECTION
from random import randint
from .createProbabilityTree import CreateProbability


# Randomly Select From List
def random_select(neighbors):
    if len(neighbors) == 0:
        return []
    elif len(neighbors) == 1:
        return neighbors[0]
    else:
        index = randint(0, len(neighbors) - 1)
        return neighbors[index]


def copy_tuple(tuple_to_copy):
    tuple_copy = (int(tuple_to_copy[0]), int(tuple_to_copy[1]))
    return tuple_copy


def copy_list(list_to_copy):
    list_copy = []
    for coordinate_i in list_to_copy:
        if type(coordinate_i[0]) is tuple:
            coordinate_j, probability = copy_tuple(coordinate_i[0]), float(coordinate_i[1])
            list_copy.append((coordinate_j, probability))
        else:
            list_copy.append(copy_tuple(coordinate_i))
    return list_copy


class Agent(GenerateMineSweeperMap):
    def __init__(self, dimensions, mines, startingCoordinate, isMapPassed, minimizeCostOrRisk, MODE, copyCacheState):
        super().__init__(dimensions, mines, startingCoordinate, isMapPassed)

        self.create_map()  # Initialize Map To Solve

        self.copyCacheState = copyCacheState
        self.minimize = minimizeCostOrRisk
        self.MODE = MODE

        if self.MODE == MineSweeper.DEBUG:
            self.print_hidden_map()  # Print the Map Hidden From Agent

        self.startingCoordinate = startingCoordinate

        self.agentCurrentLocation = None
        self.agentStateCache, self.agentCorrectlyIdentified, self.agentIncorrectlyIdentified = [], [], []

        self.agentSelectionType, self.agentPredictions = None, []

        self.isVisited = {}
        self.flagged, self.known = [], [self.startingCoordinate]

        self.listOfConstraints = None
        self.initializeAgentParams()
        self.solve()

    def initializeAgentParams(self):
        self.listOfConstraints = ListOfConstraints()
        for x_o in range(self.dimensions):
            for y_o in range(self.dimensions):
                coordinate = (x_o, y_o)
                self.isVisited[coordinate] = False

    def updateLocalMap(self, coordinate, typeOfSelection=SELECTION.RESTART):
        (x, y) = coordinate
        if self.copyCacheState:
            self.setAgentsCurrentState(typeOfSelection=typeOfSelection)
        if self.agent_map[x][y] == TYPE.FLAG:
            if self.copyCacheState:
                self.setAgentsCurrentState(correct=coordinate)
            return TYPE.FLAG
        else:
            value, didAgentDie = self.get_value(coordinate)
            if self.copyCacheState:
                if didAgentDie:
                    self.setAgentsCurrentState(incorrect=coordinate)
                else:
                    self.setAgentsCurrentState(correct=coordinate)
            return value

    # Perform Basic src Logic to Reduce Constraint Equations List
    def basicMineSweeperLogicReductions(self, coordinate):

        (x, y) = coordinate
        cells_to_uncover = []
        neighbors = self.adjacent_cells_agent_map(coordinate)
        # If coordinate is not a Clue Cell, Return Nothing to Uncover
        if self.agent_map[x][y] == TYPE.UNKNOWN or self.agent_map[x][y] == TYPE.FLAG:
            return cells_to_uncover, neighbors
        # If Clue Coordinate is equal to zero, uncover all neighbors
        if self.agent_map[x][y] == 0:
            cells_to_uncover = neighbors
        else:
            knowns = list(filter(self.isKnown, neighbors))
            flags, unknowns = list(filter(self.isFlagged, neighbors)), list(filter(self.isUnknown, neighbors))
            numOfFlags, numOfAdjUnknowns, numOfAdjKnowns = len(flags), len(unknowns), len(knowns)

            # If Coordinate's Value - # of Adj. Flags = # Of Adj. Unknowns, then all Unknowns are Mines
            if self.agent_map[x][y] - numOfFlags == numOfAdjUnknowns:
                self.updateAgentKnowledge(unknowns, isMineUpdate=True, typeOfSelection=SELECTION.CONSTRAINT_REDUCTION)

            # If Max Neighbors - Coordinate's Value - # Adj. Known Cells = # Adj. Unknowns, then all Unknowns are Clues
            elif (len(neighbors) - self.agent_map[x][y]) - numOfAdjKnowns == numOfAdjUnknowns:
                cells_to_uncover.extend(unknowns)

        return cells_to_uncover, neighbors

    def updateAgentKnowledge(self, uncover, isMineUpdate=False, typeOfSelection=SELECTION.CONSTRAINT_REDUCTION):
        updated_stack_elements = []
        clues, mines = [], []
        for coordinate in uncover:
            (x, y) = coordinate
            value = self.updateLocalMap(coordinate, typeOfSelection=typeOfSelection) if not isMineUpdate else TYPE.FLAG
            if value == TYPE.FLAG:
                self.agent_map[x][y] = TYPE.FLAG
                mines.append(coordinate)
                if coordinate not in self.flagged:
                    self.flagged.append(coordinate)
                    self.isVisited[coordinate] = True
            else:
                self.agent_map[x][y] = value
                clues.append(coordinate)
                self.createConstraintEquationForCoordinate(coordinate)
                if not self.isVisited[coordinate]:
                    if coordinate not in self.known:
                        self.known.append(coordinate)
                    updated_stack_elements.append(coordinate)

        if len(clues) > 0:
            self.updateConstraintEquations(clues, VALUE.CLUE)
        if len(mines) > 0:
            self.updateConstraintEquations(mines, VALUE.MINE)

        return updated_stack_elements

    ############################################################
    #                                                          #
    #          Agent Constraint Function Helpers               #
    #                                                          #
    ############################################################

    def updateConstraintEquations(self, coordinates, typeOfUpdate):
        for coordinate in coordinates:
            self.listOfConstraints.update(coordinate, typeOfUpdate)

    def createConstraintEquationForCoordinate(self, coordinate):
        neighbors = self.adjacent_cells_agent_map(coordinate)
        unknowns, flagged = list(filter(self.isUnknown, neighbors)), list(filter(self.isFlagged, neighbors))
        if len(unknowns) > 0:
            (x, y) = coordinate
            numberOfNeighboringMines = self.agent_map[x][y] - len(flagged)
            self.listOfConstraints.add(unknowns, numberOfNeighboringMines)

    def simplifyConstraintEquations(self):
        self.listOfConstraints.reduce()

    def deduceCluesAndMines(self):
        while True:
            clues, mines = self.listOfConstraints.deduce()
            self.updateAgentKnowledge(clues)
            self.updateAgentKnowledge(mines, isMineUpdate=True)
            if self.MODE == MineSweeper.PRODUCTION_MAPS or self.MODE == MineSweeper.DEBUG:
                self.output_agent_map()
            if len(clues) > 0 or len(mines) > 0:
                self.simplifyConstraintEquations()
            else:
                break

    def pickNextCoordinate(self):
        if self.minimize == MINIMIZE.COST or self.minimize == MINIMIZE.RISK:
            configurations = CreateProbability(self.minimize, self.listOfConstraints, self.MODE)
            configurations.predict()
            nextCoordinateToVisit = configurations.get()
            if nextCoordinateToVisit:
                if self.copyCacheState:
                    self.setAgentsCurrentState(predictions=configurations.getPredictions())
                self.updateAgentKnowledge([nextCoordinateToVisit], typeOfSelection=SELECTION.PREDICTION)
                return nextCoordinateToVisit, SELECTION.PREDICTION

        return self.force_restart(), SELECTION.RESTART

    ############################################################
    #                                                          #
    #              Agent Primary Solving Function              #
    #                                                          #
    ############################################################
    def solve(self):

        stack = [self.startingCoordinate]
        restartCoordinates, randomSelect, predictionCoordinates = [], [], []
        observed, numberOfCoordinates = len(self.known) + len(self.flagged), int((self.dimensions ** 2))

        while len(stack) > 0 and observed < numberOfCoordinates:
            if self.MODE == MineSweeper.DEBUG:
                print(len(self.known), " + ", len(self.flagged) , " = ", numberOfCoordinates)

            coordinate = stack.pop()
            if self.copyCacheState:
                self.resetAgentsCurrentState()
                self.setAgentsCurrentState(location=coordinate)

            if self.MODE == MineSweeper.PRODUCTION_MAPS or self.MODE == MineSweeper.DEBUG:
                self.output_agent_map()

            if self.MODE == MineSweeper.DEBUG:
                print("Mines: ", self.flagged)
                print("Coordinate: ", coordinate)
                print("Stack: ", stack)

            (x, y) = coordinate
            if self.agent_map[x][y] != TYPE.FLAG and self.agent_map[x][y] != TYPE.UNKNOWN:
                self.createConstraintEquationForCoordinate(coordinate)
                self.simplifyConstraintEquations()
                self.deduceCluesAndMines()

            if not self.isVisited[coordinate]:
                self.isVisited[coordinate] = True
            else:
                self.simplifyConstraintEquations()
                self.deduceCluesAndMines()

            uncover, neighbors = self.basicMineSweeperLogicReductions(coordinate)
            unknowns = list(filter(self.isUnknown, neighbors))
            typeOfSelection = None
            if len(uncover) == 0:
                if not self.minimize == MINIMIZE.NONE:
                    nextCoordinateToVisit, typeOfRetrieval = self.pickNextCoordinate()
                    uncover.append(nextCoordinateToVisit)

                    if typeOfRetrieval == SELECTION.PREDICTION:
                        predictionCoordinates.append(nextCoordinateToVisit)

                    else:
                        restartCoordinates.append(nextCoordinateToVisit)

                else:
                    if len(unknowns) == 1:
                        uncover.append(unknowns[0])
                        typeOfSelection = SELECTION.RANDOM_SELECT
                    else:
                        knowns = list(filter(self.isKnown, neighbors))
                        numOfAdjUnknowns, numOfAdjKnowns = len(unknowns), len(knowns)
                        if numOfAdjKnowns < 2 and len(uncover) == 0 and numOfAdjUnknowns > 1:
                            uncover.append(random_select(unknowns))
                            randomSelect.append(uncover[-1])
                            typeOfSelection = SELECTION.RANDOM_SELECT
            else:
                typeOfSelection = SELECTION.CONSTRAINT_REDUCTION

            if len(uncover) > 0:
                if not typeOfSelection:  # Agent will have already updated knowledge in method pickNextCoordinate()
                    stack.extend(uncover)
                else:
                    stack.extend(self.updateAgentKnowledge(uncover, typeOfSelection=typeOfSelection))

            if len(stack) == 0:
                nextCoordinateToVisit, typeOfRetrieval = self.pickNextCoordinate()

                if typeOfRetrieval == SELECTION.PREDICTION:
                    predictionCoordinates.append(nextCoordinateToVisit)

                else:
                    restartCoordinates.append(nextCoordinateToVisit)

            observed = len(self.known) + len(self.flagged)

        if self.MODE == MineSweeper.DEBUG:
            self.output_agent_map()
            print("Restart: ", restartCoordinates)
            print("Random Select: ", randomSelect)
            print("Prediction Coordinates: ", predictionCoordinates)

            incorrect = []
            for mine in self.flagged:
                if mine in predictionCoordinates:
                    incorrect.append(mine)
            print("Prediction Mines: ", incorrect)

    def force_restart(self):
        unobservedCoordinates = []
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                if self.agent_map[x][y] == TYPE.UNKNOWN:
                    unobservedCoordinates.append((x, y))

        while len(unobservedCoordinates) > 0:
            if len(unobservedCoordinates) > 1:
                index = randint(0, len(unobservedCoordinates) - 1)
            else:
                index = 0
            visitCoordinate = unobservedCoordinates[index]
            isValid = self.updateAgentKnowledge([visitCoordinate], typeOfSelection=SELECTION.RESTART)
            if len(isValid) > 0:
                return isValid[0]
            else:
                unobservedCoordinates.remove(visitCoordinate)

        return self.startingCoordinate  # should never execute

    ############################################################
    #                                                          #
    #           Agent Knowledge Helper Functions               #
    #         (Knowledge Derived From Agent's Map)             #
    #                                                          #
    ############################################################

    def isKnown(self, coordinate):
        (x, y) = coordinate
        return self.agent_map[x][y] != TYPE.UNKNOWN and self.agent_map[x][y] != TYPE.FLAG

    def isUnknown(self, coordinate):
        (x, y) = coordinate
        return self.agent_map[x][y] == TYPE.UNKNOWN

    def isFlagged(self, coordinate):
        (x, y) = coordinate
        return self.agent_map[x][y] == TYPE.FLAG

    def adjacent_cells_agent_map(self, coordinate):
        (x, y) = coordinate
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                     (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        neighbors = list(filter(self.inbounds, neighbors))
        return neighbors

    ############################################################
    #                                                          #
    #         Maintain Agent's Knowledge For Each Step         #
    #                                                          #
    ############################################################

    def setAgentsCurrentState(self, location=None, incorrect=None, correct=None,
                              typeOfSelection=None, predictions=None):

        if location:
            self.agentCurrentLocation = location

        if incorrect:
            self.agentIncorrectlyIdentified.append(copy_tuple(incorrect))

        if correct:
            self.agentCorrectlyIdentified.append(copy_tuple(correct))

        if typeOfSelection:
            self.agentSelectionType = typeOfSelection

        if predictions:
            self.agentPredictions = predictions


    def resetAgentsCurrentState(self):
        if not self.agentCurrentLocation:
            return
        location = copy_tuple(self.agentCurrentLocation)

        oldAgentState = {

            'location': location,
            'incorrectlyIdentified': copy_list(self.agentIncorrectlyIdentified),
            'correctlyIdentified': copy_list(self.agentCorrectlyIdentified),
            'selectionType': int(self.agentSelectionType),
            'predictions': copy_list(self.agentPredictions),
            'known': copy_list(self.known),
            'flagged': copy_list(self.flagged)

        }
        self.agentStateCache.append(oldAgentState)
        self.agentCorrectlyIdentified, self.agentIncorrectlyIdentified = [], []
        self.agentSelectionType = None
        self.agentPredictions = []

    ############################################################
    #                                                          #
    #                Print To STDOUT Functions                 #
    #                                                          #
    ############################################################
    def output_agent_map(self):
        print(" ------------- AGENTS MAP ------------- ")
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                print("| ", self.agent_map[x][y], end='')
            print("|", end='')
            print()
        print(" ------------- END OF MAP ------------- ")

    def output_constraints(self):
        self.listOfConstraints.output()
