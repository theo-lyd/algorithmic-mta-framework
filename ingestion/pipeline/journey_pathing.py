"""Batch 3.3 journey construction and pathing logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class JourneyBuildResult:
    touchpoints: pd.DataFrame
    journeys: pd.DataFrame
    conversions: pd.DataFrame


def _prepare_events(events_df: pd.DataFrame) -> pd.DataFrame:
    work = events_df.copy()
    work["event_timestamp"] = pd.to_datetime(work["event_timestamp"], utc=True)
    work["campaign_id"] = work["campaign_id"].fillna("unknown")
    work["event_name"] = work["event_name"].fillna("unknown")
    work["is_conversion"] = work["is_conversion"].astype(bool)
    return work.sort_values(["user_pseudo_id", "event_timestamp", "event_id"]).reset_index(drop=True)


def deduplicate_touchpoints(events_df: pd.DataFrame, dedup_minutes: int = 5) -> pd.DataFrame:
    """Remove duplicate touchpoints within a short window for the same user/campaign/event_name."""
    work = _prepare_events(events_df)
    work["prev_timestamp"] = work.groupby(
        ["user_pseudo_id", "campaign_id", "event_name"])["event_timestamp"].shift(1)
    gap_minutes = (work["event_timestamp"] -
                   work["prev_timestamp"]).dt.total_seconds() / 60.0
    keep = work["prev_timestamp"].isna() | (
        gap_minutes > dedup_minutes) | work["is_conversion"]
    return work[keep].drop(columns=["prev_timestamp"]).reset_index(drop=True)


def assign_journey_sequences(events_df: pd.DataFrame, inactivity_minutes: int = 30) -> pd.DataFrame:
    """Assign deterministic journey sequences using inactivity and conversion boundaries."""
    work = _prepare_events(events_df)
    work["prev_timestamp"] = work.groupby("user_pseudo_id")[
        "event_timestamp"].shift(1)
    work["prev_is_conversion"] = work.groupby(
        "user_pseudo_id")["is_conversion"].shift(1).fillna(False)
    gap_minutes = (work["event_timestamp"] -
                   work["prev_timestamp"]).dt.total_seconds() / 60.0
    new_journey = work["prev_timestamp"].isna() | (
        gap_minutes > inactivity_minutes) | work["prev_is_conversion"]
    work["journey_seq"] = new_journey.groupby(
        work["user_pseudo_id"]).cumsum().astype(int)
    work["journey_id"] = work.apply(
        lambda row: f"{row['user_pseudo_id']}|journey-{int(row['journey_seq'])}",
        axis=1,
    )
    return work.drop(columns=["prev_timestamp", "prev_is_conversion"])


def build_touchpoints(events_df: pd.DataFrame) -> pd.DataFrame:
    deduped = deduplicate_touchpoints(events_df)
    sequenced = assign_journey_sequences(deduped)
    touchpoints = sequenced[~sequenced["is_conversion"]].copy()
    touchpoints["touchpoint_order"] = touchpoints.groupby(
        "journey_id").cumcount() + 1
    return touchpoints.reset_index(drop=True)


def build_journeys(events_df: pd.DataFrame) -> pd.DataFrame:
    sequenced = assign_journey_sequences(deduplicate_touchpoints(events_df))
    path_rows: list[dict[str, Any]] = []

    for (user_id, journey_id), group in sequenced.groupby(["user_pseudo_id", "journey_id"], sort=False):
        ordered = group.sort_values("event_timestamp")
        path_tokens = ordered["campaign_id"].tolist()
        path_names = ordered["event_name"].tolist()
        start_ts = ordered["event_timestamp"].min()
        end_ts = ordered["event_timestamp"].max()
        conversion_rows = ordered[ordered["is_conversion"]]

        path_rows.append(
            {
                "user_pseudo_id": user_id,
                "journey_id": journey_id,
                "journey_start_ts": start_ts,
                "journey_end_ts": end_ts,
                "touchpoint_count": int((~ordered["is_conversion"]).sum()),
                "conversion_count": int(conversion_rows.shape[0]),
                "journey_path": " > ".join(path_tokens),
                "event_sequence": " > ".join(path_names),
            }
        )

    journeys = pd.DataFrame(path_rows)
    if journeys.empty:
        return pd.DataFrame(columns=["user_pseudo_id", "journey_id", "journey_start_ts", "journey_end_ts", "touchpoint_count", "conversion_count", "journey_path", "event_sequence"])
    return journeys.sort_values(["user_pseudo_id", "journey_start_ts"]).reset_index(drop=True)


def build_conversion_attribution(events_df: pd.DataFrame, lookback_days: int = 30) -> pd.DataFrame:
    """Build conversion-attribution rows bounded by 30-day lookback and conversion boundaries."""
    sequenced = assign_journey_sequences(deduplicate_touchpoints(events_df))
    conversions = sequenced[sequenced["is_conversion"]].copy()
    touchpoints = sequenced[~sequenced["is_conversion"]].copy()

    rows: list[dict[str, Any]] = []
    for _, conversion in conversions.iterrows():
        user_touchpoints = touchpoints[touchpoints["user_pseudo_id"]
                                       == conversion["user_pseudo_id"]]
        window_start = conversion["event_timestamp"] - \
            timedelta(days=lookback_days)
        eligible = user_touchpoints[
            (user_touchpoints["event_timestamp"] >= window_start)
            & (user_touchpoints["event_timestamp"] < conversion["event_timestamp"])
        ].sort_values("event_timestamp")

        rows.append(
            {
                "conversion_event_id": conversion["event_id"],
                "user_pseudo_id": conversion["user_pseudo_id"],
                "conversion_ts": conversion["event_timestamp"],
                "journey_id": conversion["journey_id"],
                "lookback_days": lookback_days,
                "attribution_path": " > ".join(eligible["campaign_id"].tolist()),
                "lookback_touchpoints": int(eligible.shape[0]),
                "conversion_boundary_event_id": conversion["event_id"],
            }
        )

    result = pd.DataFrame(rows)
    if result.empty:
        return pd.DataFrame(columns=["conversion_event_id", "user_pseudo_id", "conversion_ts", "journey_id", "lookback_days", "attribution_path", "lookback_touchpoints", "conversion_boundary_event_id"])
    return result.sort_values(["user_pseudo_id", "conversion_ts"]).reset_index(drop=True)


def summarize_journey_build(touchpoints_df: pd.DataFrame, journeys_df: pd.DataFrame, conversions_df: pd.DataFrame) -> dict[str, Any]:
    return {
        "touchpoints_rows": int(touchpoints_df.shape[0]),
        "journey_rows": int(journeys_df.shape[0]),
        "conversion_rows": int(conversions_df.shape[0]),
        "unique_journeys": int(journeys_df["journey_id"].nunique()) if not journeys_df.empty else 0,
        "lookback_window_days": 30,
    }
