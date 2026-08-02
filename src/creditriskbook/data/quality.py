"""Transparent data-quality rules and reproducible teaching defects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from .datasets import DatasetBundle


@dataclass(frozen=True)
class RuleResult:
    rule: str
    dimension: str
    severity: str
    failed_count: int
    evaluated_count: int
    threshold: int
    passed: bool
    detail: str


@dataclass(frozen=True)
class QualityReport:
    dataset_key: str
    row_count: int
    rules: tuple[RuleResult, ...]

    @property
    def critical_failure(self) -> bool:
        return any((not rule.passed) and rule.severity == "critical" for rule in self.rules)

    @property
    def failed_rules(self) -> tuple[str, ...]:
        return tuple(rule.rule for rule in self.rules if not rule.passed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_key": self.dataset_key,
            "row_count": self.row_count,
            "critical_failure": self.critical_failure,
            "failed_rules": list(self.failed_rules),
            "rules": [asdict(rule) for rule in self.rules],
        }


def _result(
    rule: str,
    dimension: str,
    severity: str,
    failed: int,
    evaluated: int,
    detail: str,
    threshold: int = 0,
) -> RuleResult:
    return RuleResult(
        rule, dimension, severity, failed, evaluated, threshold, failed <= threshold, detail
    )


def assess_quality(
    bundle: DatasetBundle,
    frame: pd.DataFrame | None = None,
    *,
    as_of_date: date | str = "2026-01-01",
) -> QualityReport:
    data = bundle.frame if frame is None else frame
    rules: list[RuleResult] = []
    required = {bundle.id_column, bundle.target, *bundle.model_features}
    missing_columns = sorted(required - set(data.columns))
    rules.append(
        _result(
            "required_columns",
            "completeness",
            "critical",
            len(missing_columns),
            len(required),
            f"Missing columns: {missing_columns}",
        )
    )
    if missing_columns:
        return QualityReport(bundle.key, len(data), tuple(rules))

    duplicate_count = int(data[bundle.id_column].duplicated(keep=False).sum())
    rules.append(
        _result(
            "unique_application_id",
            "uniqueness",
            "critical",
            duplicate_count,
            len(data),
            "Application identifiers must be unique.",
        )
    )

    null_count = int(data[list(bundle.model_features) + [bundle.target]].isna().any(axis=1).sum())
    rules.append(
        _result(
            "complete_model_fields",
            "completeness",
            "critical",
            null_count,
            len(data),
            "Baseline examples do not impute; incomplete rows are quarantined.",
        )
    )

    invalid_target = int((~data[bundle.target].isin([0, 1])).sum())
    rules.append(
        _result(
            "binary_target",
            "validity",
            "critical",
            invalid_target,
            len(data),
            "Target must use 1=default and 0=non-default.",
        )
    )

    for column, (lower, upper) in bundle.quality_spec.ranges.items():
        if column not in data:
            continue
        invalid = pd.Series(False, index=data.index)
        if lower is not None:
            invalid |= data[column] < lower
        if upper is not None:
            invalid |= data[column] > upper
        rules.append(
            _result(
                f"range_{column}",
                "validity",
                "critical",
                int(invalid.fillna(False).sum()),
                int(data[column].notna().sum()),
                f"Expected {lower if lower is not None else '-inf'} <= {column} <= {upper if upper is not None else 'inf'}.",
            )
        )

    for column, allowed in bundle.quality_spec.allowed_values.items():
        if column not in data:
            continue
        invalid = data[column].notna() & ~data[column].isin(allowed)
        rules.append(
            _result(
                f"domain_{column}",
                "validity",
                "critical",
                int(invalid.sum()),
                int(data[column].notna().sum()),
                f"Unexpected values: {sorted(map(str, set(data.loc[invalid, column])))}",
            )
        )

    if bundle.date_column and bundle.date_column in data:
        parsed = pd.to_datetime(data[bundle.date_column], errors="coerce")
        invalid_dates = parsed.isna() | (parsed > pd.Timestamp(as_of_date))
        rules.append(
            _result(
                "valid_as_of_date",
                "timeliness",
                "critical",
                int(invalid_dates.sum()),
                len(data),
                f"Dates must parse and be no later than {as_of_date}.",
            )
        )

    leakage = sorted(set(data.columns) & set(bundle.quality_spec.forbidden_model_columns))
    leakage_in_features = sorted(set(bundle.model_features) & set(leakage))
    ad_hoc_leakage = sorted(column for column in data if column.startswith("target_derived"))
    rules.append(
        _result(
            "no_target_leakage_in_model_contract",
            "lineage",
            "critical",
            len(leakage_in_features),
            len(bundle.model_features),
            f"Forbidden features in model contract: {leakage_in_features}",
        )
    )
    rules.append(
        _result(
            "flag_post_outcome_columns",
            "lineage",
            "warning",
            len(ad_hoc_leakage),
            len(data.columns),
            f"Post-outcome teaching columns present: {ad_hoc_leakage}",
        )
    )
    return QualityReport(bundle.key, len(data), tuple(rules))


def inject_teaching_defects(
    bundle: DatasetBundle,
    *,
    seed: int = 2026,
    rate: float = 0.01,
) -> pd.DataFrame:
    """Return a modified copy with documented, deterministic defects."""

    if not 0 < rate <= 0.10:
        raise ValueError("rate must be in (0, 0.10]")
    data = bundle.frame.copy(deep=True)
    rng = np.random.default_rng(seed)
    count = max(1, int(len(data) * rate))

    missing_rows = rng.choice(data.index, size=count, replace=False)
    data.loc[missing_rows, bundle.model_features[0]] = np.nan

    if bundle.numeric_features:
        range_column = next(
            (name for name in bundle.numeric_features if name in bundle.quality_spec.ranges),
            bundle.numeric_features[0],
        )
        invalid_rows = rng.choice(data.index, size=count, replace=False)
        _, upper = bundle.quality_spec.ranges.get(range_column, (None, None))
        replacement = (upper + 100.0) if upper is not None else -1.0
        data.loc[invalid_rows, range_column] = replacement

    if bundle.categorical_features:
        category_column = next(
            (
                name
                for name in bundle.categorical_features
                if name in bundle.quality_spec.allowed_values
            ),
            bundle.categorical_features[0],
        )
        invalid_rows = rng.choice(data.index, size=count, replace=False)
        if pd.api.types.is_numeric_dtype(data[category_column]):
            replacement = float(data[category_column].max()) + 999.0
        else:
            replacement = "__INVALID__"
        data.loc[invalid_rows, category_column] = replacement

    if bundle.date_column:
        future_rows = rng.choice(data.index, size=count, replace=False)
        data.loc[future_rows, bundle.date_column] = pd.Timestamp("2099-01-01")

    data["target_derived_score"] = data[bundle.target].astype(float)
    duplicates = data.sample(n=count, random_state=seed)
    data = pd.concat([data, duplicates], ignore_index=True)
    return data


def quarantine_invalid_rows(
    bundle: DatasetBundle,
    frame: pd.DataFrame,
    *,
    as_of_date: date | str = "2026-01-01",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separate valid model rows without imputation or winsorisation."""

    data = frame.copy()
    valid = ~data[bundle.id_column].duplicated(keep="first")
    valid &= ~data[list(bundle.model_features) + [bundle.target]].isna().any(axis=1)
    valid &= data[bundle.target].isin([0, 1])
    for column, (lower, upper) in bundle.quality_spec.ranges.items():
        if column not in data:
            continue
        if lower is not None:
            valid &= data[column] >= lower
        if upper is not None:
            valid &= data[column] <= upper
    for column, allowed in bundle.quality_spec.allowed_values.items():
        if column in data:
            valid &= data[column].isin(allowed)
    if bundle.date_column:
        parsed = pd.to_datetime(data[bundle.date_column], errors="coerce")
        valid &= parsed.notna() & (parsed <= pd.Timestamp(as_of_date))
        data[bundle.date_column] = parsed
    return data.loc[valid].copy(), data.loc[~valid].copy()
