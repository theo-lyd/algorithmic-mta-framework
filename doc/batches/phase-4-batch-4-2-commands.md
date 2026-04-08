# Phase 4 Batch 4.2 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Run Markov tests
- `PYTHONPATH=. python -m unittest tests/phase4/test_markov_attribution.py`
- Expected: transition and removal-effect tests pass.

2. Run Markov validator
- `PYTHONPATH=. python ingestion/pipeline/validate_markov_attribution.py`
- Expected: Markov summary JSON written to `artifacts/phase-4/batch-4-2/`.
