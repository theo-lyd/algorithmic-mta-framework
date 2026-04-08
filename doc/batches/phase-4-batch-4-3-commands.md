# Phase 4 Batch 4.3 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Run propensity tests
- `PYTHONPATH=. python -m unittest tests/phase4/test_propensity_model.py`
- Expected: feature-store and model training tests pass.

2. Run propensity validator
- `PYTHONPATH=. python ingestion/pipeline/validate_propensity_model.py`
- Expected: summary JSON and holdout prediction CSV written to `artifacts/phase-4/batch-4-3/`.
