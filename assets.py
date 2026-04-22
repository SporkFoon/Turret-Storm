from __future__ import annotations
import os
import pygame
from settings import TILE_SIZE, ENEMY_TYPES
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(HERE, 'assets')
TILES: dict[str, pygame.Surface] = {}
TOWER_BASES: dict[str, pygame.Surface] = {}
TOWER_HEADS: dict[str, pygame.Surface] = {}
ENEMIES: dict[str, pygame.Surface] = {}
PROJECTILES: dict[str, pygame.Surface] = {}
_loaded = False

def _placeholder(size: tuple[int, int]) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((255, 0, 255, 200))
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
    return surf

def _load(relpath: str, size: tuple[int, int] | None=None) -> pygame.Surface:
    full = os.path.join(ASSETS_DIR, relpath)
    if not os.path.isfile(full):
        print(f'[assets] MISSING {relpath}')
        return _placeholder(size or (32, 32))
    try:
        img = pygame.image.load(full).convert_alpha()
    except pygame.error as exc:
        print(f'[assets] failed to load {relpath}: {exc}')
        return _placeholder(size or (32, 32))
    if size and img.get_size() != size:
        img = pygame.transform.smoothscale(img, size)
    return img

def load_all() -> None:
    global _loaded
    if _loaded:
        return
    tsize = (TILE_SIZE, TILE_SIZE)
    TILES['grass_light'] = _load('tiles/grass_light.png', tsize)
    TILES['grass_dark'] = _load('tiles/grass_dark.png', tsize)
    TILES['path'] = _load('tiles/path.png', tsize)
    TILES['start'] = _load('tiles/start.png', tsize)
    TILES['end'] = _load('tiles/end.png', tsize)
    base_size = (TILE_SIZE, TILE_SIZE)
    head_size = (TILE_SIZE - 8, TILE_SIZE - 8)
    for ttype in ('arrow', 'cannon', 'ice'):
        TOWER_BASES[ttype] = _load(f'towers/{ttype}_base.png', base_size)
        TOWER_HEADS[ttype] = _load(f'towers/{ttype}_head.png', head_size)
    for (etype, cfg) in ENEMY_TYPES.items():
        r = cfg['size']
        dim = int(r * 2.6)
        ENEMIES[etype] = _load(f'enemies/{etype}.png', (dim, dim))
    PROJECTILES['arrow'] = _load('projectiles/arrow.png')
    PROJECTILES['cannon'] = _load('projectiles/cannon.png')
    PROJECTILES['ice'] = _load('projectiles/ice.png')
    _loaded = True