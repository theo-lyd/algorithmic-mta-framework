# Phase 8: Governance Hardening and ML Operations

**Objective**: Operationalize the compliance gaps identified in the Phase 7 audit, advancing from 80–90% aligned to 95%+ production-ready standards for ML governance, cross-phase automation, and structured approval workflows.

---

## Executive Summary

**Current State (Post-Phase 7)**: 
- Phase 7 complete (production readiness, impact measurement, thesis packaging) ✅
- All 7 phases (0–7) with unit tests, validators, evidence artifacts ✅
- Static governance documentation in place ✅
- **Identified Gaps** (3 specific items):
  1. Cross-phase CI/CD enforcement (currently Phase 5 only)
  2. Operationalized ML governance (bias/drift/retrain automation)
  3. Structured Gate D sign-off workflow (not codified as formal approval artifacts)

**Phase 8 Scope**: Implement executable versions of all three gaps, bringing cross-functional automation, ML safeguards, and formal approval tracking to production-grade standards.

---

## Delivery Model

**Phases**: 3 batches over 2 sprints
- **Batch 8.1** (Sprint 1): Cross-phase CI enforcement automation
- **Batch 8.2** (Sprint 1–2): ML governance integration and enforcement
- **Batch 8.3** (Sprint 2): Formal Gate D approval workflows and audit trail

**Success Criteria**: 
- All phases 0–7 automated in unified CI workflow ✓
- ML governance audit executes on every PR with passing tests ✓
- Gate D sign-off artifacts formally tracked for compliance auditing ✓
- 100% test coverage for all governance modules
- 95%+ industry standard alignment verified

---

## Batch 8.1: Cross-Phase CI Enforcement

### Goal
Unify phase validators into a single cross-phase entry/exit gate system that enforces:
- All phases run on every PR/push
- Independent phase gating (each phase has own exit criteria)
- Four global quality gates (A: schema, B: business logic, C: performance, D: stakeholder) aggregate across all phases
- Build fails if any phase fails its exit gate

### Chunks

#### 8.1.1: Unified CI Workflow
**Deliverables**:
- `.github/workflows/cross-phase-checks.yml` ✅ (created in Phase 7 gap implementation)
- Parallel phase validation (matrix build)
- Per-phase artifact upload
- Gate A–D aggregate jobs
- Success/failure reporting

**Acceptance Criteria**:
- All 8 phases (0–7) run in < 15 min total
- Phase failures block build
- Gate A–D jobs run sequentially after all phase validators
- Summary report includes all phase results

**Testing**:
- `tests/phase0/test_*` through `tests/phase7/test_*` all execute
- Each phase must have at least one batch validator (e.g., `validate_batch_7_1.py`)

#### 8.1.2: Phase-Specific Entry/Exit Gates
**Deliverables**:
- Each phase has explicit exit criteria JSON in `artifacts/phase-N/exit_criteria.json`
- Exit criteria include: test pass count, artifact count, no blocker issues
- `governance/phase_exit_validator.py` verifies exit criteria per phase
- CI workflow fails if any phase exit criteria not met

**Acceptance Criteria**:
- Phase 0 exit: bootstrap scripts run, security check passes, standards documented
- Phase 1 exit: ingestion stable, replay orchestration tested, late-data handling verified
- Phase 7 exit: production readiness, impact quantified, thesis packaged (already done)

**Testing**:
- Unit tests: `tests/governance/test_phase_exit_validator.py` (new)
- Integration: cross-phase workflow pre-check validates all exit criteria before deployment

#### 8.1.3: Failure Escalation and Rollback Orchestration
**Deliverables**:
- `governance/ci_failure_handler.py` with escalation rules
- Incident routing: Phase 2 data contract failure → Analytics DRI
- Phase 5 performance gate failure → ML Ops DRI
- Phase 7 rollback gate failure → Block deployment + notify stakeholders
- GitHub Actions integration: auto-create issues for failures

**Acceptance Criteria**:
- Failed CI runs auto-create GitHub issues with labels `phase-N`, `gate-X`, `critical`
- Escalation email sent to DRI within 5 min of failure
- Issue links to failing test, artifact, and evidence

**Testing**:
- Mock CI failure scenarios: schema break, performance regression, blocker issue
- Verify issues created and DRI notified

### Success Metrics (Batch 8.1)
- ✓ All phases gated in unified CI workflow
- ✓ CI runtime < 15 minutes
- ✓ Phase failure blocks build
- ✓ Issue auto-escalation working
- ✓ Zero false negatives (no regression slip through)

---

## Batch 8.2: ML Governance Integration

### Goal
Operationalize ML governance with executable drift detection, bias auditing, and automated retrain triggers integrated into the deployment pipeline.

### Chunks

#### 8.2.1: Drift and Bias Detection at Inference Time
**Deliverables**:
- `ml_governance/drift_bias_automation.py` ✅ (created in Phase 7 gap implementation)
- Functions: `detect_calibration_drift()`, `detect_feature_bias()`, `detect_label_bias()`, `evaluate_retrain_trigger()`
- Calibration drift: Expected Calibration Error (ECE) on prediction distribution vs reference
- Feature bias: KS statistic on feature distributions (current vs. historical)
- Label bias: positive rate shift + group fairness auditing (demographic disparity)

**Acceptance Criteria**:
- Calibration drift detected when ECE increases > 0.15
- Feature bias flagged when KS statistic > 0.25 for any feature
- Label bias detected when positive rate shifts > 10% or group disparity detected
- All detections produce actionable signals with priority levels (NONE, LOW, MEDIUM, HIGH, CRITICAL)

**Testing**:
- Unit tests: ✅ 15 tests in `tests/ml_governance/test_drift_bias_automation.py` (all passing)
- Test cases: no drift (identical distributions), drift detected, bias in single feature, group fairness violation

#### 8.2.2: Explainability and Feature Importance Tracking
**Deliverables**:
- `ml_governance/explainability_metrics.py` (new)
- Functions: `compute_feature_importance()`, `explain_prediction()`, `audit_feature_stability()`
- Feature importance aggregation from model artifacts
- Top-k features for 80% importance coverage
- Prediction-level explainability: SHAP/LIME compatibility

**Acceptance Criteria**:
- Explainability score computed per model
- Top 5 features identified for each model
- 80% importance coverage requires ≤ 20% of total features
- SHAP values optional (nice-to-have); baseline importance tracking mandatory

**Testing**:
- Unit tests: concentrated vs distributed importance, top-k feature ranking

#### 8.2.3: Retrain Trigger and ML Governance Policy Enforcement
**Deliverables**:
- `ml_governance/retrain_policy.py` (new)
- Functions: `evaluate_retrain_trigger()` ✅, `schedule_retrain()`, `enforce_ml_sla()`
- Automatic retrain trigger based on signal priorities
- Retrain trigger automatically logs issue to project board
- ML SLA enforcement: model must be retrained within 30 days or flag alert
- Integration with `governance/gate_d_signoff.py`: retrain policy affects Gate D approval

**Acceptance Criteria**:
- Retrain required: CRITICAL priority issue detected → immediate action required
- Scheduled retrain: HIGH priority issue → schedule for next sprint
- Continued monitoring: LOW/MEDIUM issues → no action but tracked
- Retrain policy enforced via Gate D check before production deployment

**Testing**:
- Unit tests: priority escalation logic, SLA enforcement, issue automation
- Integration: Gate D blocks deployment if retrain overdue

#### 8.2.4: Continuous Monitoring and Alerting
**Deliverables**:
- `ml_governance/monitoring_config.py` (new)
- Monitoring dashboard (Metabase SQL export or static JSON spec)
- Alerts: calibration drift > threshold → Slack, PagerDuty
- Alerts: critical fairness violation → escalate to Legal/Compliance
- Audit trail: all governance decisions logged with timestamp, reason, approver

**Acceptance Criteria**:
- Drift/bias metrics publishable to time-series DB (JSON export format)
- Slack notification sent within 1 min of critical alert
- PagerDuty incident escalation for fairness violations
- Audit log queryable by phase, model, decision type

**Testing**:
- Mock alert scenarios: calibration drift, fairness violation
- Verify Slack/PagerDuty integration (or stubs for test environment)

### Success Metrics (Batch 8.2)
- ✓ All ML models have drift/bias governance in place
- ✓ Retrain triggers automated and logged
- ✓ Alerts fire within SLA
- ✓ 100% audit trail coverage
- ✓ Phase 7 impact measurement protected by ML governance gates

---

## Batch 8.3: Formal Gate D Approval Workflow

### Goal
Codify Gate D sign-off as executable approval artifacts with digital signatures, audit trail, and compliance tracking.

### Chunks

#### 8.3.1: Structured Approval Artifacts
**Deliverables**:
- `governance/gate_d_signoff.py` ✅ (created in Phase 7 gap implementation)
- Approval artifact schema: phase, batch, criteria met, approver list, timestamp, content hash
- Formal sign-off JSON with structure:
  ```json
  {
    "approval_id": "APPROVAL-P7-B7-1-abc123",
    "timestamp": "2026-04-08T00:00:00Z",
    "phase": "7", "batch": "7.1",
    "gate_d_criteria": {
      "stakeholder_sign_off": true,
      "business_value_confirmed": true,
      "no_critical_blockers": true,
      "rollback_verified": true,
      "documentation_complete": true
    },
    "approvers": [
      {"name": "Alice", "role": "Analytics", "timestamp": "...", "signature": "..."}
    ],
    "content_hash": "abc123...",
    "approval_status": "APPROVED"
  }
  ```

**Acceptance Criteria**:
- Approval artifacts stored in `artifacts/gate-d/approval-P{N}-B{N}.json`
- Minimum 2 approvers required (Analytics + Marketing)
- Content hash enables tamper detection
- All 7 phases have approval artifacts before production deploy

**Testing**:
- Unit tests: ✅ 7 tests in `tests/governance/test_gate_d_signoff.py` (all passing)
- Approval generation, rejection on unmet criteria, audit trail verification

#### 8.3.2: Stakeholder Sign-Off Workflow Integration
**Deliverables**:
- GitHub Actions workflow: on PR approval, auto-send sign-off requests
- Sign-off request template with phase, batch, evidence artifacts, criteria checklist
- Approvers sign off via GitHub PR review (or external form for non-technical stakeholders)
- GA workflow updates approval artifact with approver info + timestamp

**Acceptance Criteria**:
- Gate D sign-off request sent automatically on Phase complete
- Approval form includes links to: evidence artifacts, test results, gate checks
- Approvers can sign off, request changes, or block
- Blocked deployment requires explicit approver override + documented reason

**Testing**:
- Mock PR approval → sign-off request generated
- Verify approval artifact updated with approver timestamp

#### 8.3.3: Cross-Phase Compliance Verification
**Deliverables**:
- `governance/cross_phase_summary.py` ✅ (created in Phase 7 gap implementation)
- Function: `verify_cross_phase_compliance()` generates unified summary
- Summary includes: all phases approval status, artifacts present, test pass count
- Deployment blocked if any phase not approved

**Acceptance Criteria**:
- Compliance summary reports 8/8 phases approved or provides specific blockers
- Summary generated automatically by CI workflow (last step)
- Summary artifact: `artifacts/cross-phase-summary.json` with deployment readiness status

**Testing**:
- Unit tests: compliance check across single/multiple phases
- Integration: CI workflow final step verifies compliance before allowing merge

#### 8.3.4: Audit Trail and Compliance Auditing
**Deliverables**:
- `governance/audit_trail.py` (new)
- Functions: `query_approvals()`, `verify_audit_trail()`, `export_compliance_report()`
- Queryable audit log: all approvals, sign-off timestamps, approver roles
- Compliance exports: CSV for auditors, JSON for internal tools
- Immutable audit trail: no post-hoc modifications allowed (content hash validation)

**Acceptance Criteria**:
- Audit log queryable by phase, approver, date range
- CSV export includes: phase, batch, approval_id, approvers, timestamp, status
- Content hash prevents tampering (hash mismatch = alert)
- 7-year retention policy documented (not implemented; documentation only)

**Testing**:
- Unit tests: query mechanics, export format, hash validation
- Integration: verify audit trail survives end-to-end deployment

### Success Metrics (Batch 8.3)
- ✓ All phases have signed approval artifacts
- ✓ Stakeholder sign-off tracked with timestamps
- ✓ Deployment blocked without full approval
- ✓ Audit trail queryable and immutable
- ✓ Compliance exports generated for regulators/auditors

---

## Cross-Batch Integration Points

### CI/CD Orchestration
```
Phase 0–7 validators run (parallel, matrix)
  ↓
Gate A: Schema validation (aggregate across phases)
  ↓
Gate B: Business logic validation (aggregate)
  ↓
Gate C: Performance baseline (aggregate)
  ↓
ML Governance Audit (Batch 8.2): Drift/bias detection,retrain trigger eval
  ↓
Gate D: Stakeholder approval (Batch 8.3): Formal sign-off generation + audit
  ↓
Compliance Summary (Batch 8.3): Cross-phase readiness verification
  ↓
Deploy/Block Decision
```

### Approval Workflow
```
PR submitted
  ↓
All validators pass (Batch 8.1)
  ↓
ML governance audit passes (Batch 8.2)
  ↓
Gate D sign-off request sent to stakeholders (Batch 8.3: Chunk 8.3.2)
  ↓
Approvers review phase artifacts + compliance summary + approval artifact (Batch 8.3: Chunk 8.3.1)
  ↓
Approval artifact signed (Batch 8.3: Chunk 8.3.4 audit trail logged)
  ↓
Compliance verification passes (Batch 8.3: Chunk 8.3.3)
  ↓
Merge to master allowed
```

---

## Risk Mitigation

### Risk 1: Cross-Phase CI Runtime Exceeds SLA
- **Mitigation**: Matrix parallelization reduces runtime from serial 45 min to parallel 12–15 min
- **Contingency**: Add caching for Python dependencies and dbt artifacts

### Risk 2: ML Governance False Positives
- **Mitigation**: Conservative thresholds (ECE > 0.15, KS > 0.25) tuned on Phase 7 data
- **Contingency**: Manual override + documented reason required for false positive suppression

### Risk 3: Stakeholder Sign-Off Bottleneck
- **Mitigation**: Auto-notify approvers, set 24-hour SLA for response
- **Contingency**: Escalate unresponded sign-offs to manager level

### Risk 4: Audit Trail Breach
- **Mitigation**: Content hash + immutability enforcement
- **Contingency**: Weekly audit log integrity checks, backup log sync to secure bucket

---

## Success Criteria (Phase 8)

### Functional
- [ ] All phases 0–7 run in unified cross-phase CI workflow
- [ ] ML governance audit detects drift/bias and triggers retrain
- [ ] Gate D approval artifacts formally signed and tracked
- [ ] Compliance summary generated automatically
- [ ] Audit trail queryable and immutable

### Non-Functional
- [ ] Cross-phase CI runtime < 15 minutes
- [ ] ML governance audit completes in < 2 minutes
- [ ] Gate D approval processing < 5 minutes
- [ ] Stakeholder notification SLA < 1 minute
- [ ] 100% test coverage for all governance modules (15 ML + 7 Gate D tests = 22 test suite)

### Compliance
- [ ] 95%+ alignment with modern industry standards (vs 80–90% currently)
- [ ] Formal approval audit trail for regulatory compliance
- [ ] ML SLA enforcement operational
- [ ] No regressions in Phase 0–7 functionality

---

## Resources and Timeline

**Team Composition**:
- 1 Platform/DevOps engineer (CI/CD expertise) — Batch 8.1
- 1 ML Ops engineer (governance, monitoring) — Batch 8.2
- 1 Data/Analytics engineer (compliance, sign-off workflows) — Batch 8.3

**Timeline**: 2 weeks (2 sprints)
- **Sprint 1 (Days 1–7)**:
  - Batch 8.1 complete (CI workflow, phase exit gates, failure handler)
  - Batch 8.2 integration kickoff (drift/bias module + testing)
- **Sprint 2 (Days 8–14)**:
  - Batch 8.2 complete (ML governance, monitoring, alerting)
  - Batch 8.3 complete (approval artifacts, stakeholder workflow, audit trail)
  - Phase 8 validation and sign-off

**Estimated Effort**: 40 hours (5 days × 2 engineers + 3 days × 1 engineer)

---

## Definition of Done (Phase 8)

1. **Code Complete**:
   - All 3 batch modules implemented and tested
   - 22+ unit tests passing
   - Test coverage ≥ 95% for new modules
   - Code review approved by 2+ teammates

2. **Integration Complete**:
   - CI workflow unified across all phases
   - ML governance integrated into Gate D check
   - Approval artifacts generated automatically
   - Audit trail functional end-to-end

3. **Documentation Complete**:
   - Phase 8 implementation runbook
   - Operator guide for CI debugging
   - Stakeholder sign-off process documented
   - ML governance policy manual (thresholds, escalation rules)

4. **Validation Complete**:
   - All phases pass cross-phase CI
   - ML governance audit executes on Phase 7 data
   - Gate D approval artifacts created and queryable
   - Compliance summary reports 95%+ alignment

5. **Deployed to Production**:
   - Cross-phase CI enabled on master branch
   - Gate D sign-off required for all future deployments
   - ML governance audit monitoring active
   - Audit trail logging to central sink

---

## Exit Criteria

**Phase 8 closes when**:
- ✅ Cross-phase CI runner live and < 15min SLA
- ✅ ML governance audit detects synthetic drift/bias correctly
- ✅ Gate D approval artifacts formally tracked in audit trail
- ✅ All phases 0–7 pass cross-phase validation
- ✅ Stakeholder sign-off process functional
- ✅ 95%+ industry standard compliance verified
- ✅ Phase 8 issues register closed (0 deferred items allowed)

---

## Appendix: Governed Governance

**Governance of Phase 8 Itself**:
- Phase 8 implementation tracked as GitHub issues in `doc/issues/phase-8-issues.md`
- Cross-phase CI validates Phase 8 code + tests
- Gate D sign-off requires Phase 8 code complete + tests passing + evidence artifacts generated
- After Phase 8 deployment, all future phases must comply with cross-phase CI, ML governance, and formal approval workflow
