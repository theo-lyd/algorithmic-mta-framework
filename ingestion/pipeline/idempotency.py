"""Idempotency and dedup helpers for ingestion pipelines.

Batch 1.1 deliverable: provides deterministic idempotency key generation and
in-memory dedup resolution that mirrors SQL window logic used downstream.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class IngestionRecord:
    source_name: str
    source_event_id: str
    actor_id: str
    cursor_ts: datetime
    source_file_id: str
    payload: dict


def _to_utc_iso(ts: datetime) -> str:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    else:
        ts = ts.astimezone(timezone.utc)
    return ts.isoformat()


def build_idempotency_key(record: IngestionRecord) -> str:
    """Build a deterministic SHA-256 idempotency key from canonical fields."""
    canonical = "|".join(
        [
            record.source_name.strip().lower(),
            record.source_event_id.strip(),
            _to_utc_iso(record.cursor_ts),
            record.actor_id.strip(),
        ]
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def deduplicate_records(records: Iterable[IngestionRecord]) -> List[IngestionRecord]:
    """Deduplicate by idempotency key using latest cursor_ts then source_file_id."""
    winner_by_key: dict[str, IngestionRecord] = {}
    for rec in records:
        key = build_idempotency_key(rec)
        existing: Optional[IngestionRecord] = winner_by_key.get(key)
        if existing is None:
            winner_by_key[key] = rec
            continue

        if rec.cursor_ts > existing.cursor_ts:
            winner_by_key[key] = rec
        elif rec.cursor_ts == existing.cursor_ts and rec.source_file_id > existing.source_file_id:
            winner_by_key[key] = rec

    return list(winner_by_key.values())


if __name__ == "__main__":
    base = IngestionRecord(
        source_name="ga4",
        source_event_id="evt-1",
        actor_id="u-1",
        cursor_ts=datetime(2026, 4, 8, 0, 0, 0, tzinfo=timezone.utc),
        source_file_id="f1",
        payload={"v": 1},
    )
    newer = IngestionRecord(
        source_name="ga4",
        source_event_id="evt-1",
        actor_id="u-1",
        cursor_ts=datetime(2026, 4, 8, 1, 0, 0, tzinfo=timezone.utc),
        source_file_id="f2",
        payload={"v": 2},
    )

    out = deduplicate_records([base, newer])
    print(f"deduplicated_records={len(out)}")
    print(f"idempotency_key={build_idempotency_key(newer)}")
