"""Batch 4.3 conversion propensity feature store, training, and evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split


@dataclass(frozen=True)
class PropensityModelResult:
    model: Any
    feature_columns: list[str]
    metrics: dict[str, float]
    holdout_predictions: pd.DataFrame


def build_feature_store(
    events_df: pd.DataFrame,
    snapshot_ts: str,
    history_window_days: int = 30,
    label_window_days: int = 7,
) -> pd.DataFrame:
    work = events_df.copy()
    work["event_timestamp"] = pd.to_datetime(work["event_timestamp"], utc=True)
    work["is_conversion"] = work["is_conversion"].astype(bool)

    snapshot = pd.Timestamp(snapshot_ts, tz="UTC")
    history_start = snapshot - pd.Timedelta(days=history_window_days)
    label_end = snapshot + pd.Timedelta(days=label_window_days)

    users = sorted(work["user_id"].astype(str).unique())
    rows: list[dict[str, Any]] = []

    for user_id in users:
        user_events = work[work["user_id"] == user_id]
        history = user_events[(user_events["event_timestamp"] >= history_start) & (
            user_events["event_timestamp"] < snapshot)]
        label_window = user_events[(user_events["event_timestamp"] >= snapshot) & (
            user_events["event_timestamp"] < label_end)]

        touchpoints = history[~history["is_conversion"]]
        conversions = history[history["is_conversion"]]
        last_event_ts = history["event_timestamp"].max(
        ) if not history.empty else pd.NaT
        recency_days = float((snapshot - last_event_ts).total_seconds() /
                             86400.0) if pd.notna(last_event_ts) else float(history_window_days)
        active_days = int(
            history["event_timestamp"].dt.date.nunique()) if not history.empty else 0

        rows.append(
            {
                "user_id": user_id,
                "touchpoints_30d": int(touchpoints.shape[0]),
                "conversions_30d": int(conversions.shape[0]),
                "active_days_30d": active_days,
                "recency_days": recency_days,
                "engagement_score": float(touchpoints.shape[0] + 2 * conversions.shape[0]),
                "label_next_7d": int(bool(label_window["is_conversion"].any())),
            }
        )

    return pd.DataFrame(rows).sort_values("user_id").reset_index(drop=True)


def _top_decile_lift(y_true: np.ndarray, y_scores: np.ndarray) -> float:
    base_rate = float(np.mean(y_true))
    if base_rate <= 0:
        return 0.0

    cutoff = max(int(np.ceil(len(y_scores) * 0.1)), min(3, len(y_scores)), 1)
    top_idx = np.argsort(y_scores)[::-1][:cutoff]
    top_rate = float(np.mean(y_true[top_idx])) if len(top_idx) > 0 else 0.0
    return top_rate / base_rate if base_rate > 0 else 0.0


def train_calibrated_logistic(
    feature_store_df: pd.DataFrame,
    random_state: int = 42,
) -> PropensityModelResult:
    feature_columns = [
        "touchpoints_30d",
        "conversions_30d",
        "active_days_30d",
        "recency_days",
        "engagement_score",
    ]
    work = feature_store_df.copy()
    x = work[feature_columns].to_numpy(dtype=float)
    y = work["label_next_7d"].to_numpy(dtype=int)

    stratify = y if len(np.unique(y)) > 1 else None
    x_train, x_test, y_train, y_test, user_train, user_test = train_test_split(
        x,
        y,
        work["user_id"].to_numpy(),
        test_size=0.35,
        random_state=random_state,
        stratify=stratify,
    )

    base_model = LogisticRegression(
        max_iter=500, class_weight="balanced", random_state=random_state)
    calibrated = CalibratedClassifierCV(base_model, cv=3, method="sigmoid")
    calibrated.fit(x_train, y_train)

    y_score = calibrated.predict_proba(x_test)[:, 1]
    y_pred = (y_score >= 0.5).astype(int)

    auc = float(roc_auc_score(y_test, y_score)) if len(
        np.unique(y_test)) > 1 else 0.5
    average_precision = float(average_precision_score(
        y_test, y_score)) if np.sum(y_test) > 0 else 0.0
    lift = float(_top_decile_lift(y_test, y_score))
    brier = float(brier_score_loss(y_test, y_score))
    calibration_drift = float(abs(np.mean(y_score) - np.mean(y_test)))

    holdout = pd.DataFrame(
        {
            "user_id": user_test,
            "y_true": y_test,
            "y_pred": y_pred,
            "y_score": y_score,
        }
    ).sort_values("user_id").reset_index(drop=True)

    metrics = {
        "auc": auc,
        "average_precision": average_precision,
        "top_decile_lift": lift,
        "brier_score": brier,
        "calibration_drift": calibration_drift,
        "positive_rate": float(np.mean(y_test)),
    }
    return PropensityModelResult(
        model=calibrated,
        feature_columns=feature_columns,
        metrics=metrics,
        holdout_predictions=holdout,
    )


def meets_lift_threshold(metrics: dict[str, float], threshold: float = 1.2) -> bool:
    return float(metrics.get("top_decile_lift", 0.0)) >= float(threshold)
