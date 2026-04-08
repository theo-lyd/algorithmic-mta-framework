from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline.attribution_finance_bridge import (
    allocate_net_revenue,
    reconciliation_summary,
    recompute_channel_roas,
    summarize_finance_bridge,
    variance_against_current,
)
from ingestion.pipeline.heuristic_attribution import (
    last_touch_attribution,
    linear_attribution,
)


class TestFinanceBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events_df = pd.DataFrame(
            json.loads(Path(
                "tests/fixtures/phase4/attribution_events.json").read_text(encoding="utf-8"))
        )
        cls.spend_df = pd.DataFrame(
            json.loads(
                Path("tests/fixtures/phase4/channel_spend.json").read_text(encoding="utf-8"))
        )

    def test_finance_bridge_reconciliation(self) -> None:
        last_touch = last_touch_attribution(self.events_df)
        last_touch["method"] = "last_touch"
        linear = linear_attribution(self.events_df)
        linear["method"] = "linear"
        attribution = pd.concat([last_touch, linear], ignore_index=True)

        conversions = self.events_df[self.events_df["is_conversion"]][[
            "conversion_id", "net_revenue_eur"]].copy()
        allocated = allocate_net_revenue(conversions, attribution)
        reconciliation = reconciliation_summary(conversions, allocated)
        self.assertTrue(reconciliation["reconciled_exactly"].all())

        roas = recompute_channel_roas(allocated, self.spend_df)
        variance = variance_against_current(roas, current_method="last_touch")
        baseline_rows = variance[variance["method"] == "last_touch"]
        self.assertTrue((baseline_rows["roas_delta_abs"].abs() < 1e-8).all())

        summary = summarize_finance_bridge(roas, reconciliation)
        self.assertEqual(summary["methods"], 2)
        self.assertGreaterEqual(summary["channels"], 4)


if __name__ == "__main__":
    unittest.main()
