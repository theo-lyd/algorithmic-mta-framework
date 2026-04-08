# Runbook SEV-1: Pixel Downtime

## Trigger
Spend is active while page views drop to zero.

## Immediate Actions
1. Confirm tracking tag status in tag manager.
2. Verify page render and network beacon delivery.
3. Escalate to marketing ops and web platform on-call.

## Recovery Steps
1. Roll back latest tag/container changes.
2. Re-fire synthetic event checks.
3. Backfill impacted event window once tracking is restored.

## Exit Condition
Page views recover and freshness/volume monitors return to green for two consecutive runs.
