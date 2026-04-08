"""Batch 1.3 late-arriving data orchestration helpers.

Implements:
- delayed partner feed detection (sensor-compatible logic)
- selective impacted-partition replay planning
- expected vs arrived reconciliation metrics
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List

import pandas as pd


@dataclass(frozen=True)
class ExpectedFile:
    source_file_id: str
    source_channel: str
    partition_date: str
    expected_rows: int


@dataclass(frozen=True)
class ArrivedFile:
    source_file_id: str
    source_channel: str
    partition_date: str
    arrived_rows: int
    arrived_at: str


def detect_delayed_files(expected: Iterable[ExpectedFile], arrived: Iterable[ArrivedFile]) -> List[ExpectedFile]:
    arrived_ids = {f.source_file_id for f in arrived}
    return [f for f in expected if f.source_file_id not in arrived_ids]


def impacted_partitions_for_replay(delayed_files: Iterable[ExpectedFile]) -> List[str]:
    partitions = {f"event_date={f.partition_date}/source_channel={f.source_channel}" for f in delayed_files}
    return sorted(partitions)


def reconciliation_summary(expected: Iterable[ExpectedFile], arrived: Iterable[ArrivedFile]) -> pd.DataFrame:
    exp_df = pd.DataFrame([e.__dict__ for e in expected])
    arr_df = pd.DataFrame([a.__dict__ for a in arrived])

    if exp_df.empty:
        return pd.DataFrame(
            [{
                "partition_date": None,
                "source_channel": None,
                "expected_rows": 0,
                "arrived_rows": 0,
                "delta_rows": 0,
            }]
        )

    if arr_df.empty:
        arr_df = pd.DataFrame(columns=["source_file_id", "source_channel", "partition_date", "arrived_rows", "arrived_at"])

    grouped_expected = (
        exp_df.groupby(["partition_date", "source_channel"], as_index=False)["expected_rows"].sum()
    )
    grouped_arrived = (
        arr_df.groupby(["partition_date", "source_channel"], as_index=False)["arrived_rows"].sum()
    )

    out = grouped_expected.merge(grouped_arrived, on=["partition_date", "source_channel"], how="left")
    out["arrived_rows"] = out["arrived_rows"].fillna(0).astype(int)
    out["delta_rows"] = out["expected_rows"] - out["arrived_rows"]
    return out.sort_values(["partition_date", "source_channel"]).reset_index(drop=True)


def parse_expected(rows: List[Dict]) -> List[ExpectedFile]:
    return [ExpectedFile(**row) for row in rows]


def parse_arrived(rows: List[Dict]) -> List[ArrivedFile]:
    # Validate arrived_at format for quality guardrail.
    parsed: List[ArrivedFile] = []
    for row in rows:
        datetime.fromisoformat(row["arrived_at"].replace("Z", "+00:00"))
        parsed.append(ArrivedFile(**row))
    return parsed
