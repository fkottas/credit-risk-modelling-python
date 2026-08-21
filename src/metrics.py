"""
Model evaluation metrics for credit risk modelling.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_auc_score


def gini_score(y_true, y_score):
    """
    Gini coefficient based on AUC.
    """
    auc = roc_auc_score(y_true, y_score)
    return 2 * auc - 1


def ks_statistic(y_true, y_score):
    """
    Kolmogorov-Smirnov statistic for binary classification.
    """
    data = pd.DataFrame({"y_true": y_true, "y_score": y_score}).sort_values(
        "y_score", ascending=False
    )

    data["cum_bad"] = (data["y_true"] == 1).cumsum() / (data["y_true"] == 1).sum()
    data["cum_good"] = (data["y_true"] == 0).cumsum() / (data["y_true"] == 0).sum()

    return np.max(np.abs(data["cum_bad"] - data["cum_good"]))


def classification_summary(y_true, y_pred):
    """
    Confusion matrix summary.
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    return {
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "true_positive": tp,
        "accuracy": (tp + tn) / (tp + tn + fp + fn),
        "sensitivity": tp / (tp + fn) if (tp + fn) > 0 else np.nan,
        "specificity": tn / (tn + fp) if (tn + fp) > 0 else np.nan,
    }


def population_stability_index(expected, actual, bins=10):
    """
    Calculate Population Stability Index (PSI).
    """
    expected = np.asarray(expected)
    actual = np.asarray(actual)

    breakpoints = np.percentile(expected, np.linspace(0, 100, bins + 1))
    breakpoints = np.unique(breakpoints)

    expected_counts, _ = np.histogram(expected, bins=breakpoints)
    actual_counts, _ = np.histogram(actual, bins=breakpoints)

    expected_pct = expected_counts / max(expected_counts.sum(), 1)
    actual_pct = actual_counts / max(actual_counts.sum(), 1)

    expected_pct = np.where(expected_pct == 0, 1e-6, expected_pct)
    actual_pct = np.where(actual_pct == 0, 1e-6, actual_pct)

    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))

    return psi
