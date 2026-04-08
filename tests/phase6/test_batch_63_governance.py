"""Tests for Phase VI Batch 6.3: Decision Governance and Adoption."""

from dashboards.governance.decision_framework import (
    validate_kpi_definition,
    kpi_checklist,
    monthly_ritual_checklist,
    training_curriculum_summary,
    summarize_governance,
    KPI_GLOSSARY,
    MONTHLY_DECISION_RITUAL,
    TRAINING_CURRICULUM,
)
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestBatch63Governance(unittest.TestCase):
    """Test Batch 6.3: Governance and adoption."""

    def test_kpi_definitions_complete(self):
        """Test that all KPI definitions are valid."""
        self.assertGreater(len(KPI_GLOSSARY), 0, "KPI glossary not empty")

        for kpi in KPI_GLOSSARY:
            is_valid, violations = validate_kpi_definition(kpi)
            self.assertTrue(
                is_valid, f"KPI {kpi.kpi_name} invalid: {violations}")
            self.assertIsNotNone(kpi.formula)
            self.assertGreater(len(kpi.rationale), 10)

    def test_kpi_checklist(self):
        """Test KPI validation checklist."""
        checklist = kpi_checklist()

        self.assertEqual(checklist["kpis_checked"], len(KPI_GLOSSARY))
        self.assertEqual(checklist["failed"], 0)
        self.assertGreater(checklist["passed"], 0)

    def test_monthly_ritual_completeness(self):
        """Test monthly decision ritual is properly defined."""
        ritual = MONTHLY_DECISION_RITUAL

        self.assertGreater(len(ritual.participants), 2)
        self.assertGreater(len(ritual.pre_work), 0)
        self.assertGreater(len(ritual.agenda), 0)
        self.assertGreater(len(ritual.decision_criteria), 0)
        # Agenda should be ordered by time
        times = [item["time_min"] for item in ritual.agenda]
        self.assertEqual(times, sorted(times))

    def test_monthly_ritual_checklist(self):
        """Test pre-flight checklist for monthly ritual."""
        checklist = monthly_ritual_checklist()

        self.assertIn("ceremony", checklist)
        self.assertIn("pre_work_items", checklist)
        self.assertIn("decision_criteria_count", checklist)
        self.assertGreater(checklist["decision_criteria_count"], 0)
        self.assertEqual(checklist["status"], "ready")

    def test_training_curriculum(self):
        """Test training curriculum for all roles."""
        self.assertGreater(len(TRAINING_CURRICULUM), 0)

        for module in TRAINING_CURRICULUM:
            self.assertIsNotNone(module.role)
            self.assertGreater(len(module.target_learnings), 0)
            self.assertGreater(len(module.materials), 0)
            self.assertGreater(len(module.success_criteria), 10)

    def test_training_curriculum_summary(self):
        """Test training curriculum summary generation."""
        summary = training_curriculum_summary()

        self.assertEqual(summary["total_modules"], len(TRAINING_CURRICULUM))
        self.assertGreater(summary["total_training_hours"], 0)
        self.assertGreater(len(summary["roles"]), 0)

    def test_training_covers_cmo_finance_growth(self):
        """Test training covers required roles."""
        roles = set(m.role for m in TRAINING_CURRICULUM)

        self.assertIn("CMO", roles)
        self.assertIn("Finance Controller", roles)
        self.assertIn("Growth Manager", roles)

    def test_summarize_governance(self):
        """Test governance summary generation."""
        summary = summarize_governance()

        self.assertIn("kpi_glossary", summary)
        self.assertIn("monthly_ritual", summary)
        self.assertIn("training_curriculum", summary)
        self.assertIn("governance_artifacts", summary)
        self.assertIn("adoption_readiness", summary)

        artifacts = summary["governance_artifacts"]
        self.assertGreater(artifacts["kpi_definitions"], 0)
        self.assertGreater(artifacts["decision_ritual_agenda_items"], 0)
        self.assertGreater(artifacts["training_modules"], 0)


if __name__ == "__main__":
    unittest.main()
