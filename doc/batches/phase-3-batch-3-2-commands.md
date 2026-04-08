# Phase 3 Batch 3.2 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Run Phase 3 tests
- Command:
  - `PYTHONPATH=. python -m unittest discover -s tests/phase3 -p 'test_*.py'`
- Expected:
  - All Phase 3 tests pass.

2. Run identity harmonization validation
- Command:
  - `PYTHONPATH=. python ingestion/pipeline/validate_identity_harmonization.py`
- Expected:
  - JSON summary generated with resolved/unresolved counts.
  - Unresolved queue CSV generated.

3. Create batch docs
- Commands:
  - create `doc/phase-3/batch-3-2-identity-harmonization-validation.md`
  - create `doc/batches/phase-3-batch-3-2-report.md`
  - create `doc/batches/phase-3-batch-3-2-commands.md`
- Expected:
  - Validation evidence and batch narrative complete.

4. Commit and push
- Commands:
  - `git add <scoped files>`
  - `git commit -m "..." -m "Why: ..."`
  - `git push origin master`
- Expected:
  - Batch 3.2 atomic commits published.
