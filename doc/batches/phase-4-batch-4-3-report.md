# Phase 4 Batch 4.3 Report - Supervised Conversion Propensity Model

Status: Complete
Date: 2026-04-08
Batch: 4.3

## 1. Scope and Objective
Implement supervised predictive workflow:
- feature store for next-7-day conversion signals,
- calibrated logistic regression with imbalance handling,
- evaluation on AUC, precision-recall, lift, and calibration drift.

## 2. What Was Built
- `ingestion/pipeline/propensity_model.py`
- `tests/fixtures/phase4/customer_events.json`
- `tests/phase4/test_propensity_model.py`
- `ingestion/pipeline/validate_propensity_model.py`
- `doc/phase-4/batch-4-3-propensity-validation.md`

## 3. Acceptance Criteria Verification
- Chunk 4.3.1: met.
- Chunk 4.3.2: met.
- Chunk 4.3.3: met.

## 4. Outcome
Predictive propensity pipeline is operational with an explicit agreed lift threshold.
