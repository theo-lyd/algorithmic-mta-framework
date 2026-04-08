"""Batch 4.1 heuristic attribution baselines and benchmark helpers."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import numpy as np
import pandas as pd


def _prepare_events(events_df: pd.DataFrame) -> pd.DataFrame:
    work = events_df.copy()
    work["event_timestamp"] = pd.to_datetime(work["event_timestamp"], utc=True)
    work["channel"] = work["channel"].fillna("unknown")
    work["is_conversion"] = work["is_conversion"].astype(bool)
    work["conversion_id"] = work["conversion_id"].fillna("")
    work["net_revenue_eur"] = work["net_revenue_eur"].fillna(0.0).astype(float)
    return work.sort_values(["journey_id", "event_timestamp", "event_id"]).reset_index(drop=True)


def _touchpoints_for_conversion(work: pd.DataFrame, conversion_row: pd.Series, lookback_days: int) -> pd.DataFrame:
    window_start = conversion_row["event_timestamp"] - \
        timedelta(days=lookback_days)
    return work[
        (~work["is_conversion"])
        & (work["journey_id"] == conversion_row["journey_id"])
        & (work["event_timestamp"] >= window_start)
        & (work["event_timestamp"] < conversion_row["event_timestamp"])
    ].sort_values("event_timestamp")


def _build_attribution_rows(
    events_df: pd.DataFrame,
    weight_builder: callable,
    lookback_days: int = 30,
) -> pd.DataFrame:
    work = _prepare_events(events_df)
    conversions = work[work["is_conversion"]].copy()

    rows: list[dict[str, Any]] = []
    for _, conv in conversions.iterrows():
        touchpoints = _touchpoints_for_conversion(
            work, conv, lookback_days=lookback_days)
        weights = weight_builder(touchpoints)
        for channel, weight in weights.items():
            rows.append(
                {
                    "conversion_id": conv["conversion_id"] or conv["event_id"],
                    "journey_id": conv["journey_id"],
                    "channel": channel,
                    "attribution_weight": float(weight),
                    "net_revenue_eur": float(conv["net_revenue_eur"]),
                }
            )

    if not rows:
        return pd.DataFrame(columns=["conversion_id", "journey_id", "channel", "attribution_weight", "net_revenue_eur"])

    result = pd.DataFrame(rows)
    # Keep per-conversion allocations exactly normalized for reconciliation safety.
    result["attribution_weight"] = result.groupby("conversion_id")["attribution_weight"].transform(
        lambda values: values / values.sum() if values.sum() > 0 else values
    )
    return result.sort_values(["conversion_id", "channel"]).reset_index(drop=True)


def first_touch_attribution(events_df: pd.DataFrame, lookback_days: int = 30) -> pd.DataFrame:
    def weight_builder(touchpoints: pd.DataFrame) -> dict[str, float]:
        if touchpoints.empty:
            return {"unknown": 1.0}
        first_channel = str(touchpoints.iloc[0]["channel"])
        return {first_channel: 1.0}

    return _build_attribution_rows(events_df, weight_builder, lookback_days=lookback_days)


def last_touch_attribution(events_df: pd.DataFrame, lookback_days: int = 30) -> pd.DataFrame:
    def weight_builder(touchpoints: pd.DataFrame) -> dict[str, float]:
        if touchpoints.empty:
            return {"unknown": 1.0}
        last_channel = str(touchpoints.iloc[-1]["channel"])
        return {last_channel: 1.0}

    return _build_attribution_rows(events_df, weight_builder, lookback_days=lookback_days)


def linear_attribution(events_df: pd.DataFrame, lookback_days: int = 30) -> pd.DataFrame:
    def weight_builder(touchpoints: pd.DataFrame) -> dict[str, float]:
        if touchpoints.empty:
            return {"unknown": 1.0}
        channels = touchpoints["channel"].astype(str).tolist()
        weight = 1.0 / len(channels)
        weighted: dict[str, float] = {}
        for channel in channels:
            weighted[channel] = weighted.get(channel, 0.0) + weight
        return weighted

    return _build_attribution_rows(events_df, weight_builder, lookback_days=lookback_days)


def time_decay_attribution(events_df: pd.DataFrame, lookback_days: int = 30, half_life_days: float = 7.0) -> pd.DataFrame:
    decay_lambda = np.log(2.0) / max(half_life_days, 1e-6)

    def weight_builder(touchpoints: pd.DataFrame) -> dict[str, float]:
        if touchpoints.empty:
            return {"unknown": 1.0}
        last_ts = touchpoints["event_timestamp"].max()
        age_days = (
            last_ts - touchpoints["event_timestamp"]).dt.total_seconds() / 86400.0
        raw_weights = np.exp(-decay_lambda * age_days)
        total = float(raw_weights.sum())
        normalized = raw_weights / \
            total if total > 0 else np.ones_like(
                raw_weights) / len(raw_weights)

        weighted: dict[str, float] = {}
        for channel, weight in zip(touchpoints["channel"].astype(str), normalized):
            weighted[channel] = weighted.get(channel, 0.0) + float(weight)
        return weighted

    return _build_attribution_rows(events_df, weight_builder, lookback_days=lookback_days)


def aggregate_channel_shares(attribution_df: pd.DataFrame, method: str) -> pd.DataFrame:
    work = attribution_df.copy()
    summary = work.groupby("channel", as_index=False)[
        "attribution_weight"].sum()
    total = float(summary["attribution_weight"].sum())
    summary["share_pct"] = summary["attribution_weight"] / \
        total if total > 0 else 0.0
    summary["attributed_conversions"] = summary["attribution_weight"]
    summary["method"] = method
    return summary[["method", "channel", "attributed_conversions", "share_pct"]].sort_values("channel").reset_index(drop=True)


def build_benchmark_evaluation_set(
    benchmark_reference_df: pd.DataFrame,
    method_outputs: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Compare model outputs with a benchmark reference distribution.

    Reference columns:
    - conversion_id
    - channel
    - true_weight
    """
    reference = benchmark_reference_df.copy()
    reference["true_weight"] = reference["true_weight"].astype(float)

    rows: list[dict[str, Any]] = []
    for method_name, output_df in method_outputs.items():
        aligned = reference.merge(
            output_df[["conversion_id", "channel", "attribution_weight"]],
            on=["conversion_id", "channel"],
            how="left",
        )
        aligned["attribution_weight"] = aligned["attribution_weight"].fillna(
            0.0)
        abs_error = (aligned["attribution_weight"] -
                     aligned["true_weight"]).abs()
        sq_error = (aligned["attribution_weight"] -
                    aligned["true_weight"]) ** 2

        rows.append(
            {
                "method": method_name,
                "mae": float(abs_error.mean()),
                "rmse": float(np.sqrt(sq_error.mean())),
                "max_abs_error": float(abs_error.max()),
            }
        )

    return pd.DataFrame(rows).sort_values("mae").reset_index(drop=True)
