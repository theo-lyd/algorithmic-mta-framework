# Phase 0 Batch 0.1: Architecture and Standards Baseline

Status: Implemented
Date: 2026-04-08
Owner: Analytics Engineering Program

## Scope
- Chunk 0.1.1: Finalize target architecture and data domains.
- Chunk 0.1.2: Define naming conventions, Bronze/Silver/Gold model-layer standards, and metadata standards.
- Chunk 0.1.3: Define SLA/SLO matrix for latency, completeness, and freshness.

## Target Architecture

### Logical Architecture
1. Ingestion Layer
- Airbyte connectors extract GA4 events and partner feeds.
- Raw payloads are landed in append-only storage.

2. Storage and Compute Layer
- DuckDB is used for local OLAP compute.
- Parquet files are partitioned by event date and domain.

3. Transformation Layer
- dbt governs staged and curated transformations.
- Medallion structure: Bronze (raw), Silver (cleaned/harmonized), Gold (business marts).

4. Orchestration Layer
- Airflow schedules ingestion, replay, and transformation DAGs.
- Late-arriving data triggers partition-aware reprocessing.

5. Quality and Observability Layer
- Great Expectations validates contracts and business logic.
- Monte Carlo monitors freshness, volume, schema, and anomalies.

6. Consumption Layer
- Metabase supports executive reporting.
- Streamlit provides scenario planning and what-if simulation.

## Data Domains
- marketing_events: GA4 and partner event streams.
- campaign_dim: campaign metadata with SCD2 tracking.
- identity: hashed customer and cross-system mapping.
- attribution: pathing, Markov outputs, heuristic baselines.
- finance: spend, returns, net revenue, ROAS.
- governance: quality checks, incidents, SLA metrics.

## Architecture Decision Rationale (Why)

| Decision | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| DuckDB + Parquet | Postgres, BigQuery-only | Fast local OLAP, low infra overhead, portable for thesis and reproducibility | Single-node constraints for very large concurrent workloads | Multi-team scale-out and strict concurrency needs exceed local compute |
| dbt for transformations | Custom Python SQL runners | Declarative modeling, tests, lineage, modularity | Additional project structure overhead | Team needs custom graph orchestration beyond dbt DAG patterns |
| Airflow orchestration | Cron, Prefect, Dagster | Mature scheduling ecosystem and sensor model for late data | Heavier setup than cron | Team standardizes fully on alternate orchestrator |
| Medallion model | Flat warehouse-only modeling | Explicit data quality progression and accountability by layer | More artifacts and governance burden | Data volume/use-cases become too simple for layered architecture |

## Domain Contract Baseline
- Each domain has an owner role and cadence.
- Every table includes load metadata: ingestion timestamp, batch id, source id.
- Every Gold metric has a written business definition and test mapping.

## Definition of Completion for Batch 0.1
- Architecture layers and domain boundaries are documented.
- Naming/model/metadata standards are documented in companion standards catalog.
- SLA/SLO matrix is documented in companion matrix document.
