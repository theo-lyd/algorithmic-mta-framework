# Airbyte Ingestion

This folder tracks source connector settings and sync strategies.

Planned connectors:
- GA4 events.
- Partner post-click data feeds.
- CRM export feed for identity harmonization.

Use incremental + append sync where possible, with replay support for late-arriving partitions.
