# Batch 1.3 Late-Arriving Data Validation

Date: 2026-04-08

## Validation Run
- Input manifests:
  - ingestion/samples/partner_expected_manifest.json
  - ingestion/samples/partner_arrived_manifest.json

## Expected Behaviors
- Delayed file detection identifies missing partner feed files.
- Replay planning returns only impacted partitions.
- Reconciliation compares expected vs arrived volume by date/channel.

## Observed Output
- delayed_files=1
- delayed_ids=partner_20260408_00.json
- impacted_partitions=event_date=2026-04-08/source_channel=affiliate
- reconciliation_rows=3
- reconciliation_total_delta=140

## Interpretation
- Exactly one delayed file was detected.
- Selective replay targets only one partition, not full backfill.
- Reconciliation highlights the missing volume for alerting/remediation flows.
