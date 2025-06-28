import pygame
from settings import WIDTH, HEIGHT, FPS
from sprites import Player
from level import LevelManager

def main():
    # 初期化
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Galaxy Defender")
    clock = pygame.time.Clock()

    # グループ
    all_sprites = pygame.sprite.Group()
    enemies      = pygame.sprite.Group()
    bullets      = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    level_mgr = LevelManager(enemies, all_sprites)
    score = 0
    running = True

    # -------- ゲームループ --------
    while running:
        clock.tick(FPS)

        # --- イベント処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.shoot(bullets, all_sprites)

        # --- 更新 ---
        all_sprites.update()
        level_mgr.update()

        # 衝突判定
        for _ in pygame.sprite.groupcollide(enemies, bullets, True, True):
            score += 1
            if score % 20 == 0:
                level_mgr.next_level()

        if pygame.sprite.spritecollideany(player, enemies):
            running = False     # Game Over

        # --- 描画 ---
        screen.fill((0, 0, 30))
        all_sprites.draw(screen)

        font = pygame.font.SysFont("consolas", 20)
        info = font.render(f"Score: {score}  Level: {level_mgr.level}", True, (255, 255, 255))
        screen.blit(info, (10, 10))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
