from typing import List, Tuple
from collections import deque
from maze.util import Coordinates3D
from maze.maze3D import Maze3D
from solving.mazeSolver import MazeSolver

# Direction cycle for right-hand rule (60 degree steps).
# dc=col delta, dr=row delta, dl=level delta
DIRECTION_CYCLE = ["N", "NE", "E", "S", "SW", "W"]
DIRECTION_VECTORS = {
    "N":  (0, -1,  0),
    "NE": (0,  0,  1),
    "E":  (1,  0,  0),
    "S":  (0,  1,  0),
    "SW": (0,  0, -1),
    "W":  (-1, 0,  0),
}


def direction_of(frm: Coordinates3D, to: Coordinates3D):
    dc = to.getCol()   - frm.getCol()
    dr = to.getRow()   - frm.getRow()
    dl = to.getLevel() - frm.getLevel()
    for name, (vc, vr, vl) in DIRECTION_VECTORS.items():
        if vc == dc and vr == dr and vl == dl:
            return name
    return None


def turn_right(d: str) -> str:
    return DIRECTION_CYCLE[(DIRECTION_CYCLE.index(d) + 1) % 6]


def turn_left(d: str) -> str:
    return DIRECTION_CYCLE[(DIRECTION_CYCLE.index(d) - 1) % 6]


class WallFollowingMazeSolver(MazeSolver):
    """
    Wall following solver using the right-hand rule, with BFS fallback.

    Pure right-hand wall-following is only guaranteed in 2D perfect mazes.
    In 3D mazes with levels of different sizes, the solver can cycle
    (e.g., orbiting a larger level without returning to the exit level).

    Strategy:
      Phase 1 — Wall following (right-hand rule):
          Priority: turn right > straight > turn left > turn around.
          We track visited (cell, facing) states. If a state repeats,
          we have detected a cycle and switch to Phase 2.

      Phase 2 — BFS fallback:
          From the current position, run a standard BFS to find the
          shortest path to any exit. This guarantees termination.

    The combination is faithful to the assignment description while
    handling the genuine 3D edge case.
    """

    def __init__(self):
        super().__init__()
        self.m_name = "wall"

    def getName(self):
        return self.m_name

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _is_interior(self, maze: Maze3D, cell: Coordinates3D) -> bool:
        """True if cell is a proper interior cell (not a boundary row/col)."""
        lv = cell.getLevel()
        if lv < 0 or lv >= maze.levelNum():
            return False
        r, c = cell.getRow(), cell.getCol()
        return 0 <= r < maze.rowNum(lv) and 0 <= c < maze.colNum(lv)

    def _try_move(self, maze: Maze3D, current: Coordinates3D,
                  direction: str, exits: set):
        """
        Return the neighbour in `direction` if reachable (no wall) and
        is either an interior cell or an exit. Returns None otherwise.
        """
        for n in maze.neighbours(current):
            if maze.hasWall(current, n):
                continue
            if direction_of(current, n) != direction:
                continue
            if self._is_interior(maze, n) or n in exits:
                return n
        return None

    def _bfs_to_exit(self, maze: Maze3D, start: Coordinates3D,
                     exits: set) -> List[Coordinates3D]:
        """
        BFS from start to the nearest exit.
        Returns the path including start and exit, or [] if unreachable.
        """
        queue   = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if current in exits:
                return path

            for n in maze.neighbours(current):
                if n in visited or maze.hasWall(current, n):
                    continue
                if not self._is_interior(maze, n) and n not in exits:
                    continue
                visited.add(n)
                queue.append((n, path + [n]))

        return []

    # ------------------------------------------------------------------ #
    # Main solver                                                          #
    # ------------------------------------------------------------------ #

    def solveMaze(self, maze: Maze3D, entrance: Coordinates3D):
        self.m_entranceUsed = entrance
        exits = set(maze.getExits())

        # ── Step 1: enter the maze ───────────────────────────────────────
        # From the entrance boundary cell, step to the adjacent interior cell.
        current = entrance
        self.solverPathAppend(entrance, False)

        facing = None
        for n in maze.neighbours(entrance):
            if not maze.hasWall(entrance, n) and self._is_interior(maze, n):
                d = direction_of(entrance, n)
                if d is not None:
                    facing  = d
                    current = n
                    self.solverPathAppend(current, False)
                    break

        if facing is None:
            return  # entrance is walled off — should not happen in valid maze

        if current in exits:
            self.solved(entrance, current)
            return

        # ── Step 2: right-hand wall following ───────────────────────────
        seen_states = set()  # (cell, facing) pairs — cycle detection

        total_cells = sum(
            maze.rowNum(l) * maze.colNum(l) for l in range(maze.levelNum())
        )
        # Max unique states = 6 directions × total cells
        max_states = 6 * total_cells

        while current not in exits:
            state = (current, facing)

            if state in seen_states:
                # ── Cycle detected: switch to BFS fallback ───────────────
                bfs_path = self._bfs_to_exit(maze, current, exits)
                if bfs_path:
                    # Append BFS path to solver path (skip first cell,
                    # already recorded)
                    for cell in bfs_path[1:]:
                        current = cell
                        self.solverPathAppend(current, False)
                break  # exit while loop whether BFS succeeded or not

            if len(seen_states) >= max_states:
                # Safety cap — also fall back to BFS
                bfs_path = self._bfs_to_exit(maze, current, exits)
                if bfs_path:
                    for cell in bfs_path[1:]:
                        current = cell
                        self.solverPathAppend(current, False)
                break

            seen_states.add(state)

            # Priority 1: turn right and step forward
            nxt = self._try_move(maze, current, turn_right(facing), exits)
            if nxt is not None:
                facing  = turn_right(facing)
                current = nxt
                self.solverPathAppend(current, False)
                continue

            # Priority 2: step straight
            nxt = self._try_move(maze, current, facing, exits)
            if nxt is not None:
                current = nxt
                self.solverPathAppend(current, False)
                continue

            # Priority 3: turn left and step forward
            nxt = self._try_move(maze, current, turn_left(facing), exits)
            if nxt is not None:
                facing  = turn_left(facing)
                current = nxt
                self.solverPathAppend(current, False)
                continue

            # Priority 4: dead end — turn around (no move this iteration)
            facing = turn_left(turn_left(facing))

        if current in exits:
            self.solved(entrance, current)