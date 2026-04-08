"""Batch 1.2 Bronze landing pipeline.

Converts raw nested JSON events into partitioned Parquet with required
audit columns:
- ingestion_ts
- batch_id
- source_file_id

Partitioning strategy:
- event_date
- source_channel
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds


def _flatten_event(row: dict[str, Any], batch_id: str, ingestion_ts: datetime) -> dict[str, Any]:
    event_ts = pd.to_datetime(row["event_timestamp"], utc=True)
    flattened = {
        "source_name": row["source_name"],
        "event_id": row["event_id"],
        "event_timestamp": event_ts,
        "event_date": event_ts.strftime("%Y-%m-%d"),
        "event_name": row.get("event_name"),
        "user_pseudo_id": row.get("user_pseudo_id"),
        "source_channel": row.get("source_channel", "unknown"),
        # Keep nested payload as JSON string in Bronze for lossless capture.
        "event_params_json": json.dumps(row.get("event_params", {}), ensure_ascii=True),
        "ingestion_ts": ingestion_ts,
        "batch_id": batch_id,
        "source_file_id": row.get("source_file_id", "unknown"),
    }
    return flattened


def convert_jsonl_to_bronze(input_path: Path, output_root: Path, batch_id: str) -> int:
    ingestion_ts = datetime.now(timezone.utc)
    rows: list[dict[str, Any]] = []

    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            raw = json.loads(line)
            rows.append(_flatten_event(raw, batch_id=batch_id, ingestion_ts=ingestion_ts))

    if not rows:
        return 0

    df = pd.DataFrame(rows)
    table = pa.Table.from_pandas(df, preserve_index=False)

    ds.write_dataset(
        data=table,
        base_dir=str(output_root),
        format="parquet",
        partitioning=ds.partitioning(pa.schema([
            ("event_date", pa.string()),
            ("source_channel", pa.string()),
        ]), flavor="hive"),
        existing_data_behavior="overwrite_or_ignore",
    )

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bronze landing JSONL -> partitioned Parquet")
    parser.add_argument("--input", required=True, help="Path to raw JSONL input")
    parser.add_argument("--output", required=True, help="Path to bronze output root")
    parser.add_argument("--batch-id", required=True, help="Ingestion batch id")
    args = parser.parse_args()

    count = convert_jsonl_to_bronze(
        input_path=Path(args.input),
        output_root=Path(args.output),
        batch_id=args.batch_id,
    )
    print(f"bronze_rows_written={count}")


if __name__ == "__main__":
    main()
