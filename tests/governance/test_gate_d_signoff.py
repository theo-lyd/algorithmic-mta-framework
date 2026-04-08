"""Test suite for Gate D Sign-Off module."""

from governance.gate_d_signoff import GateDSignoff
import unittest
import sys
import os
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))


class TestGateDSignoff(unittest.TestCase):
    """Test Gate D sign-off workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.gated = GateDSignoff()

    def test_approval_artifact_generation(self):
        """Should generate valid approval artifacts."""
        criteria = {
            "stakeholder_sign_off": True,
            "business_value_confirmed": True,
            "no_critical_blockers": True,
            "rollback_verified": True,
            "documentation_complete": True
        }

        approvers = [
            {"name": "Alice", "role": "Analytics", "email": "alice@example.com"},
            {"name": "Bob", "role": "Marketing", "email": "bob@example.com"}
        ]

        result = self.gated.generate_approval_artifact(
            phase="7",
            batch="7.1",
            criteria=criteria,
            approvers=approvers,
            evidence_artifacts=["artifact1.json", "artifact2.json"],
            notes="All controls validated"
        )

        # Verify structure
        self.assertIn("approval_id", result)
        self.assertIn("timestamp", result)
        self.assertEqual(result["phase"], "7")
        self.assertEqual(result["batch"], "7.1")
        self.assertEqual(result["approval_status"], "APPROVED")
        self.assertEqual(len(result["approvers"]), 2)
        self.assertIsNotNone(result["content_hash"])

    def test_approval_rejected_with_failures(self):
        """Should mark approval as REJECTED if criteria not met."""
        criteria = {
            "stakeholder_sign_off": False,  # Not met
            "business_value_confirmed": True,
            "no_critical_blockers": False,  # Not met
            "rollback_verified": True,
            "documentation_complete": True
        }

        approvers = [
            {"name": "Alice", "role": "Analytics", "email": "alice@example.com"}
        ]

        result = self.gated.generate_approval_artifact(
            phase="7",
            batch="7.2",
            criteria=criteria,
            approvers=approvers,
            evidence_artifacts=[]
        )

        self.assertEqual(result["approval_status"], "REJECTED")

    def test_audit_trail_generation(self):
        """Should generate valid audit trail."""
        criteria = {
            "stakeholder_sign_off": True,
            "business_value_confirmed": True,
            "no_critical_blockers": True,
            "rollback_verified": True,
            "documentation_complete": True
        }

        approvers = [
            {"name": "Alice", "role": "Analytics", "email": "alice@example.com"},
            {"name": "Bob", "role": "Marketing", "email": "bob@example.com"}
        ]

        result = self.gated.generate_approval_artifact(
            phase="7", batch="7.1",
            criteria=criteria,
            approvers=approvers,
            evidence_artifacts=[]
        )

        # Verify audit trail
        self.assertIn("audit_trail", result)
        self.assertEqual(result["audit_trail"]["approval_count"], 2)
        self.assertEqual(result["audit_trail"]["required_approvals"], 2)
        self.assertTrue(result["audit_trail"]["approvals_met"])

    def test_cross_phase_compliance_check(self):
        """Should verify compliance across phases."""
        # This test checks the verification logic
        compliance = self.gated.verify_cross_phase_compliance(
            phases=["0", "1", "2"])

        # Verify structure
        self.assertIn("compliance_check_timestamp", compliance)
        self.assertIn("phases_checked", compliance)
        self.assertIn("all_phases_compliant", compliance)
        self.assertIn("compliance_map", compliance)
        self.assertIn("overall_status", compliance)

        # Verify phase entries
        self.assertIsNotNone(compliance["compliance_map"].get("0"))
        self.assertIsNotNone(compliance["compliance_map"].get("1"))

    def test_signoff_report_generation(self):
        """Should generate comprehensive sign-off report."""
        report = self.gated.generate_signoff_report(branch="master")

        # Verify structure
        self.assertIn("report_id", report)
        self.assertIn("generated_at", report)
        self.assertEqual(report["branch"], "master")

        # Verify summary section
        self.assertIn("summary", report)
        self.assertIn("total_phases", report["summary"])
        self.assertIn("overall_status", report["summary"])

        # Verify stakeholder section
        self.assertIn("stakeholder_signatures", report)
        self.assertGreater(len(report["stakeholder_signatures"]), 0)

        # Verify requirements
        self.assertIn("gate_d_requirements", report)
        self.assertIn("deployment_readiness", report)

    def test_approval_count_requirement(self):
        """Should enforce minimum approval count."""
        criteria = {
            "stakeholder_sign_off": True,
            "business_value_confirmed": True,
            "no_critical_blockers": True,
            "rollback_verified": True,
            "documentation_complete": True
        }

        # Single approver
        approvers_single = [
            {"name": "Alice", "role": "Analytics", "email": "alice@example.com"}
        ]

        result_single = self.gated.generate_approval_artifact(
            phase="7", batch="7.1",
            criteria=criteria,
            approvers=approvers_single,
            evidence_artifacts=[]
        )

        self.assertEqual(result_single["audit_trail"]["approval_count"], 1)
        self.assertEqual(result_single["audit_trail"]["required_approvals"], 2)
        self.assertFalse(result_single["audit_trail"]["approvals_met"])

        # Two approvers
        approvers_dual = [
            {"name": "Alice", "role": "Analytics", "email": "alice@example.com"},
            {"name": "Bob", "role": "Marketing", "email": "bob@example.com"}
        ]

        result_dual = self.gated.generate_approval_artifact(
            phase="7", batch="7.1",
            criteria=criteria,
            approvers=approvers_dual,
            evidence_artifacts=[]
        )

        self.assertEqual(result_dual["audit_trail"]["approval_count"], 2)
        self.assertTrue(result_dual["audit_trail"]["approvals_met"])


class TestApprovalAuditTrail(unittest.TestCase):
    """Test approval audit trail verification."""

    def setUp(self):
        """Set up test fixtures."""
        self.gated = GateDSignoff()

    def test_audit_trail_verification_not_found(self):
        """Should handle missing approval artifacts."""
        result = self.gated.verify_approval_audit_trail(phase="9", batch="9.1")

        self.assertEqual(result["audit_status"], "NOT_FOUND")
        self.assertEqual(result["phase"], "9")
        self.assertEqual(result["batch"], "9.1")


if __name__ == "__main__":
    unittest.main()
