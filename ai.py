import random
from collections import deque
from copy import deepcopy

# ─────────────────────────────────────────────
#  AI BASE CLASS
# ─────────────────────────────────────────────

class QuoridorAI:
    """Base class for AI opponents."""
    
    def __init__(self, player_index, difficulty="medium"):
        self.player_index = player_index
        self.difficulty = difficulty.lower()
        
    def get_move(self, game_state):
        """
        Returns the AI's chosen move.
        Returns: tuple of (move_type, move_data)
        - move_type: "pawn" or "wall"
        - move_data: (x, y) for pawn, or (x, y, orientation) for wall
        """
        if self.difficulty == "easy":
            return self._easy_strategy(game_state)
        elif self.difficulty == "medium":
            return self._medium_strategy(game_state)
        elif self.difficulty == "hard":
            return self._hard_strategy(game_state)
        else:
            return self._medium_strategy(game_state)


# ─────────────────────────────────────────────
#  UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def get_shortest_path_length(game_state, player_index):
    """BFS to find shortest path to goal for a player."""
    from board import has_path_to_goal, get_valid_moves, BOARD_SIZE
    
    player = game_state.players[player_index]
    start = player.pos
    goal_row = player.goal_row
    
    visited = set([start])
    queue = deque([(start, 0)])  # (position, distance)
    
    while queue:
        (x, y), dist = queue.popleft()
        
        if y == goal_row:
            return dist
        
        # Get valid moves from current position
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited:
                continue
            if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE):
                continue
            
            # Check wall blocking
            from board import wall_blocks_move
            if wall_blocks_move(game_state.walls, (x, y), (nx, ny)):
                continue
            
            visited.add((nx, ny))
            queue.append(((nx, ny), dist + 1))
    
    return float('inf')  # No path found


def evaluate_position(game_state, player_index):
    """
    Heuristic evaluation of game state.
    Returns higher score for better positions.
    """
    my_path = get_shortest_path_length(game_state, player_index)
    opponent_path = get_shortest_path_length(game_state, 1 - player_index)
    
    # Positive score if we're closer, negative if opponent is closer
    return opponent_path - my_path


def get_all_valid_wall_placements(game_state, player_index):
    """Returns all valid wall placements for a player."""
    from board import is_valid_wall_placement, BOARD_SIZE
    
    player = game_state.players[player_index]
    if player.walls_left <= 0:
        return []
    
    valid_walls = []
    for x in range(BOARD_SIZE - 1):
        for y in range(BOARD_SIZE - 1):
            for orientation in ["H", "V"]:
                if is_valid_wall_placement(game_state, x, y, orientation):
                    valid_walls.append((x, y, orientation))
    
    return valid_walls


# ─────────────────────────────────────────────
#  EASY AI - Random with basic validation
# ─────────────────────────────────────────────

class QuoridorAI(QuoridorAI):
    
    def _easy_strategy(self, game_state):
        """
        Easy AI: Mostly random moves with slight preference for moving forward.
        - 80% of the time, moves pawn toward goal
        - 20% of the time, places random wall (if available)
        """
        from board import get_valid_moves
        
        player = game_state.players[self.player_index]
        
        # 80% chance to move pawn, 20% to place wall
        if random.random() < 0.8 or player.walls_left == 0:
            # Move pawn
            valid_moves = get_valid_moves(game_state, self.player_index)
            
            if not valid_moves:
                return None
            
            # Prefer moves that get closer to goal
            goal_row = player.goal_row
            current_y = player.pos[1]
            
            best_moves = []
            for x, y in valid_moves:
                # Check if this move brings us closer to goal
                if abs(y - goal_row) < abs(current_y - goal_row):
                    best_moves.append((x, y))
            
            # If no moves toward goal, use any valid move
            if not best_moves:
                best_moves = valid_moves
            
            chosen_move = random.choice(best_moves)
            return ("pawn", chosen_move)
        
        else:
            # Place wall randomly
            valid_walls = get_all_valid_wall_placements(game_state, self.player_index)
            
            if not valid_walls:
                # No valid walls, move instead
                valid_moves = get_valid_moves(game_state, self.player_index)
                if valid_moves:
                    return ("pawn", random.choice(valid_moves))
                return None
            
            chosen_wall = random.choice(valid_walls)
            return ("wall", chosen_wall)


# ─────────────────────────────────────────────
#  MEDIUM AI - Greedy with path consideration
# ─────────────────────────────────────────────

    def _medium_strategy(self, game_state):
        """
        Medium AI: Greedy approach with strategic thinking.
        - Always evaluates shortest paths for both players
        - Places walls to increase opponent's path
        - Moves toward goal along shortest path
        - Uses walls strategically when it gives significant advantage
        """
        from board import get_valid_moves
        
        player = game_state.players[self.player_index]
        
        # Get current path lengths
        my_current_path = get_shortest_path_length(game_state, self.player_index)
        opp_current_path = get_shortest_path_length(game_state, 1 - self.player_index)
        
        # Evaluate best pawn move
        best_pawn_move = None
        best_pawn_score = float('-inf')
        
        valid_moves = get_valid_moves(game_state, self.player_index)
        for move in valid_moves:
            # Simulate move
            temp_state = deepcopy(game_state)
            temp_state.players[self.player_index].pos = move
            
            score = evaluate_position(temp_state, self.player_index)
            if score > best_pawn_score:
                best_pawn_score = score
                best_pawn_move = move
        
        # Evaluate best wall placement (only if we have walls)
        best_wall = None
        best_wall_score = float('-inf')
        
        if player.walls_left > 0:
            valid_walls = get_all_valid_wall_placements(game_state, self.player_index)
            
            # Sample walls to check (checking all is expensive)
            sample_size = min(20, len(valid_walls))
            walls_to_check = random.sample(valid_walls, sample_size) if len(valid_walls) > sample_size else valid_walls
            
            for wall in walls_to_check:
                # Simulate wall placement
                temp_state = deepcopy(game_state)
                temp_state.walls.append((wall[2], wall[0], wall[1]))
                
                score = evaluate_position(temp_state, self.player_index)
                if score > best_wall_score:
                    best_wall_score = score
                    best_wall = wall
        
        # Decide: wall or pawn move?
        # Place wall if it gives significant advantage (>= 2 path difference improvement)
        if best_wall and best_wall_score > best_pawn_score + 1.5:
            return ("wall", best_wall)
        elif best_pawn_move:
            return ("pawn", best_pawn_move)
        
        return None


# ─────────────────────────────────────────────
#  HARD AI - Minimax with Alpha-Beta Pruning
# ─────────────────────────────────────────────

    def _hard_strategy(self, game_state):
        """
        Hard AI: Uses Minimax with Alpha-Beta pruning.
        - Looks ahead multiple moves
        - Considers both pawn moves and wall placements
        - Uses advanced evaluation function
        """
        depth = 3  # Look ahead 3 moves
        
        _, best_move = self._minimax(game_state, depth, float('-inf'), float('inf'), True)
        
        if best_move:
            return best_move
        
        # Fallback to medium strategy if minimax fails
        return self._medium_strategy(game_state)
    
    
    def _minimax(self, game_state, depth, alpha, beta, maximizing_player):
        """
        Minimax algorithm with alpha-beta pruning.
        Returns: (score, move)
        """
        from board import get_valid_moves, place_wall, make_move
        
        # Base case: depth 0 or game over
        if depth == 0:
            return evaluate_position(game_state, self.player_index), None
        
        # Check if game is over
        for i, player in enumerate(game_state.players):
            if player.pos[1] == player.goal_row:
                if i == self.player_index:
                    return 1000, None  # We won
                else:
                    return -1000, None  # Opponent won
        
        current_player_idx = self.player_index if maximizing_player else (1 - self.player_index)
        
        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            
            # Try all pawn moves
            valid_moves = get_valid_moves(game_state, current_player_idx)
            for move in valid_moves:
                temp_state = deepcopy(game_state)
                temp_state.players[current_player_idx].pos = move
                
                eval_score, _ = self._minimax(temp_state, depth - 1, alpha, beta, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = ("pawn", move)
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            
            # Try wall placements (sample to keep it fast)
            if game_state.players[current_player_idx].walls_left > 0:
                valid_walls = get_all_valid_wall_placements(game_state, current_player_idx)
                sample_size = min(10, len(valid_walls))
                walls_to_check = random.sample(valid_walls, sample_size) if len(valid_walls) > sample_size else valid_walls
                
                for wall in walls_to_check:
                    temp_state = deepcopy(game_state)
                    temp_state.walls.append((wall[2], wall[0], wall[1]))
                    temp_state.players[current_player_idx].walls_left -= 1
                    
                    eval_score, _ = self._minimax(temp_state, depth - 1, alpha, beta, False)
                    
                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_move = ("wall", wall)
                    
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
            
            return max_eval, best_move
        
        else:  # Minimizing player
            min_eval = float('inf')
            best_move = None
            
            # Try all pawn moves
            valid_moves = get_valid_moves(game_state, current_player_idx)
            for move in valid_moves:
                temp_state = deepcopy(game_state)
                temp_state.players[current_player_idx].pos = move
                
                eval_score, _ = self._minimax(temp_state, depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = ("pawn", move)
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            # Try wall placements (sample)
            if game_state.players[current_player_idx].walls_left > 0:
                valid_walls = get_all_valid_wall_placements(game_state, current_player_idx)
                sample_size = min(10, len(valid_walls))
                walls_to_check = random.sample(valid_walls, sample_size) if len(valid_walls) > sample_size else valid_walls
                
                for wall in walls_to_check:
                    temp_state = deepcopy(game_state)
                    temp_state.walls.append((wall[2], wall[0], wall[1]))
                    temp_state.players[current_player_idx].walls_left -= 1
                    
                    eval_score, _ = self._minimax(temp_state, depth - 1, alpha, beta, True)
                    
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = ("wall", wall)
                    
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
            
            return min_eval, best_move