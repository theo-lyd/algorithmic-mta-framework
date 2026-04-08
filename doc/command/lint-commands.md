# Lint Commands Reference (Living Document)

Status: Initialized
Last Updated: 2026-04-08
Coverage: Phase 0 to Phase 1.5

## Purpose
Track all linting/static analysis commands used in this project.

## Update Protocol
- Add lint command only when executed.
- Include tool name and affected scope.

## Commands Used So Far
- No standalone lint command execution is explicitly documented in completed batches.

## Planned/Expected Lint Commands (Template)
- ruff check .
- pylint <path>
- flake8 <path>
- eslint .
- markdownlint "doc/**/*.md"

Note: Move a command from planned to used only after execution evidence exists in batch logs.

## Next Update Hook
When linting becomes part of Phase 2+ CI hardening, append:
1. Exact command.
2. Result summary.
3. Link to batch command log.
