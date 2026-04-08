"""Batch 5.4 validation runner for performance and cost baselines."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ingestion.pipeline.performance_cost import (
    cost_dashboard,
    incremental_strategy_optimization,
    materialization_tuning_recommendations,
    profile_queries,
    threshold_alerts,
)


def main() -> None:
    base = Path(__file__).resolve().parents[2]
    payload = json.loads((base / "tests" / "fixtures" / "phase5" /
                         "performance_cost_data.json").read_text(encoding="utf-8"))

    query_runs_df = pd.DataFrame(payload["query_runs"])
    partition_df = pd.DataFrame(payload["partition_stats"])
    cost_df = pd.DataFrame(payload["cost_rows"])

    profile_df = profile_queries(query_runs_df)
    rec_df = materialization_tuning_recommendations(profile_df)
    incremental_df = incremental_strategy_optimization(partition_df)
    dashboard = cost_dashboard(cost_df, float(payload["monthly_budget_eur"]))
    alerts = threshold_alerts(dashboard, budget_threshold=0.75)

    out_dir = base / "artifacts" / "phase-5" / "batch-5-4"
    out_dir.mkdir(parents=True, exist_ok=True)

    profile_path = out_dir / "query_profile.csv"
    profile_df.to_csv(profile_path, index=False, encoding="utf-8")

    summary = {
        "recommendations": rec_df.to_dict("records"),
        "incremental_plan": incremental_df.to_dict("records"),
        "cost_dashboard": dashboard,
        "cost_alert": alerts,
    }

    out_file = out_dir / "performance_cost_summary.json"
    out_file.write_text(json.dumps(summary, indent=2,
                        ensure_ascii=True), encoding="utf-8")
    print(out_file.relative_to(base))


if __name__ == "__main__":
    main()
