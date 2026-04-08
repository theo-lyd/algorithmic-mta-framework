"""Batch 5.2 business-rule suite for governance checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class BusinessRuleResult:
    name: str
    success: bool
    details: dict[str, Any]


def referential_integrity_conversion_to_session(
    conversions_df: pd.DataFrame,
    sessions_df: pd.DataFrame,
) -> BusinessRuleResult:
    valid_sessions = set(sessions_df["session_id"].astype(str))
    invalid_rows = conversions_df[~conversions_df["session_id"].astype(
        str).isin(valid_sessions)]
    return BusinessRuleResult(
        name="referential_integrity_conversion_to_session",
        success=invalid_rows.empty,
        details={"invalid_rows": int(invalid_rows.shape[0])},
    )


def attribution_conservation_no_ghost_revenue(
    conversion_totals_df: pd.DataFrame,
    attributed_revenue_df: pd.DataFrame,
    tolerance: float = 1e-8,
) -> BusinessRuleResult:
    expected = float(conversion_totals_df["net_revenue_eur"].sum())
    observed = float(attributed_revenue_df["allocated_revenue_eur"].sum())
    delta = observed - expected
    return BusinessRuleResult(
        name="attribution_conservation_no_ghost_revenue",
        success=abs(delta) <= tolerance,
        details={"expected": expected, "observed": observed,
                 "delta": delta, "tolerance": tolerance},
    )


def lookback_and_session_boundary_assertions(
    attribution_rows_df: pd.DataFrame,
    max_lookback_days: int = 30,
    max_session_gap_minutes: int = 30,
) -> BusinessRuleResult:
    work = attribution_rows_df.copy()
    lookback_violation = int(
        (work["lookback_days"].astype(int) > max_lookback_days).sum())
    session_gap_violation = int(
        (work["session_gap_minutes"].astype(float) > max_session_gap_minutes).sum())
    success = lookback_violation == 0 and session_gap_violation == 0
    return BusinessRuleResult(
        name="lookback_and_session_boundary_assertions",
        success=success,
        details={
            "lookback_violation_rows": lookback_violation,
            "session_gap_violation_rows": session_gap_violation,
            "max_lookback_days": max_lookback_days,
            "max_session_gap_minutes": max_session_gap_minutes,
        },
    )


def summarize_business_rules(results: list[BusinessRuleResult]) -> dict[str, Any]:
    failed = [r for r in results if not r.success]
    return {
        "checks_total": len(results),
        "checks_failed": len(failed),
        "failed_names": [r.name for r in failed],
    }
