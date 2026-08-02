"""Build deterministic, valid notebooks from reviewed source cells.

The generated notebooks contain no widget state, hidden execution state, or
embedded third-party data.  Edit this source and regenerate rather than editing
the JSON by hand.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def markdown(text: str) -> dict[str, object]:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text.strip().splitlines(keepends=True),
    }


def code(text: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip().splitlines(keepends=True),
    }


def notebook(title: str, purpose: str, cells: list[dict[str, object]]) -> dict[str, object]:
    opening = markdown(
        f"# {title}\n\n{purpose}\n\n"
        "All data are generated locally unless this notebook explicitly calls a reviewed adapter. "
        "Results are educational and require independent validation before any real use."
    )
    return {
        "cells": [opening, *cells],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


NOTEBOOKS = {
    "notebooks/01_data_quality_and_dataset_switching.ipynb": notebook(
        "Data quality and dataset switching",
        "Create a legally unrestricted portfolio, inject known defects, detect them, quarantine invalid rows, and preserve an audit trail.",
        [
            code("""
from creditriskbook.data.datasets import available_datasets, load_dataset
from creditriskbook.data.quality import assess_quality, inject_teaching_defects, quarantine_invalid_rows

print("Reviewed adapters:", available_datasets())
bundle = load_dataset("synthetic_retail", n_rows=2_000, seed=101)
print(bundle.key, bundle.frame.shape, bundle.licence)
"""),
            code("""
dirty = inject_teaching_defects(bundle, seed=102, rate=0.02)
before = assess_quality(bundle, dirty)
clean, quarantine = quarantine_invalid_rows(bundle, dirty)
after = assess_quality(bundle, clean)

assert before.critical_failure
assert not after.critical_failure
assert len(quarantine) > 0
print({"dirty_rows": len(dirty), "quarantined": len(quarantine), "failed_rules": before.failed_rules})
"""),
            markdown(
                "## Student lab\n\nChange the seed and defect rate. Add an impossible category, a post-outcome feature, and a duplicated key. Explain which control should halt the run and which can be repaired under an approved rule."
            ),
        ],
    ),
    "notebooks/02_from_scratch_scorecard.ipynb": notebook(
        "From-scratch scorecard development",
        "Fit manual and automatic bins, WOE/IV, a penalised IRLS logistic model, score scaling, grades, reason codes, and characteristic tables without a scorecard library.",
        [
            code("""
from tempfile import TemporaryDirectory

from creditriskbook.data.datasets import load_dataset
from creditriskbook.models import evaluate_pd, split_dataset
from creditriskbook.scorecard import (
    BinningProcess, LogisticScorecard, export_characteristic_report,
    manual_categorical_spec, manual_numeric_spec,
)

bundle = load_dataset("synthetic_retail", n_rows=5_000, seed=202)
train, test = split_dataset(bundle, bundle.frame)
features = ["income", "employment_years", "debt_to_income", "utilisation", "enquiries_6m", "loan_amount", "product", "home_ownership"]
manual = {
    "enquiries_6m": manual_numeric_spec("enquiries_6m", [0, 1, 3, 6]),
    "product": manual_categorical_spec("product", [["personal_loan"], ["credit_card"], ["bnpl"]]),
}
"""),
            code("""
scorecard = LogisticScorecard(
    binning=BinningProcess(
        numeric_method="monotonic", max_bins=6, prebins=20,
        min_bin_fraction=0.04, min_events=5, manual_specs=manual,
    ),
    l2=1e-3,
).fit(train[features], train[bundle.target])

predicted_pd = scorecard.predict_proba(test[features])[:, 1]
scores = scorecard.score(test[features])
metrics = evaluate_pd(test[bundle.target], predicted_pd)
assert scorecard.model_.converged_
assert scores.min() >= 300 and scores.max() <= 900
print(metrics)
print(scorecard.encoder_.information_values)
"""),
            code("""
points = scorecard.points_table()
reasons = scorecard.reason_codes(test[features].iloc[:5], top_n=4)
components = scorecard.score_components(test[features].iloc[:5])
print(points.head(12).to_string(index=False))
print(reasons)
print(components[["score", "pd", "rating"]])

with TemporaryDirectory() as directory:
    paths = export_characteristic_report(scorecard, directory)
    assert all(path.exists() for path in paths.values())
"""),
            markdown(
                "## Governance questions\n\nDocument every manual cut point, compare monotonic and ChiMerge alternatives, inspect zero-event bins, challenge IV spikes for leakage, and reconcile the row score to the points table."
            ),
        ],
    ),
    "notebooks/03_ml_and_xgboost_score_mapping.ipynb": notebook(
        "Machine learning and XGBoost-compatible score mapping",
        "Fit a nonlinear challenger and map its probability to the same PDO scale. The quality CI job installs XGBoost; environments without it use a deterministic scikit-learn fallback.",
        [
            code("""
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from creditriskbook.data.datasets import load_dataset
from creditriskbook.models import evaluate_pd, split_dataset
from creditriskbook.scorecard import ModelScoreMapper

bundle = load_dataset("synthetic_retail", n_rows=6_000, seed=303)
train, test = split_dataset(bundle, bundle.frame)
features = list(bundle.numeric_features + bundle.categorical_features)
preprocess = ColumnTransformer([
    ("num", SimpleImputer(strategy="median"), list(bundle.numeric_features)),
    ("cat", Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ]), list(bundle.categorical_features)),
])

try:
    from xgboost import XGBClassifier
    estimator = XGBClassifier(
        n_estimators=180, max_depth=3, learning_rate=0.04,
        subsample=0.85, colsample_bytree=0.85, eval_metric="logloss",
        random_state=303, n_jobs=1,
    )
    model_name = "XGBoost"
except ImportError:
    estimator = HistGradientBoostingClassifier(max_iter=180, max_depth=3, learning_rate=0.04, random_state=303)
    model_name = "HistGradientBoosting fallback"

model = Pipeline([("preprocess", preprocess), ("model", estimator)])
model.fit(train[features], train[bundle.target])
"""),
            code("""
mapper = ModelScoreMapper(model, feature_names=tuple(features)).fit_reference(train[features])
predicted_pd = mapper.predict_pd(test[features])
scores = mapper.score(test[features])
reasons = mapper.reason_codes(test[features].iloc[:8], top_n=4)
metrics = evaluate_pd(test[bundle.target], predicted_pd)

assert np.all((predicted_pd >= 0) & (predicted_pd <= 1))
assert np.corrcoef(predicted_pd, scores)[0, 1] < -0.8
print(model_name, metrics)
print(reasons.head())
"""),
            markdown(
                "## Interpretation boundary\n\nProbability-to-score mapping is exact up to rounding. Sensitivity reason codes for a nonlinear model are not logistic bin points. Validate stability, actionability, correlation among features, and adverse-action requirements separately."
            ),
        ],
    ),
    "notebooks/04_evaluation_calibration_profit_and_fairness.ipynb": notebook(
        "Evaluation, calibration, profit, and group diagnostics",
        "Separate rank performance, probability accuracy, decision economics, and group outcomes.",
        [
            code("""
import pandas as pd

from creditriskbook.data.datasets import load_dataset
from creditriskbook.decisioning import cutoff_table
from creditriskbook.models import evaluate_pd, fit_pd_model, score_pd, split_dataset

bundle = load_dataset("synthetic_retail", n_rows=7_000, seed=404)
train, test = split_dataset(bundle, bundle.frame)
model = fit_pd_model(bundle, train)
predicted_pd = score_pd(model, test)
metrics = evaluate_pd(test[bundle.target], predicted_pd)
policies = cutoff_table(predicted_pd, test[bundle.target].to_numpy())
best = policies.loc[policies["realised_profit"].idxmax()]
print(metrics)
print(best.to_dict())
"""),
            code("""
audit = test[["sex", "age", bundle.target]].copy()
audit["approved"] = predicted_pd < best["pd_cutoff"]
group = audit.groupby("sex").agg(
    observations=("approved", "size"),
    approval_rate=("approved", "mean"),
    observed_default_rate=(bundle.target, "mean"),
)
group["approval_rate_ratio_to_max"] = group["approval_rate"] / group["approval_rate"].max()
print(group)
assert group["observations"].sum() == len(test)
"""),
            markdown(
                "A disparity diagnostic is a question, not a legal conclusion. Investigate sample size, label bias, legitimate need, alternative specifications, intersectional groups, uncertainty, and applicable law with qualified reviewers."
            ),
        ],
    ),
    "notebooks/05_survival_lgd_and_ead.ipynb": notebook(
        "Survival, workout LGD, and revolving EAD",
        "Construct lifetime default curves, discounted recoveries, raw LGD, and credit conversion factors with visible boundary adjustments.",
        [
            code("""
import numpy as np
import pandas as pd

from creditriskbook.risk_components import calculate_workout_lgd, construct_ccf, ead_from_ccf
from creditriskbook.survival import cumulative_pd_from_hazard, kaplan_meier

durations = np.array([3, 5, 5, 7, 9, 12, 12, 18, 24, 24], dtype=float)
events = np.array([1, 1, 0, 1, 0, 1, 0, 1, 0, 0])
curve = kaplan_meier(durations, events)
hazard_pd = cumulative_pd_from_hazard(np.array([0.02, 0.03, 0.04, 0.05]))
print(curve)
print("Cumulative PD from hazard:", hazard_pd)
"""),
            code("""
ledger = pd.DataFrame({
    "account_id": ["A", "A", "B", "B"],
    "default_date": ["2024-01-01"] * 4,
    "cashflow_date": ["2024-04-01", "2025-01-01", "2024-02-01", "2024-08-01"],
    "recovery": [2_000, 3_000, 7_000, 5_000],
    "direct_cost": [100, 150, 300, 200],
    "ead_at_default": [10_000] * 4,
    "effective_interest_rate": [0.08] * 4,
})
lgd = calculate_workout_lgd(ledger)
print(lgd)
assert {"lgd_raw", "lgd_model", "boundary_adjustment"}.issubset(lgd)
"""),
            code("""
facilities = pd.DataFrame({
    "facility_id": ["F1", "F2", "F3"],
    "drawn_reference": [4_000, 8_000, 2_000],
    "limit_reference": [10_000, 10_000, 5_000],
    "ead_at_default": [7_000, 9_500, 4_400],
})
ccf = construct_ccf(facilities)
ccf["ead_rebuilt"] = ead_from_ccf(ccf["drawn_reference"], ccf["undrawn_reference"], ccf["ccf_model"])
print(ccf)
"""),
        ],
    ),
    "notebooks/06_ifrs9_irb_and_stress.ipynb": notebook(
        "IFRS 9, IRB capital, and scenario stress",
        "Keep accounting ECL and prudential capital distinct while reconciling shared PD, LGD, and EAD inputs.",
        [
            code("""
import numpy as np
import pandas as pd

from creditriskbook.capital import corporate_irb_capital
from creditriskbook.ecl import educational_ecl

portfolio = pd.DataFrame({
    "stage": [1, 1, 2, 2, 3],
    "pd_12m": [0.005, 0.02, 0.04, 0.10, 0.45],
    "lgd": [0.35, 0.40, 0.45, 0.55, 0.65],
    "ead": [1_000_000, 750_000, 500_000, 300_000, 100_000],
    "remaining_months": [12, 36, 48, 24, 18],
    "effective_interest_rate": [0.04, 0.05, 0.045, 0.06, 0.07],
})
ecl = educational_ecl(portfolio)
assert (ecl["ecl_downside"] >= ecl["ecl_base"]).all()
print(ecl[["stage", "ecl_upside", "ecl_base", "ecl_downside", "ecl_probability_weighted"]])
"""),
            code("""
irb = corporate_irb_capital(
    portfolio["pd_12m"].to_numpy(), portfolio["lgd"].to_numpy(), portfolio["ead"].to_numpy(),
    maturity_years=np.clip(portfolio["remaining_months"].to_numpy() / 12, 1, 5),
)
reconciliation = pd.DataFrame({
    "ead": portfolio["ead"],
    "ifrs9_ecl": ecl["ecl_probability_weighted"],
    "irb_expected_loss": irb["expected_loss"],
    "irb_capital": irb["capital"],
    "rwa": irb["risk_weighted_assets"],
})
print(reconciliation)
assert np.allclose(reconciliation["rwa"], 12.5 * reconciliation["irb_capital"])
"""),
            markdown(
                "Do not force equality between IFRS 9 ECL and IRB expected loss. Horizon, cycle philosophy, floors, downturn concepts, scenario treatment, discounting, and regulatory scope differ."
            ),
        ],
    ),
    "notebooks/07_deployment_monitoring_and_agentic_controls.ipynb": notebook(
        "Deployment, monitoring, and governed agentic controls",
        "Package evidence, calculate drift, and let an agent triage only within a deterministic permission boundary.",
        [
            code("""
from creditriskbook.agents import GovernedMonitoringAgent
from creditriskbook.data.datasets import load_dataset
from creditriskbook.data.quality import assess_quality, inject_teaching_defects
from creditriskbook.monitoring import population_stability_index

bundle = load_dataset("synthetic_retail", n_rows=3_000, seed=707)
reference = bundle.frame.loc[bundle.frame["application_date"] < "2023-01-01", "utilisation"].to_numpy()
current = bundle.frame.loc[bundle.frame["application_date"] >= "2023-01-01", "utilisation"].to_numpy()
psi = population_stability_index(reference, current)
quality = assess_quality(bundle)
recommendation = GovernedMonitoringAgent().review(quality, {"pd_psi": psi, "roc_auc": 0.72})
print(recommendation.to_dict())
assert recommendation.human_approval_required
assert "approve_customer_credit" in recommendation.prohibited_actions
"""),
            code("""
dirty = inject_teaching_defects(bundle, seed=708)
halt = GovernedMonitoringAgent().review(assess_quality(bundle, dirty), {"pd_psi": 0.01, "roc_auc": 0.75})
assert halt.status == "HALT"
print(halt.recommended_action, halt.evidence_sha256)
"""),
            markdown(
                "An LLM may summarise evidence or draft a ticket. It may not invent evidence, change thresholds, approve credit, retrain, deploy, or close an incident without the separately authorised human workflow."
            ),
        ],
    ),
    "notebooks/08_public_dataset_lab.ipynb": notebook(
        "Public dataset lab",
        "Switch among checksum-verified UCI datasets or the local synthetic case. External downloads are opt-in so the notebook remains deterministic offline.",
        [
            code("""
import os

from creditriskbook.data.datasets import available_datasets, load_dataset

dataset_key = os.getenv("BOOK_DATASET", "synthetic_retail")
if dataset_key not in available_datasets():
    raise ValueError(f"Unknown BOOK_DATASET={dataset_key!r}")
bundle = load_dataset(dataset_key, n_rows=2_000, seed=808)
print({
    "key": bundle.key,
    "shape": bundle.frame.shape,
    "target": bundle.target,
    "licence": bundle.licence,
    "attribution": bundle.attribution,
    "limitations": bundle.limitations,
})
assert len(bundle.source_sha256) == 64
"""),
            markdown(
                "Try `BOOK_DATASET=uci_south_german`, `uci_taiwan_credit_card`, `uci_credit_approval`, "
                "`uci_polish_bankruptcy`, or `uci_taiwan_bankruptcy`. The Kaggle adapter requires a file "
                "downloaded under the student's own account after reviewing the current dataset page. Never "
                "treat approval as default or bankruptcy as regulatory default merely to reuse a classifier."
            ),
        ],
    ),
}


def main() -> None:
    for relative, content in NOTEBOOKS.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    invalid = ROOT / "notebooks/chapter_01_foundations/01_test_data_loaders.ipynb"
    invalid.write_text(
        json.dumps(NOTEBOOKS["notebooks/01_data_quality_and_dataset_switching.ipynb"], indent=1)
        + "\n"
    )
    print(f"Built {len(NOTEBOOKS) + 1} notebooks")


if __name__ == "__main__":
    main()
