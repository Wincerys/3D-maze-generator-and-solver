from typing import List, Tuple
from maze.util import Coordinates3D
from maze.maze3D import Maze3D
from solving.mazeSolver import MazeSolver

# Define directions including up and down movements
DIRECTIONS = {
    "N": (0, -1, 0),    # North
    "NE": (0, 0, 1),    # North-East (up one level)
    "E": (1, 0, 0),     # East
    "S": (0, 1, 0),     # South
    "SW": (0, 0, -1),   # South-West (down one level)
    "W": (-1, 0, 0)     # West
}

class WallFollowingMazeSolver(MazeSolver):
    """
    Wall following solver implementation with backtracking.
    """

    def __init__(self):
        self.path = []
        self.cells_explored = 0
        self.entrance_used = None
        self.exit_used = None
        self.m_solverPath = []
        self.exits = set()
        self.m_name = "wall"

    def getName(self):
        return self.m_name

    def get_next_position(self, current_position: Coordinates3D, direction: str) -> Coordinates3D:
        current_x, current_y, current_z = current_position.getCol(), current_position.getRow(), current_position.getLevel()
        move_x, move_y, move_z = DIRECTIONS[direction]
        return Coordinates3D(current_z + move_z, current_y + move_y, current_x + move_x)

    def is_valid_move(self, maze: Maze3D, current_position: Coordinates3D, next_position: Coordinates3D) -> bool:
        # Check if the next position is within maze bounds and not a boundary wall
        if next_position in self.exits:
            # Ensure the exit is on the same level as the current position
            if current_position.getLevel() == next_position.getLevel() and not maze.hasWall(current_position, next_position):
                return True

        if not maze.hasCell(next_position):
            return False
        if maze.hasWall(current_position, next_position):
            return False

        # Ensure we are not moving into boundary cells unless it is an exit
        level, row, col = next_position.getLevel(), next_position.getRow(), next_position.getCol()
        rowNum, colNum = maze.rowNum(level), maze.colNum(level)
        if row < 0 or row >= rowNum or col < 0 or col >= colNum:
            if next_position not in self.exits:
                return False

        # Ensure valid level transitions
        if next_position.getLevel() != current_position.getLevel():
            # If moving up or down a level, ensure the target cell is within maze boundaries
            if next_position.getLevel() > current_position.getLevel():  # Moving up
                target_row, target_col = next_position.getRow(), next_position.getCol()
            else:  # Moving down
                target_row, target_col = next_position.getRow(), next_position.getCol()

            if target_row < 0 or target_row >= maze.rowNum(next_position.getLevel()) or target_col < 0 or target_col >= maze.colNum(next_position.getLevel()):
                return False

        return True

    def solveMaze(self, maze: Maze3D, start: Coordinates3D) -> List[Coordinates3D]:
        self.entrance_used = start
        self.path = [start]
        self.current_position = start
        self.directions_order = ["N", "NE", "E", "S", "SW", "W"]
        visited = set()
        self.m_solverPath = [(start, False)]
        self.exits = set(maze.getExits())

        while True:
            if self.current_position in self.exits:
                self.exit_used = self.current_position
                break

            moved = False
            visited.add(self.current_position)
            self.cells_explored += 1

            for direction in self.directions_order:
                next_position = self.get_next_position(self.current_position, direction)
                if self.is_valid_move(maze, self.current_position, next_position) and next_position not in visited:
                    self.current_position = next_position
                    self.path.append(next_position)
                    self.m_solverPath.append((next_position, False))
                    moved = True
                    break

            if not moved:
                if len(self.path) > 1:
                    # If no valid move is found, backtrack
                    self.path.pop()
                    self.m_solverPath.append((self.path[-1], True))
                    self.current_position = self.path[-1]
                else:
                    # If backtracking is not possible, terminate to prevent infinite loop
                    break

        self.m_solverPath.append((self.current_position, False))
        return self.path

    def getCellsExplored(self) -> int:
        return self.cells_explored

    def getEntranceUsed(self) -> Coordinates3D:
        return self.entrance_used

    def getExitUsed(self) -> Coordinates3D:
        return self.exit_used

    def getSolverPath(self) -> List[Tuple[Coordinates3D, bool]]:
        return self.m_solverPath
