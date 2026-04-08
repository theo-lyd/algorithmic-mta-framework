# Airbyte Sync Strategy (Batch 1.1)

## Objective
Harden connector behavior for incremental ingestion and late-arrival resilience.

## Connector Modes

### GA4
- Sync mode: incremental append
- Cursor: event_timestamp
- Frequency: hourly
- Replay policy: 2-day rolling replay window for late event fixes

### Partner Post-Click
- Sync mode: incremental append
- Cursor: click_timestamp
- Frequency: hourly with offset
- Replay policy: 7-day rolling replay window to account for delayed deliveries

## Incremental Cursor Logic
1. Maintain high-watermark per source connector.
2. On each run, pull records where cursor >= (high_watermark - replay_window).
3. Deduplicate using idempotency key and latest cursor value.
4. Advance high-watermark only after successful write + audit metadata commit.

## Failure Behavior
- If connector fails mid-run, watermark is not advanced.
- Retry reads same replay window and dedup logic prevents duplication.

## Why This Approach

| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| Incremental append with replay window | Full refresh | Lower compute cost and supports late data | Requires robust dedup | Source quality forces periodic full refresh |
| Source-specific replay windows | Single global window | Better fit to source latency profiles | More configuration complexity | Latency patterns converge and can be standardized |
| Watermark commit after successful write | Early watermark update | Prevents data loss on partial failures | Might re-read some data on retries | Transactional exactly-once infrastructure is available |
