"""Batch 5.1 validation runner for reliability monitors and incident policy."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ingestion.pipeline.reliability_monitors import (
    distribution_monitor,
    freshness_monitor,
    pixel_downtime_detection,
    schema_monitor,
    summarize_reliability,
    volume_monitor,
)


def main() -> None:
    base = Path(__file__).resolve().parents[2]
    payload = json.loads((base / "tests" / "fixtures" / "phase5" /
                         "reliability_metrics.json").read_text(encoding="utf-8"))
    expected_cols = json.loads(
        (base / "tests" / "fixtures" / "phase5" / "schema_expected.json").read_text(encoding="utf-8"))
    actual_cols = json.loads((base / "tests" / "fixtures" /
                             "phase5" / "schema_actual.json").read_text(encoding="utf-8"))

    checks = [
        freshness_monitor(pd.DataFrame(
            payload["freshness"]), max_lag_minutes=60),
        volume_monitor(pd.DataFrame(
            payload["volume"]), drop_threshold_ratio=0.7),
        schema_monitor(actual_cols, expected_cols),
        distribution_monitor(payload["distribution_baseline"],
                             payload["distribution_current"], max_l1_distance=0.2),
        pixel_downtime_detection(
            payload["pixel"]["spend_eur"], payload["pixel"]["page_views"]),
    ]
    summary = summarize_reliability(checks)

    out_dir = base / "artifacts" / "phase-5" / "batch-5-1"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "reliability_summary.json"
    out_file.write_text(
        json.dumps(
            {
                "checks": [
                    {"name": c.name, "success": c.success, "details": c.details}
                    for c in checks
                ],
                "summary": summary,
            },
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )
    print(out_file.relative_to(base))


if __name__ == "__main__":
    main()
