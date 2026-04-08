"""Tests for Phase VI Batch 6.1: Metabase Executive Dashboards."""

from dashboards.metabase.executive_dashboards import (
    attribution_war_view,
    waste_report,
    roas_drilldown,
    summarize_dashboards,
)
import unittest
import json
import pandas as pd
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestBatch61Dashboards(unittest.TestCase):
    """Test Batch 6.1: Executive dashboards."""

    @classmethod
    def setUpClass(cls):
        """Load dashboard metrics fixture."""
        fixture_path = (
            Path(__file__).parent.parent / "fixtures" /
            "phase6" / "dashboard_metrics.json"
        )
        with open(fixture_path) as f:
            cls.fixture = json.load(f)

    def test_attribution_war_view(self):
        """Test attribution war view comparison (last-touch vs Markov)."""
        data = pd.DataFrame(self.fixture["channels_with_metrics"])
        war = attribution_war_view(data)

        self.assertEqual(len(war), 4, "Should compare 4 channels")
        # Search should have largest loss (Markov < Last-Touch)
        search_result = next((w for w in war if w.channel == "search"), None)
        self.assertIsNotNone(search_result)
        self.assertEqual(search_result.direction, "loss")
        self.assertGreater(search_result.variance_pct, 5)

    def test_waste_report(self):
        """Test waste report identification."""
        data = pd.DataFrame(self.fixture["channels_with_metrics"])
        waste = waste_report(data, self.fixture["monthly_budget_eur"])

        self.assertGreater(len(waste), 0, "Should identify waste channels")
        # Check that first entry has high waste score
        self.assertGreater(waste[0].waste_score, 0.05)

    def test_roas_drilldown(self):
        """Test ROAS drilldown by channel, campaign, segment."""
        # Create sample conversion and spend data
        conversion_data = pd.DataFrame([
            {
                "channel": "search",
                "campaign": "q2_sale",
                "segment": "high_value",
                "attributed_revenue_eur": 8000,
                "conversions": 200,
                "sessions": 2500,
            },
            {
                "channel": "display",
                "campaign": "awareness",
                "segment": "new_user",
                "attributed_revenue_eur": 6000,
                "conversions": 120,
                "sessions": 3000,
            },
        ])
        spend_data = pd.DataFrame([
            {"channel": "search", "campaign": "q2_sale",
                "segment": "high_value", "spend_eur": 2500},
            {"channel": "display", "campaign": "awareness",
                "segment": "new_user", "spend_eur": 3000},
        ])

        roas = roas_drilldown(conversion_data, spend_data)
        self.assertEqual(len(roas), 2)
        # Search should have higher ROAS
        search_roas = roas[0]
        self.assertEqual(search_roas.channel, "search")
        self.assertGreater(search_roas.roas, 3.0)

    def test_summarize_dashboards(self):
        """Test dashboard summary generation."""
        data = pd.DataFrame(self.fixture["channels_with_metrics"])
        conversion_data = pd.DataFrame([
            {
                "channel": "search",
                "campaign": "q2",
                "segment": "high_value",
                "attributed_revenue_eur": 10000,
                "conversions": 200,
                "sessions": 2500,
            }
        ])
        spend_data = pd.DataFrame([
            {"channel": "search", "campaign": "q2",
                "segment": "high_value", "spend_eur": 3000}
        ])

        summary = summarize_dashboards(data, data, conversion_data, spend_data)

        self.assertIn("attribution_war", summary)
        self.assertIn("waste_report", summary)
        self.assertIn("roas_drilldown", summary)
        self.assertIn("key_insights", summary)

        insights = summary["key_insights"]
        self.assertEqual(insights["total_channels"], 4)
        self.assertGreater(insights["average_roas"], 0)


if __name__ == "__main__":
    unittest.main()
