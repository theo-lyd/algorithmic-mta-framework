"""Validator for Phase VII Batch 7.1: Production readiness."""

from __future__ import annotations
from production.readiness import summarize_production_readiness

import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_batch_71_production_readiness() -> dict:
    """Generate production readiness evidence artifact for Phase VII Batch 7.1."""
    root = Path(__file__).parent.parent
    fixture_path = root / "tests" / "fixtures" / \
        "phase7" / "production_readiness.json"
    output_dir = root / "artifacts" / "phase-7" / "batch-7-1"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(fixture_path, "r", encoding="utf-8") as handle:
        fixture = json.load(handle)

    summary = summarize_production_readiness(
        replay_runs=fixture["replay_runs"],
        expected_checksum_by_batch=fixture["expected_checksum_by_batch"],
        backfill_windows=fixture["backfill_windows"],
        users=fixture["users"],
        role_permissions=fixture["role_permissions"],
    )

    evidence = {
        "batch": "7.1",
        "name": "Production Readiness",
        "status": "passing" if summary["production_signoff_complete"] else "failing",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
        "exit_criteria": {
            "production_signoff_complete": summary["production_signoff_complete"],
            "dr_replay_passed": summary["disaster_recovery"]["all_checks_passed"],
            "backfill_stress_passed": summary["backfill_stress"]["all_checks_passed"],
            "security_access_signoff": summary["security_access"]["all_checks_passed"],
        },
    }

    output_path = output_dir / "production_readiness_summary.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(evidence, handle, indent=2)

    print(f"Batch 7.1 validation complete: {output_path}")
    return evidence


if __name__ == "__main__":
    print(json.dumps(validate_batch_71_production_readiness(), indent=2))
