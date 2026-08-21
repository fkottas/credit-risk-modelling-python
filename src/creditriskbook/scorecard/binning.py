"""Original credit-scorecard binning algorithms.

The implementation deliberately avoids specialist scorecard packages.  Numeric
variables can be binned manually, by quantiles, by equal width, by supervised
ChiMerge, or by a monotonic ChiMerge variant.  Missing and special values are
always explicit bins so that training and scoring use the same contract.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
import pandas as pd

MISSING_BIN = "__MISSING__"
OTHER_BIN = "__OTHER__"


def _fmt(value: float) -> str:
    if np.isneginf(value):
        return "-inf"
    if np.isposinf(value):
        return "inf"
    return f"{value:.8g}"


def _numeric_labels(edges: np.ndarray) -> tuple[str, ...]:
    return tuple(
        f"({_fmt(left)}, {_fmt(right)}]" for left, right in zip(edges[:-1], edges[1:], strict=False)
    )


def _validate_binary_target(y: pd.Series) -> np.ndarray:
    values = np.asarray(y, dtype=int)
    if values.ndim != 1 or not np.isin(values, [0, 1]).all():
        raise ValueError("The target must be one-dimensional and contain only 0 and 1")
    if np.unique(values).size != 2:
        raise ValueError("The target must contain both non-events (0) and events (1)")
    return values


def _chi_square(left: tuple[int, int], right: tuple[int, int]) -> float:
    """Pearson chi-square for two adjacent [good, bad] rows, without scipy."""

    observed = np.asarray([left, right], dtype=float)
    total = observed.sum()
    if total == 0:
        return 0.0
    expected = observed.sum(axis=1, keepdims=True) @ observed.sum(axis=0, keepdims=True) / total
    mask = expected > 0
    return float(np.sum((observed[mask] - expected[mask]) ** 2 / expected[mask]))


@dataclass(frozen=True)
class NumericBinSpec:
    feature: str
    edges: tuple[float, ...]
    special_values: tuple[float, ...] = ()
    labels: tuple[str, ...] = ()
    method: str = "manual"
    trend: str | None = None

    def __post_init__(self) -> None:
        edges = np.asarray(self.edges, dtype=float)
        if len(edges) < 2 or np.any(np.diff(edges) <= 0):
            raise ValueError(f"Numeric edges for {self.feature!r} must be strictly increasing")
        if not np.isneginf(edges[0]) or not np.isposinf(edges[-1]):
            raise ValueError("Numeric edges must begin at -inf and end at inf")
        if self.labels and len(self.labels) != len(edges) - 1:
            raise ValueError("Numeric labels must match the number of intervals")

    @property
    def interval_labels(self) -> tuple[str, ...]:
        return self.labels or _numeric_labels(np.asarray(self.edges, dtype=float))

    @property
    def all_labels(self) -> tuple[str, ...]:
        specials = tuple(f"__SPECIAL__:{value!r}" for value in self.special_values)
        return self.interval_labels + specials + (MISSING_BIN,)

    def transform(self, values: pd.Series) -> pd.Series:
        numeric = pd.to_numeric(values, errors="coerce")
        result = pd.Series(MISSING_BIN, index=values.index, dtype="object")
        regular = numeric.notna()
        for value in self.special_values:
            mask = regular & (numeric == value)
            result.loc[mask] = f"__SPECIAL__:{value!r}"
            regular &= ~mask
        if regular.any():
            cut = pd.cut(
                numeric.loc[regular],
                bins=np.asarray(self.edges, dtype=float),
                labels=list(self.interval_labels),
                include_lowest=True,
                right=True,
            )
            result.loc[regular] = cut.astype("object")
        return result.astype("string")


@dataclass(frozen=True)
class CategoricalBinSpec:
    feature: str
    groups: tuple[tuple[str, ...], ...]
    labels: tuple[str, ...] = ()
    method: str = "manual"

    def __post_init__(self) -> None:
        flat = [value for group in self.groups for value in group]
        if len(flat) != len(set(flat)):
            raise ValueError(f"A category is assigned to multiple groups for {self.feature!r}")
        if self.labels and len(self.labels) != len(self.groups):
            raise ValueError("Categorical labels must match the number of groups")

    @property
    def group_labels(self) -> tuple[str, ...]:
        if self.labels:
            return self.labels
        return tuple("{" + "|".join(group) + "}" for group in self.groups)

    @property
    def all_labels(self) -> tuple[str, ...]:
        return self.group_labels + (OTHER_BIN, MISSING_BIN)

    def transform(self, values: pd.Series) -> pd.Series:
        text = values.astype("string")
        result = pd.Series(OTHER_BIN, index=values.index, dtype="object")
        result.loc[values.isna()] = MISSING_BIN
        for group, label in zip(self.groups, self.group_labels, strict=False):
            result.loc[text.isin(group) & values.notna()] = label
        return result.astype("string")


def manual_numeric_spec(
    feature: str,
    cut_points: Iterable[float],
    *,
    special_values: Iterable[float] = (),
    labels: Iterable[str] | None = None,
) -> NumericBinSpec:
    points = sorted(set(float(value) for value in cut_points if np.isfinite(value)))
    edges = (-np.inf, *points, np.inf)
    return NumericBinSpec(
        feature=feature,
        edges=edges,
        special_values=tuple(float(value) for value in special_values),
        labels=tuple(labels or ()),
        method="manual",
    )


def manual_categorical_spec(
    feature: str,
    groups: Iterable[Iterable[Any]],
    *,
    labels: Iterable[str] | None = None,
) -> CategoricalBinSpec:
    normalised = tuple(tuple(str(value) for value in group) for group in groups)
    return CategoricalBinSpec(feature, normalised, tuple(labels or ()), "manual")


@dataclass
class _Interval:
    left: float
    right: float
    good: int
    bad: int

    @property
    def n(self) -> int:
        return self.good + self.bad

    @property
    def bad_rate(self) -> float:
        return self.bad / self.n if self.n else 0.0


class NumericBinner:
    """Fit transparent numeric bins with deterministic adjacent merging."""

    def __init__(
        self,
        *,
        method: Literal["quantile", "uniform", "chimerge", "monotonic"] = "monotonic",
        max_bins: int = 6,
        prebins: int = 20,
        min_bin_fraction: float = 0.05,
        min_events: int = 5,
        monotonic_trend: Literal["auto", "increasing", "decreasing"] = "auto",
        special_values: Iterable[float] = (),
    ) -> None:
        if max_bins < 2:
            raise ValueError("max_bins must be at least 2")
        if prebins < max_bins:
            raise ValueError("prebins must be greater than or equal to max_bins")
        if not 0 <= min_bin_fraction < 0.5:
            raise ValueError("min_bin_fraction must be in [0, 0.5)")
        self.method = method
        self.max_bins = max_bins
        self.prebins = prebins
        self.min_bin_fraction = min_bin_fraction
        self.min_events = min_events
        self.monotonic_trend = monotonic_trend
        self.special_values = tuple(float(value) for value in special_values)

    @staticmethod
    def _candidate_edges(values: np.ndarray, method: str, bins: int) -> np.ndarray:
        if np.unique(values).size < 2:
            return np.array([-np.inf, np.inf])
        if method == "uniform":
            internal = np.linspace(float(values.min()), float(values.max()), bins + 1)[1:-1]
        else:
            internal = np.quantile(values, np.linspace(0, 1, bins + 1)[1:-1])
        internal = np.unique(internal[np.isfinite(internal)])
        return np.r_[-np.inf, internal, np.inf]

    @staticmethod
    def _intervals(values: np.ndarray, target: np.ndarray, edges: np.ndarray) -> list[_Interval]:
        index = np.digitize(values, edges[1:-1], right=True)
        intervals: list[_Interval] = []
        for i in range(len(edges) - 1):
            mask = index == i
            if not mask.any():
                continue
            bad = int(target[mask].sum())
            intervals.append(
                _Interval(float(edges[i]), float(edges[i + 1]), int(mask.sum()) - bad, bad)
            )
        if intervals:
            intervals[0].left = -np.inf
            intervals[-1].right = np.inf
        return intervals

    @staticmethod
    def _merge(intervals: list[_Interval], left_index: int) -> None:
        left, right = intervals[left_index], intervals[left_index + 1]
        intervals[left_index] = _Interval(
            left.left, right.right, left.good + right.good, left.bad + right.bad
        )
        del intervals[left_index + 1]

    def _merge_constraints(self, intervals: list[_Interval], n_regular: int) -> None:
        minimum = max(1, int(np.ceil(self.min_bin_fraction * n_regular)))
        while len(intervals) > 1:
            violations = [
                i
                for i, item in enumerate(intervals)
                if item.n < minimum or item.bad < self.min_events or item.good < self.min_events
            ]
            if not violations:
                break
            i = min(violations, key=lambda j: (intervals[j].n, j))
            candidates = []
            if i > 0:
                candidates.append((abs(intervals[i].bad_rate - intervals[i - 1].bad_rate), i - 1))
            if i < len(intervals) - 1:
                candidates.append((abs(intervals[i].bad_rate - intervals[i + 1].bad_rate), i))
            self._merge(intervals, min(candidates)[1])

    def _merge_chi_square(self, intervals: list[_Interval]) -> None:
        while len(intervals) > self.max_bins:
            scores = [
                _chi_square((left.good, left.bad), (right.good, right.bad))
                for left, right in zip(intervals[:-1], intervals[1:], strict=False)
            ]
            self._merge(intervals, int(np.argmin(scores)))

    def _merge_monotonic(self, intervals: list[_Interval]) -> str:
        rates = np.array([item.bad_rate for item in intervals])
        if self.monotonic_trend == "auto":
            trend = (
                "increasing"
                if np.corrcoef(np.arange(len(rates)), rates)[0, 1] >= 0
                else "decreasing"
            )
        else:
            trend = self.monotonic_trend
        while len(intervals) > 2:
            rates = np.array([item.bad_rate for item in intervals])
            differences = np.diff(rates)
            violating = np.flatnonzero(
                differences < -1e-12 if trend == "increasing" else differences > 1e-12
            )
            if not len(violating):
                break
            i = min(violating, key=lambda j: (abs(differences[j]), j))
            self._merge(intervals, int(i))
        return trend

    def fit(self, feature: str, x: pd.Series, y: pd.Series) -> NumericBinSpec:
        target = _validate_binary_target(y)
        numeric = pd.to_numeric(x, errors="coerce").to_numpy(dtype=float)
        regular = np.isfinite(numeric)
        for value in self.special_values:
            regular &= numeric != value
        values, observed = numeric[regular], target[regular]
        if len(values) == 0:
            raise ValueError(f"Feature {feature!r} has no regular numeric observations")
        candidate_method = "uniform" if self.method == "uniform" else "quantile"
        initial_bins = self.max_bins if self.method in {"quantile", "uniform"} else self.prebins
        edges = self._candidate_edges(values, candidate_method, initial_bins)
        intervals = self._intervals(values, observed, edges)
        self._merge_constraints(intervals, len(values))
        if self.method in {"chimerge", "monotonic"}:
            self._merge_chi_square(intervals)
        trend = self._merge_monotonic(intervals) if self.method == "monotonic" else None
        fitted_edges = tuple([intervals[0].left] + [item.right for item in intervals])
        return NumericBinSpec(
            feature, fitted_edges, self.special_values, method=self.method, trend=trend
        )


class CategoricalBinner:
    """Supervised category grouping ordered by empirical event rate."""

    def __init__(self, *, max_bins: int = 6, min_bin_fraction: float = 0.03) -> None:
        if max_bins < 2:
            raise ValueError("max_bins must be at least 2")
        self.max_bins = max_bins
        self.min_bin_fraction = min_bin_fraction

    def fit(self, feature: str, x: pd.Series, y: pd.Series) -> CategoricalBinSpec:
        _validate_binary_target(y)
        work = pd.DataFrame({"x": x.astype("string"), "y": np.asarray(y, dtype=int)}).dropna(
            subset=["x"]
        )
        if work.empty:
            raise ValueError(f"Feature {feature!r} has no non-missing categories")
        stats = (
            work.groupby("x", observed=True)["y"].agg(["size", "mean"]).sort_values(["mean", "x"])
        )
        minimum = max(1, int(np.ceil(len(work) * self.min_bin_fraction)))
        rare = stats.index[stats["size"] < minimum].astype(str).tolist()
        regular = stats.index[stats["size"] >= minimum].astype(str).tolist()
        n_groups = min(self.max_bins - int(bool(rare)), max(1, len(regular)))
        groups = [
            tuple(chunk.tolist())
            for chunk in np.array_split(np.asarray(regular, dtype=object), n_groups)
            if len(chunk)
        ]
        if rare:
            groups.append(tuple(rare))
        return CategoricalBinSpec(feature, tuple(groups), method="event_rate_grouping")


@dataclass
class BinningProcess:
    """Fit and apply a mixed numeric/categorical binning contract."""

    numeric_method: str = "monotonic"
    max_bins: int = 6
    prebins: int = 20
    min_bin_fraction: float = 0.05
    min_events: int = 5
    manual_specs: dict[str, NumericBinSpec | CategoricalBinSpec] = field(default_factory=dict)
    special_values: dict[str, tuple[float, ...]] = field(default_factory=dict)
    specs_: dict[str, NumericBinSpec | CategoricalBinSpec] = field(default_factory=dict, init=False)
    features_: tuple[str, ...] = field(default=(), init=False)

    def fit(self, X: pd.DataFrame, y: pd.Series | np.ndarray) -> BinningProcess:
        target = pd.Series(_validate_binary_target(pd.Series(y)), index=X.index)
        specs: dict[str, NumericBinSpec | CategoricalBinSpec] = {}
        for feature in X.columns:
            if feature in self.manual_specs:
                spec = self.manual_specs[feature]
                if spec.feature != feature:
                    raise ValueError(
                        f"Manual spec key {feature!r} does not match spec.feature {spec.feature!r}"
                    )
            elif pd.api.types.is_numeric_dtype(X[feature]):
                spec = NumericBinner(
                    method=self.numeric_method,
                    max_bins=self.max_bins,
                    prebins=self.prebins,
                    min_bin_fraction=self.min_bin_fraction,
                    min_events=self.min_events,
                    special_values=self.special_values.get(feature, ()),
                ).fit(feature, X[feature], target)
            else:
                spec = CategoricalBinner(
                    max_bins=self.max_bins, min_bin_fraction=self.min_bin_fraction
                ).fit(feature, X[feature], target)
            specs[feature] = spec
        self.specs_ = specs
        self.features_ = tuple(X.columns)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if not self.specs_:
            raise RuntimeError("BinningProcess must be fitted before transform")
        missing = set(self.features_) - set(X.columns)
        if missing:
            raise ValueError(f"Missing scoring features: {sorted(missing)}")
        return pd.DataFrame(
            {feature: self.specs_[feature].transform(X[feature]) for feature in self.features_}
        )

    def fit_transform(self, X: pd.DataFrame, y: pd.Series | np.ndarray) -> pd.DataFrame:
        return self.fit(X, y).transform(X)
