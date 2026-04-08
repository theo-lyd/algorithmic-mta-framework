from __future__ import annotations

import unittest
from pathlib import Path

from ingestion.pipeline.silver_harmonization import (
    build_silver_tables,
    load_jsonl,
)


class TestSilverHarmonization(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture = Path(
            "tests/fixtures/phase2/silver/raw_events_for_silver.jsonl")
        cls.rows = load_jsonl(fixture)
        cls.tables = build_silver_tables(cls.rows)

    def test_flatten_event_params(self) -> None:
        params_df = self.tables.event_params
        self.assertGreaterEqual(params_df.shape[0], 8)
        self.assertTrue({"event_id", "param_key", "param_value"}.issubset(
            set(params_df.columns)))

    def test_flatten_item_arrays(self) -> None:
        items_df = self.tables.event_items
        self.assertEqual(items_df.shape[0], 3)
        self.assertTrue({"event_id", "item_id", "quantity",
                        "price"}.issubset(set(items_df.columns)))

    def test_sessionization_30_minute_rule(self) -> None:
        sessions_df = self.tables.sessions
        u100_sessions = sessions_df[sessions_df["user_pseudo_id"] == "u-100"]
        self.assertEqual(u100_sessions.shape[0], 2)

        events_df = self.tables.events
        u100_events = events_df[events_df["user_pseudo_id"]
                                == "u-100"].sort_values("event_timestamp")
        first_two_session_ids = u100_events.iloc[0:2]["session_id"].unique()
        third_session_id = u100_events.iloc[2]["session_id"]
        self.assertEqual(len(first_two_session_ids), 1)
        self.assertNotEqual(first_two_session_ids[0], third_session_id)

    def test_canonical_dimensions(self) -> None:
        self.assertGreaterEqual(self.tables.dim_channel.shape[0], 2)
        self.assertGreaterEqual(self.tables.dim_campaign.shape[0], 2)
        self.assertGreaterEqual(self.tables.dim_device.shape[0], 2)
        self.assertGreaterEqual(self.tables.dim_geography.shape[0], 2)


if __name__ == "__main__":
    unittest.main()
