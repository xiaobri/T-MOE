"""Plot paired seed effects and conditional folder-bootstrap intervals."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from make_tables import DROPS

here = Path(__file__).resolve().parent
data = json.loads((here.parent / "results" / "summary.json").read_text())
fig, ax = plt.subplots(figsize=(6.8, 2.65))
arms = list(DROPS)[1:]
for j, arm in enumerate(arms):
    y = len(arms) - j - 1
    effects = []
    for seed in ("3", "42"):
        rows = data["ablation"][seed]["selected"]
        effects.append(100 * (rows["full"]["f1"] - rows[arm]["f1"]))
    lo, hi = data["grouped_ablation"][arm]["paired_bootstrap_full_minus_arm_pp"]
    ax.plot([lo, hi], [y, y], color="#565b66", lw=1.5, solid_capstyle="round")
    ax.scatter(np.mean(effects), y, marker="D", s=23, color="#252934", zorder=3)
    ax.scatter(effects[0], y + .16, marker="o", s=24, color="#116e90", zorder=3)
    ax.scatter(effects[1], y - .16, marker="^", s=27, color="#ac4d20", zorder=3)
ax.axvline(0, color="#717680", lw=.8, ls="--")
ax.set_yticks(list(reversed(range(len(arms)))), [DROPS[a] for a in arms])
ax.set_xlim(-.43, 1.68)
ax.set_ylim(-.5, len(arms) - .35)
ax.set_xlabel("Full model minus model with one score removed (F1 percentage points)", fontsize=9)
ax.tick_params(axis="both", labelsize=8.5, length=0)
ax.grid(axis="x", color="#e8e8e8", linewidth=.55)
ax.set_axisbelow(True)
for side in ("right", "top", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color("#a9a9a9")
handles = [
    Line2D([], [], ls="", marker="o", color="#116e90", markersize=5, label="Seed 3"),
    Line2D([], [], ls="", marker="^", color="#ac4d20", markersize=5, label="Seed 42"),
    Line2D([], [], ls="-", marker="D", color="#252934", markersize=4, label="Mean and 95% folder interval"),
]
ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(.52,1.24), ncol=3, frameon=False, fontsize=8)
fig.subplots_adjust(left=.18, bottom=.21, top=.84, right=.985)
fig.savefig(here / "figures" / "paired-ablation.pdf", metadata={"CreationDate": None})
