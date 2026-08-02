"""Independent synthetic portfolios used for tests and unrestricted exercises."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _sigmoid(value: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-value))


def make_synthetic_retail_portfolio(n_rows: int = 5_000, seed: int = 42) -> pd.DataFrame:
    """Create a reproducible application and outcome dataset.

    The generator is original project code. Its relationships are intentionally
    simplified and are not estimates from, or replicas of, a real lender.
    """

    if n_rows < 200:
        raise ValueError("n_rows must be at least 200 so time splits remain meaningful")

    rng = np.random.default_rng(seed)
    start = np.datetime64("2018-01-01")
    end = np.datetime64("2025-12-31")
    day_offsets = rng.integers(0, int((end - start) / np.timedelta64(1, "D")) + 1, n_rows)
    application_date = pd.to_datetime(start + day_offsets.astype("timedelta64[D]"))

    age = np.clip(np.rint(rng.normal(42, 12, n_rows)), 18, 79).astype(int)
    sex = rng.choice(["female", "male", "not_recorded"], n_rows, p=[0.49, 0.49, 0.02])
    region = rng.choice(["north", "south", "east", "west"], n_rows)
    product = rng.choice(["personal_loan", "credit_card", "bnpl"], n_rows, p=[0.48, 0.32, 0.20])
    home_ownership = rng.choice(["rent", "mortgage", "own", "other"], n_rows, p=[0.38, 0.36, 0.22, 0.04])
    purpose = rng.choice(["debt_consolidation", "vehicle", "home", "education", "other"], n_rows)

    income = np.clip(rng.lognormal(mean=np.log(38_000), sigma=0.55, size=n_rows), 8_000, 300_000)
    employment_years = np.minimum(rng.gamma(2.1, 3.4, n_rows), np.maximum(age - 18, 0))
    debt_to_income = np.clip(rng.beta(2.2, 4.8, n_rows) * 1.35, 0.01, 1.35)
    utilisation = np.clip(rng.beta(2.0, 2.6, n_rows), 0.0, 1.0)
    credit_history_years = np.minimum(rng.gamma(2.4, 3.2, n_rows), np.maximum(age - 18, 0))
    enquiries_6m = np.clip(rng.poisson(1.4, n_rows), 0, 12)
    loan_amount = np.clip(rng.lognormal(np.log(8_000), 0.65, n_rows), 500, 80_000)
    term_months = rng.choice([6, 12, 24, 36, 48, 60], n_rows, p=[0.05, 0.16, 0.18, 0.31, 0.10, 0.20])

    year_fraction = (application_date.year.to_numpy() - 2018) + application_date.month.to_numpy() / 12
    macro_unemployment = 5.1 + 0.55 * np.sin(year_fraction * 1.3)
    macro_unemployment += np.where((application_date >= "2020-03-01") & (application_date <= "2021-06-30"), 2.1, 0)

    risk_logit = (
        -4.25
        + 1.70 * debt_to_income
        + 1.55 * utilisation
        + 0.16 * enquiries_6m
        - 0.035 * employment_years
        - 0.22 * np.log(income / 30_000)
        + 0.16 * (macro_unemployment - 5.0)
        + 0.38 * (product == "bnpl")
        + 0.22 * (home_ownership == "rent")
        + 0.15 * (purpose == "debt_consolidation")
        + rng.normal(0, 0.22, n_rows)
    )
    true_pd = np.clip(_sigmoid(risk_logit), 0.002, 0.80)
    default_12m = rng.binomial(1, true_pd)

    interest_rate = np.clip(0.045 + 0.24 * true_pd + rng.normal(0, 0.012, n_rows), 0.025, 0.32)
    ead = loan_amount * np.clip(rng.normal(0.97, 0.07, n_rows), 0.72, 1.18)
    lgd_mean = np.clip(0.28 + 0.18 * (home_ownership == "rent") + 0.10 * (product == "bnpl"), 0.08, 0.85)
    concentration = 11.0
    lgd = rng.beta(lgd_mean * concentration, (1.0 - lgd_mean) * concentration)
    days_past_due = np.where(
        default_12m == 1,
        rng.choice([90, 120, 180, 360], n_rows, p=[0.35, 0.30, 0.25, 0.10]),
        rng.choice([0, 0, 0, 0, 15, 30], n_rows),
    )

    return pd.DataFrame(
        {
            "application_id": [f"APP-{seed:04d}-{i:07d}" for i in range(n_rows)],
            "application_date": application_date,
            "age": age,
            "sex": sex,
            "region": region,
            "product": product,
            "home_ownership": home_ownership,
            "purpose": purpose,
            "income": np.round(income, 2),
            "employment_years": np.round(employment_years, 2),
            "debt_to_income": np.round(debt_to_income, 4),
            "utilisation": np.round(utilisation, 4),
            "credit_history_years": np.round(credit_history_years, 2),
            "enquiries_6m": enquiries_6m,
            "loan_amount": np.round(loan_amount, 2),
            "term_months": term_months,
            "macro_unemployment": np.round(macro_unemployment, 3),
            "interest_rate": np.round(interest_rate, 5),
            "default_12m": default_12m,
            "lgd": np.round(lgd, 5),
            "ead": np.round(ead, 2),
            "days_past_due_after_12m": days_past_due,
        }
    )
