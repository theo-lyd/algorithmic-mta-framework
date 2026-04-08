"""Batch 2.4 failed-record quarantine and remediation helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def quarantine_failed_rows(
    df: pd.DataFrame,
    failed_mask: pd.Series,
    reason: str,
    quarantine_path: Path,
    remediation_path: Path,
) -> int:
    failed_df = df[failed_mask].copy()
    if failed_df.empty:
        return 0

    quarantine_path.parent.mkdir(parents=True, exist_ok=True)
    remediation_path.parent.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).isoformat()

    with quarantine_path.open("a", encoding="utf-8") as f:
        for _, row in failed_df.iterrows():
            payload = {
                "quarantine_ts": ts,
                "reason": reason,
                "record": row.to_dict(),
            }
            f.write(json.dumps(payload, ensure_ascii=True, default=str) + "\n")

    remediation_df = failed_df.copy()
    remediation_df["quarantine_reason"] = reason
    remediation_df["quarantine_ts"] = ts
    remediation_df.to_csv(remediation_path, index=False, encoding="utf-8")

    return int(failed_df.shape[0])
