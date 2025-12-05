from copy import deepcopy
from collections import deque

BOARD_SIZE = 9


# ─────────────────────────────────────────────
#  PLAYER & GAME STATE
# ─────────────────────────────────────────────

class Player:
    def __init__(self, start_pos, goal_row):
        self.pos = start_pos
        self.goal_row = goal_row
        self.walls_left = 10


class GameState:
    """Stores everything needed for a full game snapshot."""

    def __init__(self):
        self.players = [
            Player(start_pos=(4, 0), goal_row=8),  # Player 0 (top)
            Player(start_pos=(4, 8), goal_row=0),  # Player 1 (bottom)
        ]
        self.walls = []          # Walls stored as tuples: (x, y, orientation)
                                 # orientation = "H" or "V"
        self.current_player = 0  # 0 or 1


# ─────────────────────────────────────────────
#  HISTORY (UNDO / REDO)
# ─────────────────────────────────────────────

class History:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def push(self, game_state):
        self.undo_stack.append(deepcopy(game_state))
        self.redo_stack.clear()  # New action = redo history cleared

    def undo(self, game_state):
        if not self.undo_stack:
            return None
        self.redo_stack.append(deepcopy(game_state))
        return self.undo_stack.pop()

    def redo(self, game_state):
        if not self.redo_stack:
            return None
        self.undo_stack.append(deepcopy(game_state))
        return self.redo_stack.pop()


# ─────────────────────────────────────────────
#  MOVEMENT LOGIC
# ─────────────────────────────────────────────

def is_on_board(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE


def wall_blocks_move(walls, from_pos, to_pos):
    """Checks if a wall physically blocks a movement."""

    x1, y1 = from_pos
    x2, y2 = to_pos

    # Horizontal movement
    if x1 != x2:   ##so the move is horizontal (same y), then we check for vertical walls
        left = min(x1, x2)
        y = y1
        return ("V", left, y) in walls  ##if there is a vertical wall at that position, return True, so there is a block


    # Vertical movement
    if y1 != y2:  ##so the move is vertical (same x), then we check for horizontal walls
        x = x1
        top = min(y1, y2)
        return ("H", x, top) in walls  ##if there is a horizontal wall at that position, return True, so there is a block

    return False


def get_valid_moves(game_state, player_index):
    p = game_state.players[player_index]
    opponent = game_state.players[1 - player_index]

    moves = []
    x, y = p.pos
    ox, oy = opponent.pos

    # 4 basic directions
    directions = [(1,0), (-1,0), (0,1), (0,-1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy      ##new position after moving in that direction
        if not is_on_board(nx, ny):  ##check if new position is on board
            continue
        if wall_blocks_move(game_state.walls, (x, y), (nx, ny)): ##check if there is a wall that blocks the move
            continue

        # If not stepping on opponent → valid
        if (nx, ny) != (ox, oy):
            moves.append((nx, ny))
            continue

        # If stepping on opponent → try jump
        jx, jy = ox + dx, oy + dy
        if (
            is_on_board(jx, jy)
            and not wall_blocks_move(game_state.walls, (ox, oy), (jx, jy))
        ):
            moves.append((jx, jy))
        else:
            # Side diagonal steps if direct jump is blocked
            side1 = (ox + dy, oy + dx)
            side2 = (ox - dy, oy - dx)
            for sx, sy in (side1, side2):
                if (
                    is_on_board(sx, sy)
                    and not wall_blocks_move(game_state.walls, (ox, oy), (sx, sy))
                ):
                    moves.append((sx, sy))

    return moves


# ─────────────────────────────────────────────
#  WALL RULES & PATH VALIDATION
# ─────────────────────────────────────────────

def is_valid_wall_placement(game_state, x, y, orientation):
    """Checks if a wall is legal."""

    # Invalid coordinates
    if x < 0 or y < 0 or x >= BOARD_SIZE-1 or y >= BOARD_SIZE-1:
        return False

    wall = (orientation, x, y)

    # Cannot overlap existing walls
    if wall in game_state.walls:
        return False

    # Cannot cross walls
    if orientation == "H":
        if ("H", x+1, y) in game_state.walls:  ##we check the next block in the x direction to have a wall 
            return False
    else:  # vertical
        if ("V", x, y+1) in game_state.walls:  ##we check the next block in the y direction to have a wall
            return False 

    # Temporarily place the wall to check paths
    game_state.walls.append(wall)

    ok = True
    for p in game_state.players:
        if not has_path_to_goal(game_state, p):
            ok = False
            break

    # Remove temporary wall
    game_state.walls.remove(wall)

    return ok


def has_path_to_goal(game_state, player):
    """BFS to ensure player has at least one path."""
    start = player.pos
    visited = set()
    q = deque([start])

    while q:
        x, y = q.popleft()

        if y == player.goal_row:
            return True  # valid path found

        for nx, ny in get_valid_moves(game_state, game_state.players.index(player)):
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                q.append((nx, ny))

    return False


# ─────────────────────────────────────────────
#  APPLY MOVES
# ─────────────────────────────────────────────

def make_move(game_state, new_pos):
    """Moves the pawn if legal."""
    moves = get_valid_moves(game_state, game_state.current_player)
    if new_pos in moves:
        game_state.players[game_state.current_player].pos = new_pos
        game_state.current_player = 1 - game_state.current_player
        return True
    return False


def place_wall(game_state, x, y, orientation):
    """Places a wall if legal."""
    p = game_state.players[game_state.current_player]

    if p.walls_left <= 0:
        return False

    if not is_valid_wall_placement(game_state, x, y, orientation):
        return False

    game_state.walls.append((orientation, x, y))
    p.walls_left -= 1
    game_state.current_player = 1 - game_state.current_player
    return True
