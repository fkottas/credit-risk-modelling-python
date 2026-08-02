"""Original synthetic case datasets for components that public data rarely expose."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import timedelta

import numpy as np
import pandas as pd

from creditriskbook.ifrs9.curves import constant_hazard_curve


@dataclass(frozen=True)
class CaseDataset:
    key: str
    frame: pd.DataFrame
    unit_of_observation: str
    purpose: str
    licence: str
    attribution: str
    limitations: str
    source_sha256: str


def _bundle(
    key: str,
    frame: pd.DataFrame,
    unit: str,
    purpose: str,
    limitations: str,
) -> CaseDataset:
    digest = hashlib.sha256(frame.to_csv(index=False).encode()).hexdigest()
    return CaseDataset(
        key=key,
        frame=frame,
        unit_of_observation=unit,
        purpose=purpose,
        licence="Project-generated synthetic teaching data",
        attribution=f"CreditRiskBook {key} generator, generated locally.",
        limitations=limitations,
        source_sha256=digest,
    )


def make_revolving_facilities(n_facilities: int = 2_000, seed: int = 42) -> CaseDataset:
    if n_facilities < 100:
        raise ValueError("n_facilities must be at least 100")
    rng = np.random.default_rng(seed)
    limit = np.clip(rng.lognormal(np.log(12_000), 0.75, n_facilities), 1_000, 250_000)
    utilisation = rng.beta(2.0, 2.4, n_facilities)
    drawn = limit * utilisation
    pd_12m = np.clip(
        1 / (1 + np.exp(-(-4.2 + 3.0 * utilisation + rng.normal(0, 0.35, n_facilities)))),
        0.001,
        0.70,
    )
    default = rng.binomial(1, pd_12m)
    draw_propensity = np.clip(
        0.15 + 0.65 * utilisation + rng.normal(0, 0.15, n_facilities), -0.3, 1.4
    )
    ead_default = np.where(
        default == 1,
        drawn + (limit - drawn) * draw_propensity,
        drawn,
    )
    frame = pd.DataFrame(
        {
            "facility_id": [f"REV-{seed:04d}-{i:06d}" for i in range(n_facilities)],
            "reference_date": pd.Timestamp("2024-12-31"),
            "drawn_reference": np.round(drawn, 2),
            "limit_reference": np.round(limit, 2),
            "utilisation": np.round(utilisation, 5),
            "pd_12m": np.round(pd_12m, 6),
            "default_12m": default,
            "ead_at_default": np.round(ead_default, 2),
        }
    )
    return _bundle(
        "synthetic_revolving",
        frame,
        "one row per facility at the reference date",
        "CCF construction, EAD modelling, utilisation and limit-policy exercises",
        "Synthetic drawdowns are simplified and do not reproduce a real revolving portfolio.",
    )


def make_recovery_ledger(n_defaults: int = 600, seed: int = 42) -> CaseDataset:
    if n_defaults < 100:
        raise ValueError("n_defaults must be at least 100")
    rng = np.random.default_rng(seed)
    rows = []
    for index in range(n_defaults):
        account_id = f"LGD-{seed:04d}-{index:06d}"
        default_date = pd.Timestamp("2019-01-01") + timedelta(days=int(rng.integers(0, 1_800)))
        ead = float(np.clip(rng.lognormal(np.log(18_000), 0.9), 500, 750_000))
        eir = float(np.clip(rng.normal(0.09, 0.035), 0.01, 0.30))
        secured = bool(rng.random() < 0.35)
        recovery_rate = float(rng.beta(4.5, 3.0) if secured else rng.beta(2.0, 4.8))
        total_recovery = ead * recovery_rate
        cashflow_count = int(rng.integers(1, 6))
        shares = rng.dirichlet(np.ones(cashflow_count))
        for cashflow, share in enumerate(shares, start=1):
            delay_days = int(60 + cashflow * rng.integers(90, 300))
            recovery = total_recovery * share
            rows.append(
                {
                    "account_id": account_id,
                    "default_date": default_date,
                    "cashflow_date": default_date + timedelta(days=delay_days),
                    "recovery": round(recovery, 2),
                    "direct_cost": round(recovery * rng.uniform(0.01, 0.08), 2),
                    "ead_at_default": round(ead, 2),
                    "effective_interest_rate": round(eir, 6),
                    "secured_flag": secured,
                    "workout_closed_flag": cashflow == cashflow_count,
                }
            )
    return _bundle(
        "synthetic_recovery",
        pd.DataFrame(rows),
        "one row per post-default recovery or cost cash flow",
        "workout LGD, discounting, cures, incomplete workouts and recovery timing",
        "Synthetic recoveries omit legal, collateral, guarantee and operational complexities.",
    )


def make_ifrs9_schedule(
    n_accounts: int = 500,
    periods: int = 36,
    seed: int = 42,
) -> CaseDataset:
    if n_accounts < 50 or periods < 12:
        raise ValueError("Use at least 50 accounts and 12 projection periods")
    rng = np.random.default_rng(seed)
    rows = []
    for index in range(n_accounts):
        account_id = f"ECL-{seed:04d}-{index:06d}"
        stage = int(rng.choice([1, 2, 3], p=[0.78, 0.17, 0.05]))
        pd_12m = float(np.clip(rng.lognormal(np.log(0.025), 0.9), 0.001, 0.65))
        if stage == 2:
            pd_12m = min(pd_12m * 2.2, 0.85)
        exposure = float(np.clip(rng.lognormal(np.log(20_000), 0.8), 500, 500_000))
        lgd = float(np.clip(rng.beta(3.2, 4.5), 0.05, 0.95))
        eir = float(np.clip(rng.normal(0.065, 0.02), 0.005, 0.25))
        curve = constant_hazard_curve(pd_12m, periods).reshape(-1)
        for period, marginal in enumerate(curve, start=1):
            rows.append(
                {
                    "account_id": account_id,
                    "period": period,
                    "stage": stage,
                    "marginal_pd": round(float(marginal), 10),
                    "lgd": round(lgd, 6),
                    "ead": round(max(exposure * (1 - (period - 1) / (periods + 6)), 0), 2),
                    "effective_interest_rate": round(eir, 6),
                    "segment": rng.choice(["prime", "subprime", "thin_file"]),
                }
            )
    return _bundle(
        "synthetic_ifrs9_schedule",
        pd.DataFrame(rows),
        "one row per account and contractual projection period",
        "staging, lifetime PD, scenario weighting, discounting, overlays and reconciliation",
        "The schedule is pedagogical and omits product-specific contractual cash-flow mechanics.",
    )


def make_corporate_irb_portfolio(n_obligors: int = 1_000, seed: int = 42) -> CaseDataset:
    if n_obligors < 100:
        raise ValueError("n_obligors must be at least 100")
    rng = np.random.default_rng(seed)
    pd_value = np.clip(rng.lognormal(np.log(0.012), 1.0, n_obligors), 0.0005, 0.45)
    lgd = np.clip(rng.beta(3.0, 4.0, n_obligors), 0.10, 0.90)
    ead = np.clip(rng.lognormal(np.log(2_000_000), 1.2, n_obligors), 50_000, 250_000_000)
    sales = np.clip(rng.lognormal(np.log(40), 1.0, n_obligors), 2, 2_000)
    grade_edges = np.quantile(pd_value, np.linspace(0, 1, 9))
    grade = pd.cut(
        pd_value, grade_edges, labels=[f"G{i}" for i in range(1, 9)], include_lowest=True
    )
    frame = pd.DataFrame(
        {
            "obligor_id": [f"CORP-{seed:04d}-{i:06d}" for i in range(n_obligors)],
            "grade": grade.astype(str),
            "pd": np.round(pd_value, 7),
            "lgd": np.round(lgd, 6),
            "ead": np.round(ead, 2),
            "maturity_years": np.round(rng.uniform(1, 5, n_obligors), 4),
            "annual_sales_eur_millions": np.round(sales, 3),
            "sme_flag": sales <= 50,
        }
    )
    return _bundle(
        "synthetic_corporate_irb",
        frame,
        "one row per obligor/facility snapshot",
        "IRB risk weights, grade calibration, concentration, maturity and SME correlation",
        "Synthetic parameters are not approved regulatory estimates and omit facility hierarchy.",
    )


def make_counterparty_profiles(n_netting_sets: int = 120, seed: int = 42) -> CaseDataset:
    if n_netting_sets < 20:
        raise ValueError("n_netting_sets must be at least 20")
    rng = np.random.default_rng(seed)
    horizons = np.array([0.0, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0])
    rows = []
    for index in range(n_netting_sets):
        peak = float(rng.lognormal(np.log(2_000_000), 1.0))
        maturity = float(rng.uniform(1, 5))
        collateral = float(peak * rng.uniform(0, 0.65))
        for horizon in horizons[horizons <= maturity]:
            profile = peak * (horizon / max(maturity, 0.25)) * np.exp(-1.5 * horizon / maturity)
            rows.append(
                {
                    "netting_set_id": f"CCR-{seed:04d}-{index:05d}",
                    "horizon_years": horizon,
                    "expected_exposure": round(max(profile * 0.65 - collateral, 0), 2),
                    "pfe_975": round(max(profile - collateral, 0), 2),
                    "collateral": round(collateral, 2),
                    "counterparty_pd": round(float(rng.uniform(0.001, 0.08)), 6),
                    "counterparty_lgd": round(float(rng.uniform(0.35, 0.65)), 6),
                }
            )
    return _bundle(
        "synthetic_counterparty_profiles",
        pd.DataFrame(rows),
        "one row per netting set and future horizon",
        "exposure profiles, collateral, PFE and introductory CVA exercises",
        "Profiles are stylised and are not market-calibrated derivative simulations.",
    )


def available_case_datasets() -> tuple[str, ...]:
    return (
        "synthetic_revolving",
        "synthetic_recovery",
        "synthetic_ifrs9_schedule",
        "synthetic_corporate_irb",
        "synthetic_counterparty_profiles",
    )


def load_case_dataset(key: str, *, n_rows: int | None = None, seed: int = 42) -> CaseDataset:
    if key == "synthetic_revolving":
        return make_revolving_facilities(n_rows or 2_000, seed)
    if key == "synthetic_recovery":
        return make_recovery_ledger(n_rows or 600, seed)
    if key == "synthetic_ifrs9_schedule":
        return make_ifrs9_schedule(n_rows or 500, seed=seed)
    if key == "synthetic_corporate_irb":
        return make_corporate_irb_portfolio(n_rows or 1_000, seed)
    if key == "synthetic_counterparty_profiles":
        return make_counterparty_profiles(n_rows or 120, seed)
    raise KeyError(f"Unknown case dataset {key!r}; choose from {available_case_datasets()}")
