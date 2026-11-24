"""Draw the view-to-readout map for the deployed EEG classifier."""
from pathlib import Path

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(7.2, 2.5))
ax.set_xlim(0, 10)
ax.set_ylim(-.45, 6.1)
ax.axis("off")
centers = (2.8, 3.82, 4.98, 6.04)
headings = ("Original", "Mirror", "Detrended", "Detrended\nmirror")
ax.text(.07, 5.72, "Score term", weight="bold", fontsize=9)
ax.text(4.42, 5.72, "Four views of one EEG window", ha="center", weight="bold", fontsize=9)
ax.text(6.85, 5.72, "Combination rule", weight="bold", fontsize=9)
for idx, title in enumerate(headings):
    ax.text(centers[idx], 5.02, title, ha="center", va="center", fontsize=8)
rows = [
    ("Shared core", (1, 1, 1, 1), "Mean of four probabilities"),
    ("Regional / pair", (1, 1, 1, 1), "Pool orientations, then trends"),
    ("Spatial / spectrum", (1, 0, 1, 0), "Pool trend references"),
    ("Bilateral PID", (1, 1, 0, 0), "Joint class-odds correction"),
    ("Head history", (1, 1, 0, 0), "Agreement-weighted heads"),
]
for i, (name, used, rule) in enumerate(rows):
    y = 4.1 - i * .85
    ax.plot([.07,9.95],[y+.43,y+.43],color="#d8dee2",lw=.7)
    ax.text(.07,y,name,va="center",fontsize=8.5)
    ax.text(6.85,y,rule,va="center",fontsize=8.2)
    for x, enabled in zip(centers, used):
        if enabled:
            ax.plot(x,y,"o",markersize=5.7,color="#175e77")
        else:
            ax.plot([x-.065,x+.065],[y,y],color="#979fa5",lw=1)
ax.plot([.07,9.95],[.25,.25],color="#d8dee2",lw=.7)
fig.subplots_adjust(left=.01,right=.99,bottom=0,top=1)
fig.savefig(Path(__file__).parent / "figures" / "view-routing.pdf",bbox_inches="tight",pad_inches=.015,metadata={"CreationDate":None})
