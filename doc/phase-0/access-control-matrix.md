# Access Control and Least-Privilege Role Matrix

Status: Approved Baseline (Phase 0)
Date: 2026-04-08

## Role Definitions
- DE: Data Engineer
- AE: Analytics Engineer
- MLE: ML Engineer
- BI: BI Analyst
- SEC: Security Reviewer
- OPS: Platform/Operations

## Permission Model
- R: Read
- W: Write
- A: Admin
- N: No access

## Matrix

| System/Domain | DE | AE | MLE | BI | SEC | OPS |
|---|---|---|---|---|---|---|
| Bronze raw datasets | W | R | R | N | R | A |
| Silver curated datasets | W | W | R | R | R | A |
| Gold marts | R | W | R | R | R | A |
| CRM restricted identifiers | R (approved) | N | N | N | R | A |
| dbt project | W | W | R | R | R | A |
| Airflow configs | W | R | N | N | R | A |
| CI workflow configs | R | R | R | R | R | A |
| Secrets manager | N | N | N | N | R | A |

## Access Control Rules
1. Production write access requires role and environment approval.
2. No shared admin credentials.
3. Every elevated access grant must include expiration date.
4. Quarterly access review required for all roles.

## Why This Matrix

| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| Domain/layer-scoped permissions | Global broad roles | Enforces least-privilege and improves auditability | More role administration work | Team shrinks and role complexity is no longer justified |
| Restricted CRM raw access | Open read to engineering roles | Reduces high-risk data exposure | Slower debugging for unauthorized roles | Privacy-safe synthetic mirrors are universally available |
| Expiring elevated access | Permanent privileged grants | Reduces privilege creep | Operational overhead for renewals | Automated short-lived access broker is implemented |
