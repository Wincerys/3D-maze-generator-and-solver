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
        dimensions = [(maze.rowNum(level), maze.colNum(level)) for level in range(num_levels)]
        
        # Set to track visited cells and a list for the frontier cells (walls to be considered)
        visited = set()
        frontier = []

        # Start from a random cell
        start_level = random.randint(0, num_levels - 1)
        start_row = random.randint(0, dimensions[start_level][0] - 1)
        start_col = random.randint(0, dimensions[start_level][1] - 1)
        start_cell = Coordinates3D(start_level, start_row, start_col)
        
        # Mark the starting cell as visited
        visited.add(start_cell)
        
        # Add the neighbors of the starting cell to the frontier
        self.addNeighboursToFrontier(maze, start_cell, visited, frontier, dimensions)
        
        while frontier:
            # Randomly select a wall from the frontier
            current_wall = random.choice(frontier)
            frontier.remove(current_wall)
            
            # Find the visited neighbor of the wall
            neighbours = self.getVisitedNeighbours(maze, current_wall, visited)
            
            if neighbours:
                # Randomly choose one of the visited neighbors
                neighbour = random.choice(neighbours)
                
                # Remove the wall between the current cell and the chosen neighbor
                maze.removeWall(current_wall, neighbour)
                
                # Mark the current cell as visited
                visited.add(current_wall)
                
                # Add the neighbors of the current cell to the frontier
                self.addNeighboursToFrontier(maze, current_wall, visited, frontier, dimensions)
        
        # Set the mazeGenerated flag to True
        self.m_mazeGenerated = True

    def addNeighboursToFrontier(self, maze, cell, visited, frontier, dimensions):
        """
        Add the neighboring cells of the given cell to the frontier if they are not visited and within bounds.
        """
        neighbours = maze.neighbours(cell)
        for neighbour in neighbours:
            level, row, col = neighbour.getLevel(), neighbour.getRow(), neighbour.getCol()
            if (0 <= row < dimensions[level][0] and 0 <= col < dimensions[level][1] and
                    neighbour not in visited and neighbour not in frontier):
                frontier.append(neighbour)
    
    def getVisitedNeighbours(self, maze, cell, visited):
        """
        Get the neighbors of the given cell that have been visited.
        """
        neighbours = maze.neighbours(cell)
        return [neighbour for neighbour in neighbours if neighbour in visited]
