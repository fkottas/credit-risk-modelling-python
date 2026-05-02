import numpy as np
import pandas as pd


def create_synthetic_ead_dataset(n=10_000, seed=42):
    np.random.seed(seed)

    df = pd.DataFrame({
        "loan_id": np.arange(1, n + 1),
        "credit_limit": np.random.lognormal(mean=9.7, sigma=0.8, size=n),
        "current_balance": np.random.lognormal(mean=8.8, sigma=0.9, size=n),
        "months_to_default": np.random.randint(1, 24, n),
        "utilization_rate": np.random.beta(2, 4, n),
        "delinquency_flag": np.random.binomial(1, 0.25, n)
    })

    df["current_balance"] = np.minimum(df["current_balance"], df["credit_limit"])
    df["undrawn_amount"] = df["credit_limit"] - df["current_balance"]

    ccf = (
        0.20
        + 0.35 * df["delinquency_flag"]
        + 0.30 * df["utilization_rate"]
        - 0.01 * df["months_to_default"]
        + np.random.normal(0, 0.15, n)
    )

    df["ccf"] = np.clip(ccf, -0.2, 1.5)
    df["ead"] = df["current_balance"] + df["ccf"] * df["undrawn_amount"]

    return df


if __name__ == "__main__":
    df = create_synthetic_ead_dataset()
    df.to_csv("data/synthetic/synthetic_ead.csv", index=False)
