"""Game settings and constants"""

# screen
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 64
GRID_COLS = 12
GRID_ROWS = 10
GRID_OFFSET_X = 32
GRID_OFFSET_Y = 32
FPS = 60

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 220)
LIGHT_BLUE = (100, 180, 255)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
BROWN = (139, 90, 43)
DARK_BROWN = (100, 60, 20)
PURPLE = (150, 50, 200)
CYAN = (0, 200, 200)
SAND = (210, 180, 120)
DARK_SAND = (180, 150, 90)

# UI colors
UI_BG = (30, 30, 45)
UI_PANEL = (45, 45, 65)
UI_BORDER = (80, 80, 110)
UI_TEXT = (220, 220, 240)
UI_HIGHLIGHT = (100, 140, 255)
UI_GOLD = (255, 215, 0)

# game balance
STARTING_GOLD = 200
STARTING_LIVES = 20
GOLD_PER_KILL = 5
WAVE_BONUS_GOLD = 50

# tower definitions: {name: (cost, damage, range, fire_rate, color, projectile_color)}
TOWER_TYPES = {
    "arrow": {
        "name": "Arrow Tower",
        "cost": 50,
        "damage": 15,
        "range": 150,
        "fire_rate": 1.0,  # shots/second
        "color": (60, 130, 60),
        "proj_color": BROWN,
        "proj_speed": 400,
        "upgrade_cost": 40,
        "upgrade_damage": 8,
        "upgrade_range": 15,
        "description": "Fast, cheap. Good all-round."
    },
    "cannon": {
        "name": "Cannon Tower",
        "cost": 100,
        "damage": 50,
        "range": 120,
        "fire_rate": 0.5,
        "color": (100, 60, 60),
        "proj_color": DARK_GRAY,
        "proj_speed": 250,
        "splash_radius": 50,
        "upgrade_cost": 75,
        "upgrade_damage": 25,
        "upgrade_range": 10,
        "description": "Slow, splash damage."
    },
    "ice": {
        "name": "Ice Tower",
        "cost": 75,
        "damage": 8,
        "range": 130,
        "fire_rate": 0.8,
        "color": (60, 80, 160),
        "proj_color": LIGHT_BLUE,
        "proj_speed": 350,
        "slow_factor": 0.5,
        "slow_duration": 2.0,
        "upgrade_cost": 55,
        "upgrade_damage": 5,
        "upgrade_range": 12,
        "description": "Slows enemies down."
    }
}

# enemy definitions
ENEMY_TYPES = {
    "normal": {
        "name": "Grunt",
        "health": 80,
        "speed": 60,
        "reward": 5,
        "color": RED,
        "size": 12
    },
    "fast": {
        "name": "Scout",
        "health": 40,
        "speed": 120,
        "reward": 7,
        "color": ORANGE,
        "size": 10
    },
    "tank": {
        "name": "Tank",
        "health": 250,
        "speed": 35,
        "reward": 15,
        "color": PURPLE,
        "size": 16
    },
    "boss": {
        "name": "Boss",
        "health": 800,
        "speed": 25,
        "reward": 50,
        "color": (200, 0, 0),
        "size": 20
    }
}

# map layout: 0=grass, 1=path, 2=start, 3=end
GAME_MAP = [
    [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0],
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0],
]

# path waypoints (grid coords, in order from start to end)
PATH_WAYPOINTS = [
    (2, 0), (2, 1), (2, 2), (2, 3),
    (3, 3), (4, 3), (5, 3),
    (5, 4), (5, 5), (5, 6),
    (6, 6), (7, 6),
    (7, 5), (7, 4), (7, 3),
    (7, 2), (7, 1),
    (8, 1), (9, 1), (10, 1),
    (10, 2), (10, 3), (10, 4), (10, 5),
    (10, 6), (10, 7), (10, 8), (10, 9),
]

# wave definitions
def get_wave_enemies(wave_num):
    # generate enemy list for a given wave number
    enemies = []
    if wave_num <= 3:
        enemies = [("normal", 0.8)] * (3 + wave_num * 2)
    elif wave_num <= 6:
        enemies = [("normal", 0.6)] * (5 + wave_num) + [("fast", 0.5)] * (wave_num - 2)
    elif wave_num <= 9:
        enemies = ([("normal", 0.5)] * (4 + wave_num) +
                   [("fast", 0.4)] * (wave_num - 3) +
                   [("tank", 1.2)] * (wave_num - 5))
    else:
        enemies = ([("normal", 0.4)] * (5 + wave_num) +
                   [("fast", 0.3)] * wave_num +
                   [("tank", 1.0)] * (wave_num - 5))
        if wave_num % 5 == 0:
            enemies.append(("boss", 2.0))

    # scale enemy health with wave number
    health_scale = 1.0 + (wave_num - 1) * 0.12
    return enemies, health_scale
