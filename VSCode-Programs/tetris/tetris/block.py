class Block:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = (0, 255, 0)
        self.rotation = 0

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def move_down(self):
        self.y += 1

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)
        self.shape = self.get_rotated_shape()

    def get_rotated_shape(self):
        return [list(x[::-1]) for x in zip(*self.shape)]

    def draw(self, screen, block_size):
        for y, row in enumerate(self.shape):
            for x, col in enumerate(row):
                if col:
                    pygame.draw.rect(screen, self.color,
                                     (self.x * block_size + x * block_size,
                                      self.y * block_size + y * block_size,
                                      block_size, block_size), 0)
