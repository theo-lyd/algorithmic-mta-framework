# Batch 5.1 Reliability Validation

Date: 2026-04-08

## Scope
Validate reliability controls for freshness, volume, schema, distribution, pixel downtime, and incident routing.

## Validation Command
```bash
PYTHONPATH=. python ingestion/pipeline/validate_reliability_monitors.py
```

## Results
- Checks total: 5
- Failed checks: 1 (pixel downtime rule)
- Derived severity: sev-1
- Incident routing owner: oncall-data-sre

## Evidence Artifact
- `artifacts/phase-5/batch-5-1/reliability_summary.json`
