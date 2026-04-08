"""Batch 1.4 dead-letter and alert handling helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_dead_letter(dead_letter_path: Path, source_name: str, source_file_id: str, raw_record: dict[str, Any], error_message: str) -> None:
    dead_letter_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "dead_letter_ts": datetime.now(timezone.utc).isoformat(),
        "source_name": source_name,
        "source_file_id": source_file_id,
        "error_message": error_message,
        "raw_record": raw_record,
    }
    with dead_letter_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")


def emit_failure_alert(alert_path: Path, title: str, severity: str, details: str) -> None:
    alert_path.parent.mkdir(parents=True, exist_ok=True)
    message = {
        "alert_ts": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "severity": severity,
        "details": details,
    }
    with alert_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(message, ensure_ascii=True) + "\n")
