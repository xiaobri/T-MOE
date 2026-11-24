# T-MoE for EEG window classification

**[Read the paper and experimental appendix (PDF)](paper/main.pdf)** · [LaTeX source](paper/main.tex) · [Appendix source](paper/appendix.tex) · [Aggregate results](results/summary.json)

*Regional Evidence and Bilateral Interactions for EEG Window Classification* is an English-language research preprint typeset with the official ICML 2026 preprint style. T-MoE combines five frozen regional sources and a learned global expert with matched ranking, spatial and spectral features, and a bilateral partial-information correction.

| Positive-class F1 on the original validation split | Seed 3 | Seed 42 | Mean |
| --- | ---: | ---: | ---: |
| Six-expert baseline | 69.3896% | 70.1845% | 69.7870% |
| Baseline with the same four views and head history | 69.7023% | 70.1538% | 69.9280% |
| Refreshed-pair predecessor | 72.0964% | 71.9673% | 72.0318% |
| T-MoE | 72.8352% | 73.2127% | **73.0240%** |

All four methods use the original split, paired seeds and training draw schedule. Model capacity and inference cost differ. The 166,079-window validation split also guided development. Selecting the epoch and threshold on other inferred subjects gives 72.6689% for T-MoE. The dataset has no verified patient IDs.

## External evaluation and expert activity

The four-hospital evaluation uses the source-selected models and thresholds on all 698,502 windows from Qilu, Tiantan, Chifeng and Xi’an. T-MoE reaches 45.32% equal-hospital mean F1, compared with 42.67% for the native baseline, 42.66% for the four-view baseline with head history and 45.63% for the refreshed-pair predecessor. The external results include per-seed confusion counts, precision, recall, F1, AP and AUROC. Expert activation is measured on the source validation set and all four external sites, with six routing weights and six expert positive scores captured for each of the four views. [Four-hospital results](results/external_hospitals.csv) · [Per-expert measurements](results/expert_activation.csv) · [Evaluation protocol and paired intervals](results/hospital_protocol.json)

## Appendix

- **A.** Input and training protocol, raw-input verification, and equations for drift coherence, local PID features and head history.
- **B.** Single-term deletions with reselected and locked operating points, per-seed TP/FP/FN, and cumulative reconstruction of the readout.
- **C.** Eight view-pooling policies and separately trained controls with matched parameter counts.
- **D.** Group-held selection, paired recording-folder bootstrap intervals, and sensitivity to suspected train/validation overlap.
- **E.** Locked-threshold tests at four external hospitals, equally weighted and pooled summaries, and per-site paired intervals.
- **F.** Core expert routing and positive scores by site and true label, the source top-weight shares, and the distinction between dense usage and score contribution. [External and activation appendix source](paper/hospital_appendix.tex)

## Rebuild

The PDF and generated tables and figures are checked in. From the repository root, build with Tectonic or use a standard LaTeX installation with BibTeX.

```sh
cd paper
tectonic main.tex
```

To check the aggregate confusion counts and regenerate the manuscript materials, run the following from the repository root. Figure generation requires NumPy and Matplotlib. Table generation and the result checks use only the Python standard library.

```sh
python3 results/check.py
python3 results/check_hospitals.py
python3 paper/make_tables.py
python3 paper/make_figure.py
python3 paper/make_routing_figure.py
python3 paper/make_hospital_figures.py
```

The published results contain aggregate counts, operating points and uncertainty summaries. The official style, bibliography style and accompanying LaTeX dependencies are distributed with the manuscript. [ICML 2026 author instructions](https://icml.cc/Conferences/2026/AuthorInstructions) · [Official style archive](https://media.icml.cc/Conferences/ICML2026/Styles/icml2026.zip)
