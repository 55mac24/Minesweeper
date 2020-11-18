from collections import Counter
from random import randint
from constraintList import ListOfConstraints
from definitionsForAgent import MineSweeper
from tree import Tree

class CreateProbabilityTree:
    def __init__(self, minimize):
        self.minimize = minimize

    def minimizeCost(self, predictionsOfCellsAsMine):
        candidates = []
        min_cost = float('inf')
        if len(predictionsOfCellsAsMine) > 0:
            predictionsOfCellsAsMine.sort(key=lambda x: x[1])
            min_cost = predictionsOfCellsAsMine[0][1]
            for predictionForCoordinate in predictionsOfCellsAsMine:
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

    def minimizeRisk(self, cellsThatCanBeDeducedIfClue, cellsThatCanBeDeducedIfMine, predictionsOfCellAsMine):

        riskOfCoordinates, risk_values = [], []
        for prediction in predictionsOfCellAsMine:
            cell, q = prediction
            if cell in cellsThatCanBeDeducedIfClue and cell in cellsThatCanBeDeducedIfMine:
                risk = (q * cellsThatCanBeDeducedIfClue[cell]) + ((1 - q) * cellsThatCanBeDeducedIfMine[cell])
            elif cell in cellsThatCanBeDeducedIfClue:
                risk = (q * cellsThatCanBeDeducedIfClue[cell])
            elif cell in cellsThatCanBeDeducedIfMine:
                risk = ((1 - q) * cellsThatCanBeDeducedIfMine[cell])
            else:
                continue
            riskOfCoordinates.append((cell, risk))
            risk_values.append(risk)

        min_risk = min(risk_values)
        candidates = []
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

    def combineCellValues(self, valuesFromClueTree, valuesFromMineTree):
        # print("From Clue Tree: ", valuesFromClueTree)
        # print("From Mine Tree: ", valuesFromMineTree)
        merged = dict(Counter(valuesFromClueTree) + Counter(valuesFromMineTree))
        return merged

    def createMineProbability(self, cellsDeducedFromMineTree, total):

        probability = []
        for cell, observed in total.items():
            predictionForMine = 0
            if cell in cellsDeducedFromMineTree:
                predictionForMine = cellsDeducedFromMineTree[cell]

            cell_mine_probability = [cell, 0.0]
            if observed > 0:
                cell_mine_probability[1] = predictionForMine / observed
            probability.append(tuple(cell_mine_probability))

        probability.sort(key = lambda x: x[1])
        # print("Probabilities: ", probability)

        return probability

    def create2DConstraintList(self, constraints_list):
        constraint_list_2D = []
        for constraint_list in constraints_list:
            constraint_list_i = ListOfConstraints()
            for union_i in constraint_list:
                constraint_list_i.addConstraintEquation(union_i.constraint[:], int(union_i.value))
            constraint_list_2D.append(constraint_list_i)
        return constraint_list_2D

    def testPossibleConfigurations(self, constraints):

        testCell = None
        constraints.output_constraints()
        disjointConstraintsSets = constraints.getDisjointConstraints(constraints.getConstraintList_RAW())

        disjointConstraintsList = self.create2DConstraintList(disjointConstraintsSets)
        cellsAsClueObservations, cellsAsMineObservations, total = {}, {}, {}

        cellsDeducedIfClue, cellsDeducedIfMine = {}, {}

        print("--------------- Combining Start ---------------")
        for unionConstraint in disjointConstraintsList:
            exhaustive_constraints = unionConstraint.getListOfConstraintCoordinates()
            testCell = unionConstraint.getRandomCellForTree(exhaustive_constraints, testCell)
            print("TEST CELL: ", testCell)

            clueTree = Tree(testCell, unionConstraint.getConstraintList_RAW(), MineSweeper.CLUE, self.minimize, None)
            clueTree.createCSPProbabilityTree()
            clueTree.getCellTypePredictions()

            mineTree = Tree(testCell, unionConstraint.getConstraintList_RAW(), MineSweeper.MINE, self.minimize, clueTree.resolved_paths)
            mineTree.createCSPProbabilityTree()
            mineTree.getCellTypePredictions()

            clues_ClueTree, clues_MineTree = clueTree.cellAsClue, mineTree.cellAsClue
            mines_ClueTree, mines_MineTree = clueTree.cellAsMine, mineTree.cellAsMine

            cluesDeduced_ClueTree, cluesDeduced_MineTree = clueTree.cellsDeducedIfClue, mineTree.cellsDeducedIfClue
            minesDeduced_ClueTree, minesDeduced_MineTree = clueTree.cellsDeducedIfMine, mineTree.cellsDeducedIfMine

            print("------------- Sub Combining Start -------------")

            tempCellsAsClueObservations = self.combineCellValues(cellsAsClueObservations, clues_ClueTree)
            cellsAsClueObservations = self.combineCellValues(tempCellsAsClueObservations, clues_MineTree)

            tempCellsAsMineObservations = self.combineCellValues(cellsAsMineObservations, mines_ClueTree)
            cellsAsMineObservations = self.combineCellValues(tempCellsAsMineObservations, mines_MineTree)

            tempCellsDeducedIfClue = self.combineCellValues(cellsDeducedIfClue, cluesDeduced_ClueTree)
            cellsDeducedIfClue = self.combineCellValues(tempCellsDeducedIfClue, cluesDeduced_MineTree)

            tempCellsDeducedIfMine = self.combineCellValues(cellsDeducedIfMine, minesDeduced_ClueTree)
            cellsDeducedIfMine = self.combineCellValues(tempCellsDeducedIfMine, minesDeduced_MineTree)

            tempTotal = self.combineCellValues(total, cellsAsClueObservations)
            total = self.combineCellValues(tempTotal, cellsAsMineObservations)
            print("Clue Observations: ", cellsAsClueObservations)
            print("Mine Observations: ", cellsAsMineObservations)
            print("Total: ", total)

        predictionsOfCellsAsMine = self.createMineProbability(cellsAsMineObservations, total)
        print("Predictions: ", predictionsOfCellsAsMine)
        print("---------------- Combining End ----------------")

        if self.minimize == MineSweeper.RISK:

            (coordinate, risk) = self.minimizeRisk(cellsDeducedIfClue, cellsDeducedIfMine,predictionsOfCellsAsMine)
            print("Pick: ", coordinate, " Risk: ", risk)
            return coordinate

        else:

            (coordinate, cost) = self.minimizeCost(predictionsOfCellsAsMine)
            print("Pick: ", coordinate, " Cost: ", cost)
            return coordinate