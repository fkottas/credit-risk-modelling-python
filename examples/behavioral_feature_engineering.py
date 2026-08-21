"""Chapter 24: clean longitudinal data and build point-in-time features."""

from __future__ import annotations

import pandas as pd

from creditriskbook.data import make_behavioral_credit_history
from creditriskbook.data.cleaning import clean_monthly_performance
from creditriskbook.features import build_behavioral_features


def run(seed: int = 2401, n_customers: int = 800) -> tuple[pd.DataFrame, pd.DataFrame]:
    case = make_behavioral_credit_history(
        n_customers=n_customers,
        months=18,
        seed=seed,
    )
    reference_dates = case.applications[["customer_id", "reference_date"]]
    cleaning = clean_monthly_performance(case.monthly_performance, reference_dates)
    if not cleaning.issues.empty:
        raise AssertionError("The clean generator should not produce quarantined performance rows")
    features = build_behavioral_features(
        cleaning.clean,
        case.contracts,
        reference_dates,
        enquiries=case.bureau_enquiries,
    )
    model_table = case.applications.merge(
        features,
        on=["customer_id", "reference_date"],
        validate="one_to_one",
    )
    columns = [
        "max_dpd_6m",
        "last_dpd",
        "count_dpd30_6m",
        "count_contracts_last_6m",
        "current_utilisation",
    ]
    characteristic_rows: list[dict[str, object]] = []
    for column in columns:
        bands = pd.qcut(model_table[column], q=4, duplicates="drop")
        table = (
            model_table.assign(band=bands)
            .groupby("band", observed=True)["default_12m"]
            .agg(observations="size", defaults="sum", default_rate="mean")
            .reset_index()
        )
        table.insert(0, "feature", column)
        characteristic_rows.extend(table.to_dict("records"))
    characteristic = pd.DataFrame(characteristic_rows)
    return model_table, characteristic


if __name__ == "__main__":
    model_table, characteristic = run()
    print(model_table.head().to_string(index=False))
    print(characteristic.to_string(index=False))
