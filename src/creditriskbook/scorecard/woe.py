"""Weight-of-evidence, information value, and stability calculations."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CharacteristicTable:
    feature: str
    table: pd.DataFrame
    information_value: float


@dataclass
class WOEEncoder:
    """Smoothed WOE encoder using WOE = ln(distribution_good/distribution_bad)."""

    smoothing: float = 0.5
    mappings_: dict[str, dict[str, float]] = field(default_factory=dict, init=False)
    tables_: dict[str, CharacteristicTable] = field(default_factory=dict, init=False)
    features_: tuple[str, ...] = field(default=(), init=False)

    def fit(self, binned: pd.DataFrame, y: pd.Series | np.ndarray) -> WOEEncoder:
        target = np.asarray(y, dtype=int)
        if not np.isin(target, [0, 1]).all() or np.unique(target).size != 2:
            raise ValueError("WOE requires a binary target with both classes")
        if self.smoothing <= 0:
            raise ValueError("smoothing must be strictly positive")
        tables: dict[str, CharacteristicTable] = {}
        mappings: dict[str, dict[str, float]] = {}
        for feature in binned.columns:
            work = pd.DataFrame({"bin": binned[feature].astype("string"), "target": target})
            grouped = work.groupby("bin", dropna=False, observed=True)["target"].agg(
                ["count", "sum"]
            )
            grouped = grouped.rename(columns={"sum": "bad"})
            grouped["good"] = grouped["count"] - grouped["bad"]
            k = len(grouped)
            grouped["dist_good"] = (grouped["good"] + self.smoothing) / (
                grouped["good"].sum() + self.smoothing * k
            )
            grouped["dist_bad"] = (grouped["bad"] + self.smoothing) / (
                grouped["bad"].sum() + self.smoothing * k
            )
            grouped["bad_rate"] = grouped["bad"] / grouped["count"]
            grouped["woe"] = np.log(grouped["dist_good"] / grouped["dist_bad"])
            grouped["iv_component"] = (grouped["dist_good"] - grouped["dist_bad"]) * grouped["woe"]
            table = grouped.reset_index()
            iv = float(table["iv_component"].sum())
            tables[feature] = CharacteristicTable(feature, table, iv)
            mappings[feature] = dict(
                zip(table["bin"].astype(str), table["woe"].astype(float), strict=False)
            )
        self.features_ = tuple(binned.columns)
        self.tables_ = tables
        self.mappings_ = mappings
        return self

    def transform(self, binned: pd.DataFrame) -> pd.DataFrame:
        if not self.mappings_:
            raise RuntimeError("WOEEncoder must be fitted before transform")
        missing = set(self.features_) - set(binned.columns)
        if missing:
            raise ValueError(f"Missing binned features: {sorted(missing)}")
        encoded = {}
        for feature in self.features_:
            encoded[feature] = (
                binned[feature]
                .astype("string")
                .map(self.mappings_[feature])
                .fillna(0.0)
                .astype(float)
            )
        return pd.DataFrame(encoded, index=binned.index)

    def fit_transform(self, binned: pd.DataFrame, y: pd.Series | np.ndarray) -> pd.DataFrame:
        return self.fit(binned, y).transform(binned)

    @property
    def information_values(self) -> pd.Series:
        return pd.Series(
            {feature: item.information_value for feature, item in self.tables_.items()}
        ).sort_values(ascending=False)


def population_stability_index(
    reference: pd.Series | np.ndarray,
    current: pd.Series | np.ndarray,
    *,
    bins: int = 10,
    smoothing: float = 1e-4,
) -> float:
    """Calculate PSI for numeric scores using reference quantile cut points."""

    ref = np.asarray(reference, dtype=float)
    cur = np.asarray(current, dtype=float)
    ref, cur = ref[np.isfinite(ref)], cur[np.isfinite(cur)]
    if len(ref) == 0 or len(cur) == 0:
        raise ValueError("PSI inputs require finite observations")
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    if len(edges) < 3:
        return 0.0
    ref_counts = np.histogram(ref, bins=edges)[0] / len(ref)
    cur_counts = np.histogram(cur, bins=edges)[0] / len(cur)
    ref_share, cur_share = np.maximum(ref_counts, smoothing), np.maximum(cur_counts, smoothing)
    return float(np.sum((cur_share - ref_share) * np.log(cur_share / ref_share)))
