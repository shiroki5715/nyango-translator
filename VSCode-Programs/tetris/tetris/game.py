import pygame
from tetris.block import Block

class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(200, 50)
        self.width, self.height = 13 * 22, 22 * 22
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.game_over = False

        # Create a new block
        self.block = Block(5, 0, [[[1, 1, 1, 1]]])  # Example block

    def draw_grid(self):
        self.screen.fill((255, 255, 255))  # White background
        for x in range(13):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (x * 22, 0), (x * 22, self.height))
        for y in range(22):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (0, y * 22), (self.width, y * 22))

    def run(self):
        # This is the game loop
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.block.move_left()
                    if event.key == pygame.K_RIGHT:
                        self.block.move_right()
                    if event.key == pygame.K_DOWN:
                        self.block.move_down()
                    if event.key == pygame.K_UP:
                        self.block.rotate()

            # Update the block position
            self.block.move_down()

            self.draw_grid()

            # Draw the block
            self.draw_block()

            pygame.display.update()
            self.clock.tick(60)  # Limit the frame rate to 60 FPS
