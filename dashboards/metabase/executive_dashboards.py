"""Metabase Executive Dashboard Queries for Phase VI.

Batch 6.1: Executive-facing visualizations for budget decisions.
Includes:
  - Attribution War View: last-touch vs Markov comparison
  - Channel Waste Report: high-cost, low-removal-effect channels
  - ROAS Drilldowns: by channel, campaign, and segment
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import pandas as pd


@dataclass
class AttributionWarView:
    """Last-touch vs Markov attribution comparison."""

    channel: str
    last_touch_credit: float
    markov_credit: float
    variance_pct: float
    direction: str  # "gain" or "loss"

    @property
    def credit_shift_eur(self) -> float:
        """Absolute EUR shift from last-touch to Markov."""
        return self.markov_credit - self.last_touch_credit


@dataclass
class WasteReport:
    """Channel waste: high cost, low removal effect."""

    channel: str
    monthly_spend_eur: float
    removal_effect_pct: float
    waste_score: float  # 0-1: 1 = pure waste
    recommendation: str  # "reallocate", "optimize", "maintain"


@dataclass
class ROASDrilldown:
    """ROAS and efficiency metrics."""

    channel: str
    campaign: str
    segment: str
    spend_eur: float
    attributed_revenue_eur: float
    roas: float
    conversion_rate_pct: float
    customer_acq_cost_eur: float


def attribution_war_view(
    attribution_data: pd.DataFrame,
) -> List[AttributionWarView]:
    """
    Compare last-touch vs Markov attribution credit by channel.

    Args:
        attribution_data: DataFrame with columns:
          - channel, last_touch_credit, markov_credit

    Returns:
        List of AttributionWarView records showing credit shifts.
    """
    results = []
    for _, row in attribution_data.iterrows():
        variance_pct = (
            (row["markov_credit"] - row["last_touch_credit"])
            / row["last_touch_credit"]
            * 100
        )
        direction = "gain" if variance_pct > 0 else "loss"
        results.append(
            AttributionWarView(
                channel=row["channel"],
                last_touch_credit=row["last_touch_credit"],
                markov_credit=row["markov_credit"],
                variance_pct=abs(variance_pct),
                direction=direction,
            )
        )
    return sorted(results, key=lambda x: abs(x.variance_pct), reverse=True)


def waste_report(
    channel_metrics: pd.DataFrame, monthly_budget_eur: float = 100000.0
) -> List[WasteReport]:
    """
    Identify waste channels: high spend, low removal effect.

    Args:
        channel_metrics: DataFrame with columns:
          - channel, spend_eur, removal_effect_pct
        monthly_budget_eur: total monthly marketing budget

    Returns:
        List of WasteReport records, sorted by waste score (descending).
    """
    results = []
    for _, row in channel_metrics.iterrows():
        removal_effect_pct = max(0, row["removal_effect_pct"])
        spend_ratio = row["spend_eur"] / monthly_budget_eur
        # Waste score = (1 - removal effect) * spend ratio
        waste_score = (1 - removal_effect_pct / 100.0) * spend_ratio

        if waste_score > 0.01:  # 1% waste threshold
            recommendation = (
                "reallocate"
                if waste_score > 0.1
                else ("optimize" if removal_effect_pct < 25 else "maintain")
            )
        else:
            recommendation = "maintain"

        results.append(
            WasteReport(
                channel=row["channel"],
                monthly_spend_eur=row["spend_eur"],
                removal_effect_pct=removal_effect_pct,
                waste_score=waste_score,
                recommendation=recommendation,
            )
        )
    return sorted(results, key=lambda x: x.waste_score, reverse=True)


def roas_drilldown(
    conversion_data: pd.DataFrame, spend_data: pd.DataFrame
) -> List[ROASDrilldown]:
    """
    Create ROAS drilldown by channel, campaign, and segment.

    Args:
        conversion_data: DataFrame with columns:
          - channel, campaign, segment, attributed_revenue_eur, conversions
        spend_data: DataFrame with columns:
          - channel, campaign, segment, spend_eur

    Returns:
        List of ROASDrilldown records with ROAS and efficiency metrics.
    """
    # Merge conversion and spend data
    merged = conversion_data.merge(
        spend_data, on=["channel", "campaign", "segment"], how="inner"
    )

    results = []
    for _, row in merged.iterrows():
        roas = (
            row["attributed_revenue_eur"] / row["spend_eur"]
            if row["spend_eur"] > 0
            else 0.0
        )
        conversion_rate_pct = (
            (row["conversions"] / row.get("sessions", 1))
            * 100
            if row.get("sessions", 1) > 0
            else 0.0
        )
        cac_eur = (
            row["spend_eur"] / row["conversions"]
            if row["conversions"] > 0
            else 0.0
        )

        results.append(
            ROASDrilldown(
                channel=row["channel"],
                campaign=row["campaign"],
                segment=row["segment"],
                spend_eur=row["spend_eur"],
                attributed_revenue_eur=row["attributed_revenue_eur"],
                roas=roas,
                conversion_rate_pct=conversion_rate_pct,
                customer_acq_cost_eur=cac_eur,
            )
        )
    return sorted(results, key=lambda x: x.roas, reverse=True)


def summarize_dashboards(
    attribution_data: pd.DataFrame,
    channel_metrics: pd.DataFrame,
    conversion_data: pd.DataFrame,
    spend_data: pd.DataFrame,
) -> Dict:
    """
    Generate executive dashboard summary across all three views.

    Returns dict with:
      - attribution_war: list of AttributionWarView (top 5 gainers/losers)
      - waste_report: list of WasteReport (top waste channels)
      - roas_drilldown: list of ROASDrilldown (top performers)
      - key_insights: dict of headline findings
    """
    war = attribution_war_view(attribution_data)
    waste = waste_report(channel_metrics)
    roas = roas_drilldown(conversion_data, spend_data)

    # Key insights
    top_waste = waste[0] if waste else None
    top_roas = roas[0] if roas else None
    biggest_shift = war[0] if war else None

    key_insights = {
        "total_channels": len(set(attribution_data["channel"])),
        "channels_to_reallocate": sum(1 for w in waste if w.recommendation == "reallocate"),
        "average_roas": (
            sum(r.roas for r in roas) / len(roas) if roas else 0.0
        ),
        "top_waste_channel": top_waste.channel if top_waste else None,
        "waste_score_top": top_waste.waste_score if top_waste else 0.0,
        "best_roas_channel": top_roas.channel if top_roas else None,
        "best_roas_value": top_roas.roas if top_roas else 0.0,
        "biggest_attribution_shift_channel": (
            biggest_shift.channel if biggest_shift else None
        ),
        "biggest_shift_variance_pct": (
            biggest_shift.variance_pct if biggest_shift else 0.0
        ),
    }

    return {
        "attribution_war": war,
        "waste_report": waste,
        "roas_drilldown": roas,
        "key_insights": key_insights,
    }
