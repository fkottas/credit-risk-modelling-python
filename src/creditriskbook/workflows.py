"""End-to-end teaching workflow shared by the CLI and tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from creditriskbook.agents import GovernedMonitoringAgent
from creditriskbook.data.datasets import load_dataset
from creditriskbook.data.quality import assess_quality, inject_teaching_defects, quarantine_invalid_rows
from creditriskbook.ecl import educational_ecl
from creditriskbook.models import evaluate_pd, fit_pd_model, score_pd, split_dataset
from creditriskbook.monitoring import population_stability_index


def run_end_to_end(
    dataset_key: str = "synthetic_retail",
    *,
    data_path: str | Path | None = None,
    cache_dir: str | Path = "data/raw",
    n_rows: int = 5_000,
    seed: int = 42,
    inject_defects: bool = True,
) -> dict[str, Any]:
    bundle = load_dataset(
        dataset_key,
        data_path=data_path,
        cache_dir=cache_dir,
        n_rows=n_rows,
        seed=seed,
    )
    source_frame = inject_teaching_defects(bundle, seed=seed + 1) if inject_defects else bundle.frame
    quality_before = assess_quality(bundle, source_frame)
    clean, quarantine = quarantine_invalid_rows(bundle, source_frame)
    quality_after = assess_quality(bundle, clean)
    if quality_after.critical_failure:
        raise RuntimeError(f"Critical quality failures remain after quarantine: {quality_after.failed_rules}")

    train, test = split_dataset(bundle, clean, seed=seed)
    model = fit_pd_model(bundle, train)
    train_pd = score_pd(model, train)
    test_pd = score_pd(model, test)
    metrics = evaluate_pd(test[bundle.target], test_pd)
    metrics["pd_psi"] = population_stability_index(train_pd, test_pd)

    agent = GovernedMonitoringAgent().review(quality_after, metrics)
    result: dict[str, Any] = {
        "dataset": {
            "key": bundle.key,
            "source_url": bundle.source_url,
            "licence": bundle.licence,
            "attribution": bundle.attribution,
            "source_sha256": bundle.source_sha256,
            "limitations": bundle.limitations,
            "split_strategy": bundle.split_strategy,
        },
        "rows": {
            "loaded": len(bundle.frame),
            "teaching_copy": len(source_frame),
            "clean": len(clean),
            "quarantined": len(quarantine),
            "train": len(train),
            "test": len(test),
        },
        "quality_before": quality_before.to_dict(),
        "quality_after": quality_after.to_dict(),
        "pd_metrics": metrics,
        "agent_recommendation": agent.to_dict(),
        "ecl": {"status": "not_run", "reason": "This dataset has no compatible LGD/EAD fields."},
    }

    if dataset_key == "synthetic_retail":
        scored = test[["application_id", "term_months", "interest_rate", "lgd", "ead", "days_past_due_after_12m"]].copy()
        scored["pd_12m"] = test_pd
        scored["stage"] = np.select(
            [scored["days_past_due_after_12m"] >= 90, scored["days_past_due_after_12m"] >= 30],
            [3, 2],
            default=1,
        )
        scored = scored.rename(
            columns={"term_months": "remaining_months", "interest_rate": "effective_interest_rate"}
        )
        ecl = educational_ecl(scored)
        result["ecl"] = {
            "status": "educational_simplification",
            "total_probability_weighted_ecl": float(ecl["ecl_probability_weighted"].sum()),
            "mean_ecl": float(ecl["ecl_probability_weighted"].mean()),
            "stage_counts": {str(int(key)): int(value) for key, value in ecl["stage"].value_counts().items()},
            "warning": "Uses a constant-hazard approximation and average loss timing, not contractual cash-flow ECL.",
        }
    return result


def write_run_manifest(result: dict[str, Any], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return output

