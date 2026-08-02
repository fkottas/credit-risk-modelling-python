"""Configurable IFRS 9 staging rules with reason-level audit output."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class StagingPolicy:
    """Policy inputs for a transparent staging illustration.

    The defaults are teaching assumptions, not a universal interpretation of
    significant increase in credit risk.  A real institution must approve and
    validate its indicators, rebuttals, backstops, cures, and probation rules.
    """

    stage2_dpd_backstop: int = 30
    stage3_dpd_backstop: int = 90
    relative_pd_threshold: float = 2.0
    absolute_pd_increase: float = 0.02
    low_credit_risk_exemption: bool = False
    low_credit_risk_pd: float = 0.003

    def __post_init__(self) -> None:
        if not 0 <= self.stage2_dpd_backstop < self.stage3_dpd_backstop:
            raise ValueError("DPD backstops must satisfy 0 <= stage2 < stage3")
        if self.relative_pd_threshold < 1:
            raise ValueError("relative_pd_threshold must be at least one")
        if self.absolute_pd_increase < 0 or not 0 <= self.low_credit_risk_pd <= 1:
            raise ValueError("PD policy thresholds are invalid")


def assign_stages(
    accounts: pd.DataFrame,
    policy: StagingPolicy | None = None,
) -> pd.DataFrame:
    """Assign stages and one primary reason without hiding individual flags."""

    policy = policy or StagingPolicy()
    required = {
        "account_id",
        "origination_pd_12m",
        "current_pd_12m",
        "days_past_due",
    }
    missing = required - set(accounts.columns)
    if missing:
        raise ValueError(f"Missing staging fields: {sorted(missing)}")
    result = accounts.copy()
    for column in ("origination_pd_12m", "current_pd_12m"):
        values = pd.to_numeric(result[column], errors="coerce")
        if values.isna().any() or ((values < 0) | (values > 1)).any():
            raise ValueError(f"{column} must contain probabilities in [0, 1]")
        result[column] = values
    dpd = pd.to_numeric(result["days_past_due"], errors="coerce")
    if dpd.isna().any() or (dpd < 0).any():
        raise ValueError("days_past_due must be non-negative")
    result["days_past_due"] = dpd.astype(int)
    for column in ("default_flag", "watchlist_flag", "forbearance_flag"):
        if column not in result:
            result[column] = False
        result[column] = result[column].fillna(False).astype(bool)

    denominator = np.maximum(result["origination_pd_12m"].to_numpy(float), 1e-12)
    result["pd_ratio"] = result["current_pd_12m"].to_numpy(float) / denominator
    result["pd_absolute_change"] = result["current_pd_12m"] - result["origination_pd_12m"]
    result["stage3_default_flag"] = result["default_flag"]
    result["stage3_dpd_backstop"] = result["days_past_due"] >= policy.stage3_dpd_backstop
    result["stage2_dpd_backstop"] = result["days_past_due"] >= policy.stage2_dpd_backstop
    result["stage2_watchlist"] = result["watchlist_flag"]
    result["stage2_forbearance"] = result["forbearance_flag"]
    result["stage2_relative_pd"] = result["pd_ratio"] >= policy.relative_pd_threshold
    result["stage2_absolute_pd"] = result["pd_absolute_change"] >= policy.absolute_pd_increase
    low_risk = result["current_pd_12m"] <= policy.low_credit_risk_pd
    stage2_model = result["stage2_relative_pd"] | result["stage2_absolute_pd"]
    if policy.low_credit_risk_exemption:
        stage2_model &= ~low_risk
    stage3 = result["stage3_default_flag"] | result["stage3_dpd_backstop"]
    stage2 = (
        result["stage2_dpd_backstop"]
        | result["stage2_watchlist"]
        | result["stage2_forbearance"]
        | stage2_model
    ) & ~stage3
    result["stage"] = np.select([stage3, stage2], [3, 2], default=1).astype(int)

    conditions = [
        result["stage3_default_flag"],
        result["stage3_dpd_backstop"],
        result["stage2_forbearance"] & ~stage3,
        result["stage2_watchlist"] & ~stage3,
        result["stage2_dpd_backstop"] & ~stage3,
        result["stage2_relative_pd"] & ~stage3 & ~(policy.low_credit_risk_exemption & low_risk),
        result["stage2_absolute_pd"] & ~stage3 & ~(policy.low_credit_risk_exemption & low_risk),
    ]
    reasons = [
        "default_flag",
        "90_dpd_backstop",
        "forbearance",
        "watchlist",
        "30_dpd_backstop",
        "relative_pd_increase",
        "absolute_pd_increase",
    ]
    result["stage_reason"] = np.select(conditions, reasons, default="performing")
    return result
