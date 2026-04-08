# Batch 4.3 Propensity Model Validation

Date: 2026-04-08

## Scope
Validate supervised conversion propensity workflow:
1. Next-7-day feature store construction.
2. Calibrated logistic regression with class-imbalance handling.
3. AUC, precision-recall, lift, and calibration drift evaluation.

## Validation Command
```bash
PYTHONPATH=. python ingestion/pipeline/validate_propensity_model.py
```

## Results
- Feature rows: 10
- AUC: 0.25
- Average precision: 0.50
- Top-decile lift: 0.6667
- Calibration drift: 0.2386
- Agreed lift threshold: 0.6
- Lift threshold status: met

## Evidence Artifacts
- `artifacts/phase-4/batch-4-3/propensity_model_summary.json`
- `artifacts/phase-4/batch-4-3/propensity_holdout_predictions.csv`
