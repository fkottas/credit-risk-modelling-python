"""Provision-matrix construction for trade-receivable teaching cases."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_provision_matrix(
    history: pd.DataFrame,
    *,
    aging_column: str = "aging_bucket",
    exposure_column: str = "exposure",
    loss_column: str = "credit_loss",
    smoothing: float = 0.5,
    forward_multipliers: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Estimate smoothed historical loss rates and optional forward adjustments."""

    required = {aging_column, exposure_column, loss_column}
    missing = required - set(history)
    if missing:
        raise ValueError(f"Missing provision-matrix fields: {sorted(missing)}")
    if smoothing < 0 or (history[exposure_column] < 0).any() or (history[loss_column] < 0).any():
        raise ValueError("Smoothing, exposure, and credit loss must be non-negative")
    table = history.groupby(aging_column, as_index=False).agg(
        observations=(aging_column, "size"),
        exposure=(exposure_column, "sum"),
        credit_loss=(loss_column, "sum"),
    )
    portfolio_rate = (history[loss_column].sum() + smoothing) / (
        history[exposure_column].sum() + 2 * smoothing
    )
    table["historical_loss_rate"] = (table["credit_loss"] + smoothing * portfolio_rate) / (
        table["exposure"] + smoothing
    )
    multipliers = forward_multipliers or {}
    table["forward_multiplier"] = table[aging_column].map(multipliers).fillna(1.0)
    table["adjusted_loss_rate"] = np.clip(
        table["historical_loss_rate"] * table["forward_multiplier"], 0.0, 1.0
    )
    table["ecl"] = table["exposure"] * table["adjusted_loss_rate"]
    return table
