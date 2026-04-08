# Phase 0 Standards Catalog

Status: Implemented for Batch 0.1
Date: 2026-04-08

## 1. Naming Conventions

### 1.1 File and Model Naming
- Use snake_case for files and model names.
- Prefix by layer where appropriate:
  - stg_ for staging models.
  - int_ for intermediate models.
  - fct_ for fact tables.
  - dim_ for dimension tables.
- Example:
  - stg_ga4_events.sql
  - int_sessionized_events.sql
  - fct_attribution_conversions.sql
  - dim_campaign_scd2.sql

### 1.2 Column Naming
- Primary keys: <entity>_id (e.g., session_id).
- Foreign keys: referenced entity key name (e.g., campaign_id).
- Timestamps must end with _ts (event_ts, load_ts).
- Booleans must use is_/has_ prefix (is_conversion, has_return).

### 1.3 Partition and Path Naming
- Parquet partitions use dt=YYYY-MM-DD convention.
- Domain-first pathing:
  - data/bronze/marketing_events/dt=2026-04-08/
  - data/silver/identity/dt=2026-04-08/
  - data/gold/attribution/dt=2026-04-08/

## 2. Model Layer Standards

### 2.1 Bronze
- Append-only raw ingestion with minimal mutation.
- Required metadata columns:
  - load_ts
  - batch_id
  - source_system
  - source_record_id

### 2.2 Silver
- Cleaned, typed, normalized data.
- Encoding and locale normalization occurs here.
- Sessionization and identity harmonization begin here.

### 2.3 Gold
- Business-ready marts with stable semantics.
- ROAS and attribution metrics are computed here.
- Every Gold model requires tests for reconciliation and definitions.

## 3. Metadata Standards

### 3.1 Table-Level Metadata
- owner_role: DE/AE/MLE/BI
- domain: marketing_events/campaign_dim/identity/attribution/finance
- refresh_cadence: hourly/daily
- pii_classification: none/low/moderate/high

### 3.2 Column-Level Metadata
- description: required for all business columns.
- data_type: canonical type specification.
- sensitivity: non_sensitive/pseudonymous/sensitive.

### 3.3 Test Metadata
- Every critical model includes:
  - freshness expectation
  - uniqueness checks
  - referential integrity checks
  - business rule checks

## 4. Approval Workflow
- Draft: authored by owning role.
- Technical review: AE + DE.
- Business sign-off: BI + Finance stakeholder.
- Effective date: tagged in release notes.

## 5. Why This Standard Set

| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| Snake_case + prefix schema | CamelCase, no prefixes | Easier scanning and layer visibility at scale | Slight verbosity in names | Team adopts strongly typed namespace tooling that removes need for prefixes |
| Domain-first partition paths | Pipeline-first pathing | Better discoverability and ownership mapping | Requires strict governance | Cross-domain joins dominate and pathing strategy needs optimization |
| Required metadata columns | Optional metadata only | Enables replay, lineage, and auditability | Extra storage and ingestion logic | Storage constraints become severe and metadata strategy is centralized elsewhere |
