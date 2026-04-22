"""StatsManager class - collects gameplay statistics and provides visualization"""

import pygame
import csv
import os
import math
from settings import *


class StatsManager:
    """manages collection, storage, and visualization of gameplay statistics
    
    Tracks 7 features (all with 100+ records potential):
    1. wave_stats: Per-wave performance (enemies killed, leaked, gold earned, time)
    2. tower_placements: Every tower placed (type, position, wave, time)
    3. enemy_kills: Every enemy killed (type, tower, damage, wave)
    4. gold_transactions: Every gold change (amount, reason, balance, wave)
    5. damage_events: Damage dealt per shot (tower type, damage, enemy type, wave)
    6. wave_completion_times: Time to complete each wave
    7. player_actions: Every player action (click, key press, type, timestamp)
    """

    def __init__(self):
        # per-wave aggregate stats
        self.wave_stats = []  # 1

        # individual event records
        self.tower_placements = []  # 2
        self.enemy_kills = []  # 3
        self.gold_transactions = []  # 4
        self.damage_events = []  # 5
        self.wave_completion_times = []  # 6
        self.player_actions = []  # 7

        # session tracking
        self.game_time = 0.0
        self.current_wave_start = 0.0
        self.total_kills = 0
        self.total_damage_dealt = 0
        self.total_gold_earned = 0
        self.total_gold_spent = 0
        self.total_towers_placed = 0

        # for visualization
        self.show_dashboard = False
        self.dashboard_page = 0
        self.max_pages = 3

    def update(self, dt):
        self.game_time += dt

    def record_wave_start(self, wave_num):
        self.current_wave_start = self.game_time

    def record_wave_end(self, wave_num, enemies_killed, enemies_leaked, gold_earned):
        wave_time = self.game_time - self.current_wave_start
        self.wave_stats.append({
            "wave": wave_num,
            "enemies_killed": enemies_killed,
            "enemies_leaked": enemies_leaked,
            "gold_earned": gold_earned,
            "wave_time": round(wave_time, 2),
            "game_time": round(self.game_time, 2)
        })
        self.wave_completion_times.append({
            "wave": wave_num,
            "completion_time": round(wave_time, 2),
            "kill_count": enemies_killed,
            "leak_count": enemies_leaked
        })

    def record_tower_placed(self, tower_type, col, row, wave_num, cost):
        self.total_towers_placed += 1
        self.tower_placements.append({
            "id": self.total_towers_placed,
            "tower_type": tower_type,
            "col": col,
            "row": row,
            "wave": wave_num,
            "cost": cost,
            "game_time": round(self.game_time, 2)
        })

    def record_enemy_kill(self, enemy_type, tower_type, damage_dealt, wave_num):
        self.total_kills += 1
        self.enemy_kills.append({
            "kill_id": self.total_kills,
            "enemy_type": enemy_type,
            "killed_by": tower_type,
            "damage_dealt": damage_dealt,
            "wave": wave_num,
            "game_time": round(self.game_time, 2)
        })

    def record_gold_change(self, amount, reason, balance, wave_num):
        if amount > 0:
            self.total_gold_earned += amount
        else:
            self.total_gold_spent += abs(amount)
        self.gold_transactions.append({
            "amount": amount,
            "reason": reason,
            "balance": balance,
            "wave": wave_num,
            "game_time": round(self.game_time, 2)
        })

    def record_damage(self, tower_type, damage, enemy_type, wave_num):
        self.total_damage_dealt += damage
        self.damage_events.append({
            "tower_type": tower_type,
            "damage": damage,
            "enemy_type": enemy_type,
            "wave": wave_num,
            "game_time": round(self.game_time, 2)
        })

    def record_action(self, action_type, details=""):
        self.player_actions.append({
            "action": action_type,
            "details": details,
            "game_time": round(self.game_time, 2)
        })

    def save_to_csv(self):
        """Save all statistics to CSV files."""
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats_data")
        os.makedirs(output_dir, exist_ok=True)

        datasets = {
            "wave_stats.csv": self.wave_stats,
            "tower_placements.csv": self.tower_placements,
            "enemy_kills.csv": self.enemy_kills,
            "gold_transactions.csv": self.gold_transactions,
            "damage_events.csv": self.damage_events,
            "wave_completion_times.csv": self.wave_completion_times,
            "player_actions.csv": self.player_actions,
        }

        for filename, data in datasets.items():
            if not data:
                continue
            filepath = os.path.join(output_dir, filename)
            keys = data[0].keys()
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)

    def toggle_dashboard(self):
        self.show_dashboard = not self.show_dashboard
        self.dashboard_page = 0

    def next_page(self):
        self.dashboard_page = (self.dashboard_page + 1) % self.max_pages

    def draw_dashboard(self, surface):
        # draw statistics dashboard overlay
        if not self.show_dashboard:
            return

        # semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font_title = pygame.font.SysFont(None, 36)
        font_header = pygame.font.SysFont(None, 26)
        font_text = pygame.font.SysFont(None, 22)
        font_small = pygame.font.SysFont(None, 18)

        # title
        title = font_title.render("STATISTICS DASHBOARD", True, UI_GOLD)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        page_text = font_small.render(f"Page {self.dashboard_page + 1}/{self.max_pages} (Press TAB to cycle, TAB again to close)", True, LIGHT_GRAY)
        surface.blit(page_text, (SCREEN_WIDTH // 2 - page_text.get_width() // 2, 55))

        if self.dashboard_page == 0:
            self._draw_overview_page(surface, font_header, font_text)
        elif self.dashboard_page == 1:
            self._draw_wave_charts(surface, font_header, font_text, font_small)
        elif self.dashboard_page == 2:
            self._draw_tower_stats(surface, font_header, font_text, font_small)

    def _draw_overview_page(self, surface, font_header, font_text):
        # page 1: general overview stats
        y = 90
        header = font_header.render("Game Overview", True, UI_HIGHLIGHT)
        surface.blit(header, (60, y))
        y += 35

        stats = [
            f"Total Waves Completed: {len(self.wave_stats)}",
            f"Total Enemies Killed: {self.total_kills}",
            f"Total Damage Dealt: {self.total_damage_dealt}",
            f"Total Gold Earned: {self.total_gold_earned}",
            f"Total Gold Spent: {self.total_gold_spent}",
            f"Total Towers Placed: {self.total_towers_placed}",
            f"Total Game Time: {self.game_time:.1f}s",
            f"Total Player Actions: {len(self.player_actions)}",
        ]
        for s in stats:
            text = font_text.render(s, True, UI_TEXT)
            surface.blit(text, (80, y))
            y += 26

        # records summary
        y += 20
        header2 = font_header.render("Data Records Collected", True, UI_HIGHLIGHT)
        surface.blit(header2, (60, y))
        y += 35

        records = [
            ("Wave Stats", len(self.wave_stats)),
            ("Tower Placements", len(self.tower_placements)),
            ("Enemy Kills", len(self.enemy_kills)),
            ("Gold Transactions", len(self.gold_transactions)),
            ("Damage Events", len(self.damage_events)),
            ("Wave Completion Times", len(self.wave_completion_times)),
            ("Player Actions", len(self.player_actions)),
        ]
        total_records = 0
        for name, count in records:
            total_records += count
            color = GREEN if count >= 100 else YELLOW if count >= 50 else RED
            text = font_text.render(f"{name}: {count} records", True, color)
            surface.blit(text, (80, y))
            y += 24

        y += 10
        total_text = font_text.render(f"TOTAL RECORDS: {total_records}", True, UI_GOLD)
        surface.blit(total_text, (80, y))

    def _draw_wave_charts(self, surface, font_header, font_text, font_small):
        # page 2: wave performance bar charts
        y = 90
        header = font_header.render("Wave Performance", True, UI_HIGHLIGHT)
        surface.blit(header, (60, y))
        y += 40

        if not self.wave_stats:
            text = font_text.render("No wave data yet. Complete a wave first!", True, UI_TEXT)
            surface.blit(text, (80, y))
            return

        # bar chart: kills per wave
        chart_x, chart_y = 80, y
        chart_w, chart_h = 400, 200

        label = font_text.render("Enemies Killed Per Wave", True, UI_TEXT)
        surface.blit(label, (chart_x, chart_y - 5))
        chart_y += 25

        # draw axes
        pygame.draw.line(surface, LIGHT_GRAY, (chart_x, chart_y + chart_h), (chart_x + chart_w, chart_y + chart_h), 1)
        pygame.draw.line(surface, LIGHT_GRAY, (chart_x, chart_y), (chart_x, chart_y + chart_h), 1)

        max_kills = max(w["enemies_killed"] for w in self.wave_stats) or 1
        bar_count = min(len(self.wave_stats), 15)
        bar_width = max(10, chart_w // (bar_count + 1))
        start_idx = max(0, len(self.wave_stats) - bar_count)

        for i, ws in enumerate(self.wave_stats[start_idx:]):
            bx = chart_x + 10 + i * (bar_width + 4)
            ratio = ws["enemies_killed"] / max_kills
            bh = int(ratio * (chart_h - 20))
            by = chart_y + chart_h - bh

            pygame.draw.rect(surface, (80, 160, 80), (bx, by, bar_width - 2, bh))
            pygame.draw.rect(surface, GREEN, (bx, by, bar_width - 2, bh), 1)

            # wave label
            wlabel = font_small.render(f"W{ws['wave']}", True, LIGHT_GRAY)
            surface.blit(wlabel, (bx, chart_y + chart_h + 4))

        # second chart: wave completion time
        chart_y2 = chart_y + chart_h + 50
        label2 = font_text.render("Wave Completion Time (seconds)", True, UI_TEXT)
        surface.blit(label2, (chart_x, chart_y2 - 5))
        chart_y2 += 25

        pygame.draw.line(surface, LIGHT_GRAY, (chart_x, chart_y2 + chart_h), (chart_x + chart_w, chart_y2 + chart_h), 1)
        pygame.draw.line(surface, LIGHT_GRAY, (chart_x, chart_y2), (chart_x, chart_y2 + chart_h), 1)

        max_time = max(w["wave_time"] for w in self.wave_stats) or 1
        for i, ws in enumerate(self.wave_stats[start_idx:]):
            bx = chart_x + 10 + i * (bar_width + 4)
            ratio = ws["wave_time"] / max_time
            bh = int(ratio * (chart_h - 20))
            by = chart_y2 + chart_h - bh

            pygame.draw.rect(surface, (80, 80, 180), (bx, by, bar_width - 2, bh))
            pygame.draw.rect(surface, BLUE, (bx, by, bar_width - 2, bh), 1)

            wlabel = font_small.render(f"W{ws['wave']}", True, LIGHT_GRAY)
            surface.blit(wlabel, (bx, chart_y2 + chart_h + 4))

        # right side: gold chart
        rx = 540
        label3 = font_text.render("Gold Earned Per Wave", True, UI_TEXT)
        surface.blit(label3, (rx, y - 5))
        ry = y + 25

        pygame.draw.line(surface, LIGHT_GRAY, (rx, ry + chart_h), (rx + chart_w, ry + chart_h), 1)
        pygame.draw.line(surface, LIGHT_GRAY, (rx, ry), (rx, ry + chart_h), 1)

        max_gold = max(w["gold_earned"] for w in self.wave_stats) or 1
        for i, ws in enumerate(self.wave_stats[start_idx:]):
            bx = rx + 10 + i * (bar_width + 4)
            ratio = ws["gold_earned"] / max_gold
            bh = int(ratio * (chart_h - 20))
            by = ry + chart_h - bh

            pygame.draw.rect(surface, (180, 160, 40), (bx, by, bar_width - 2, bh))
            pygame.draw.rect(surface, YELLOW, (bx, by, bar_width - 2, bh), 1)

            wlabel = font_small.render(f"W{ws['wave']}", True, LIGHT_GRAY)
            surface.blit(wlabel, (bx, ry + chart_h + 4))

    def _draw_tower_stats(self, surface, font_header, font_text, font_small):
        # page 3: tower type effectiveness
        y = 90
        header = font_header.render("Tower Performance Analysis", True, UI_HIGHLIGHT)
        surface.blit(header, (60, y))
        y += 40

        if not self.damage_events:
            text = font_text.render("No combat data yet. Play some waves!", True, UI_TEXT)
            surface.blit(text, (80, y))
            return

        # aggregate damage by tower type
        tower_damage = {}
        tower_kills = {}
        for d in self.damage_events:
            tt = d["tower_type"]
            tower_damage[tt] = tower_damage.get(tt, 0) + d["damage"]
        for k in self.enemy_kills:
            tt = k["killed_by"]
            tower_kills[tt] = tower_kills.get(tt, 0) + 1

        # pie chart: damage distribution
        label = font_text.render("Damage Distribution by Tower Type", True, UI_TEXT)
        surface.blit(label, (80, y))
        y += 30

        total_dmg = sum(tower_damage.values()) or 1
        colors = {"arrow": (80, 180, 80), "cannon": (200, 100, 80), "ice": (80, 120, 220)}
        cx, cy, radius = 200, y + 120, 100

        start_angle = 0
        for tt, dmg in tower_damage.items():
            ratio = dmg / total_dmg
            end_angle = start_angle + ratio * 2 * math.pi
            # draw pie slice
            points = [(cx, cy)]
            for a in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1):
                px = cx + radius * math.cos(math.radians(a))
                py = cy + radius * math.sin(math.radians(a))
                points.append((px, py))
            points.append((cx, cy))
            if len(points) > 2:
                pygame.draw.polygon(surface, colors.get(tt, GRAY), points)
                pygame.draw.polygon(surface, WHITE, points, 1)
            start_angle = end_angle

        # legend
        ly = y
        for tt, dmg in tower_damage.items():
            pct = (dmg / total_dmg) * 100
            pygame.draw.rect(surface, colors.get(tt, GRAY), (350, ly, 16, 16))
            ltext = font_text.render(f"{tt.title()}: {dmg} ({pct:.0f}%)", True, UI_TEXT)
            surface.blit(ltext, (375, ly))
            ly += 24

        # kill counts
        ly += 20
        kheader = font_text.render("Kills by Tower Type:", True, UI_HIGHLIGHT)
        surface.blit(kheader, (350, ly))
        ly += 28
        for tt, kills in tower_kills.items():
            ktext = font_text.render(f"{tt.title()}: {kills} kills", True, UI_TEXT)
            surface.blit(ktext, (370, ly))
            ly += 24

        # enemy kill distribution
        enemy_kill_counts = {}
        for k in self.enemy_kills:
            et = k["enemy_type"]
            enemy_kill_counts[et] = enemy_kill_counts.get(et, 0) + 1

        ry = y
        rx = 600
        eheader = font_header.render("Enemy Kill Distribution", True, UI_HIGHLIGHT)
        surface.blit(eheader, (rx, ry))
        ry += 35

        total_enemy_kills = sum(enemy_kill_counts.values()) or 1
        enemy_colors = {"normal": RED, "fast": ORANGE, "tank": PURPLE, "boss": (200, 0, 0)}

        # horizontal bar chart
        max_enemy_kills = max(enemy_kill_counts.values()) if enemy_kill_counts else 1
        bar_max_w = 300
        for et, count in sorted(enemy_kill_counts.items(), key=lambda x: -x[1]):
            label = font_text.render(f"{et.title()}", True, UI_TEXT)
            surface.blit(label, (rx, ry))
            bar_w = int((count / max_enemy_kills) * bar_max_w)
            pygame.draw.rect(surface, enemy_colors.get(et, GRAY), (rx + 80, ry + 2, bar_w, 18))
            count_text = font_small.render(f"{count}", True, WHITE)
            surface.blit(count_text, (rx + 85 + bar_w, ry + 2))
            ry += 28
