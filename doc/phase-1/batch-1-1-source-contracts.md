# Phase 1 Batch 1.1: Source Contracts and Connector Hardening

Status: Complete
Date: 2026-04-08

## Scope Coverage
- Chunk 1.1.1: Define source contracts for GA4 and partner feeds.
- Chunk 1.1.2: Configure Airbyte sync modes and incremental cursor logic.
- Chunk 1.1.3: Create ingestion idempotency keys and dedup strategy.

## Contract Set

### Source A: GA4 Events (Obfuscated Export)
- Contract name: ga4_events_v1
- Grain: one event record per event_id and event_timestamp.
- Expected delivery: near-hourly batch files/API pages.
- Required fields:
  - event_id (string)
  - event_timestamp (ISO8601 or microseconds epoch)
  - event_name (string)
  - user_pseudo_id (string)
  - source_channel (string)
  - event_params (array/object)
  - ingestion_source_file_id (string, nullable for API mode)
- Optional fields:
  - campaign_id
  - session_id
  - geo_country
- Cursor field: event_timestamp
- Primary idempotency key seed:
  - event_id + event_timestamp + user_pseudo_id

### Source B: Partner Post-Click Feed
- Contract name: partner_post_click_v1
- Grain: one click/conversion candidate per partner_event_id.
- Expected delivery: delayed file drop (up to 24h late).
- Required fields:
  - partner_event_id (string)
  - partner_name (string)
  - click_timestamp (ISO8601)
  - channel (string)
  - customer_hash (string)
  - payload (object)
  - source_file_id (string)
- Cursor field: click_timestamp
- Primary idempotency key seed:
  - partner_event_id + click_timestamp + partner_name

## Contract Validation Rules
- Required fields must be non-null for accepted records.
- Cursor fields must be parseable timestamps.
- Source identifiers must be present for replay/auditability.
- Records violating contract are diverted to dead-letter handling in later batches.

## Why This Contract Shape

| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| Explicit required/optional fields | Loose schema inference | Prevents silent schema drift and data loss | Requires stricter producer alignment | Source APIs are highly volatile and need schema registry automation |
| Timestamp cursor strategy | Full-refresh sync | Enables efficient incremental sync and replay | Requires timestamp quality controls | Source timestamps become unreliable |
| Source file identifier in contract | No file-level lineage | Supports replay, audit, and dedup diagnosis | Additional metadata handling | Source does not provide stable file identifiers |
