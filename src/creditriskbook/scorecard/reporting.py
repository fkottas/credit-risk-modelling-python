"""Characteristic-analysis exports suitable for review packs and teaching."""

from __future__ import annotations

import html
from pathlib import Path

import pandas as pd

from .model import LogisticScorecard


def characteristic_summary(scorecard: LogisticScorecard) -> pd.DataFrame:
    points = scorecard.points_table()
    return (
        points.groupby("feature", as_index=False)
        .agg(
            bins=("bin", "count"),
            observations=("count", "sum"),
            information_value=("iv_component", "sum"),
            min_bad_rate=("bad_rate", "min"),
            max_bad_rate=("bad_rate", "max"),
            points_range=("points", lambda values: float(values.max() - values.min())),
        )
        .sort_values("information_value", ascending=False)
    )


def export_characteristic_report(
    scorecard: LogisticScorecard, output_dir: str | Path
) -> dict[str, Path]:
    """Write CSV tables and a dependency-light HTML review pack."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    points = scorecard.points_table()
    summary = characteristic_summary(scorecard)
    points_path = destination / "scorecard_points.csv"
    summary_path = destination / "characteristic_summary.csv"
    html_path = destination / "characteristic_analysis.html"
    points.to_csv(points_path, index=False)
    summary.to_csv(summary_path, index=False)
    sections = []
    for feature, table in points.groupby("feature", sort=False):
        sections.append(
            f"<h2>{html.escape(str(feature))}</h2>{table.to_html(index=False, float_format=lambda x: f'{x:.5f}')}"
        )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Characteristic analysis</title>
<style>body{{font:14px Arial;max-width:1200px;margin:2rem auto;color:#18324b}}table{{border-collapse:collapse;width:100%;margin-bottom:2rem}}th,td{{border:1px solid #c8d4df;padding:.4rem;text-align:right}}th{{background:#e8eef5}}td:first-child,td:nth-child(2){{text-align:left}}h1,h2{{color:#1f4d78}}</style>
</head><body><h1>Scorecard characteristic analysis</h1><p>Generated from the fitted training sample. Validate independently before use.</p>
<h2>Summary</h2>{summary.to_html(index=False, float_format=lambda x: f"{x:.5f}")}{"".join(sections)}</body></html>"""
    html_path.write_text(document, encoding="utf-8")
    return {"points": points_path, "summary": summary_path, "html": html_path}
