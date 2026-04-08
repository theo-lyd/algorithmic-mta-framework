# Phase 4 Batch 4.1 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Run heuristic tests
- `PYTHONPATH=. python -m unittest tests/phase4/test_heuristic_attribution.py`
- Expected: heuristic attribution tests pass.

2. Run heuristic validator
- `PYTHONPATH=. python ingestion/pipeline/validate_heuristic_attribution.py`
- Expected: benchmark summary JSON written to `artifacts/phase-4/batch-4-1/`.
