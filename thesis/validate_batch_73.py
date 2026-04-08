"""Validator for Phase VII Batch 7.3: Thesis package and defense narrative."""

from __future__ import annotations
from thesis.narrative_package import summarize_thesis_package

import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_batch_73_thesis_package() -> dict:
    """Generate thesis-package evidence artifact for Phase VII Batch 7.3."""
    root = Path(__file__).parent.parent
    fixture_path = root / "tests" / "fixtures" / "phase7" / "thesis_package.json"
    output_dir = root / "artifacts" / "phase-7" / "batch-7-3"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(fixture_path, "r", encoding="utf-8") as handle:
        fixture = json.load(handle)

    summary = summarize_thesis_package(
        pipeline_components=fixture["pipeline_components"],
        validation_commands=fixture["validation_commands"],
        evidence_artifacts=fixture["evidence_artifacts"],
        environment_snapshot=fixture["environment_snapshot"],
        value_metrics=fixture["value_metrics"],
        governance_summary=fixture["governance_summary"],
        operating_model=fixture["operating_model"],
        technical_risks=fixture["technical_risks"],
    )

    evidence = {
        "batch": "7.3",
        "name": "Thesis and Board Narrative Package",
        "status": "passing" if summary["thesis_package_review_ready"] else "failing",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
        "exit_criteria": {
            "methods_appendix_complete": summary["methods_appendix"]["reproducibility_ready"],
            "business_blueprint_complete": summary["business_blueprint"]["exec_blueprint_ready"],
            "defense_deck_complete": summary["defense_deck"]["review_ready"],
        },
    }

    output_path = output_dir / "thesis_package_summary.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(evidence, handle, indent=2)

    print(f"Batch 7.3 validation complete: {output_path}")
    return evidence


if __name__ == "__main__":
    print(json.dumps(validate_batch_73_thesis_package(), indent=2))
