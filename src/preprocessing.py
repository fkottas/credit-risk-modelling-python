"""
Basic preprocessing utilities for credit risk modelling.
"""

import pandas as pd


def identify_variable_types(df, target=None):
    """
    Identify numerical and categorical variables.
    """
    exclude = [target] if target else []

    numerical = [col for col in df.select_dtypes(include=["number"]).columns if col not in exclude]

    categorical = [
        col
        for col in df.select_dtypes(include=["object", "category", "bool"]).columns
        if col not in exclude
    ]

    return numerical, categorical


def missing_value_report(df):
    """
    Create missing value summary.
    """
    report = pd.DataFrame({"missing_count": df.isna().sum(), "missing_rate": df.isna().mean()})

    return report.sort_values("missing_rate", ascending=False)


def fill_missing_values(df, numerical_strategy="median", categorical_strategy="missing"):
    """
    Fill missing values using simple default strategies.
    """
    df = df.copy()

    numerical_cols, categorical_cols = identify_variable_types(df)

    for col in numerical_cols:
        if numerical_strategy == "median":
            df[col] = df[col].fillna(df[col].median())
        elif numerical_strategy == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif isinstance(numerical_strategy, int | float):
            df[col] = df[col].fillna(numerical_strategy)

    for col in categorical_cols:
        if categorical_strategy == "missing":
            df[col] = df[col].fillna("Missing")
        elif categorical_strategy == "mode":
            df[col] = df[col].fillna(df[col].mode()[0])

    return df


def cap_outliers_iqr(df, columns=None, multiplier=1.5):
    """
    Cap numerical outliers using the IQR rule.
    """
    df = df.copy()

    if columns is None:
        columns = df.select_dtypes(include=["number"]).columns

    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr

        df[col] = df[col].clip(lower, upper)

    return df


def one_hot_encode(df, categorical_cols=None, drop_first=True):
    """
    One-hot encode categorical variables.
    """
    if categorical_cols is None:
        _, categorical_cols = identify_variable_types(df)

    return pd.get_dummies(df, columns=categorical_cols, drop_first=drop_first)


def basic_preprocessing_pipeline(df, target=None):
    """
    Basic preprocessing pipeline:
    - Fill missing values
    - Cap outliers
    - One-hot encode categorical variables
    """
    df = df.copy()

    y = None
    if target is not None:
        y = df[target]
        X = df.drop(columns=[target])
    else:
        X = df

    X = fill_missing_values(X)
    X = cap_outliers_iqr(X)
    X = one_hot_encode(X)

    if target is not None:
        return X, y

    return X
