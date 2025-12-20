import pygame
from src.gui import QuoridorGUI

def main():
    pygame.init()
    game = QuoridorGUI()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()