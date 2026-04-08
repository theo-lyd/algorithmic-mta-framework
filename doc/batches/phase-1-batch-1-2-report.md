# Phase 1 Batch 1.2 Report: Partitioned Data Lake Landing (Bronze)

Status: Complete
Date: 2026-04-08
Batch: 1.2

## 1. Scope and Objectives
Implemented Phase I Batch 1.2:
- Chunk 1.2.1: Convert raw nested payloads to partitioned Parquet.
- Chunk 1.2.2: Apply partition strategy by event date and source channel.
- Chunk 1.2.3: Add write-audit columns for ingestion timestamp, batch id, and source file id.

## 2. What Was Built

### 2.1 Files Created
- ingestion/pipeline/bronze_landing.py
- ingestion/samples/raw_nested_events.jsonl
- ingestion/contracts/bronze_partition_strategy.md
- doc/phase-1/batch-1-2-bronze-validation.md
- doc/batches/phase-1-batch-1-2-report.md
- doc/batches/phase-1-batch-1-2-commands.md

### 2.2 Functional Outcome
- Nested JSONL events are flattened and landed to Parquet.
- Partitions materialized by event_date and source_channel.
- Audit columns verified in Parquet schema:
  - ingestion_ts
  - batch_id
  - source_file_id

## 3. Why Decisions Were Made

### 3.1 PyArrow Dataset Writer
- Why: native partitioned Parquet writes and schema control.
- Alternatives: pandas.to_parquet per file, Spark job.
- Trade-off: less distributed power than Spark, but simpler for current scope.

### 3.2 Hive-style Partitions
- Why: interoperable directory structure for replay and query pruning.
- Alternatives: custom folder naming.
- Trade-off: stricter naming discipline required.

### 3.3 JSON-in-Bronze Preservation
- Why: keep raw nested payload lossless while still flattening key fields.
- Alternatives: full flatten in Bronze.
- Trade-off: downstream parsing required for advanced fields.

## 4. Issues Encountered
- No blocking issues encountered in Batch 1.2 execution.

## 5. Acceptance Criteria Verification
- Nested payload conversion to Parquet: met.
- Partition strategy by date/channel: met.
- Audit columns added and verified: met.
- Batch docs and evidence produced: met.
- Atomic commits and push: met.

## 6. Time Taken
- Estimated: 45-75 minutes.
- Actual: approximately 55 minutes.

## 7. Dependencies Introduced
- No new dependency packages introduced.

## 8. Outcome
Batch 1.2 completed with executable bronze landing pipeline and validation evidence. Ready for Batch 1.3 late-arriving orchestration.
