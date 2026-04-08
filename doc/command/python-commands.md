# Python Commands Reference (Living Document)

Status: Active
Last Updated: 2026-04-08
Coverage: Phase 0 to Phase 4.5

## Purpose
Track all Python commands used in project setup, validation, and ingestion pipeline execution.

## Update Protocol
- Append exact command with batch context.
- Add one-line purpose for each command.

## Commands Used So Far
- python --version
- python -c "import csv, pathlib, typing; print('All stdlib modules available')"
- python -c "import csv; print('csv module available')"
- python scripts/generate_jira_csv.py
- python ingestion/pipeline/idempotency.py
- python ingestion/pipeline/bronze_landing.py --input ingestion/samples/raw_nested_events.jsonl --output data/bronze/events --batch-id batch_20260408_1200
- python ingestion/pipeline/validate_observability.py
- python ingestion/pipeline/bronze_landing.py --input ingestion/samples/raw_nested_events.jsonl --output artifacts/phase-1/gate-closure/bronze_output --batch-id phase1_gate_20260408 > artifacts/phase-1/gate-closure/bronze_run.txt
- PYTHONPATH=. python <inline gate summary script for bronze schema/partitions>
- PYTHONPATH=. python <inline gate summary script for replay validation>
- PYTHONPATH=. python -m unittest discover -s tests/phase2 -p 'test_*.py'
- PYTHONPATH=. python ingestion/pipeline/validate_text_normalization.py
- PYTHONPATH=. python ingestion/pipeline/validate_financial_normalization.py
- PYTHONPATH=. python ingestion/pipeline/validate_silver_harmonization.py
- PYTHONPATH=. python ingestion/pipeline/validate_silver_contracts.py
- PYTHONPATH=. python ingestion/pipeline/validate_campaign_scd2.py
- PYTHONPATH=. python ingestion/pipeline/validate_identity_harmonization.py
- PYTHONPATH=. python ingestion/pipeline/validate_journey_pathing.py
- PYTHONPATH=. python ingestion/pipeline/validate_heuristic_attribution.py
- PYTHONPATH=. python ingestion/pipeline/validate_markov_attribution.py
- PYTHONPATH=. python ingestion/pipeline/validate_propensity_model.py
- PYTHONPATH=. python ingestion/pipeline/validate_behavioral_segmentation.py
- PYTHONPATH=. python ingestion/pipeline/validate_finance_bridge.py

## Typical Patterns
- Module validation:
  - python <module_or_script>.py
- Inline verification scripts:
  - PYTHONPATH=. python - <<'PY'
    ...
    PY

## Next Update Hook
After each successful batch, append new Python commands and map to evidence artifacts.
