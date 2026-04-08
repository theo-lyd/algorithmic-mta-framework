# Phase 3 Batch 3.1 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Run Phase 2 regression tests
- Command:
  - `PYTHONPATH=. python -m unittest discover -s tests/phase2 -p 'test_*.py'`
- Expected:
  - Existing tests pass.

2. Run Phase 3 SCD2 tests
- Command:
  - `PYTHONPATH=. python -m unittest discover -s tests/phase3 -p 'test_*.py'`
- Expected:
  - Batch 3.1 tests pass.

3. Run validation summary generator
- Command:
  - `PYTHONPATH=. python ingestion/pipeline/validate_campaign_scd2.py`
- Expected:
  - JSON summary with full event match coverage (`all_events_matched: true`).

4. Create batch docs
- Commands:
  - create `doc/phase-3/batch-3-1-scd2-validation.md`
  - create `doc/batches/phase-3-batch-3-1-report.md`
  - create `doc/batches/phase-3-batch-3-1-commands.md`
- Expected:
  - Validation evidence and batch narrative complete.

5. Commit and push
- Commands:
  - `git add <scoped files>`
  - `git commit -m "..." -m "Why: ..."`
  - `git push origin master`
- Expected:
  - Batch 3.1 atomic commits published.
