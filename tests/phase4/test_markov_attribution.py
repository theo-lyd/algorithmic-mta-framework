from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline.markov_attribution import (
    ABSORBING_CONVERSION,
    ABSORBING_NULL,
    START_STATE,
    build_transition_matrix,
    compute_removal_effects,
    extract_paths,
    normalize_markov_attribution,
    summarize_markov_stability,
)


class TestMarkovAttribution(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events_df = pd.DataFrame(
            json.loads(Path(
                "tests/fixtures/phase4/attribution_events.json").read_text(encoding="utf-8"))
        )
        cls.paths_df = extract_paths(cls.events_df)

    def test_transition_matrix(self) -> None:
        matrix = build_transition_matrix(self.paths_df)
        self.assertIn(START_STATE, matrix.index)
        self.assertIn(ABSORBING_CONVERSION, matrix.index)
        self.assertIn(ABSORBING_NULL, matrix.index)
        self.assertAlmostEqual(
            float(matrix.loc[START_STATE].sum()), 1.0, places=6)
        self.assertAlmostEqual(
            float(matrix.loc[ABSORBING_CONVERSION, ABSORBING_CONVERSION]), 1.0, places=6)
        self.assertAlmostEqual(
            float(matrix.loc[ABSORBING_NULL, ABSORBING_NULL]), 1.0, places=6)

    def test_removal_effects_and_normalization(self) -> None:
        effects = compute_removal_effects(self.paths_df)
        self.assertTrue((effects["removal_effect"] >= 0).all())
        self.assertGreater(float(effects["removal_effect"].sum()), 0.0)

        conversions = int(
            self.events_df[self.events_df["is_conversion"]].shape[0])
        markov = normalize_markov_attribution(
            effects, total_conversions=conversions)
        self.assertAlmostEqual(
            float(markov["attribution_share"].sum()), 1.0, places=6)
        self.assertAlmostEqual(
            float(markov["attributed_conversions"].sum()), float(conversions), places=6)

        summary = summarize_markov_stability(markov)
        self.assertGreaterEqual(summary["channels"], 1)
        self.assertAlmostEqual(summary["share_sum"], 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
