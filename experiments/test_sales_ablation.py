"""Regression checks for the validation boundary and train-only preprocessing."""

from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from experiments.evaluate import FEATURES, TEST_START, fit_reserves, partition_origins
from experiments.sales_ablation import CANCELLATION_FEATURES, boundary_check


class SalesAblationChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        daily = pd.read_csv(Path("data/processed/daily.csv"), index_col="date", parse_dates=["date"])
        cls.daily = daily.loc[daily.index < TEST_START].copy()

    def test_validation_discards_future_before_feature_construction(self):
        expected_train, expected_replay = partition_origins(self.daily, "validation")
        # Synthetic invalid future totals would fail feature construction if accessed.
        # No actual held-out values are used in this check.
        poison = pd.DataFrame(np.inf, index=pd.date_range(TEST_START, periods=31),
                              columns=self.daily.columns)
        poison.index.name = self.daily.index.name
        train, replay = partition_origins(pd.concat([self.daily, poison]), "validation")
        pd.testing.assert_frame_equal(train, expected_train, check_exact=True)
        pd.testing.assert_frame_equal(replay, expected_replay, check_exact=True)
        self.assertLess(replay.index[-1] + pd.Timedelta(days=6), TEST_START)

    def test_both_fits_scale_only_their_training_features(self):
        train, replay = partition_origins(self.daily, "validation")
        # Strongly shifted validation inputs make accidental preprocessing leakage visible.
        shifted = replay.copy()
        shifted[FEATURES] += 1e9
        for features in [FEATURES, CANCELLATION_FEATURES]:
            with self.subTest(features=features):
                original_method, _ = fit_reserves(train, replay, features)
                method, predictions = fit_reserves(train, shifted, features)
                scaler = method.steps[0][1]
                np.testing.assert_array_equal(scaler.feature_names_in_, features)
                self.assertEqual(int(scaler.n_samples_seen_), len(train))
                np.testing.assert_allclose(scaler.mean_, train[features].mean().to_numpy())
                np.testing.assert_allclose(scaler.scale_, train[features].std(ddof=0).to_numpy())
                np.testing.assert_array_equal(method.steps[1][1].coef_,
                                              original_method.steps[1][1].coef_)
                self.assertEqual(method.steps[1][1].intercept_,
                                 original_method.steps[1][1].intercept_)
                np.testing.assert_array_equal(predictions.training_q80,
                                              np.full(len(replay), train.actual_gbp.quantile(0.8)))

    def test_transactions_from_D_do_not_change_morning_D(self):
        result = boundary_check(self.daily)
        self.assertTrue(result["passed"])
        self.assertAlmostEqual(result["actual_week_delta_gbp"], 7000.0)


if __name__ == "__main__":
    unittest.main()
