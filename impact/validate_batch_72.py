"""Validator for Phase VII Batch 7.2: Impact measurement."""

from __future__ import annotations
from impact.impact_measurement import summarize_impact_measurement

import json
from datetime import datetime
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_batch_72_impact_measurement() -> dict:
    """Generate impact-measurement evidence artifact for Phase VII Batch 7.2."""
    root = Path(__file__).parent.parent
    fixture_path = root / "tests" / "fixtures" / "phase7" / "impact_measurement.json"
    output_dir = root / "artifacts" / "phase-7" / "batch-7-2"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(fixture_path, "r", encoding="utf-8") as handle:
        fixture = json.load(handle)

    pre_period = pd.DataFrame(fixture["pre_period"])
    post_period = pd.DataFrame(fixture["post_period"])

    summary = summarize_impact_measurement(
        pre_period=pre_period,
        post_period=post_period,
        assumptions=fixture["assumptions"],
    )

    evidence = {
        "batch": "7.2",
        "name": "Impact Measurement",
        "status": "passing" if summary["business_value_quantified"] else "failing",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
        "exit_criteria": {
            "business_value_quantified": summary["business_value_quantified"],
            "roas_uplift_positive": summary["impact_delta"]["roas_uplift_pct"] > 0,
            "waste_reduction_positive": summary["impact_delta"]["waste_reduction_pct"] > 0,
            "statistically_significant": summary["confidence"]["statistically_significant_at_95"],
        },
    }

    output_path = output_dir / "impact_measurement_summary.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(evidence, handle, indent=2)

    print(f"Batch 7.2 validation complete: {output_path}")
    return evidence


if __name__ == "__main__":
    print(json.dumps(validate_batch_72_impact_measurement(), indent=2))
