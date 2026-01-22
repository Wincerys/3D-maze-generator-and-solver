from random import randint, choice
from collections import deque

from typing import List, Tuple
from maze.maze3D import Maze3D
from maze.util import Coordinates3D
from generation.mazeGenerator import MazeGenerator
import random

DIRECTIONS = [
    (0, -1, 0),    # North
    (0, 0, 1),     # North-East (up one level)
    (1, 0, 0),     # East
    (0, 1, 0),     # South
    (0, 0, -1),    # South-West (down one level)
    (-1, 0, 0)     # West
]

class TaskDMazeGenerator(MazeGenerator):
    def __init__(self, solver_name: str):
        self.solver_name = solver_name
        self.m_mazeGenerated = False

    def generateMaze(self, maze: Maze3D):
        maze.initCells(addWallFlag=True)
        
        if self.solver_name == 'recur':
            self._generate_maze_for_recur(maze)
            print(f"Recursive Backtrack maze generator was used")
        elif self.solver_name == 'wall':
            self._generate_maze_for_wall(maze)
            print(f"Wall follower maze generator was used")
        elif self.solver_name == 'pledge':
            self._generate_maze_for_pledge(maze)
            print(f"Pledge maze generator was used")
        elif self.solver_name == 'taskC':
            self._generate_maze_for_taskC(maze)
            print(f"TaskC maze generator was used")

        self._add_boundaries(maze)
        self.m_mazeGenerated = True

    def _add_boundaries(self, maze: Maze3D):
        levels = maze.levelNum()
        for level in range(levels):
            rows, cols = maze.rowNum(level), maze.colNum(level)
            for row in range(rows):
                maze.addWall(Coordinates3D(level, row, -1), Coordinates3D(level, row, 0))
                maze.addWall(Coordinates3D(level, row, cols - 1), Coordinates3D(level, row, cols))
            for col in range(cols):
                maze.addWall(Coordinates3D(level, -1, col), Coordinates3D(level, 0, col))
                maze.addWall(Coordinates3D(level, rows - 1, col), Coordinates3D(level, rows, col))

    def _generate_maze_for_recur(self, maze: Maze3D):
        # select starting cell 
        # random floor
        startLevel = randint(0, maze.levelNum()-1)
        startCoord: Coordinates3D = Coordinates3D(startLevel, randint(0, maze.rowNum(startLevel)-1), randint(0, maze.colNum(startLevel)-1))

        # run recursive backtracking/DFS from starting cell
        stack: deque = deque()
        stack.append(startCoord)
        currCell: Coordinates3D = startCoord 
        visited: set[Coordinates3D] = set([startCoord])

        totalCells = sum([maze.rowNum(l) * maze.colNum(l) for l in range(maze.levelNum())])

        while len(visited) < totalCells:
            # find all neighbours of current cell
            neighbours: list[Coordinates3D] = maze.neighbours(currCell)

            # filter to ones that haven't been visited and within boundary
            nonVisitedNeighs: list[Coordinates3D] = [neigh for neigh in neighbours if neigh not in visited and\
                                             neigh.getRow() >= 0 and neigh.getRow() < maze.rowNum(neigh.getLevel()) and\
                                                neigh.getCol() >= 0 and neigh.getCol() < maze.colNum(neigh.getLevel())]
            
            # see if any unvisited neighbours
            if len(nonVisitedNeighs) > 0:
                # randomly select one of them
                neigh = choice(nonVisitedNeighs)

                # we move there and knock down wall
                maze.removeWall(currCell, neigh)

                # add to stack
                stack.append(neigh)

                # updated visited
                visited.add(neigh)

                # update currCell
                currCell = neigh
            else:
                # backtrack
                currCell = stack.pop()

        # update maze generated
        self.m_mazeGenerated = True

    def _generate_maze_for_wall(self, maze: Maze3D):
        def prim_algorithm():
            start_cell = Coordinates3D(0, 0, 0)
            frontier = [start_cell]
            in_maze = set([start_cell])

            while frontier:
                current_cell = random.choice(frontier)
                neighbors = self._get_neighbors(maze, current_cell)
                valid_neighbors = [neighbor for neighbor in neighbors if neighbor not in in_maze and maze.hasCell(neighbor)]

                if valid_neighbors:
                    next_cell = random.choice(valid_neighbors)
                    if not maze.checkCoordinates(current_cell) or not maze.checkCoordinates(next_cell):
                        frontier.remove(current_cell)
                        continue

                    maze.removeWall(current_cell, next_cell)
                    in_maze.add(next_cell)
                    frontier.append(next_cell)
                else:
                    frontier.remove(current_cell)

        prim_algorithm()

    def _generate_maze_for_pledge(self, maze: Maze3D):
        self._generate_maze_with_kruskal(maze)
        self._add_dead_ends(maze)

    def _generate_maze_for_taskC(self, maze: Maze3D):
        self._generate_maze_with_kruskal(maze)

    def _generate_maze_with_kruskal(self, maze: Maze3D):
        """
        Generate a perfect maze using Kruskal's algorithm.
        """
        edges = []
        cells = maze.allCells()
        parent = {cell: cell for cell in cells}

        def find(cell):
            if parent[cell] != cell:
                parent[cell] = find(parent[cell])
            return parent[cell]

        def union(cell1, cell2):
            root1 = find(cell1)
            root2 = find(cell2)
            if root1 != root2:
                parent[root2] = root1

        for cell in cells:
            for neighbor in self._get_neighbors(maze, cell):
                if maze.hasWall(cell, neighbor):
                    edges.append((cell, neighbor))

        random.shuffle(edges)

        while edges:
            cell1, cell2 = edges.pop()
            if find(cell1) != find(cell2):
                # Check if both cells are within boundaries
                if not maze.checkCoordinates(cell1) or not maze.checkCoordinates(cell2):
                    continue

                # Check if removing the wall will not lead outside the maze boundaries
                if not self._is_within_boundaries(maze, cell1, cell2):
                    continue

                maze.removeWall(cell1, cell2)
                union(cell1, cell2)

    def _is_within_boundaries(self, maze: Maze3D, cell1: Coordinates3D, cell2: Coordinates3D) -> bool:
        """
        Check if the passage between two cells is within the maze boundaries.
        """
        levels = maze.levelNum()
        for cell in [cell1, cell2]:
            if not (0 <= cell.getLevel() < levels):
                return False
            rows, cols = maze.rowNum(cell.getLevel()), maze.colNum(cell.getLevel())
            if not (0 <= cell.getRow() < rows) or not (0 <= cell.getCol() < cols):
                return False
        return True

    def _add_dead_ends(self, maze: Maze3D):
        levels = maze.levelNum()
        for level in range(levels):
            rows, cols = maze.rowNum(level), maze.colNum(level)
            for _ in range(rows * cols // 6):  # Add a few dead ends
                cell = Coordinates3D(level, random.randint(0, rows - 1), random.randint(0, cols - 1))
                if maze.checkCoordinates(cell):
                    neighbors = self._get_neighbors(maze, cell)
                    if len(neighbors) == 1:
                        neighbor = neighbors[0]
                        if not maze.hasWall(cell, neighbor):
                            maze.addWall(cell, neighbor)

    def _get_neighbors(self, maze: Maze3D, cell: Coordinates3D) -> List[Coordinates3D]:
        neighbors = []
        levels, rows, cols = maze.levelNum(), maze.rowNum(cell.getLevel()), maze.colNum(cell.getLevel())
        for direction in DIRECTIONS:
            neighbor = Coordinates3D(
                cell.getLevel() + direction[2],
                cell.getRow() + direction[1],
                cell.getCol() + direction[0]
            )
            # Check that neighbor is within maze boundaries
            if 0 <= neighbor.getLevel() < levels:
                target_level = neighbor.getLevel()
                target_rows = maze.rowNum(target_level)
                target_cols = maze.colNum(target_level)
                if 0 <= neighbor.getRow() < target_rows and 0 <= neighbor.getCol() < target_cols:
                    neighbors.append(neighbor)
        return neighbors

    def solveMaze(self, maze: Maze3D, mazeEntrances: List[Coordinates3D], solverEntIndex: int):
        if self.solver_name == 'taskC':
            solver.solveMaze(maze)
        else:
            solver.solveMaze(maze, mazeEntrances[solverEntIndex])

    def isMazeGenerated(self):
        return self.m_mazeGenerated
 