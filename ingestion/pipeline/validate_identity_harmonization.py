"""Batch 3.2 validation runner for unified identity harmonization."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ingestion.pipeline.identity_harmonization import resolve_identity, summarize_resolution


def main() -> None:
    base_dir = Path(__file__).resolve().parents[2]
    records_path = base_dir / "tests" / "fixtures" / \
        "phase3" / "identity_records.json"
    out_dir = base_dir / "artifacts" / "phase-3" / "batch-3-2"
    out_dir.mkdir(parents=True, exist_ok=True)

    records_df = pd.DataFrame(json.loads(
        records_path.read_text(encoding="utf-8")))
    result = resolve_identity(records_df)

    unresolved_path = out_dir / "unresolved_identity_queue.csv"
    result.unresolved_queue.to_csv(
        unresolved_path, index=False, encoding="utf-8")

    summary = {
        "resolution_summary": summarize_resolution(result),
        "unresolved_queue_path": str(unresolved_path.relative_to(base_dir)),
        "resolved_records": result.resolved_identities[["record_id", "customer_hash", "identity_confidence_score"]]
        .sort_values("record_id")
        .to_dict("records"),
        "unresolved_records": result.unresolved_queue[["record_id", "reason"]]
        .sort_values("record_id")
        .to_dict("records"),
    }

    summary_path = out_dir / "identity_harmonization_summary.json"
    summary_path.write_text(json.dumps(
        summary, indent=2, ensure_ascii=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True, default=str))


if __name__ == "__main__":
    main()
