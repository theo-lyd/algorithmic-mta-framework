# Phase 2 Batch 2.5 Command Log

Status: Complete
Date: 2026-04-08

## Commands and Expected Outputs

1. Run full Phase 2 deterministic tests
- Command:
  - PYTHONPATH=. python -m unittest discover -s tests/phase2 -p 'test_*.py' > artifacts/phase-2/gate-closure/phase2_tests.txt 2>&1
- Expected:
  - Test transcript contains `OK` and test count.

2. Re-run Phase 2 validation runners for gate evidence
- Commands:
  - PYTHONPATH=. python ingestion/pipeline/validate_text_normalization.py > artifacts/phase-2/gate-closure/text_normalization_gate.json
  - PYTHONPATH=. python ingestion/pipeline/validate_financial_normalization.py > artifacts/phase-2/gate-closure/financial_normalization_gate.json
  - PYTHONPATH=. python ingestion/pipeline/validate_silver_harmonization.py > artifacts/phase-2/gate-closure/silver_harmonization_gate.json
  - PYTHONPATH=. python ingestion/pipeline/validate_silver_contracts.py > artifacts/phase-2/gate-closure/silver_contracts_gate.json
- Expected:
  - Validation JSON outputs show passing statuses for all relevant criteria.

3. Create closure docs
- Commands:
  - create doc/phase-2/phase-2-gate-check-report.md
  - create doc/batches/phase-2-batch-2-5-closure-report.md
  - create doc/batches/phase-2-batch-2-5-commands.md
- Expected:
  - Closure artifacts complete and evidence-linked.

4. Update README index
- Command:
  - patch README.md to include Batch 2.5 closure links
- Expected:
  - Phase 2 closure artifacts discoverable from top-level index.

5. Commit and push
- Commands:
  - git add <scoped files>
  - git commit -m "..." -m "Why: ..."
  - git push origin master
- Expected:
  - Closure batch commits published to origin/master.
