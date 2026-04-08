# Phase 0 Batch 0.3: Security and Compliance Baseline

Status: Complete
Date: 2026-04-08

## Scope Coverage
- Chunk 0.3.1: Secrets handling policy and key rotation workflow.
- Chunk 0.3.2: PII classification and masking policy for event/CRM joins.
- Chunk 0.3.3: Access controls and least-privilege role matrix.

## Delivered Artifacts
- doc/phase-0/secrets-key-rotation.md
- doc/phase-0/pii-classification-masking.md
- doc/phase-0/access-control-matrix.md
- doc/phase-0/batch-0-3-security-compliance.md
- scripts/security_guardrail_check.sh
- .github/workflows/phase0-security-check.yml
- doc/phase-0/batch-0-3-security-validation.md

## Security Baseline Summary

### 1. Secrets and Key Rotation
- Secrets must be injected through environment variables or managed secret stores.
- Secrets are prohibited in source-controlled files.
- Rotation cadence and emergency rotation paths are defined.

### 2. PII and Masking
- PII classes defined (none, pseudonymous, sensitive, restricted).
- Join keys for CRM/web identity must use irreversible hashes.
- Dataset-level masking and role-based exposure rules are defined.

### 3. Least-Privilege RBAC
- Role matrix defines read/write/admin by system layer and domain.
- No broad wildcard permissions for production datasets.
- Access changes require owner + security approver.

## Why These Controls

| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| Policy-as-doc plus CI guardrail | Policy-only docs, manual review only | Combines clarity with enforceable checks in CI | More maintenance for checks and false-positive tuning | Enterprise secret scanning platform fully replaces local checks |
| PII classification tiers | Binary PII/non-PII | Better data minimization and access granularity | Additional governance overhead | Regulatory model changes simplify classification |
| Role matrix by domain/layer | Global coarse-grained roles | Supports least-privilege and auditability | More role management complexity | Team size and domains become very small |

## Validation Outcome
- Guardrail script executed successfully.
- Security validation artifact generated.
- CI security-check workflow defined for push and pull requests.
