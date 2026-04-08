from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline.behavioral_segmentation import (
    engineer_rfm_features,
    label_segments_with_playbooks,
    train_kmeans_segments,
)


class TestBehavioralSegmentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events_df = pd.DataFrame(
            json.loads(
                Path("tests/fixtures/phase4/customer_events.json").read_text(encoding="utf-8"))
        )

    def test_segmentation_pipeline(self) -> None:
        features = engineer_rfm_features(
            self.events_df, reference_ts="2026-03-08T00:00:00Z")
        self.assertGreaterEqual(features.shape[0], 8)

        result = train_kmeans_segments(features, cluster_options=(2, 3))
        self.assertIn(result.selected_k, (2, 3))
        self.assertGreaterEqual(result.silhouette, -1.0)
        self.assertLessEqual(result.silhouette, 1.0)
        self.assertGreaterEqual(result.stability, 0.0)
        self.assertLessEqual(result.stability, 1.0)

        labeled = label_segments_with_playbooks(result.labeled_features)
        self.assertTrue(labeled["segment_label"].notna().all())
        self.assertTrue(labeled["playbook"].notna().all())


if __name__ == "__main__":
    unittest.main()
