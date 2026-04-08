# Execution-Ready Master Backlog

## Planning Baseline
- Sprint length: 2 weeks.
- Timeline: 10 sprints (20 weeks).
- Story points: Fibonacci (1, 2, 3, 5, 8, 13).
- Roles:
  - DE: Data Engineer
  - AE: Analytics Engineer
  - MLE: ML Engineer
  - BI: BI Analyst
- Capacity target per sprint:
  - DE: 18
  - AE: 20
  - MLE: 16
  - BI: 14
  - Team: 68
- Buffer: reserve 15 to 20 percent for data volatility and rework.

## Role Ownership
- DE: ingestion, orchestration, storage, reliability plumbing.
- AE: dbt modeling, business rules, semantic consistency.
- MLE: attribution and ML models, drift and retraining logic.
- BI: dashboards, simulator UX, stakeholder adoption.

## Master Backlog Table

| ID | Epic | Work Item | Primary | Support | Points | Target Sprint | Acceptance Criteria |
|---|---|---|---|---|---:|---|---|
| MTA-001 | Foundation | Dev container and service orchestration baseline | DE | AE | 5 | S1 | One-command startup for core stack works on clean environment |
| MTA-002 | Foundation | Secrets, env strategy, role-based access matrix | DE | AE | 3 | S1 | Secrets not hardcoded, access matrix approved |
| MTA-003 | Foundation | Naming conventions, layer standards, modeling contract | AE | DE | 3 | S1 | Standards approved and used by first pipelines |
| MTA-004 | Foundation | SLA/SLO definitions and incident severity policy | AE | DE | 3 | S1 | Freshness, completeness, and error SLOs agreed |
| MTA-005 | Ingestion | GA4 connector setup with incremental cursor logic | DE | AE | 8 | S1 | Incremental sync stable across three runs |
| MTA-006 | Ingestion | Raw JSON landing and partitioned parquet writer | DE | AE | 8 | S1 | Bronze partition output generated and queryable |
| MTA-007 | Ingestion | Ingestion audit columns and idempotency keys | DE | AE | 5 | S2 | No duplicate loads on replay |
| MTA-008 | Ingestion | Airflow DAG base and schedule orchestration | DE | AE | 5 | S2 | DAG succeeds end-to-end on sample day |
| MTA-009 | Ingestion | Late-arriving data sensor and partition replay logic | DE | AE | 8 | S2 | Delayed feed triggers selective reprocessing only |
| MTA-010 | Ingestion | Reconciliation check expected vs arrived event volumes | AE | DE | 5 | S2 | Alert generated on threshold breach |
| MTA-011 | Cleaning | Encoding detection and UTF normalization pipeline | AE | DE | 5 | S3 | Known bad encodings corrected in fixtures |
| MTA-012 | Cleaning | German string normalization and transliteration rules | AE | DE | 5 | S3 | Umlaut handling validated by tests |
| MTA-013 | Cleaning | Locale-aware financial parsing and abbreviation expansion | AE | DE | 8 | S3 | Inputs like 10 Mio converted correctly |
| MTA-014 | Cleaning | Nested GA4 flattening to canonical silver schema | AE | DE | 8 | S3 | Silver tables populated with expected row counts |
| MTA-015 | Core Modeling | Sessionization with 30-minute inactivity rule | AE | DE | 8 | S4 | Deterministic boundary tests pass |
| MTA-016 | Core Modeling | 30-day conversion lookback enforcement | AE | DE | 5 | S4 | Out-of-window touches excluded |
| MTA-017 | Core Modeling | Campaign dimension SCD Type 2 implementation | AE | DE | 8 | S4 | Point-in-time joins reproduce prior state |
| MTA-018 | Core Modeling | Customer hash harmonization and identity rules | AE | DE | 8 | S4 | CRM-web linkage quality above threshold |
| MTA-019 | Core Modeling | Journey path builder using recursive and window logic | AE | DE | 8 | S5 | Benchmark user paths are accurate |
| MTA-020 | Core Modeling | Gold marts for spend, net conversions, and ROAS | AE | BI | 8 | S5 | Finance reconciliation passes |
| MTA-021 | Quality | GE suite for schema and integrity contracts | AE | DE | 8 | S5 | Tests fail correctly on injected bad data |
| MTA-022 | Quality | Attribution conservation test (no ghost revenue) | AE | MLE | 5 | S5 | Attributed totals equal actual totals |
| MTA-023 | Attribution | Baselines: first, last, linear, and time-decay | MLE | AE | 8 | S6 | Baseline outputs published and comparable |
| MTA-024 | Attribution | Markov transition matrix and removal effect engine | MLE | AE | 13 | S6 | Stable channel removal scores |
| MTA-025 | Attribution | Normalization and attributed revenue allocation | MLE | AE | 8 | S6 | Revenue by channel reconciles to net total |
| MTA-026 | ML | Feature store for next-7-day propensity model | MLE | AE | 8 | S7 | Versioned feature sets generated daily |
| MTA-027 | ML | Logistic regression training and calibration | MLE | AE | 8 | S7 | AUC and calibration meet thresholds |
| MTA-028 | ML | Drift monitoring and retraining trigger policy | MLE | DE | 5 | S7 | Drift alerts fire on synthetic shift |
| MTA-029 | ML | User segmentation with K-means and labeling | MLE | BI | 8 | S8 | Segments stable and interpretable |
| MTA-030 | Observability | Monte Carlo freshness, volume, schema monitors | DE | AE | 8 | S8 | Alerts route with severity metadata |
| MTA-031 | Observability | Pixel downtime detector under active spend | DE | BI | 5 | S8 | Incident triggers when views collapse |
| MTA-032 | CI/CD | PR pipeline for dbt tests and GE checkpoints | DE | AE | 8 | S8 | Failed checks block merge |
| MTA-033 | BI | Metabase Attribution War dashboard | BI | AE | 8 | S9 | Last-touch vs Markov deltas validated |
| MTA-034 | BI | Channel waste report and efficiency heatmap | BI | AE | 5 | S9 | High-cost low-impact channels highlighted |
| MTA-035 | BI/ML | Streamlit budget what-if simulator | BI | MLE | 13 | S9 | Scenario output aligned with model assumptions |
| MTA-036 | Adoption | KPI glossary and board-facing metric definitions | BI | AE | 5 | S10 | Executive sign-off on metric definitions |
| MTA-037 | Hardening | Backfill, replay, and disaster recovery drill | DE | AE | 8 | S10 | Recovery runbook proven in timed test |
| MTA-038 | Validation | End-to-end UAT with Marketing and Finance | BI | AE | 5 | S10 | Critical defects closed |
| MTA-039 | Impact | Pre/post budget reallocation experiment framework | MLE | BI | 8 | S10 | Uplift measurement approach approved |
| MTA-040 | Closeout | Thesis evidence pack and reproducibility appendix | AE | BI | 5 | S10 | Final package complete |

## Sprint Milestones
| Sprint | Milestone Theme | Planned Outcomes |
|---|---|---|
| S1 | Platform Ready | Reproducible environment, baseline ingestion, standards finalized |
| S2 | Resilient ELT | Late-arrival replay and reconciliation checks active |
| S3 | Clean Silver Layer | Encoding, locale, parsing, and flattening complete |
| S4 | Source of Truth Core | Session and lookback rules, SCD2, identity linkage complete |
| S5 | Attribution-Ready Gold | Journey marts and contract tests complete |
| S6 | Algorithmic Attribution | Markov model productionized alongside heuristic baselines |
| S7 | Predictive Intelligence | Propensity model with calibration and drift policy |
| S8 | Reliability at Scale | Observability and CI/CD quality gates hardened |
| S9 | Executive Decisioning | Metabase war views and Streamlit simulator delivered |
| S10 | Production and Thesis Readiness | UAT, DR drills, impact framework, and closeout docs complete |

## Backlog Totals
- Total planned points: 273 (note: initial estimate was 283; actual sum of all 40 stories is 273—a 10-point variance likely due to manual calculation).
- Recommended 20 percent contingency: 55 points.
- Effective program envelope: 328 points.

## Definition of Done
- Peer-reviewed implementation merged.
- Tests and quality checks pass.
- Monitoring and runbook updates included when applicable.
- Documentation and stakeholder validation completed.
