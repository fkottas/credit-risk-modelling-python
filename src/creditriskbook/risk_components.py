"""Workout LGD and EAD/CCF construction with auditable intermediate fields."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_workout_lgd(cashflows: pd.DataFrame) -> pd.DataFrame:
    """Aggregate discounted recoveries and costs into account-level workout LGD.

    One input row is one recovery or cost cash flow.  Required fields are
    ``account_id``, ``default_date``, ``cashflow_date``, ``recovery``,
    ``direct_cost``, ``ead_at_default``, and ``effective_interest_rate``.
    Negative or greater-than-one raw LGDs remain visible and are accompanied by
    a bounded modelling value so that data issues are not silently erased.
    """

    required = {
        "account_id",
        "default_date",
        "cashflow_date",
        "recovery",
        "direct_cost",
        "ead_at_default",
        "effective_interest_rate",
    }
    missing = required - set(cashflows.columns)
    if missing:
        raise ValueError(f"Missing workout LGD fields: {sorted(missing)}")
    frame = cashflows.copy()
    frame["default_date"] = pd.to_datetime(frame["default_date"])
    frame["cashflow_date"] = pd.to_datetime(frame["cashflow_date"])
    frame["days_from_default"] = (frame["cashflow_date"] - frame["default_date"]).dt.days
    if (frame["days_from_default"] < 0).any():
        raise ValueError("Recovery cash flows cannot precede the default date")
    if (frame["ead_at_default"] <= 0).any() or (frame["effective_interest_rate"] <= -1).any():
        raise ValueError("EAD must be positive and effective interest rates must exceed -100%")
    frame["discount_factor"] = np.power(
        1.0 + frame["effective_interest_rate"].astype(float),
        -frame["days_from_default"].astype(float) / 365.25,
    )
    frame["discounted_net_recovery"] = (
        frame["recovery"].astype(float) - frame["direct_cost"].astype(float)
    ) * frame["discount_factor"]
    consistency = frame.groupby("account_id")[
        ["ead_at_default", "effective_interest_rate", "default_date"]
    ].nunique()
    if (consistency > 1).any().any():
        raise ValueError(
            "Account-level EAD, EIR, and default date must be constant across cash-flow rows"
        )
    result = frame.groupby("account_id", as_index=False).agg(
        default_date=("default_date", "first"),
        ead_at_default=("ead_at_default", "first"),
        effective_interest_rate=("effective_interest_rate", "first"),
        gross_recovery=("recovery", "sum"),
        direct_cost=("direct_cost", "sum"),
        discounted_net_recovery=("discounted_net_recovery", "sum"),
        last_cashflow_date=("cashflow_date", "max"),
        cashflow_count=("cashflow_date", "size"),
    )
    result["lgd_raw"] = 1.0 - result["discounted_net_recovery"] / result["ead_at_default"]
    result["lgd_model"] = result["lgd_raw"].clip(0.0, 1.0)
    result["boundary_adjustment"] = result["lgd_model"] - result["lgd_raw"]
    return result


def construct_ccf(observations: pd.DataFrame, *, bound_for_modelling: bool = True) -> pd.DataFrame:
    """Construct raw and modelling credit conversion factors for facilities."""

    required = {"facility_id", "drawn_reference", "limit_reference", "ead_at_default"}
    missing = required - set(observations.columns)
    if missing:
        raise ValueError(f"Missing CCF fields: {sorted(missing)}")
    result = observations.copy()
    result["undrawn_reference"] = result["limit_reference"] - result["drawn_reference"]
    if (result["undrawn_reference"] <= 0).any():
        raise ValueError("CCF requires strictly positive undrawn amount at the reference date")
    result["additional_draw"] = result["ead_at_default"] - result["drawn_reference"]
    result["ccf_raw"] = result["additional_draw"] / result["undrawn_reference"]
    result["ccf_model"] = (
        result["ccf_raw"].clip(0.0, 1.0) if bound_for_modelling else result["ccf_raw"]
    )
    result["boundary_adjustment"] = result["ccf_model"] - result["ccf_raw"]
    return result


def ead_from_ccf(drawn: np.ndarray, undrawn: np.ndarray, ccf: np.ndarray) -> np.ndarray:
    drawn_value = np.asarray(drawn, dtype=float)
    undrawn_value = np.asarray(undrawn, dtype=float)
    conversion = np.asarray(ccf, dtype=float)
    if np.any(drawn_value < 0) or np.any(undrawn_value < 0):
        raise ValueError("Drawn and undrawn exposures cannot be negative")
    return drawn_value + undrawn_value * conversion
