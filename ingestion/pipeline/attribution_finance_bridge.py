"""Batch 4.5 attribution-to-finance bridge helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd


def allocate_net_revenue(conversions_df: pd.DataFrame, attribution_df: pd.DataFrame) -> pd.DataFrame:
    conversions = conversions_df.copy()
    conversions["net_revenue_eur"] = conversions["net_revenue_eur"].astype(
        float)

    attrib = attribution_df.copy()
    if "net_revenue_eur" in attrib.columns:
        attrib = attrib.drop(columns=["net_revenue_eur"])
    attrib["attribution_weight"] = attrib["attribution_weight"].astype(float)

    # Normalize per conversion/method so allocations reconcile exactly with finance totals.
    attrib["attribution_weight"] = attrib.groupby(["method", "conversion_id"])["attribution_weight"].transform(
        lambda values: values / values.sum() if values.sum() > 0 else values
    )

    merged = attrib.merge(
        conversions[["conversion_id", "net_revenue_eur"]], on="conversion_id", how="inner")
    merged["allocated_revenue_eur"] = merged["attribution_weight"] * \
        merged["net_revenue_eur"]
    return merged.sort_values(["method", "conversion_id", "channel"]).reset_index(drop=True)


def recompute_channel_roas(allocated_df: pd.DataFrame, spend_df: pd.DataFrame) -> pd.DataFrame:
    spend = spend_df.copy()
    spend["channel_spend_eur"] = spend["channel_spend_eur"].astype(float)

    revenue = (
        allocated_df.groupby(["method", "channel"], as_index=False)[
            "allocated_revenue_eur"].sum()
        .rename(columns={"allocated_revenue_eur": "attributed_revenue_eur"})
    )
    roas = revenue.merge(spend, on="channel", how="left")
    roas["channel_spend_eur"] = roas["channel_spend_eur"].fillna(0.0)
    roas["roas"] = roas.apply(
        lambda row: float(row["attributed_revenue_eur"] /
                          row["channel_spend_eur"]) if row["channel_spend_eur"] > 0 else 0.0,
        axis=1,
    )
    return roas.sort_values(["method", "channel"]).reset_index(drop=True)


def variance_against_current(roas_df: pd.DataFrame, current_method: str = "last_touch") -> pd.DataFrame:
    base = roas_df[roas_df["method"] == current_method][[
        "channel", "roas"]].rename(columns={"roas": "baseline_roas"})
    merged = roas_df.merge(base, on="channel", how="left")
    merged["roas_delta_abs"] = merged["roas"] - merged["baseline_roas"]
    merged["roas_delta_pct"] = merged.apply(
        lambda row: float(row["roas_delta_abs"] / row["baseline_roas"]
                          ) if row["baseline_roas"] not in [0, None] else 0.0,
        axis=1,
    )
    return merged.sort_values(["method", "channel"]).reset_index(drop=True)


def reconciliation_summary(conversions_df: pd.DataFrame, allocated_df: pd.DataFrame) -> pd.DataFrame:
    total_net = float(conversions_df["net_revenue_eur"].astype(float).sum())
    grouped = allocated_df.groupby("method", as_index=False)[
        "allocated_revenue_eur"].sum()
    grouped["net_revenue_total_eur"] = total_net
    grouped["reconciliation_delta_eur"] = grouped["allocated_revenue_eur"] - total_net
    grouped["reconciled_exactly"] = grouped["reconciliation_delta_eur"].abs() < 1e-8
    return grouped.sort_values("method").reset_index(drop=True)


def summarize_finance_bridge(roas_df: pd.DataFrame, reconciliation_df: pd.DataFrame) -> dict[str, Any]:
    return {
        "methods": int(roas_df["method"].nunique()),
        "channels": int(roas_df["channel"].nunique()),
        "max_roas": float(roas_df["roas"].max()) if not roas_df.empty else 0.0,
        "reconciled_methods": int(reconciliation_df["reconciled_exactly"].sum()) if not reconciliation_df.empty else 0,
    }
