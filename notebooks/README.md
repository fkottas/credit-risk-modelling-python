# Executable student labs

The sixteen notebooks are deliberately small enough to rerun and rich enough to modify. They cover data-quality failure injection, from-scratch scorecards, nonlinear challengers and XGBoost-compatible score mapping, evaluation and fairness diagnostics, survival/LGD/EAD, IFRS 9 staging and reconciliation, IRB asset classes and calibration, scorecard diagnostics and presentations, governed agentic controls, synthetic component cases, public-dataset switching, behavioural cleaning and features, NLP retrieval, structured LLM outputs, and a bounded document-underwriting agent.

Every notebook is generated from `tools/build_notebooks.py` and enforced by `tools/validate_notebooks.py`. The validator checks notebook JSON and executes all code cells in a fresh Python process; GitHub Actions runs it on Python 3.11 and 3.12.

External data are opt-in. The default path uses deterministic synthetic data. Set `BOOK_DATASET` to a reviewed UCI key for a live download, or place the permitted Kaggle file in the documented local path after accepting its current terms.
