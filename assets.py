"""Sprite asset loader

During startup, all PNG sprites are loaded and pygame 
Surfaces are made available to the game environment. 
If a file is missing, a magenta placeholder is displayed 
to ensure the game continues to function

The expected directory layout is

    assets/
        tiles/    (grass_light, grass_dark, path, start, end)
        towers/   (<type>_base, <type>_head)
        enemies/  (<type>)
        projectiles/ (<type>)

Sprites are authored at a reference size, while towers and enemies are scaled to 
fit the TILE_SIZE / per-enemy size from settings.py, maintaining the original 
rect/circle rendering
"""

from __future__ import annotations

import os
import pygame

from settings import TILE_SIZE, ENEMY_TYPES


HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(HERE, "assets")


# in-memory caches
TILES: dict[str, pygame.Surface] = {}
TOWER_BASES: dict[str, pygame.Surface] = {}
TOWER_HEADS: dict[str, pygame.Surface] = {}   # base rotation
ENEMIES: dict[str, pygame.Surface] = {}
PROJECTILES: dict[str, pygame.Surface] = {}

_loaded = False


def _placeholder(size: tuple[int, int]) -> pygame.Surface:
    # Bright magenta 'missing asset' placeholder
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((255, 0, 255, 200))
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
    return surf


def _load(relpath: str, size: tuple[int, int] | None = None) -> pygame.Surface:
    # Load PNG from ASSETS_DIR, scale if requested or return placeholder.
    full = os.path.join(ASSETS_DIR, relpath)
    if not os.path.isfile(full):
        print(f"[assets] MISSING {relpath}")
        return _placeholder(size or (32, 32))
    try:
        img = pygame.image.load(full).convert_alpha()
    except pygame.error as exc:
        print(f"[assets] failed to load {relpath}: {exc}")
        return _placeholder(size or (32, 32))
    if size and img.get_size() != size:
        img = pygame.transform.smoothscale(img, size)
    return img


def load_all() -> None:
    # Populate all sprite caches. after pygame.display.set_mode()
    global _loaded
    if _loaded:
        return

    # scale to exactly TILE_SIZE so the map grid aligns
    tsize = (TILE_SIZE, TILE_SIZE)
    TILES["grass_light"] = _load("tiles/grass_light.png", tsize)
    TILES["grass_dark"] = _load("tiles/grass_dark.png", tsize)
    TILES["path"] = _load("tiles/path.png", tsize)
    TILES["start"] = _load("tiles/start.png", tsize)
    TILES["end"] = _load("tiles/end.png", tsize)

    # Towers: base sits on the tile; head is drawn on top and rotated
    base_size = (TILE_SIZE, TILE_SIZE)
    head_size = (TILE_SIZE - 8, TILE_SIZE - 8)
    for ttype in ("arrow", "cannon", "ice"):
        TOWER_BASES[ttype] = _load(f"towers/{ttype}_base.png", base_size)
        TOWER_HEADS[ttype] = _load(f"towers/{ttype}_head.png", head_size)

    # nemies each has its own reference size in settings.
    # The sprite "size" config is an approximate radius, so we
    # render at 2.4x the radius for a properly-sized body
    for etype, cfg in ENEMY_TYPES.items():
        r = cfg["size"]
        dim = int(r * 2.6)
        ENEMIES[etype] = _load(f"enemies/{etype}.png", (dim, dim))

    # Projectiles authored at final size, no scaling
    PROJECTILES["arrow"] = _load("projectiles/arrow.png")
    PROJECTILES["cannon"] = _load("projectiles/cannon.png")
    PROJECTILES["ice"] = _load("projectiles/ice.png")

    _loaded = True
