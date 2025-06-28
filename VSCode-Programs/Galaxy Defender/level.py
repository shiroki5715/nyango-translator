import pygame, random
from sprites import Enemy
from settings import WIDTH

class LevelManager:
    """レベルごとに敵を出現させるクラス"""
    def __init__(self, enemy_group, all_sprites):
        self.enemy_group = enemy_group
        self.all_sprites = all_sprites
        self.level = 1
        self.spawn_delay = 1500   # ms
        self.last_spawn = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_spawn > self.spawn_delay:
            self.spawn_wave()
            self.last_spawn = now

    def spawn_wave(self):
        for _ in range(self.level + 4):
            x = random.randint(0, WIDTH - 30)
            y = random.randint(-100, -40)
            speed = random.randint(2, 4) + self.level // 2
            enemy = Enemy(x, y, speed)
            self.enemy_group.add(enemy)
            self.all_sprites.add(enemy)

    def next_level(self):
        self.level += 1
        self.spawn_delay = max(300, 1500 - self.level * 100)
