# Executable student labs

The nine notebooks are deliberately small enough to rerun and rich enough to modify. They cover data-quality failure injection, from-scratch scorecards, nonlinear challengers and XGBoost-compatible score mapping, evaluation and fairness diagnostics, survival/LGD/EAD, IFRS 9 and IRB, governed agentic monitoring, and public-dataset switching.

Every notebook is generated from `tools/build_notebooks.py` and enforced by `tools/validate_notebooks.py`. The validator checks notebook JSON and executes all code cells in a fresh Python process; GitHub Actions runs it on Python 3.11 and 3.12.

External data are opt-in. The default path uses deterministic synthetic data. Set `BOOK_DATASET` to a reviewed UCI key for a live download, or place the permitted Kaggle file in the documented local path after accepting its current terms.
