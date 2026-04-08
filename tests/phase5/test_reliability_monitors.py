from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline.reliability_monitors import (
    classify_severity,
    distribution_monitor,
    freshness_monitor,
    pixel_downtime_detection,
    route_incident,
    schema_monitor,
    summarize_reliability,
    volume_monitor,
)


class TestReliabilityMonitors(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        payload = json.loads(Path(
            "tests/fixtures/phase5/reliability_metrics.json").read_text(encoding="utf-8"))
        cls.fresh_df = pd.DataFrame(payload["freshness"])
        cls.volume_df = pd.DataFrame(payload["volume"])
        cls.dist_base = payload["distribution_baseline"]
        cls.dist_current = payload["distribution_current"]
        cls.pixel = payload["pixel"]
        cls.expected_cols = json.loads(
            Path("tests/fixtures/phase5/schema_expected.json").read_text(encoding="utf-8"))
        cls.actual_cols = json.loads(
            Path("tests/fixtures/phase5/schema_actual.json").read_text(encoding="utf-8"))

    def test_reliability_checks_and_routing(self) -> None:
        results = [
            freshness_monitor(self.fresh_df, max_lag_minutes=60),
            volume_monitor(self.volume_df, drop_threshold_ratio=0.7),
            schema_monitor(self.actual_cols, self.expected_cols),
            distribution_monitor(
                self.dist_base, self.dist_current, max_l1_distance=0.2),
            pixel_downtime_detection(
                self.pixel["spend_eur"], self.pixel["page_views"]),
        ]

        self.assertFalse(results[-1].success)
        severity = classify_severity(results)
        self.assertEqual(severity, "sev-1")

        routing = route_incident(severity)
        self.assertEqual(routing["owner"], "oncall-data-sre")

        summary = summarize_reliability(results)
        self.assertEqual(summary["checks_total"], 5)
        self.assertEqual(summary["severity"], "sev-1")


if __name__ == "__main__":
    unittest.main()
