"""Transparent cut-off and profitability analysis for binary credit decisions."""

from __future__ import annotations

import numpy as np
import pandas as pd


def cutoff_table(
    predicted_pd: np.ndarray,
    outcome: np.ndarray,
    *,
    cutoffs: np.ndarray | None = None,
    performing_margin: float = 1_200.0,
    default_loss: float = 7_500.0,
    decline_cost: float = 50.0,
) -> pd.DataFrame:
    """Evaluate approve-if-PD-below-cutoff policies on matured outcomes."""

    probability = np.asarray(predicted_pd, dtype=float)
    target = np.asarray(outcome, dtype=int)
    if len(probability) != len(target) or not np.isin(target, [0, 1]).all():
        raise ValueError("Predictions and binary outcomes must have equal length")
    grid = np.asarray(cutoffs if cutoffs is not None else np.linspace(0.01, 0.50, 50), dtype=float)
    rows = []
    for cutoff in grid:
        approve = probability < cutoff
        profit = np.where(
            approve,
            np.where(target == 0, performing_margin, -default_loss),
            -decline_cost,
        )
        approved = int(approve.sum())
        rows.append(
            {
                "pd_cutoff": float(cutoff),
                "approval_rate": float(approve.mean()),
                "approved": approved,
                "approved_default_rate": float(target[approve].mean()) if approved else np.nan,
                "realised_profit": float(profit.sum()),
                "profit_per_application": float(profit.mean()),
            }
        )
    return pd.DataFrame(rows)


def expected_application_value(
    pd_values: np.ndarray,
    *,
    performing_margin: np.ndarray | float,
    loss_given_default: np.ndarray | float,
    exposure: np.ndarray | float,
    acquisition_cost: np.ndarray | float = 0.0,
) -> np.ndarray:
    pd_array = np.clip(np.asarray(pd_values, dtype=float), 0.0, 1.0)
    return (
        (1.0 - pd_array) * np.asarray(performing_margin, dtype=float)
        - pd_array * np.asarray(loss_given_default, dtype=float) * np.asarray(exposure, dtype=float)
        - np.asarray(acquisition_cost, dtype=float)
    )
