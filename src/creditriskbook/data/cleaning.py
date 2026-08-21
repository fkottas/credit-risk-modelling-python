"""Auditable cleaning and quarantine for longitudinal credit histories.

The functions preserve input values, apply only explicitly authorised record-selection rules,
and return row-level evidence.  They never impute, cap, winsorise or overwrite an implausible
value merely to make a model run.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

PERFORMANCE_COLUMNS = (
    "customer_id",
    "contract_id",
    "snapshot_date",
    "ingestion_timestamp",
    "credit_limit",
    "balance",
    "scheduled_payment",
    "payment_received",
    "dpd",
    "status",
)
PERMITTED_STATUS = frozenset({"current", "delinquent", "default"})


@dataclass(frozen=True)
class CleaningResult:
    """Clean rows, quarantined rows and one issue record per failed rule."""

    clean: pd.DataFrame
    quarantine: pd.DataFrame
    issues: pd.DataFrame

    @property
    def passed(self) -> bool:
        return self.quarantine.empty


def _issue(
    row_id: int,
    row: pd.Series,
    rule: str,
    field: str,
    observed: object,
    action: str = "quarantine",
) -> dict[str, object]:
    return {
        "source_row_id": row_id,
        "customer_id": row.get("customer_id"),
        "contract_id": row.get("contract_id"),
        "snapshot_date": row.get("snapshot_date"),
        "rule": rule,
        "field": field,
        "observed_value": observed,
        "action": action,
    }


def clean_monthly_performance(
    performance: pd.DataFrame,
    reference_dates: pd.DataFrame,
) -> CleaningResult:
    """Validate monthly histories and select the latest ingested record per business key.

    ``reference_dates`` must contain ``customer_id`` and ``reference_date``.  Where two source
    rows share customer, contract and snapshot date, the record with the latest non-null
    ingestion timestamp is retained.  Earlier rows are evidenced as ``superseded``; this is a
    source-system version rule, not a statistical repair.
    """

    missing = set(PERFORMANCE_COLUMNS) - set(performance)
    if missing:
        raise ValueError(f"Missing performance columns: {sorted(missing)}")
    reference_missing = {"customer_id", "reference_date"} - set(reference_dates)
    if reference_missing:
        raise ValueError(f"Missing reference-date columns: {sorted(reference_missing)}")
    if reference_dates["customer_id"].duplicated().any():
        raise ValueError("reference_dates must contain one row per customer_id")

    data = (
        performance.copy(deep=True)
        .reset_index(drop=False)
        .rename(columns={"index": "source_row_id"})
    )
    data["snapshot_date"] = pd.to_datetime(data["snapshot_date"], errors="coerce")
    data["ingestion_timestamp"] = pd.to_datetime(data["ingestion_timestamp"], errors="coerce")
    references = reference_dates[["customer_id", "reference_date"]].copy()
    references["reference_date"] = pd.to_datetime(references["reference_date"], errors="coerce")
    data = data.merge(references, on="customer_id", how="left", validate="many_to_one")

    issues: list[dict[str, object]] = []
    quarantined_ids: set[int] = set()

    key = ["customer_id", "contract_id", "snapshot_date"]
    ordered = data.sort_values(key + ["ingestion_timestamp", "source_row_id"], na_position="first")
    superseded = ordered.duplicated(key, keep="last")
    for _, row in ordered.loc[superseded].iterrows():
        row_id = int(row["source_row_id"])
        quarantined_ids.add(row_id)
        issues.append(
            _issue(
                row_id,
                row,
                "superseded_business_key",
                "ingestion_timestamp",
                row["ingestion_timestamp"],
                "retain_latest_ingestion_and_quarantine_prior_version",
            )
        )

    candidates = ordered.loc[~superseded].copy()
    for _, row in candidates.iterrows():
        row_id = int(row["source_row_id"])
        row_issues: list[dict[str, object]] = []
        if pd.isna(row["snapshot_date"]):
            row_issues.append(
                _issue(row_id, row, "unparseable_snapshot_date", "snapshot_date", None)
            )
        if pd.isna(row["ingestion_timestamp"]):
            row_issues.append(
                _issue(row_id, row, "unparseable_ingestion_timestamp", "ingestion_timestamp", None)
            )
        if pd.isna(row["reference_date"]):
            row_issues.append(
                _issue(row_id, row, "missing_customer_reference_date", "reference_date", None)
            )
        elif pd.notna(row["snapshot_date"]) and row["snapshot_date"] > row["reference_date"]:
            row_issues.append(
                _issue(
                    row_id,
                    row,
                    "post_reference_snapshot",
                    "snapshot_date",
                    row["snapshot_date"],
                )
            )
        if pd.isna(row["credit_limit"]) or float(row["credit_limit"]) <= 0:
            row_issues.append(
                _issue(
                    row_id, row, "non_positive_credit_limit", "credit_limit", row["credit_limit"]
                )
            )
        if pd.isna(row["balance"]) or float(row["balance"]) < 0:
            row_issues.append(_issue(row_id, row, "negative_balance", "balance", row["balance"]))
        elif pd.notna(row["credit_limit"]) and float(row["credit_limit"]) > 0:
            if float(row["balance"]) > 1.20 * float(row["credit_limit"]):
                row_issues.append(
                    _issue(
                        row_id,
                        row,
                        "balance_exceeds_120pct_limit",
                        "balance",
                        row["balance"],
                    )
                )
        for field in ("scheduled_payment", "payment_received"):
            if pd.isna(row[field]) or float(row[field]) < 0:
                row_issues.append(
                    _issue(row_id, row, f"negative_or_missing_{field}", field, row[field])
                )
        if pd.isna(row["dpd"]) or not 0 <= float(row["dpd"]) <= 999:
            row_issues.append(_issue(row_id, row, "dpd_out_of_domain", "dpd", row["dpd"]))
        if row["status"] not in PERMITTED_STATUS:
            row_issues.append(_issue(row_id, row, "status_out_of_domain", "status", row["status"]))
        elif pd.notna(row["dpd"]) and 0 <= float(row["dpd"]) <= 999:
            expected = (
                "default"
                if float(row["dpd"]) >= 90
                else ("delinquent" if float(row["dpd"]) > 0 else "current")
            )
            if row["status"] != expected:
                row_issues.append(
                    _issue(row_id, row, "status_dpd_inconsistent", "status", row["status"])
                )
        if row_issues:
            quarantined_ids.add(row_id)
            issues.extend(row_issues)

    clean = data.loc[~data["source_row_id"].isin(quarantined_ids)].copy()
    quarantine = data.loc[data["source_row_id"].isin(quarantined_ids)].copy()
    issue_frame = pd.DataFrame(
        issues,
        columns=[
            "source_row_id",
            "customer_id",
            "contract_id",
            "snapshot_date",
            "rule",
            "field",
            "observed_value",
            "action",
        ],
    )
    drop_internal = ["reference_date"]
    return CleaningResult(
        clean=clean.drop(columns=drop_internal).sort_values(key).reset_index(drop=True),
        quarantine=quarantine.drop(columns=drop_internal).sort_values(key).reset_index(drop=True),
        issues=issue_frame.sort_values(["source_row_id", "rule"]).reset_index(drop=True),
    )


def validate_contract_history(
    contracts: pd.DataFrame, reference_dates: pd.DataFrame
) -> pd.DataFrame:
    """Return contract-level issues without modifying the contract ledger."""

    required = {
        "customer_id",
        "contract_id",
        "open_date",
        "close_date",
        "initial_limit",
        "outstanding_balance",
        "status",
    }
    missing = required - set(contracts)
    if missing:
        raise ValueError(f"Missing contract columns: {sorted(missing)}")
    references = reference_dates[["customer_id", "reference_date"]].copy()
    references["reference_date"] = pd.to_datetime(references["reference_date"], errors="coerce")
    data = (
        contracts.copy(deep=True).reset_index(drop=False).rename(columns={"index": "source_row_id"})
    )
    data["open_date"] = pd.to_datetime(data["open_date"], errors="coerce")
    data["close_date"] = pd.to_datetime(data["close_date"], errors="coerce")
    data = data.merge(references, on="customer_id", how="left", validate="many_to_one")
    issues: list[dict[str, object]] = []
    for _, row in data.iterrows():
        row_id = int(row["source_row_id"])
        if pd.isna(row["open_date"]):
            issues.append(_issue(row_id, row, "missing_open_date", "open_date", None))
        elif pd.notna(row["reference_date"]) and row["open_date"] > row["reference_date"]:
            issues.append(
                _issue(row_id, row, "post_reference_open_date", "open_date", row["open_date"])
            )
        if (
            pd.notna(row["close_date"])
            and pd.notna(row["open_date"])
            and row["close_date"] < row["open_date"]
        ):
            issues.append(_issue(row_id, row, "close_before_open", "close_date", row["close_date"]))
        if pd.isna(row["initial_limit"]) or float(row["initial_limit"]) <= 0:
            issues.append(
                _issue(
                    row_id, row, "non_positive_initial_limit", "initial_limit", row["initial_limit"]
                )
            )
        if pd.isna(row["outstanding_balance"]) or float(row["outstanding_balance"]) < 0:
            issues.append(
                _issue(
                    row_id,
                    row,
                    "negative_outstanding_balance",
                    "outstanding_balance",
                    row["outstanding_balance"],
                )
            )
    return pd.DataFrame(issues)
