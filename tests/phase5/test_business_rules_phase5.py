from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from quality.contracts.business_rules_phase5 import (
    attribution_conservation_no_ghost_revenue,
    lookback_and_session_boundary_assertions,
    referential_integrity_conversion_to_session,
    summarize_business_rules,
)


class TestBusinessRulesPhase5(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        payload = json.loads(Path(
            "tests/fixtures/phase5/business_rules_data.json").read_text(encoding="utf-8"))
        cls.sessions_df = pd.DataFrame(payload["sessions"])
        cls.conversions_df = pd.DataFrame(payload["conversions"])
        cls.attributed_df = pd.DataFrame(payload["attributed_revenue"])
        cls.boundary_df = pd.DataFrame(payload["boundary_rows"])

    def test_business_rules(self) -> None:
        checks = [
            referential_integrity_conversion_to_session(
                self.conversions_df, self.sessions_df),
            attribution_conservation_no_ghost_revenue(
                self.conversions_df, self.attributed_df),
            lookback_and_session_boundary_assertions(
                self.boundary_df, max_lookback_days=30, max_session_gap_minutes=30),
        ]
        self.assertTrue(all(check.success for check in checks))

        summary = summarize_business_rules(checks)
        self.assertEqual(summary["checks_failed"], 0)


if __name__ == "__main__":
    unittest.main()
