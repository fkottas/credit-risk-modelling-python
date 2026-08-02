"""A transparent baseline probability-of-default pipeline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from creditriskbook.data.datasets import DatasetBundle


@dataclass(frozen=True)
class PDModel:
    pipeline: Pipeline
    dataset_key: str
    target: str
    numeric_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    split_strategy: str


def split_dataset(
    bundle: DatasetBundle,
    frame: pd.DataFrame,
    *,
    test_size: float = 0.25,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not 0.10 <= test_size <= 0.50:
        raise ValueError("test_size must be between 0.10 and 0.50")
    if bundle.date_column:
        ordered = frame.sort_values([bundle.date_column, bundle.id_column]).reset_index(drop=True)
        split_at = int(len(ordered) * (1.0 - test_size))
        train, test = ordered.iloc[:split_at].copy(), ordered.iloc[split_at:].copy()
        if train[bundle.date_column].max() > test[bundle.date_column].min():
            raise AssertionError("Out-of-time split ordering failed")
        return train, test
    train, test = train_test_split(
        frame,
        test_size=test_size,
        random_state=seed,
        stratify=frame[bundle.target],
    )
    return train.copy(), test.copy()


def _pipeline(bundle: DatasetBundle) -> Pipeline:
    transformers: list[tuple[str, object, list[str]]] = []
    if bundle.numeric_features:
        transformers.append(("numeric", StandardScaler(), list(bundle.numeric_features)))
    if bundle.categorical_features:
        transformers.append(
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", drop=None),
                list(bundle.categorical_features),
            )
        )
    preprocessing = ColumnTransformer(transformers=transformers, remainder="drop")
    estimator = LogisticRegression(max_iter=2_000, solver="lbfgs")
    return Pipeline([("preprocessing", preprocessing), ("model", estimator)])


def fit_pd_model(bundle: DatasetBundle, train: pd.DataFrame) -> PDModel:
    required = list(bundle.model_features) + [bundle.target]
    if train[required].isna().any().any():
        raise ValueError("Training data contain missing model fields; run quarantine_invalid_rows first")
    if train[bundle.target].nunique() != 2:
        raise ValueError("Training target must contain both default and non-default observations")
    pipeline = _pipeline(bundle)
    pipeline.fit(train[list(bundle.model_features)], train[bundle.target].astype(int))
    return PDModel(
        pipeline=pipeline,
        dataset_key=bundle.key,
        target=bundle.target,
        numeric_features=bundle.numeric_features,
        categorical_features=bundle.categorical_features,
        split_strategy=bundle.split_strategy,
    )


def score_pd(model: PDModel, frame: pd.DataFrame) -> np.ndarray:
    features = list(model.numeric_features + model.categorical_features)
    return model.pipeline.predict_proba(frame[features])[:, 1]


def evaluate_pd(y_true: pd.Series | np.ndarray, predicted_pd: np.ndarray) -> dict[str, float]:
    observed = np.asarray(y_true, dtype=int)
    predicted = np.clip(np.asarray(predicted_pd, dtype=float), 1e-9, 1 - 1e-9)
    if len(observed) != len(predicted):
        raise ValueError("Observed and predicted arrays must have equal length")
    if np.unique(observed).size != 2:
        raise ValueError("Evaluation requires both target classes")
    defaults = predicted[observed == 1]
    non_defaults = predicted[observed == 0]
    ks = float(ks_2samp(defaults, non_defaults, alternative="two-sided").statistic)
    return {
        "n": float(len(observed)),
        "default_rate": float(observed.mean()),
        "mean_predicted_pd": float(predicted.mean()),
        "roc_auc": float(roc_auc_score(observed, predicted)),
        "brier_score": float(brier_score_loss(observed, predicted)),
        "log_loss": float(log_loss(observed, predicted, labels=[0, 1])),
        "ks": ks,
    }

