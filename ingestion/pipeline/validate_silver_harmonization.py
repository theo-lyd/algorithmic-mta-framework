"""Batch 2.3 validation runner for silver harmonization controls."""

from __future__ import annotations

import json
from pathlib import Path

from ingestion.pipeline.silver_harmonization import build_silver_tables, load_jsonl


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    source_path = base_dir / "tests" / "fixtures" / \
        "phase2" / "silver" / "raw_events_for_silver.jsonl"
    output_path = base_dir / "artifacts" / "phase-2" / \
        "batch-2-3" / "silver_harmonization_summary.json"

    rows = load_jsonl(source_path)
    tables = build_silver_tables(rows)

    summary = {
        "events_count": int(tables.events.shape[0]),
        "event_params_count": int(tables.event_params.shape[0]),
        "event_items_count": int(tables.event_items.shape[0]),
        "sessions_count": int(tables.sessions.shape[0]),
        "dim_channel_count": int(tables.dim_channel.shape[0]),
        "dim_campaign_count": int(tables.dim_campaign.shape[0]),
        "dim_device_count": int(tables.dim_device.shape[0]),
        "dim_geography_count": int(tables.dim_geography.shape[0]),
        "sessionization_rule_valid": int(
            tables.sessions[tables.sessions["user_pseudo_id"]
                            == "u-100"].shape[0]
        )
        == 2,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(
        summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
