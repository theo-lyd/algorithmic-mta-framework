# Batch 2.4 Data Quality Contracts

## Scope
Implements the following Phase 2.4 controls:
1. Great Expectations suite/checkpoint artifacts for nulls, ranges, uniqueness, referential integrity.
2. Contract tests for required fields and schema drift detection.
3. Failed-record quarantine and remediation workflow.

## Great Expectations Artifacts
- Suite: `quality/great_expectations/suites/silver_events_quality_suite.json`
- Checkpoint: `quality/great_expectations/checkpoints/silver_quality_checkpoint.yml`

## Contract Rules
- Required event fields must exist and be non-null.
- Canonical silver table schemas must match expected columns.
- Event IDs must be unique.
- Session event counts must be within valid range (`>= 1`).
- Referential integrity:
  - event_params.event_id -> events.event_id
  - event_items.event_id -> events.event_id
  - dim_campaign.source_channel -> dim_channel.source_channel

## Quarantine Workflow
- Detect failed rows (example: missing required event_id).
- Write failed records to append-only quarantine JSONL.
- Emit remediation candidate CSV for operational fix flow.

## Implementation References
- `quality/contracts/silver_contracts.py`
- `quality/contracts/quarantine.py`
- `ingestion/pipeline/validate_silver_contracts.py`
