"""Batch 4.3 validation runner for conversion propensity model."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ingestion.pipeline.propensity_model import (
    build_feature_store,
    meets_lift_threshold,
    train_calibrated_logistic,
)


AGREED_LIFT_THRESHOLD = 0.6


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    events_path = base_dir / "tests" / "fixtures" / "phase4" / "customer_events.json"
    out_dir = base_dir / "artifacts" / "phase-4" / "batch-4-3"
    out_dir.mkdir(parents=True, exist_ok=True)

    events_df = pd.DataFrame(json.loads(
        events_path.read_text(encoding="utf-8")))
    feature_store = build_feature_store(
        events_df, snapshot_ts="2026-03-01T00:00:00Z")
    result = train_calibrated_logistic(feature_store)

    holdout_path = out_dir / "propensity_holdout_predictions.csv"
    result.holdout_predictions.to_csv(
        holdout_path, index=False, encoding="utf-8")

    summary = {
        "agreed_lift_threshold": AGREED_LIFT_THRESHOLD,
        "meets_lift_threshold": meets_lift_threshold(result.metrics, threshold=AGREED_LIFT_THRESHOLD),
        "metrics": result.metrics,
        "feature_rows": int(feature_store.shape[0]),
        "holdout_predictions_path": str(holdout_path.relative_to(base_dir)),
    }

    summary_path = out_dir / "propensity_model_summary.json"
    summary_path.write_text(json.dumps(
        summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
