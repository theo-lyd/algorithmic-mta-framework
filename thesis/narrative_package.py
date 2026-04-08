"""Phase VII Batch 7.3: thesis and board narrative packaging."""

from __future__ import annotations

from typing import Dict, List


def build_methods_reproducibility_appendix(
    pipeline_components: List[Dict],
    validation_commands: List[str],
    evidence_artifacts: List[str],
    environment_snapshot: Dict,
) -> Dict:
    """Build methods appendix with reproducibility controls."""
    required_component_names = {
        "bronze_ingestion",
        "silver_harmonization",
        "attribution_modeling",
        "bi_governance_layer",
    }
    present_names = {component["name"] for component in pipeline_components}
    missing = sorted(required_component_names - present_names)

    reproducibility_score = 100.0
    reproducibility_score -= 15.0 if missing else 0.0
    reproducibility_score -= 10.0 if len(validation_commands) < 6 else 0.0
    reproducibility_score -= 10.0 if len(evidence_artifacts) < 6 else 0.0

    return {
        "appendix_sections": [
            "Data lineage and architecture",
            "Modeling methods and assumptions",
            "Validation protocol and commands",
            "Evidence artifact index",
            "Environment and dependency snapshot",
        ],
        "pipeline_components": pipeline_components,
        "validation_commands": validation_commands,
        "evidence_artifacts": evidence_artifacts,
        "environment_snapshot": environment_snapshot,
        "missing_required_components": missing,
        "reproducibility_score": max(0.0, reproducibility_score),
        "reproducibility_ready": len(missing) == 0,
    }


def build_business_blueprint_summary(
    value_metrics: Dict,
    governance_summary: Dict,
    operating_model: Dict,
) -> Dict:
    """Build executive blueprint that maps value to operations."""
    headline = (
        f"ROAS +{value_metrics['roas_uplift_pct']:.1f}% and waste -"
        f"{value_metrics['waste_reduction_pct']:.1f}% with production controls in place."
    )

    return {
        "headline": headline,
        "value_metrics": value_metrics,
        "governance_summary": governance_summary,
        "operating_model": operating_model,
        "board_decisions_supported": [
            "Quarterly channel budget mix",
            "Monthly reallocation approvals",
            "Data quality and resilience investment",
        ],
        "exec_blueprint_ready": (
            value_metrics["roas_uplift_pct"] > 0
            and value_metrics["waste_reduction_pct"] > 0
            and governance_summary.get("production_signoff_complete", False)
        ),
    }


def build_final_defense_deck(
    methods_appendix: Dict,
    business_blueprint: Dict,
    technical_risks: List[Dict],
) -> Dict:
    """Build final defense deck storyline for technical and strategic review."""
    slides = [
        {"slide": 1, "title": "Problem Framing and Research Question"},
        {"slide": 2, "title": "Data Foundation and Governance Baseline"},
        {"slide": 3, "title": "Attribution and Propensity Method Stack"},
        {"slide": 4, "title": "Production Hardening Evidence"},
        {"slide": 5, "title": "Experiment Design and Causal Guardrails"},
        {"slide": 6, "title": "ROAS Uplift and Waste Reduction Outcomes"},
        {"slide": 7, "title": "Confidence Intervals and Sensitivity"},
        {"slide": 8, "title": "Executive Operating Blueprint"},
        {"slide": 9, "title": "Risk Register and Mitigations"},
        {"slide": 10, "title": "Thesis Contributions and Future Work"},
    ]

    unresolved_risks = [
        risk for risk in technical_risks if risk["status"] != "mitigated"]

    return {
        "slides": slides,
        "technical_storyline_complete": methods_appendix["reproducibility_ready"],
        "strategic_storyline_complete": business_blueprint["exec_blueprint_ready"],
        "unresolved_risks": unresolved_risks,
        "review_ready": (
            methods_appendix["reproducibility_ready"]
            and business_blueprint["exec_blueprint_ready"]
            and len(unresolved_risks) == 0
        ),
    }


def summarize_thesis_package(
    pipeline_components: List[Dict],
    validation_commands: List[str],
    evidence_artifacts: List[str],
    environment_snapshot: Dict,
    value_metrics: Dict,
    governance_summary: Dict,
    operating_model: Dict,
    technical_risks: List[Dict],
) -> Dict:
    """Build Batch 7.3 summary for validator and gate-check consumption."""
    appendix = build_methods_reproducibility_appendix(
        pipeline_components,
        validation_commands,
        evidence_artifacts,
        environment_snapshot,
    )
    blueprint = build_business_blueprint_summary(
        value_metrics,
        governance_summary,
        operating_model,
    )
    deck = build_final_defense_deck(appendix, blueprint, technical_risks)

    return {
        "batch": "7.3",
        "name": "Thesis and Board Narrative Package",
        "methods_appendix": appendix,
        "business_blueprint": blueprint,
        "defense_deck": deck,
        "thesis_package_review_ready": (
            appendix["reproducibility_ready"]
            and blueprint["exec_blueprint_ready"]
            and deck["review_ready"]
        ),
    }
