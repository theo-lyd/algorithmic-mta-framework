# Batch 1.4 Backfill Playbook (Date-Range Recovery)

## Purpose
Provide a controlled runbook for reprocessing historical ingestion windows while minimizing downstream disruption.

## Preconditions
- Incident ticket with scope, root cause, and impacted date range.
- Approval from Data Engineering owner and Analytics Engineering owner.
- Validation plan and rollback plan prepared.

## Backfill Procedure
1. Identify impacted range and channels.
- Inputs:
  - start_date (inclusive)
  - end_date (inclusive)
  - source_channel set

2. Freeze dependent publishes.
- Pause downstream Gold publishes during replay window.

3. Execute selective replay.
- Re-run only impacted partitions:
  - event_date in [start_date, end_date]
  - source_channel in impacted set
- Preserve original source_file_id lineage.

4. Run reconciliation.
- Compare expected vs arrived volume by date/channel.
- Validate no negative drift remains.

5. Validate quality checks.
- Freshness restored to SLA.
- Anomaly flags reviewed and approved.

6. Resume publishes.
- Unpause downstream jobs after sign-off.

## Rollback Procedure
- If replay output invalid:
  - Stop replay.
  - Restore prior partition snapshots.
  - Emit incident update and re-plan remediation.

## Why This Playbook
| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| Selective date-range replay | Full historical reload | Minimizes cost and blast radius | Requires accurate impact scoping | Impact scope cannot be determined reliably |
| Pause dependent publishes | Keep all pipelines running | Prevents inconsistent business reporting | Temporary reporting delay | Consumers can tolerate eventual consistency with clear banners |
| Mandatory reconciliation post-backfill | Best-effort checks | Ensures repair quality and auditability | Additional operational steps | Fully automated reconciliation guarantees are in place |
