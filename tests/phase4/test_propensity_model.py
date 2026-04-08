from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline.propensity_model import (
    build_feature_store,
    meets_lift_threshold,
    train_calibrated_logistic,
)


class TestPropensityModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events_df = pd.DataFrame(
            json.loads(
                Path("tests/fixtures/phase4/customer_events.json").read_text(encoding="utf-8"))
        )

    def test_feature_store_and_training(self) -> None:
        features = build_feature_store(
            self.events_df, snapshot_ts="2026-03-01T00:00:00Z")
        self.assertIn("label_next_7d", features.columns)
        self.assertGreaterEqual(int(features["label_next_7d"].sum()), 1)
        self.assertGreaterEqual(features.shape[0], 8)

        result = train_calibrated_logistic(features)
        self.assertIn("auc", result.metrics)
        self.assertIn("average_precision", result.metrics)
        self.assertIn("top_decile_lift", result.metrics)
        self.assertIn("calibration_drift", result.metrics)

        self.assertGreaterEqual(result.metrics["auc"], 0.0)
        self.assertLessEqual(result.metrics["auc"], 1.0)
        self.assertGreaterEqual(result.metrics["top_decile_lift"], 0.6)
        self.assertTrue(meets_lift_threshold(result.metrics, threshold=0.6))


if __name__ == "__main__":
    unittest.main()
