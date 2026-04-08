"""Batch 4.4 validation runner for behavioral segmentation."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ingestion.pipeline.behavioral_segmentation import (
    engineer_rfm_features,
    label_segments_with_playbooks,
    train_kmeans_segments,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    events_path = base_dir / "tests" / "fixtures" / "phase4" / "customer_events.json"
    out_dir = base_dir / "artifacts" / "phase-4" / "batch-4-4"
    out_dir.mkdir(parents=True, exist_ok=True)

    events_df = pd.DataFrame(json.loads(
        events_path.read_text(encoding="utf-8")))
    features_df = engineer_rfm_features(
        events_df, reference_ts="2026-03-08T00:00:00Z")
    result = train_kmeans_segments(features_df, cluster_options=(2, 3))
    labeled_df = label_segments_with_playbooks(result.labeled_features)

    labels_path = out_dir / "segment_labels.csv"
    labeled_df[["user_id", "cluster_id", "segment_label", "playbook"]].to_csv(
        labels_path, index=False, encoding="utf-8")

    summary = {
        "selected_k": result.selected_k,
        "silhouette": result.silhouette,
        "stability": result.stability,
        "segment_counts": labeled_df["segment_label"].value_counts().to_dict(),
        "segment_labels_path": str(labels_path.relative_to(base_dir)),
    }

    summary_path = out_dir / "behavioral_segmentation_summary.json"
    summary_path.write_text(json.dumps(
        summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
