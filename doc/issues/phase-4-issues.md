# Phase 4 Issues Log

Status: Active
Phase: 4
Last Updated: 2026-04-08

## Purpose
Record issues encountered in Phase 4 and how they were resolved.

## Issue Register
## Issue 4.1 - Heuristic benchmarks can over-credit edge channels without reference controls
- What issue was encountered:
	- Simple first/last-touch baselines produced materially different channel allocations with no quality signal for method choice.
- Cause:
	- Heuristic methods encode fixed assumptions and ignore path context.
- Solution applied:
	- Added linear and time-decay baselines plus a benchmark evaluation set with MAE/RMSE scoring.
- How solution was implemented:
	- Implemented `heuristic_attribution.py`, benchmark fixture, tests, and validation summary.
- How to avoid in future:
	- Treat all heuristic outputs as baseline references and score them against a benchmark set before adoption.
- Lesson learned:
	- Baselines are useful only when paired with explicit error metrics.

## Issue 4.2 - Naive channel removal can produce degenerate Markov attribution
- What issue was encountered:
	- Initial channel-removal simulation produced near-zero effects and unstable attribution concentration.
- Cause:
	- Path-pruning alone did not correctly represent channel suppression in transition dynamics.
- Solution applied:
	- Switched to transition-matrix channel removal by redirecting removed-channel incoming flow to NULL.
- How solution was implemented:
	- Updated `markov_attribution.py` removal logic and revalidated normalized shares.
- How to avoid in future:
	- Validate removal mechanics against transition-state semantics, not only path filtering behavior.
- Lesson learned:
	- Markov explainability depends on explicit state-transition intervention logic.

## Issue 4.3 - Small holdout sizes make lift metrics volatile
- What issue was encountered:
	- Top-decile lift fluctuated on compact synthetic holdout samples.
- Cause:
	- Decile slicing on very small test sets is sensitive to single-record rank changes.
- Solution applied:
	- Defined an agreed threshold for this fixture and stabilized top-bucket sizing in evaluation.
- How solution was implemented:
	- Updated propensity lift computation and validator threshold contract.
- How to avoid in future:
	- Use larger holdout windows for production lift gates and document threshold assumptions.
- Lesson learned:
	- Lift gates require data-volume-aware evaluation policy.

## Issue 4.4 - Cluster labels are not inherently business-readable
- What issue was encountered:
	- Raw cluster IDs were technically valid but not actionable for marketing teams.
- Cause:
	- Unsupervised outputs do not include semantic meaning by default.
- Solution applied:
	- Added deterministic segment labeling and playbook mapping from cluster ranking signals.
- How solution was implemented:
	- Extended segmentation pipeline with label and playbook assignment logic.
- How to avoid in future:
	- Always pair clustering output with stakeholder-readable labels and action templates.
- Lesson learned:
	- Segmentation value is realized only when model output is operationally interpretable.

## Issue 4.5 - Revenue allocation can drift when attribution weights are not normalized
- What issue was encountered:
	- Finance bridge reconciliation can fail if per-conversion method weights do not sum to 1.0.
- Cause:
	- Aggregation and merge operations can introduce inconsistent weights across methods.
- Solution applied:
	- Added per-method/per-conversion weight normalization before allocation.
- How solution was implemented:
	- Implemented normalization guardrails and reconciliation assertions in finance bridge logic.
- How to avoid in future:
	- Enforce normalization before any revenue allocation and block publication when reconciliation delta is non-zero.
- Lesson learned:
	- Exact reconciliation is a non-negotiable invariant for attribution-to-finance workflows.

## Issue Template
- What issue was encountered:
- Cause:
- Solution applied:
- How solution was implemented:
- How to avoid in future:
- Lesson learned:
