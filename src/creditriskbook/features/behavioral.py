"""Point-in-time behavioural and bureau features from first principles."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BehavioralFeatureConfig:
    """Explicit windows and boundary convention for feature construction."""

    windows_months: tuple[int, ...] = (3, 6, 12)
    include_start: bool = False

    def __post_init__(self) -> None:
        if not self.windows_months or any(window <= 0 for window in self.windows_months):
            raise ValueError("windows_months must contain positive integers")
        if len(set(self.windows_months)) != len(self.windows_months):
            raise ValueError("windows_months cannot contain duplicates")


business_name_map = {
    "MaxDPDLast6Months": "max_dpd_6m",
    "LastDPD": "last_dpd",
    "CountContractsLast6Months": "count_contracts_last_6m",
    "CountDPD30Last6Months": "count_dpd30_6m",
    "UtilisationTrendLast6Months": "utilisation_slope_6m",
}


def _in_window(
    series: pd.Series, reference: pd.Timestamp, months: int, include_start: bool
) -> pd.Series:
    lower = reference - pd.DateOffset(months=months)
    return ((series >= lower) if include_start else (series > lower)) & (series <= reference)


def _ols_slope(values: pd.Series) -> float:
    """Slope per monthly observation using the closed-form OLS expression."""

    clean = values.dropna().astype(float)
    if len(clean) < 2:
        return 0.0
    x = np.arange(len(clean), dtype=float)
    x_centered = x - x.mean()
    denominator = float(np.dot(x_centered, x_centered))
    return float(np.dot(x_centered, clean.to_numpy() - clean.mean()) / denominator)


def _months_between(later: pd.Timestamp, earlier: pd.Timestamp) -> int:
    return (later.year - earlier.year) * 12 + later.month - earlier.month


def _consecutive_positive(values: pd.Series) -> int:
    count = 0
    for value in reversed(values.fillna(0).tolist()):
        if float(value) <= 0:
            break
        count += 1
    return count


def build_behavioral_features(
    performance: pd.DataFrame,
    contracts: pd.DataFrame,
    reference_dates: pd.DataFrame,
    *,
    enquiries: pd.DataFrame | None = None,
    config: BehavioralFeatureConfig | None = None,
) -> pd.DataFrame:
    """Create one leakage-safe feature row per customer and reference date.

    Window convention is ``reference - window < event_date <= reference`` unless
    ``include_start`` is enabled.  No future row is used.  Missing histories remain visible
    through counts and ``history_available``; the function does not impute business values.
    """

    config = config or BehavioralFeatureConfig()
    performance_required = {
        "customer_id",
        "contract_id",
        "snapshot_date",
        "credit_limit",
        "balance",
        "scheduled_payment",
        "payment_received",
        "dpd",
    }
    contract_required = {
        "customer_id",
        "contract_id",
        "open_date",
        "close_date",
        "outstanding_balance",
    }
    reference_required = {"customer_id", "reference_date"}
    for name, frame, required in (
        ("performance", performance, performance_required),
        ("contracts", contracts, contract_required),
        ("reference_dates", reference_dates, reference_required),
    ):
        missing = required - set(frame)
        if missing:
            raise ValueError(f"{name} missing columns: {sorted(missing)}")
    if reference_dates["customer_id"].duplicated().any():
        raise ValueError("reference_dates must contain one row per customer")

    perf = performance.copy(deep=True)
    con = contracts.copy(deep=True)
    refs = reference_dates[["customer_id", "reference_date"]].copy(deep=True)
    perf["snapshot_date"] = pd.to_datetime(perf["snapshot_date"], errors="raise")
    con["open_date"] = pd.to_datetime(con["open_date"], errors="raise")
    con["close_date"] = pd.to_datetime(con["close_date"], errors="coerce")
    refs["reference_date"] = pd.to_datetime(refs["reference_date"], errors="raise")
    enquiry_frame = None
    if enquiries is not None:
        required = {"customer_id", "enquiry_date"}
        missing = required - set(enquiries)
        if missing:
            raise ValueError(f"enquiries missing columns: {sorted(missing)}")
        enquiry_frame = enquiries.copy(deep=True)
        enquiry_frame["enquiry_date"] = pd.to_datetime(
            enquiry_frame["enquiry_date"], errors="raise"
        )

    performance_groups = {
        customer_id: group.copy() for customer_id, group in perf.groupby("customer_id", sort=False)
    }
    contract_groups = {
        customer_id: group.copy() for customer_id, group in con.groupby("customer_id", sort=False)
    }
    enquiry_groups = (
        {
            customer_id: group.copy()
            for customer_id, group in enquiry_frame.groupby("customer_id", sort=False)
        }
        if enquiry_frame is not None
        else {}
    )
    empty_performance = perf.iloc[0:0].copy()
    empty_contracts = con.iloc[0:0].copy()
    empty_enquiries = enquiry_frame.iloc[0:0].copy() if enquiry_frame is not None else None

    rows: list[dict[str, object]] = []
    for reference_row in refs.itertuples(index=False):
        customer_id = reference_row.customer_id
        reference = pd.Timestamp(reference_row.reference_date)
        performance_group = performance_groups.get(customer_id, empty_performance)
        contract_group = contract_groups.get(customer_id, empty_contracts)
        customer_perf = performance_group.loc[
            performance_group["snapshot_date"] <= reference
        ].copy()
        customer_contracts = contract_group.loc[contract_group["open_date"] <= reference].copy()
        customer_perf = customer_perf.sort_values(["snapshot_date", "contract_id"])
        record: dict[str, object] = {
            "customer_id": customer_id,
            "reference_date": reference,
            "history_available": int(not customer_perf.empty),
            "history_months": int(customer_perf["snapshot_date"].dt.to_period("M").nunique()),
        }

        if customer_perf.empty:
            record.update(
                {
                    "last_dpd": np.nan,
                    "months_since_last_dpd30": np.nan,
                    "consecutive_delinquent_months": 0,
                    "current_utilisation": np.nan,
                    "active_contracts": int(
                        (
                            customer_contracts["close_date"].isna()
                            | (customer_contracts["close_date"] > reference)
                        ).sum()
                    ),
                    "total_outstanding_balance": float(
                        customer_contracts.loc[
                            customer_contracts["close_date"].isna()
                            | (customer_contracts["close_date"] > reference),
                            "outstanding_balance",
                        ].sum()
                    ),
                }
            )
        else:
            monthly = (
                customer_perf.groupby("snapshot_date", as_index=False)
                .agg(
                    dpd=("dpd", "max"),
                    balance=("balance", "sum"),
                    credit_limit=("credit_limit", "sum"),
                    scheduled_payment=("scheduled_payment", "sum"),
                    payment_received=("payment_received", "sum"),
                )
                .sort_values("snapshot_date")
            )
            monthly["utilisation"] = monthly["balance"] / monthly["credit_limit"]
            monthly["payment_ratio"] = np.where(
                monthly["scheduled_payment"] > 0,
                monthly["payment_received"] / monthly["scheduled_payment"],
                np.nan,
            )
            last_month = monthly.iloc[-1]
            delinquent_dates = monthly.loc[monthly["dpd"] >= 30, "snapshot_date"]
            record.update(
                {
                    "last_dpd": float(last_month["dpd"]),
                    "months_since_last_dpd30": (
                        _months_between(reference, pd.Timestamp(delinquent_dates.max()))
                        if not delinquent_dates.empty
                        else np.nan
                    ),
                    "consecutive_delinquent_months": _consecutive_positive(monthly["dpd"]),
                    "current_utilisation": float(last_month["utilisation"]),
                    "active_contracts": int(
                        (
                            customer_contracts["close_date"].isna()
                            | (customer_contracts["close_date"] > reference)
                        ).sum()
                    ),
                    "total_outstanding_balance": float(
                        customer_contracts.loc[
                            customer_contracts["close_date"].isna()
                            | (customer_contracts["close_date"] > reference),
                            "outstanding_balance",
                        ].sum()
                    ),
                }
            )

        for window in config.windows_months:
            perf_window = customer_perf.loc[
                _in_window(customer_perf["snapshot_date"], reference, window, config.include_start)
            ].copy()
            contracts_window = customer_contracts.loc[
                _in_window(customer_contracts["open_date"], reference, window, config.include_start)
            ]
            record[f"count_contracts_last_{window}m"] = int(len(contracts_window))
            if perf_window.empty:
                record.update(
                    {
                        f"max_dpd_{window}m": np.nan,
                        f"mean_dpd_{window}m": np.nan,
                        f"count_dpd30_{window}m": 0,
                        f"count_dpd60_{window}m": 0,
                        f"count_dpd90_{window}m": 0,
                        f"utilisation_mean_{window}m": np.nan,
                        f"utilisation_max_{window}m": np.nan,
                        f"utilisation_slope_{window}m": np.nan,
                        f"payment_ratio_mean_{window}m": np.nan,
                        f"payment_ratio_min_{window}m": np.nan,
                        f"overlimit_months_{window}m": 0,
                    }
                )
            else:
                monthly_window = (
                    perf_window.groupby("snapshot_date", as_index=False)
                    .agg(
                        dpd=("dpd", "max"),
                        balance=("balance", "sum"),
                        credit_limit=("credit_limit", "sum"),
                        scheduled_payment=("scheduled_payment", "sum"),
                        payment_received=("payment_received", "sum"),
                    )
                    .sort_values("snapshot_date")
                )
                monthly_window["utilisation"] = (
                    monthly_window["balance"] / monthly_window["credit_limit"]
                )
                monthly_window["payment_ratio"] = np.where(
                    monthly_window["scheduled_payment"] > 0,
                    monthly_window["payment_received"] / monthly_window["scheduled_payment"],
                    np.nan,
                )
                record.update(
                    {
                        f"max_dpd_{window}m": float(monthly_window["dpd"].max()),
                        f"mean_dpd_{window}m": float(monthly_window["dpd"].mean()),
                        f"count_dpd30_{window}m": int((monthly_window["dpd"] >= 30).sum()),
                        f"count_dpd60_{window}m": int((monthly_window["dpd"] >= 60).sum()),
                        f"count_dpd90_{window}m": int((monthly_window["dpd"] >= 90).sum()),
                        f"utilisation_mean_{window}m": float(monthly_window["utilisation"].mean()),
                        f"utilisation_max_{window}m": float(monthly_window["utilisation"].max()),
                        f"utilisation_slope_{window}m": _ols_slope(monthly_window["utilisation"]),
                        f"payment_ratio_mean_{window}m": float(
                            monthly_window["payment_ratio"].mean()
                        ),
                        f"payment_ratio_min_{window}m": float(
                            monthly_window["payment_ratio"].min()
                        ),
                        f"overlimit_months_{window}m": int(
                            (monthly_window["balance"] > monthly_window["credit_limit"]).sum()
                        ),
                    }
                )
            if enquiry_frame is not None:
                customer_enquiries = enquiry_groups.get(customer_id, empty_enquiries)
                assert customer_enquiries is not None
                record[f"count_enquiries_last_{window}m"] = int(
                    _in_window(
                        customer_enquiries["enquiry_date"],
                        reference,
                        window,
                        config.include_start,
                    ).sum()
                )
        rows.append(record)

    return pd.DataFrame(rows).sort_values(["customer_id", "reference_date"]).reset_index(drop=True)
