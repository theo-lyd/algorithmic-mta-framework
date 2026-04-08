"""Batch 4.2 validation runner for Markov attribution."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ingestion.pipeline.markov_attribution import (
    compute_removal_effects,
    extract_paths,
    normalize_markov_attribution,
    summarize_markov_stability,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    events_path = base_dir / "tests" / "fixtures" / \
        "phase4" / "attribution_events.json"
    out_dir = base_dir / "artifacts" / "phase-4" / "batch-4-2"
    out_dir.mkdir(parents=True, exist_ok=True)

    events_df = pd.DataFrame(json.loads(
        events_path.read_text(encoding="utf-8")))
    paths_df = extract_paths(events_df)
    effects_df = compute_removal_effects(paths_df)
    total_conversions = int(events_df[events_df["is_conversion"]].shape[0])
    normalized_df = normalize_markov_attribution(
        effects_df, total_conversions=total_conversions)

    summary = {
        "markov_summary": summarize_markov_stability(normalized_df),
        "total_conversions": total_conversions,
        "removal_effects": effects_df.to_dict("records"),
        "normalized_attribution": normalized_df.to_dict("records"),
    }

    summary_path = out_dir / "markov_attribution_summary.json"
    summary_path.write_text(json.dumps(
        summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
