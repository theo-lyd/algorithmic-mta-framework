"""Batch 4.2 Markov attribution and removal-effect engine."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


ABSORBING_CONVERSION = "__CONVERSION__"
ABSORBING_NULL = "__NULL__"
START_STATE = "__START__"


def extract_paths(events_df: pd.DataFrame) -> pd.DataFrame:
    work = events_df.copy()
    work["event_timestamp"] = pd.to_datetime(work["event_timestamp"], utc=True)
    work["is_conversion"] = work["is_conversion"].astype(bool)
    work["channel"] = work["channel"].fillna("unknown")
    work = work.sort_values(
        ["journey_id", "event_timestamp", "event_id"]).reset_index(drop=True)

    rows: list[dict[str, Any]] = []
    for journey_id, group in work.groupby("journey_id", sort=False):
        ordered = group.sort_values("event_timestamp")
        channels = ordered[~ordered["is_conversion"]
                           ]["channel"].astype(str).tolist()
        converted = bool(ordered["is_conversion"].any())
        rows.append(
            {
                "journey_id": journey_id,
                "channels": channels,
                "converted": converted,
            }
        )

    return pd.DataFrame(rows)


def build_transition_matrix(paths_df: pd.DataFrame) -> pd.DataFrame:
    transition_counts: dict[tuple[str, str], int] = {}
    states: set[str] = {START_STATE, ABSORBING_CONVERSION, ABSORBING_NULL}

    for _, row in paths_df.iterrows():
        channels = list(row["channels"])
        terminal = ABSORBING_CONVERSION if bool(
            row["converted"]) else ABSORBING_NULL
        sequence = [START_STATE] + channels + [terminal]
        states.update(sequence)

        for source, target in zip(sequence[:-1], sequence[1:]):
            key = (source, target)
            transition_counts[key] = transition_counts.get(key, 0) + 1

    ordered_states = sorted(states)
    matrix = pd.DataFrame(0.0, index=ordered_states, columns=ordered_states)

    for (source, target), count in transition_counts.items():
        matrix.loc[source, target] = float(count)

    for source in ordered_states:
        row_sum = float(matrix.loc[source].sum())
        if row_sum > 0:
            matrix.loc[source] = matrix.loc[source] / row_sum

    matrix.loc[ABSORBING_CONVERSION] = 0.0
    matrix.loc[ABSORBING_NULL] = 0.0
    matrix.loc[ABSORBING_CONVERSION, ABSORBING_CONVERSION] = 1.0
    matrix.loc[ABSORBING_NULL, ABSORBING_NULL] = 1.0
    return matrix


def _absorption_probability(transition_matrix: pd.DataFrame, start_state: str = START_STATE) -> float:
    states = list(transition_matrix.index)
    transient = [state for state in states if state not in {
        ABSORBING_CONVERSION, ABSORBING_NULL}]
    if not transient:
        return 0.0

    q = transition_matrix.loc[transient, transient].to_numpy(dtype=float)
    r = transition_matrix.loc[transient, [
        ABSORBING_CONVERSION, ABSORBING_NULL]].to_numpy(dtype=float)

    identity = np.eye(q.shape[0])
    fundamental = np.linalg.inv(identity - q)
    absorption = fundamental @ r

    start_idx = transient.index(start_state)
    return float(absorption[start_idx, 0])


def compute_removal_effects(paths_df: pd.DataFrame) -> pd.DataFrame:
    base_matrix = build_transition_matrix(paths_df)
    base_conversion_probability = _absorption_probability(base_matrix)

    channels = sorted(
        {channel for channels in paths_df["channels"].tolist() for channel in channels})
    rows: list[dict[str, Any]] = []

    for channel in channels:
        removed_matrix = base_matrix.copy()

        # Redirect incoming channel traffic to NULL and make the removed channel
        # itself a dead-end into NULL to represent channel removal.
        for source in removed_matrix.index:
            if source in {channel, ABSORBING_CONVERSION, ABSORBING_NULL}:
                continue
            incoming = float(removed_matrix.loc[source, channel])
            if incoming > 0:
                removed_matrix.loc[source, ABSORBING_NULL] = float(
                    removed_matrix.loc[source, ABSORBING_NULL]
                ) + incoming
                removed_matrix.loc[source, channel] = 0.0
                row_sum = float(removed_matrix.loc[source].sum())
                if row_sum > 0:
                    removed_matrix.loc[source] = removed_matrix.loc[source] / row_sum

        removed_matrix.loc[channel] = 0.0
        removed_matrix.loc[channel, ABSORBING_NULL] = 1.0

        removed_probability = _absorption_probability(removed_matrix)
        effect = max(base_conversion_probability - removed_probability, 0.0)

        rows.append(
            {
                "channel": channel,
                "base_conversion_probability": base_conversion_probability,
                "removed_conversion_probability": removed_probability,
                "removal_effect": effect,
            }
        )

    return pd.DataFrame(rows).sort_values("channel").reset_index(drop=True)


def normalize_markov_attribution(removal_effects_df: pd.DataFrame, total_conversions: float) -> pd.DataFrame:
    work = removal_effects_df.copy()
    effect_sum = float(work["removal_effect"].sum())
    if effect_sum <= 0:
        work["attribution_share"] = 0.0
    else:
        work["attribution_share"] = work["removal_effect"] / effect_sum

    work["attributed_conversions"] = work["attribution_share"] * \
        float(total_conversions)
    return work[["channel", "removal_effect", "attribution_share", "attributed_conversions"]].sort_values("channel").reset_index(drop=True)


def summarize_markov_stability(markov_df: pd.DataFrame) -> dict[str, Any]:
    return {
        "channels": int(markov_df["channel"].nunique()),
        "share_sum": float(markov_df["attribution_share"].sum()),
        "max_channel_share": float(markov_df["attribution_share"].max()) if not markov_df.empty else 0.0,
        "min_channel_share": float(markov_df["attribution_share"].min()) if not markov_df.empty else 0.0,
    }
