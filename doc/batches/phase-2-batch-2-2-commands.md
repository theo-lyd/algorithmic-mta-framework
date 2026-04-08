# Phase 2 Batch 2.2 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Run deterministic unit tests
- Command:
  - `PYTHONPATH=. python -m unittest discover -s tests/phase2 -p 'test_*.py'`
- Expected:
  - All tests pass with `OK`.

2. Run financial validation summary generator
- Command:
  - `PYTHONPATH=. python ingestion/pipeline/validate_financial_normalization.py`
- Expected:
  - JSON summary printed with `all_passed: true`.
  - Artifact generated at `artifacts/phase-2/batch-2-2/financial_normalization_summary.json`.

3. Create batch documentation
- Commands:
  - create `doc/phase-2/batch-2-2-currency-conversion-policy.md`
  - create `doc/phase-2/batch-2-2-financial-normalization-validation.md`
  - create `doc/batches/phase-2-batch-2-2-report.md`
  - create `doc/batches/phase-2-batch-2-2-commands.md`
- Expected:
  - Policy, validation, and batch docs complete.

4. Commit and push
- Commands:
  - `git add <scoped files>`
  - `git commit -m "..." -m "Why: ..."`
  - `git push origin master`
- Expected:
  - Batch 2.2 atomic commits published.
