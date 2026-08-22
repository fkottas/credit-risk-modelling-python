from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from creditriskbook.data import load_cfpb_complaint_extract, load_world_bank_wdi


class PublicDataTests(unittest.TestCase):
    def test_world_bank_adapter_preserves_indicator_identity_and_metadata(self) -> None:
        payload = [
            {"lastupdated": "2026-07-13"},
            [
                {
                    "indicator": {"id": "NY.GDP.MKTP.KD.ZG", "value": "GDP growth"},
                    "country": {"id": "GR", "value": "Greece"},
                    "countryiso3code": "GRC",
                    "date": "2025",
                    "value": 2.07,
                    "unit": "",
                    "obs_status": "",
                },
                {
                    "indicator": {"id": "NY.GDP.MKTP.KD.ZG", "value": "GDP growth"},
                    "country": {"id": "GR", "value": "Greece"},
                    "countryiso3code": "GRC",
                    "date": "2024",
                    "value": 2.09,
                    "unit": "",
                    "obs_status": "",
                },
            ],
        ]

        def opener(request: object, timeout: int) -> io.BytesIO:
            self.assertIn("api.worldbank.org", request.full_url)
            self.assertEqual(timeout, 60)
            return io.BytesIO(json.dumps(payload).encode())

        bundle = load_world_bank_wdi(
            ("GRC",),
            ("NY.GDP.MKTP.KD.ZG",),
            start_year=2024,
            end_year=2025,
            opener=opener,
        )
        self.assertEqual(bundle.frame["year"].tolist(), [2024, 2025])
        self.assertEqual(bundle.frame["indicator_code"].nunique(), 1)
        self.assertIn("2026-07-13", bundle.limitations)
        self.assertEqual(bundle.licence, "CC BY 4.0")

    def test_complaint_extract_excludes_narratives_by_default(self) -> None:
        frame = pd.DataFrame(
            {
                "Date received": ["2026-01-02", "2026-01-03"],
                "Product": ["Credit card", "Mortgage"],
                "Issue": ["Billing dispute", "Application delay"],
                "Company": ["Example A", "Example B"],
                "State": ["NY", "CA"],
                "Submitted via": ["Web", "Phone"],
                "Company response to consumer": ["Closed", "Closed"],
                "Timely response?": ["Yes", "Yes"],
                "Complaint ID": [1001, 1002],
                "Consumer complaint narrative": ["private-style text", "other text"],
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "complaints.csv"
            frame.to_csv(path, index=False)
            bundle = load_cfpb_complaint_extract(path)
        self.assertNotIn("Consumer complaint narrative", bundle.frame)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(bundle.frame["Date received"]))
        self.assertIn("not a statistical sample", bundle.limitations)


if __name__ == "__main__":
    unittest.main()
