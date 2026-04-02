"""
LOC (Lines of Code) chart: generates a matplotlib bar chart from yearly commit data.
Saved as a PNG and committed to the repository.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

GRAPH_PATH = Path("loc_chart.png")


def draw_loc_chart(yearly_data: dict, path: Path = GRAPH_PATH) -> None:
    """
    yearly_data format:
        { year: { quarter: { date_str: {"add": int, "del": int} } } }
    Plots net lines added per year.
    """
    year_totals: dict[str, int] = {}
    for year, quarters in yearly_data.items():
        net = 0
        for quarter in quarters.values():
            for day in quarter.values():
                net += day.get("add", 0) - day.get("del", 0)
        year_totals[str(year)] = net

    if not year_totals:
        return

    years = sorted(year_totals)
    values = [year_totals[y] for y in years]
    colors = ["#58a6ff" if v >= 0 else "#f85149" for v in values]

    fig, ax = plt.subplots(figsize=(10, 4), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")

    bars = ax.bar(years, values, color=colors, width=0.6, zorder=3)
    ax.bar_label(bars, fmt=lambda v: f"+{v:,}" if v >= 0 else f"{v:,}", color="white", fontsize=9)

    ax.set_xlabel("Year", color="white")
    ax.set_ylabel("Net Lines of Code", color="white")
    ax.set_title("Lines of Code Over the Years", color="white", fontsize=14, pad=15)
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#30363d")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="y", color="#30363d", linestyle="--", linewidth=0.7, zorder=0)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close()
    print(f"[Chart] LOC chart saved to {path}")
