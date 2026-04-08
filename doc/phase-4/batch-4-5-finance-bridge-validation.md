# Batch 4.5 Attribution-to-Finance Bridge Validation

Date: 2026-04-08

## Scope
Validate finance bridge controls:
1. Net revenue allocation by attributed share.
2. Channel ROAS recomputation by attribution method.
3. Variance analysis against current reporting method.

## Validation Command
```bash
PYTHONPATH=. python ingestion/pipeline/validate_finance_bridge.py
```

## Results
- Methods bridged: 4
- Channels in ROAS output: 4
- Reconciled methods: 4 / 4
- Max channel ROAS: 2.5

## Evidence Artifacts
- `artifacts/phase-4/batch-4-5/finance_bridge_summary.json`
- `artifacts/phase-4/batch-4-5/channel_roas_by_method.csv`
