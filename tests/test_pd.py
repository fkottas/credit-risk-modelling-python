from __future__ import annotations

import unittest

from creditriskbook.data.datasets import load_dataset
from creditriskbook.models import evaluate_pd, fit_pd_model, score_pd, split_dataset


class PDModelTests(unittest.TestCase):
    def test_out_of_time_baseline_runs_and_returns_probabilities(self) -> None:
        bundle = load_dataset("synthetic_retail", n_rows=3_000, seed=19)
        train, test = split_dataset(bundle, bundle.frame, seed=19)
        self.assertLessEqual(train[bundle.date_column].max(), test[bundle.date_column].min())
        model = fit_pd_model(bundle, train)
        prediction = score_pd(model, test)
        self.assertTrue(((prediction >= 0) & (prediction <= 1)).all())
        metrics = evaluate_pd(test[bundle.target], prediction)
        self.assertGreater(metrics["roc_auc"], 0.62)
        self.assertGreater(metrics["ks"], 0.10)
        self.assertLess(metrics["brier_score"], 0.25)


if __name__ == "__main__":
    unittest.main()
