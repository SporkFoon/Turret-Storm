"""
TurretStorm - Tower Defense Game
A complete tower defense game built with Pygame featuring:
- Multiple tower types with upgrades
- Wave-based enemy spawning with increasing difficulty
- In-game economy (gold system)
- Full statistics collection and visualization
- OOP design with 5+ classes

Controls:
- Click on grass tiles to place towers
- Press 1/2/3 to select tower type (Arrow/Cannon/Ice)
- Press U to upgrade selected tower
- Press S to sell selected tower
- Press SPACE to start next wave
- Press TAB to view statistics dashboard
- Press ESC to quit
"""

import pygame
import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("TurretStorm - Tower Defense")
    clock = pygame.time.Clock()

    # Load sprite assets now that a display is available.
    import assets
    assets.load_all()

    game = Game(screen)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds

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

if __name__ == "__main__":
    main()
