import numpy as np
import pandas as pd


def create_synthetic_ifrs9_cohort_dataset(n=20_000, seed=42):
    np.random.seed(seed)

    origination_months = pd.date_range("2018-01-01", "2023-12-01", freq="MS")

    df = pd.DataFrame({
        "loan_id": np.arange(1, n + 1),
        "origination_month": np.random.choice(origination_months, n),
        "original_balance": np.random.lognormal(mean=9.0, sigma=0.7, size=n),
        "term_months": np.random.choice([12, 24, 36, 60], n, p=[0.2, 0.3, 0.3, 0.2]),
        "initial_pd": np.random.beta(2, 20, n),
        "unemployment_at_origination": np.random.normal(6, 1.5, n)
    })

    df["risk_grade"] = pd.qcut(
        df["initial_pd"],
        q=5,
        labels=["A", "B", "C", "D", "E"]
    )

    monthly_hazard = df["initial_pd"] / 12
    default_month = []

    for h, term in zip(monthly_hazard, df["term_months"]):
        default_flags = np.random.binomial(1, np.repeat(h, term))
        default_month.append(np.argmax(default_flags) + 1 if default_flags.sum() > 0 else np.nan)

    df["default_month"] = default_month
    df["default_flag"] = df["default_month"].notna().astype(int)

    df["stage"] = np.where(
        df["default_flag"] == 1,
        "Stage 3",
        np.where(df["initial_pd"] > df["initial_pd"].median() * 2, "Stage 2", "Stage 1")
    )

    return df


if __name__ == "__main__":
    df = create_synthetic_ifrs9_cohort_dataset()
    df.to_csv("data/synthetic/synthetic_ifrs9_cohort.csv", index=False)
