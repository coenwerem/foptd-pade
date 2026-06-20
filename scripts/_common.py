"""Shared script helpers: paths, matplotlib style, dual-format figure save."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = REPO_ROOT / "figures"
TABLE_DIR = REPO_ROOT / "tables"

sys.path.insert(0, str(REPO_ROOT))

_CMU_BOLD = Path("/usr/share/fonts/truetype/cmu/cmunsx.ttf")
_CMU_REG = Path("/usr/share/fonts/truetype/cmu/cmunss.ttf")


def configure_mpl() -> None:
    if _CMU_BOLD.exists():
        fm.fontManager.addfont(str(_CMU_BOLD))
    if _CMU_REG.exists():
        fm.fontManager.addfont(str(_CMU_REG))

    plt.rcParams.update({
        "font.family":        "sans-serif",
        "font.sans-serif":    ["CMU Sans Serif", "DejaVu Sans", "Arial"],
        "font.size":          13,
        "axes.labelsize":     18,
        "axes.titlesize":     20,
        "axes.titleweight":   "bold",
        "axes.labelweight":   "normal",
        "axes.spines.top":    True,
        "axes.spines.right":  True,
        "axes.linewidth":     1,
        "legend.fontsize":    12,
        "xtick.labelsize":    14,
        "ytick.labelsize":    14,
        "figure.dpi":         600,
        "grid.alpha":         0.12,
        "grid.linewidth":     0.3,
        "text.usetex":        False,
        "axes.unicode_minus": False,
    })


def new_figure(
    nrows: int = 1,
    ncols: int = 1,
    *,
    figsize: tuple[float, float] = (7.0, 4.5),
    left: float = 0.14,
    right: float = 0.99,
    bottom: float = 0.16,
    top: float = 0.88,
    wspace: float = 0.10,
    hspace: float = 0.32,
):
    """Create a figure + GridSpec with explicit margins (never use tight_layout)."""
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(
        nrows, ncols, figure=fig,
        left=left, right=right, bottom=bottom, top=top,
        wspace=wspace, hspace=hspace,
    )
    if nrows == 1 and ncols == 1:
        return fig, fig.add_subplot(gs[0, 0])
    axes = [[fig.add_subplot(gs[r, c]) for c in range(ncols)] for r in range(nrows)]
    return fig, axes


def save_figure(fig, stem: str) -> tuple[Path, Path]:
    """Save both PNG (600 dpi) and PDF versions; return (png_path, pdf_path)."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIG_DIR / f"{stem}.png"
    pdf_path = FIG_DIR / f"{stem}.pdf"
    fig.savefig(str(png_path), dpi=600, bbox_inches="tight",
                facecolor="white", pad_inches=0.02)
    fig.savefig(str(pdf_path), bbox_inches="tight",
                facecolor="white", pad_inches=0.02)
    return png_path, pdf_path


def fig_path(name: str) -> Path:
    """Back-compat single-PNG path (deprecated; prefer save_figure)."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    return FIG_DIR / name


def table_path(name: str) -> Path:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    return TABLE_DIR / name
