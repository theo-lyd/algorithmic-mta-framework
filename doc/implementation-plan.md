# Phase-by-Phase Implementation Plan

## Thesis Statement
Evaluating the transition from heuristic-based attribution (First/Last-Touch) to data-driven Markov Chain models to eliminate ad-spend waste and optimize Return on Ad Spend (ROAS) in fragmented digital ecosystems.

## Delivery Model
- Execution style: incremental, test-first, with hard quality gates.
- Cadence: 2-week sprints.
- Promotion path: Dev -> Staging -> Prod.
- Constraint: no phase closes without quality checks and business-rule validation.

## Global Quality Controls
### Definition of Ready
- Scope and inputs are approved.
- Source and target schemas are documented.
- SLA and tests are agreed.

### Definition of Done
- Unit, integration, and data tests pass.
- Monitoring and alerting are active.
- Backfill and rollback workflows are verified.

### Quality Gates
- Gate A: schema and data contract validation.
- Gate B: business logic validation against benchmark samples.
- Gate C: performance and cost baseline checks.
- Gate D: stakeholder sign-off from Analytics and Marketing.

---

## Phase 0: Program Foundation and Standards
**Goal:** Establish governance, reproducibility, and operating standards.

### Batch 0.1: Architecture and standards
- Chunk 0.1.1: finalize target architecture and data domains.
- Chunk 0.1.2: define naming conventions and bronze/silver/gold contracts.
- Chunk 0.1.3: define SLA/SLO matrix for freshness, completeness, and latency.

### Batch 0.2: Environment reproducibility
- Chunk 0.2.1: build `.devcontainer` and local runtime services.
- Chunk 0.2.2: create one-command bootstrap scripts.
- Chunk 0.2.3: validate onboarding on a clean machine.

### Batch 0.3: Security and compliance baseline
- Chunk 0.3.1: define secrets and key rotation workflow.
- Chunk 0.3.2: define PII masking policy.
- Chunk 0.3.3: define least-privilege access model.

**Exit Criteria**
- Reproducible setup validated.
- Standards approved.
- Security controls verified.

---

## Phase I: Environment and Ingestion (ELT)
**Goal:** Build resilient ingestion with late-arriving data support.

### Batch 1.1: Source onboarding
- Chunk 1.1.1: define source contracts for GA4 and partner feeds.
- Chunk 1.1.2: configure Airbyte incremental syncs.
- Chunk 1.1.3: implement idempotency and deduplication.

### Batch 1.2: Bronze landing
- Chunk 1.2.1: convert raw JSON payloads to partitioned Parquet.
- Chunk 1.2.2: partition by event date and channel.
- Chunk 1.2.3: append ingestion audit metadata.

### Batch 1.3: Late-arriving replay orchestration
- Chunk 1.3.1: implement Airflow sensors for delayed feeds.
- Chunk 1.3.2: replay impacted partitions only.
- Chunk 1.3.3: reconcile expected vs arrived volume.

### Batch 1.4: Ingestion observability
- Chunk 1.4.1: add freshness and volume checks.
- Chunk 1.4.2: set alerting for failed ingestion.
- Chunk 1.4.3: define backfill playbook.

**Exit Criteria**
- Stable raw-to-parquet ingestion.
- Replay logic proven.
- Ingestion SLAs achieved.

---

## Phase II: Data Cleaning and Harmonization
**Goal:** Handle German-market data quality and flatten nested payloads.

### Batch 2.1: Encoding and locale normalization
- Chunk 2.1.1: detect and standardize encoding.
- Chunk 2.1.2: normalize German text and transliteration rules.
- Chunk 2.1.3: test deterministic string cleaning fixtures.

### Batch 2.2: Financial parsing
- Chunk 2.2.1: parse abbreviations (e.g., Mio, Tsd).
- Chunk 2.2.2: normalize locale decimal/thousand separators.
- Chunk 2.2.3: standardize to EUR.

### Batch 2.3: Flattening and silver schema
- Chunk 2.3.1: unnest GA4 arrays and event params.
- Chunk 2.3.2: enforce 30-minute inactivity sessionization.
- Chunk 2.3.3: build canonical dimensions.

### Batch 2.4: Data contract testing
- Chunk 2.4.1: GE checks for nulls, uniqueness, and referential integrity.
- Chunk 2.4.2: schema drift tests.
- Chunk 2.4.3: failed-record quarantine and remediation flow.

**Exit Criteria**
- Silver layer passes data contracts.
- Locale edge cases validated.
- Session rule validated.

---

## Phase III: Analytics Engineering Core
**Goal:** Build a single source of truth for journeys and campaign history.

### Batch 3.1: SCD Type 2 campaign metadata
- Chunk 3.1.1: build campaign dimension with validity windows.
- Chunk 3.1.2: preserve owner and budget history.
- Chunk 3.1.3: validate point-in-time joins.

### Batch 3.2: Identity harmonization
- Chunk 3.2.1: define deterministic identity match hierarchy.
- Chunk 3.2.2: create unified customer hash.
- Chunk 3.2.3: track confidence score and unresolved records.

### Batch 3.3: Journey pathing
- Chunk 3.3.1: de-dup and event ordering logic.
- Chunk 3.3.2: recursive CTE path assembly.
- Chunk 3.3.3: enforce 30-day lookback window.

### Batch 3.4: Gold marts
- Chunk 3.4.1: conversion fact table net of returns.
- Chunk 3.4.2: channel spend fact harmonization.
- Chunk 3.4.3: ROAS mart output.

**Exit Criteria**
- Journey SSOT validated.
- SCD2 integrity proven.
- Gold marts reconciled with source totals.

---

## Phase IV: Algorithmic Attribution and AI
**Goal:** Replace heuristic attribution with explainable algorithmic outputs.

### Batch 4.1: Baseline heuristic models
- Chunk 4.1.1: first-touch and last-touch attribution.
- Chunk 4.1.2: linear and time-decay baselines.
- Chunk 4.1.3: benchmark comparison set.

### Batch 4.2: Markov attribution
- Chunk 4.2.1: transition matrix from observed paths.
- Chunk 4.2.2: removal effect by channel.
- Chunk 4.2.3: attribution normalization to 100 percent.

### Batch 4.3: Conversion propensity model
- Chunk 4.3.1: feature set for next-7-day conversion.
- Chunk 4.3.2: logistic regression training and calibration.
- Chunk 4.3.3: evaluate AUC, precision-recall, and lift.

### Batch 4.4: Segmentation
- Chunk 4.4.1: feature engineering for clustering.
- Chunk 4.4.2: K-means training and stability checks.
- Chunk 4.4.3: business-friendly segment labeling.

### Batch 4.5: Finance bridge
- Chunk 4.5.1: allocate net revenue by attributed share.
- Chunk 4.5.2: compute ROAS under each attribution model.
- Chunk 4.5.3: run variance analysis vs current reporting.

**Exit Criteria**
- Markov outputs stable and explainable.
- Propensity model meets performance thresholds.
- Attributed revenue reconciles exactly.

---

## Phase V: Governance, Observability, and CI/CD
**Goal:** Enforce trust with tests, monitoring, and deployment controls.

### Batch 5.1: Monte Carlo monitors
- Chunk 5.1.1: monitor freshness, volume, and schema drift.
- Chunk 5.1.2: detect tracking pixel downtime.
- Chunk 5.1.3: incident routing and runbooks.

### Batch 5.2: Great Expectations business rules
- Chunk 5.2.1: conversion-to-session referential integrity.
- Chunk 5.2.2: no ghost revenue test.
- Chunk 5.2.3: lookback and inactivity assertions.

### Batch 5.3: CI/CD automation
- Chunk 5.3.1: automate dbt and GE checks on PR.
- Chunk 5.3.2: gated environment promotions.
- Chunk 5.3.3: versioned artifacts and reproducibility.

### Batch 5.4: Performance and cost
- Chunk 5.4.1: query profiling and materialization tuning.
- Chunk 5.4.2: optimize incremental runs.
- Chunk 5.4.3: cost monitoring thresholds.

**Exit Criteria**
- Governance checks automated.
- SLA breaches are detectable and actionable.
- Cost and reliability targets met.

---

## Phase VI: BI and Decisioning
**Goal:** Deliver executive decision tools and scenario simulation.

### Batch 6.1: Metabase dashboards
- Chunk 6.1.1: Attribution War view.
- Chunk 6.1.2: channel waste report.
- Chunk 6.1.3: ROAS drilldown suite.

### Batch 6.2: Streamlit simulator
- Chunk 6.2.1: budget reallocation inputs and constraints.
- Chunk 6.2.2: predicted revenue impact outputs.
- Chunk 6.2.3: confidence intervals and export.

### Batch 6.3: Adoption and governance
- Chunk 6.3.1: KPI glossary.
- Chunk 6.3.2: monthly decision ritual.
- Chunk 6.3.3: stakeholder training.

**Exit Criteria**
- Dashboard metrics finance-reconciled.
- Simulator supports planning cycles.
- Stakeholders can operationalize outputs.

---

## Phase VII: Production Hardening and Thesis Packaging
**Goal:** Prove repeatability and quantify business value.

### Batch 7.1: Production readiness
- Chunk 7.1.1: disaster recovery and replay drills.
- Chunk 7.1.2: historical backfill stress tests.
- Chunk 7.1.3: security and access audit sign-off.

### Batch 7.2: Impact measurement
- Chunk 7.2.1: pre/post budget experiment design.
- Chunk 7.2.2: measure ROAS uplift and waste reduction.
- Chunk 7.2.3: sensitivity analysis.

### Batch 7.3: Thesis package
- Chunk 7.3.1: methodology and reproducibility appendix.
- Chunk 7.3.2: executive blueprint summary.
- Chunk 7.3.3: defense deck.

**Exit Criteria**
- Production sign-off complete.
- Impact quantified with confidence.
- Thesis package finalized.

---

## Cross-Phase Validation Matrix
- Data correctness: schema, nulls, uniqueness, and referential integrity.
- Business rules: 30-day lookback, 30-minute inactivity, net-of-returns revenue.
- Attribution conservation: totals equal actual conversions and revenue.
- ML quality: calibration, drift, retraining criteria.
- Operations: freshness SLA and replay integrity.

## Reference Timeline
- Phase 0: 1 to 2 weeks.
- Phase I: 2 to 3 weeks.
- Phase II: 2 to 3 weeks.
- Phase III: 3 to 4 weeks.
- Phase IV: 3 to 4 weeks.
- Phase V: 2 to 3 weeks.
- Phase VI: 2 to 3 weeks.
- Phase VII: 1 to 2 weeks.

Total: 16 to 24 weeks.
