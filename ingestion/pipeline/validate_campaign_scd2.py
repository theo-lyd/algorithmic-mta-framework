"""Batch 3.1 validation runner for campaign SCD2 and point-in-time joins."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ingestion.pipeline.campaign_scd2 import (
    build_campaign_scd2,
    point_in_time_join,
    summarize_scd2_changes,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    changes_path = base_dir / "tests" / "fixtures" / \
        "phase3" / "campaign_changes.json"
    events_path = base_dir / "tests" / "fixtures" / "phase3" / "campaign_events.json"
    out_path = base_dir / "artifacts" / "phase-3" / \
        "batch-3-1" / "campaign_scd2_summary.json"

    changes_df = pd.DataFrame(json.loads(
        changes_path.read_text(encoding="utf-8")))
    events_df = pd.DataFrame(json.loads(
        events_path.read_text(encoding="utf-8")))

    scd2_df = build_campaign_scd2(changes_df).campaign_scd2
    pit_joined = point_in_time_join(events_df, scd2_df)

    coverage = int(pit_joined["event_id"].nunique())
    total_events = int(events_df["event_id"].nunique())

    summary = {
        "scd2_summary": summarize_scd2_changes(scd2_df),
        "point_in_time_join": {
            "total_events": total_events,
            "matched_events": coverage,
            "all_events_matched": coverage == total_events,
        },
        "sample_assignments": pit_joined[["event_id", "campaign_id", "owner_name", "budget_eur", "taxonomy_l2"]]
        .sort_values("event_id")
        .to_dict("records"),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2,
                        ensure_ascii=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True, default=str))


if __name__ == "__main__":
    main()
