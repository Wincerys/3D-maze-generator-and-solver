from maze.maze3D import Maze3D
from maze.util import Coordinates3D
from generation.mazeGenerator import MazeGenerator
import random

class WilsonMazeGenerator(MazeGenerator):
    """
    Wilson's algorithm maze generator for 3D mazes.
    """

    def generateMaze(self, maze: Maze3D):
        # Initialize the maze with all walls
        maze.initCells(addWallFlag=True)

        # Dimensions of the maze
        num_levels = maze.levelNum()
        dimensions = [(maze.rowNum(level), maze.colNum(level)) for level in range(num_levels)]

        # Set of finalized cells
        finalized = set()

        # Start with a random cell
        start_level = random.randint(0, num_levels - 1)
        start_row = random.randint(0, dimensions[start_level][0] - 1)
        start_col = random.randint(0, dimensions[start_level][1] - 1)
        start_cell = Coordinates3D(start_level, start_row, start_col)

        # Mark the starting cell as finalized
        finalized.add(start_cell)

        # Generate maze using Wilson's algorithm
        unfinalized_cells = [Coordinates3D(l, r, c) for l in range(num_levels) for r in range(dimensions[l][0]) for c in range(dimensions[l][1])]
        unfinalized_cells.remove(start_cell)

        while unfinalized_cells:
            # Select a random unfinalized cell
            current_cell = random.choice(unfinalized_cells)
            path = [current_cell]

            while current_cell not in finalized:
                # Perform a random walk
                neighbours = self._get_valid_neighbors(maze, current_cell)
                next_cell = random.choice(neighbours)

                if next_cell in path:
                    # Remove the loop if we've visited the cell before
                    loop_index = path.index(next_cell)
                    path = path[:loop_index + 1]
                else:
                    path.append(next_cell)

                current_cell = next_cell

            # Add the path to the finalized cells and remove walls
            for i in range(len(path) - 1):
                if self._is_within_boundaries(maze, path[i], path[i + 1]):
                    maze.removeWall(path[i], path[i + 1])
                finalized.add(path[i])
                if path[i] in unfinalized_cells:
                    unfinalized_cells.remove(path[i])

            # Ensure the last cell is also finalized
            finalized.add(path[-1])
            if path[-1] in unfinalized_cells:
                unfinalized_cells.remove(path[-1])

        # Add boundaries after generating the maze
        self._add_boundaries(maze)

        # Set the mazeGenerated flag to True
        self.m_mazeGenerated = True

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

    def _get_valid_neighbors(self, maze: Maze3D, cell: Coordinates3D):
        neighbors = []
        directions = [
            (0, -1, 0),    # North
            (0, 0, 1),     # North-East (up one level)
            (1, 0, 0),     # East
            (0, 1, 0),     # South
            (0, 0, -1),    # South-West (down one level)
            (-1, 0, 0)     # West
        ]

        levels = maze.levelNum()
        for direction in directions:
            neighbor = Coordinates3D(
                cell.getLevel() + direction[2],
                cell.getRow() + direction[1],
                cell.getCol() + direction[0]
            )
            if 0 <= neighbor.getLevel() < levels:
                target_level = neighbor.getLevel()
                target_rows = maze.rowNum(target_level)
                target_cols = maze.colNum(target_level)
                if 0 <= neighbor.getRow() < target_rows and 0 <= neighbor.getCol() < target_cols:
                    neighbors.append(neighbor)

        return neighbors
