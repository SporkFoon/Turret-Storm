"""
data_analysis.py

Offline analysis + visualization for the gameplay CSVs exported by
StatsManager into ``stats_data/``

Run from the project root *after* playing at least one game:

    python data_analysis.py

The script produces PNG charts and a small summary table inside
``stats_data/analysis/`` and also prints a text summary to the console.
It uses pandas for aggregation and matplotlib for plotting so the same
analysis can be reproduced headlessly (e.g. for a report)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render off-screen
import matplotlib.pyplot as plt
import pandas as pd


# paths
ROOT = Path(__file__).resolve().parent
STATS_DIR = ROOT / "stats_data"
OUT_DIR = STATS_DIR / "analysis"


CSV_FILES = {
    "wave_stats": "wave_stats.csv",
    "tower_placements": "tower_placements.csv",
    "enemy_kills": "enemy_kills.csv",
    "gold_transactions": "gold_transactions.csv",
    "damage_events": "damage_events.csv",
    "wave_completion_times": "wave_completion_times.csv",
    "player_actions": "player_actions.csv",
}


# loading
def load_all() -> dict[str, pd.DataFrame]:
    # load every CSV into a dict of DataFrames

    if not STATS_DIR.exists():
        sys.exit(
            f"stats_data/ not found at {STATS_DIR}\n"
            "Play at least one game so the game can export CSVs first."
        )

    frames: dict[str, pd.DataFrame] = {}
    for key, name in CSV_FILES.items():
        path = STATS_DIR / name
        if path.exists() and path.stat().st_size > 0:
            frames[key] = pd.read_csv(path)
        else:
            frames[key] = pd.DataFrame()
    return frames


# aggregations
def wave_summary(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # per-wave summary: kills, leaks, gold, time, kill-rate
    ws = frames["wave_stats"].copy()
    if ws.empty:
        return ws
    ws["kill_rate"] = ws["enemies_killed"] / (
        ws["enemies_killed"] + ws["enemies_leaked"]
    ).replace(0, pd.NA)
    return ws


def damage_by_tower(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # total damage each tower type dealt across the whole run
    de = frames["damage_events"]
    if de.empty:
        return pd.DataFrame(columns=["tower_type", "damage"])
    return (
        de.groupby("tower_type", as_index=False)["damage"]
        .sum()
        .sort_values("damage", ascending=False)
    )


def kills_by_enemy(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # how many enemies of each type were killed
    ek = frames["enemy_kills"]
    if ek.empty:
        return pd.DataFrame(columns=["enemy_type", "kills"])
    return (
        ek.groupby("enemy_type", as_index=False)
        .size()
        .rename(columns={"size": "kills"})
        .sort_values("kills", ascending=False)
    )


def gold_balance_over_time(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # running gold balance
    gt = frames["gold_transactions"]
    if gt.empty:
        return gt
    return gt.sort_values("game_time")[["game_time", "balance"]]


def towers_placed(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # how many of each tower type the player actually built
    tp = frames["tower_placements"]
    if tp.empty:
        return pd.DataFrame(columns=["tower_type", "built"])
    return (
        tp.groupby("tower_type", as_index=False)
        .size()
        .rename(columns={"size": "built"})
        .sort_values("built", ascending=False)
    )


# plotting
def _save(fig: plt.Figure, name: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / name
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def plot_wave_kill_leak(ws: pd.DataFrame) -> Path | None:
    if ws.empty:
        return None
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = ws["wave"].astype(int)
    width = 0.4
    ax.bar(x - width / 2, ws["enemies_killed"], width, label="Killed", color="#3aa655")
    ax.bar(x + width / 2, ws["enemies_leaked"], width, label="Leaked", color="#d94f4f")
    ax.set_xlabel("Wave")
    ax.set_ylabel("Enemies")
    ax.set_title("Kills vs leaks per wave")
    ax.set_xticks(x)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    return _save(fig, "01_kills_vs_leaks_per_wave.png")


def plot_damage_by_tower(df: pd.DataFrame) -> Path | None:
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["tower_type"], df["damage"], color=["#6ea84f", "#a65a3a", "#5a7fc7"])
    ax.set_xlabel("Tower type")
    ax.set_ylabel("Total damage dealt")
    ax.set_title("Total damage by tower type")
    for i, v in enumerate(df["damage"]):
        ax.text(i, v, f"{int(v):,}", ha="center", va="bottom", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    return _save(fig, "02_damage_by_tower.png")


def plot_kills_by_enemy(df: pd.DataFrame) -> Path | None:
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["enemy_type"], df["kills"], color="#8860b8")
    ax.set_xlabel("Enemy type")
    ax.set_ylabel("Kills")
    ax.set_title("Kills by enemy type")
    for i, v in enumerate(df["kills"]):
        ax.text(i, v, str(int(v)), ha="center", va="bottom", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    return _save(fig, "03_kills_by_enemy.png")


def plot_gold_over_time(df: pd.DataFrame) -> Path | None:
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["game_time"], df["balance"], color="#c9a227", linewidth=1.8)
    ax.fill_between(df["game_time"], df["balance"], alpha=0.2, color="#c9a227")
    ax.set_xlabel("Game time (s)")
    ax.set_ylabel("Gold balance")
    ax.set_title("Gold balance over time")
    ax.grid(linestyle="--", alpha=0.4)
    return _save(fig, "04_gold_over_time.png")


def plot_towers_built(df: pd.DataFrame) -> Path | None:
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["tower_type"], df["built"], color=["#6ea84f", "#a65a3a", "#5a7fc7"])
    ax.set_xlabel("Tower type")
    ax.set_ylabel("Number built")
    ax.set_title("Towers built by type")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    return _save(fig, "05_towers_built.png")


def plot_wave_time(ws: pd.DataFrame) -> Path | None:
    if ws.empty or "wave_time" not in ws.columns:
        return None
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ws["wave"], ws["wave_time"], marker="o", color="#3a6ea5")
    ax.set_xlabel("Wave")
    ax.set_ylabel("Completion time (s)")
    ax.set_title("Wave completion time")
    ax.grid(linestyle="--", alpha=0.4)
    return _save(fig, "06_wave_completion_time.png")


# reporting
def print_text_summary(frames: dict[str, pd.DataFrame]) -> None:
    print("\n=== Turret Storm — Run summary ===")
    ws = frames["wave_stats"]
    if not ws.empty:
        total_killed = int(ws["enemies_killed"].sum())
        total_leaked = int(ws["enemies_leaked"].sum())
        total_gold = int(ws["gold_earned"].sum())
        total_time = float(ws["wave_time"].sum())
        print(f"Waves played:       {len(ws)}")
        print(f"Enemies killed:     {total_killed}")
        print(f"Enemies leaked:     {total_leaked}")
        kr = total_killed / max(1, total_killed + total_leaked)
        print(f"Overall kill rate:  {kr:.1%}")
        print(f"Gold earned:        {total_gold}")
        print(f"Time in waves:      {total_time:.1f}s")

    db = damage_by_tower(frames)
    if not db.empty:
        print("\nDamage by tower type:")
        for _, row in db.iterrows():
            print(f"  {row['tower_type']:<7} {int(row['damage']):>8,}")

    tb = towers_placed(frames)
    if not tb.empty:
        print("\nTowers built:")
        for _, row in tb.iterrows():
            print(f"  {row['tower_type']:<7} {int(row['built']):>3}")


def write_summary_csv(frames: dict[str, pd.DataFrame]) -> Path | None:
    ws = wave_summary(frames)
    if ws.empty:
        return None
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "wave_summary.csv"
    ws.to_csv(path, index=False)
    return path


# entry point
def main() -> None:
    frames = load_all()

    ws = wave_summary(frames)
    db = damage_by_tower(frames)
    ke = kills_by_enemy(frames)
    gb = gold_balance_over_time(frames)
    tb = towers_placed(frames)

    produced: list[Path] = []
    for fn, arg in [
        (plot_wave_kill_leak, ws),
        (plot_damage_by_tower, db),
        (plot_kills_by_enemy, ke),
        (plot_gold_over_time, gb),
        (plot_towers_built, tb),
        (plot_wave_time, ws),
    ]:
        p = fn(arg)
        if p is not None:
            produced.append(p)

    summary_csv = write_summary_csv(frames)
    if summary_csv is not None:
        produced.append(summary_csv)

    print_text_summary(frames)
    if produced:
        print("\nArtifacts written to:")
        for p in produced:
            print(f"  - {p.relative_to(ROOT)}")
    else:
        print("\nNo artifacts produced (stats_data/ appears to be empty).")


if __name__ == "__main__":
    main()
