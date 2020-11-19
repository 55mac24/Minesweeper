from constraint import Constraint


class ListOfConstraints:
    def __init__(self):
        self.constraints = []

    def set(self, constraint_list):
        self.constraints = []
        for equation in constraint_list:
            constraint = []
            for tuple_i in equation.constraint:
                (x_i, y_i) = int(tuple_i[0]), int(tuple_i[1])
                constraint.append((x_i, y_i))
            self.constraints.append(Constraint(constraint, int(equation.value)))

    def get(self):
        constraints = []
        for equation in self.constraints:
            constraint = []
            for tuple_i in equation.constraint:
                (x_i, y_i) = int(tuple_i[0]), int(tuple_i[1])
                constraint.append((x_i, y_i))
            constraints.append(Constraint(constraint, int(equation.value)))
        return constraints

    def update(self, coordinate, value):
        for equation in self.constraints:
            if coordinate in equation.constraint:
                equation.constraint.remove(coordinate)
                equation.value = equation.value - value

    # Add a constraint equation and its value to the constraint equation list
    def add(self, constraint, value):
        self.constraints.append(Constraint(constraint, value))

    # Determine coordinates that are clues and mines if it satisfies an equation
    def deduce(self):
        deducedClueCells, deducedMineCells = [], []
        new_constraint_list = []
        for c in self.constraints:
            if len(c.constraint) == 0:
                continue
            elif c.value == 0:
                deducedClueCells.extend(c.constraint)
            elif len(c.constraint) == c.value:
                deducedMineCells.extend(c.constraint)
            else:
                if len(c.constraint) > 0:
                    new_constraint_list.append(c)

        self.set(new_constraint_list)

        return deducedClueCells, deducedMineCells

    # Simplify Constraint Equations
    def reduce(self):
        self.constraints.sort(key=lambda x: len(x.constraint))
        for eq_i in self.constraints:
            for eq_j in self.constraints:
                if eq_i == eq_j or len(eq_j.constraint) == 0:
                    continue

                elif set(eq_i.constraint).issubset(set(eq_j.constraint)):
                    eq_j.constraint = list(set(eq_j.constraint) - set(eq_i.constraint))
                    eq_j.value = eq_j.value - eq_i.value

                elif set(eq_j.constraint).issubset(set(eq_i.constraint)):
                    eq_i.constraint = list(set(eq_i.constraint) - set(eq_j.constraint))
                    eq_i.value = eq_i.value - eq_j.value

    # Get List of All Coordinates that Appear in a Constraint Equation
    def coordinates(self):
        exhaustive_constraints = []
        for equation in self.constraints:
            exhaustive_constraints.extend(equation.constraint)
        return exhaustive_constraints

    # Check if Constraint List Equations Are Valid
    def check(self, check_length=True):
        numberOfEquations = 0
        for eq_i in self.constraints:
            if len(eq_i.constraint) < eq_i.value or eq_i.value < 0:
                return False
            elif len(eq_i.constraint) > 0:
                numberOfEquations += 1
        if check_length:
            return False if numberOfEquations > 0 else True
        else:
            return True

    # Get Length of the Constraint Equations List
    def length(self):
        numberOfEquations = 0
        for equation in self.constraints:
            if len(equation.constraint) > 0:
                numberOfEquations += 1
        return numberOfEquations

    # Print Constraints List Equations
    def output(self):
        for eq_i in self.constraints:
            print("Equation: ", eq_i.constraint, " Value: ", eq_i.value)