from generation.mazeGenerator import MazeGenerator
from generation.recurBackGenerator import RecurBackMazeGenerator
from generation.primGenerator import PrimMazeGenerator
from generation.wilsonGenerator import WilsonMazeGenerator
from generation.taskDMazeGenerator import TaskDMazeGenerator
from solving.mazeSolver import MazeSolver


class GeneratorSelector:
    """
    Class used to select and construct appropriate maze generator.
    """


    def construct(self, genApproach: str)->MazeGenerator:
        """
        Tasks A, B and C, with a specified maze generator.
        If genApproach is unknown, None will be returned.

        @param genApproach: Name of generator to use.
        
        @return: Instance of a maze generator.
        """
        generator: MazeGenerator = None

        if genApproach == 'recur':
            generator = RecurBackMazeGenerator()
        elif genApproach == 'prim':
            generator = PrimMazeGenerator()
        elif genApproach == 'wilson':
            generator = WilsonMazeGenerator()
        # TODO: If you implement other generators, you can add them here

        return generator



    def match(self, solver: MazeSolver) -> MazeGenerator:
        """
        Task D, with a specified maze generator.
        A solver is provided, and you can access the particular solver by calling its name() method.

        @param solver: Instance of a maze solver you should generate a maze to maximize the number of cells it explores.
        
        @return: Instance of a maze generator.
        """
        generator: MazeGenerator = None
        solver_name = solver.getName()

        if solver_name == 'recur':
            generator = TaskDMazeGenerator(solver_name)
        elif solver_name == 'wall':
            generator = TaskDMazeGenerator(solver_name)
        elif solver_name == 'pledge':
            generator = TaskDMazeGenerator(solver_name)
        elif solver_name == 'taskC':
            generator = TaskDMazeGenerator(solver_name)
        else:
            generator = TaskDMazeGenerator(solver_name)

        return generator
