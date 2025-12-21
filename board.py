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

    # Horizontal movement (moving left or right, same row)
    if x1 != x2:
        # Check for vertical walls between the two columns
        left = min(x1, x2)
        y = y1
        # A vertical wall at (left, y) blocks movement from (left, y) to (left+1, y)
        # But it also blocks movement from (left, y-1) to (left+1, y-1) if y > 0
        # So we need to check both (left, y) and (left, y-1)
        return ("V", left, y) in walls or (y > 0 and ("V", left, y - 1) in walls)

    # Vertical movement (moving up or down, same column)
    if y1 != y2:
        # Check for horizontal walls between the two rows
        x = x1
        top = min(y1, y2)
        # A horizontal wall at (x, top) blocks movement from (x, top) to (x, top+1)
        # But it also blocks movement from (x-1, top) to (x-1, top+1) if x > 0
        # So we need to check both (x, top) and (x-1, top)
        return ("H", x, top) in walls or (x > 0 and ("H", x - 1, top) in walls)

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
                    and not wall_blocks_move(game_state.walls, (x, y), (sx, sy))  # Also check from current position
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

    # Cannot cross walls - check BOTH directions for adjacent walls
    if orientation == "H":
        # Check horizontal wall to the right
        if ("H", x+1, y) in game_state.walls:
            return False
        # Check horizontal wall to the left
        if ("H", x-1, y) in game_state.walls:
            return False
    else:  # vertical
        # Check vertical wall below
        if ("V", x, y+1) in game_state.walls:
            return False
        # Check vertical wall above
        if ("V", x, y-1) in game_state.walls:
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
    visited = set([start])
    q = deque([start])

    while q:
        x, y = q.popleft()

        if y == player.goal_row:
            return True  # valid path found

        # Check all 4 directions without considering opponent blocking
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited:
                continue
            if not is_on_board(nx, ny):
                continue
            if wall_blocks_move(game_state.walls, (x, y), (nx, ny)):
                continue
            
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


# ─────────────────────────────────────────────
#  GAME CLASS
# ─────────────────────────────────────────────

class Game:
    """
    Main game controller that handles:
    - Turn management
    - Move execution (move_pawn, place_wall)
    - Win detection
    - Undo/redo integration
    """
    
    def __init__(self):
        self.state = GameState()
        self.history = History()
        self.winner = None  # None, 0, or 1
        
    def reset(self):
        """Reset the game to initial state."""
        self.state = GameState()
        self.history = History()
        self.winner = None
        
    def move_pawn(self, new_pos):
        """
        Execute a pawn move for the current player.
        Returns True if move was successful, False otherwise.
        """
        if self.winner is not None:
            return False  # Game already over
            
        # Save state before move for undo
        self.history.push(self.state)
        
        # Attempt the move
        success = make_move(self.state, new_pos)
        
        if success:
            # Check for win condition
            self._check_winner()
        else:
            # Move failed, remove from history
            self.history.undo_stack.pop()
            
        return success
    
    def place_wall(self, x, y, orientation):
        """
        Place a wall for the current player.
        Returns True if placement was successful, False otherwise.
        """
        if self.winner is not None:
            return False  # Game already over
            
        # Save state before action for undo
        self.history.push(self.state)
        
        # Attempt wall placement
        success = place_wall(self.state, x, y, orientation)
        
        if not success:
            # Placement failed, remove from history
            self.history.undo_stack.pop()
            
        return success
    
    def undo(self):
        """
        Undo the last move.
        Returns True if undo was successful, False if no moves to undo.
        """
        previous_state = self.history.undo(self.state)
        
        if previous_state is not None:
            self.state = previous_state
            self.winner = None  # Reset winner on undo
            return True
        
        return False
    
    def redo(self):
        """
        Redo a previously undone move.
        Returns True if redo was successful, False if no moves to redo.
        """
        next_state = self.history.redo(self.state)
        
        if next_state is not None:
            self.state = next_state
            # Re-check winner after redo
            self._check_winner()
            return True
        
        return False
    
    def _check_winner(self):
        """Check if any player has won."""
        for i, player in enumerate(self.state.players):
            x, y = player.pos
            if y == player.goal_row:
                self.winner = i
                return
    
    def get_current_player(self):
        """Returns the index of the current player (0 or 1)."""
        return self.state.current_player
    
    def get_walls_left(self, player_index):
        """Returns number of walls remaining for a player."""
        return self.state.players[player_index].walls_left
    
    def get_valid_moves_for_current_player(self):
        """Returns list of valid moves for the current player."""
        return get_valid_moves(self.state, self.state.current_player)
    
    def is_game_over(self):
        """Returns True if the game has ended."""
        return self.winner is not None
    
    def get_winner(self):
        """Returns the winner (0, 1, or None)."""
        return self.winner


# ─────────────────────────────────────────────
#  CLI TESTING INTERFACE
# ─────────────────────────────────────────────

def print_board(game):
    """Simple CLI visualization for testing."""
    state = game.state
    print("\n" + "="*40)
    print(f"Player {game.get_current_player()}'s turn")
    print(f"Walls: P0={game.get_walls_left(0)}, P1={game.get_walls_left(1)}")
    
    if game.is_game_over():
        print(f"*** PLAYER {game.get_winner()} WINS! ***")
    
    print("="*40)
    
    # Simple grid representation
    for y in range(BOARD_SIZE):
        row = ""
        for x in range(BOARD_SIZE):
            pos = (x, y)
            if pos == state.players[0].pos:
                row += " 0 "
            elif pos == state.players[1].pos:
                row += " 1 "
            else:
                row += " . "
        print(row)
    print()


def test_game():
    """Basic CLI test for game functionality."""
    game = Game()
    
    print("Quoridor Game - CLI Test")
    print("Commands: move x y | wall x y H/V | undo | redo | quit")
    
    while True:
        print_board(game)
        
        if game.is_game_over():
            play_again = input("Play again? (y/n): ")
            if play_again.lower() == 'y':
                game.reset()
                continue
            else:
                break
        
        cmd = input("> ").strip().split()
        
        if not cmd:
            continue
            
        if cmd[0] == "quit":
            break
        elif cmd[0] == "move" and len(cmd) == 3:
            x, y = int(cmd[1]), int(cmd[2])
            if game.move_pawn((x, y)):
                print("✓ Move successful")
            else:
                print("✗ Invalid move")
        elif cmd[0] == "wall" and len(cmd) == 4:
            x, y = int(cmd[1]), int(cmd[2])
            orientation = cmd[3].upper()
            if game.place_wall(x, y, orientation):
                print("✓ Wall placed")
            else:
                print("✗ Invalid wall placement")
        elif cmd[0] == "undo":
            if game.undo():
                print("✓ Undone")
            else:
                print("✗ Nothing to undo")
        elif cmd[0] == "redo":
            if game.redo():
                print("✓ Redone")
            else:
                print("✗ Nothing to redo")
        else:
            print("Unknown command")


if __name__ == "__main__":
    test_game()
