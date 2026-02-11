from maze.maze3D import Maze3D
from maze.util import Coordinates3D
from generation.mazeGenerator import MazeGenerator
import random

class PrimMazeGenerator(MazeGenerator):
    """
    Prim's algorithm maze generator for 3D mazes.
    """

    def generateMaze(self, maze: Maze3D):
        # Initialize the maze with all walls
        maze.initCells(addWallFlag=True)

        # Dimensions of the maze
        num_levels = maze.levelNum()
        
        # Set to track visited cells and dict for frontier cells
        # frontier maps: cell -> neighboring visited cell that added it
        visited = set()
        frontier = {}  # Changed from list to dict
        
        # Get all valid cells
        all_cells = [Coordinates3D(l, r, c) 
                     for l in range(num_levels) 
                     for r in range(maze.rowNum(l)) 
                     for c in range(maze.colNum(l))]
        
        # Start from a random cell
        start_cell = random.choice(all_cells)
        
        # Mark the starting cell as visited
        visited.add(start_cell)
        
        # Add the neighbors of the starting cell to the frontier
        self._addNeighboursToFrontier(maze, start_cell, visited, frontier)
        
        while frontier:
            # Randomly select a cell from the frontier
            current_cell = random.choice(list(frontier.keys()))
            neighbor_that_added_it = frontier[current_cell]
            
            # Remove wall between current cell and the neighbor that added it
            maze.removeWall(current_cell, neighbor_that_added_it)
            
            # Mark the current cell as visited
            visited.add(current_cell)
            del frontier[current_cell]
            
            # Add the neighbors of the current cell to the frontier
            self._addNeighboursToFrontier(maze, current_cell, visited, frontier)
        
        # Set the mazeGenerated flag to True
        self.m_mazeGenerated = True

    def _addNeighboursToFrontier(self, maze, cell, visited, frontier):
        """
        Add the neighboring cells of the given cell to the frontier.
        Maps each frontier cell to the visited cell that added it.
        """
        neighbours = maze.neighbours(cell)
        for neighbour in neighbours:
            # Check if within maze boundaries
            level = neighbour.getLevel()
            if level < 0 or level >= maze.levelNum():
                continue
                
            row, col = neighbour.getRow(), neighbour.getCol()
            if (0 <= row < maze.rowNum(level) and 
                0 <= col < maze.colNum(level) and
                neighbour not in visited and 
                neighbour not in frontier):
                frontier[neighbour] = cell  # Track which visited cell added this frontier cell