"""Tests for Phase VI Batch 6.2: Streamlit What-If Simulator."""

from dashboards.streamlit.whatif_simulator import (
    validate_reallocation_constraints,
    predict_revenue_impact,
    compare_scenarios,
    summarize_simulator,
)
import unittest
import json
import pandas as pd
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestBatch62Simulator(unittest.TestCase):
    """Test Batch 6.2: What-if simulator."""

    @classmethod
    def setUpClass(cls):
        """Load simulator data fixture."""
        fixture_path = (
            Path(__file__).parent.parent / "fixtures" /
            "phase6" / "simulator_data.json"
        )
        with open(fixture_path) as f:
            cls.fixture = json.load(f)

    def test_validate_reallocation_constraints(self):
        """Test budget reallocation validation."""
        current = self.fixture["current_allocation"]
        proposed = self.fixture["proposed_allocation"]
        total_budget = sum(proposed.values())

        is_valid, violations = validate_reallocation_constraints(
            current, proposed, total_budget)

        self.assertTrue(is_valid, f"Valid reallocation failed: {violations}")

    def test_validate_constraints_over_budget(self):
        """Test constraint: total spend exceeds budget."""
        current = {"search": 20000, "display": 30000}
        proposed = {"search": 30000, "display": 40000}  # Total 70k

        is_valid, violations = validate_reallocation_constraints(
            current, proposed, total_budget_eur=50000
        )

        self.assertFalse(is_valid)
        self.assertGreater(len(violations), 0)

    def test_validate_constraints_min_spend(self):
        """Test constraint: channel below minimum."""
        current = {"search": 20000, "display": 30000}
        proposed = {"search": 200, "display": 49500}  # Search below min

        is_valid, violations = validate_reallocation_constraints(
            current, proposed, total_budget_eur=50000, min_channel_spend_eur=500
        )

        self.assertFalse(is_valid)
        self.assertIn("below minimum", violations[0])

    def test_predict_revenue_impact(self):
        """Test revenue impact prediction."""
        proposed = self.fixture["proposed_allocation"]
        roas = self.fixture["base_roas_by_channel"]
        propensity_df = pd.DataFrame(self.fixture["propensity_model_output"])

        impact = predict_revenue_impact(proposed, roas, propensity_df)

        self.assertGreater(impact.base_revenue_eur, 0)
        self.assertGreater(impact.predicted_revenue_eur, 0)
        self.assertGreater(impact.confidence_upper_95_pct,
                           impact.confidence_lower_95_pct)

    def test_confidence_intervals(self):
        """Test that confidence intervals are ±15% around estimate."""
        proposed = self.fixture["proposed_allocation"]
        roas = self.fixture["base_roas_by_channel"]
        propensity_df = pd.DataFrame(self.fixture["propensity_model_output"])

        impact = predict_revenue_impact(proposed, roas, propensity_df)

        margin_pct = (
            (impact.confidence_upper_95_pct - impact.predicted_revenue_eur)
            / impact.predicted_revenue_eur
            * 100
        )
        self.assertAlmostEqual(margin_pct, 15.0, delta=1.0)

    def test_scenario_comparison(self):
        """Test scenario comparison export."""
        proposed = self.fixture["proposed_allocation"]
        roas = self.fixture["base_roas_by_channel"]
        propensity_df = pd.DataFrame(self.fixture["propensity_model_output"])

        impact = predict_revenue_impact(proposed, roas, propensity_df)
        comparison = compare_scenarios([impact])

        self.assertEqual(len(comparison), 1)
        self.assertIn("scenario_name", comparison.columns)
        self.assertIn("predicted_lift_pct", comparison.columns)

    def test_summarize_simulator(self):
        """Test simulator summary generation."""
        current = self.fixture["current_allocation"]
        proposed = self.fixture["proposed_allocation"]
        roas = self.fixture["base_roas_by_channel"]
        propensity_df = pd.DataFrame(self.fixture["propensity_model_output"])

        summary = summarize_simulator(current, proposed, roas, propensity_df)

        self.assertIn("validation", summary)
        self.assertIn("revenue_impact", summary)
        self.assertIn("export", summary)

        self.assertTrue(summary["validation"]["is_valid"])
        self.assertGreater(summary["revenue_impact"]["base_revenue_eur"], 0)


if __name__ == "__main__":
    unittest.main()
