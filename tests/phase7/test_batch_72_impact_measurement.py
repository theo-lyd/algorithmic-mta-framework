"""Tests for Phase VII Batch 7.2: Impact measurement."""

import json
from pathlib import Path
import unittest

import pandas as pd

from impact.impact_measurement import (
    design_pre_post_reallocation_experiment,
    measure_roas_uplift_and_waste_reduction,
    quantify_confidence_and_sensitivity,
    summarize_impact_measurement,
)


class TestBatch72ImpactMeasurement(unittest.TestCase):
    """Validate experiment design, impact deltas, and confidence statistics."""

    @classmethod
    def setUpClass(cls):
        fixture_path = (
            Path(__file__).parent.parent / "fixtures" /
            "phase7" / "impact_measurement.json"
        )
        with open(fixture_path, "r", encoding="utf-8") as handle:
            cls.fixture = json.load(handle)

        cls.pre_period = pd.DataFrame(cls.fixture["pre_period"])
        cls.post_period = pd.DataFrame(cls.fixture["post_period"])

    def test_experiment_design_is_valid(self):
        design = design_pre_post_reallocation_experiment(
            self.pre_period, self.post_period)
        self.assertTrue(design["design_valid"])
        self.assertEqual(design["pre_days"], 30)
        self.assertEqual(design["post_days"], 30)

    def test_experiment_design_requires_min_observations(self):
        with self.assertRaises(ValueError):
            design_pre_post_reallocation_experiment(
                self.pre_period.head(10),
                self.post_period.head(10),
                min_observations=28,
            )

    def test_measure_roas_uplift_and_waste_reduction(self):
        delta = measure_roas_uplift_and_waste_reduction(
            self.pre_period, self.post_period)
        self.assertGreater(delta.roas_uplift_pct, 0)
        self.assertGreater(delta.waste_reduction_pct, 0)
        self.assertGreater(delta.post_roas, delta.pre_roas)

    def test_confidence_statistics(self):
        confidence = quantify_confidence_and_sensitivity(
            self.pre_period,
            self.post_period,
            self.fixture["assumptions"],
        )
        self.assertIn("daily_roas_delta_ci_95", confidence)
        self.assertLess(confidence["p_value_two_tailed"], 0.05)
        self.assertTrue(confidence["statistically_significant_at_95"])

    def test_sensitivity_bounds(self):
        confidence = quantify_confidence_and_sensitivity(
            self.pre_period,
            self.post_period,
            self.fixture["assumptions"],
        )
        bounds = confidence["sensitivity_uplift_range_pct"]
        self.assertEqual(len(bounds), 2)
        self.assertLess(bounds[0], bounds[1])

    def test_summarize_impact_measurement(self):
        summary = summarize_impact_measurement(
            self.pre_period,
            self.post_period,
            self.fixture["assumptions"],
        )
        self.assertIn("experiment_design", summary)
        self.assertIn("impact_delta", summary)
        self.assertIn("confidence", summary)
        self.assertTrue(summary["business_value_quantified"])


if __name__ == "__main__":
    unittest.main()
