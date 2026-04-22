# Enemy class represents enemies that traverse the path

import pygame
import math
from settings import *


class Enemy:
    """an enemy unit that follows the path from start to end
    
    Attributes:
        enemy_type: Type key from ENEMY_TYPES
        health / max_health: Current and maximum HP
        speed / base_speed: Movement speed (can be slowed)
        position: Current (x, y) pixel position
        reward: Gold given on death
        alive: Whether enemy is still active
        reached_end: Whether enemy made it to the end
    """

    def __init__(self, enemy_type, health_scale=1.0):
        config = ENEMY_TYPES[enemy_type]
        self.enemy_type = enemy_type
        self.name = config["name"]
        self.max_health = int(config["health"] * health_scale)
        self.health = self.max_health
        self.base_speed = config["speed"]
        self.speed = self.base_speed
        self.reward = config["reward"]
        self.color = config["color"]
        self.size = config["size"]

        self.alive = True
        self.reached_end = False

        # path following
        self.waypoint_index = 0
        self.position = self._grid_to_pixel(PATH_WAYPOINTS[0])
        self.target = self._grid_to_pixel(PATH_WAYPOINTS[1]) if len(PATH_WAYPOINTS) > 1 else self.position

        # slow effect
        self.slow_timer = 0.0
        self.slow_factor = 1.0

        # damage 
        self.damage_taken = 0
        self.distance_traveled = 0.0

    def _grid_to_pixel(self, grid_pos):
        # convert grid (col, row) to pixel center 
        col, row = grid_pos
        x = GRID_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2
        y = GRID_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2
        return [float(x), float(y)]

    def take_damage(self, damage):
        # apply damage to enemy
        self.health -= damage
        self.damage_taken += damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        return False

    def apply_slow(self, factor, duration):
        # apply a slow effect
        self.slow_factor = factor
        self.slow_timer = duration

    def update(self, dt):
        # move along the path
        if not self.alive or self.reached_end:
            return

        # update slow
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0
                self.slow_timer = 0

        effective_speed = self.base_speed * self.slow_factor

        # move toward target
        dx = self.target[0] - self.position[0]
        dy = self.target[1] - self.position[1]
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 2.0:
            # reached waypoint
            self.waypoint_index += 1
            if self.waypoint_index >= len(PATH_WAYPOINTS) - 1:
                self.reached_end = True
                self.alive = False
                return
            self.target = self._grid_to_pixel(PATH_WAYPOINTS[self.waypoint_index + 1])
        else:
            move = effective_speed * dt
            self.distance_traveled += move
            ratio = move / dist
            self.position[0] += dx * ratio
            self.position[1] += dy * ratio

    def draw(self, surface):
        # draw the enemy sprite and health bar"""
        if not self.alive:
            return

        import assets  # optimization (local import to avoid module-load cycle)

        x, y = int(self.position[0]), int(self.position[1])

        # Subtle walk bob driven by distance travelled so movement
        # feels alive without needing multi-frame animation.
        bob = int(math.sin(self.distance_traveled * 0.15) * 2)

        # cold aura ring underneath when slowed
        if self.slow_timer > 0:
            aura = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
            pygame.draw.circle(aura, (120, 200, 255, 70),
                               (self.size * 3 // 2, self.size * 3 // 2),
                               self.size + 4)
            surface.blit(aura, (x - self.size * 3 // 2,
                                y - self.size * 3 // 2 + bob))

        sprite = assets.ENEMIES.get(self.enemy_type)
        if sprite is not None:
            rect = sprite.get_rect(center=(x, y + bob))
            surface.blit(sprite, rect)
            # light blue tint overlay while slowed
            if self.slow_timer > 0:
                tint = sprite.copy()
                tint.fill((80, 160, 230, 0),
                          special_flags=pygame.BLEND_RGBA_MULT)
                tint.fill((40, 80, 140, 0),
                          special_flags=pygame.BLEND_RGBA_ADD)

                overlay = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                overlay.fill((80, 160, 230, 110))
                overlay.blit(sprite, (0, 0),
                             special_flags=pygame.BLEND_RGBA_MIN)
                surface.blit(overlay, rect)
        else:
            color = self.color
            if self.slow_timer > 0:
                color = (max(0, color[0] - 60),
                         max(0, color[1] - 30),
                         min(255, color[2] + 80))
            pygame.draw.circle(surface, color, (x, y + bob), self.size)
            pygame.draw.circle(surface, BLACK, (x, y + bob), self.size, 2)

        # Health bar
        bar_width = self.size * 2
        bar_height = 4
        bar_x = x - bar_width // 2
        bar_y = y - self.size - 8 + bob

        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_width, bar_height), 1)

    @property
    def center(self):
        return (self.position[0], self.position[1])
