"""Regenerate manuscript table bodies from the public aggregate results."""
import json
from pathlib import Path
from statistics import mean

PAPER = Path(__file__).resolve().parent
DATA = json.loads((PAPER.parent / "results" / "summary.json").read_text())
SEEDS = ("3", "42")
DROPS = {
    "full": "Full model",
    "without_regional": "Regional fusion",
    "without_pair_rank": "Matched ranking",
    "without_history": "Head history",
    "without_spectrum_video": "Spectrum video",
    "without_spatial": "Spatial field",
    "without_pid": "Bilateral PID",
}
PRIMARY = {
    "strict_baseline": "Six-expert baseline",
    "baseline_same_views_and_history": "Baseline + views/history",
    "fresh_both": "Refreshed-pair predecessor",
    "quality_drift_coherence": "T-MoE",
}


def pct(value):
    return f"{100 * value:.4f}"


def save(name, rows):
    (PAPER / "tables" / f"{name}.tex").write_text("".join(
        " & ".join(str(cell) for cell in row) + r" \\" + "\n" for row in rows
    ))


def scores(name, policy):
    return [DATA["ablation"][seed][policy][name]["f1"] for seed in SEEDS]


def main():
    (PAPER / "tables").mkdir(exist_ok=True)
    primary, sensitivity = [], []
    for name, label in PRIMARY.items():
        row = DATA["primary"][name]
        primary.append([label, *map(pct, row["by_seed"]), pct(row["mean"])])
        sensitivity.append([label, *map(pct, [row["mean"], row["held"], row["excluded_overlap"]])])
    save("primary", primary)
    save("sensitivity", sensitivity)
    drop, transfer, operating = [], [], []
    total = mean(scores("full", "selected"))
    for name, label in DROPS.items():
        values = scores(name, "selected")
        difference = 100 * (total - mean(values))
        drop.append([label, *map(pct, values), pct(mean(values)), f"{difference:.4f}",
                     pct(mean(scores(name, "locked")))])
        outcome = DATA["grouped_ablation"][name]
        held = [outcome["held_by_seed"][seed]["f1"] for seed in SEEDS]
        lo, hi = outcome["paired_bootstrap_full_minus_arm_pp"]
        transfer.append([label, *map(pct, held), pct(mean(held)),
                         "--" if name == "full" else f"[{lo:.3f}, {hi:.3f}]"])
        cells = [label]
        for seed in SEEDS:
            choice = DATA["ablation"][seed]["selected"][name]
            cells.extend([choice["epoch"], f"{choice['threshold']:.2f}",
                          f"{choice['tp']:,}", f"{choice['fp']:,}", f"{choice['fn']:,}"])
        operating.append(cells)
    save("drop", drop)
    save("held", transfer)
    save("operating", operating)
    chain = []
    stages = [
        ("core_with_views_and_history", "Shared core, four views and history"),
        ("through_regional", "+ regional fusion"),
        ("through_pair_rank", "+ matched ranking"),
        ("through_spatial", "+ spatial field"),
        ("through_spectrum_video", "+ spectrum video"),
        ("full", "+ bilateral PID"),
    ]
    previous = None
    for name, label in stages:
        values = scores(name, "selected")
        current = mean(values)
        chain.append([label, *map(pct, values), pct(current),
                      "--" if previous is None else f"{100 * (current - previous):+.4f}"])
        previous = current
    save("chain", chain)
    policies = {
        "original": "Native increments only",
        "regional_and_paired": "Average regional and pair increments over all views",
        "field_and_movie": "Average field and video over native and detrended views",
        "full_orbit": "Average all increments over all four views",
        "quality_equal": "Orientation-aware pooling, equal trend weights",
        "quality_drift_energy": "Weight by total drift energy",
        "quality_lateralized": "Weight by left--right asymmetry",
        "quality_drift_coherence": "Weight by drift coherence (T-MoE)",
    }
    views = []
    for name, label in policies.items():
        values = [DATA["view_policy"][s][name]["f1"] for s in SEEDS]
        views.append([label, *map(pct, values), pct(mean(values))])
    save("views", views)
    controls = {
        "baseline": "Cached six-expert baseline",
        "video_uniform": "One background group",
        "video_eeg_only": "Online spectral groups",
        "stationary_eeg": "Stationary waveform groups",
        "stable_soft_diag": "Soft background matching",
        "neighbor_fixed": "Fixed neighboring-group support",
    }
    save("training", [[controls[row["method"]], f"{row['parameters_trainable']:,}",
                       *map(pct, row["seed_f1"]), pct(row["mean"])] for row in DATA["training_controls"]])


if __name__ == "__main__":
    main()
