"""Chapter 19: Internal, Bureau, Alternative, Public, and Synthetic Data.

Standalone construction code: no creditriskbook imports.
"""

import pandas as pd


def source_fit_table() -> pd.DataFrame:
    """Map each empirical question to data that can actually answer it."""
    return pd.DataFrame(
        [
            ("application PD", "UCI Taiwan card", "default outcome, no dates", "benchmark only"),
            ("fair-lending decisions", "HMDA", "application outcomes", "not a PD dataset"),
            (
                "SME loan performance",
                "SBA 7(a)/504 FOIA",
                "loan outcomes",
                "definitions and vintages required",
            ),
            (
                "complaint NLP",
                "CFPB complaints",
                "narratives and responses",
                "not underwriting evidence",
            ),
            (
                "lifetime mortgage",
                "Fannie/Freddie",
                "monthly performance",
                "provider terms; not bundled",
            ),
        ],
        columns=["question", "candidate_source", "useful_content", "boundary"],
    )


table = source_fit_table()
print(table.to_string(index=False))
