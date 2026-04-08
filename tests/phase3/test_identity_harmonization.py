from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from ingestion.pipeline.identity_harmonization import resolve_identity, summarize_resolution


class TestIdentityHarmonization(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        records = json.loads(
            Path("tests/fixtures/phase3/identity_records.json").read_text(encoding="utf-8"))
        cls.df = pd.DataFrame(records)
        cls.result = resolve_identity(cls.df)

    def test_matching_hierarchy_and_merge(self) -> None:
        resolved = self.result.resolved_identities
        rec_1 = resolved[resolved["record_id"] == "id-001"].iloc[0]
        rec_2 = resolved[resolved["record_id"] == "id-002"].iloc[0]
        self.assertEqual(rec_1["customer_hash"], rec_2["customer_hash"])

    def test_conflict_goes_to_unresolved_queue(self) -> None:
        unresolved = self.result.unresolved_queue
        rec_4 = unresolved[unresolved["record_id"] == "id-004"].iloc[0]
        self.assertEqual(rec_4["resolution_status"], "unresolved")
        self.assertEqual(rec_4["reason"], "conflicting_identifier_clusters")

    def test_no_identifier_goes_to_unresolved_queue(self) -> None:
        unresolved = self.result.unresolved_queue
        rec_5 = unresolved[unresolved["record_id"] == "id-005"].iloc[0]
        self.assertEqual(rec_5["reason"], "no_identifiers_available")

    def test_confidence_score_present(self) -> None:
        resolved = self.result.resolved_identities
        self.assertTrue((resolved["identity_confidence_score"] > 0).all())

    def test_summary_metrics(self) -> None:
        summary = summarize_resolution(self.result)
        self.assertEqual(summary["resolved_rows"], 3)
        self.assertEqual(summary["unresolved_rows"], 2)
        self.assertEqual(summary["unique_customer_hashes"], 2)


if __name__ == "__main__":
    unittest.main()
