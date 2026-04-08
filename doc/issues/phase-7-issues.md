# Phase 7 Issues Register

Status: Complete
Phase: 7
Last Updated: 2026-04-08

## Purpose
Track key implementation issues from production hardening, impact measurement, and thesis packaging.

## Issue Register

### Issue 7.1.1: Replay determinism criteria ambiguity
- What issue was encountered: Initial DR scope focused on count parity only, which could miss content drift.
- Cause: Replay acceptance criteria lacked checksum verification in early design notes.
- Solution applied: Added checksum parity and event-count parity checks per replay batch.
- How solution was implemented: `run_disaster_recovery_replay_testing` now validates both expected count and checksum.
- How to avoid in future: Define replay acceptance criteria as count + checksum + RTO/RPO before coding.
- Lesson learned: Determinism should be verified semantically, not only volumetrically.

### Issue 7.1.2: Backfill throughput threshold realism
- What issue was encountered: Early threshold draft of 2000 rows/s risked failing realistic historical windows.
- Cause: Threshold calibrated to best-case windows only.
- Solution applied: Set minimum throughput threshold to 1500 rows/s and documented runtime/error co-constraints.
- How solution was implemented: Encoded threshold parameters in `run_backfill_stress_tests` with breach reporting.
- How to avoid in future: Use p10-p90 historical throughput to set practical stress-test thresholds.
- Lesson learned: Stress thresholds must be strict but operationally attainable.

### Issue 7.1.3: Access audit least-privilege gap risk
- What issue was encountered: Role checks did not initially reject sensitive permissions explicitly.
- Cause: Draft audit emphasized required permissions but omitted forbidden permission checks.
- Solution applied: Added restricted permission deny-list validation.
- How solution was implemented: `run_security_access_audit` now fails users/roles carrying restricted permissions.
- How to avoid in future: Include both allow-list and deny-list in all access audits.
- Lesson learned: Least-privilege enforcement requires explicit denial checks.

### Issue 7.2.1: Confidence computation dependency risk
- What issue was encountered: Using scipy for statistical testing would add dependency overhead.
- Cause: Requirement for confidence metrics without new environment complexity.
- Solution applied: Implemented normal CDF via `math.erf` and z-test approximation.
- How solution was implemented: Added `_normal_cdf` helper and two-tailed p-value logic in `quantify_confidence_and_sensitivity`.
- How to avoid in future: Prefer standard library implementations when dependency value is marginal.
- Lesson learned: Lightweight statistical validation can be production-sufficient for reporting layers.

### Issue 7.2.2: Sensitivity range interpretation
- What issue was encountered: Sensitivity band could span negative uplift despite significant average uplift.
- Cause: Combined uncertainty assumptions (attribution + elasticity) widened range.
- Solution applied: Kept full uncertainty range visible instead of clipping to positive outcomes.
- How solution was implemented: Reported raw lower/upper sensitivity bounds in evidence output.
- How to avoid in future: Pair significance metrics with scenario sensitivity to avoid overconfidence.
- Lesson learned: Confidence and sensitivity answer different questions and should be shown together.

### Issue 7.3.1: Thesis package completeness criteria drift
- What issue was encountered: Review-readiness definition differed between technical and executive stakeholders.
- Cause: No unified pass rule for appendix, blueprint, and deck.
- Solution applied: Enforced aggregate readiness rule requiring all three components to pass.
- How solution was implemented: `summarize_thesis_package` computes `thesis_package_review_ready` only when all component checks pass.
- How to avoid in future: Define cross-audience acceptance criteria before package assembly.
- Lesson learned: Defense readiness is a system property, not a document property.

## Deferred Item
- Channel-specific elasticity calibration remains deferred to next hardening cycle; current approach is documented with sensitivity safeguards.

## Final Status
- Open blockers: 0
- Resolved issues: 6
- Deferred issues: 1
