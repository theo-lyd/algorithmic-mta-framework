# Phase 0 Batch 0.2: Environment Reproducibility

Status: Complete
Date: 2026-04-08

## Scope Coverage
- Chunk 0.2.1: Build dev container with required services and pinned versions.
- Chunk 0.2.2: Add local and CI bootstrap scripts for one-command startup.
- Chunk 0.2.3: Validate cold-start onboarding on a clean machine.

## Implemented Artifacts
- .devcontainer/devcontainer.json
- docker-compose.yml
- requirements.txt
- scripts/bootstrap.sh
- scripts/bootstrap_ci.sh
- scripts/cold_start_validate.sh
- Makefile
- .github/workflows/phase0-bootstrap-check.yml
- doc/phase-0/batch-0-2-cold-start-validation.md

## Reproducibility Decisions (Why)

| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| Devcontainer + compose services | Host-only setup docs | Standardized onboarding and minimized machine drift | More container orchestration overhead | Team standardizes on managed cloud dev env without local containers |
| One-command bootstrap scripts | Manual setup steps | Faster onboarding and fewer human mistakes | Script maintenance required | Setup complexity becomes too small to justify scripts |
| CI bootstrap workflow on push/PR | Manual developer-only checks | Early detection of dependency drift and environment regressions | CI runtime cost | CI budget constraints require reduced frequency |
| Version pins in requirements and images | Floating latest tags | Deterministic installs and predictable behavior | Periodic pin refresh work | Security or upstream compatibility forces urgent upgrades |

## Validation Summary
- CI bootstrap validated with import checks for core packages.
- Cold-start validation artifact generated and committed.
- Docker compose config validates successfully.

## Notes
- During validation, a dependency conflict was detected between pandas and Great Expectations.
- Root cause was incompatible version constraints.
- Remediation: aligned pandas pin to 2.1.4; reran bootstrap and cold-start checks successfully.
