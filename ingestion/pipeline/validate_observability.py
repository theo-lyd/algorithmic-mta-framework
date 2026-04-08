"""Batch 1.4 validation runner for ingestion observability controls."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingestion.pipeline.dead_letter import emit_failure_alert, write_dead_letter
from ingestion.pipeline.observability import anomaly_baseline, freshness_check


def main() -> None:
    base_dir = ROOT
    sample_csv = base_dir / "ingestion" / "samples" / "event_count_history.csv"

    validation_dir = base_dir / "artifacts" / "phase-1" / "batch-1-4"
    validation_dir.mkdir(parents=True, exist_ok=True)

    dead_letter_file = validation_dir / "dead_letter_events.jsonl"
    alert_file = validation_dir / "alerts.jsonl"
    summary_file = validation_dir / "observability_summary.json"

    for artifact_file in [dead_letter_file, alert_file, summary_file]:
        if artifact_file.exists():
            artifact_file.unlink()

    now = datetime(2026, 4, 8, 12, 0, tzinfo=timezone.utc)
    last_event_ts = datetime(2026, 4, 8, 11, 20, tzinfo=timezone.utc)
    freshness = freshness_check(last_event_ts=last_event_ts, threshold_minutes=60, now=now)

    df = pd.read_csv(sample_csv)
    anomaly_df = anomaly_baseline(df=df, sigma_threshold=2.0)
    flagged = anomaly_df[anomaly_df["is_anomaly"]]

    write_dead_letter(
        dead_letter_path=dead_letter_file,
        source_name="ga4",
        source_file_id="ga4_2026-04-08T11",
        raw_record={"event_date": "2026-04-08", "source_channel": "search", "event_count": 450},
        error_message="Event count breached anomaly threshold; quarantined for review",
    )
    emit_failure_alert(
        alert_path=alert_file,
        title="Ingestion anomaly detected",
        severity="high",
        details="search channel event_count dropped to 450 vs baseline",
    )

    flagged_rows = flagged[["event_date", "source_channel", "event_count", "z_score"]].copy()
    flagged_rows["event_date"] = flagged_rows["event_date"].astype(str)

    summary = {
        "freshness": {
            "is_fresh": freshness.is_fresh,
            "lag_minutes": freshness.lag_minutes,
            "threshold_minutes": freshness.threshold_minutes,
        },
        "anomaly": {
            "sigma_threshold": 2.0,
            "flagged_count": int(flagged.shape[0]),
            "flagged_rows": flagged_rows.to_dict("records"),
        },
        "dead_letter_file": str(dead_letter_file.relative_to(base_dir)),
        "alert_file": str(alert_file.relative_to(base_dir)),
    }

    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
