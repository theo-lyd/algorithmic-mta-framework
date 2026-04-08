# Phase 5 Issues Log

Status: Active
Phase: 5
Last Updated: 2026-04-08

## Purpose
Record issues encountered in Phase 5 and how they were resolved.

## Issue Register
## Issue 5.1 - Pixel downtime can hide behind healthy spend signals
- What issue was encountered:
	- Spend remained active while page-view telemetry dropped to zero, masking tracking outage risk.
- Cause:
	- Spend and telemetry pipelines can drift independently without a combined cross-signal rule.
- Solution applied:
	- Added explicit pixel downtime monitor and severity-based routing.
- How solution was implemented:
	- Implemented `reliability_monitors.py` outage rule, severity mapping, and runbook routing.
- How to avoid in future:
	- Keep spend-vs-telemetry cross-check as a blocking reliability gate.
- Lesson learned:
	- Trust requires coupling business-activity and telemetry signals, not monitoring them separately.

## Issue 5.2 - Revenue governance fails when attribution totals are unchecked
- What issue was encountered:
	- Risk of ghost revenue when attributed totals are not reconciled against conversion net revenue.
- Cause:
	- Transform changes can alter attribution allocations without finance-level invariants.
- Solution applied:
	- Added attribution conservation business rule and GE suite/checkpoint entries.
- How solution was implemented:
	- Implemented `business_rules_phase5.py` and phase 5 GE contract assets.
- How to avoid in future:
	- Enforce conservation checks in CI on every PR touching attribution logic.
- Lesson learned:
	- Finance invariants are governance constraints, not optional QA checks.

## Issue 5.3 - CI artifacts can be non-reproducible without deterministic manifests
- What issue was encountered:
	- Model package artifacts were hard to audit across environments.
- Cause:
	- Packaging lacked versioned checksum manifest.
- Solution applied:
	- Added reproducible packaging script plus SHA-256 artifact manifest generation.
- How solution was implemented:
	- Introduced `package_model_artifacts.sh` and `version_artifacts.py` with CI workflow integration.
- How to avoid in future:
	- Treat checksum manifests as required deploy artifacts.
- Lesson learned:
	- Reproducibility is an explicit output, not an assumption.

## Issue 5.4 - Cost overruns emerge late without thresholded alerts
- What issue was encountered:
	- Spend visibility existed but threshold-triggered escalation was missing.
- Cause:
	- Cost reporting was descriptive only, not policy-driven.
- Solution applied:
	- Added cost dashboard summary and threshold alert policy.
- How solution was implemented:
	- Implemented performance/cost module with budget-percentage alerts and severity outputs.
- How to avoid in future:
	- Maintain explicit budget thresholds and review alert calibration periodically.
- Lesson learned:
	- Cost reliability requires enforceable thresholds, not just dashboards.

## Issue Template
- What issue was encountered:
- Cause:
- Solution applied:
- How solution was implemented:
- How to avoid in future:
- Lesson learned:
