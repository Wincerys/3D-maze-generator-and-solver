from solving.recurBackMazeSolver import RecurBackMazeSolver
from solving.wallFollowingSolver import WallFollowingMazeSolver
from solving.pledgeSolver import PledgeMazeSolver
from solving.taskCMazeSolver import TaskCMazeSolver
from solving.mazeSolver import MazeSolver


class SolverSelector:
    """
    Class used to select and construct appropriate maze solver.
    """


    def construct(self, solverApproach: str)->MazeSolver:
        """
        Task A, B and D, with a specified maze generator.
        If solverApproach is unknown, None will be returned.

        @param solverApproach: Name of solver to use.
        
        @return: Instance of a maze generator.
        """
        solver: MazeSolver = None

        if solverApproach == 'recur':
            solver = RecurBackMazeSolver()
        elif solverApproach == 'wall':
            solver = WallFollowingMazeSolver()
        elif solverApproach == 'pledge':
            solver = PledgeMazeSolver()
        elif solverApproach == 'taskC':
            solver = TaskCMazeSolver()
        # TODO: If you implement other solvers, you can add them here

        return solver
    

 


