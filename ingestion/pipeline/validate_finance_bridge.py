"""Batch 4.5 validation runner for attribution-to-finance bridge."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ingestion.pipeline.attribution_finance_bridge import (
    allocate_net_revenue,
    reconciliation_summary,
    recompute_channel_roas,
    summarize_finance_bridge,
    variance_against_current,
)
from ingestion.pipeline.heuristic_attribution import (
    first_touch_attribution,
    last_touch_attribution,
    linear_attribution,
    time_decay_attribution,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    events_path = base_dir / "tests" / "fixtures" / \
        "phase4" / "attribution_events.json"
    spend_path = base_dir / "tests" / "fixtures" / "phase4" / "channel_spend.json"
    out_dir = base_dir / "artifacts" / "phase-4" / "batch-4-5"
    out_dir.mkdir(parents=True, exist_ok=True)

    events_df = pd.DataFrame(json.loads(
        events_path.read_text(encoding="utf-8")))
    spend_df = pd.DataFrame(json.loads(spend_path.read_text(encoding="utf-8")))

    methods = {
        "first_touch": first_touch_attribution(events_df),
        "last_touch": last_touch_attribution(events_df),
        "linear": linear_attribution(events_df),
        "time_decay": time_decay_attribution(events_df),
    }
    attributed_rows = []
    for method_name, frame in methods.items():
        method_frame = frame.copy()
        method_frame["method"] = method_name
        attributed_rows.append(method_frame)
    attribution_df = pd.concat(attributed_rows, ignore_index=True)

    conversions_df = events_df[events_df["is_conversion"]][[
        "conversion_id", "net_revenue_eur"]].copy()
    allocated_df = allocate_net_revenue(conversions_df, attribution_df)
    roas_df = recompute_channel_roas(allocated_df, spend_df)
    variance_df = variance_against_current(
        roas_df, current_method="last_touch")
    reconciliation_df = reconciliation_summary(conversions_df, allocated_df)

    roas_path = out_dir / "channel_roas_by_method.csv"
    roas_df.to_csv(roas_path, index=False, encoding="utf-8")

    summary = {
        "finance_bridge_summary": summarize_finance_bridge(roas_df, reconciliation_df),
        "reconciliation": reconciliation_df.to_dict("records"),
        "variance_sample": variance_df[["method", "channel", "roas", "roas_delta_abs", "roas_delta_pct"]]
        .sort_values(["method", "channel"]).to_dict("records"),
        "roas_output_path": str(roas_path.relative_to(base_dir)),
    }

    summary_path = out_dir / "finance_bridge_summary.json"
    summary_path.write_text(json.dumps(
        summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
