from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from creditriskbook.data.behavioral import (
    inject_behavioral_defects,
    make_behavioral_credit_history,
)
from creditriskbook.data.cleaning import clean_monthly_performance, validate_contract_history
from creditriskbook.features.behavioral import build_behavioral_features, business_name_map


class BehavioralDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = make_behavioral_credit_history(n_customers=150, months=18, seed=91)
        cls.references = cls.dataset.applications[["customer_id", "reference_date"]]

    def test_generator_is_reproducible_and_relationally_coherent(self) -> None:
        second = make_behavioral_credit_history(n_customers=150, months=18, seed=91)
        self.assertEqual(self.dataset.source_sha256, second.source_sha256)
        self.assertEqual(len(self.dataset.source_sha256), 64)
        contract_customers = set(self.dataset.contracts["customer_id"])
        self.assertTrue(
            set(self.dataset.monthly_performance["customer_id"]).issubset(contract_customers)
        )
        self.assertTrue(
            (self.dataset.monthly_performance["snapshot_date"] <= pd.Timestamp("2025-12-31")).all()
        )
        self.assertTrue((self.dataset.monthly_performance["dpd"] >= 0).all())
        self.assertTrue((self.dataset.monthly_performance["balance"] >= 0).all())
        self.assertGreater(self.dataset.applications["default_12m"].mean(), 0.01)
        self.assertLess(self.dataset.applications["default_12m"].mean(), 0.70)

    def test_dirty_copy_is_quarantined_with_row_level_reasons(self) -> None:
        dirty = inject_behavioral_defects(self.dataset.monthly_performance, seed=92)
        result = clean_monthly_performance(dirty, self.references)
        rules = set(result.issues["rule"])
        self.assertIn("dpd_out_of_domain", rules)
        self.assertIn("negative_or_missing_payment_received", rules)
        self.assertIn("post_reference_snapshot", rules)
        self.assertIn("status_dpd_inconsistent", rules)
        self.assertIn("superseded_business_key", rules)
        self.assertGreater(len(result.quarantine), 0)
        self.assertFalse(
            result.clean["source_row_id"].isin(result.quarantine["source_row_id"]).any()
        )
        self.assertTrue((result.clean["dpd"] >= 0).all())

    def test_contract_ledger_has_no_structural_issues(self) -> None:
        issues = validate_contract_history(self.dataset.contracts, self.references)
        self.assertTrue(issues.empty)


class BehavioralFeatureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = make_behavioral_credit_history(n_customers=150, months=18, seed=101)
        self.references = self.dataset.applications[["customer_id", "reference_date"]]

    def test_feature_values_follow_definitions(self) -> None:
        features = build_behavioral_features(
            self.dataset.monthly_performance,
            self.dataset.contracts,
            self.references,
            enquiries=self.dataset.bureau_enquiries,
        )
        customer = features.iloc[0]
        customer_id = customer["customer_id"]
        reference = pd.Timestamp(customer["reference_date"])
        history = self.dataset.monthly_performance.loc[
            (self.dataset.monthly_performance["customer_id"] == customer_id)
            & (
                self.dataset.monthly_performance["snapshot_date"]
                > reference - pd.DateOffset(months=6)
            )
            & (self.dataset.monthly_performance["snapshot_date"] <= reference)
        ]
        monthly = history.groupby("snapshot_date")["dpd"].max()
        expected_last = monthly.loc[monthly.index.max()]
        self.assertEqual(customer["last_dpd"], expected_last)
        self.assertEqual(customer["max_dpd_6m"], monthly.max())
        self.assertEqual(customer["count_dpd30_6m"], int((monthly >= 30).sum()))
        contracts = self.dataset.contracts.loc[
            (self.dataset.contracts["customer_id"] == customer_id)
            & (self.dataset.contracts["open_date"] > reference - pd.DateOffset(months=6))
            & (self.dataset.contracts["open_date"] <= reference)
        ]
        self.assertEqual(customer["count_contracts_last_6m"], len(contracts))
        self.assertEqual(business_name_map["CountContractsLast6Months"], "count_contracts_last_6m")

    def test_point_in_time_cutoff_blocks_future_rows(self) -> None:
        baseline = build_behavioral_features(
            self.dataset.monthly_performance,
            self.dataset.contracts,
            self.references,
        )
        future = self.dataset.monthly_performance.iloc[[0]].copy()
        future["snapshot_date"] = pd.Timestamp("2027-01-31")
        future["dpd"] = 999
        with_future = pd.concat([self.dataset.monthly_performance, future], ignore_index=True)
        observed = build_behavioral_features(with_future, self.dataset.contracts, self.references)
        pd.testing.assert_frame_equal(baseline, observed)

    def test_ols_utilisation_slope_matches_closed_form(self) -> None:
        customer = self.references.iloc[[0]]
        customer_id = customer.iloc[0]["customer_id"]
        reference = pd.Timestamp(customer.iloc[0]["reference_date"])
        contract = self.dataset.contracts.loc[
            self.dataset.contracts["customer_id"] == customer_id
        ].iloc[[0]]
        dates = pd.date_range(reference - pd.offsets.MonthEnd(5), reference, freq="ME")
        simple = pd.DataFrame(
            {
                "customer_id": customer_id,
                "contract_id": contract.iloc[0]["contract_id"],
                "snapshot_date": dates,
                "credit_limit": 100.0,
                "balance": np.arange(10.0, 70.0, 10.0),
                "scheduled_payment": 10.0,
                "payment_received": 10.0,
                "dpd": 0,
            }
        )
        features = build_behavioral_features(simple, contract, customer)
        self.assertAlmostEqual(features.iloc[0]["utilisation_slope_6m"], 0.1, places=12)


if __name__ == "__main__":
    unittest.main()
