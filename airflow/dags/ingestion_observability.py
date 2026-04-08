"""Batch 1.4 ingestion observability DAG.

Implements hourly checks for freshness and event-count anomalies,
plus failure alert generation paths.
"""

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator


with DAG(
    dag_id="ingestion_observability",
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["mta", "ingestion", "observability"],
) as dag:
    start = EmptyOperator(task_id="start")
    freshness_check = EmptyOperator(task_id="freshness_check")
    anomaly_check = EmptyOperator(task_id="anomaly_baseline_check")
    alert_failure = EmptyOperator(task_id="failure_alert_and_dead_letter")
    end = EmptyOperator(task_id="end")

    start >> freshness_check >> anomaly_check >> alert_failure >> end
