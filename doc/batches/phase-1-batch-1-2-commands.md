# Phase 1 Batch 1.2 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Baseline inspection
- Commands:
  - git status --short
  - find ingestion -maxdepth 4 -type f
- Expected:
  - Verify pre-batch ingestion file set.

2. Create implementation artifacts
- Commands:
  - create_directory ingestion/samples
  - create_file ingestion/pipeline/bronze_landing.py
  - create_file ingestion/samples/raw_nested_events.jsonl
  - create_file ingestion/contracts/bronze_partition_strategy.md
- Expected:
  - Bronze landing implementation and strategy docs available.

3. Run bronze landing pipeline
- Command:
  - python ingestion/pipeline/bronze_landing.py --input ingestion/samples/raw_nested_events.jsonl --output data/bronze/events --batch-id batch_20260408_1200
- Expected:
  - Output includes `bronze_rows_written=3`.

4. Validate partition layout
- Command:
  - find data/bronze/events -maxdepth 4 -type f | sort
- Expected:
  - Partitioned files under event_date=<...>/source_channel=<...>/part-0.parquet

5. Validate audit columns
- Command:
  - python pyarrow schema inspection script
- Expected:
  - `audit_columns_present=True`

6. Create batch validation and docs
- Commands:
  - create_file doc/phase-1/batch-1-2-bronze-validation.md
  - create_file doc/batches/phase-1-batch-1-2-report.md
  - create_file doc/batches/phase-1-batch-1-2-commands.md
- Expected:
  - Batch evidence and documentation complete.

7. Update README index
- Command:
  - patch README.md to add Batch 1.2 links
- Expected:
  - Phase 1 artifacts include Batch 1.2 navigation.

8. Commit and push
- Commands:
  - git add ...
  - git commit ...
  - git push origin master
- Expected:
  - Atomic commits published to origin/master.
