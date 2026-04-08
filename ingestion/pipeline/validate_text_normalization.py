"""Batch 2.1 validation runner for encoding and locale normalization."""

from __future__ import annotations

import json
from pathlib import Path

from ingestion.pipeline.text_normalization import normalize_text


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    fixture_path = base_dir / "tests" / "fixtures" / \
        "phase2" / "text_cleaning_fixtures.json"
    output_path = base_dir / "artifacts" / "phase-2" / \
        "batch-2-1" / "text_normalization_summary.json"

    fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))

    checks = []
    for case in fixtures:
        normalized = normalize_text(case["raw_text"])
        checks.append(
            {
                "raw_text": case["raw_text"],
                "display_text": normalized.display_text,
                "join_key_text": normalized.join_key_text,
                "source_encoding": normalized.source_encoding,
                "display_match": normalized.display_text == case["expected_display_text"],
                "join_key_match": normalized.join_key_text == case["expected_join_key_text"],
            }
        )

    passed = sum(
        1 for row in checks if row["display_match"] and row["join_key_match"])
    summary = {
        "total_cases": len(checks),
        "passed_cases": passed,
        "failed_cases": len(checks) - passed,
        "all_passed": passed == len(checks),
        "results": checks,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(
        summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
