"""Batch 2.4 silver quality contracts and schema drift checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


REQUIRED_EVENT_FIELDS = [
    "event_id",
    "event_timestamp",
    "user_pseudo_id",
    "source_channel",
    "session_id",
]

EXPECTED_SCHEMAS = {
    "events": [
        "event_id",
        "source_name",
        "source_file_id",
        "event_name",
        "event_timestamp",
        "event_date",
        "user_pseudo_id",
        "source_channel",
        "campaign_name",
        "device_type",
        "device_os",
        "country_code",
        "country_name",
        "city_name",
        "session_seq",
        "session_start_ts",
        "session_id",
    ],
    "event_params": ["event_id", "param_key", "param_value"],
    "event_items": ["event_id", "item_index", "item_id", "item_name", "item_category", "quantity", "price"],
    "sessions": ["session_id", "user_pseudo_id", "session_start_ts", "session_end_ts", "event_count"],
    "dim_channel": ["channel_id", "source_channel"],
    "dim_campaign": ["campaign_id", "campaign_name", "source_channel"],
    "dim_device": ["device_id", "device_type", "device_os"],
    "dim_geography": ["geo_id", "country_code", "country_name", "city_name"],
}


@dataclass(frozen=True)
class ContractResult:
    name: str
    success: bool
    details: dict[str, Any]


def required_fields_check(events_df: pd.DataFrame) -> ContractResult:
    missing_columns = [
        c for c in REQUIRED_EVENT_FIELDS if c not in events_df.columns]
    if missing_columns:
        return ContractResult(
            name="required_fields_check",
            success=False,
            details={"missing_columns": missing_columns},
        )

    null_counts = {c: int(events_df[c].isna().sum())
                   for c in REQUIRED_EVENT_FIELDS}
    failed = {k: v for k, v in null_counts.items() if v > 0}
    return ContractResult(
        name="required_fields_check",
        success=len(failed) == 0,
        details={"null_counts": null_counts, "failing_columns": failed},
    )


def schema_drift_check(table_name: str, df: pd.DataFrame) -> ContractResult:
    expected = EXPECTED_SCHEMAS[table_name]
    current = list(df.columns)
    missing = [c for c in expected if c not in current]
    unexpected = [c for c in current if c not in expected]
    return ContractResult(
        name=f"schema_drift_check:{table_name}",
        success=(len(missing) == 0 and len(unexpected) == 0),
        details={"missing_columns": missing, "unexpected_columns": unexpected},
    )


def null_uniqueness_range_checks(events_df: pd.DataFrame, sessions_df: pd.DataFrame) -> list[ContractResult]:
    results: list[ContractResult] = []

    null_counts = {
        "event_id": int(events_df["event_id"].isna().sum()),
        "event_timestamp": int(events_df["event_timestamp"].isna().sum()),
        "user_pseudo_id": int(events_df["user_pseudo_id"].isna().sum()),
        "source_channel": int(events_df["source_channel"].isna().sum()),
    }
    results.append(
        ContractResult(
            name="ge_null_checks",
            success=all(v == 0 for v in null_counts.values()),
            details={"null_counts": null_counts},
        )
    )

    duplicate_events = int(events_df["event_id"].duplicated().sum())
    results.append(
        ContractResult(
            name="ge_uniqueness_checks",
            success=duplicate_events == 0,
            details={"duplicate_event_id_rows": duplicate_events},
        )
    )

    invalid_event_count_rows = int((sessions_df["event_count"] < 1).sum())
    results.append(
        ContractResult(
            name="ge_range_checks",
            success=invalid_event_count_rows == 0,
            details={"invalid_event_count_rows": invalid_event_count_rows},
        )
    )

    return results


def referential_integrity_checks(
    events_df: pd.DataFrame,
    event_params_df: pd.DataFrame,
    event_items_df: pd.DataFrame,
    dim_channel_df: pd.DataFrame,
    dim_campaign_df: pd.DataFrame,
) -> list[ContractResult]:
    results: list[ContractResult] = []

    event_ids = set(events_df["event_id"].astype(str))
    params_orphans = int(
        (~event_params_df["event_id"].astype(str).isin(event_ids)).sum())
    items_orphans = int(
        (~event_items_df["event_id"].astype(str).isin(event_ids)).sum())

    results.append(
        ContractResult(
            name="ge_referential_event_params",
            success=params_orphans == 0,
            details={"orphan_param_rows": params_orphans},
        )
    )
    results.append(
        ContractResult(
            name="ge_referential_event_items",
            success=items_orphans == 0,
            details={"orphan_item_rows": items_orphans},
        )
    )

    channel_set = set(dim_channel_df["source_channel"].astype(str))
    campaign_invalid = int(
        (~dim_campaign_df["source_channel"].astype(str).isin(channel_set)).sum())
    results.append(
        ContractResult(
            name="ge_referential_campaign_channel",
            success=campaign_invalid == 0,
            details={"invalid_campaign_channel_rows": campaign_invalid},
        )
    )

    return results
