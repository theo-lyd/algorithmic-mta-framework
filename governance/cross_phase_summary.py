"""
Cross-Phase Summary: Aggregate CI/CD results across all phases

This module consolidates test results, evidence artifacts, and compliance
status into a unified summary for the entire deployment pipeline.
"""

import json
import os
import sys
import argparse
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path


def collect_phase_artifacts(phase: str, artifacts_dir: str = "artifacts") -> Dict[str, Any]:
    """Collect evidence artifacts for a phase."""
    phase_dir = Path(artifacts_dir) / f"phase-{phase}"

    artifacts = {
        "phase": phase,
        "batches": {},
        "total_artifacts": 0
    }

    if phase_dir.exists():
        for batch_dir in phase_dir.iterdir():
            if batch_dir.is_dir():
                batch_name = batch_dir.name
                batch_artifacts = []

                for artifact_file in batch_dir.glob("**/*.json"):
                    batch_artifacts.append(str(artifact_file))
                    artifacts["total_artifacts"] += 1

                if batch_artifacts:
                    artifacts["batches"][batch_name] = batch_artifacts

    return artifacts


def collect_test_results(phase: str) -> Dict[str, Any]:
    """Collect test results for a phase."""
    test_dir = Path("tests") / f"phase{phase}"

    results = {
        "phase": phase,
        "test_files": [],
        "total_tests": 0
    }

    if test_dir.exists():
        for test_file in test_dir.glob("test_*.py"):
            results["test_files"].append(test_file.name)
            # Parse test count from file
            with open(test_file) as f:
                content = f.read()
                test_count = content.count("def test_")
                results["total_tests"] += test_count

    return results


def check_gate_approval(phase: str) -> Dict[str, Any]:
    """Check Gate D approval status for phase."""
    gate_check = Path("doc") / "batches" / \
        f"phase-{phase}-gate-check-report.md"

    if not gate_check.exists():
        return {
            "phase": phase,
            "gate_d_approved": False,
            "gates_passed": 0,
            "gates_total": 4
        }

    with open(gate_check) as f:
        content = f.read()
        gates_passed = content.count("✓")

        return {
            "phase": phase,
            "gate_d_approved": "3/3 gates passed" in content or gates_passed >= 3,
            "gates_passed": gates_passed,
            "gates_total": 4
        }


def generate_cross_phase_summary(artifacts_dir: str = "artifacts") -> Dict[str, Any]:
    """Generate unified cross-phase summary."""
    summary = {
        "generated_at": datetime.utcnow().isoformat(),
        "phases": [],
        "totals": {
            "phases": 8,
            "phases_complete": 0,
            "total_tests": 0,
            "total_artifacts": 0,
            "gates_passed": 0
        },
        "pipeline_status": "UNKNOWN"
    }

    for phase_num in range(8):
        phase = str(phase_num)

        artifacts = collect_phase_artifacts(phase, artifacts_dir)
        tests = collect_test_results(phase)
        gate = check_gate_approval(phase)

        phase_summary = {
            "phase": phase,
            "gates_approved": gate["gate_d_approved"],
            "tests": tests["total_tests"],
            "artifacts": artifacts["total_artifacts"],
            "batches_complete": len(artifacts["batches"])
        }

        summary["phases"].append(phase_summary)

        summary["totals"]["total_tests"] += tests["total_tests"]
        summary["totals"]["total_artifacts"] += artifacts["total_artifacts"]

        if gate["gate_d_approved"]:
            summary["totals"]["phases_complete"] += 1
            summary["totals"]["gates_passed"] += 1

    # Determine overall status
    if summary["totals"]["phases_complete"] == 8:
        summary["pipeline_status"] = "PRODUCTION_READY"
    elif summary["totals"]["phases_complete"] >= 6:
        summary["pipeline_status"] = "NEARLY_COMPLETE"
    elif summary["totals"]["phases_complete"] >= 3:
        summary["pipeline_status"] = "IN_PROGRESS"
    else:
        summary["pipeline_status"] = "EARLY_STAGE"

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Phase Summary Generator")
    parser.add_argument("--artifacts-dir", type=str, default="artifacts",
                        help="Artifacts root directory")
    parser.add_argument("--output", type=str, default="artifacts/cross-phase-summary.json",
                        help="Output file path")

    args = parser.parse_args()

    summary = generate_cross_phase_summary(args.artifacts_dir)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"\n✓ Cross-phase summary saved: {args.output}")
    print(f"  Pipeline Status: {summary['pipeline_status']}")
    print(f"  Phases Complete: {summary['totals']['phases_complete']}/8")
    print(f"  Total Tests: {summary['totals']['total_tests']}")
    print(f"  Total Artifacts: {summary['totals']['total_artifacts']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
