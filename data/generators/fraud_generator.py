import numpy as np
import pandas as pd


def create_synthetic_fraud_dataset(
    n_transactions=100_000,
    fraud_rate_target=0.015,
    seed=42
):
    np.random.seed(seed)

    df = pd.DataFrame({
        "transaction_id": np.arange(1, n_transactions + 1),
        "customer_id": np.random.randint(1, 20_000, n_transactions),
        "merchant_id": np.random.randint(1, 5_000, n_transactions),
        "transaction_amount": np.random.lognormal(mean=3.3, sigma=1.1, size=n_transactions),
        "hour": np.random.randint(0, 24, n_transactions),
        "day_of_week": np.random.randint(0, 7, n_transactions),
        "transactions_last_24h": np.random.poisson(lam=2.0, size=n_transactions),
        "avg_customer_amount_30d": np.random.lognormal(mean=3.0, sigma=0.8, size=n_transactions),
        "merchant_risk_score": np.random.beta(a=2, b=8, size=n_transactions),
        "customer_tenure_months": np.random.exponential(scale=18, size=n_transactions),
        "device_age_days": np.random.exponential(scale=120, size=n_transactions),
        "is_foreign_transaction": np.random.binomial(1, 0.08, n_transactions),
        "is_high_risk_country": np.random.binomial(1, 0.04, n_transactions),
        "is_new_device": np.random.binomial(1, 0.12, n_transactions),
        "ip_mismatch": np.random.binomial(1, 0.07, n_transactions),
        "failed_login_attempts_24h": np.random.poisson(lam=0.3, size=n_transactions),
        "card_not_present": np.random.binomial(1, 0.55, n_transactions),
    })

    df["amount_to_customer_avg"] = (
        df["transaction_amount"] / (df["avg_customer_amount_30d"] + 1e-6)
    )

    df["night_transaction"] = ((df["hour"] >= 0) & (df["hour"] <= 5)).astype(int)

    logit = (
        -6.0
        + 0.70 * np.log1p(df["transaction_amount"])
        + 0.90 * (df["amount_to_customer_avg"] > 4).astype(int)
        + 0.45 * df["transactions_last_24h"]
        + 2.20 * df["merchant_risk_score"]
        + 0.90 * df["is_foreign_transaction"]
        + 1.30 * df["is_high_risk_country"]
        + 1.00 * df["is_new_device"]
        + 1.10 * df["ip_mismatch"]
        + 0.55 * df["failed_login_attempts_24h"]
        + 0.45 * df["card_not_present"]
        + 0.40 * df["night_transaction"]
        - 0.015 * df["customer_tenure_months"]
        - 0.002 * df["device_age_days"]
    )

    raw_probability = 1 / (1 + np.exp(-logit))

    scaling_factor = fraud_rate_target / raw_probability.mean()
    fraud_probability = np.clip(raw_probability * scaling_factor, 0, 0.95)

    df["fraud_probability_true"] = fraud_probability
    df["fraud"] = np.random.binomial(1, fraud_probability)

    return df


if __name__ == "__main__":
    df = create_synthetic_fraud_dataset()
    df.to_csv("data/synthetic/synthetic_fraud_transactions.csv", index=False)

    print("Synthetic fraud dataset created.")
    print(df.shape)
    print("Fraud rate:", df["fraud"].mean())
