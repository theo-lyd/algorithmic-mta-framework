"""Batch 4.4 behavioral segmentation with RFM and engagement features."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class SegmentationResult:
    labeled_features: pd.DataFrame
    selected_k: int
    silhouette: float
    stability: float


def engineer_rfm_features(events_df: pd.DataFrame, reference_ts: str) -> pd.DataFrame:
    work = events_df.copy()
    work["event_timestamp"] = pd.to_datetime(work["event_timestamp"], utc=True)
    work["revenue_eur"] = work["revenue_eur"].fillna(0.0).astype(float)

    reference = pd.Timestamp(reference_ts, tz="UTC")
    window_start = reference - pd.Timedelta(days=90)
    window = work[(work["event_timestamp"] >= window_start)
                  & (work["event_timestamp"] < reference)]

    rows: list[dict[str, Any]] = []
    for user_id, group in window.groupby("user_id", sort=False):
        last_event = group["event_timestamp"].max()
        recency_days = float(
            (reference - last_event).total_seconds() / 86400.0)
        frequency = int(group.shape[0])
        monetary = float(group["revenue_eur"].sum())
        engagement = int(group[~group["is_conversion"]].shape[0])

        rows.append(
            {
                "user_id": user_id,
                "recency_days": recency_days,
                "frequency_90d": frequency,
                "monetary_90d": monetary,
                "engagement_90d": engagement,
            }
        )

    return pd.DataFrame(rows).sort_values("user_id").reset_index(drop=True)


def train_kmeans_segments(
    feature_df: pd.DataFrame,
    cluster_options: tuple[int, ...] = (2, 3, 4, 5),
    random_state: int = 42,
) -> SegmentationResult:
    work = feature_df.copy()
    numeric_cols = ["recency_days", "frequency_90d",
                    "monetary_90d", "engagement_90d"]
    x = work[numeric_cols].to_numpy(dtype=float)

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)

    best_k = cluster_options[0]
    best_silhouette = -1.0
    best_labels: np.ndarray | None = None

    for k in cluster_options:
        if len(work) <= k:
            continue
        model = KMeans(n_clusters=k, n_init=20, random_state=random_state)
        labels = model.fit_predict(x_scaled)
        score = float(silhouette_score(x_scaled, labels))
        if score > best_silhouette:
            best_silhouette = score
            best_k = k
            best_labels = labels

    if best_labels is None:
        fallback = KMeans(n_clusters=2, n_init=20, random_state=random_state)
        best_labels = fallback.fit_predict(x_scaled)
        best_k = 2
        best_silhouette = float(silhouette_score(x_scaled, best_labels))

    stability_scores: list[float] = []
    for seed in [1, 7, 11, 19, 29]:
        model = KMeans(n_clusters=best_k, n_init=20, random_state=seed)
        labels = model.fit_predict(x_scaled)
        stability_scores.append(
            float(adjusted_rand_score(best_labels, labels)))

    work["cluster_id"] = best_labels
    return SegmentationResult(
        labeled_features=work,
        selected_k=int(best_k),
        silhouette=float(best_silhouette),
        stability=float(np.mean(stability_scores)),
    )


def label_segments_with_playbooks(segmentation_df: pd.DataFrame) -> pd.DataFrame:
    work = segmentation_df.copy()
    cluster_stats = (
        work.groupby("cluster_id", as_index=False)
        .agg(
            recency_days=("recency_days", "mean"),
            frequency_90d=("frequency_90d", "mean"),
            monetary_90d=("monetary_90d", "mean"),
            engagement_90d=("engagement_90d", "mean"),
        )
    )

    cluster_stats["rank_score"] = (
        -cluster_stats["recency_days"]
        + cluster_stats["frequency_90d"]
        + cluster_stats["monetary_90d"] /
        (cluster_stats["monetary_90d"].max() + 1e-6)
        + cluster_stats["engagement_90d"]
    )
    cluster_stats = cluster_stats.sort_values(
        "rank_score", ascending=False).reset_index(drop=True)

    labels = ["Champions", "Loyal", "Promising", "At-Risk", "Dormant"]
    playbooks = {
        "Champions": "Protect with premium offers, loyalty perks, and cross-sell journeys.",
        "Loyal": "Increase basket size with bundles and personalized retention campaigns.",
        "Promising": "Nurture with onboarding, educational content, and timed incentives.",
        "At-Risk": "Trigger win-back flows with urgency messaging and selective discounts.",
        "Dormant": "Run low-cost reactivation tests and suppress from expensive paid media.",
    }

    assignment_rows: list[dict[str, Any]] = []
    for idx, row in cluster_stats.iterrows():
        label = labels[min(idx, len(labels) - 1)]
        assignment_rows.append(
            {
                "cluster_id": int(row["cluster_id"]),
                "segment_label": label,
                "playbook": playbooks[label],
            }
        )

    mapping = pd.DataFrame(assignment_rows)
    return work.merge(mapping, on="cluster_id", how="left").sort_values("user_id").reset_index(drop=True)
