# Git Commands Reference (Living Document)

Status: Active
Last Updated: 2026-04-08
Coverage: Phase 0 to Phase 1.5

## Purpose
Central reference for all Git commands used in this project.

## Update Protocol
- Append new commands after each successful batch.
- Include command, intent, and when it was used.
- Do not remove historical commands unless incorrect.

## Commands Used So Far
- git status --short
- git -C /workspaces/algorithmic-mta-framework status
- git config --show-origin --get core.hooksPath
- git add <file-or-path>
- git commit -m "<message>" -m "<why rationale>"
- git log --oneline -n 6
- git log --oneline -8
- git log --oneline -16
- git diff -- <file>
- git push origin master
- git push --no-verify origin master

## Typical Patterns
- Atomic commit pattern:
  - git add <scoped paths>
  - git commit -m "<batch-specific message>" -m "Why: <decision rationale>"
  - git push origin master

## Next Update Hook
For each new batch, add:
1. New Git commands introduced.
2. Any changed commit/push workflow.
3. Any Git troubleshooting command used.
