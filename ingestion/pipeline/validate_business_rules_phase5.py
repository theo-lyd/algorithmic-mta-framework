"""Batch 5.2 validation runner for GE-style business rules."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from quality.contracts.business_rules_phase5 import (
    attribution_conservation_no_ghost_revenue,
    lookback_and_session_boundary_assertions,
    referential_integrity_conversion_to_session,
    summarize_business_rules,
)


def main() -> None:
    base = Path(__file__).resolve().parents[2]
    payload = json.loads((base / "tests" / "fixtures" / "phase5" /
                         "business_rules_data.json").read_text(encoding="utf-8"))

    conversions_df = pd.DataFrame(payload["conversions"])
    sessions_df = pd.DataFrame(payload["sessions"])
    attributed_df = pd.DataFrame(payload["attributed_revenue"])
    boundary_df = pd.DataFrame(payload["boundary_rows"])

    checks = [
        referential_integrity_conversion_to_session(
            conversions_df, sessions_df),
        attribution_conservation_no_ghost_revenue(
            conversions_df, attributed_df),
        lookback_and_session_boundary_assertions(boundary_df),
    ]

    out_dir = base / "artifacts" / "phase-5" / "batch-5-2"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "business_rules_summary.json"
    out_file.write_text(
        json.dumps(
            {
                "checks": [
                    {"name": c.name, "success": c.success, "details": c.details}
                    for c in checks
                ],
                "summary": summarize_business_rules(checks),
            },
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )
    print(out_file.relative_to(base))


if __name__ == "__main__":
    main()
