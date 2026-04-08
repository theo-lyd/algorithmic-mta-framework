from __future__ import annotations

import unittest
from pathlib import Path

from ingestion.pipeline.silver_harmonization import build_silver_tables, load_jsonl
from quality.contracts.quarantine import quarantine_failed_rows
from quality.contracts.silver_contracts import (
    null_uniqueness_range_checks,
    referential_integrity_checks,
    required_fields_check,
    schema_drift_check,
)


class TestSilverContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture = Path(
            "tests/fixtures/phase2/silver/raw_events_for_silver.jsonl")
        rows = load_jsonl(fixture)
        cls.tables = build_silver_tables(rows)

    def test_contracts_pass_for_valid_tables(self) -> None:
        required = required_fields_check(self.tables.events)
        self.assertTrue(required.success)

        for table_name in [
            "events",
            "event_params",
            "event_items",
            "sessions",
            "dim_channel",
            "dim_campaign",
            "dim_device",
            "dim_geography",
        ]:
            df = getattr(self.tables, table_name)
            drift = schema_drift_check(table_name, df)
            self.assertTrue(drift.success)

        checks = null_uniqueness_range_checks(
            self.tables.events, self.tables.sessions)
        self.assertTrue(all(c.success for c in checks))

        refs = referential_integrity_checks(
            self.tables.events,
            self.tables.event_params,
            self.tables.event_items,
            self.tables.dim_channel,
            self.tables.dim_campaign,
        )
        self.assertTrue(all(c.success for c in refs))

    def test_schema_drift_detected(self) -> None:
        drift_df = self.tables.events.drop(columns=["source_channel"]).copy()
        result = schema_drift_check("events", drift_df)
        self.assertFalse(result.success)
        self.assertIn("source_channel", result.details["missing_columns"])

    def test_quarantine_workflow(self) -> None:
        bad_df = self.tables.events.copy()
        bad_df.loc[0, "event_id"] = None
        mask = bad_df["event_id"].isna()

        quarantine_path = Path(
            "artifacts/phase-2/batch-2-4/quarantine/test_quarantine.jsonl")
        remediation_path = Path(
            "artifacts/phase-2/batch-2-4/quarantine/test_remediation.csv")

        count = quarantine_failed_rows(
            df=bad_df,
            failed_mask=mask,
            reason="required_event_id_missing",
            quarantine_path=quarantine_path,
            remediation_path=remediation_path,
        )
        self.assertEqual(count, 1)
        self.assertTrue(quarantine_path.exists())
        self.assertTrue(remediation_path.exists())


if __name__ == "__main__":
    unittest.main()
