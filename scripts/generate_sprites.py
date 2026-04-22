"""Sprite generator for Turret Storm.

Produces clean pixel-art PNG sprites for tiles, towers, enemies, and
projectiles into the project's `assets/` folder. Run from the project
root:

    python scripts/generate_sprites.py

All sprites are generated procedurally with Pillow so the project
remains fully self-contained and has no external licensing concerns.
Style: 64x64 tile art with a clean, readable pixel-art look.
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

# -- config -------------------------------------------------------------
TILE = 64                # base tile size
TOWER_BASE = 64          # tower base sprite dimensions
TOWER_HEAD = 56          # square canvas for the rotating tower head
ENEMY_SIZES = {          # per-enemy render size (pixels)
    "normal": 40,
    "fast": 36,
    "tank": 52,
    "boss": 64,
}

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")

random.seed(1337)  # deterministic output across runs


# -- small helpers ------------------------------------------------------
def new_canvas(size):
    return Image.new("RGBA", (size, size), (0, 0, 0, 0))


def save(img, relpath):
    """Save RGBA image, creating intermediate dirs."""
    full = os.path.join(ASSETS, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    img.save(full)
    print(f"  -> {relpath}")


def rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


def shade(color, amount):
    """Lighten (amount>0) or darken (amount<0) an RGB/RGBA color."""
    r, g, b = color[:3]
    a = color[3] if len(color) == 4 else 255
    if amount >= 0:
        r = int(r + (255 - r) * amount)
        g = int(g + (255 - g) * amount)
        b = int(b + (255 - b) * amount)
    else:
        f = 1.0 + amount
        r, g, b = int(r * f), int(g * f), int(b * f)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), a)


def pixel_noise(img, amount=18, alpha=80):
    """Add subtle pixel noise to non-transparent areas for texture."""
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            n = random.randint(-amount, amount)
            px[x, y] = (
                max(0, min(255, r + n)),
                max(0, min(255, g + n)),
                max(0, min(255, b + n)),
                a,
            )


# -- TILES --------------------------------------------------------------
def make_grass(dark=False):
    """Grass tile with tufts."""
    img = new_canvas(TILE)
    d = ImageDraw.Draw(img)
    base = (58, 140, 62) if not dark else (46, 118, 52)
    d.rectangle([0, 0, TILE, TILE], fill=base)

    # Slight vertical gradient
    for y in range(TILE):
        k = (y / TILE) * 0.08
        d.line([(0, y), (TILE, y)], fill=shade(base, -k))

    # Grass blades (tufts)
    rng = random.Random(7 if not dark else 13)
    for _ in range(22):
        x = rng.randint(2, TILE - 3)
        y = rng.randint(4, TILE - 3)
        blade = shade(base, rng.uniform(-0.25, 0.2))
        d.line([(x, y), (x, y - rng.randint(2, 4))], fill=blade)

    # Small flowers
    for _ in range(3 if not dark else 2):
        x = rng.randint(4, TILE - 4)
        y = rng.randint(4, TILE - 4)
        color = rng.choice([(255, 236, 120), (240, 240, 255), (255, 200, 230)])
        d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=color)
        d.point((x, y), fill=(255, 255, 255))

    pixel_noise(img, amount=10, alpha=40)
    return img


def make_path():
    """Sandy path tile."""
    img = new_canvas(TILE)
    d = ImageDraw.Draw(img)
    base = (212, 184, 132)
    d.rectangle([0, 0, TILE, TILE], fill=base)

    # Darker edge border for tile definition
    d.rectangle([0, 0, TILE - 1, TILE - 1],
                outline=shade(base, -0.25), width=2)

    # Little pebbles
    rng = random.Random(21)
    for _ in range(14):
        x = rng.randint(4, TILE - 4)
        y = rng.randint(4, TILE - 4)
        r = rng.randint(1, 2)
        col = shade(base, rng.uniform(-0.3, 0.15))
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)

    pixel_noise(img, amount=12, alpha=40)
    return img


def make_start():
    """Green start tile with a small flag."""
    img = new_canvas(TILE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, TILE, TILE], fill=(120, 200, 110))
    d.rectangle([0, 0, TILE - 1, TILE - 1],
                outline=(60, 140, 70), width=2)

    # Flag pole
    d.rectangle([TILE // 2 - 1, 10, TILE // 2 + 1, TILE - 10],
                fill=(60, 45, 30))
    # Flag cloth
    d.polygon([(TILE // 2 + 1, 12),
               (TILE // 2 + 18, 16),
               (TILE // 2 + 1, 22)],
              fill=(80, 200, 90), outline=(40, 110, 50))
    pixel_noise(img, amount=10)
    return img


def make_end():
    """Red end tile with a target."""
    img = new_canvas(TILE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, TILE, TILE], fill=(220, 110, 110))
    d.rectangle([0, 0, TILE - 1, TILE - 1],
                outline=(130, 50, 50), width=2)

    # Target rings
    cx = cy = TILE // 2
    rings = [(22, (240, 240, 240)),
             (16, (200, 50, 50)),
             (10, (240, 240, 240)),
             (5, (200, 50, 50))]
    for r, c in rings:
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=c, outline=(60, 30, 30))
    pixel_noise(img, amount=8)
    return img


# -- TOWERS -------------------------------------------------------------
def make_tower_base(body_color, stone_color=(150, 150, 160)):
    """Shared stone pedestal with a colored top disk."""
    img = new_canvas(TOWER_BASE)
    d = ImageDraw.Draw(img)
    cx = cy = TOWER_BASE // 2

    # Ground shadow
    sh = Image.new("RGBA", (TOWER_BASE, TOWER_BASE), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(
        [cx - 26, cy + 8, cx + 26, cy + 24], fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=1.5))
    img.alpha_composite(sh)

    # Stone base (two-tone, hex-ish)
    d.polygon([
        (cx - 24, cy + 10), (cx - 18, cy + 20), (cx + 18, cy + 20),
        (cx + 24, cy + 10), (cx + 18, cy), (cx - 18, cy),
    ], fill=stone_color, outline=(40, 40, 45))
    d.polygon([
        (cx - 24, cy + 10), (cx - 18, cy + 20), (cx + 18, cy + 20),
        (cx + 24, cy + 10), (cx + 18, cy + 2),
    ], fill=shade(stone_color, -0.15))

    # Stone highlights / bricks
    d.line([(cx - 18, cy), (cx + 18, cy)], fill=shade(stone_color, 0.25))
    d.line([(cx - 5, cy), (cx - 5, cy + 20)], fill=shade(stone_color, -0.25))
    d.line([(cx + 5, cy), (cx + 5, cy + 20)], fill=shade(stone_color, -0.25))

    # Colored top platform (the tower's identity color)
    d.ellipse([cx - 16, cy - 10, cx + 16, cy + 6],
              fill=shade(body_color, -0.1), outline=(30, 30, 35))
    d.ellipse([cx - 14, cy - 12, cx + 14, cy + 2],
              fill=body_color, outline=(30, 30, 35))

    return img


def make_arrow_head():
    """Crossbow-style head pointing up (+Y to +X rotation later)."""
    img = new_canvas(TOWER_HEAD)
    d = ImageDraw.Draw(img)
    cx = cy = TOWER_HEAD // 2

    # Stock
    wood = (130, 85, 45)
    wood_d = shade(wood, -0.25)
    d.rectangle([cx - 4, cy - 2, cx + 4, cy + 14],
                fill=wood, outline=wood_d)
    # Bow arms
    d.line([(cx - 18, cy - 6), (cx + 18, cy - 6)],
           fill=(60, 40, 20), width=2)
    d.line([(cx - 20, cy - 4), (cx - 14, cy - 10)],
           fill=(60, 40, 20), width=2)
    d.line([(cx + 20, cy - 4), (cx + 14, cy - 10)],
           fill=(60, 40, 20), width=2)
    # String
    d.line([(cx - 16, cy - 8), (cx + 16, cy - 8)],
           fill=(230, 230, 210))
    # Arrow loaded (pointing -Y = "forward" before rotation)
    d.line([(cx, cy - 18), (cx, cy + 6)], fill=(200, 170, 120), width=2)
    # Arrow head
    d.polygon([(cx, cy - 22), (cx - 3, cy - 16), (cx + 3, cy - 16)],
              fill=(220, 220, 220), outline=(40, 40, 40))
    # Fletching
    d.polygon([(cx - 3, cy + 4), (cx, cy + 2), (cx + 3, cy + 4),
               (cx, cy + 10)], fill=(220, 60, 60), outline=(120, 20, 20))
    return img


def make_cannon_head():
    """Cannon barrel head pointing forward (-Y)."""
    img = new_canvas(TOWER_HEAD)
    d = ImageDraw.Draw(img)
    cx = cy = TOWER_HEAD // 2

    # Turret body (dome)
    body = (90, 65, 55)
    d.ellipse([cx - 12, cy - 6, cx + 12, cy + 14],
              fill=body, outline=(30, 20, 15))
    d.ellipse([cx - 10, cy - 8, cx + 10, cy + 4],
              fill=shade(body, 0.15))

    # Barrel (points up, which will be rotated toward target)
    barrel = (70, 55, 50)
    d.rectangle([cx - 5, cy - 22, cx + 5, cy + 2],
                fill=barrel, outline=(20, 15, 10))
    d.rectangle([cx - 5, cy - 22, cx + 5, cy - 18],
                fill=(25, 20, 18))  # muzzle
    # Barrel band
    d.rectangle([cx - 6, cy - 14, cx + 6, cy - 11],
                fill=(40, 30, 25))
    # Highlight
    d.line([(cx - 3, cy - 20), (cx - 3, cy - 4)],
           fill=shade(barrel, 0.4))
    return img


def make_ice_head():
    """Ice crystal spire pointing forward (-Y)."""
    img = new_canvas(TOWER_HEAD)
    d = ImageDraw.Draw(img)
    cx = cy = TOWER_HEAD // 2

    # Base ring
    ring = (70, 110, 180)
    d.ellipse([cx - 12, cy - 2, cx + 12, cy + 14],
              fill=ring, outline=(20, 40, 80))

    # Main crystal (kite shape, faceted)
    ice_light = (200, 235, 255)
    ice_mid = (130, 200, 240)
    ice_dark = (70, 130, 190)

    d.polygon([(cx, cy - 24), (cx - 8, cy - 6),
               (cx, cy + 6), (cx + 8, cy - 6)],
              fill=ice_mid, outline=(20, 60, 120))
    # Highlight facet (left)
    d.polygon([(cx, cy - 24), (cx - 8, cy - 6), (cx, cy - 6)],
              fill=ice_light)
    # Shadow facet (right)
    d.polygon([(cx, cy + 6), (cx, cy - 6), (cx + 8, cy - 6)],
              fill=ice_dark)

    # Tiny side shards
    d.polygon([(cx - 10, cy - 4), (cx - 13, cy + 2), (cx - 8, cy + 4)],
              fill=ice_mid, outline=(20, 60, 120))
    d.polygon([(cx + 10, cy - 4), (cx + 13, cy + 2), (cx + 8, cy + 4)],
              fill=ice_mid, outline=(20, 60, 120))

    # Sparkle
    d.point((cx - 2, cy - 16), fill=(255, 255, 255))
    d.point((cx - 1, cy - 17), fill=(255, 255, 255))
    return img


# -- ENEMIES ------------------------------------------------------------
def make_grunt():
    """Green goblin grunt, size 40."""
    S = ENEMY_SIZES["normal"]
    img = new_canvas(S)
    d = ImageDraw.Draw(img)
    cx = cy = S // 2

    body = (110, 170, 70)
    d.ellipse([cx - 14, cy - 12, cx + 14, cy + 14],
              fill=body, outline=(40, 70, 30), width=2)
    # Belly highlight
    d.ellipse([cx - 10, cy - 2, cx + 10, cy + 10],
              fill=shade(body, 0.18))
    # Eyes
    d.ellipse([cx - 8, cy - 6, cx - 3, cy - 1],
              fill=(255, 255, 255), outline=(0, 0, 0))
    d.ellipse([cx + 3, cy - 6, cx + 8, cy - 1],
              fill=(255, 255, 255), outline=(0, 0, 0))
    d.point((cx - 6, cy - 4), fill=(0, 0, 0))
    d.point((cx + 5, cy - 4), fill=(0, 0, 0))
    # Mouth
    d.line([(cx - 3, cy + 5), (cx + 3, cy + 5)], fill=(40, 20, 10))
    # Tusks
    d.polygon([(cx - 3, cy + 5), (cx - 5, cy + 9), (cx - 2, cy + 7)],
              fill=(250, 250, 240))
    d.polygon([(cx + 3, cy + 5), (cx + 5, cy + 9), (cx + 2, cy + 7)],
              fill=(250, 250, 240))
    return img


def make_scout():
    """Fast yellow-orange runner, size 36."""
    S = ENEMY_SIZES["fast"]
    img = new_canvas(S)
    d = ImageDraw.Draw(img)
    cx = cy = S // 2

    body = (255, 160, 60)
    # Diamond-ish fast silhouette
    d.polygon([(cx, cy - 13), (cx + 13, cy),
               (cx, cy + 13), (cx - 13, cy)],
              fill=body, outline=(120, 70, 20))
    # Streak (speed lines)
    d.line([(cx - 12, cy + 4), (cx - 4, cy + 4)],
           fill=(255, 240, 200))
    d.line([(cx - 10, cy - 4), (cx - 3, cy - 4)],
           fill=(255, 240, 200))
    # Face
    d.ellipse([cx - 5, cy - 5, cx - 1, cy - 1],
              fill=(255, 255, 255), outline=(0, 0, 0))
    d.ellipse([cx + 1, cy - 5, cx + 5, cy - 1],
              fill=(255, 255, 255), outline=(0, 0, 0))
    d.point((cx - 3, cy - 3), fill=(0, 0, 0))
    d.point((cx + 3, cy - 3), fill=(0, 0, 0))
    return img


def make_tank():
    """Armored tank enemy, size 52."""
    S = ENEMY_SIZES["tank"]
    img = new_canvas(S)
    d = ImageDraw.Draw(img)
    cx = cy = S // 2

    body = (140, 80, 180)
    armor = (90, 50, 130)
    # Body
    rounded_rect(d,
                 [cx - 20, cy - 16, cx + 20, cy + 18],
                 radius=6, fill=body, outline=(40, 20, 60), width=2)
    # Armor plate
    rounded_rect(d,
                 [cx - 16, cy - 12, cx + 16, cy + 2],
                 radius=4, fill=armor, outline=(30, 15, 50))
    # Rivets
    for rx in (-14, -7, 0, 7, 14):
        d.ellipse([cx + rx - 1, cy - 10, cx + rx + 1, cy - 8],
                  fill=(220, 220, 220))
        d.ellipse([cx + rx - 1, cy - 2, cx + rx + 1, cy],
                  fill=(220, 220, 220))
    # Eyes / visor slit
    d.rectangle([cx - 10, cy + 6, cx + 10, cy + 10],
                fill=(255, 80, 80), outline=(0, 0, 0))
    d.line([(cx - 7, cy + 8), (cx + 7, cy + 8)],
           fill=(255, 220, 220))
    # Shoulder spikes
    d.polygon([(cx - 20, cy - 10), (cx - 26, cy - 6), (cx - 20, cy - 2)],
              fill=armor, outline=(30, 15, 50))
    d.polygon([(cx + 20, cy - 10), (cx + 26, cy - 6), (cx + 20, cy - 2)],
              fill=armor, outline=(30, 15, 50))
    return img


def make_boss():
    """Boss demon, size 64."""
    S = ENEMY_SIZES["boss"]
    img = new_canvas(S)
    d = ImageDraw.Draw(img)
    cx = cy = S // 2

    body = (210, 40, 40)
    # Body
    d.ellipse([cx - 26, cy - 22, cx + 26, cy + 24],
              fill=body, outline=(80, 15, 15), width=2)
    d.ellipse([cx - 20, cy - 10, cx + 20, cy + 18],
              fill=shade(body, 0.15))
    # Horns
    d.polygon([(cx - 22, cy - 18), (cx - 28, cy - 30), (cx - 14, cy - 22)],
              fill=(60, 30, 30), outline=(0, 0, 0))
    d.polygon([(cx + 22, cy - 18), (cx + 28, cy - 30), (cx + 14, cy - 22)],
              fill=(60, 30, 30), outline=(0, 0, 0))
    # Eyes (glowing)
    d.ellipse([cx - 12, cy - 6, cx - 4, cy + 2],
              fill=(255, 230, 80), outline=(0, 0, 0))
    d.ellipse([cx + 4, cy - 6, cx + 12, cy + 2],
              fill=(255, 230, 80), outline=(0, 0, 0))
    d.ellipse([cx - 10, cy - 4, cx - 6, cy], fill=(0, 0, 0))
    d.ellipse([cx + 6, cy - 4, cx + 10, cy], fill=(0, 0, 0))
    # Fanged mouth
    d.rectangle([cx - 12, cy + 8, cx + 12, cy + 16],
                fill=(30, 10, 10), outline=(0, 0, 0))
    for fx in (-10, -6, -2, 2, 6, 10):
        d.polygon([(cx + fx, cy + 8), (cx + fx + 2, cy + 14),
                   (cx + fx + 4, cy + 8)],
                  fill=(250, 250, 240))
    return img


# -- PROJECTILES --------------------------------------------------------
def make_arrow_proj():
    """Small arrow, 20x20 square with arrow pointing up."""
    S = 20
    img = new_canvas(S)
    d = ImageDraw.Draw(img)
    cx = S // 2
    # Shaft
    d.rectangle([cx - 1, 3, cx + 1, S - 5],
                fill=(220, 190, 130), outline=(90, 60, 30))
    # Head
    d.polygon([(cx, 0), (cx - 3, 5), (cx + 3, 5)],
              fill=(230, 230, 230), outline=(40, 40, 40))
    # Fletching
    d.polygon([(cx - 3, S - 5), (cx, S - 7),
               (cx + 3, S - 5), (cx, S - 1)],
              fill=(220, 60, 60), outline=(120, 20, 20))
    return img


def make_cannonball():
    """Dark sphere with highlight."""
    S = 14
    img = new_canvas(S)
    d = ImageDraw.Draw(img)
    d.ellipse([1, 1, S - 2, S - 2], fill=(45, 45, 50),
              outline=(0, 0, 0))
    d.ellipse([3, 3, 7, 7], fill=(120, 120, 130))
    d.ellipse([4, 4, 5, 5], fill=(220, 220, 230))
    return img


def make_ice_shard():
    """Small blue shard."""
    S = 16
    img = new_canvas(S)
    d = ImageDraw.Draw(img)
    cx = S // 2
    d.polygon([(cx, 0), (S - 2, cx), (cx, S - 1), (1, cx)],
              fill=(160, 220, 255), outline=(30, 80, 140))
    d.polygon([(cx, 0), (cx, S - 1), (1, cx)],
              fill=(210, 240, 255))
    d.point((cx - 1, 3), fill=(255, 255, 255))
    return img


# -- main ---------------------------------------------------------------
def main():
    print(f"Generating sprites into {ASSETS}")

    # Tiles
    save(make_grass(dark=False), "tiles/grass_light.png")
    save(make_grass(dark=True), "tiles/grass_dark.png")
    save(make_path(), "tiles/path.png")
    save(make_start(), "tiles/start.png")
    save(make_end(), "tiles/end.png")

    # Towers: bases + heads
    tower_colors = {
        "arrow": (95, 170, 95),
        "cannon": (170, 90, 70),
        "ice": (90, 130, 210),
    }
    for name, color in tower_colors.items():
        save(make_tower_base(color), f"towers/{name}_base.png")

    save(make_arrow_head(),  "towers/arrow_head.png")
    save(make_cannon_head(), "towers/cannon_head.png")
    save(make_ice_head(),    "towers/ice_head.png")

    # Enemies
    save(make_grunt(),  "enemies/normal.png")
    save(make_scout(),  "enemies/fast.png")
    save(make_tank(),   "enemies/tank.png")
    save(make_boss(),   "enemies/boss.png")

    # Projectiles
    save(make_arrow_proj(), "projectiles/arrow.png")
    save(make_cannonball(), "projectiles/cannon.png")
    save(make_ice_shard(),  "projectiles/ice.png")

    print("Done.")


if __name__ == "__main__":
    main()
