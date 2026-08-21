"""Management-overlay application and ECL reconciliation controls."""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_overlay(
    account_ecl: pd.DataFrame,
    overlays: pd.DataFrame,
) -> pd.DataFrame:
    """Apply approved additive or multiplicative overlays at account level."""

    required_ecl = {"account_id", "ecl"}
    required_overlay = {"account_id", "overlay_type", "overlay_value", "overlay_reason"}
    if required_ecl - set(account_ecl) or required_overlay - set(overlays):
        raise ValueError("ECL and overlay frames do not satisfy the required contracts")
    if overlays["account_id"].duplicated().any():
        raise ValueError("Only one consolidated overlay row is allowed per account")
    result = account_ecl.merge(overlays, how="left", on="account_id", validate="one_to_one")
    result["overlay_type"] = result["overlay_type"].fillna("none")
    result["overlay_value"] = result["overlay_value"].fillna(0.0).astype(float)
    if not result["overlay_type"].isin(["none", "additive", "multiplicative"]).all():
        raise ValueError("overlay_type must be none, additive, or multiplicative")
    result["pre_overlay_ecl"] = result["ecl"].astype(float)
    result["post_overlay_ecl"] = np.select(
        [result["overlay_type"].eq("additive"), result["overlay_type"].eq("multiplicative")],
        [
            result["pre_overlay_ecl"] + result["overlay_value"],
            result["pre_overlay_ecl"] * result["overlay_value"],
        ],
        default=result["pre_overlay_ecl"],
    )
    result["post_overlay_ecl"] = result["post_overlay_ecl"].clip(lower=0.0)
    result["overlay_amount"] = result["post_overlay_ecl"] - result["pre_overlay_ecl"]
    return result


def reconcile_ecl(
    account_ecl: pd.DataFrame,
    *,
    ledger_total: float,
    tolerance: float = 0.01,
) -> dict[str, float | bool]:
    """Reconcile calculated account ECL with the posting ledger."""

    column = "post_overlay_ecl" if "post_overlay_ecl" in account_ecl else "ecl"
    calculated = float(account_ecl[column].sum())
    difference = calculated - float(ledger_total)
    return {
        "calculated_total": calculated,
        "ledger_total": float(ledger_total),
        "difference": difference,
        "within_tolerance": abs(difference) <= tolerance,
    }
