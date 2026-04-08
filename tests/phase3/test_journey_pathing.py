from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline.journey_pathing import (
    build_conversion_attribution,
    build_journeys,
    build_touchpoints,
    deduplicate_touchpoints,
    summarize_journey_build,
)


class TestJourneyPathing(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        events = json.loads(Path(
            "tests/fixtures/phase3/journeys/journey_events.json").read_text(encoding="utf-8"))
        cls.events_df = pd.DataFrame(events)
        cls.touchpoints_df = build_touchpoints(cls.events_df)
        cls.journeys_df = build_journeys(cls.events_df)
        cls.conversions_df = build_conversion_attribution(cls.events_df)

    def test_event_ordering_and_dedup_window(self) -> None:
        deduped = deduplicate_touchpoints(self.events_df)
        u1_touchpoints = deduped[(
            deduped["user_pseudo_id"] == "u-journey-1") & (~deduped["is_conversion"])]
        self.assertEqual(u1_touchpoints.shape[0], 3)
        self.assertNotIn("j-1002", set(u1_touchpoints["event_id"]))

    def test_journey_paths_are_built(self) -> None:
        journey = self.journeys_df[self.journeys_df["user_pseudo_id"]
                                   == "u-journey-1"].iloc[0]
        self.assertEqual(journey["journey_path"],
                         "cmp-001 > cmp-002 > cmp-002")
        self.assertEqual(journey["conversion_count"], 1)

    def test_lookback_and_conversion_boundary(self) -> None:
        conv_1 = self.conversions_df[self.conversions_df["conversion_event_id"]
                                     == "j-1004"].iloc[0]
        conv_2 = self.conversions_df[self.conversions_df["conversion_event_id"]
                                     == "j-2002"].iloc[0]
        self.assertEqual(conv_1["lookback_touchpoints"], 2)
        self.assertEqual(conv_2["lookback_touchpoints"], 0)
        self.assertEqual(conv_1["attribution_path"], "cmp-001 > cmp-002")
        self.assertEqual(conv_2["attribution_path"], "")

    def test_summary(self) -> None:
        summary = summarize_journey_build(
            self.touchpoints_df, self.journeys_df, self.conversions_df)
        self.assertEqual(summary["touchpoints_rows"], 5)
        self.assertEqual(summary["journey_rows"], 5)
        self.assertEqual(summary["conversion_rows"], 2)
        self.assertEqual(summary["unique_journeys"], 5)


if __name__ == "__main__":
    unittest.main()
