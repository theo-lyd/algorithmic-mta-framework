"""Batch 5.4 performance profiling and cost baseline helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd


def profile_queries(query_runs_df: pd.DataFrame) -> pd.DataFrame:
    work = query_runs_df.copy()
    grouped = (
        work.groupby("query_name", as_index=False)
        .agg(
            avg_runtime_seconds=("runtime_seconds", "mean"),
            p95_runtime_seconds=(
                "runtime_seconds", lambda s: float(s.quantile(0.95))),
            avg_scanned_gb=("scanned_gb", "mean"),
            runs=("query_name", "count"),
        )
        .sort_values("p95_runtime_seconds", ascending=False)
        .reset_index(drop=True)
    )
    return grouped


def materialization_tuning_recommendations(profile_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in profile_df.iterrows():
        recommendation = "keep_table"
        if row["p95_runtime_seconds"] > 120:
            recommendation = "incremental_partitioned"
        elif row["avg_runtime_seconds"] < 10 and row["avg_scanned_gb"] < 0.5:
            recommendation = "view"
        rows.append(
            {
                "query_name": row["query_name"],
                "recommendation": recommendation,
                "p95_runtime_seconds": float(row["p95_runtime_seconds"]),
                "avg_scanned_gb": float(row["avg_scanned_gb"]),
            }
        )
    return pd.DataFrame(rows).sort_values("query_name").reset_index(drop=True)


def incremental_strategy_optimization(partition_stats_df: pd.DataFrame) -> pd.DataFrame:
    work = partition_stats_df.copy()
    work["recommended_strategy"] = work.apply(
        lambda row: "merge_on_partition"
        if row["partition_rows"] >= 1_000_000 or row["late_arrival_pct"] > 0.05
        else "append_only",
        axis=1,
    )
    return work.sort_values("partition_date").reset_index(drop=True)


def cost_dashboard(cost_df: pd.DataFrame, monthly_budget_eur: float) -> dict[str, Any]:
    work = cost_df.copy()
    total_cost = float(work["cost_eur"].sum())
    pct_of_budget = total_cost / \
        float(monthly_budget_eur) if monthly_budget_eur > 0 else 0.0
    by_component = (
        work.groupby("component", as_index=False)[
            "cost_eur"].sum().sort_values("cost_eur", ascending=False)
    )
    return {
        "monthly_budget_eur": float(monthly_budget_eur),
        "total_cost_eur": total_cost,
        "pct_of_budget": pct_of_budget,
        "by_component": by_component.to_dict("records"),
    }


def threshold_alerts(cost_dashboard_summary: dict[str, Any], budget_threshold: float = 0.85) -> dict[str, Any]:
    pct = float(cost_dashboard_summary.get("pct_of_budget", 0.0))
    return {
        "threshold": budget_threshold,
        "pct_of_budget": pct,
        "alert_triggered": pct >= budget_threshold,
        "severity": "high" if pct >= 1.0 else ("medium" if pct >= budget_threshold else "none"),
    }
