"""Batch 5.3 artifact versioning helper for reproducible packaging."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    artifact_targets = [
        root / "artifacts" / "phase-4" / "batch-4-2" / "markov_attribution_summary.json",
        root / "artifacts" / "phase-4" / "batch-4-3" / "propensity_model_summary.json",
        root / "artifacts" / "phase-4" / "batch-4-5" / "finance_bridge_summary.json",
    ]

    records = []
    for target in artifact_targets:
        if target.exists():
            records.append(
                {
                    "path": str(target.relative_to(root)),
                    "sha256": sha256_file(target),
                    "size_bytes": target.stat().st_size,
                }
            )

    manifest = {
        "manifest_version": "1.0.0",
        "artifact_count": len(records),
        "artifacts": records,
    }

    out_dir = root / "artifacts" / "phase-5" / "batch-5-3"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "artifact_manifest.json"
    out_file.write_text(json.dumps(manifest, indent=2,
                        ensure_ascii=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
