"""Batch 1.3 Airflow DAG for late-arriving data orchestration.

This DAG models:
- sensor-style delayed file detection
- selective partition replay planning
- reconciliation of expected vs arrived counts
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

from ingestion.pipeline.late_arrival import (
    detect_delayed_files,
    impacted_partitions_for_replay,
    parse_arrived,
    parse_expected,
    reconciliation_summary,
)

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PATH = ROOT / "ingestion" / "samples" / "partner_expected_manifest.json"
ARRIVED_PATH = ROOT / "ingestion" / "samples" / "partner_arrived_manifest.json"
OUT_DIR = ROOT / "doc" / "phase-1"


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def detect_delayed_task(**context):
    expected = parse_expected(_load_json(EXPECTED_PATH))
    arrived = parse_arrived(_load_json(ARRIVED_PATH))
    delayed = detect_delayed_files(expected, arrived)
    payload = [d.__dict__ for d in delayed]
    context["ti"].xcom_push(key="delayed_files", value=payload)


def replay_partitions_task(**context):
    delayed_raw = context["ti"].xcom_pull(task_ids="detect_delayed_partner_files", key="delayed_files") or []
    delayed = parse_expected(delayed_raw)
    partitions = impacted_partitions_for_replay(delayed)
    context["ti"].xcom_push(key="impacted_partitions", value=partitions)


def reconciliation_task(**context):
    expected = parse_expected(_load_json(EXPECTED_PATH))
    arrived = parse_arrived(_load_json(ARRIVED_PATH))
    summary = reconciliation_summary(expected, arrived)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "batch-1-3-reconciliation.csv"
    summary.to_csv(out_path, index=False)


with DAG(
    dag_id="late_arrival_orchestration",
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["mta", "ingestion", "late-arrival"],
) as dag:
    detect_delayed = PythonOperator(
        task_id="detect_delayed_partner_files",
        python_callable=detect_delayed_task,
    )

    replay_partitions = PythonOperator(
        task_id="selective_partition_replay",
        python_callable=replay_partitions_task,
    )

    reconcile = PythonOperator(
        task_id="reconciliation_expected_vs_arrived",
        python_callable=reconciliation_task,
    )

    detect_delayed >> replay_partitions >> reconcile
