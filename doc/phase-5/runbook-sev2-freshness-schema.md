# Runbook SEV-2: Freshness or Schema Breach

## Trigger
Freshness SLA miss or schema drift in critical tables.

## Immediate Actions
1. Pause downstream production refreshes.
2. Identify upstream source or contract change.
3. Open incident ticket and notify analytics engineering.

## Recovery Steps
1. Apply schema compatibility patch or rollback incompatible change.
2. Replay affected partitions.
3. Re-run governance checks and confirm no drift remains.

## Exit Condition
Freshness lag is below threshold and schema monitor reports no missing/unexpected columns.
