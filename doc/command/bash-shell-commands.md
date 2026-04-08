# Bash and Shell Commands Reference (Living Document)

Status: Active
Last Updated: 2026-04-08
Coverage: Phase 0 to Phase 1.5

## Purpose
Central reference for all Bash and shell commands used in project execution.

## Update Protocol
- Add command lines exactly as executed.
- Keep environment-setup and validation commands distinct.

## Commands Used So Far
- bash scripts/bootstrap.sh
- bash scripts/bootstrap_ci.sh
- bash scripts/cold_start_validate.sh
- bash scripts/security_guardrail_check.sh
- command -v dbt
- dbt --version
- mkdir -p artifacts/phase-1/gate-closure
- tail -n 20 /tmp/batch0_2_bootstrap_ci.log
- tail -n 30 /tmp/phase0_gate_bootstrap_ci.log
- cat /tmp/phase0_gate_security.log
- cat artifacts/phase-1/batch-1-4/observability_summary.json
- cat artifacts/phase-1/batch-1-4/dead_letter_events.jsonl
- cat artifacts/phase-1/batch-1-4/alerts.jsonl
- grep -E "duckdb|pandas|dbt-core|airflow" requirements.txt
- ls -la .git/hooks
- sed -n '1,160p' .git/hooks/pre-push
- rm -f .git/hooks/pre-push .git/hooks/post-commit .git/hooks/post-checkout .git/hooks/post-merge

## Typical Patterns
- CI-style validation with exit-code capture:
  - bash <script>.sh >/tmp/<log>.log 2>&1; echo EXIT:$?

## Next Update Hook
After each batch, append any new shell command with brief purpose.
