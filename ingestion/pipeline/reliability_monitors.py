"""Batch 5.1 reliability monitors and incident routing helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ReliabilityCheck:
    name: str
    success: bool
    details: dict[str, Any]


def freshness_monitor(df: pd.DataFrame, max_lag_minutes: int) -> ReliabilityCheck:
    work = df.copy()
    work["event_ts"] = pd.to_datetime(work["event_ts"], utc=True)
    latest_event_ts = work["event_ts"].max()
    now_ts = pd.to_datetime(work["observed_at"].iloc[0], utc=True)
    lag_minutes = float((now_ts - latest_event_ts).total_seconds() / 60.0)
    return ReliabilityCheck(
        name="freshness_monitor",
        success=lag_minutes <= max_lag_minutes,
        details={
            "lag_minutes": lag_minutes,
            "max_lag_minutes": max_lag_minutes,
            "latest_event_ts": str(latest_event_ts),
        },
    )


def volume_monitor(df: pd.DataFrame, drop_threshold_ratio: float = 0.5) -> ReliabilityCheck:
    work = df.copy()
    baseline = float(work["baseline_count"].mean())
    current = float(work["current_count"].iloc[-1])
    ratio = current / baseline if baseline > 0 else 0.0
    return ReliabilityCheck(
        name="volume_monitor",
        success=ratio >= drop_threshold_ratio,
        details={
            "baseline": baseline,
            "current": current,
            "ratio": ratio,
            "drop_threshold_ratio": drop_threshold_ratio,
        },
    )


def schema_monitor(actual_columns: list[str], expected_columns: list[str]) -> ReliabilityCheck:
    missing = [c for c in expected_columns if c not in actual_columns]
    unexpected = [c for c in actual_columns if c not in expected_columns]
    return ReliabilityCheck(
        name="schema_monitor",
        success=(len(missing) == 0 and len(unexpected) == 0),
        details={"missing_columns": missing, "unexpected_columns": unexpected},
    )


def distribution_monitor(
    baseline_distribution: dict[str, float],
    current_distribution: dict[str, float],
    max_l1_distance: float = 0.3,
) -> ReliabilityCheck:
    keys = sorted(set(baseline_distribution) | set(current_distribution))
    l1_distance = sum(abs(float(baseline_distribution.get(
        k, 0.0)) - float(current_distribution.get(k, 0.0))) for k in keys)
    return ReliabilityCheck(
        name="distribution_monitor",
        success=l1_distance <= max_l1_distance,
        details={"l1_distance": l1_distance,
                 "max_l1_distance": max_l1_distance},
    )


def pixel_downtime_detection(spend_eur: float, page_views: int) -> ReliabilityCheck:
    outage = spend_eur > 0 and page_views == 0
    return ReliabilityCheck(
        name="pixel_downtime_detection",
        success=not outage,
        details={
            "spend_eur": float(spend_eur),
            "page_views": int(page_views),
            "rule": "spend_active_and_page_views_zero",
        },
    )


def classify_severity(failed_checks: list[ReliabilityCheck]) -> str:
    failed_names = {check.name for check in failed_checks if not check.success}
    if "pixel_downtime_detection" in failed_names:
        return "sev-1"
    if "freshness_monitor" in failed_names or "schema_monitor" in failed_names:
        return "sev-2"
    if failed_names:
        return "sev-3"
    return "none"


def route_incident(severity: str) -> dict[str, str]:
    routing = {
        "sev-1": {
            "channel": "pagerduty-data-platform",
            "owner": "oncall-data-sre",
            "runbook": "doc/phase-5/runbook-sev1-pixel-downtime.md",
        },
        "sev-2": {
            "channel": "slack-#data-reliability",
            "owner": "analytics-engineering",
            "runbook": "doc/phase-5/runbook-sev2-freshness-schema.md",
        },
        "sev-3": {
            "channel": "jira-data-quality-queue",
            "owner": "data-quality",
            "runbook": "doc/phase-5/runbook-sev3-volume-distribution.md",
        },
    }
    return routing.get(severity, {"channel": "none", "owner": "none", "runbook": "none"})


def summarize_reliability(results: list[ReliabilityCheck]) -> dict[str, Any]:
    failed = [check for check in results if not check.success]
    severity = classify_severity(failed)
    return {
        "checks_total": len(results),
        "checks_failed": len(failed),
        "failed_names": [check.name for check in failed],
        "severity": severity,
        "routing": route_incident(severity),
    }
