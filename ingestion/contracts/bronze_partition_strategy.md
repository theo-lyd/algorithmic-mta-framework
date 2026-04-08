# Bronze Partition and Audit Strategy (Batch 1.2)

## Partition Strategy
- Partition keys:
  - event_date (YYYY-MM-DD)
  - source_channel
- Path format (hive style):
  - data/bronze/events/event_date=2026-04-08/source_channel=search/

## Why This Partitioning
| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| event_date + source_channel | event_date only; source_name only | Aligns with replay windows and channel-focused reporting | More partitions to manage | Query profile shifts away from channel/date access patterns |

## Required Audit Columns
- ingestion_ts: UTC timestamp when pipeline landed record.
- batch_id: deterministic run identifier for replay and rollback.
- source_file_id: upstream file/page identifier for traceability.

## Dedup and Replay Compatibility
- Partitioning by event_date allows selective replay for impacted windows.
- source_file_id + batch_id support run-level reconciliation.
