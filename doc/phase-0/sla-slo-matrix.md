# Phase 0 SLA/SLO Matrix

Status: Implemented for Batch 0.1
Date: 2026-04-08

## Scope
This matrix defines latency, completeness, and freshness standards for core datasets and reporting outputs.

## SLA/SLO Definitions
- SLA: contractual/operational promise for service performance.
- SLO: internal objective target to keep SLA healthy.
- SLI: measured indicator used to evaluate SLO/SLA.

## Matrix

| Domain | SLI | SLO Target | SLA Target | Measurement Window | Owner | Breach Action |
|---|---|---|---|---|---|---|
| Ingestion (marketing_events) | End-to-end ingest latency (event time to Bronze availability) | <= 60 min for 95% | <= 90 min for 99% | Daily rolling | DE | Trigger replay check and source connector incident |
| Ingestion (partner feeds) | Late-arrival correction latency | Replay completed <= 120 min after file arrival | <= 180 min | Daily rolling | DE | Sensor escalation and targeted partition rerun |
| Silver quality | Completeness ratio (expected rows / received rows) | >= 99.5% | >= 99.0% | Daily | AE | Block Gold publish, open data quality incident |
| Silver quality | Schema conformity | 100% required columns present | 99.9% | Per run | AE | Fail pipeline, notify on-call, quarantine records |
| Gold attribution | Freshness (last successful build age) | <= 4 hours | <= 6 hours | Hourly check | AE | Run catch-up job and issue stakeholder notice |
| Gold finance | Reconciliation integrity (attributed vs actual conversions) | 100% equality within tolerance 0.0 | 100% | Per run | AE + BI | Halt dashboard publish, investigate rule drift |
| BI dashboards | Dashboard data freshness | <= 6 hours | <= 8 hours | Hourly check | BI | Mark dashboard degraded and notify business owners |

## Operational Policies
- Error budget policy:
  - Monthly error budget for freshness SLO breaches: 5% of checks.
  - If consumed > 80%, freeze non-critical changes until stabilized.
- Escalation policy:
  - P1: SLA breach affecting executive reporting.
  - P2: SLO breach with potential same-day impact.
  - P3: Warning threshold exceeded without business impact.

## Why These Targets

| Choice | Alternatives Considered | Why Chosen | Trade-offs | Reconsider When |
|---|---|---|---|---|
| 60-minute ingestion SLO | 15-minute near-real-time target | Aligns with batch ingestion and partner lag reality | Not true real-time analytics | Business moves to minute-level spend optimization decisions |
| 99.5% completeness SLO | 100% strict objective | Balances practical ingestion variability and reliability | Small tolerated shortfalls require replay controls | Compliance/regulatory needs require hard 100% ingestion |
| 4-hour Gold freshness SLO | 24-hour daily reporting | Supports daily and intraday stakeholder decisioning | More frequent processing cost | Stakeholders shift to daily-only review cadence |

## Verification Checklist
- SLI definitions documented.
- SLO/SLA targets documented with owners.
- Breach actions and escalation states documented.
- Error budget policy defined.
