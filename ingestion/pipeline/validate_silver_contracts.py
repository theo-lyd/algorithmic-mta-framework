"""Batch 2.4 validation runner for silver quality contracts."""

from __future__ import annotations

import json
from pathlib import Path

from ingestion.pipeline.silver_harmonization import build_silver_tables, load_jsonl
from quality.contracts.quarantine import quarantine_failed_rows
from quality.contracts.silver_contracts import (
    null_uniqueness_range_checks,
    referential_integrity_checks,
    required_fields_check,
    schema_drift_check,
)


def _serialize(result) -> dict:
    return {
        "name": result.name,
        "success": result.success,
        "details": result.details,
    }


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    source_path = base_dir / "tests" / "fixtures" / \
        "phase2" / "silver" / "raw_events_for_silver.jsonl"

    out_dir = base_dir / "artifacts" / "phase-2" / "batch-2-4"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_jsonl(source_path)
    tables = build_silver_tables(rows)

    required = required_fields_check(tables.events)

    schema_checks = []
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
        schema_checks.append(schema_drift_check(
            table_name, getattr(tables, table_name)))

    ge_style_checks = null_uniqueness_range_checks(
        tables.events, tables.sessions)
    ref_checks = referential_integrity_checks(
        tables.events,
        tables.event_params,
        tables.event_items,
        tables.dim_channel,
        tables.dim_campaign,
    )

    # Quarantine demo path with intentionally invalid record.
    bad_events = tables.events.copy()
    bad_events.loc[0, "event_id"] = None
    failed_mask = bad_events["event_id"].isna()

    quarantine_path = out_dir / "quarantine" / "failed_records.jsonl"
    remediation_path = out_dir / "quarantine" / "remediation_candidates.csv"

    quarantined_count = quarantine_failed_rows(
        df=bad_events,
        failed_mask=failed_mask,
        reason="required_event_id_missing",
        quarantine_path=quarantine_path,
        remediation_path=remediation_path,
    )

    summary = {
        "required_fields_check": _serialize(required),
        "schema_drift_checks": [_serialize(r) for r in schema_checks],
        "ge_style_checks": [_serialize(r) for r in ge_style_checks],
        "referential_integrity_checks": [_serialize(r) for r in ref_checks],
        "all_contracts_passed": all(
            [
                required.success,
                all(r.success for r in schema_checks),
                all(r.success for r in ge_style_checks),
                all(r.success for r in ref_checks),
            ]
        ),
        "quarantine_workflow": {
            "quarantined_count": quarantined_count,
            "quarantine_path": str(quarantine_path.relative_to(base_dir)),
            "remediation_path": str(remediation_path.relative_to(base_dir)),
        },
        "great_expectations_suite": "quality/great_expectations/suites/silver_events_quality_suite.json",
        "great_expectations_checkpoint": "quality/great_expectations/checkpoints/silver_quality_checkpoint.yml",
    }

    out_path = out_dir / "silver_contracts_summary.json"
    out_path.write_text(json.dumps(summary, indent=2,
                        ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
