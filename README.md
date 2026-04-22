# Turret Storm

## Project Description

- **Project by:** Navin Bunthuphanich (6610545251)
- **Course:** Computer Programming II (01219116 / 01219117) — 2026/2, Section 450
- **Game Genre:** Tower Defense, Strategy

Turret Storm is a wave-based tower defense game built in Python with Pygame.
The player buys and places three kinds of defensive towers on a grass grid to
stop waves of enemies marching along a fixed path from the start tile to the
end tile. Towers target, shoot, upgrade, and can be sold back for a partial
refund. The game also silently collects seven streams of gameplay statistics
and, when the game ends, exports them to CSV files for offline analysis and
visualization.

---

## Installation

To clone this project:

```sh
git clone https://github.com/SporkFoon/Turret-Storm.git
cd Turret-Storm
```

To create and run a Python environment for this project:

**Windows**

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac / Linux**

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running Guide

After activating the Python environment of this project, run the game with:

**Windows**

```bat
python main.py
```

**Mac / Linux**

```sh
python3 main.py
```

To run the offline data-analysis script (after you have played at least one
game, so that `stats_data/` has CSVs in it):

**Windows**

```bat
python data_analysis.py
```

**Mac / Linux**

```sh
python3 data_analysis.py
```

Charts and a wave-summary CSV will be written to `stats_data/analysis/`.

---

## Tutorial / Usage

1. The game opens on a 12 x 10 tile map. Green tiles are grass (buildable),
   brown tiles are the path enemies will walk along, and the coloured tiles
   at the path endpoints are the start and the end.
2. Press **1**, **2**, or **3** to pick a tower type (Arrow / Cannon / Ice).
3. **Left-click** a grass tile to place the selected tower, or **left-click**
   an existing tower to select it.
4. With a tower selected, press **U** to upgrade it or **S** to sell it.
5. Press **SPACE** to start the next wave. Enemies spawn from the start tile
   and follow the path to the end; every enemy that reaches the end costs
   you a life.
6. Press **TAB** while playing to cycle through the in-game statistics
   dashboard pages.
7. Press **ESC** to quit. On quit, all collected statistics are exported to
   `stats_data/*.csv`.

| Key         | Action                                                |
|-------------|-------------------------------------------------------|
| 1 / 2 / 3   | Select tower type (Arrow / Cannon / Ice)              |
| Left-click  | Place tower on a grass tile / select existing tower   |
| U           | Upgrade the selected tower                            |
| S           | Sell the selected tower (60% refund)                  |
| SPACE       | Start the next wave                                   |
| TAB         | Cycle statistics dashboard pages                      |
| ESC         | Quit (also writes `stats_data/*.csv`)                 |

---

## Game Features

- **Three tower types** with distinct roles:
  - *Arrow Tower* — fast, cheap, single-target damage.
  - *Cannon Tower* — slow fire rate but splash damage over an area.
  - *Ice Tower* — lower damage, but slows enemies on hit.
- **Four enemy types** that scale with wave number: Grunt, Scout (fast),
  Tank (high-HP), and a Boss that appears on every fifth wave from wave 10.
- **Upgrade system** — each tower can be upgraded twice, increasing its
  damage and range.
- **Economy** — start with 200 gold, earn gold per kill and a wave bonus,
  and sell towers for 60% of total gold invested.
- **Procedurally generated pixel-art sprites** — the game ships with PNG
  assets in `assets/`, and `scripts/generate_sprites.py` can regenerate them
  from scratch with Pillow.
- **Rotating tower heads** — every tower's cannon/barrel rotates in real
  time to track the enemy it's aiming at.
- **Seven streams of in-game statistics** (see DESCRIPTION.md §5) saved on
  exit as CSVs for offline analysis.
- **Offline analysis script** (`data_analysis.py`) that uses pandas +
  matplotlib to produce six charts and a per-wave summary CSV from the
  exported data.

---

## Known Bugs

- If the game window is closed with the OS close button before any wave
  starts, the CSV files will still be written but will only contain the
  initial 200-gold starting-gold entry.
- When the game runs at a very low frame rate (<20 FPS), projectile
  collision detection can miss fast enemies at the extreme edge of a
  tower's range. Frame-rate capping keeps this a corner case.

---

## Unfinished Works

All work planned for the 22 Apr milestone is complete: game, statistics
collection, CSV export, offline analysis script, UML diagram, and
guideline-aligned documentation.

---

## External sources

Acknowledgements:

1. Pygame — https://www.pygame.org — game rendering, input, and audio
   framework (LGPL).
2. Pillow — https://pillow.readthedocs.io — used only by
   `scripts/generate_sprites.py` to (re)generate the pixel-art assets
   (HPND license).
3. pandas — https://pandas.pydata.org — tabular data analysis in
   `data_analysis.py` (BSD-3).
4. matplotlib — https://matplotlib.org — chart rendering in
   `data_analysis.py` (PSF-compatible license).

All sprite art (tiles, towers, enemies, projectiles) was generated
procedurally by `scripts/generate_sprites.py` (AI Generated) for this project; no
third-party art, music, or source code is redistributed in this repository.
