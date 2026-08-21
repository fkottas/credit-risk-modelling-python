"""Educational Basel IRB risk-weight calculations with explicit assumptions."""

from __future__ import annotations

import numpy as np
from scipy.stats import norm


def corporate_asset_correlation(pd_values: np.ndarray) -> np.ndarray:
    pd_array = np.clip(np.asarray(pd_values, dtype=float), 1e-10, 1.0)
    exponential = (1.0 - np.exp(-50.0 * pd_array)) / (1.0 - np.exp(-50.0))
    return 0.12 * exponential + 0.24 * (1.0 - exponential)


def corporate_irb_capital(
    pd_values: np.ndarray,
    lgd_values: np.ndarray,
    ead_values: np.ndarray,
    *,
    maturity_years: np.ndarray | float = 2.5,
    pd_floor: float = 0.0005,
) -> dict[str, np.ndarray]:
    """Return unexpected-loss capital, RWA, EL, and supporting parameters.

    This implements the corporate one-factor risk-weight function for teaching.
    It is not a jurisdiction-specific regulatory calculator and intentionally
    does not infer eligibility, slotting, supporting factors, output floors, or
    transitional arrangements.
    """

    pd_array = np.clip(np.asarray(pd_values, dtype=float), pd_floor, 1.0 - 1e-10)
    lgd = np.clip(np.asarray(lgd_values, dtype=float), 0.0, 1.0)
    ead = np.maximum(np.asarray(ead_values, dtype=float), 0.0)
    maturity = np.clip(np.asarray(maturity_years, dtype=float), 1.0, 5.0)
    correlation = corporate_asset_correlation(pd_array)
    b = np.square(0.11852 - 0.05478 * np.log(pd_array))
    conditional_pd = norm.cdf(
        (norm.ppf(pd_array) + np.sqrt(correlation) * norm.ppf(0.999)) / np.sqrt(1.0 - correlation)
    )
    maturity_adjustment = (1.0 + (maturity - 2.5) * b) / (1.0 - 1.5 * b)
    capital_rate = np.maximum((lgd * conditional_pd - pd_array * lgd) * maturity_adjustment, 0.0)
    expected_loss = pd_array * lgd * ead
    capital = capital_rate * ead
    return {
        "pd": pd_array,
        "lgd": lgd,
        "ead": ead,
        "asset_correlation": correlation,
        "maturity_adjustment": maturity_adjustment,
        "capital_rate": capital_rate,
        "capital": capital,
        "risk_weighted_assets": 12.5 * capital,
        "expected_loss": expected_loss,
    }


def vasicek_portfolio_loss_quantile(
    pd_value: float,
    lgd_value: float,
    *,
    asset_correlation: float,
    confidence: float = 0.999,
) -> float:
    pd_value = float(np.clip(pd_value, 1e-10, 1 - 1e-10))
    correlation = float(np.clip(asset_correlation, 0.0, 0.999999))
    conditional_pd = norm.cdf(
        (norm.ppf(pd_value) + np.sqrt(correlation) * norm.ppf(confidence))
        / np.sqrt(1 - correlation)
    )
    return float(np.clip(lgd_value, 0, 1) * conditional_pd)
