class MineSweeper:
    # Cell Types
    UNKNOWN_CELL = "C"
    MINE_CELL = "M"
    FLAG = "F"
    # Cell Type Values
    CLUE = 0
    MINE = 1
    CLUE_AND_MINE = 2
    # Minimize Types
    COST = "COST"
    RISK = "RISK"
    NONE = "NONE"
    # Bounds
    MAX_NEIGHBORS = 8