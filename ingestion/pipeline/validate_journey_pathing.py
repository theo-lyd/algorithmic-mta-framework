"""Batch 3.3 validation runner for journey construction and pathing."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ingestion.pipeline.journey_pathing import (
    build_conversion_attribution,
    build_journeys,
    build_touchpoints,
    summarize_journey_build,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    events_path = base_dir / "tests" / "fixtures" / \
        "phase3" / "journeys" / "journey_events.json"
    out_dir = base_dir / "artifacts" / "phase-3" / "batch-3-3"
    out_dir.mkdir(parents=True, exist_ok=True)

    events_df = pd.DataFrame(json.loads(
        events_path.read_text(encoding="utf-8")))
    touchpoints_df = build_touchpoints(events_df)
    journeys_df = build_journeys(events_df)
    conversions_df = build_conversion_attribution(events_df)

    summary = {
        "journey_summary": summarize_journey_build(touchpoints_df, journeys_df, conversions_df),
        "sample_journeys": journeys_df[["user_pseudo_id", "journey_id", "journey_path", "conversion_count"]]
        .sort_values(["user_pseudo_id", "journey_id"])
        .to_dict("records"),
        "sample_conversions": conversions_df[["conversion_event_id", "journey_id", "attribution_path", "lookback_touchpoints"]]
        .sort_values(["conversion_event_id"])
        .to_dict("records"),
    }

    summary_path = out_dir / "journey_pathing_summary.json"
    summary_path.write_text(json.dumps(
        summary, indent=2, ensure_ascii=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True, default=str))


if __name__ == "__main__":
    main()
