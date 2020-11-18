from constraint import Constraint
from copy import deepcopy
from definitionsForAgent import MineSweeper
from random import randint


class ListOfConstraints:
    def __init__(self):
        self.constraints = []

    def setConstraintList(self, constraint_list):
        self.constraints = []
        if constraint_list and len(constraint_list.constraints) > 0:
            for equation in constraint_list.constraints:
                constraint, value = [], int(equation.value)
                for tuple_ in equation.constraint:
                    (x_i, y_i) = int(tuple_[0]), int(tuple_[1])
                    constraint.append((x_i, y_i))
                self.constraints.append(Constraint(constraint, value))

    def setConstraintsFromList(self, constraint_list):
        for equation in constraint_list:
            constraint, value = [], int(equation.value)
            for tuple_ in equation.constraint:
                (x_i, y_i) = int(tuple_[0]), int(tuple_[1])
                constraint.append((x_i, y_i))
            self.constraints.append(Constraint(constraint, value))

    def getConstraintListRef(self):
        return self.constraints

    def getDeepCopyConstraintList(self):
        return deepcopy(self.constraints)

    def getConstraintList_RAW(self):
        constraints = []
        for equation in self.constraints:
            constraint, value = [], int(equation.value)
            for tuple_ in equation.constraint:
                (x_i, y_i) = int(tuple_[0]), int(tuple_[1])
                constraint.append((x_i, y_i))
            constraints.append(Constraint(constraint, value))
        return constraints

    def getConstraintList(self, new_constraint_list_obj):
        for equation in self.constraints:
            new_constraint_list_obj.constraints.append(Constraint(deepcopy(equation.constraint[:]), deepcopy(equation.value)))
        # return copy.deepcopy(self.constraint_list)
        return new_constraint_list_obj.constraints

    def setConstraintListCopy(self, new_constraint_list_obj):
        for equation in self.constraints:
            new_constraint_list_obj.constraints.append(Constraint(equation.constraint[:], int(equation.value)))
        # return copy.deepcopy(self.constraint_list)
        return new_constraint_list_obj.constraints

    # Get Length of the Constraint Equations List
    def getConstraintsListLength(self):
        numberOfEquations = 0
        for equation in self.constraints:
            if len(equation.constraint) > 0:
                numberOfEquations += 1
        return numberOfEquations

    def updateConstraintEquations(self, coordinate, value):
        for equation in self.constraints:
            if coordinate in equation.constraint:
                equation.constraint.remove(coordinate)
                equation.value = equation.value - value

    # Add a Constraint Equation and its Value to the Constraint Equation List
    def addConstraintEquation(self, constraint, value):
        self.constraints.append(Constraint(constraint, value))

    # Get Unique List of Constraint Equations
    def getUniqueConstraintList(self):
        uniqueConstraintList = []
        for equation in self.constraints:
            if len(equation) > 0 and equation not in uniqueConstraintList:
                uniqueConstraintList.append(equation)
        return uniqueConstraintList

    # Determine Coordinates that are Clues and Mines if it satisfies an Equation
    def markCluesAndMines(self):

        deducedClueCells = []
        deducedMineCells = []
        new_constraint_list = []

        for c in self.constraints:
            if len(c.constraint) == 0:
                continue
            elif c.value == 0:
                deducedClueCells.extend(c.constraint)
            elif len(c.constraint) == c.value:
                deducedMineCells.extend(c.constraint)
            else:
                new_constraint_list.append(c)
        self.constraints = new_constraint_list
        return deducedClueCells, deducedMineCells

    # Simplify Constraint Equations
    def performConstraintReductions(self):

        self.constraints.sort(key= lambda x: len(x.constraint))

        for eq_i in self.constraints:
            constraint_eq_i = eq_i.constraint
            value_eq_i = eq_i.value
            for eq_j in self.constraints:
                constraint_eq_j = eq_j.constraint
                value_eq_j = eq_j.value
                if eq_i == eq_j or len(constraint_eq_j) == 0:
                    continue
                elif set(constraint_eq_i).issubset(set(constraint_eq_j)):
                    eq_j.constraint = list(set(constraint_eq_j) - set(constraint_eq_i))
                    eq_j.value = value_eq_j - value_eq_i

                elif set(constraint_eq_j).issubset(set(constraint_eq_i)):
                    eq_i.constraint = list(set(constraint_eq_i) - set(constraint_eq_j))
                    eq_i.value = value_eq_i - value_eq_j

                    constraint_eq_i = eq_i.constraint
                    value_eq_i = eq_i.value

    # Get List of All Coordinates that Appear in a Constraint Equation
    def getListOfConstraintCoordinates(self):

        exhaustive_constraints = []
        for equation in self.constraints:
            exhaustive_constraints.extend(equation.constraint)
        return exhaustive_constraints

    # Get Random Cell From Coordinates in Constraint Equation List
    def getRandomCellForTree(self, exhaustive_constraints, testCell):
        if len(exhaustive_constraints) > 0:
            index = randint(0, len(exhaustive_constraints) - 1)
            return exhaustive_constraints[index]
        else:
            for equation in self.constraints:
                if len(equation.constraint) > 0:
                    index = randint(0, len(equation.constraint) - 1)
                    return equation[index]
            return testCell

    # Get Independent Sets of Constraint Equations
    def getDisjointConstraints(self, constraint_list):
        constraint_list_coordinates_set = set()
        for equation in constraint_list:
            for coordinate in equation.constraint:
                if coordinate not in constraint_list_coordinates_set:
                    constraint_list_coordinates_set.add(coordinate)

        constraint_list_coordinates = list(constraint_list_coordinates_set)
        union_set_index = {coordinate: None for coordinate in constraint_list_coordinates}

        disjointConstraints = []

        for coordinate in constraint_list_coordinates:
            index = 0
            if union_set_index[coordinate] is not None:
                continue

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

    # Get a Random Coordinate and Cell Type it (Mine or Clue) satisfies from the Constraint List of Equations
    def getRandomCellType(self, constraint_list):

        cellToReturnClue = None
        cellToReturnMine = None

        for c in constraint_list:
            if len(c.constraint) < 1:
                continue
            for cell in c.constraint:

                clue_list = ListOfConstraints()
                clue_list.setConstraintsFromList(constraint_list)

                mine_list = ListOfConstraints()
                mine_list.setConstraintsFromList(constraint_list)

                foundPotentialClueCell = self.testCellConstraints(clue_list.constraints,
                                                                  cell, MineSweeper.CLUE)
                foundPotentialMineCell = self.testCellConstraints(mine_list.constraints,
                                                                  cell, MineSweeper.MINE)
                # self.output_constraints()
                if foundPotentialClueCell and foundPotentialMineCell:

                    return cell, cell

                elif foundPotentialClueCell:

                    cellToReturnClue = cell

                elif foundPotentialMineCell:

                    cellToReturnMine = cell

        if cellToReturnClue:
            return cellToReturnClue, None
        elif cellToReturnMine:
            return None, cellToReturnMine
        else:
            return None, None

    # Check if Constraint List Equations Are Valid
    def checkConstraintsList(self):
        for eq_i in self.constraints:
            if len(eq_i.constraint) < eq_i.value or eq_i.value < 0:
                return False
            for eq_j in self.constraints:
                if eq_i == eq_j:
                    continue
                elif len(eq_j.constraint) < eq_j.value or eq_j.value < 0:
                    return False
        return True

    def testCellConstraints(self, constraints, cell, cellType):

        constraints.sort(key= lambda x: len(x.constraint))

        for c in constraints:
            if cell in c.constraint:
                c.value = c.value - cellType
                c.constraint.remove(cell)
                if len(c.constraint) < c.value or c.value < 0:
                    return False

        for i in constraints:
            constraint_i = i.constraint
            constraint_i_value = i.value
            if len(constraint_i) == 0:
                continue
            for j in constraints:
                constraint_j = j.constraint
                constraint_j_value = j.value
                if i == j or len(constraint_j) == 0:
                    continue
                elif set(constraint_i).issubset(set(constraint_j)):

                    j.constraint = list(set(constraint_j) - set(constraint_i))
                    j.value = constraint_j_value - constraint_i_value

                elif set(constraint_j).issubset(set(constraint_i)):

                    i.constraint = list(set(constraint_i) - set(constraint_j))
                    i.value = constraint_i_value - constraint_j_value
                    constraint_i = i.constraint
                    constraint_i_value = i.value

        for eq_i in constraints:
            if len(eq_i.constraint) < eq_i.value or eq_i.value < 0:
                return False
            for eq_j in constraints:
                if eq_i == eq_j or (len(eq_j.constraint) == 0 and eq_j.value == 0):
                    continue
                elif len(eq_j.constraint) < eq_j.value or eq_j.value < 0:
                    return False
        return True

    # Print Constraints List Equations
    def output_constraints(self):
        for c in self.constraints:
            print("List: ", c.constraint, " Value: ", c.value)