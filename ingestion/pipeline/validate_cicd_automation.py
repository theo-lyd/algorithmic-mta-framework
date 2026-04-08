"""Batch 5.3 validation runner for CI/CD automation and artifact versioning."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    base = Path(__file__).resolve().parents[2]
    required_workflows = [
        ".github/workflows/phase5-pr-checks.yml",
        ".github/workflows/phase5-deploy.yml",
    ]

    existing = []
    missing = []
    for rel_path in required_workflows:
        if (base / rel_path).exists():
            existing.append(rel_path)
        else:
            missing.append(rel_path)

    out_dir = base / "artifacts" / "phase-5" / "batch-5-3"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "required_workflows": required_workflows,
        "existing_workflows": existing,
        "missing_workflows": missing,
        "workflows_complete": len(missing) == 0,
    }

    out_file = out_dir / "cicd_automation_summary.json"
    out_file.write_text(json.dumps(summary, indent=2,
                        ensure_ascii=True), encoding="utf-8")
    print(out_file.relative_to(base))


if __name__ == "__main__":
    main()
