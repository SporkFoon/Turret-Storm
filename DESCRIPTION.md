# Project Description

## 1. Project Overview

- **Project Name:** Turret Storm
- **Brief Description:**

  Turret Storm is a wave-based tower defense game built in Python with
  Pygame. The player places three distinct tower types — Arrow, Cannon,
  and Ice — on a grass grid to stop enemies walking along a fixed path
  from a start tile to an end tile. Enemies scale in number, speed, and
  toughness with each wave, and a Boss appears every fifth wave from
  wave 10. Between waves the player upgrades and sells towers using gold
  earned from kills and wave-completion bonuses.

  Alongside gameplay, the game silently collects seven streams of
  statistics while the player plays and, on exit, writes them to CSV
  files inside `stats_data/`. A companion script
  (`data_analysis.py`, pandas + matplotlib) turns those CSVs into
  charts and a wave-summary table so the run can be inspected offline.

- **Problem Statement:**

  Two-semester Computer Programming II course projects require a full
  interactive application, structured with clean OOP, together with a
  meaningful data-collection and visualization component. Turret Storm
  does both in one project: the game is the interactive application, and
  the seven statistics streams (plus the analysis script) form the data
  component.

- **Target Users:**

  Classmates and the course grading team who want to play a complete,
  self-contained tower defense game, and anyone curious to inspect how
  their playstyle translates into tower-level / wave-level data.

- **Key Features:**

  - Three tower types (Arrow / Cannon / Ice) with distinct roles
    (single-target / splash / slow).
  - Four enemy types with per-wave health scaling and a Boss every fifth
    wave starting at wave 10.
  - Upgrade + sell economy with a 60%-refund sell price.
  - Procedurally generated pixel-art sprites (regenerable at any time
    through `scripts/generate_sprites.py`).
  - Rotating tower heads that visibly track their current target.
  - Seven streams of in-game statistics (see §5) exported as CSVs.
  - Offline analysis script (`data_analysis.py`) producing six PNG
    charts plus a wave-summary CSV.
  - In-game TAB-cycled statistics dashboard rendered directly in Pygame.

- **Proposal:** [docs/Proposal.pdf](docs/Proposal.pdf)

---

## 2. Concept

### 2.1 Background

- **Why this project exists.** Tower defense is a genre that pairs
  naturally with the OOP requirement of Computer Programming II: the
  same abstractions (path, enemy, tower, projectile, wave manager) map
  cleanly to Python classes and exhibit many of the relationships that
  the UML requirement asks us to model (composition, aggregation,
  association).
- **What inspired it.** Classic wave-based tower defense games such as
  Bloons Tower Defense and Kingdom Rush. The fixed path, per-tile
  build rules, and round-by-round economy are all idioms borrowed from
  that lineage.
- **Importance / Highlight.** The game loop is compact enough to
  implement end-to-end in one course project, yet rich enough to
  generate a sizeable, structured dataset per playthrough — which is
  exactly what the data component of the project needs.

### 2.2 Objectives

- Ship a complete, playable, and polished tower defense game written
  entirely in Python using Pygame.
- Model the game with a clean object-oriented design (6 classes,
  no god-object) and render that design as a UML class diagram.
- Instrument the game with statistics collection that never gets in the
  player's way, then expose the collected data both in-game (dashboard)
  and offline (CSV + analysis script).
- Keep the repository reproducible: a fresh clone plus
  `pip install -r requirements.txt` must be enough to run.

---

## 3. UML Class Diagram

The system is modelled with six classes. Classes, attributes, methods,
and their relationships are shown in the UML class diagram.

**Submission:**

- [docs/UML_Class_Diagram.pdf](docs/UML_Class_Diagram.pdf)

PNG preview:

![UML Class Diagram](docs/UML_Class_Diagram.png)

The diagram uses three relationship styles:

- **Composition** (solid with filled arrowhead): `Game` owns exactly one
  `GameMap` and exactly one `StatsManager`; a `Tower` owns its live
  `Projectile` instances.
- **Aggregation** (dashed with filled arrowhead): `Game` holds many
  `Tower`s and many `Enemy`s in lists whose lifetimes it manages but
  which can meaningfully be reasoned about independently.
- **Association** (dotted): `Tower`s and `Projectile`s *use* `Enemy`s as
  their targets without owning them.

---

## 4. Object-Oriented Programming Implementation

All six classes are implemented in the repository root:

- **`Game`** (`game.py`) — the top-level controller. Holds the game
  state (`playing` / `wave_active` / `game_over` / `victory`), the gold
  and lives counters, and the lists of live towers and enemies. Drives
  the main update/draw cycle, dispatches keyboard and mouse events, and
  starts waves.
- **`GameMap`** (`game_map.py`) — the tile-based map. Stores the 12 × 10
  grid from `settings.GAME_MAP`, tracks which tiles are on the enemy
  path, answers `is_buildable(col, row)` questions for the tower-placement
  UI, and draws the map using tile sprites from `assets.TILES`.
- **`Tower`** (`tower.py`) — a defensive structure placed on a grass
  tile. Tracks its type, level (1–3), gold invested, stats
  (damage/range/fire rate), live projectiles, selection state, and the
  rotation angle of its head. Each frame it picks the nearest enemy in
  range, rotates its head toward that enemy, and shoots when its fire
  timer expires.
- **`Projectile`** (`tower.py`) — a short-lived object spawned by a
  tower. Moves toward its target, handles impact (single-target,
  splash, or slow), and reports hit/kill events back to its owning
  tower so per-tower statistics stay accurate.
- **`Enemy`** (`enemy.py`) — a path-following unit. Walks between
  waypoints, accepts damage, can be slowed by Ice-tower projectiles
  (with a visible cold aura), and signals when it dies or reaches the
  end of the path.
- **`StatsManager`** (`stats_manager.py`) — the data pipeline. Exposes
  `record_*` methods the rest of the game calls whenever something
  interesting happens, renders an in-game dashboard cycled with TAB,
  and writes seven CSV files to `stats_data/` on shutdown.

---

## 5. Statistical Data

### 5.1 Data Recording Method

The game collects data during play by calling `StatsManager.record_*`
methods from the rest of the codebase at the moment each event occurs:

- `Game.place_tower()` calls `record_tower_placed()` and
  `record_gold_transaction()`.
- `Tower.update()` calls `record_damage_event()` on every hit and
  `record_enemy_kill()` when the hit is lethal.
- `Game.start_next_wave()` / wave-end logic call `record_wave_complete()`
  and `record_gold_transaction()` for the wave bonus.
- `Game.handle_key()` / `handle_click()` call `record_player_action()`.

Each record is a plain Python dict; `StatsManager` keeps them in a list
per feature. On shutdown, `main.py` calls `StatsManager.save_to_csv()`,
which writes one CSV per feature into `stats_data/`. The offline script
`data_analysis.py` reads those CSVs back with pandas and produces PNG
charts plus a wave-summary table in `stats_data/analysis/`.

### 5.2 Data Features

Seven features are recorded. Each is exported as one CSV file.

| # | Feature (CSV file) | Columns | Purpose |
|---|---|---|---|
| 1 | `wave_stats.csv` | `wave, enemies_killed, enemies_leaked, gold_earned, wave_time, game_time` | Aggregate result of each wave. |
| 2 | `tower_placements.csv` | `id, tower_type, col, row, wave, cost, game_time` | Every tower the player built. |
| 3 | `enemy_kills.csv` | `kill_id, enemy_type, killed_by, damage_dealt, wave, game_time` | Every lethal hit, broken down by enemy and killer. |
| 4 | `gold_transactions.csv` | `amount, reason, balance, wave, game_time` | Every change to the player's gold (income and expense), with running balance. |
| 5 | `damage_events.csv` | `tower_type, damage, enemy_type, wave, game_time` | Every hit — lets us compare damage output across tower types and waves. |
| 6 | `wave_completion_times.csv` | `wave, completion_time, kill_count, leak_count` | How long each wave actually took end-to-end. |
| 7 | `player_actions.csv` | `action, details, game_time` | Every click and keypress, for interaction-pattern analysis. |

From these, `data_analysis.py` derives six visualizations and a
wave-summary table (see [VISUALIZATION.md](screenshots/visualization/VISUALIZATION.md)
for per-visual explanations).

---

## 6. Changed Proposed Features

Relative to the original proposal in [docs/Proposal.pdf](docs/Proposal.pdf),
the scope of the final project is essentially as proposed. Two minor
changes:

- **Sprite art.** The proposal allowed for either hand-drawn or
  programmatically generated sprites; the final version uses
  programmatically generated pixel-art sprites produced by
  `scripts/generate_sprites.py`. This keeps the repository
  self-contained and reproducible (no external image downloads).
- **Data pipeline.** The proposal described a single "stats" file; the
  final version expands this into seven CSV features plus a companion
  analysis script (`data_analysis.py`) so the data component is richer.
  The in-game TAB dashboard is a superset of what was proposed.

No feature was dropped.

---

## 7. External Sources

Libraries (runtime / tooling; no third-party source code is
copy-pasted into the repository):

- **Pygame** — https://www.pygame.org — game rendering, input, audio
  framework. License: LGPL.
- **Pillow** — https://pillow.readthedocs.io — used only by
  `scripts/generate_sprites.py` for offline pixel-art generation.
  License: HPND.
- **pandas** — https://pandas.pydata.org — CSV loading and aggregation
  in `data_analysis.py`. License: BSD-3.
- **matplotlib** — https://matplotlib.org — chart rendering in
  `data_analysis.py` and for the UML diagram. License: PSF-compatible.

Art, music, and source code:

- All sprite art (tiles, tower bases and heads, enemies, projectiles)
  is generated procedurally by `scripts/generate_sprites.py` (Entirely generated by AI) for this
  project. No third-party sprites or music are bundled.
- No third-party source code was copy-pasted into the repository; all
  game logic was written for this project.
