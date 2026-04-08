# Batch 3.2 Identity Harmonization Validation

Date: 2026-04-08

## Scope
Validate Phase 3 Batch 3.2 controls:
1. Deterministic matching hierarchy across CRM and web identifiers.
2. Customer hash construction with conflict and merge rules.
3. Identity confidence score and unresolved identity queue.

## Validation Commands
```bash
PYTHONPATH=. python -m unittest discover -s tests/phase3 -p 'test_*.py'
PYTHONPATH=. python ingestion/pipeline/validate_identity_harmonization.py
```

## Results
- Phase 3 unit tests executed: 9
- Unit test result: PASS
- Validation summary:
  - resolved_rows: 3
  - unresolved_rows: 2
  - unique_customer_hashes: 2
  - avg_confidence: 0.96

## Evidence Artifacts
- `artifacts/phase-3/batch-3-2/identity_harmonization_summary.json`
- `artifacts/phase-3/batch-3-2/unresolved_identity_queue.csv`

## Key Behavioral Proof
- Shared email link merges web-only and CRM-linked records into one customer hash.
- Conflicting CRM+email linkage is sent to unresolved queue.
- Records without identifiers are quarantined in unresolved queue.
