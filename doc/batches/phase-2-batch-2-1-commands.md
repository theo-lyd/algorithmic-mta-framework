# Phase 2 Batch 2.1 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Run deterministic unit tests
- Command:
  - `PYTHONPATH=. python -m unittest discover -s tests/phase2 -p 'test_*.py'`
- Expected:
  - Test suite passes with `OK`.

2. Run validation summary generator
- Command:
  - `PYTHONPATH=. python ingestion/pipeline/validate_text_normalization.py`
- Expected:
  - JSON summary printed with `all_passed: true`.
  - Artifact generated at `artifacts/phase-2/batch-2-1/text_normalization_summary.json`.

3. Create batch documentation
- Commands:
  - create `doc/phase-2/batch-2-1-locale-normalization-validation.md`
  - create `doc/batches/phase-2-batch-2-1-report.md`
  - create `doc/batches/phase-2-batch-2-1-commands.md`
- Expected:
  - Batch report, command log, and validation evidence docs complete.

4. Commit and push
- Commands:
  - `git add <scoped files>`
  - `git commit -m "..." -m "Why: ..."`
  - `git push origin master`
- Expected:
  - Atomic commit history for Batch 2.1 published.
