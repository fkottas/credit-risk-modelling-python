"""An advanced from-scratch logistic credit scorecard."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .binning import BinningProcess
from .scaling import RatingScale, ScoreScale
from .woe import WOEEncoder


@dataclass
class IRLSLogisticRegression:
    """Penalised binary logistic regression fitted by Newton/IRLS."""

    l2: float = 1e-4
    max_iter: int = 100
    tolerance: float = 1e-8
    fit_intercept: bool = True
    coef_: np.ndarray | None = field(default=None, init=False)
    intercept_: float = field(default=0.0, init=False)
    covariance_: np.ndarray | None = field(default=None, init=False)
    n_iter_: int = field(default=0, init=False)
    converged_: bool = field(default=False, init=False)

    def fit(
        self,
        X: pd.DataFrame | np.ndarray,
        y: pd.Series | np.ndarray,
        sample_weight: np.ndarray | None = None,
    ) -> IRLSLogisticRegression:
        matrix = np.asarray(X, dtype=float)
        target = np.asarray(y, dtype=float)
        if matrix.ndim != 2 or target.shape != (len(matrix),):
            raise ValueError("X must be two-dimensional and y must match its rows")
        if not np.isin(target, [0, 1]).all() or np.unique(target).size != 2:
            raise ValueError("Logistic regression requires a binary target with both classes")
        design = np.column_stack([np.ones(len(matrix)), matrix]) if self.fit_intercept else matrix
        weights = (
            np.ones(len(matrix))
            if sample_weight is None
            else np.asarray(sample_weight, dtype=float)
        )
        if np.any(weights <= 0):
            raise ValueError("sample weights must be positive")
        beta = np.zeros(design.shape[1])
        penalty = np.eye(design.shape[1]) * self.l2
        if self.fit_intercept:
            penalty[0, 0] = 0.0
        for iteration in range(1, self.max_iter + 1):
            linear = np.clip(design @ beta, -35, 35)
            probability = 1.0 / (1.0 + np.exp(-linear))
            variance_weight = np.maximum(probability * (1 - probability) * weights, 1e-10)
            gradient = design.T @ ((target - probability) * weights) - penalty @ beta
            information = (design.T * variance_weight) @ design + penalty
            step = np.linalg.solve(information, gradient)
            beta_new = beta + step
            if np.max(np.abs(step)) < self.tolerance:
                beta = beta_new
                self.converged_ = True
                self.n_iter_ = iteration
                break
            beta = beta_new
        else:
            self.n_iter_ = self.max_iter
        self.intercept_ = float(beta[0]) if self.fit_intercept else 0.0
        self.coef_ = beta[1:].copy() if self.fit_intercept else beta.copy()
        self.covariance_ = np.linalg.pinv(information)
        return self

    def decision_function(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise RuntimeError("The model must be fitted before scoring")
        return self.intercept_ + np.asarray(X, dtype=float) @ self.coef_

    def predict_proba(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        linear = np.clip(self.decision_function(X), -35, 35)
        bad = 1.0 / (1.0 + np.exp(-linear))
        return np.column_stack([1.0 - bad, bad])


@dataclass
class LogisticScorecard:
    """Binning, WOE, logistic estimation, scoring, ratings, and explanations."""

    binning: BinningProcess = field(default_factory=BinningProcess)
    scale: ScoreScale = field(default_factory=ScoreScale)
    ratings: RatingScale = field(default_factory=RatingScale)
    smoothing: float = 0.5
    l2: float = 1e-4
    encoder_: WOEEncoder = field(init=False)
    model_: IRLSLogisticRegression = field(init=False)
    features_: tuple[str, ...] = field(default=(), init=False)

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series | np.ndarray,
        sample_weight: np.ndarray | None = None,
    ) -> LogisticScorecard:
        self.features_ = tuple(X.columns)
        binned = self.binning.fit_transform(X, y)
        self.encoder_ = WOEEncoder(self.smoothing)
        woe = self.encoder_.fit_transform(binned, y)
        self.model_ = IRLSLogisticRegression(l2=self.l2).fit(woe, y, sample_weight)
        return self

    def _woe(self, X: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        if not self.features_:
            raise RuntimeError("The scorecard must be fitted before scoring")
        binned = self.binning.transform(X[list(self.features_)])
        return binned, self.encoder_.transform(binned)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        _, woe = self._woe(X)
        return self.model_.predict_proba(woe)

    def score(self, X: pd.DataFrame) -> np.ndarray:
        return self.scale.probability_to_score(self.predict_proba(X)[:, 1])

    def score_components(self, X: pd.DataFrame) -> pd.DataFrame:
        binned, woe = self._woe(X)
        factor = self.scale.factor
        components = pd.DataFrame(index=X.index)
        components["base_points"] = self.scale.offset - factor * self.model_.intercept_
        for index, feature in enumerate(self.features_):
            components[feature] = -factor * self.model_.coef_[index] * woe[feature]
        components["raw_total"] = components.sum(axis=1)
        components["score"] = np.clip(
            np.rint(components["raw_total"]), self.scale.minimum, self.scale.maximum
        ).astype(int)
        components["pd"] = self.predict_proba(X)[:, 1]
        components["rating"] = self.ratings.assign(components["score"])
        for feature in self.features_:
            components[f"{feature}__bin"] = binned[feature]
        return components

    def points_table(self) -> pd.DataFrame:
        if not self.features_:
            raise RuntimeError("The scorecard must be fitted before creating a points table")
        rows: list[dict[str, object]] = []
        for index, feature in enumerate(self.features_):
            table = self.encoder_.tables_[feature].table
            for row in table.itertuples(index=False):
                rows.append(
                    {
                        "feature": feature,
                        "bin": row.bin,
                        "count": int(row.count),
                        "bad_rate": float(row.bad_rate),
                        "woe": float(row.woe),
                        "iv_component": float(row.iv_component),
                        "coefficient": float(self.model_.coef_[index]),
                        "points": float(-self.scale.factor * self.model_.coef_[index] * row.woe),
                    }
                )
        return pd.DataFrame(rows)

    def reason_codes(self, X: pd.DataFrame, *, top_n: int = 4) -> pd.DataFrame:
        components = self.score_components(X)
        table = self.points_table()
        best = table.groupby("feature")["points"].max()
        penalties = pd.DataFrame(
            {feature: best[feature] - components[feature] for feature in self.features_},
            index=X.index,
        )
        rows = []
        for index, values in penalties.iterrows():
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
