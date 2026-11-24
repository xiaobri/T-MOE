"""Verify the published F1 values against aggregate confusion counts and policies."""
import json
from math import isclose
from pathlib import Path
from statistics import mean

summary = json.loads(Path(__file__).with_name("summary.json").read_text())
seeds = ("3", "42")
positives = summary["manifest"]["validation_positives"]


def verify(row):
    tp, fp, fn = (row[k] for k in ("tp", "fp", "fn"))
    assert tp + fn == positives
    assert isclose(2 * tp / (2 * tp + fp + fn), row["f1"], abs_tol=1e-12)


for seed in seeds:
    selected = summary["ablation"][seed]["selected"]
    locked = summary["ablation"][seed]["locked"]
    for row in [*selected.values(), *locked.values()]:
        verify(row)
    replay = summary["threshold_replay"][seed]
    verify(replay["raw"])
    assert replay["changed_threshold_decisions"] == 0
    assert replay["reference_vs_export_threshold_decisions_changed"] == 0
    assert len(replay["epoch_grid_best"]) == 20
    for row in replay["epoch_grid_best"]:
        verify(row)
    best = max(replay["epoch_grid_best"], key=lambda row: (row["f1"], row["epoch"]))
    assert best == selected["full"]
    assert best["f1"] == replay["raw"]["f1"]
    for arm in summary["grouped_ablation"].values():
        verify(arm["held_by_seed"][seed])
    assert selected["without_pid"]["f1"] == selected["through_spectrum_video"]["f1"]
    assert locked["without_pid"] == summary["ablation"][seed]["raw_without_pid_at_released_threshold"]

primary = summary["primary"]
for arm in primary.values():
    assert isclose(mean(arm["by_seed"]), arm["mean"], abs_tol=1e-12)
assert isclose(mean(summary["grouped_ablation"]["full"]["held_by_seed"][s]["f1"]
                    for s in seeds), primary["quality_drift_coherence"]["held"], abs_tol=1e-12)
print("Verified both primary raw replays, 40 epoch results and the ablation confusion counts.")
