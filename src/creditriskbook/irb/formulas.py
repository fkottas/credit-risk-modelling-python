"""Basel one-factor IRB risk-weight functions for major teaching asset classes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from scipy.stats import norm

IRBAssetClass = Literal[
    "corporate",
    "sme_corporate",
    "residential_mortgage",
    "qualifying_revolving_retail",
    "other_retail",
]


@dataclass(frozen=True)
class IRBResult:
    rows: pd.DataFrame
    summary: dict[str, float]


def _as_array(values: np.ndarray | float, length: int | None = None) -> np.ndarray:
    array = np.atleast_1d(np.asarray(values, dtype=float))
    if length is not None:
        array = np.broadcast_to(array, (length,)).astype(float, copy=True)
    if not np.isfinite(array).all():
        raise ValueError("IRB inputs must be finite")
    return array


def asset_correlation(
    pd_values: np.ndarray,
    asset_class: IRBAssetClass,
    *,
    annual_sales_eur_millions: np.ndarray | float | None = None,
) -> np.ndarray:
    """Return the prescribed asset-correlation function for an asset class."""

    pd_array = np.clip(_as_array(pd_values), 1e-10, 1 - 1e-10)
    if asset_class in {"corporate", "sme_corporate"}:
        weight = (1.0 - np.exp(-50.0 * pd_array)) / (1.0 - np.exp(-50.0))
        correlation = 0.12 * weight + 0.24 * (1.0 - weight)
        if asset_class == "sme_corporate":
            if annual_sales_eur_millions is None:
                raise ValueError("SME corporate correlation requires annual sales")
            sales = np.clip(_as_array(annual_sales_eur_millions, len(pd_array)), 5.0, 50.0)
            correlation -= 0.04 * (1.0 - (sales - 5.0) / 45.0)
        return correlation
    if asset_class == "residential_mortgage":
        return np.full_like(pd_array, 0.15)
    if asset_class == "qualifying_revolving_retail":
        return np.full_like(pd_array, 0.04)
    if asset_class == "other_retail":
        weight = (1.0 - np.exp(-35.0 * pd_array)) / (1.0 - np.exp(-35.0))
        return 0.03 * weight + 0.16 * (1.0 - weight)
    raise ValueError(f"Unsupported IRB asset class: {asset_class}")


def maturity_adjustment(pd_values: np.ndarray, maturity_years: np.ndarray | float) -> np.ndarray:
    """Return the corporate effective-maturity adjustment."""

    pd_array = np.clip(_as_array(pd_values), 1e-10, 1 - 1e-10)
    maturity = np.clip(_as_array(maturity_years, len(pd_array)), 1.0, 5.0)
    b = np.square(0.11852 - 0.05478 * np.log(pd_array))
    denominator = 1.0 - 1.5 * b
    if np.any(denominator <= 0):
        raise ValueError("Maturity adjustment is undefined for the supplied PD")
    return (1.0 + (maturity - 2.5) * b) / denominator


def irb_capital(
    pd_values: np.ndarray,
    lgd_values: np.ndarray | float,
    ead_values: np.ndarray | float,
    *,
    asset_class: IRBAssetClass = "corporate",
    maturity_years: np.ndarray | float = 2.5,
    annual_sales_eur_millions: np.ndarray | float | None = None,
    pd_floor: float = 0.0005,
    confidence: float = 0.999,
) -> IRBResult:
    """Calculate base IRB K, capital, RWA, and EL with visible inputs.

    Eligibility, parameter floors beyond the user-supplied PD floor,
    specialised-lending slotting, currency-specific adjustments, supporting
    factors, output floors, expected-loss/provision treatment, and national
    discretions are outside this function and must be handled by policy.
    """

    if not 0 < pd_floor < 1 or not 0.5 < confidence < 1:
        raise ValueError("pd_floor and confidence are outside valid ranges")
    raw_pd = _as_array(pd_values)
    n = len(raw_pd)
    if np.any((raw_pd < 0) | (raw_pd > 1)):
        raise ValueError("PD must be in [0, 1]")
    pd_array = np.clip(raw_pd, pd_floor, 1 - 1e-10)
    lgd = _as_array(lgd_values, n)
    ead = _as_array(ead_values, n)
    if np.any((lgd < 0) | (lgd > 1)) or np.any(ead < 0):
        raise ValueError("LGD must be in [0, 1] and EAD must be non-negative")
    correlation = asset_correlation(
        pd_array,
        asset_class,
        annual_sales_eur_millions=annual_sales_eur_millions,
    )
    conditional_pd = norm.cdf(
        (norm.ppf(pd_array) + np.sqrt(correlation) * norm.ppf(confidence))
        / np.sqrt(1.0 - correlation)
    )
    if asset_class in {"corporate", "sme_corporate"}:
        adjustment = maturity_adjustment(pd_array, maturity_years)
    else:
        adjustment = np.ones(n)
    capital_rate = np.maximum((lgd * conditional_pd - pd_array * lgd) * adjustment, 0.0)
    rows = pd.DataFrame(
        {
            "asset_class": asset_class,
            "pd_raw": raw_pd,
            "pd": pd_array,
            "pd_floor_adjustment": pd_array - raw_pd,
            "lgd": lgd,
            "ead": ead,
            "asset_correlation": correlation,
            "conditional_pd": conditional_pd,
            "maturity_adjustment": adjustment,
            "capital_rate": capital_rate,
            "capital": capital_rate * ead,
            "risk_weighted_assets": 12.5 * capital_rate * ead,
            "expected_loss": pd_array * lgd * ead,
        }
    )
    summary = {
        "exposure": float(rows["ead"].sum()),
        "capital": float(rows["capital"].sum()),
        "risk_weighted_assets": float(rows["risk_weighted_assets"].sum()),
        "expected_loss": float(rows["expected_loss"].sum()),
        "weighted_average_risk_weight": float(
            rows["risk_weighted_assets"].sum() / rows["ead"].sum() if rows["ead"].sum() > 0 else 0.0
        ),
    }
    return IRBResult(rows=rows, summary=summary)
