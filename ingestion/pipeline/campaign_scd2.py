"""Batch 3.1 campaign SCD2 and point-in-time join helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class SCD2BuildResult:
    campaign_scd2: pd.DataFrame


def build_campaign_scd2(changes_df: pd.DataFrame) -> SCD2BuildResult:
    """Build SCD Type 2 campaign windows from change records.

    Required input columns:
    - campaign_id
    - effective_from
    - owner_name
    - budget_eur
    - taxonomy_l1
    - taxonomy_l2
    """
    work = changes_df.copy()
    work["effective_from"] = pd.to_datetime(work["effective_from"], utc=True)
    work = work.sort_values(
        ["campaign_id", "effective_from"]).reset_index(drop=True)

    work["valid_from"] = work["effective_from"]
    work["valid_to"] = work.groupby("campaign_id")["effective_from"].shift(-1)
    work["is_current"] = work["valid_to"].isna()

    cols = [
        "campaign_id",
        "valid_from",
        "valid_to",
        "is_current",
        "owner_name",
        "budget_eur",
        "taxonomy_l1",
        "taxonomy_l2",
    ]
    return SCD2BuildResult(campaign_scd2=work[cols])


def point_in_time_join(events_df: pd.DataFrame, campaign_scd2_df: pd.DataFrame) -> pd.DataFrame:
    """Join events to campaign attributes valid at event timestamp.

    Join logic:
    - event_timestamp >= valid_from
    - event_timestamp < valid_to OR valid_to is null
    """
    events = events_df.copy()
    events["event_timestamp"] = pd.to_datetime(
        events["event_timestamp"], utc=True)
    scd2 = campaign_scd2_df.copy()

    merged = events.merge(scd2, on="campaign_id", how="left")
    matched = merged[
        (merged["event_timestamp"] >= merged["valid_from"])
        & (
            merged["valid_to"].isna()
            | (merged["event_timestamp"] < merged["valid_to"])
        )
    ].copy()

    # One event should map to one window for stable SCD2 history semantics.
    matched = matched.sort_values(["event_id", "valid_from"]).drop_duplicates(
        subset=["event_id"], keep="last")
    return matched.reset_index(drop=True)


def summarize_scd2_changes(campaign_scd2_df: pd.DataFrame) -> dict[str, Any]:
    return {
        "campaign_rows": int(campaign_scd2_df.shape[0]),
        "campaign_ids": int(campaign_scd2_df["campaign_id"].nunique()),
        "current_rows": int(campaign_scd2_df["is_current"].sum()),
        "historical_rows": int((~campaign_scd2_df["is_current"]).sum()),
    }
