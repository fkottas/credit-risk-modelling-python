"""Cash-flow-aware, multi-scenario expected-credit-loss teaching engine."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .curves import hazard_to_marginal, marginal_to_hazard, scale_hazard


@dataclass(frozen=True)
class Scenario:
    name: str
    weight: float
    pd_multiplier: float = 1.0
    lgd_multiplier: float = 1.0
    ead_multiplier: float = 1.0

    def __post_init__(self) -> None:
        values = (self.weight, self.pd_multiplier, self.lgd_multiplier, self.ead_multiplier)
        if not self.name or not all(np.isfinite(values)) or any(value < 0 for value in values):
            raise ValueError("Scenario name and non-negative finite parameters are required")


@dataclass(frozen=True)
class ECLConfig:
    periods_per_year: int = 12
    stage1_horizon_periods: int = 12
    period_column: str = "period"

    def __post_init__(self) -> None:
        if self.periods_per_year < 1 or self.stage1_horizon_periods < 1:
            raise ValueError("ECL period settings must be positive")


@dataclass(frozen=True)
class ECLResult:
    account: pd.DataFrame
    scenario: pd.DataFrame
    detail: pd.DataFrame
    reconciliation: pd.DataFrame


def _validate_schedule(schedule: pd.DataFrame, config: ECLConfig) -> pd.DataFrame:
    required = {
        "account_id",
        config.period_column,
        "stage",
        "marginal_pd",
        "lgd",
        "ead",
        "effective_interest_rate",
    }
    missing = required - set(schedule.columns)
    if missing:
        raise ValueError(f"Missing ECL schedule fields: {sorted(missing)}")
    frame = schedule.copy().sort_values(["account_id", config.period_column])
    if frame.duplicated(["account_id", config.period_column]).any():
        raise ValueError("Each account-period pair must be unique")
    if not frame["stage"].isin([1, 2, 3]).all():
        raise ValueError("stage must be 1, 2, or 3")
    if (frame[config.period_column] < 1).any():
        raise ValueError("periods must begin at one or later")
    for column in ("marginal_pd", "lgd"):
        if frame[column].isna().any() or ((frame[column] < 0) | (frame[column] > 1)).any():
            raise ValueError(f"{column} must contain probabilities in [0, 1]")
    if (frame["ead"] < 0).any() or (frame["effective_interest_rate"] <= -1).any():
        raise ValueError("EAD must be non-negative and EIR must exceed -100%")
    if frame.groupby("account_id")["stage"].nunique().gt(1).any():
        raise ValueError("Stage must be constant within an account calculation date")
    if frame.groupby("account_id")["marginal_pd"].sum().gt(1 + 1e-10).any():
        raise ValueError("Account marginal PDs cannot sum to more than one")
    return frame


def calculate_ecl(
    schedule: pd.DataFrame,
    scenarios: tuple[Scenario, ...] | list[Scenario],
    *,
    config: ECLConfig | None = None,
) -> ECLResult:
    """Calculate discounted, scenario-weighted ECL with auditable detail."""

    config = config or ECLConfig()
    if not scenarios or len({scenario.name for scenario in scenarios}) != len(scenarios):
        raise ValueError("At least one uniquely named scenario is required")
    if not np.isclose(sum(scenario.weight for scenario in scenarios), 1.0):
        raise ValueError("Scenario weights must sum to one")
    base = _validate_schedule(schedule, config)
    details: list[pd.DataFrame] = []
    for scenario in scenarios:
        pieces: list[pd.DataFrame] = []
        for _, account in base.groupby("account_id", sort=False):
            item = account.copy()
            stage = int(item["stage"].iloc[0])
            if stage == 3:
                adjusted_marginal = np.zeros(len(item), dtype=float)
                adjusted_marginal[0] = 1.0
            else:
                base_hazard = marginal_to_hazard(item["marginal_pd"].to_numpy(float))
                adjusted_marginal = hazard_to_marginal(
                    scale_hazard(base_hazard, scenario.pd_multiplier)
                )
                if stage == 1:
                    adjusted_marginal = np.where(
                        item[config.period_column].to_numpy(int) <= config.stage1_horizon_periods,
                        adjusted_marginal,
                        0.0,
                    )
            period = item[config.period_column].to_numpy(float)
            eir = item["effective_interest_rate"].to_numpy(float)
            item["scenario"] = scenario.name
            item["scenario_weight"] = scenario.weight
            item["scenario_marginal_pd"] = adjusted_marginal
            item["scenario_lgd"] = np.clip(
                item["lgd"].to_numpy(float) * scenario.lgd_multiplier, 0.0, 1.0
            )
            item["scenario_ead"] = np.maximum(
                item["ead"].to_numpy(float) * scenario.ead_multiplier, 0.0
            )
            item["discount_factor"] = np.power(
                1.0 + eir / config.periods_per_year,
                -period,
            )
            item["ecl"] = (
                item["scenario_marginal_pd"]
                * item["scenario_lgd"]
                * item["scenario_ead"]
                * item["discount_factor"]
            )
            item["weighted_ecl"] = item["ecl"] * scenario.weight
            pieces.append(item)
        details.append(pd.concat(pieces, ignore_index=True))
    detail = pd.concat(details, ignore_index=True)
    by_scenario = (
        detail.groupby(["account_id", "scenario", "stage", "scenario_weight"], as_index=False)
        .agg(ecl=("ecl", "sum"), weighted_ecl=("weighted_ecl", "sum"))
        .sort_values(["account_id", "scenario"])
    )
    account = (
        by_scenario.groupby(["account_id", "stage"], as_index=False)
        .agg(ecl=("weighted_ecl", "sum"))
        .sort_values("account_id")
    )
    reconciliation = pd.DataFrame(
        {
            "measure": ["detail_weighted_ecl", "scenario_weighted_ecl", "account_ecl"],
            "amount": [
                detail["weighted_ecl"].sum(),
                by_scenario["weighted_ecl"].sum(),
                account["ecl"].sum(),
            ],
        }
    )
    if not np.allclose(reconciliation["amount"], reconciliation["amount"].iloc[0]):
        raise AssertionError("ECL reconciliation failed")
    return ECLResult(
        account=account, scenario=by_scenario, detail=detail, reconciliation=reconciliation
    )
