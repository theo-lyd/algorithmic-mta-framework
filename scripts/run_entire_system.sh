#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
LOG_DIR="${ROOT_DIR}/logs"
LOG_FILE="${LOG_DIR}/full_system_run_${TIMESTAMP}.log"

INTERACTIVE=false
SKIP_INSTALL=false

for arg in "$@"; do
  case "$arg" in
    --interactive)
      INTERACTIVE=true
      ;;
    --skip-install)
      SKIP_INSTALL=true
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Usage: $0 [--interactive] [--skip-install]"
      exit 2
      ;;
  esac
done

mkdir -p "${LOG_DIR}"
cd "${ROOT_DIR}"

run_step() {
  local name="$1"
  local cmd="$2"
  echo
  echo "==> ${name}"
  echo "    ${cmd}"
  if ! bash -lc "${cmd}" >>"${LOG_FILE}" 2>&1; then
    echo "[FAIL] ${name}"
    echo "Log: ${LOG_FILE}"
    exit 1
  fi
  echo "[PASS] ${name}"
}

run_non_blocking_step() {
  local name="$1"
  local cmd="$2"
  echo
  echo "==> ${name}"
  echo "    ${cmd}"
  if ! bash -lc "${cmd}" >>"${LOG_FILE}" 2>&1; then
    echo "[WARN] ${name} reported issues (continuing)."
    return 0
  fi
  echo "[PASS] ${name}"
}

echo "Starting full system run at ${TIMESTAMP}"
echo "Root: ${ROOT_DIR}"
echo "Log: ${LOG_FILE}"

echo "Full System Run" >"${LOG_FILE}"
echo "Timestamp: ${TIMESTAMP}" >>"${LOG_FILE}"
echo "Root: ${ROOT_DIR}" >>"${LOG_FILE}"
echo "" >>"${LOG_FILE}"

if [[ "${SKIP_INSTALL}" == "false" ]]; then
  run_step "Install dependencies" "python -m pip install --upgrade pip && pip install -r requirements.txt"
else
  echo "Skipping dependency installation (--skip-install)."
fi

run_step "Run all unit tests" "PYTHONPATH=. python -m unittest discover -s tests -p 'test_*.py'"

# Phase 2-5 core validators
run_step "Validate text normalization" "PYTHONPATH=. python ingestion/pipeline/validate_text_normalization.py"
run_step "Validate financial normalization" "PYTHONPATH=. python ingestion/pipeline/validate_financial_normalization.py"
run_step "Validate silver harmonization" "PYTHONPATH=. python ingestion/pipeline/validate_silver_harmonization.py"
run_step "Validate silver contracts" "PYTHONPATH=. python ingestion/pipeline/validate_silver_contracts.py"
run_step "Validate campaign SCD2" "PYTHONPATH=. python ingestion/pipeline/validate_campaign_scd2.py"
run_step "Validate identity harmonization" "PYTHONPATH=. python ingestion/pipeline/validate_identity_harmonization.py"
run_step "Validate journey pathing" "PYTHONPATH=. python ingestion/pipeline/validate_journey_pathing.py"
run_step "Validate heuristic attribution" "PYTHONPATH=. python ingestion/pipeline/validate_heuristic_attribution.py"
run_step "Validate markov attribution" "PYTHONPATH=. python ingestion/pipeline/validate_markov_attribution.py"
run_step "Validate propensity model" "PYTHONPATH=. python ingestion/pipeline/validate_propensity_model.py"
run_step "Validate behavioral segmentation" "PYTHONPATH=. python ingestion/pipeline/validate_behavioral_segmentation.py"
run_step "Validate finance bridge" "PYTHONPATH=. python ingestion/pipeline/validate_finance_bridge.py"
run_step "Validate reliability monitors" "PYTHONPATH=. python ingestion/pipeline/validate_reliability_monitors.py"
run_step "Validate phase 5 business rules" "PYTHONPATH=. python ingestion/pipeline/validate_business_rules_phase5.py"
run_step "Validate CI/CD automation" "PYTHONPATH=. python ingestion/pipeline/validate_cicd_automation.py"
run_step "Validate performance and cost" "PYTHONPATH=. python ingestion/pipeline/validate_performance_cost.py"

# Phase 6 validators
run_step "Validate metabase governance dashboard" "PYTHONPATH=. python dashboards/metabase/validate_batch_61.py"
run_step "Validate streamlit simulator" "PYTHONPATH=. python dashboards/streamlit/validate_batch_62.py"
run_step "Validate governance layer" "PYTHONPATH=. python dashboards/governance/validate_batch_63.py"

# Phase 7 validators
run_step "Validate production readiness" "PYTHONPATH=. python production/validate_batch_71.py"
run_step "Validate impact measurement" "PYTHONPATH=. python impact/validate_batch_72.py"
run_step "Validate thesis package" "PYTHONPATH=. python thesis/validate_batch_73.py"

# Governance automation checks (may surface actionable warnings by design)
run_non_blocking_step "Run ML governance audit" "PYTHONPATH=. python ml_governance/drift_bias_automation.py --mode=report --phase=all --output artifacts/gate-d/ml_governance_audit.json"
run_non_blocking_step "Run Gate D compliance verification" "PYTHONPATH=. python governance/gate_d_signoff.py --mode=verify --branch=master --output artifacts/gate-d/gate_d_signoff_report.json"
run_step "Generate cross-phase summary" "PYTHONPATH=. python governance/cross_phase_summary.py --artifacts-dir=artifacts --output artifacts/cross-phase-summary.json"

echo
echo "Full system run completed successfully."
echo "Execution log: ${LOG_FILE}"
echo "Summary artifact: artifacts/cross-phase-summary.json"

if [[ "${INTERACTIVE}" == "true" ]]; then
  echo
  read -r -p "Press Enter to close..." _
fi
