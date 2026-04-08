# Phase 1 Batch 1.5 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Re-run Bronze landing for gate evidence
- Command:
  - python ingestion/pipeline/bronze_landing.py --input ingestion/samples/raw_nested_events.jsonl --output artifacts/phase-1/gate-closure/bronze_output --batch-id phase1_gate_20260408 > artifacts/phase-1/gate-closure/bronze_run.txt
- Expected:
  - `bronze_rows_written` is greater than 0.

2. Validate Bronze output schema/partitions
- Command:
  - PYTHONPATH=. python (gate summary script) -> artifacts/phase-1/gate-closure/bronze_summary.json
- Expected:
  - `required_audit_columns_present: true`
  - `partition_columns_present: true`

3. Re-run replay logic evidence
- Command:
  - PYTHONPATH=. python (replay summary script) -> artifacts/phase-1/gate-closure/replay_summary.json
- Expected:
  - Delayed files detected and impacted partition list returned.

4. Re-run observability checks
- Command:
  - python ingestion/pipeline/validate_observability.py > artifacts/phase-1/gate-closure/observability_run.json
- Expected:
  - `freshness.is_fresh: true` with anomaly and alert/dead-letter outputs.

5. Create closure docs
- Commands:
  - create doc/phase-1/phase-1-gate-check-report.md
  - create doc/batches/phase-1-batch-1-5-closure-report.md
  - create doc/batches/phase-1-batch-1-5-commands.md
- Expected:
  - Closure artifacts complete and internally consistent.

6. Update README index
- Command:
  - patch README.md to include Batch 1.5 closure links
- Expected:
  - README includes gate-check and closure artifacts for Phase 1.

7. Commit and push
- Commands:
  - git add ...
  - git commit -m "... why ..."
  - git push origin master
- Expected:
  - Closure batch commits published to origin/master.
