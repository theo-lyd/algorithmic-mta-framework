"""Tests for Phase VII Batch 7.1: Production readiness."""

import json
from pathlib import Path
import unittest

from production.readiness import (
    run_backfill_stress_tests,
    run_disaster_recovery_replay_testing,
    run_security_access_audit,
    summarize_production_readiness,
)


class TestBatch71ProductionReadiness(unittest.TestCase):
    """Validate DR replay, backfill stress, and security access sign-off."""

    @classmethod
    def setUpClass(cls):
        fixture_path = (
            Path(__file__).parent.parent / "fixtures" /
            "phase7" / "production_readiness.json"
        )
        with open(fixture_path, "r", encoding="utf-8") as handle:
            cls.fixture = json.load(handle)

    def test_disaster_recovery_replay_passes(self):
        summary = run_disaster_recovery_replay_testing(
            replay_runs=self.fixture["replay_runs"],
            expected_checksum_by_batch=self.fixture["expected_checksum_by_batch"],
        )
        self.assertTrue(summary["all_checks_passed"])
        self.assertEqual(summary["replay_batches"], 3)
        self.assertEqual(summary["deterministic_batches"], 3)

    def test_disaster_recovery_detects_checksum_mismatch(self):
        replay_runs = [row.copy() for row in self.fixture["replay_runs"]]
        replay_runs[0]["replay_checksum"] = "bad-checksum"

        summary = run_disaster_recovery_replay_testing(
            replay_runs=replay_runs,
            expected_checksum_by_batch=self.fixture["expected_checksum_by_batch"],
        )

        self.assertFalse(summary["all_checks_passed"])
        self.assertGreater(len(summary["violations"]), 0)

    def test_backfill_stress_passes(self):
        summary = run_backfill_stress_tests(self.fixture["backfill_windows"])
        self.assertTrue(summary["all_checks_passed"])
        self.assertEqual(summary["windows_tested"], 4)

    def test_backfill_stress_detects_runtime_breach(self):
        windows = [row.copy() for row in self.fixture["backfill_windows"]]
        windows[1]["runtime_minutes"] = 140
        summary = run_backfill_stress_tests(windows)
        self.assertFalse(summary["all_checks_passed"])
        self.assertIn("runtime breach", summary["violations"][0])

    def test_security_access_audit_passes(self):
        summary = run_security_access_audit(
            users=self.fixture["users"],
            role_permissions=self.fixture["role_permissions"],
            required_prod_permissions=[
                "read_metrics", "trigger_replay", "view_logs"],
            restricted_permissions=["drop_production_tables", "write_raw_pii"],
        )
        self.assertTrue(summary["all_checks_passed"])
        self.assertEqual(summary["users_audited"], 4)

    def test_summarize_production_readiness(self):
        summary = summarize_production_readiness(
            replay_runs=self.fixture["replay_runs"],
            expected_checksum_by_batch=self.fixture["expected_checksum_by_batch"],
            backfill_windows=self.fixture["backfill_windows"],
            users=self.fixture["users"],
            role_permissions=self.fixture["role_permissions"],
        )
        self.assertTrue(summary["production_signoff_complete"])
        self.assertIn("disaster_recovery", summary)
        self.assertIn("backfill_stress", summary)
        self.assertIn("security_access", summary)


if __name__ == "__main__":
    unittest.main()
