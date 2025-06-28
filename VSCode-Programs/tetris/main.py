import pygame
from tetris.game import Game

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

def main():
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris")
    
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        game.run()

if __name__ == "__main__":
    main()
