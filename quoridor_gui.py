import pygame
import sys
from board import Game, BOARD_SIZE
from ai import QuoridorAI
# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900
CELL_SIZE = 60
GAP_SIZE = 0
BOARD_OFFSET_X = 100
BOARD_OFFSET_Y = 100
WALL_THICKNESS = 8
WALL_VISUAL_LENGTH = CELL_SIZE * 2 - 8
WALL_OFFSET = 4

# Colors
COLOR_BACKGROUND = (245, 245, 220)
COLOR_BOARD = (139, 69, 19)
COLOR_CELL = (222, 184, 135)
COLOR_PLAYER1 = (255, 0, 0)
COLOR_PLAYER2 = (0, 0, 255)
COLOR_WALL = (0, 0, 0)
COLOR_VALID_MOVE = (0, 255, 0, 100)
COLOR_WALL_PREVIEW = (128, 128, 128, 150)
COLOR_TEXT = (0, 0, 0)
COLOR_BUTTON = (100, 150, 200)
COLOR_BUTTON_HOVER = (120, 170, 220)
COLOR_GOAL_P1 = (255, 200, 200)
COLOR_GOAL_P2 = (200, 200, 255)

# Game settings
FPS = 60


class Button:
    
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_TEXT, self.rect, 2, border_radius=5)
        
        text_surface = font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


class QuoridorGUI:
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Quoridor Game")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game instance
        self.game = Game()
        self.ai = None  # Will be set if playing against AI
        self.game_mode = None  # "pvp" or "ai"
        self.ai_difficulty = None  # "easy", "medium", or "hard"
        
        # UI state
        self.wall_preview = None  # (x, y, orientation) or None
        self.message = "Player 1's turn"
        self.show_valid_moves = False
        
        # Buttons (positioned below the board)
        self.reset_button = Button(50, 750, 150, 50, "New Game", COLOR_BUTTON, COLOR_BUTTON_HOVER)
        self.undo_button = Button(220, 750, 100, 50, "Undo", COLOR_BUTTON, COLOR_BUTTON_HOVER)
        self.redo_button = Button(340, 750, 100, 50, "Redo", COLOR_BUTTON, COLOR_BUTTON_HOVER)
        self.mode_button = Button(460, 750, 100, 50, "Mode", COLOR_BUTTON, COLOR_BUTTON_HOVER)
        
        # Mode selection screen
        self.selecting_mode = True
        self.mode_buttons = {
            "pvp": Button(250, 300, 300, 60, "Player vs Player", COLOR_BUTTON, COLOR_BUTTON_HOVER),
            "ai_easy": Button(250, 380, 300, 60, "vs AI (Easy)", COLOR_BUTTON, COLOR_BUTTON_HOVER),
            "ai_medium": Button(250, 460, 300, 60, "vs AI (Medium)", COLOR_BUTTON, COLOR_BUTTON_HOVER),
            "ai_hard": Button(250, 540, 300, 60, "vs AI (Hard)", COLOR_BUTTON, COLOR_BUTTON_HOVER),
        }
        
    def board_to_screen(self, x, y):
        screen_x = BOARD_OFFSET_X + x * (CELL_SIZE + GAP_SIZE)
        screen_y = BOARD_OFFSET_Y + y * (CELL_SIZE + GAP_SIZE)
        return screen_x, screen_y
    
    def screen_to_board(self, screen_x, screen_y):
        x = (screen_x - BOARD_OFFSET_X) // (CELL_SIZE + GAP_SIZE)
        y = (screen_y - BOARD_OFFSET_Y) // (CELL_SIZE + GAP_SIZE)
        return x, y
    
    def get_wall_at_mouse(self, mouse_pos):
        mx, my = mouse_pos
        best_wall = None
        best_dist = float('inf')
        detection_tolerance = 15
        
        # Horizontal walls
        for x in range(BOARD_SIZE - 1):
            for y in range(BOARD_SIZE - 1):
                sx, sy = self.board_to_screen(x, y)
                wall_y = sy + CELL_SIZE
                wall_x_start = sx
                wall_x_end = sx + CELL_SIZE * 2
                
                if wall_x_start <= mx <= wall_x_end and abs(my - wall_y) < detection_tolerance:
                    dist = abs(my - wall_y)
                    if dist < best_dist:
                        best_dist = dist
                        best_wall = (x, y, "H")
        
        # Vertical walls
        for x in range(BOARD_SIZE - 1):
            for y in range(BOARD_SIZE - 1):
                sx, sy = self.board_to_screen(x, y)
                wall_x = sx + CELL_SIZE
                wall_y_start = sy
                wall_y_end = sy + CELL_SIZE * 2
                
                if wall_y_start <= my <= wall_y_end and abs(mx - wall_x) < detection_tolerance:
                    dist = abs(mx - wall_x)
                    if dist < best_dist:
                        best_dist = dist
                        best_wall = (x, y, "V")
        
        return best_wall
    
    def draw_board(self):
        for x in range(BOARD_SIZE):
            sx, sy = self.board_to_screen(x, 8)
            pygame.draw.rect(self.screen, COLOR_GOAL_P1, (sx, sy, CELL_SIZE, CELL_SIZE))
            
            sx, sy = self.board_to_screen(x, 0)
            pygame.draw.rect(self.screen, COLOR_GOAL_P2, (sx, sy, CELL_SIZE, CELL_SIZE))
        
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                sx, sy = self.board_to_screen(x, y)
                pygame.draw.rect(self.screen, COLOR_CELL, (sx, sy, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, COLOR_BOARD, (sx, sy, CELL_SIZE, CELL_SIZE), 2)
    
    def draw_walls(self):
        for orientation, x, y in self.game.state.walls:
            sx, sy = self.board_to_screen(x, y)
            
            if orientation == "H":
                start_x = sx + WALL_OFFSET
                start_y = sy + CELL_SIZE - WALL_THICKNESS // 2
                pygame.draw.rect(self.screen, COLOR_WALL, (start_x, start_y, WALL_VISUAL_LENGTH, WALL_THICKNESS))
            else:
                start_x = sx + CELL_SIZE - WALL_THICKNESS // 2
                start_y = sy + WALL_OFFSET
                pygame.draw.rect(self.screen, COLOR_WALL, (start_x, start_y, WALL_THICKNESS, WALL_VISUAL_LENGTH))
    
    def draw_wall_preview(self):
        if self.wall_preview is None:
            return
        
        x, y, orientation = self.wall_preview
        current_player = self.game.get_current_player()
        if self.game.get_walls_left(current_player) <= 0:
            return
        
        sx, sy = self.board_to_screen(x, y)
        
        if orientation == "H":
            start_x = sx + WALL_OFFSET
            start_y = sy + CELL_SIZE - WALL_THICKNESS // 2
            pygame.draw.rect(self.screen, COLOR_WALL_PREVIEW, (start_x, start_y, WALL_VISUAL_LENGTH, WALL_THICKNESS))
        else:
            start_x = sx + CELL_SIZE - WALL_THICKNESS // 2
            start_y = sy + WALL_OFFSET
            pygame.draw.rect(self.screen, COLOR_WALL_PREVIEW, (start_x, start_y, WALL_THICKNESS, WALL_VISUAL_LENGTH))
    
    def draw_pawns(self):
        for i, player in enumerate(self.game.state.players):
            x, y = player.pos
            sx, sy = self.board_to_screen(x, y)
            color = COLOR_PLAYER1 if i == 0 else COLOR_PLAYER2
            center = (sx + CELL_SIZE // 2, sy + CELL_SIZE // 2)
            
            pygame.draw.circle(self.screen, color, center, CELL_SIZE // 3)
            pygame.draw.circle(self.screen, COLOR_TEXT, center, CELL_SIZE // 3, 2)
            
            text = self.font_medium.render(str(i + 1), True, (255, 255, 255))
            text_rect = text.get_rect(center=center)
            self.screen.blit(text, text_rect)
    
    def draw_valid_moves(self):
        if not self.show_valid_moves:
            return
        
        valid_moves = self.game.get_valid_moves_for_current_player()
        highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(COLOR_VALID_MOVE)
        
        for x, y in valid_moves:
            sx, sy = self.board_to_screen(x, y)
            self.screen.blit(highlight_surface, (sx, sy))
    
    def draw_ui(self):
        title = self.font_large.render("QUORIDOR", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title, title_rect)
        
        p1_walls = self.game.get_walls_left(0)
        p2_walls = self.game.get_walls_left(1)
        
        p1_text = self.font_medium.render(f"Player 1", True, COLOR_PLAYER1)
        p1_walls_text = self.font_small.render(f"Walls: {p1_walls}", True, COLOR_TEXT)
        self.screen.blit(p1_text, (50, 650))
        self.screen.blit(p1_walls_text, (50, 690))
        
        p2_text = self.font_medium.render(f"Player 2", True, COLOR_PLAYER2)
        p2_walls_text = self.font_small.render(f"Walls: {p2_walls}", True, COLOR_TEXT)
        p2_text_rect = p2_text.get_rect(topright=(SCREEN_WIDTH - 50, 650))
        p2_walls_rect = p2_walls_text.get_rect(topright=(SCREEN_WIDTH - 50, 690))
        self.screen.blit(p2_text, p2_text_rect)
        self.screen.blit(p2_walls_text, p2_walls_rect)
        
        if not self.game.is_game_over():
            current = self.game.get_current_player()
            turn_color = COLOR_PLAYER1 if current == 0 else COLOR_PLAYER2
            turn_text = self.font_medium.render("<<", True, turn_color)
            if current == 0:
                arrow = "<<"
                turn_text = self.font_medium.render(arrow, True, turn_color)
                self.screen.blit(turn_text, (180, 655))
            else:
                arrow = ">>"
                turn_text = self.font_medium.render(arrow, True, turn_color)
                turn_rect = turn_text.get_rect(topright=(SCREEN_WIDTH - 180, 655))
                self.screen.blit(turn_text, turn_rect)
        
        # Message
        message_text = self.font_small.render(self.message, True, COLOR_TEXT)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 820))
        self.screen.blit(message_text, message_rect)
        
        # Instructions
        instr = "Left Click: Move | Right Click: Place Wall"
        instr_text = self.font_small.render(instr, True, COLOR_TEXT)
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, 850))
        self.screen.blit(instr_text, instr_rect)
        
        # Buttons
        self.reset_button.draw(self.screen, self.font_small)
        self.undo_button.draw(self.screen, self.font_small)
        self.redo_button.draw(self.screen, self.font_small)
        self.mode_button.draw(self.screen, self.font_small)
    
    def draw_mode_selection(self):
        self.screen.fill(COLOR_BACKGROUND)
        
        title = self.font_large.render("QUORIDOR", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Select Game Mode", True, COLOR_TEXT)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)
        
        for button in self.mode_buttons.values():
            button.draw(self.screen, self.font_medium)
    
    def handle_mode_selection(self, event):
        for mode, button in self.mode_buttons.items():
            if button.handle_event(event):
                if mode == "pvp":
                    self.game_mode = "pvp"
                    self.ai = None
                else:
                    self.game_mode = "ai"
                    difficulty = mode.replace("ai_", "")
                    self.ai_difficulty = difficulty
                    self.ai = QuoridorAI(player_index=1, difficulty=difficulty)
                
                self.selecting_mode = False
                self.game.reset()
                self.update_message()
                return
        
        for button in self.mode_buttons.values():
            button.handle_event(event)
    
    def handle_click(self, pos, button):
        if self.game.is_game_over():
            return
        
        x, y = self.screen_to_board(pos[0], pos[1])
        
        if button == 1:
            if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
                if self.game.move_pawn((x, y)):
                    self.update_message()
                    if self.game_mode == "ai" and not self.game.is_game_over():
                        pygame.time.set_timer(pygame.USEREVENT + 1, 500)
                else:
                    self.message = "Invalid move!"
        
        elif button == 3:
            wall_pos = self.get_wall_at_mouse(pos)
            if wall_pos:
                wx, wy, orientation = wall_pos
                if self.game.place_wall(wx, wy, orientation):
                    self.update_message()
                    if self.game_mode == "ai" and not self.game.is_game_over():
                        pygame.time.set_timer(pygame.USEREVENT + 1, 500)
                else:
                    self.message = "Invalid wall placement!"
    
    def execute_ai_move(self):
        if self.ai is None or self.game.is_game_over():
            return
        if self.game.get_current_player() != self.ai.player_index:
            return
        
        move = self.ai.get_move(self.game.state)
        if move:
            move_type, move_data = move
            if move_type == "pawn":
                self.game.move_pawn(move_data)
            elif move_type == "wall":
                x, y, orientation = move_data
                self.game.place_wall(x, y, orientation)
            self.update_message()
    
    def update_message(self):
        if self.game.is_game_over():
            winner = self.game.get_winner()
            self.message = f"Player {winner + 1} wins!"
        else:
            current = self.game.get_current_player()
            self.message = f"Player {current + 1}'s turn"
    
    def handle_button_events(self, event):
        if self.reset_button.handle_event(event):
            self.selecting_mode = True
            self.game.reset()
            self.update_message()
            return True
        
        if self.undo_button.handle_event(event):
            if self.game.undo():
                if self.game_mode == "ai" and self.game.get_current_player() == self.ai.player_index:
                    self.game.undo()
                self.update_message()
            return True
        
        if self.redo_button.handle_event(event):
            if self.game.redo():
                self.update_message()
            return True
        
        if self.mode_button.handle_event(event):
            self.selecting_mode = True
            return True
        
        return False
    
    def run(self):
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.selecting_mode:
                    self.handle_mode_selection(event)
                    continue
                
                if self.handle_button_events(event):
                    continue
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button)
                
                if event.type == pygame.MOUSEMOTION:
                    x, y = self.screen_to_board(event.pos[0], event.pos[1])
                    current_player = self.game.get_current_player()
                    pawn_pos = self.game.state.players[current_player].pos
                    
                    self.show_valid_moves = (x, y) == pawn_pos
                    self.wall_preview = self.get_wall_at_mouse(event.pos)
                
                if event.type == pygame.USEREVENT + 1:
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                    self.execute_ai_move()
            
            self.screen.fill(COLOR_BACKGROUND)
            
            if self.selecting_mode:
                self.draw_mode_selection()
            else:
                self.draw_board()
                self.draw_walls()
                self.draw_wall_preview()
                self.draw_valid_moves()
                self.draw_pawns()
                self.draw_ui()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    gui = QuoridorGUI()
    gui.run()
