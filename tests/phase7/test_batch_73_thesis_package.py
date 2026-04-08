"""Tests for Phase VII Batch 7.3: Thesis package and defense narrative."""

import json
from pathlib import Path
import unittest

from thesis.narrative_package import (
    build_business_blueprint_summary,
    build_final_defense_deck,
    build_methods_reproducibility_appendix,
    summarize_thesis_package,
)


class TestBatch73ThesisPackage(unittest.TestCase):
    """Validate methods appendix, executive blueprint, and defense deck storyline."""

    @classmethod
    def setUpClass(cls):
        fixture_path = (
            Path(__file__).parent.parent / "fixtures" /
            "phase7" / "thesis_package.json"
        )
        with open(fixture_path, "r", encoding="utf-8") as handle:
            cls.fixture = json.load(handle)

    def test_methods_appendix_ready(self):
        appendix = build_methods_reproducibility_appendix(
            self.fixture["pipeline_components"],
            self.fixture["validation_commands"],
            self.fixture["evidence_artifacts"],
            self.fixture["environment_snapshot"],
        )
        self.assertTrue(appendix["reproducibility_ready"])
        self.assertGreaterEqual(appendix["reproducibility_score"], 80.0)

    def test_methods_appendix_detects_missing_component(self):
        components = [row.copy()
                      for row in self.fixture["pipeline_components"]][:-1]
        appendix = build_methods_reproducibility_appendix(
            components,
            self.fixture["validation_commands"],
            self.fixture["evidence_artifacts"],
            self.fixture["environment_snapshot"],
        )
        self.assertFalse(appendix["reproducibility_ready"])
        self.assertGreater(len(appendix["missing_required_components"]), 0)

    def test_business_blueprint_ready(self):
        blueprint = build_business_blueprint_summary(
            self.fixture["value_metrics"],
            self.fixture["governance_summary"],
            self.fixture["operating_model"],
        )
        self.assertTrue(blueprint["exec_blueprint_ready"])
        self.assertIn("ROAS", blueprint["headline"])

    def test_defense_deck_ready(self):
        appendix = build_methods_reproducibility_appendix(
            self.fixture["pipeline_components"],
            self.fixture["validation_commands"],
            self.fixture["evidence_artifacts"],
            self.fixture["environment_snapshot"],
        )
        blueprint = build_business_blueprint_summary(
            self.fixture["value_metrics"],
            self.fixture["governance_summary"],
            self.fixture["operating_model"],
        )
        deck = build_final_defense_deck(
            appendix,
            blueprint,
            self.fixture["technical_risks"],
        )
        self.assertTrue(deck["review_ready"])
        self.assertEqual(len(deck["slides"]), 10)

    def test_defense_deck_detects_unresolved_risk(self):
        appendix = build_methods_reproducibility_appendix(
            self.fixture["pipeline_components"],
            self.fixture["validation_commands"],
            self.fixture["evidence_artifacts"],
            self.fixture["environment_snapshot"],
        )
        blueprint = build_business_blueprint_summary(
            self.fixture["value_metrics"],
            self.fixture["governance_summary"],
            self.fixture["operating_model"],
        )
        risks = [row.copy() for row in self.fixture["technical_risks"]]
        risks[0]["status"] = "open"
        deck = build_final_defense_deck(appendix, blueprint, risks)
        self.assertFalse(deck["review_ready"])
        self.assertEqual(len(deck["unresolved_risks"]), 1)

    def test_summarize_thesis_package(self):
        summary = summarize_thesis_package(
            pipeline_components=self.fixture["pipeline_components"],
            validation_commands=self.fixture["validation_commands"],
            evidence_artifacts=self.fixture["evidence_artifacts"],
            environment_snapshot=self.fixture["environment_snapshot"],
            value_metrics=self.fixture["value_metrics"],
            governance_summary=self.fixture["governance_summary"],
            operating_model=self.fixture["operating_model"],
            technical_risks=self.fixture["technical_risks"],
        )
        self.assertTrue(summary["thesis_package_review_ready"])
        self.assertIn("methods_appendix", summary)
        self.assertIn("business_blueprint", summary)
        self.assertIn("defense_deck", summary)


if __name__ == "__main__":
    unittest.main()
