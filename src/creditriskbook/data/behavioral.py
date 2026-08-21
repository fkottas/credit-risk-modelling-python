"""Relational, point-in-time synthetic data for behavioural credit-risk teaching.

The generator is original project code.  It deliberately creates separate application,
contract, monthly-performance and bureau-enquiry tables so that students must define keys,
cardinalities and availability dates before engineering features.  It is not calibrated to a
real lender and must not be represented as observed customer data.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BehavioralDataset:
    """A reproducible relational teaching dataset plus its usage contract."""

    applications: pd.DataFrame
    contracts: pd.DataFrame
    monthly_performance: pd.DataFrame
    bureau_enquiries: pd.DataFrame
    licence: str
    attribution: str
    limitations: str
    source_sha256: str


def _digest_tables(*tables: pd.DataFrame) -> str:
    digest = hashlib.sha256()
    for table in tables:
        digest.update(table.to_csv(index=False).encode("utf-8"))
    return digest.hexdigest()


def make_behavioral_credit_history(
    n_customers: int = 800,
    months: int = 18,
    seed: int = 42,
    reference_date: str | pd.Timestamp = "2025-12-31",
) -> BehavioralDataset:
    """Generate coherent histories with useful delinquency and contract-opening signals.

    Default risk is driven by an unobserved customer propensity, recent delinquency,
    utilisation and new-credit intensity.  The relationship gives students rational expected
    directions without claiming to reproduce any institution's portfolio.
    """

    if n_customers < 100:
        raise ValueError("n_customers must be at least 100")
    if months < 12:
        raise ValueError("months must be at least 12")

    rng = np.random.default_rng(seed)
    reference = pd.Timestamp(reference_date)
    customer_ids = [f"CUS-{seed:04d}-{i:06d}" for i in range(n_customers)]
    latent_risk = rng.normal(0.0, 1.0, n_customers)
    income = np.clip(rng.lognormal(np.log(42_000), 0.55, n_customers), 8_000, 300_000)
    requested = np.clip(rng.lognormal(np.log(7_500), 0.65, n_customers), 300, 75_000)
    application_product = rng.choice(
        ["personal_loan", "credit_card", "bnpl"], n_customers, p=[0.48, 0.34, 0.18]
    )

    contract_rows: list[dict[str, object]] = []
    performance_rows: list[dict[str, object]] = []
    enquiry_rows: list[dict[str, object]] = []
    recent_max_dpd = np.zeros(n_customers, dtype=float)
    recent_utilisation = np.zeros(n_customers, dtype=float)
    recent_contract_count = np.zeros(n_customers, dtype=int)

    first_month = reference - pd.offsets.MonthEnd(months)
    month_ends = pd.date_range(first_month + pd.offsets.MonthEnd(1), reference, freq="ME")

    for customer_index, customer_id in enumerate(customer_ids):
        risk = float(latent_risk[customer_index])
        n_contracts = int(np.clip(1 + rng.poisson(1.4 + 0.25 * max(risk, 0)), 1, 7))
        customer_contract_rows: list[dict[str, object]] = []
        customer_performance_rows: list[dict[str, object]] = []
        for contract_index in range(n_contracts):
            contract_id = f"CON-{seed:04d}-{customer_index:06d}-{contract_index:02d}"
            product = str(
                rng.choice(["credit_card", "personal_loan", "bnpl"], p=[0.46, 0.39, 0.15])
            )
            # Recent openings are deliberately common enough to support a meaningful
            # CountContractsLast6Months exercise; older books remain the majority.
            open_months_ago = int(
                rng.integers(0, 7) if rng.random() < 0.30 else rng.integers(7, 49)
            )
            open_date = (reference - pd.DateOffset(months=open_months_ago)).normalize()
            open_date -= pd.offsets.Day(int(rng.integers(0, 25)))
            limit = float(
                np.clip(
                    rng.lognormal(np.log(8_500 if product == "credit_card" else 11_000), 0.65),
                    300,
                    120_000,
                )
            )
            close_probability = 0.12 if open_months_ago > 8 else 0.02
            closed = bool(rng.random() < close_probability)
            close_date = None
            if closed:
                earliest_close = open_date + pd.DateOffset(months=3)
                if earliest_close < reference:
                    possible = pd.date_range(earliest_close, reference, freq="ME")
                    close_date = pd.Timestamp(rng.choice(possible.to_numpy()))
                else:
                    closed = False

            base_util = float(np.clip(0.36 + 0.12 * risk + rng.normal(0, 0.12), 0.02, 0.92))
            dpd_state = 0
            latest_balance = 0.0
            latest_status = "current"
            for month_number, month_end in enumerate(month_ends):
                if month_end < open_date or (close_date is not None and month_end > close_date):
                    continue
                seasonal = 0.04 * np.sin(month_number / 2.5)
                utilisation = float(
                    np.clip(
                        base_util + seasonal + 0.018 * month_number + rng.normal(0, 0.08), 0, 1.12
                    )
                )
                if product != "credit_card":
                    age_months = max((month_end.to_period("M") - open_date.to_period("M")).n, 0)
                    term = 36 if product == "personal_loan" else 6
                    utilisation = float(np.clip(1 - age_months / term + rng.normal(0, 0.025), 0, 1))

                deterioration = 1 / (1 + np.exp(-(-3.1 + 0.85 * risk + 1.3 * utilisation)))
                if dpd_state >= 90:
                    dpd_state = int(
                        rng.choice([0, 30, 60, 90, 120], p=[0.05, 0.05, 0.10, 0.55, 0.25])
                    )
                elif dpd_state >= 30:
                    dpd_state = int(
                        rng.choice([0, 15, 30, 60, 90], p=[0.25, 0.10, 0.28, 0.24, 0.13])
                    )
                elif rng.random() < deterioration:
                    dpd_state = int(rng.choice([15, 30, 60], p=[0.55, 0.35, 0.10]))
                else:
                    dpd_state = 0

                balance = limit * utilisation
                scheduled = max(balance * (0.035 if product == "credit_card" else 0.06), 10.0)
                payment_ratio = float(
                    np.clip(
                        1.08 - 0.006 * dpd_state - 0.12 * max(risk, 0) + rng.normal(0, 0.15), 0, 1.5
                    )
                )
                received = scheduled * payment_ratio
                status = (
                    "default" if dpd_state >= 90 else ("delinquent" if dpd_state > 0 else "current")
                )
                ingestion = month_end + pd.offsets.Day(int(rng.integers(1, 6))) + pd.offsets.Hour(2)
                performance_record = {
                    "customer_id": customer_id,
                    "contract_id": contract_id,
                    "snapshot_date": month_end,
                    "ingestion_timestamp": ingestion,
                    "credit_limit": round(limit, 2),
                    "balance": round(balance, 2),
                    "scheduled_payment": round(scheduled, 2),
                    "payment_received": round(received, 2),
                    "dpd": dpd_state,
                    "status": status,
                }
                performance_rows.append(performance_record)
                customer_performance_rows.append(performance_record)
                latest_balance = balance
                latest_status = status

            contract_record = {
                "customer_id": customer_id,
                "contract_id": contract_id,
                "product": product,
                "open_date": open_date,
                "close_date": close_date,
                "initial_limit": round(limit, 2),
                "outstanding_balance": round(0.0 if closed else latest_balance, 2),
                "status": "closed" if closed else latest_status,
            }
            contract_rows.append(contract_record)
            customer_contract_rows.append(contract_record)

        n_enquiries = int(rng.poisson(1.6 + 0.4 * max(risk, 0)))
        for enquiry_index in range(n_enquiries):
            enquiry_rows.append(
                {
                    "customer_id": customer_id,
                    "enquiry_id": f"ENQ-{seed:04d}-{customer_index:06d}-{enquiry_index:02d}",
                    "enquiry_date": reference - pd.offsets.Day(int(rng.integers(0, 366))),
                    "enquiry_type": str(rng.choice(["credit_card", "loan", "mortgage"])),
                }
            )

        customer_performance = [
            row
            for row in customer_performance_rows
            if pd.Timestamp(row["snapshot_date"]) > reference - pd.DateOffset(months=6)
        ]
        recent_max_dpd[customer_index] = max(
            (float(row["dpd"]) for row in customer_performance), default=0.0
        )
        latest_date = max(
            (pd.Timestamp(row["snapshot_date"]) for row in customer_performance), default=reference
        )
        latest_rows = [
            row for row in customer_performance if pd.Timestamp(row["snapshot_date"]) == latest_date
        ]
        total_limit = sum(float(row["credit_limit"]) for row in latest_rows)
        recent_utilisation[customer_index] = (
            sum(float(row["balance"]) for row in latest_rows) / total_limit if total_limit else 0.0
        )
        recent_contract_count[customer_index] = sum(
            reference - pd.DateOffset(months=6) < pd.Timestamp(row["open_date"]) <= reference
            for row in customer_contract_rows
        )

    logit = (
        -3.55
        + 0.78 * latent_risk
        + 0.020 * recent_max_dpd
        + 1.10 * recent_utilisation
        + 0.28 * recent_contract_count
        - 0.18 * np.log(income / 30_000)
    )
    probability = np.clip(1 / (1 + np.exp(-logit)), 0.002, 0.85)
    default_12m = rng.binomial(1, probability)
    applications = pd.DataFrame(
        {
            "application_id": [f"APP-BEH-{seed:04d}-{i:06d}" for i in range(n_customers)],
            "customer_id": customer_ids,
            "reference_date": reference,
            "product": application_product,
            "income": np.round(income, 2),
            "requested_amount": np.round(requested, 2),
            "default_12m": default_12m,
        }
    )
    contracts = pd.DataFrame(contract_rows).sort_values(["customer_id", "open_date"])
    performance = pd.DataFrame(performance_rows).sort_values(
        ["customer_id", "contract_id", "snapshot_date", "ingestion_timestamp"]
    )
    enquiries = pd.DataFrame(enquiry_rows).sort_values(["customer_id", "enquiry_date"])
    digest = _digest_tables(applications, contracts, performance, enquiries)
    return BehavioralDataset(
        applications=applications.reset_index(drop=True),
        contracts=contracts.reset_index(drop=True),
        monthly_performance=performance.reset_index(drop=True),
        bureau_enquiries=enquiries.reset_index(drop=True),
        licence="Project-generated synthetic teaching data",
        attribution="CreditRiskBook Synthetic Behavioural History, generated locally.",
        limitations=(
            "Original synthetic relationships are pedagogical, simplified and not calibrated "
            "to any lender, country, product policy or protected group."
        ),
        source_sha256=digest,
    )


def inject_behavioral_defects(
    performance: pd.DataFrame,
    *,
    seed: int = 2026,
) -> pd.DataFrame:
    """Create a labelled defect copy while preserving the supplied source frame."""

    required = {
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
    }
    missing = required - set(performance)
    if missing:
        raise ValueError(f"Missing behavioural columns: {sorted(missing)}")
    if len(performance) < 20:
        raise ValueError("At least 20 rows are required to inject distinct defects")

    rng = np.random.default_rng(seed)
    dirty = performance.copy(deep=True).reset_index(drop=True)
    dirty["teaching_defect"] = "none"
    indices = rng.choice(dirty.index, size=7, replace=False)
    dirty.loc[indices[0], ["dpd", "teaching_defect"]] = [-15, "negative_dpd"]
    dirty.loc[indices[1], ["payment_received", "teaching_defect"]] = [
        -25.0,
        "negative_payment",
    ]
    dirty.loc[indices[2], ["balance", "teaching_defect"]] = [
        float(dirty.loc[indices[2], "credit_limit"]) * 1.75,
        "impossible_balance",
    ]
    dirty.loc[indices[3], ["status", "teaching_defect"]] = ["mystery", "invalid_status"]
    dirty.loc[indices[4], ["snapshot_date", "teaching_defect"]] = [
        pd.Timestamp("2099-12-31"),
        "future_snapshot",
    ]
    dirty.loc[indices[5], ["dpd", "status", "teaching_defect"]] = [
        120,
        "current",
        "status_dpd_conflict",
    ]

    exact_duplicate = dirty.loc[[indices[6]]].copy()
    exact_duplicate["teaching_defect"] = "exact_duplicate"
    corrected = dirty.loc[[indices[6]]].copy()
    corrected["ingestion_timestamp"] = pd.to_datetime(
        corrected["ingestion_timestamp"]
    ) + pd.offsets.Day(2)
    corrected["dpd"] = 30
    corrected["status"] = "delinquent"
    corrected["teaching_defect"] = "later_authoritative_correction"
    return pd.concat([dirty, exact_duplicate, corrected], ignore_index=True)
