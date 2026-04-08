"""Validator for Phase VI Batch 6.2: Streamlit What-If Simulator."""

from dashboards.streamlit.whatif_simulator import summarize_simulator
import json
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def validate_batch_62_simulator() -> dict:
    """
    Generate evidence artifacts for Batch 6.2: What-If Simulator.

    Outputs JSON summary to artifacts/phase-6/batch-6-2/
    """
    output_dir = Path(__file__).parent.parent.parent / \
        "artifacts" / "phase-6" / "batch-6-2"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load fixture data
    fixture_path = (
        Path(__file__).parent.parent.parent / "tests" /
        "fixtures" / "phase6" / "simulator_data.json"
    )
    with open(fixture_path) as f:
        fixture = json.load(f)

    # Run simulator
    current_allocation = fixture["current_allocation"]
    proposed_allocation = fixture["proposed_allocation"]
    base_roas = fixture["base_roas_by_channel"]
    propensity_df = pd.DataFrame(fixture["propensity_model_output"])

    simulator_result = summarize_simulator(
        current_allocation, proposed_allocation, base_roas, propensity_df)

    # Build evidence artifact
    evidence = {
        "batch": "6.2",
        "name": "What-If Simulator",
        "status": "passing" if simulator_result["validation"]["is_valid"] else "blocked",
        "timestamp": pd.Timestamp.now().isoformat(),
        "simulator_validation": {
            "budget_constraints_met": simulator_result["validation"]["is_valid"],
            "constraint_violations": simulator_result["validation"]["violations"],
        },
        "revenue_impact": simulator_result["revenue_impact"],
        "scenario_export": {
            "winner_scenario": simulator_result["export"].get("winner_scenario", "N/A"),
            "predicted_lift_pct": simulator_result["export"].get("winner_lift_pct", 0),
            "recommendation": simulator_result["export"].get("recommendation", ""),
        },
        "exit_criteria": {
            "simulator_functional": True,
            "constraints_enforced": bool(simulator_result["validation"]["is_valid"]),
            "revenue_impact_quantified": bool(simulator_result["revenue_impact"]["predicted_lift_eur"] != 0),
            "confidence_intervals_provided": bool(
                simulator_result["revenue_impact"]["confidence_lower_95_pct"] > 0
                and simulator_result["revenue_impact"]["confidence_upper_95_pct"] > 0
            ),
        },
    }

    output_path = output_dir / "simulator_summary.json"
    with open(output_path, "w") as f:
        json.dump(evidence, f, indent=2)

    print(f"✅ Batch 6.2 validation complete: {output_path}")
    return evidence


if __name__ == "__main__":
    result = validate_batch_62_simulator()
    print(json.dumps(result, indent=2))
