"""Shared script helpers: output paths, matplotlib defaults."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = REPO_ROOT / "figures"
TABLE_DIR = REPO_ROOT / "tables"

# Ensure local package importable when scripts run from CLI
sys.path.insert(0, str(REPO_ROOT))


def configure_mpl() -> None:
    plt.rcParams.update({
        "figure.figsize": (7.0, 4.5),
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "lines.linewidth": 1.6,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "legend.fontsize": 9,
    })


def fig_path(name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    return FIG_DIR / name


def table_path(name: str) -> Path:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    return TABLE_DIR / name
