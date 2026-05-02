"""
Basic data quality checks.
"""

import pandas as pd


def dataset_overview(df):
    """
    Return basic dataset overview.
    """
    return pd.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes.astype(str).values,
        "missing_count": df.isna().sum().values,
        "missing_rate": df.isna().mean().values,
        "unique_values": df.nunique(dropna=False).values
    })


def target_summary(df, target):
    """
    Return target distribution.
    """
    return df[target].value_counts(dropna=False).to_frame("count").assign(
        rate=lambda x: x["count"] / x["count"].sum()
    )


def missing_summary(df):
    """
    Return only columns with missing values.
    """
    summary = dataset_overview(df)
    return summary[summary["missing_count"] > 0].sort_values(
        "missing_rate",
        ascending=False
    )


def duplicate_summary(df):
    """
    Return duplicate row count and rate.
    """
    duplicate_count = df.duplicated().sum()

    return {
        "duplicate_count": duplicate_count,
        "duplicate_rate": duplicate_count / len(df)
    }
