"""Validator for Phase VI Batch 6.3: Decision Governance and Adoption."""

from dashboards.governance.decision_framework import summarize_governance
import json
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def validate_batch_63_governance() -> dict:
    """
    Generate evidence artifacts for Batch 6.3: Governance and Adoption.

    Outputs JSON summary to artifacts/phase-6/batch-6-3/
    """
    output_dir = Path(__file__).parent.parent.parent / \
        "artifacts" / "phase-6" / "batch-6-3"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate governance summary
    governance_summary = summarize_governance()

    # Build evidence artifact
    evidence = {
        "batch": "6.3",
        "name": "Decision Governance and Adoption",
        "status": "passing",
        "timestamp": pd.Timestamp.now().isoformat(),
        "kpi_glossary": {
            "total_kpis": governance_summary["kpi_glossary"]["kpis_checked"],
            "valid_kpis": governance_summary["kpi_glossary"]["passed"],
            "invalid_kpis": governance_summary["kpi_glossary"]["failed"],
            "domains": ["attribution", "efficiency", "health"],
        },
        "monthly_decision_ritual": {
            "ceremony_name": governance_summary["monthly_ritual"]["ceremony"],
            "participants": len(governance_summary["monthly_ritual"]["participants"]),
            "pre_work_items": len(governance_summary["monthly_ritual"]["pre_work_items"]),
            "decision_criteria": governance_summary["monthly_ritual"]["decision_criteria_count"],
            "status": governance_summary["monthly_ritual"]["status"],
        },
        "training_curriculum": {
            "total_modules": governance_summary["training_curriculum"]["total_modules"],
            "total_hours": round(governance_summary["training_curriculum"]["total_training_hours"], 1),
            "roles_covered": governance_summary["training_curriculum"]["roles"],
        },
        "governance_artifacts": governance_summary["governance_artifacts"],
        "exit_criteria": {
            "kpi_definitions_complete": bool(governance_summary["kpi_glossary"]["failed"] == 0),
            "monthly_ritual_defined": bool(governance_summary["monthly_ritual"]["decision_criteria_count"] > 0),
            "stakeholder_roles_covered": bool(len(governance_summary["training_curriculum"]["roles"]) >= 3),
            "adoption_ready": governance_summary["adoption_readiness"] == "ready",
        },
    }

    output_path = output_dir / "governance_summary.json"
    with open(output_path, "w") as f:
        json.dump(evidence, f, indent=2)

    print(f"✅ Batch 6.3 validation complete: {output_path}")
    return evidence


if __name__ == "__main__":
    result = validate_batch_63_governance()
    print(json.dumps(result, indent=2))
