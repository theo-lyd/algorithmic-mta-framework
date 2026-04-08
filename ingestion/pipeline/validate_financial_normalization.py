"""Batch 2.2 validation runner for financial and numeric normalization."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from ingestion.pipeline.financial_normalization import normalize_currency_to_eur


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    fixture_path = base_dir / "tests" / "fixtures" / \
        "phase2" / "financial" / "financial_cases.json"
    output_path = base_dir / "artifacts" / "phase-2" / \
        "batch-2-2" / "financial_normalization_summary.json"

    cases = json.loads(fixture_path.read_text(encoding="utf-8"))

    results = []
    for case in cases:
        normalized = normalize_currency_to_eur(
            raw_text=case["raw_text"],
            effective_dt=date.fromisoformat(case["effective_date"]),
        )
        results.append(
            {
                "raw_text": case["raw_text"],
                "currency": normalized.currency,
                "amount_native": normalized.amount_native,
                "fx_rate_to_eur": normalized.fx_rate_to_eur,
                "amount_eur": normalized.amount_eur,
                "matches_expected": (
                    normalized.currency == case["expected_currency"]
                    and round(normalized.amount_native, 6) == round(case["expected_native"], 6)
                    and round(normalized.fx_rate_to_eur, 6) == round(case["expected_rate"], 6)
                    and round(normalized.amount_eur, 2) == round(case["expected_eur"], 2)
                ),
            }
        )

    passed = sum(1 for row in results if row["matches_expected"])
    summary = {
        "total_cases": len(results),
        "passed_cases": passed,
        "failed_cases": len(results) - passed,
        "all_passed": passed == len(results),
        "results": results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(
        summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
