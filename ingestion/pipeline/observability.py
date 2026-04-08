"""Batch 1.4 ingestion observability helpers.

Provides:
- freshness checks against SLA thresholds
- anomaly detection baseline for event counts
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd


@dataclass(frozen=True)
class FreshnessResult:
    is_fresh: bool
    lag_minutes: int
    threshold_minutes: int


def freshness_check(last_event_ts: datetime, threshold_minutes: int, now: datetime | None = None) -> FreshnessResult:
    if now is None:
        now = datetime.now(timezone.utc)
    if last_event_ts.tzinfo is None:
        last_event_ts = last_event_ts.replace(tzinfo=timezone.utc)

    lag = int((now - last_event_ts).total_seconds() // 60)
    return FreshnessResult(is_fresh=lag <= threshold_minutes, lag_minutes=lag, threshold_minutes=threshold_minutes)


def anomaly_baseline(df: pd.DataFrame, sigma_threshold: float = 3.0) -> pd.DataFrame:
    """Compute z-score style anomaly baseline by source_channel.

    Input requires columns:
    - event_date (YYYY-MM-DD)
    - source_channel
    - event_count
    """
    work = df.copy()
    work["event_date"] = pd.to_datetime(work["event_date"], utc=True)

    grouped = []
    for channel, part in work.groupby("source_channel", as_index=False):
        mean = part["event_count"].mean()
        std = part["event_count"].std(ddof=0)
        if std == 0:
            part["z_score"] = 0.0
        else:
            part["z_score"] = (part["event_count"] - mean) / std
        part["is_anomaly"] = part["z_score"].abs() >= sigma_threshold
        grouped.append(part)

    out = pd.concat(grouped).sort_values(["event_date", "source_channel"]).reset_index(drop=True)
    return out
