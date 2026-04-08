from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline.performance_cost import (
    cost_dashboard,
    incremental_strategy_optimization,
    materialization_tuning_recommendations,
    profile_queries,
    threshold_alerts,
)


class TestPerformanceCost(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        payload = json.loads(Path(
            "tests/fixtures/phase5/performance_cost_data.json").read_text(encoding="utf-8"))
        cls.query_runs_df = pd.DataFrame(payload["query_runs"])
        cls.partition_df = pd.DataFrame(payload["partition_stats"])
        cls.cost_df = pd.DataFrame(payload["cost_rows"])
        cls.monthly_budget = float(payload["monthly_budget_eur"])

    def test_profile_and_cost_controls(self) -> None:
        profile_df = profile_queries(self.query_runs_df)
        rec_df = materialization_tuning_recommendations(profile_df)
        self.assertIn("incremental_partitioned", set(rec_df["recommendation"]))

        incremental_df = incremental_strategy_optimization(self.partition_df)
        self.assertIn("merge_on_partition", set(
            incremental_df["recommended_strategy"]))

        dashboard = cost_dashboard(self.cost_df, self.monthly_budget)
        alerts = threshold_alerts(dashboard, budget_threshold=0.75)
        self.assertTrue(alerts["alert_triggered"])


if __name__ == "__main__":
    unittest.main()
