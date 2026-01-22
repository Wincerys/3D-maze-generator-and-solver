from typing import List, Tuple
import random
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

# Define angles for turns
TURN_ANGLES = {
    "N": {"L": -60, "R": 60},
    "NE": {"L": -60, "R": 60},
    "E": {"L": -60, "R": 60},
    "S": {"L": -60, "R": 60},
    "SW": {"L": -60, "R": 60},
    "W": {"L": -60, "R": 60}
}

class PledgeMazeSolver(MazeSolver):
    """
    Pledge solver implementation.
    """

    def __init__(self):
        super().__init__()
        self.m_name = "pledge"
        self.path = []
        self.cells_explored = 0
        self.entrance_used = None
        self.exit_used = None
        self.m_solverPath = []
        self.exits = set()

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
        return True

    def wall_following(self, maze: Maze3D, start: Coordinates3D, initial_direction: str, hand_rule: str) -> Coordinates3D:
        current_position = start
        angle = 0
        visited = set()
        self.path = [start]
        self.m_solverPath.append((start, False))

        while True:
            if current_position in self.exits:
                self.exit_used = current_position
                return current_position

            visited.add(current_position)
            self.cells_explored += 1

            if hand_rule == "left":
                directions_order = ["N", "NE", "E", "S", "SW", "W"]
            else:
                directions_order = ["N", "W", "SW", "S", "E", "NE"]

            moved = False
            for direction in directions_order:
                next_position = self.get_next_position(current_position, direction)
                if self.is_valid_move(maze, current_position, next_position) and next_position not in visited:
                    angle += TURN_ANGLES[initial_direction]["L"] if hand_rule == "left" else TURN_ANGLES[initial_direction]["R"]
                    current_position = next_position
                    self.path.append(next_position)
                    self.m_solverPath.append((next_position, False))
                    moved = True
                    break

            if angle == 0:
                return current_position  # Return to initial direction

            if not moved:
                if len(self.path) > 1:
                    self.path.pop()
                    self.m_solverPath.append((self.path[-1], True))
                    current_position = self.path[-1]
                else:
                    break

    def solveMaze(self, maze: Maze3D, entrance: Coordinates3D):
        self.entrance_used = entrance
        self.exits = set(maze.getExits())
        initial_direction = random.choice(list(DIRECTIONS.keys()))
        hand_rule = random.choice(["left", "right"])

        current_position = entrance
        while True:
            next_position = self.get_next_position(current_position, initial_direction)
            if self.is_valid_move(maze, current_position, next_position):
                current_position = next_position
                self.path.append(next_position)
                self.m_solverPath.append((next_position, False))
            else:
                current_position = self.wall_following(maze, current_position, initial_direction, hand_rule)

            if current_position in self.exits:
                break

        return self.path

    def getCellsExplored(self) -> int:
        return self.cells_explored

    def getEntranceUsed(self) -> Coordinates3D:
        return self.entrance_used

    def getExitUsed(self) -> Coordinates3D:
        return self.exit_used

    def getSolverPath(self) -> List[Tuple[Coordinates3D, bool]]:
        return self.m_solverPath
