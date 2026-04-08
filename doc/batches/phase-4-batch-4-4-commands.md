# Phase 4 Batch 4.4 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Run segmentation tests
- `PYTHONPATH=. python -m unittest tests/phase4/test_behavioral_segmentation.py`
- Expected: RFM engineering and clustering tests pass.

2. Run segmentation validator
- `PYTHONPATH=. python ingestion/pipeline/validate_behavioral_segmentation.py`
- Expected: segmentation summary JSON and labels CSV written to `artifacts/phase-4/batch-4-4/`.
