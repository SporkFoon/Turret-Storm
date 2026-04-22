import pygame
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption('TurretStorm - Tower Defense')
    clock = pygame.time.Clock()
    import assets
    assets.load_all()
    game = Game(screen)
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                game.handle_mouse_move(event.pos)
        game.update(dt)
        game.draw()
        pygame.display.flip()
    game.stats_manager.save_to_csv()
    pygame.quit()
    sys.exit()
if __name__ == '__main__':
    main()