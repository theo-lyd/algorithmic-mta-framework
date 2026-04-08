# Phase 4 Batch 4.1 Report - Heuristic Baseline Models

Status: Complete
Date: 2026-04-08
Batch: 4.1

## 1. Scope and Objective
Implement baseline attribution methods for controlled model comparison:
- first-touch and last-touch,
- linear and time-decay,
- benchmark evaluation set for method scoring.

## 2. What Was Built
- `ingestion/pipeline/heuristic_attribution.py`
- `tests/fixtures/phase4/attribution_events.json`
- `tests/fixtures/phase4/benchmark_reference.json`
- `tests/phase4/test_heuristic_attribution.py`
- `ingestion/pipeline/validate_heuristic_attribution.py`
- `doc/phase-4/batch-4-1-heuristic-validation.md`

## 3. Acceptance Criteria Verification
- Chunk 4.1.1: met.
- Chunk 4.1.2: met.
- Chunk 4.1.3: met.

## 4. Outcome
Heuristic benchmark baselines are now deterministic and comparison-ready.
