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
        
        # Set of finalized cells
        finalized = set()
        
        # Get all cells
        all_cells = [Coordinates3D(l, r, c) 
                     for l in range(num_levels) 
                     for r in range(maze.rowNum(l)) 
                     for c in range(maze.colNum(l))]
        
        # Start with a random cell
        start_cell = random.choice(all_cells)
        finalized.add(start_cell)
        
        # Track unfinalized cells
        unfinalized_cells = set(all_cells) - {start_cell}

        while unfinalized_cells:
            # Select a random unfinalized cell
            current_cell = random.choice(list(unfinalized_cells))
            path = {current_cell: None}  # Use dict to track path and handle loops efficiently
            path_order = [current_cell]
            
            # Perform random walk until we hit a finalized cell
            walk_cell = current_cell
            while walk_cell not in finalized:
                neighbours = self._get_valid_neighbors(maze, walk_cell)
                next_cell = random.choice(neighbours)
                
                if next_cell in path:
                    # Loop detected - erase the loop
                    loop_start_idx = path_order.index(next_cell)
                    # Remove cells in the loop from path
                    for cell in path_order[loop_start_idx + 1:]:
                        del path[cell]
                    path_order = path_order[:loop_start_idx + 1]
                else:
                    # Add to path
                    path[next_cell] = walk_cell
                    path_order.append(next_cell)
                
                walk_cell = next_cell
            
            # Carve the path (excluding the last cell which is already finalized)
            for i in range(len(path_order) - 1):
                cell1 = path_order[i]
                cell2 = path_order[i + 1]
                maze.removeWall(cell1, cell2)
                finalized.add(cell1)
                unfinalized_cells.discard(cell1)

        # Set the mazeGenerated flag to True
        self.m_mazeGenerated = True

    def _get_valid_neighbors(self, maze: Maze3D, cell: Coordinates3D):
        """Get all valid neighbors of a cell within maze boundaries."""
        neighbors = []
        directions = [
            (0, -1, 0),    # North
            (0, 0, 1),     # North-East (up one level)
            (1, 0, 0),     # East
            (0, 1, 0),     # South
            (0, 0, -1),    # South-West (down one level)
            (-1, 0, 0)     # West
        ]

        for dcol, drow, dlevel in directions:
            neighbor = Coordinates3D(
                cell.getLevel() + dlevel,
                cell.getRow() + drow,
                cell.getCol() + dcol
            )
            level = neighbor.getLevel()
            
            # Check level bounds
            if 0 <= level < maze.levelNum():
                row, col = neighbor.getRow(), neighbor.getCol()
                # Check row/col bounds for this level
                if 0 <= row < maze.rowNum(level) and 0 <= col < maze.colNum(level):
                    neighbors.append(neighbor)

        return neighbors