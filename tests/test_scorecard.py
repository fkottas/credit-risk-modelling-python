from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from creditriskbook.data.datasets import load_dataset
from creditriskbook.models import evaluate_pd, split_dataset
from creditriskbook.scorecard import (
    BinningProcess,
    LogisticScorecard,
    ModelScoreMapper,
    ScoreScale,
    binned_population_stability,
    coefficient_inference,
    export_characteristic_presentation,
    export_characteristic_report,
    manual_categorical_spec,
    manual_numeric_spec,
    population_stability_index,
    scorecard_policy_flags,
    variance_inflation_factors,
)


class ScorecardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = load_dataset("synthetic_retail", n_rows=4_000, seed=87)
        cls.features = [
            "income",
            "employment_years",
            "debt_to_income",
            "utilisation",
            "enquiries_6m",
            "loan_amount",
            "product",
            "home_ownership",
        ]
        cls.train, cls.test = split_dataset(cls.bundle, cls.bundle.frame, seed=87)

    def test_manual_and_automatic_bins_woe_points_and_reasons(self) -> None:
        manual = {
            "enquiries_6m": manual_numeric_spec("enquiries_6m", [0, 1, 3, 6]),
            "product": manual_categorical_spec(
                "product",
                [["personal_loan"], ["credit_card"], ["bnpl"]],
            ),
        }
        scorecard = LogisticScorecard(
            binning=BinningProcess(
                numeric_method="monotonic",
                max_bins=6,
                prebins=15,
                min_bin_fraction=0.04,
                min_events=4,
                manual_specs=manual,
            ),
            l2=1e-3,
        ).fit(self.train[self.features], self.train[self.bundle.target])

        predicted = scorecard.predict_proba(self.test[self.features])[:, 1]
        scores = scorecard.score(self.test[self.features])
        metrics = evaluate_pd(self.test[self.bundle.target], predicted)
        self.assertGreater(metrics["roc_auc"], 0.62)
        self.assertTrue(scorecard.model_.converged_)
        self.assertTrue(((predicted > 0) & (predicted < 1)).all())
        self.assertTrue(((scores >= 300) & (scores <= 900)).all())
        rank_correlation = pd.Series(predicted).corr(pd.Series(scores).rank(), method="spearman")
        self.assertLess(rank_correlation, -0.99)

        components = scorecard.score_components(self.test[self.features].iloc[:20])
        np.testing.assert_array_equal(
            components["score"], scorecard.score(self.test[self.features].iloc[:20])
        )
        self.assertEqual(set(scorecard.encoder_.information_values.index), set(self.features))
        self.assertIn("__MISSING__", scorecard.binning.specs_["income"].all_labels)
        self.assertEqual(scorecard.binning.specs_["enquiries_6m"].method, "manual")

        points = scorecard.points_table()
        self.assertEqual(set(points["feature"]), set(self.features))
        reasons = scorecard.reason_codes(self.test[self.features].iloc[:10], top_n=3)
        self.assertEqual(reasons.shape, (10, 6))
        self.assertTrue(reasons["reason_1"].isin(self.features).all())

        with tempfile.TemporaryDirectory() as directory:
            artefacts = export_characteristic_report(scorecard, directory)
            self.assertTrue(
                all(path.exists() and path.stat().st_size > 0 for path in artefacts.values())
            )
            self.assertIn("Characteristic analysis", Path(artefacts["html"]).read_text())
            presentation = export_characteristic_presentation(
                scorecard, Path(directory) / "characteristic_analysis.pptx"
            )
            self.assertTrue(presentation.exists() and presentation.stat().st_size > 10_000)

        inference = coefficient_inference(scorecard)
        self.assertEqual(inference["term"].tolist(), ["intercept", *self.features])
        flags = scorecard_policy_flags(scorecard, minimum_bin_count=20)
        self.assertEqual(set(flags["feature"]), set(self.features))

        reference_bins = scorecard.binning.transform(self.train[self.features])
        current_bins = scorecard.binning.transform(self.test[self.features])
        detail, summary = binned_population_stability(reference_bins, current_bins)
        self.assertEqual(set(summary["feature"]), set(self.features))
        self.assertAlmostEqual(detail["psi_component"].sum(), summary["psi"].sum())

        vif = variance_inflation_factors(scorecard.encoder_.transform(reference_bins).astype(float))
        self.assertEqual(set(vif["feature"]), set(self.features))

    def test_score_scale_round_trip_and_pdo(self) -> None:
        scale = ScoreScale(base_score=600, pdo=50, base_odds_good_to_bad=20)
        base_pd = 1 / 21
        score = scale.probability_to_score(np.array([base_pd]))[0]
        doubled_good_odds_pd = 1 / 41
        stronger = scale.probability_to_score(np.array([doubled_good_odds_pd]))[0]
        self.assertEqual(score, 600)
        self.assertEqual(stronger - score, 50)
        recovered = scale.score_to_probability(np.array([score]))[0]
        self.assertAlmostEqual(recovered, base_pd, places=8)

    def test_model_agnostic_mapping_accepts_any_predict_proba_model(self) -> None:
        class ProbabilityModel:
            def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
                bad = 1 / (1 + np.exp(-(-2.0 + 3.0 * X["utilisation"].to_numpy())))
                return np.column_stack([1 - bad, bad])

        frame = self.test[["utilisation", "debt_to_income"]].iloc[:30]
        mapper = ModelScoreMapper(ProbabilityModel()).fit_reference(frame)
        scores = mapper.score(frame)
        reasons = mapper.reason_codes(frame, top_n=2)
        self.assertEqual(len(scores), len(frame))
        self.assertEqual(reasons.shape, (len(frame), 4))
        self.assertLess(np.corrcoef(frame["utilisation"], scores)[0, 1], -0.9)

    def test_population_stability_detects_a_shift(self) -> None:
        rng = np.random.default_rng(5)
        reference = rng.normal(600, 40, 5_000)
        stable = population_stability_index(reference, rng.normal(600, 40, 5_000))
        shifted = population_stability_index(reference, rng.normal(660, 40, 5_000))
        self.assertLess(stable, 0.02)
        self.assertGreater(shifted, 0.5)


if __name__ == "__main__":
    unittest.main()
