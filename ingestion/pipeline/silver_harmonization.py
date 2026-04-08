"""Batch 2.3 JSON flattening and canonical silver schema helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class SilverTables:
    events: pd.DataFrame
    event_params: pd.DataFrame
    event_items: pd.DataFrame
    sessions: pd.DataFrame
    dim_channel: pd.DataFrame
    dim_campaign: pd.DataFrame
    dim_device: pd.DataFrame
    dim_geography: pd.DataFrame


def _dim_id(prefix: str, value: str) -> str:
    token = hashlib.md5(value.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{token}"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def build_event_fact(rows: list[dict[str, Any]]) -> pd.DataFrame:
    events = []
    for row in rows:
        ts = pd.to_datetime(row["event_timestamp"], utc=True)
        params = row.get("event_params", {})
        device = row.get("device", {})
        geo = row.get("geography", {})
        events.append(
            {
                "event_id": row["event_id"],
                "source_name": row.get("source_name", "unknown"),
                "source_file_id": row.get("source_file_id", "unknown"),
                "event_name": row.get("event_name", "unknown"),
                "event_timestamp": ts,
                "event_date": ts.strftime("%Y-%m-%d"),
                "user_pseudo_id": row.get("user_pseudo_id", "unknown"),
                "source_channel": row.get("source_channel", "unknown"),
                "campaign_name": str(params.get("campaign", "unknown")),
                "device_type": str(device.get("category", "unknown")),
                "device_os": str(device.get("os", "unknown")),
                "country_code": str(geo.get("country_code", "unknown")),
                "country_name": str(geo.get("country_name", "unknown")),
                "city_name": str(geo.get("city_name", "unknown")),
            }
        )

    out = pd.DataFrame(events)
    return out.sort_values("event_timestamp").reset_index(drop=True)


def flatten_event_params(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        for k, v in row.get("event_params", {}).items():
            records.append(
                {
                    "event_id": row["event_id"],
                    "param_key": str(k),
                    "param_value": json.dumps(v, ensure_ascii=True) if isinstance(v, (dict, list)) else str(v),
                }
            )
    if not records:
        return pd.DataFrame(columns=["event_id", "param_key", "param_value"])
    return pd.DataFrame(records)


def flatten_event_items(rows: list[dict[str, Any]]) -> pd.DataFrame:
    records = []
    for row in rows:
        for idx, item in enumerate(row.get("items", [])):
            records.append(
                {
                    "event_id": row["event_id"],
                    "item_index": idx,
                    "item_id": str(item.get("item_id", "unknown")),
                    "item_name": str(item.get("item_name", "unknown")),
                    "item_category": str(item.get("item_category", "unknown")),
                    "quantity": float(item.get("quantity", 0.0)),
                    "price": float(item.get("price", 0.0)),
                }
            )
    if not records:
        return pd.DataFrame(columns=["event_id", "item_index", "item_id", "item_name", "item_category", "quantity", "price"])
    return pd.DataFrame(records)


def sessionize_events(events_df: pd.DataFrame, inactivity_minutes: int = 30) -> pd.DataFrame:
    if events_df.empty:
        return events_df.copy()

    work = events_df.sort_values(["user_pseudo_id", "event_timestamp"]).copy()
    work["prev_event_timestamp"] = work.groupby(
        "user_pseudo_id")["event_timestamp"].shift(1)

    gap_minutes = (work["event_timestamp"] -
                   work["prev_event_timestamp"]).dt.total_seconds() / 60.0
    is_new = work["prev_event_timestamp"].isna() | (
        gap_minutes > inactivity_minutes)
    work["session_seq"] = is_new.groupby(
        work["user_pseudo_id"]).cumsum().astype(int)

    starts = (
        work.groupby(["user_pseudo_id", "session_seq"],
                     as_index=False)["event_timestamp"]
        .min()
        .rename(columns={"event_timestamp": "session_start_ts"})
    )
    work = work.merge(starts, on=["user_pseudo_id", "session_seq"], how="left")
    work["session_id"] = work.apply(
        lambda x: f"{x['user_pseudo_id']}|{x['session_start_ts'].isoformat()}",
        axis=1,
    )

    return work.drop(columns=["prev_event_timestamp"])


def build_canonical_dimensions(events_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    channel = events_df[["source_channel"]].drop_duplicates().copy()
    channel["channel_id"] = channel["source_channel"].map(
        lambda v: _dim_id("chn", str(v)))
    channel = channel[["channel_id", "source_channel"]].sort_values(
        "source_channel").reset_index(drop=True)

    campaign = events_df[["campaign_name",
                          "source_channel"]].drop_duplicates().copy()
    campaign["campaign_id"] = campaign.apply(lambda r: _dim_id(
        "cmp", f"{r['source_channel']}|{r['campaign_name']}"), axis=1)
    campaign = campaign[["campaign_id", "campaign_name", "source_channel"]].sort_values(
        ["source_channel", "campaign_name"]).reset_index(drop=True)

    device = events_df[["device_type", "device_os"]].drop_duplicates().copy()
    device["device_id"] = device.apply(lambda r: _dim_id(
        "dev", f"{r['device_type']}|{r['device_os']}"), axis=1)
    device = device[["device_id", "device_type", "device_os"]].sort_values(
        ["device_type", "device_os"]).reset_index(drop=True)

    geo = events_df[["country_code", "country_name",
                     "city_name"]].drop_duplicates().copy()
    geo["geo_id"] = geo.apply(lambda r: _dim_id(
        "geo", f"{r['country_code']}|{r['country_name']}|{r['city_name']}"), axis=1)
    geo = geo[["geo_id", "country_code", "country_name", "city_name"]].sort_values(
        ["country_code", "city_name"]).reset_index(drop=True)

    return channel, campaign, device, geo


def build_silver_tables(rows: list[dict[str, Any]]) -> SilverTables:
    events = build_event_fact(rows)
    events = sessionize_events(events, inactivity_minutes=30)
    event_params = flatten_event_params(rows)
    event_items = flatten_event_items(rows)
    dim_channel, dim_campaign, dim_device, dim_geography = build_canonical_dimensions(
        events)

    sessions = (
        events.groupby(["session_id", "user_pseudo_id"], as_index=False)
        .agg(
            session_start_ts=("event_timestamp", "min"),
            session_end_ts=("event_timestamp", "max"),
            event_count=("event_id", "count"),
        )
        .sort_values(["user_pseudo_id", "session_start_ts"])
        .reset_index(drop=True)
    )

    return SilverTables(
        events=events,
        event_params=event_params,
        event_items=event_items,
        sessions=sessions,
        dim_channel=dim_channel,
        dim_campaign=dim_campaign,
        dim_device=dim_device,
        dim_geography=dim_geography,
    )
