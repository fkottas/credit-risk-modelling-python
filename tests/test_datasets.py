import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from creditriskbook.data import available_case_datasets, load_case_dataset
from creditriskbook.data.datasets import (
    _bank_marketing_bundle,
    _statlog_german_bundle,
    available_datasets,
    load_dataset,
)


class DatasetTests(unittest.TestCase):
    def test_synthetic_is_reproducible_and_has_documented_contract(self) -> None:
        first = load_dataset("synthetic_retail", n_rows=500, seed=11)
        second = load_dataset("synthetic_retail", n_rows=500, seed=11)
        pd.testing.assert_frame_equal(first.frame, second.frame)
        self.assertEqual(first.source_sha256, second.source_sha256)
        self.assertEqual(set(first.frame[first.target].unique()), {0, 1})
        self.assertTrue(set(first.model_features).isdisjoint(first.protected_attributes))

    def test_kaggle_local_adapter_validates_schema_and_hashes_file(self) -> None:
        fixture = pd.DataFrame(
            {
                "person_age": [25, 42, 36, 51],
                "person_income": [30_000, 70_000, 52_000, 91_000],
                "person_home_ownership": ["RENT", "MORTGAGE", "OWN", "MORTGAGE"],
                "person_emp_length": [2.0, 10.0, 6.0, 20.0],
                "loan_intent": ["EDUCATION", "MEDICAL", "VENTURE", "PERSONAL"],
                "loan_grade": ["C", "A", "B", "A"],
                "loan_amnt": [8_000, 12_000, 10_000, 20_000],
                "loan_int_rate": [14.0, 7.0, 10.0, 6.5],
                "loan_status": [1, 0, 0, 0],
                "loan_percent_income": [0.27, 0.17, 0.19, 0.22],
                "cb_person_default_on_file": ["Y", "N", "N", "N"],
                "cb_person_cred_hist_length": [3, 15, 9, 25],
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credit_risk_dataset.csv"
            fixture.to_csv(path, index=False)
            bundle = load_dataset("kaggle_credit_risk", data_path=path)
        self.assertEqual(bundle.key, "kaggle_credit_risk")
        self.assertEqual(bundle.frame[bundle.target].tolist(), [1, 0, 0, 0])
        self.assertEqual(len(bundle.source_sha256), 64)
        self.assertNotIn("person_age", bundle.model_features)

    def test_available_dataset_keys_are_stable(self) -> None:
        self.assertEqual(
            available_datasets(),
            (
                "synthetic_retail",
                "uci_south_german",
                "uci_statlog_german",
                "uci_taiwan_credit_card",
                "uci_credit_approval",
                "uci_australian_credit_approval",
                "uci_polish_bankruptcy",
                "uci_taiwan_bankruptcy",
                "uci_bank_marketing",
                "kaggle_credit_risk",
            ),
        )

    def test_scope_limited_adapters_preserve_their_non_pd_meaning(self) -> None:
        german_rows = (
            b"A11 6 A34 A43 1000 A65 A75 4 A93 A101 4 A121 35 A143 A152 1 A173 1 A192 A201 1\n"
            b"A12 18 A32 A40 2500 A61 A73 2 A92 A101 2 A123 29 A143 A153 2 A172 1 A191 A201 2\n"
        )
        german_archive = io.BytesIO()
        with zipfile.ZipFile(german_archive, "w") as zipped:
            zipped.writestr("german.data", german_rows)

        marketing_csv = (
            b'"age";"job";"marital";"education";"default";"housing";"loan";'
            b'"contact";"month";"day_of_week";"duration";"campaign";"pdays";'
            b'"previous";"poutcome";"emp.var.rate";"cons.price.idx";"cons.conf.idx";'
            b'"euribor3m";"nr.employed";"y"\n'
            b'42;"admin.";"single";"university.degree";"no";"yes";"no";'
            b'"cellular";"may";"mon";120;1;999;0;"nonexistent";1.1;93.9;-36.4;4.8;5191;"yes"\n'
        )
        nested = io.BytesIO()
        with zipfile.ZipFile(nested, "w") as zipped:
            zipped.writestr("bank-additional/bank-additional-full.csv", marketing_csv)
        marketing_archive = io.BytesIO()
        with zipfile.ZipFile(marketing_archive, "w") as zipped:
            zipped.writestr("bank-additional.zip", nested.getvalue())

        with patch(
            "creditriskbook.data.datasets._download_checked",
            return_value=german_archive.getvalue(),
        ):
            german = _statlog_german_bundle(Path("unused"))
        with patch(
            "creditriskbook.data.datasets._download_checked",
            return_value=marketing_archive.getvalue(),
        ):
            marketing = _bank_marketing_bundle(Path("unused"))

        self.assertEqual(german.frame["default_12m"].tolist(), [0, 1])
        self.assertIn("coding-information errors", german.limitations)
        self.assertEqual(marketing.target, "subscribed")
        self.assertNotIn("duration", marketing.model_features)
        self.assertIn("not credit approval", marketing.limitations)

    def test_case_datasets_cover_ifrs9_irb_lgd_ead_and_counterparty(self) -> None:
        self.assertEqual(len(available_case_datasets()), 5)
        revolving = load_case_dataset("synthetic_revolving", n_rows=200, seed=5)
        recovery = load_case_dataset("synthetic_recovery", n_rows=100, seed=5)
        ifrs9 = load_case_dataset("synthetic_ifrs9_schedule", n_rows=50, seed=5)
        corporate = load_case_dataset("synthetic_corporate_irb", n_rows=100, seed=5)
        counterparty = load_case_dataset("synthetic_counterparty_profiles", n_rows=20, seed=5)
        self.assertEqual(len(revolving.frame), 200)
        self.assertGreater(len(recovery.frame), 100)
        self.assertEqual(len(ifrs9.frame), 50 * 36)
        self.assertEqual(len(corporate.frame), 100)
        self.assertGreater(len(counterparty.frame), 20)
        for case in (revolving, recovery, ifrs9, corporate, counterparty):
            self.assertEqual(len(case.source_sha256), 64)
            self.assertIn("synthetic", case.licence.lower())


if __name__ == "__main__":
    unittest.main()
