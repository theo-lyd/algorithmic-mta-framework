"""Batch 4.1 validation runner for heuristic attribution baselines."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ingestion.pipeline.heuristic_attribution import (
    build_benchmark_evaluation_set,
    first_touch_attribution,
    last_touch_attribution,
    linear_attribution,
    time_decay_attribution,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    events_path = base_dir / "tests" / "fixtures" / \
        "phase4" / "attribution_events.json"
    benchmark_path = base_dir / "tests" / "fixtures" / \
        "phase4" / "benchmark_reference.json"
    out_dir = base_dir / "artifacts" / "phase-4" / "batch-4-1"
    out_dir.mkdir(parents=True, exist_ok=True)

    events_df = pd.DataFrame(json.loads(
        events_path.read_text(encoding="utf-8")))
    benchmark_df = pd.DataFrame(json.loads(
        benchmark_path.read_text(encoding="utf-8")))

    first_df = first_touch_attribution(events_df)
    last_df = last_touch_attribution(events_df)
    linear_df = linear_attribution(events_df)
    decay_df = time_decay_attribution(events_df)

    benchmark = build_benchmark_evaluation_set(
        benchmark_df,
        {
            "first_touch": first_df,
            "last_touch": last_df,
            "linear": linear_df,
            "time_decay": decay_df,
        },
    )

    summary = {
        "conversions": int(events_df[events_df["is_conversion"]].shape[0]),
        "methods": ["first_touch", "last_touch", "linear", "time_decay"],
        "benchmark": benchmark.to_dict("records"),
    }

    summary_path = out_dir / "heuristic_attribution_summary.json"
    summary_path.write_text(json.dumps(
        summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
