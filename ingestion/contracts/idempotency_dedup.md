# Ingestion Idempotency and Dedup Strategy

## Goal
Ensure repeated ingestion runs do not create duplicate business events and that late records reconcile safely.

## Idempotency Key Design
- Canonical key input fields:
  - source_name
  - source_event_id (or partner_event_id)
  - event_timestamp/click_timestamp normalized to UTC
  - stable actor id (user_pseudo_id or customer_hash)
- Key algorithm:
  - Concatenate canonicalized values with '|'
  - Hash using SHA-256

## Dedup Resolution Rule
- Partition dedup by idempotency_key.
- Keep record with latest cursor timestamp.
- If cursor tie occurs, keep lexicographically max source_file_id to enforce determinism.

## SQL Reference Pattern
```sql
with ranked as (
  select
    *,
    row_number() over (
      partition by idempotency_key
      order by cursor_ts desc, source_file_id desc
    ) as rn
  from bronze_events
)
select *
from ranked
where rn = 1;
```

## Audit Columns Required in Bronze Writes
- ingestion_ts
- batch_id
- source_file_id
- idempotency_key

## Why This Strategy

| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| Hash-based idempotency key | Natural key only | Consistent key size and source-agnostic pattern | Requires deterministic normalization | Natural keys become globally stable and complete |
| Latest-cursor winner | First-seen winner | Handles late corrected records | May overwrite earlier payload variants | Source sends immutable never-corrected data |
| Tie-break by source_file_id | Random tie resolution | Deterministic replay outputs | Requires source_file_id quality | Source lacks stable file-level metadata |
