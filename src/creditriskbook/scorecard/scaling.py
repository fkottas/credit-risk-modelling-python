"""Score scaling, rating bands, and model-agnostic score mapping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ScoreScale:
    base_score: float = 600.0
    pdo: float = 50.0
    base_odds_good_to_bad: float = 20.0
    minimum: int = 300
    maximum: int = 900

    def __post_init__(self) -> None:
        if self.pdo <= 0 or self.base_odds_good_to_bad <= 0:
            raise ValueError("PDO and base odds must be positive")
        if self.minimum >= self.maximum:
            raise ValueError("minimum must be below maximum")

    @property
    def factor(self) -> float:
        return self.pdo / np.log(2.0)

    @property
    def offset(self) -> float:
        return self.base_score - self.factor * np.log(self.base_odds_good_to_bad)

    def probability_to_score(self, pd_values: np.ndarray | pd.Series) -> np.ndarray:
        probability = np.clip(np.asarray(pd_values, dtype=float), 1e-9, 1 - 1e-9)
        score = self.offset - self.factor * np.log(probability / (1.0 - probability))
        return np.clip(np.rint(score), self.minimum, self.maximum).astype(int)

    def score_to_probability(self, score: np.ndarray | pd.Series) -> np.ndarray:
        log_odds = (self.offset - np.asarray(score, dtype=float)) / self.factor
        return 1.0 / (1.0 + np.exp(-log_odds))


@dataclass(frozen=True)
class RatingScale:
    """Ascending minimum-score thresholds; higher grades represent lower risk."""

    thresholds: tuple[tuple[int, str], ...] = (
        (300, "R8"),
        (500, "R7"),
        (550, "R6"),
        (600, "R5"),
        (650, "R4"),
        (700, "R3"),
        (750, "R2"),
        (800, "R1"),
    )

    def assign(self, scores: np.ndarray | pd.Series) -> np.ndarray:
        ordered = sorted(self.thresholds)
        result = np.full(len(scores), ordered[0][1], dtype=object)
        values = np.asarray(scores, dtype=float)
        for minimum, grade in ordered:
            result[values >= minimum] = grade
        return result


@dataclass
class ModelScoreMapper:
    """Map any binary probabilistic model to a governed score and reason codes.

    This preserves the model's probabilities exactly up to score rounding.  For
    non-additive models, feature reasons are sensitivity-based rather than
    pretending that a tree ensemble has logistic scorecard bin points.
    """

    model: Any
    scale: ScoreScale = field(default_factory=ScoreScale)
    feature_names: tuple[str, ...] = ()
    reference_: dict[str, Any] = field(default_factory=dict, init=False)

    def fit_reference(self, X: pd.DataFrame) -> ModelScoreMapper:
        self.feature_names = tuple(self.feature_names or tuple(X.columns))
        reference: dict[str, Any] = {}
        for feature in self.feature_names:
            series = X[feature]
            if pd.api.types.is_numeric_dtype(series):
                reference[feature] = float(series.median())
            else:
                mode = series.mode(dropna=True)
                reference[feature] = mode.iloc[0] if len(mode) else None
        self.reference_ = reference
        return self

    def predict_pd(self, X: pd.DataFrame) -> np.ndarray:
        if hasattr(self.model, "predict_proba"):
            probability = np.asarray(self.model.predict_proba(X))
            return probability[:, 1] if probability.ndim == 2 else probability
        if hasattr(self.model, "decision_function"):
            logit = np.asarray(self.model.decision_function(X), dtype=float)
            return 1.0 / (1.0 + np.exp(-logit))
        prediction = np.asarray(self.model(X), dtype=float)
        if np.any((prediction < 0) | (prediction > 1)):
            raise ValueError("Callable model output must be probabilities in [0, 1]")
        return prediction

    def score(self, X: pd.DataFrame) -> np.ndarray:
        return self.scale.probability_to_score(self.predict_pd(X))

    def reason_codes(self, X: pd.DataFrame, *, top_n: int = 4) -> pd.DataFrame:
        if not self.reference_:
            raise RuntimeError("Call fit_reference before requesting model-agnostic reason codes")
        baseline = self.score(X)
        penalties: dict[str, np.ndarray] = {}
        for feature in self.feature_names:
            counterfactual = X.copy()
            counterfactual[feature] = self.reference_[feature]
            penalties[feature] = self.score(counterfactual) - baseline
        matrix = pd.DataFrame(penalties, index=X.index)
        rows = []
        for index, values in matrix.iterrows():
            ranked = values.sort_values(ascending=False)
            rows.append(
                {
                    "index": index,
                    **{
                        f"reason_{i + 1}": feature for i, feature in enumerate(ranked.index[:top_n])
                    },
                    **{
                        f"penalty_{i + 1}": float(value)
                        for i, value in enumerate(ranked.iloc[:top_n])
                    },
                }
            )
        return pd.DataFrame(rows).set_index("index")
