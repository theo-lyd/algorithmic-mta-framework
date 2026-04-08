# Batch 4.1 Heuristic Attribution Validation

Date: 2026-04-08

## Scope
Validate heuristic baseline attribution methods:
1. First-touch and last-touch allocation.
2. Linear and time-decay comparison baselines.
3. Benchmark evaluation set for model comparison.

## Validation Command
```bash
PYTHONPATH=. python ingestion/pipeline/validate_heuristic_attribution.py
```

## Results
- Conversions evaluated: 4
- Methods benchmarked: first_touch, last_touch, linear, time_decay
- Best benchmark MAE on reference set: time_decay (0.0999)

## Evidence Artifact
- `artifacts/phase-4/batch-4-1/heuristic_attribution_summary.json`
