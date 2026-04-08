# Batch 1.2 Bronze Landing Validation

Date: 2026-04-08

## Execution
- Command run:
  - `python ingestion/pipeline/bronze_landing.py --input ingestion/samples/raw_nested_events.jsonl --output data/bronze/events --batch-id batch_20260408_1200`

## Expected Outcome
- Nested JSON records converted to Parquet.
- Hive partitions created by event_date and source_channel.
- Audit columns present in output schema:
  - ingestion_ts
  - batch_id
  - source_file_id

## Observed Evidence
- Parquet files materialized under:
  - data/bronze/events/event_date=2026-04-08/source_channel=search/
  - data/bronze/events/event_date=2026-04-09/source_channel=affiliate/
- Audit columns verified via pyarrow schema inspection.
