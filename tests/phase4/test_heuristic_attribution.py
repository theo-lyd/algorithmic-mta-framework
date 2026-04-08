from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline.heuristic_attribution import (
    build_benchmark_evaluation_set,
    first_touch_attribution,
    last_touch_attribution,
    linear_attribution,
    time_decay_attribution,
)


class TestHeuristicAttribution(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events_df = pd.DataFrame(
            json.loads(Path(
                "tests/fixtures/phase4/attribution_events.json").read_text(encoding="utf-8"))
        )
        cls.reference_df = pd.DataFrame(
            json.loads(Path(
                "tests/fixtures/phase4/benchmark_reference.json").read_text(encoding="utf-8"))
        )

    def test_first_and_last_touch(self) -> None:
        first_df = first_touch_attribution(self.events_df)
        last_df = last_touch_attribution(self.events_df)

        c1_first = first_df[first_df["conversion_id"] == "c-1"].iloc[0]
        c1_last = last_df[last_df["conversion_id"] == "c-1"].iloc[0]
        self.assertEqual(c1_first["channel"], "search")
        self.assertEqual(c1_last["channel"], "social")

        self.assertAlmostEqual(
            float(first_df.groupby("conversion_id")[
                  "attribution_weight"].sum().min()),
            1.0,
            places=6,
        )
        self.assertAlmostEqual(
            float(last_df.groupby("conversion_id")[
                  "attribution_weight"].sum().min()),
            1.0,
            places=6,
        )

    def test_linear_and_time_decay(self) -> None:
        linear_df = linear_attribution(self.events_df)
        decay_df = time_decay_attribution(self.events_df)

        c4_linear = linear_df[linear_df["conversion_id"]
                              == "c-4"].sort_values("channel")
        self.assertEqual(c4_linear.shape[0], 2)
        self.assertAlmostEqual(
            float(c4_linear["attribution_weight"].sum()), 1.0, places=6)

        c1_decay = decay_df[decay_df["conversion_id"]
                            == "c-1"].set_index("channel")
        self.assertGreater(float(c1_decay.loc["social", "attribution_weight"]), float(
            c1_decay.loc["search", "attribution_weight"]))

    def test_benchmark_evaluation_set(self) -> None:
        method_outputs = {
            "first_touch": first_touch_attribution(self.events_df),
            "last_touch": last_touch_attribution(self.events_df),
            "linear": linear_attribution(self.events_df),
            "time_decay": time_decay_attribution(self.events_df),
        }
        benchmark = build_benchmark_evaluation_set(
            self.reference_df, method_outputs)
        self.assertEqual(benchmark.shape[0], 4)
        self.assertTrue((benchmark["mae"] >= 0).all())
        self.assertTrue((benchmark["rmse"] >= 0).all())


if __name__ == "__main__":
    unittest.main()
