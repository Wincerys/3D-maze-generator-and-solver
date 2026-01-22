from typing import List, Tuple, Dict
from collections import deque
from maze.util import Coordinates3D
from maze.maze3D import Maze3D
from solving.mazeSolver import MazeSolver

# Define the possible directions of movement, including level transitions
DIRECTIONS = [
    (0, -1, 0),    # North
    (0, 0, 1),     # North-East (up one level)
    (1, 0, 0),     # East
    (0, 1, 0),     # South
    (0, 0, -1),    # South-West (down one level)
    (-1, 0, 0)     # West
]

class TaskCMazeSolver(MazeSolver):
    
    """
    Task C solver implementation for finding the closest entrance-exit pair in a 3D maze.
    """

    def __init__(self):
        super().__init__()
        self.m_name = "taskC"
        self.cells_explored = 0
        self.entrance_used = None
        self.exit_used = None
        self.m_solverPath = []
        self.distance = 0

    def getName(self):
        return self.m_name
    
    def is_valid_move(self, maze: Maze3D, current_position: Coordinates3D, next_position: Coordinates3D) -> bool:
        """
        Checks if the move to the next position is valid.
        """
        if not maze.hasCell(next_position):
            return False
        if maze.hasWall(current_position, next_position):
            return False
        return True

    def bfs_explore(self, maze: Maze3D, start: Coordinates3D) -> Dict[Coordinates3D, Tuple[Coordinates3D, int]]:
        """
        Explores the maze using BFS to find all reachable cells and distances from the start position.
        """
        queue = deque([start])
        visited = {start: (None, 0)}
        unique_cells_explored = set()
        exits = set(maze.getExits())

        while queue:
            current_position = queue.popleft()
            current_distance = visited[current_position][1]
            unique_cells_explored.add(current_position)

            if current_position in exits:
                exits.remove(current_position)
                if not exits:
                    break

            for direction in DIRECTIONS:
                next_position = Coordinates3D(
                    current_position.getLevel() + direction[2],
                    current_position.getRow() + direction[1],
                    current_position.getCol() + direction[0]
                )
                if self.is_valid_move(maze, current_position, next_position) and next_position not in visited:
                    queue.append(next_position)
                    visited[next_position] = (current_position, current_distance + 1)

        self.cells_explored = len(unique_cells_explored)
        return visited

    def backtrack_path(self, visited: Dict[Coordinates3D, Tuple[Coordinates3D, int]], start: Coordinates3D, end: Coordinates3D) -> List[Coordinates3D]:
        """
        Backtracks to find the path from start to end using the visited dictionary.
        """
        path = []
        current = end
        while current != start:
            path.append(current)
            current = visited[current][0]
        path.append(start)
        path.reverse()
        return path

    def solveMazeTaskC(self, maze: Maze3D):
        """
        Solves the maze to find the closest entrance-exit pair.
        """
        entrances = maze.getEntrances()
        all_exits = maze.getExits()
        best_cost = float('inf')
        best_path = []
        best_entrance = None
        best_exit = None

        for entrance in entrances:
            visited = self.bfs_explore(maze, entrance)
            for exit in all_exits:
                if exit in visited:
                    path_to_exit = self.backtrack_path(visited, entrance, exit)
                    total_cost = len(path_to_exit) + self.cells_explored
                    if total_cost < best_cost:
                        best_cost = total_cost
                        best_path = path_to_exit
                        best_entrance = entrance
                        best_exit = exit

        self.entrance_used = best_entrance
        self.exit_used = best_exit
        self.m_solverPath = [(cell, False) for cell in best_path]
        self.distance = len(best_path) - 1  # Distance is the number of steps in the path

        # Print the results
        print(f"Distance between entrance {self.entrance_used} and exit {self.exit_used}: {self.distance}")

    def solveMaze(self, maze: Maze3D):
        """
        Wrapper method to call the solve maze task C without providing an entrance.
        """
        self.solveMazeTaskC(maze)

    def getCellsExplored(self) -> int:
        return self.cells_explored

    def getEntranceUsed(self) -> Coordinates3D:
        return self.entrance_used

    def getExitUsed(self) -> Coordinates3D:
        return self.exit_used

    def getSolverPath(self) -> List[Tuple[Coordinates3D, bool]]:
        return self.m_solverPath

    def getDistance(self) -> int:
        return self.distance
