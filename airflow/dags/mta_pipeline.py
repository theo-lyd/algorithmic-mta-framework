from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator


with DAG(
    dag_id="mta_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["mta", "marketing", "attribution"],
) as dag:
    start = EmptyOperator(task_id="start")
    ingest = EmptyOperator(task_id="ingest_ga4_events")
    transform = EmptyOperator(task_id="run_dbt_models")
    score = EmptyOperator(task_id="run_markov_and_ml")
    publish = EmptyOperator(task_id="publish_bi_outputs")
    end = EmptyOperator(task_id="end")

    start >> ingest >> transform >> score >> publish >> end
