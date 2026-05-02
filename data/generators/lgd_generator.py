import numpy as np
import pandas as pd


def create_synthetic_lgd_dataset(n=10_000, seed=42):
    np.random.seed(seed)

    df = pd.DataFrame({
        "loan_id": np.arange(1, n + 1),
        "secured": np.random.binomial(1, 0.45, n),
        "ead": np.random.lognormal(mean=9.5, sigma=0.7, size=n),
        "collateral_value": np.random.lognormal(mean=9.3, sigma=0.8, size=n),
        "months_in_default": np.random.randint(1, 48, n),
        "collection_cost_rate": np.random.uniform(0.01, 0.15, n),
        "cure_flag": np.random.binomial(1, 0.25, n)
    })

    collateral_coverage = df["collateral_value"] / df["ead"]

    lgd = (
        0.65
        - 0.25 * df["secured"]
        - 0.20 * np.clip(collateral_coverage, 0, 2)
        + 0.01 * df["months_in_default"]
        + df["collection_cost_rate"]
        - 0.25 * df["cure_flag"]
        + np.random.normal(0, 0.10, n)
    )

    df["lgd"] = np.clip(lgd, 0, 1.2)

    return df


if __name__ == "__main__":
    df = create_synthetic_lgd_dataset()
    df.to_csv("data/synthetic/synthetic_lgd.csv", index=False)
