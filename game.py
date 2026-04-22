import pygame
from settings import *
from game_map import GameMap
from tower import Tower
from enemy import Enemy
from stats_manager import StatsManager

class Game:

    def __init__(self, screen):
        self.screen = screen
        self.game_map = GameMap()
        self.stats_manager = StatsManager()
        self.state = 'playing'
        self.wave_num = 0
        self.gold = STARTING_GOLD
        self.lives = STARTING_LIVES
        self.towers = []
        self.enemies = []
        self.tower_grid = {}
        self.wave_enemies_queue = []
        self.spawn_timer = 0.0
        self.wave_kills = 0
        self.wave_leaked = 0
        self.wave_gold = 0
        self.selected_tower_type = 'arrow'
        self.selected_tower = None
        self.hover_pos = None
        self.font_large = pygame.font.SysFont(None, 36)
        self.font_medium = pygame.font.SysFont(None, 26)
        self.font_small = pygame.font.SysFont(None, 22)
        self.font_tiny = pygame.font.SysFont(None, 18)
        self.message = 'Press SPACE to start Wave 1'
        self.message_timer = 0
        self.stats_manager.record_gold_change(STARTING_GOLD, 'starting_gold', self.gold, 0)

    def handle_key(self, key):
        self.stats_manager.record_action('key_press', pygame.key.name(key))
        if key == pygame.K_TAB:
            if self.stats_manager.show_dashboard:
                self.stats_manager.next_page()
                if self.stats_manager.dashboard_page == 0:
                    self.stats_manager.show_dashboard = False
            else:
                self.stats_manager.toggle_dashboard()
            return
        if self.stats_manager.show_dashboard:
            return
        if key == pygame.K_SPACE and self.state == 'playing':
            self._start_wave()
        elif key == pygame.K_1:
            self.selected_tower_type = 'arrow'
            self.selected_tower = None
            self.message = 'Selected: Arrow Tower (50g)'
        elif key == pygame.K_2:
            self.selected_tower_type = 'cannon'
            self.selected_tower = None
            self.message = 'Selected: Cannon Tower (100g)'
        elif key == pygame.K_3:
            self.selected_tower_type = 'ice'
            self.selected_tower = None
            self.message = 'Selected: Ice Tower (75g)'
        elif key == pygame.K_u and self.selected_tower:
            self._upgrade_tower(self.selected_tower)
        elif key == pygame.K_s and self.selected_tower:
            self._sell_tower(self.selected_tower)

    def handle_click(self, pos, button):
        if self.stats_manager.show_dashboard:
            return
        (x, y) = pos
        self.stats_manager.record_action('mouse_click', f'{x},{y}')
        (col, row) = self.game_map.pixel_to_grid(x, y)
        if (col, row) in self.tower_grid:
            tower = self.tower_grid[col, row]
            if self.selected_tower:
                self.selected_tower.selected = False
            self.selected_tower = tower
            tower.selected = True
            self.message = f'{tower.name} Lv.{tower.level} | U=Upgrade, S=Sell'
            return
        if self.selected_tower:
            self.selected_tower.selected = False
            self.selected_tower = None
        if button == 1:
            self._place_tower(col, row)

    def handle_mouse_move(self, pos):
        self.hover_pos = pos

    def _place_tower(self, col, row):
        if not self.game_map.is_buildable(col, row):
            return
        if (col, row) in self.tower_grid:
            return
        config = TOWER_TYPES[self.selected_tower_type]
        cost = config['cost']
        if self.gold < cost:
            self.message = 'Not enough gold!'
            return
        tower = Tower(self.selected_tower_type, col, row)
        self.towers.append(tower)
        self.tower_grid[col, row] = tower
        self.gold -= cost
        self.stats_manager.record_tower_placed(self.selected_tower_type, col, row, self.wave_num, cost)
        self.stats_manager.record_gold_change(-cost, f'build_{self.selected_tower_type}', self.gold, self.wave_num)
        self.message = f"Placed {config['name']}!"

    def _upgrade_tower(self, tower):
        if tower.level >= tower.max_level:
            self.message = 'Tower already max level!'
            return
        cost = tower.get_upgrade_price()
        if self.gold < cost:
            self.message = 'Not enough gold to upgrade!'
            return
        tower.upgrade()
        self.gold -= cost
        self.stats_manager.record_gold_change(-cost, f'upgrade_{tower.tower_type}', self.gold, self.wave_num)
        self.stats_manager.record_action('upgrade_tower', f'{tower.tower_type}_lv{tower.level}')
        self.message = f'Upgraded to Lv.{tower.level}!'

    def _sell_tower(self, tower):
        refund = tower.get_sell_price()
        self.gold += refund
        pos = tower.grid_pos
        self.towers.remove(tower)
        del self.tower_grid[pos]
        self.selected_tower = None
        self.stats_manager.record_gold_change(refund, f'sell_{tower.tower_type}', self.gold, self.wave_num)
        self.stats_manager.record_action('sell_tower', tower.tower_type)
        self.message = f'Sold for {refund}g'

    def _start_wave(self):
        self.wave_num += 1
        self.state = 'wave_active'
        self.wave_kills = 0
        self.wave_leaked = 0
        self.wave_gold = 0
        (enemies_config, health_scale) = get_wave_enemies(self.wave_num)
        self.wave_enemies_queue = [(etype, delay, health_scale) for (etype, delay) in enemies_config]
        self.spawn_timer = 0.5
        self.stats_manager.record_wave_start(self.wave_num)
        self.stats_manager.record_action('start_wave', str(self.wave_num))
        self.message = f'Wave {self.wave_num} incoming!'

    def update(self, dt):
        self.stats_manager.update(dt)
        if self.message_timer > 0:
            self.message_timer -= dt
        if self.state == 'game_over':
            return
        if self.state == 'wave_active' and self.wave_enemies_queue:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                (etype, delay, health_scale) = self.wave_enemies_queue.pop(0)
                enemy = Enemy(etype, health_scale)
                self.enemies.append(enemy)
                self.spawn_timer = delay
        for enemy in self.enemies[:]:
            enemy.update(dt)
            if enemy.reached_end:
                self.lives -= 1
                self.wave_leaked += 1
                self.enemies.remove(enemy)
                self.stats_manager.record_action('enemy_leaked', enemy.enemy_type)
                if self.lives <= 0:
                    self.state = 'game_over'
                    self.message = 'GAME OVER! Press TAB for stats.'
                    self.stats_manager.save_to_csv()
                    return
            elif not enemy.alive:
                self.gold += enemy.reward
                self.wave_kills += 1
                self.wave_gold += enemy.reward
                self.enemies.remove(enemy)
                killer_type = 'unknown'
                for t in self.towers:
                    if t.kills > 0:
                        killer_type = t.tower_type
                self.stats_manager.record_enemy_kill(enemy.enemy_type, killer_type, enemy.damage_taken, self.wave_num)
                self.stats_manager.record_gold_change(enemy.reward, f'kill_{enemy.enemy_type}', self.gold, self.wave_num)
        for tower in self.towers:
            old_kills = tower.kills
            tower.update(dt, self.enemies)
            if tower.total_damage > 0:
                for p in tower.projectiles:
                    pass
        if self.state == 'wave_active' and (not self.wave_enemies_queue) and (not self.enemies):
            self._complete_wave()

    def _complete_wave(self):
        bonus = WAVE_BONUS_GOLD + self.wave_num * 10
        self.gold += bonus
        self.wave_gold += bonus
        self.stats_manager.record_wave_end(self.wave_num, self.wave_kills, self.wave_leaked, self.wave_gold)
        self.stats_manager.record_gold_change(bonus, 'wave_bonus', self.gold, self.wave_num)
        for tower in self.towers:
            if tower.shots_fired > 0:
                self.stats_manager.record_damage(tower.tower_type, tower.total_damage, 'mixed', self.wave_num)
        self.state = 'playing'
        self.message = f'Wave {self.wave_num} complete! +{bonus}g | SPACE for next wave'

    def draw(self):
        self.screen.fill(UI_BG)
        self.game_map.draw(self.screen)
        if self.hover_pos and (not self.stats_manager.show_dashboard):
            (col, row) = self.game_map.pixel_to_grid(*self.hover_pos)
            if self.game_map.is_buildable(col, row) and (col, row) not in self.tower_grid:
                hx = GRID_OFFSET_X + col * TILE_SIZE
                hy = GRID_OFFSET_Y + row * TILE_SIZE
                hover_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                can_afford = self.gold >= TOWER_TYPES[self.selected_tower_type]['cost']
                color = (0, 255, 0, 60) if can_afford else (255, 0, 0, 60)
                hover_surf.fill(color)
                self.screen.blit(hover_surf, (hx, hy))
        for tower in self.towers:
            tower.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        self._draw_ui()
        self.stats_manager.draw_dashboard(self.screen)
        if self.state == 'game_over':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))
            go_text = self.font_large.render('GAME OVER', True, RED)
            self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            hint = self.font_medium.render('Press TAB to view statistics', True, UI_TEXT)
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

    def _draw_ui(self):
        panel_x = GRID_OFFSET_X + GRID_COLS * TILE_SIZE + 16
        panel_w = SCREEN_WIDTH - panel_x - 8
        panel_rect = pygame.Rect(panel_x, GRID_OFFSET_Y, panel_w, GRID_ROWS * TILE_SIZE)
        pygame.draw.rect(self.screen, UI_PANEL, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, UI_BORDER, panel_rect, 2, border_radius=8)
        y = GRID_OFFSET_Y + 12
        x = panel_x + 12
        gold_text = self.font_medium.render(f'Gold: {self.gold}', True, UI_GOLD)
        self.screen.blit(gold_text, (x, y))
        y += 28
        lives_color = GREEN if self.lives > 10 else YELLOW if self.lives > 5 else RED
        lives_text = self.font_medium.render(f'Lives: {self.lives}', True, lives_color)
        self.screen.blit(lives_text, (x, y))
        y += 28
        wave_text = self.font_medium.render(f'Wave: {self.wave_num}', True, UI_TEXT)
        self.screen.blit(wave_text, (x, y))
        y += 40
        header = self.font_medium.render('Towers:', True, UI_HIGHLIGHT)
        self.screen.blit(header, (x, y))
        y += 28
        tower_keys = [('1', 'arrow'), ('2', 'cannon'), ('3', 'ice')]
        for (key, ttype) in tower_keys:
            config = TOWER_TYPES[ttype]
            is_selected = ttype == self.selected_tower_type
            color = UI_HIGHLIGHT if is_selected else UI_TEXT
            prefix = '> ' if is_selected else '  '
            line = self.font_small.render(f"{prefix}[{key}] {config['name']}", True, color)
            self.screen.blit(line, (x, y))
            y += 20
            cost_text = self.font_tiny.render(f"     {config['cost']}g | {config['description']}", True, LIGHT_GRAY)
            self.screen.blit(cost_text, (x, y))
            y += 22
        y += 10
        if self.selected_tower:
            sep = self.font_small.render('--- Selected Tower ---', True, UI_BORDER)
            self.screen.blit(sep, (x, y))
            y += 24
            self.selected_tower.draw_info(self.screen, x, y)
            y += 180
        y = GRID_OFFSET_Y + GRID_ROWS * TILE_SIZE - 120
        controls = ['Controls:', '1/2/3: Select tower', 'Click: Place tower', 'U: Upgrade | S: Sell', 'SPACE: Next wave', 'TAB: Statistics']
        for line in controls:
            text = self.font_tiny.render(line, True, LIGHT_GRAY)
            self.screen.blit(text, (x, y))
            y += 18
        msg_y = GRID_OFFSET_Y + GRID_ROWS * TILE_SIZE + 8
        msg_rect = pygame.Rect(GRID_OFFSET_X, msg_y, GRID_COLS * TILE_SIZE, 30)
        pygame.draw.rect(self.screen, UI_PANEL, msg_rect, border_radius=4)
        msg_text = self.font_small.render(self.message, True, UI_TEXT)
        self.screen.blit(msg_text, (GRID_OFFSET_X + 10, msg_y + 6))