# Secrets Handling and Key Rotation Policy

Status: Approved Baseline (Phase 0)
Date: 2026-04-08

## 1. Secret Sources of Truth
Allowed:
- Environment variables injected at runtime.
- Hosted secret managers (when enabled in deployment environment).
- Local-only .env for development (never committed).

Prohibited:
- Plaintext credentials in source files, notebooks, SQL, YAML, or markdown.
- Long-lived personal access tokens in scripts.

## 2. Secret Categories
- Database credentials.
- API tokens (GA4, partner APIs, observability tools).
- Service account keys and signing keys.
- Webhook secrets.

## 3. Rotation Workflow

### 3.1 Standard Rotation Cadence
- High-risk tokens: every 30 days.
- Standard service credentials: every 90 days.
- Emergency rotation: within 4 hours of suspected exposure.

### 3.2 Rotation Steps
1. Generate replacement secret in source system.
2. Update secret manager/runtime environment.
3. Validate connectivity with new secret.
4. Revoke old secret.
5. Document rotation event and approvers.

### 3.3 Emergency Rotation Triggers
- Secret appears in commit history.
- Security scan alert for leaked token.
- Third-party compromise notification.

## 4. Audit and Logging
- Rotation events must record timestamp, owner, approver, and scope.
- Failed rotation attempts are logged and escalated.

## 5. Why This Policy

| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| Env-var/secret-store injection | File-based committed config | Eliminates plaintext secrets in repository | Requires deployment/runtime secret plumbing | Platform has secure encrypted config engine with stronger controls |
| 30/90-day rotation cadence | Annual/manual rotation | Reduces window of exposure | Operational overhead and potential service disruptions | Risk posture changes and compensating controls improve |
| Emergency 4-hour rotation SLA | Best-effort response | Limits breach blast radius | Requires on-call readiness | Low criticality environment with no sensitive integrations |
