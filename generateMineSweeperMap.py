from definitionsForAgent import MineSweeper, VALUE, TYPE
from random import randint


class GenerateMineSweeperMap:
    def __init__(self, dimensions, numberOfMines, startingCoordinate, map_):

        self.dimensions = dimensions
        self.startingCoordinate = startingCoordinate
        self.numberOfMines = numberOfMines

        self.minesResolvedByAgent, self.agent_died = 0, 0

        self.mines, self.hidden_map, self.agent_map = {}, None, None

        self.initialize_maps(isMapPassed=map_)

    def initialize_maps(self, isMapPassed):
        if isMapPassed == -1:
            self.hidden_map = [[0 for _ in range(self.dimensions)] for _ in range(self.dimensions)]
        else:
            self.hidden_map = isMapPassed
            for x in range(self.dimensions):
                for y in range(self.dimensions):
                    self.hidden_map[x][y] = isMapPassed[x][y]
                    if self.hidden_map[x][y] == VALUE.MINE:
                        self.mines[(x, y)] = True
                    else:
                        self.mines[(x, y)] = False

        self.agent_map = [[TYPE.UNKNOWN for _ in range(self.dimensions)] for _ in range(self.dimensions)]

    def isMine(self, coordinate):
        (x, y) = coordinate
        return self.hidden_map[x][y] == TYPE.MINE

    def inbounds(self, coordinate):
        (x, y) = coordinate
        return True if MineSweeper.MIN_BOUND <= x < self.dimensions and MineSweeper.MIN_BOUND <= y < self.dimensions else False

    def adjacentMines(self, coordinate):
        (x, y) = coordinate
        neighboringMines = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                            (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        neighboringMines = list(filter(self.inbounds, neighboringMines))
        neighboringMines = list(filter(self.isMine, neighboringMines))
        return neighboringMines

    def markAdjacentMines(self):
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                if self.hidden_map[x][y] == TYPE.MINE:
                    self.mines[(x, y)] = True
                else:
                    neighboringMines = self.adjacentMines((x, y))
                    self.hidden_map[x][y] = len(neighboringMines)
                    self.mines[(x, y)] = False

    def get_value(self, uncoveredCell):
        (x, y) = uncoveredCell
        if self.hidden_map[x][y] == TYPE.MINE:
            # print("Your agent unfortunately blew up...")
            self.agent_died = self.agent_died + 1
            return TYPE.FLAG, True
        else:
            return int(self.hidden_map[x][y]), False

    def create_map(self):
        mines = []
        while len(mines) < self.numberOfMines:
            x = randint(0, self.dimensions)
            y = randint(0, self.dimensions)
            if (x, y) == self.startingCoordinate:
                continue
            elif x < self.dimensions and y < self.dimensions and self.hidden_map[x][y] != TYPE.MINE:
                if (x, y) not in mines:
                    mines.append((x, y))
                    self.hidden_map[x][y] = TYPE.MINE
        self.markAdjacentMines()

    def validate(self, agent_solution):
        failure, mines_found = 0, 0
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                if not ((self.hidden_map[x][y] == TYPE.MINE and agent_solution[x][y] == TYPE.FLAG)
                        or self.hidden_map[x][y] == agent_solution[x][y]):
                    failure = failure + 1
                if self.hidden_map[x][y] == TYPE.MINE and agent_solution[x][y] == TYPE.FLAG:
                    mines_found = mines_found + 1

        if failure == 0:
            print("Agent successfully found all", self.numberOfMines, "mines and died ", self.agent_died)
            self.minesResolvedByAgent = self.numberOfMines
        else:
            self.minesResolvedByAgent = mines_found
            print("Agent failed but found", mines_found, "mines and died ", self.agent_died)

    def print_hidden_map(self):
        print(" ------------- HIDDEN MAP ------------- ")
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                if not self.mines[(x, y)]:
                    print("| ", self.hidden_map[x][y], end="")
                else:
                    print("|  M", end="")
            print("|", end="")
            print()
        print(" ------------- END OF MAP ------------- ")
