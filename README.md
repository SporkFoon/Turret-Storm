# TurretStorm - Tower Defense Game - Programming 2 Project

## Setup
```bash
pip install pygame
```

## Run the Game
```bash
cd tower_defense
python main.py
```

## Controls
| Key | Action |
|-----|--------|
| 1 / 2 / 3 | Select tower type (Arrow / Cannon / Ice) |
| Left Click | Place tower on grass tile / Select existing tower |
| U | Upgrade selected tower |
| S | Sell selected tower |
| SPACE | Start next wave |
| TAB | View statistics dashboard (cycle pages) |
| ESC | Quit game |

## Project Structure
- `main.py` - Entry point
- `settings.py` - Constants, tower/enemy configs, map layout
- `game.py` - Main Game class (controller)
- `game_map.py` - GameMap class (map rendering)
- `tower.py` - Tower and Projectile classes
- `enemy.py` - Enemy class
- `stats_manager.py` - StatsManager class (data collection + visualization)

## Classes (6 total)
1. **Game** - Main controller, manages state, UI, and all subsystems
2. **GameMap** - Tile-based map with path/grass tiles
3. **Tower** - Defensive structures with targeting, shooting, upgrades
4. **Projectile** - Projectiles with tracking, splash, and slow effects
5. **Enemy** - Path-following enemies with health, speed, slow debuffs
6. **StatsManager** - Collects 7 features, exports CSV, renders dashboard

## Statistics (7 Features)
1. Wave Stats - per-wave kills, leaks, gold, time
2. Tower Placements - every tower built
3. Enemy Kills - every kill event
4. Gold Transactions - every gold change
5. Damage Events - damage by tower type per wave
6. Wave Completion Times - time per wave
7. Player Actions - every click/keypress

Data is saved to `stats_data/` as CSV files when the game ends.
