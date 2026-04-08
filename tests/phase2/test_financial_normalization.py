from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path

from ingestion.pipeline.financial_normalization import (
    normalize_currency_to_eur,
    parse_abbreviated_amount,
    standardize_numeric_token,
)


class TestFinancialNormalization(unittest.TestCase):
    def test_standardize_numeric_token_de_style(self) -> None:
        self.assertEqual(standardize_numeric_token("1.234,56"), 1234.56)

    def test_standardize_numeric_token_us_style(self) -> None:
        self.assertEqual(standardize_numeric_token("1,234.56"), 1234.56)

    def test_parse_abbreviated_amount(self) -> None:
        self.assertEqual(parse_abbreviated_amount("1,25 Mio EUR"), 1_250_000.0)
        self.assertEqual(parse_abbreviated_amount(
            "3,2 Mrd GBP"), 3_200_000_000.0)

    def test_currency_normalization_from_fixtures(self) -> None:
        fixture_path = Path(
            "tests/fixtures/phase2/financial/financial_cases.json")
        cases = json.loads(fixture_path.read_text(encoding="utf-8"))

        for case in cases:
            normalized = normalize_currency_to_eur(
                raw_text=case["raw_text"],
                effective_dt=date.fromisoformat(case["effective_date"]),
            )
            self.assertEqual(normalized.currency, case["expected_currency"])
            self.assertAlmostEqual(
                normalized.amount_native, case["expected_native"], places=6)
            self.assertAlmostEqual(
                normalized.fx_rate_to_eur, case["expected_rate"], places=6)
            self.assertAlmostEqual(normalized.amount_eur,
                                   case["expected_eur"], places=2)


if __name__ == "__main__":
    unittest.main()
