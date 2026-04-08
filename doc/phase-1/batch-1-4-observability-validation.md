# Batch 1.4 Observability Validation Evidence

## Scope
Validate Phase 1 Batch 1.4 controls:
1. Freshness SLA check.
2. Anomaly baseline and flagging.
3. Dead-letter and failure alert path.

## Validation Command
```bash
python ingestion/pipeline/validate_observability.py
```

## Evidence Summary
- Freshness result: pass.
  - lag_minutes: 40
  - threshold_minutes: 60
  - is_fresh: true
- Anomaly baseline result: pass.
  - sigma_threshold: 2.0
  - flagged_count: 1
  - flagged row: search channel on 2026-04-08 with count=450 and z_score=-2.6304933255561975
- Dead-letter routing result: pass.
  - Output file: `artifacts/phase-1/batch-1-4/dead_letter_events.jsonl`
  - Contains quarantined anomaly event payload.
- Failure alerting result: pass.
  - Output file: `artifacts/phase-1/batch-1-4/alerts.jsonl`
  - Contains high-severity alert event for anomaly breach.

## Artifact Files
- `artifacts/phase-1/batch-1-4/observability_summary.json`
- `artifacts/phase-1/batch-1-4/dead_letter_events.jsonl`
- `artifacts/phase-1/batch-1-4/alerts.jsonl`

## Why This Validation Is Sufficient
- It proves SLA freshness logic with deterministic timestamps.
- It proves anomaly detection against a baseline with an intentional outlier.
- It proves failure routing behavior by persisting both dead-letter and alert outputs.
