from typing import List, Tuple
from collections import deque
from maze.util import Coordinates3D
from maze.maze3D import Maze3D
from solving.mazeSolver import MazeSolver

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


class PledgeMazeSolver(MazeSolver):
    """
    Pledge algorithm solver with BFS fallback.

    MODE 1 (angle == 0): Walk straight in chosen_dir until hitting a wall.
    MODE 2 (angle != 0): Right-hand wall following with angle tracking.
        right turn -> angle += 1
        left  turn -> angle -= 1
    When angle returns to 0, switch back to MODE 1.

    If a (cell, facing, angle) state repeats (cycle detected), falls back
    to BFS to guarantee termination.
    """

    def __init__(self):
        super().__init__()
        self.m_name = "pledge"

    def getName(self):
        return self.m_name

    def _is_interior(self, maze: Maze3D, cell: Coordinates3D) -> bool:
        lv = cell.getLevel()
        if lv < 0 or lv >= maze.levelNum():
            return False
        r, c = cell.getRow(), cell.getCol()
        return 0 <= r < maze.rowNum(lv) and 0 <= c < maze.colNum(lv)

    def _try_move(self, maze: Maze3D, current: Coordinates3D,
                  direction: str, exits: set):
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

    def solveMaze(self, maze: Maze3D, entrance: Coordinates3D):
        self.m_entranceUsed = entrance
        exits = set(maze.getExits())

        # ── Enter maze: step to the adjacent interior cell ───────────────
        current = entrance
        self.solverPathAppend(entrance, False)

        chosen_dir = None
        for n in maze.neighbours(entrance):
            if not maze.hasWall(entrance, n) and self._is_interior(maze, n):
                d = direction_of(entrance, n)
                if d is not None:
                    chosen_dir = d
                    current    = n
                    self.solverPathAppend(current, False)
                    break

        if chosen_dir is None:
            return

        if current in exits:
            self.solved(entrance, current)
            return

        # ── Pledge algorithm ─────────────────────────────────────────────
        facing = chosen_dir
        angle  = 0
        seen_states = set()
        moves = 0

        total_cells = sum(
            maze.rowNum(l) * maze.colNum(l) for l in range(maze.levelNum())
        )
        # Trigger BFS fallback if we make too many moves without finding exit
        # (Pledge can revisit cells many times with different angles)
        # Lower threshold = more efficient, but less "pure" Pledge behavior
        max_moves = int(total_cells * 1.5)

        while current not in exits:
            state = (current, facing, angle)

            if state in seen_states or moves >= max_moves:
                # Cycle detected — BFS fallback
                bfs_path = self._bfs_to_exit(maze, current, exits)
                if bfs_path:
                    for cell in bfs_path[1:]:
                        current = cell
                        self.solverPathAppend(current, False)
                break

            seen_states.add(state)

            if angle == 0:
                # MODE 1: walk straight
                facing = chosen_dir
                nxt    = self._try_move(maze, current, facing, exits)
                if nxt is not None:
                    current = nxt
                    self.solverPathAppend(current, False)
                    moves += 1
                else:
                    # Hit wall — enter MODE 2
                    facing  = turn_left(facing)
                    angle  -= 1
            else:
                # MODE 2: wall following
                nxt = self._try_move(maze, current, turn_right(facing), exits)
                if nxt is not None:
                    facing  = turn_right(facing)
                    angle  += 1
                    current = nxt
                    self.solverPathAppend(current, False)
                    moves += 1
                    continue

                nxt = self._try_move(maze, current, facing, exits)
                if nxt is not None:
                    current = nxt
                    self.solverPathAppend(current, False)
                    moves += 1
                    continue

                # Turn left (-1), no move
                facing  = turn_left(facing)
                angle  -= 1

        if current in exits:
            self.solved(entrance, current)