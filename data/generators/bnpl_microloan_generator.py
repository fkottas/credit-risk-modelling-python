import numpy as np
import pandas as pd


def create_synthetic_bnpl_microloan_dataset(n=20_000, seed=42):
    np.random.seed(seed)

    df = pd.DataFrame({
        "customer_id": np.arange(1, n + 1),
        "product_type": np.random.choice(["BNPL", "microloan"], size=n, p=[0.65, 0.35]),
        "loan_amount": np.random.lognormal(mean=5.5, sigma=0.7, size=n),
        "tenor_months": np.random.choice([1, 3, 6, 12], size=n, p=[0.35, 0.35, 0.20, 0.10]),
        "previous_loans": np.random.poisson(2, n),
        "missed_payments_last_6m": np.random.poisson(0.4, n),
        "monthly_income_proxy": np.random.lognormal(mean=7.2, sigma=0.5, size=n),
        "digital_engagement_score": np.random.beta(4, 2, n),
        "merchant_risk_score": np.random.beta(2, 5, n)
    })

    df["payment_to_income"] = df["loan_amount"] / df["monthly_income_proxy"]

    logit = (
        -2.8
        + 1.8 * df["payment_to_income"]
        + 0.45 * df["missed_payments_last_6m"]
        - 0.20 * df["previous_loans"]
        - 0.70 * df["digital_engagement_score"]
        + 1.10 * df["merchant_risk_score"]
        + np.where(df["product_type"] == "microloan", 0.35, 0)
    )

    df["pd_true"] = 1 / (1 + np.exp(-logit))
    df["default"] = np.random.binomial(1, df["pd_true"])

    return df


if __name__ == "__main__":
    df = create_synthetic_bnpl_microloan_dataset()
    df.to_csv("data/synthetic/synthetic_bnpl_microloan.csv", index=False)
