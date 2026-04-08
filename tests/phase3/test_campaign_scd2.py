from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline.campaign_scd2 import (
    build_campaign_scd2,
    point_in_time_join,
    summarize_scd2_changes,
)


class TestCampaignSCD2(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        changes = json.loads(
            Path("tests/fixtures/phase3/campaign_changes.json").read_text(encoding="utf-8"))
        events = json.loads(
            Path("tests/fixtures/phase3/campaign_events.json").read_text(encoding="utf-8"))
        cls.changes_df = pd.DataFrame(changes)
        cls.events_df = pd.DataFrame(events)
        cls.scd2_df = build_campaign_scd2(cls.changes_df).campaign_scd2

    def test_scd2_windows_built(self) -> None:
        self.assertEqual(self.scd2_df.shape[0], 5)
        current_rows = self.scd2_df[self.scd2_df["is_current"]]
        self.assertEqual(current_rows.shape[0], 2)

    def test_historical_owner_budget_taxonomy_changes(self) -> None:
        cmp1 = self.scd2_df[self.scd2_df["campaign_id"]
                            == "cmp-001"].sort_values("valid_from")
        self.assertEqual(cmp1.iloc[0]["owner_name"], "team_search")
        self.assertEqual(cmp1.iloc[1]["owner_name"], "team_growth")
        self.assertEqual(float(cmp1.iloc[0]["budget_eur"]), 100000.0)
        self.assertEqual(float(cmp1.iloc[2]["budget_eur"]), 150000.0)
        self.assertEqual(cmp1.iloc[0]["taxonomy_l2"], "search_brand")
        self.assertEqual(cmp1.iloc[1]["taxonomy_l2"], "search_non_brand")

    def test_point_in_time_join_integrity(self) -> None:
        joined = point_in_time_join(self.events_df, self.scd2_df)
        self.assertEqual(joined.shape[0], 5)

        row_evt_3001 = joined[joined["event_id"] == "evt-3001"].iloc[0]
        row_evt_3002 = joined[joined["event_id"] == "evt-3002"].iloc[0]
        row_evt_3003 = joined[joined["event_id"] == "evt-3003"].iloc[0]

        self.assertEqual(row_evt_3001["owner_name"], "team_search")
        self.assertEqual(row_evt_3002["owner_name"], "team_growth")
        self.assertEqual(float(row_evt_3003["budget_eur"]), 150000.0)

    def test_scd2_summary(self) -> None:
        summary = summarize_scd2_changes(self.scd2_df)
        self.assertEqual(summary["campaign_rows"], 5)
        self.assertEqual(summary["campaign_ids"], 2)
        self.assertEqual(summary["current_rows"], 2)
        self.assertEqual(summary["historical_rows"], 3)


if __name__ == "__main__":
    unittest.main()
