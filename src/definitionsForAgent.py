class MineSweeper:
    # Bounds
    MAX_NEIGHBORS = 8
    MIN_BOUND = 0
    # Execution modes that change output
    DEBUG = -1
    PRODUCTION = -2
    PRODUCTION_MAPS = -3


class SELECTION:
    # Coordinate Selection Type
    CONSTRAINT_REDUCTION = 200
    RANDOM_SELECT = 201
    PREDICTION = 202
    RESTART = 203
    START = 204


class MINIMIZE:
    # Minimize Types
    COST = 102
    RISK = 101
    NONE = 100


class VALUE:
    # Cell Type Values
    CLUE = 0
    MINE = 1


class TYPE:
    # Cell Types
    UNKNOWN = "C"
    MINE = "M"
    FLAG = "F"
