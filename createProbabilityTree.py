from collections import Counter
from random import randint
from constraintList import ListOfConstraints
from definitionsForAgent import VALUE, MINIMIZE
from tree import Tree


# Get Random Coordinate From List of Coordinates
def random_coordinate(coordinates):
    if len(coordinates) > 0:
        index = randint(0, len(coordinates) - 1)
        return coordinates[index]
    else:
        return None


def create2DConstraintList(constraints_list):
    constraint_list_2D = []
    for constraint_list in constraints_list:
        constraint_list_i = ListOfConstraints()
        constraint_list_i.set(constraint_list)
        constraint_list_2D.append(constraint_list_i)
    return constraint_list_2D


def combineTreePredictions(valuesFromClueTree, valuesFromMineTree):
    merged = dict(Counter(valuesFromClueTree) + Counter(valuesFromMineTree))
    return merged


class CreateProbability:
    def __init__(self, minimize, original_constraints):
        self.minimize = minimize
        self.original_constraints = original_constraints

        self.cellsAsClueObservations, self.cellsAsMineObservations, self.total = {}, {}, {}
        self.cellsDeducedIfClue, self.cellsDeducedIfMine = {}, {}

        self.predictions = []

    def minimizeCost(self):
        candidates = []
        min_cost = float('inf')
        if len(self.predictions) > 0:
            min_cost = self.predictions[0][1]
            for predictionForCoordinate in self.predictions:
                (coordinate, likelihood) = predictionForCoordinate
                if likelihood == min_cost:
                    candidates.append(coordinate)

        if len(candidates) == 0:
            return None, None
        elif len(candidates) == 1:
            return candidates[0], min_cost
        else:
            random_index = randint(0, len(candidates) - 1)
            return candidates[random_index], min_cost

    def minimizeRisk(self):
        riskOfCoordinates, risk_values = [], []
        for prediction in self.predictions:
            coordinate, q = prediction
            if coordinate in self.cellsDeducedIfClue and coordinate in self.cellsDeducedIfMine:
                risk = (q * self.cellsDeducedIfClue[coordinate]) + ((1 - q) * self.cellsDeducedIfMine[coordinate])
            elif coordinate in self.cellsDeducedIfClue:
                risk = (q * self.cellsDeducedIfClue[coordinate])
            elif coordinate in self.cellsDeducedIfMine:
                risk = ((1 - q) * self.cellsDeducedIfMine[coordinate])
            else:
                continue

            riskOfCoordinates.append((coordinate, risk))
            risk_values.append(risk)

        candidates = []
        min_risk = float('inf')
        if len(risk_values) > 0:
            min_risk = min(risk_values)
            for riskOfCoordinate in riskOfCoordinates:
                (coordinate, risk) = riskOfCoordinate
                if risk == min_risk:
                    candidates.append(coordinate)

        if len(candidates) == 0:
            return None, None
        elif len(candidates) == 1:
            return candidates[0], min_risk
        else:
            random_index = randint(0, len(candidates) - 1)
            return candidates[random_index], min_risk

    def createMineProbability(self):
        for coordinate, observed in self.total.items():
            predictionForMine = 0.0
            if coordinate in self.cellsAsMineObservations:
                predictionForMine = self.cellsAsMineObservations[coordinate]
            cell_mine_probability = [coordinate, 0.0]
            if observed > 0:
                cell_mine_probability[1] = predictionForMine / observed
            self.predictions.append(tuple(cell_mine_probability))
        self.predictions.sort(key=lambda x: x[1])

    def getPredictions(self):
        predictions = []
        for prediction_i in self.predictions:
            (coordinate_j, prediction_j) = prediction_i
            coordinate = (int(coordinate_j[0]), int(coordinate_j[1]))
            prediction = float(prediction_j)
            predictions.append((coordinate, prediction))
        return predictions

    def calculate(self, clue_tree, mine_tree):

        clues_ClueTree, clues_MineTree = clue_tree.cellAsClue, mine_tree.cellAsClue
        mines_ClueTree, mines_MineTree = clue_tree.cellAsMine, mine_tree.cellAsMine

        cluesDeduced_ClueTree, cluesDeduced_MineTree = clue_tree.cellsDeducedIfClue, mine_tree.cellsDeducedIfClue
        minesDeduced_ClueTree, minesDeduced_MineTree = clue_tree.cellsDeducedIfMine, mine_tree.cellsDeducedIfMine

        # print("------------- Sub Combining Start -------------")

        tempCellsAsClueObservations = combineTreePredictions(self.cellsAsClueObservations, clues_ClueTree)
        self.cellsAsClueObservations = combineTreePredictions(tempCellsAsClueObservations, clues_MineTree)

        tempCellsAsMineObservations = combineTreePredictions(self.cellsAsMineObservations, mines_ClueTree)
        self.cellsAsMineObservations = combineTreePredictions(tempCellsAsMineObservations, mines_MineTree)

        tempCellsDeducedIfClue = combineTreePredictions(self.cellsDeducedIfClue, cluesDeduced_ClueTree)
        self.cellsDeducedIfClue = combineTreePredictions(tempCellsDeducedIfClue, cluesDeduced_MineTree)

        tempCellsDeducedIfMine = combineTreePredictions(self.cellsDeducedIfMine, minesDeduced_ClueTree)
        self.cellsDeducedIfMine = combineTreePredictions(tempCellsDeducedIfMine, minesDeduced_MineTree)

        tempTotal = combineTreePredictions(self.total, self.cellsAsClueObservations)
        self.total = combineTreePredictions(tempTotal, self.cellsAsMineObservations)

        # print("Clue Observations: ", self.cellsAsClueObservations)
        # print("Mine Observations: ", self.cellsAsMineObservations)
        # print("Total: ", self.total)

    def predict(self):
        if self.original_constraints.length() < 1:
            return

        independent_sets = self.independent_sets()
        independentConstraintListSets = create2DConstraintList(independent_sets)

        # print("--------------- Combining Start ---------------")

        for constraints in independentConstraintListSets:

            coordinates = constraints.coordinates()
            root_coordinate = random_coordinate(coordinates)

            # print("TEST CELL: ", root_coordinate)
            if not root_coordinate:
                continue

            clue_tree = Tree(root_coordinate, constraints.get(), VALUE.CLUE, self.minimize)
            clue_tree.COMPUTE()

            mine_tree = Tree(root_coordinate, constraints.get(), VALUE.MINE, self.minimize)
            mine_tree.COMPUTE()

            self.calculate(clue_tree=clue_tree, mine_tree=mine_tree)

        self.createMineProbability()

        # if len(self.predictions) > 0:
        #     print("Predictions: ", self.predictions)

        #print("---------------- Combining End ----------------")

    def get(self):
        coordinate, probability = self.minimizeRisk() if self.minimize == MINIMIZE.RISK else self.minimizeCost()

        # if coordinate:
        #     if self.minimize == MINIMIZE.RISK:
        #         print("Pick: ", coordinate, " Risk: ", probability)
        #
        #     else:
        #         print("Pick: ", coordinate, " Cost: ", probability)
        # else:
        #     print("Pick: Force Restart")

        return coordinate

    # Get Independent Sets of Constraint Equations
    def independent_sets(self):
        constraint_list_coordinates_set = set()
        constraint_list = self.original_constraints.get()
        for equation in constraint_list:
            for coordinate in equation.constraint:
                if coordinate not in constraint_list_coordinates_set:
                    constraint_list_coordinates_set.add(coordinate)

        constraint_list_coordinates = list(constraint_list_coordinates_set)
        union_set_index = {coordinate: None for coordinate in constraint_list_coordinates}

        disjointConstraints = []
        for coordinate in constraint_list_coordinates:
            if union_set_index[coordinate] is not None:
                continue

            index = 0
            while len(constraint_list) > 0 and index < len(constraint_list):
                if coordinate in constraint_list[index].constraint:
                    insert_set_index = -1
                    for joint_coordinate in constraint_list[index].constraint:
                        if union_set_index[joint_coordinate] is not None:
                            insert_set_index = union_set_index[joint_coordinate]
                            break
                    if insert_set_index == -1:
                        insert_set_index = len(disjointConstraints)

                    for joint_coordinate in constraint_list[index].constraint:
                        union_set_index[joint_coordinate] = insert_set_index

                    if insert_set_index == len(disjointConstraints):
                        disjointConstraints.append([])
                        disjointConstraints[insert_set_index].append(constraint_list[index])
                    else:
                        disjointConstraints[insert_set_index].append(constraint_list[index])

                    constraint_list.remove(constraint_list[index])
                else:
                    index += 1
        # count = 0
        # print(union_set_index)
        # for union in disjointConstraints:
        #     print("Set #%d: " % (count), end='')
        #     for equation in union:
        #         print(equation.constraint, " ", equation.value, " | ", end='')
        #     print()
        #     count += 1
        return disjointConstraints