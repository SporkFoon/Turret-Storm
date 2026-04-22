"""Tower class - defensive structures that shoot enemies"""

import pygame
import math
from settings import *


# map tower_type to its projectile sprite key in assets.PROJECTILES
PROJ_SPRITE_FOR = {
    "arrow": "arrow",
    "cannon": "cannon",
    "ice": "ice",
}


class Projectile:
    # projectile fired by a tower toward an enemy

    def __init__(self, x, y, target, damage, speed, color, splash_radius=0,
                 slow_factor=0, slow_duration=0, sprite_key=None):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.damage = damage
        self.speed = speed
        self.color = color
        self.splash_radius = splash_radius
        self.slow_factor = slow_factor
        self.slow_duration = slow_duration
        self.alive = True
        self.radius = 4
        # sprite key to look up in assets.PROJECTILES None => fallback circle
        self.sprite_key = sprite_key
        # current angle used for rotating the sprite toward motion
        self.angle = 0.0

    def update(self, dt, enemies):
        # move toward target. returns list of hit enemies
        if not self.alive:
            return []

        # if target died, keep going toward last known position
        if self.target and self.target.alive:
            tx, ty = self.target.position[0], self.target.position[1]
        elif self.target:
            tx, ty = self.target.position[0], self.target.position[1]
            self.target = None
        else:
            self.alive = False
            return []

        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 10:
            # hit
            self.alive = False
            hit_enemies = []

            if self.splash_radius > 0:
                # splash damage
                for e in enemies:
                    if not e.alive:
                        continue
                    ex, ey = e.position[0], e.position[1]
                    edist = math.sqrt((ex - self.x) ** 2 + (ey - self.y) ** 2)
                    if edist <= self.splash_radius:
                        killed = e.take_damage(self.damage)
                        hit_enemies.append((e, killed))
            else:
                # single target
                if self.target and self.target.alive:
                    killed = self.target.take_damage(self.damage)
                    hit_enemies.append((self.target, killed))

            # apply slow
            if self.slow_factor > 0:
                for e, _ in hit_enemies:
                    if e.alive:
                        e.apply_slow(self.slow_factor, self.slow_duration)

            return hit_enemies
        else:
            move = self.speed * dt
            ratio = move / dist
            self.x += dx * ratio
            self.y += dy * ratio
            # sprite faces its direction of travel
            self.angle = math.degrees(math.atan2(-dy, dx)) - 90
            return []

    def draw(self, surface):
        if not self.alive:
            return
        # pefer a sprite; fall back to the legacy coloured circle if the asset couldn't be loaded
        import assets
        sprite = assets.PROJECTILES.get(self.sprite_key) if self.sprite_key else None
        if sprite is not None:
            rotated = pygame.transform.rotate(sprite, self.angle)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(rotated, rect)
        else:
            pygame.draw.circle(surface, self.color,
                               (int(self.x), int(self.y)), self.radius)


class Tower:
    """ a defensive tower placed on the grid
    
    Attributes:
        tower_type: Type key from TOWER_TYPES
        grid_pos: (col, row) on the grid
        level: Upgrade level (1-3)
        kills: Number of enemies killed by this tower
        total_damage: Total damage dealt
    """

    def __init__(self, tower_type, grid_col, grid_row):
        config = TOWER_TYPES[tower_type]
        self.tower_type = tower_type
        self.name = config["name"]
        self.grid_pos = (grid_col, grid_row)

        # position in pixels (center)
        self.x = GRID_OFFSET_X + grid_col * TILE_SIZE + TILE_SIZE // 2
        self.y = GRID_OFFSET_Y + grid_row * TILE_SIZE + TILE_SIZE // 2

        # stats from config
        self.base_damage = config["damage"]
        self.damage = self.base_damage
        self.base_range = config["range"]
        self.range = self.base_range
        self.fire_rate = config["fire_rate"]
        self.color = config["color"]
        self.proj_color = config["proj_color"]
        self.proj_speed = config["proj_speed"]
        self.cost = config["cost"]

        # special attributes
        self.splash_radius = config.get("splash_radius", 0)
        self.slow_factor = config.get("slow_factor", 0)
        self.slow_duration = config.get("slow_duration", 0)

        # upgrade
        self.level = 1
        self.max_level = 3
        self.upgrade_cost = config["upgrade_cost"]
        self.upgrade_damage = config["upgrade_damage"]
        self.upgrade_range = config["upgrade_range"]
        self.total_invested = self.cost

        # combat
        self.fire_timer = 0.0
        self.target = None
        self.projectiles = []

        # visual: rotation angle of the tower head
        # each frame toward the current target
        self.head_angle = 0.0

        # tracking
        self.kills = 0
        self.total_damage = 0
        self.shots_fired = 0
        self.shots_hit = 0

        self.selected = False

    def get_upgrade_price(self):
        if self.level >= self.max_level:
            return 0
        return int(self.upgrade_cost * self.level)

    def upgrade(self):
        # upgrade the tower. returns cost or 0 if max level
        if self.level >= self.max_level:
            return 0
        cost = self.get_upgrade_price()
        self.level += 1
        self.damage += self.upgrade_damage
        self.range += self.upgrade_range
        self.total_invested += cost
        return cost

    def get_sell_price(self):
        return int(self.total_invested * 0.6)

    def find_target(self, enemies):
        # find the closest enemy in range
        best = None
        best_dist = float('inf')
        for e in enemies:
            if not e.alive:
                continue
            dx = e.position[0] - self.x
            dy = e.position[1] - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= self.range and dist < best_dist:
                best = e
                best_dist = dist
        self.target = best

    def update(self, dt, enemies):
        # update tower find target, shoot, update projectiles
        # Update projectiles
        for p in self.projectiles:
            hits = p.update(dt, enemies)
            for enemy, killed in hits:
                self.total_damage += self.damage
                self.shots_hit += 1
                if killed:
                    self.kills += 1

        self.projectiles = [p for p in self.projectiles if p.alive]

        # Keep tracking an enemy so the head sprite swivels even
        # between shots (otherwise the head would only move when we fire)
        # this is a cheap O(N) scan; enemies list is small.
        if self.target is None or not self.target.alive:
            self.find_target(enemies)

        # rotate head toward the current target if we have one
        if self.target and self.target.alive:
            dx = self.target.position[0] - self.x
            dy = self.target.position[1] - self.y
            # Sprite's default orientation points up (-Y)
            self.head_angle = math.degrees(math.atan2(-dy, dx)) - 90

        # shooting logic
        self.fire_timer -= dt
        if self.fire_timer <= 0:
            # re-acquire target in case the tracked one wandered out of range
            self.find_target(enemies)
            if self.target and self.target.alive:
                self._shoot()
                self.fire_timer = 1.0 / self.fire_rate
            else:
                self.fire_timer = 0.1  # Check again soon

    def _shoot(self):
        # fire a projectile at the current target
        p = Projectile(
            self.x, self.y, self.target,
            self.damage, self.proj_speed, self.proj_color,
            self.splash_radius, self.slow_factor, self.slow_duration,
            sprite_key=PROJ_SPRITE_FOR.get(self.tower_type),
        )
        self.projectiles.append(p)
        self.shots_fired += 1

    def draw(self, surface):
        # draw the tower using sprite assets
        import assets

        # range circle if selected
        if self.selected:
            range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (255, 255, 255, 40), (self.range, self.range), self.range)
            pygame.draw.circle(range_surface, (255, 255, 255, 80), (self.range, self.range), self.range, 2)
            surface.blit(range_surface, (self.x - self.range, self.y - self.range))

        # base sprite
        base = assets.TOWER_BASES.get(self.tower_type)
        if base is not None:
            rect = base.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(base, rect)
        else:
            # fallback rectangle if asset is missing
            rect = pygame.Rect(self.x - 20, self.y - 20, 40, 40)
            pygame.draw.rect(surface, self.color, rect, border_radius=6)
            pygame.draw.rect(surface, BLACK, rect, 2, border_radius=6)

        # rotating head sprite
        head = assets.TOWER_HEADS.get(self.tower_type)
        if head is not None:
            rotated = pygame.transform.rotate(head, self.head_angle)
            rect = rotated.get_rect(center=(int(self.x), int(self.y) - 4))
            surface.blit(rotated, rect)

        # level indicator (gold pips above the tower)
        if self.level > 1:
            for i in range(self.level - 1):
                star_x = int(self.x) - 6 + i * 12
                star_y = int(self.y) - 30
                pygame.draw.circle(surface, YELLOW, (star_x, star_y), 4)
                pygame.draw.circle(surface, BLACK, (star_x, star_y), 4, 1)

        # draw projectiles
        for p in self.projectiles:
            p.draw(surface)

    def draw_info(self, surface, x, y):
        # draw tower info panel
        font = pygame.font.SysFont(None, 22)
        lines = [
            f"{self.name} (Lv.{self.level})",
            f"Damage: {self.damage}",
            f"Range: {self.range}",
            f"Rate: {self.fire_rate:.1f}/s",
            f"Kills: {self.kills}",
            f"Sell: {self.get_sell_price()}g",
        ]
        if self.level < self.max_level:
            lines.append(f"Upgrade: {self.get_upgrade_price()}g")

        for i, line in enumerate(lines):
            color = UI_GOLD if "Sell" in line or "Upgrade" in line else UI_TEXT
            text = font.render(line, True, color)
            surface.blit(text, (x, y + i * 22))
