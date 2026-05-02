import numpy as np
import pandas as pd
from sklearn.datasets import fetch_openml


def load_base_customers():
    """
    Load base customer dataset (OpenML German Credit)
    """
    data = fetch_openml(name="credit-g", version=1, as_frame=True)
    df = data.frame.copy()

    df["credit_default"] = (df["class"] == "bad").astype(int)
    df = df.drop(columns=["class"])

    df["customer_id"] = np.arange(1, len(df) + 1)

    return df


def create_hybrid_fraud_dataset(
    n_transactions=100_000,
    fraud_rate_target=0.015,
    seed=42
):
    np.random.seed(seed)

    customers = load_base_customers()

    sampled = customers.sample(
        n=n_transactions,
        replace=True,
        random_state=seed
    ).reset_index(drop=True)

    df = sampled.copy()

    # Transaction layer
    df["transaction_id"] = np.arange(1, n_transactions + 1)
    df["merchant_id"] = np.random.randint(1, 5000, n_transactions)

    df["transaction_amount"] = np.random.lognormal(3.3, 1.1, n_transactions)
    df["hour"] = np.random.randint(0, 24, n_transactions)

    df["transactions_last_24h"] = np.random.poisson(2, n_transactions)
    df["avg_customer_amount_30d"] = np.random.lognormal(3.0, 0.8, n_transactions)

    df["amount_ratio"] = df["transaction_amount"] / (
        df["avg_customer_amount_30d"] + 1e-6
    )

    # Behavioral / fraud signals
    df["merchant_risk_score"] = np.random.beta(2, 8, n_transactions)
    df["is_foreign"] = np.random.binomial(1, 0.08, n_transactions)
    df["is_new_device"] = np.random.binomial(1, 0.12, n_transactions)
    df["ip_mismatch"] = np.random.binomial(1, 0.07, n_transactions)
    df["failed_logins"] = np.random.poisson(0.3, n_transactions)

    df["night_txn"] = ((df["hour"] <= 5)).astype(int)

    # Credit risk interaction
    credit_risk = df["credit_default"]

    logit = (
        -6.2
        + 0.7 * np.log1p(df["transaction_amount"])
        + 1.0 * (df["amount_ratio"] > 4).astype(int)
        + 0.45 * df["transactions_last_24h"]
        + 2.3 * df["merchant_risk_score"]
        + 0.9 * df["is_foreign"]
        + 1.1 * df["is_new_device"]
        + 1.2 * df["ip_mismatch"]
        + 0.6 * df["failed_logins"]
        + 0.4 * df["night_txn"]
        + 0.5 * credit_risk
    )

    prob = 1 / (1 + np.exp(-logit))

    scaling = fraud_rate_target / prob.mean()
    prob = np.clip(prob * scaling, 0, 0.95)

    df["fraud_probability_true"] = prob
    df["fraud"] = np.random.binomial(1, prob)

    return df


if __name__ == "__main__":
    df = create_hybrid_fraud_dataset()

    df.to_csv(
        "data/synthetic/hybrid_fraud_dataset.csv",
        index=False
    )

    print("Hybrid fraud dataset created:", df.shape)
    print("Fraud rate:", df["fraud"].mean())
