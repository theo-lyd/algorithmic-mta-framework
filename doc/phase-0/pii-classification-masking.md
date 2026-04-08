# PII Classification and Masking Policy

Status: Approved Baseline (Phase 0)
Date: 2026-04-08

## 1. Classification Tiers
- none: operational metadata with no personal context.
- pseudonymous: hashed IDs that cannot be directly attributed without external mapping.
- sensitive: personal identifiers (email, phone, name, IP when combined).
- restricted: highly sensitive attributes requiring explicit legal or security controls.

## 2. Policy for Event/CRM Joins
- Use irreversible Customer_Hash for identity harmonization.
- Raw CRM identifiers must not be exposed outside restricted silver models.
- Gold layer only surfaces aggregated or masked fields.

## 3. Masking Standards
- Email: retain domain only where needed (example: ****@domain.com).
- Phone: mask all but last 2 digits.
- Names: tokenize or hash for analytics workflows.
- IP data: truncate/pseudonymize before persistent storage in shared layers.

## 4. Access and Data Minimization
- Only required columns are carried forward between layers.
- Sensitive and restricted fields are excluded from BI extracts by default.

## 5. Data Quality and Compliance Checks
- Contract tests validate no sensitive fields leak into Gold marts.
- Periodic audits check masking consistency.

## 6. Why This Policy

| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| Four-tier classification | Binary classification | Provides nuanced controls across layers and roles | More governance complexity | Regulatory scope narrows and simpler policy is sufficient |
| Hash-based join key | Raw identifier joins | Enables cross-system analytics while reducing direct exposure | Hash collisions or mismatches must be managed | Dedicated privacy-preserving identity platform is adopted |
| Gold exclusion by default | Gold open access | Minimizes accidental leakage in dashboards | Extra work for approved exceptions | Business needs mandate broader access with legal approval |
