import pygame
from settings import *

class GameMap:

    def __init__(self):
        self.grid = GAME_MAP
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.grid else 0
        self.path_tiles = set()
        self._build_path_set()

    def _build_path_set(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] in (1, 2, 3):
                    self.path_tiles.add((col, row))

    def is_buildable(self, col, row):
        if row < 0 or row >= self.rows or col < 0 or (col >= self.cols):
            return False
        return self.grid[row][col] == 0

    def pixel_to_grid(self, x, y):
        col = (x - GRID_OFFSET_X) // TILE_SIZE
        row = (y - GRID_OFFSET_Y) // TILE_SIZE
        return (col, row)

    def grid_to_pixel_center(self, col, row):
        x = GRID_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2
        y = GRID_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2
        return (x, y)

    def draw(self, surface):
        import assets
        grass_light = assets.TILES.get('grass_light')
        grass_dark = assets.TILES.get('grass_dark')
        path_img = assets.TILES.get('path')
        start_img = assets.TILES.get('start')
        end_img = assets.TILES.get('end')
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.grid[row][col]
                x = GRID_OFFSET_X + col * TILE_SIZE
                y = GRID_OFFSET_Y + row * TILE_SIZE
                if tile == 0:
                    sprite = grass_light if (col + row) % 2 == 0 else grass_dark
                elif tile == 1:
                    sprite = path_img
                elif tile == 2:
                    sprite = start_img
                elif tile == 3:
                    sprite = end_img
                else:
                    sprite = None
                if sprite is not None:
                    surface.blit(sprite, (x, y))
                else:
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, GREEN, rect)
        for row in range(self.rows + 1):
            y = GRID_OFFSET_Y + row * TILE_SIZE
            pygame.draw.line(surface, (0, 0, 0, 30), (GRID_OFFSET_X, y), (GRID_OFFSET_X + self.cols * TILE_SIZE, y), 1)
        for col in range(self.cols + 1):
            x = GRID_OFFSET_X + col * TILE_SIZE
            pygame.draw.line(surface, (0, 0, 0, 30), (x, GRID_OFFSET_Y), (x, GRID_OFFSET_Y + self.rows * TILE_SIZE), 1)