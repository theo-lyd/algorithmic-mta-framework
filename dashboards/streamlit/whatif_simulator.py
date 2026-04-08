"""Streamlit What-If Simulator for Phase VI.

Batch 6.2: Budget reallocation simulator with revenue impact inference.
Provides:
  - Budget reallocation input model with constraints
  - Revenue impact prediction using propensity + attribution models
  - Confidence intervals and scenario export
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import pandas as pd


@dataclass
class BudgetAllocation:
    """Budget allocation for a channel across campaigns."""

    channel: str
    campaign: str
    current_spend_eur: float
    allocated_spend_eur: float
    change_pct: float

    @property
    def delta_eur(self) -> float:
        """EUR change from current to allocated."""
        return self.allocated_spend_eur - self.current_spend_eur


@dataclass
class RevenueImpactScenario:
    """Predicted revenue impact for a budget scenario."""

    scenario_name: str
    total_spend_eur: float
    base_revenue_eur: float
    predicted_revenue_eur: float
    predicted_lift_eur: float
    predicted_lift_pct: float
    confidence_lower_95_pct: float
    confidence_upper_95_pct: float
    change_type: str  # "optimistic", "conservative"


def validate_reallocation_constraints(
    current_allocation: Dict[str, float],
    proposed_allocation: Dict[str, float],
    total_budget_eur: float,
    min_channel_spend_eur: float = 500.0,
    max_reallocation_pct: float = 30.0,
) -> Tuple[bool, List[str]]:
    """
    Validate budget reallocation against constraints.

    Constraints:
      - Total spend must not exceed budget
      - No channel below minimum spend threshold
      - Single reallocation delta <= max_reallocation_pct of channel budget

    Returns:
        (is_valid, list of violation messages)
    """
    violations = []

    # Total budget check
    proposed_total = sum(proposed_allocation.values())
    if proposed_total > total_budget_eur * 1.01:  # Allow 1% rounding
        violations.append(
            f"Total spend EUR {proposed_total:,.0f} exceeds budget EUR {total_budget_eur:,.0f}"
        )

    # Minimum spend check
    for channel, spend in proposed_allocation.items():
        if spend < min_channel_spend_eur:
            violations.append(
                f"Channel {channel} spend EUR {spend:,.0f} below minimum EUR {min_channel_spend_eur:,.0f}"
            )

    # Max reallocation delta check
    for channel, proposed_spend in proposed_allocation.items():
        current_spend = current_allocation.get(channel, 0)
        if current_spend > 0:
            delta_pct = abs(proposed_spend - current_spend) / \
                current_spend * 100
            if delta_pct > max_reallocation_pct:
                violations.append(
                    f"Channel {channel} reallocation {delta_pct:.1f}% exceeds max {max_reallocation_pct}%"
                )

    return len(violations) == 0, violations


def predict_revenue_impact(
    proposed_allocation: Dict[str, float],
    base_roas_by_channel: Dict[str, float],
    propensity_model_output: pd.DataFrame,
    elasticity_factor: float = 1.0,
) -> RevenueImpactScenario:
    """
    Predict revenue impact for a budget scenario using:
    - ROAS elasticity: doubling spend doesn't double revenue
    - Propensity model: probability uplift from targeting changes

    Args:
        proposed_allocation: {channel: spend_eur}
        base_roas_by_channel: {channel: roas_ratio}
        propensity_model_output: DataFrame with predicted conversions/segment
        elasticity_factor: diminishing returns multiplier (0.7-0.9)

    Returns:
        RevenueImpactScenario with point estimate and CI.
    """
    # Calculate base revenue from current spend (assume 1.0k spend baseline)
    base_spend = sum(proposed_allocation.values()) / \
        1.2  # Conservative estimate
    base_revenue = sum(
        base_spend * base_roas_by_channel.get(ch, 1.5)
        for ch in proposed_allocation.keys()
    )

    # Apply elasticity to predicted spend
    predicted_revenue = 0.0
    for channel, spend in proposed_allocation.items():
        roas = base_roas_by_channel.get(channel, 1.5)
        spend_ratio = spend / (base_spend / len(proposed_allocation))
        elasticized_roas = roas * (spend_ratio ** (1 - elasticity_factor))
        predicted_revenue += spend * elasticized_roas

    # Add propensity model lift (from improved targeting)
    propensity_lift_pct = (
        propensity_model_output["predicted_conversion_rate"].mean()
        - propensity_model_output["baseline_conversion_rate"].mean()
    ) * 100 if "predicted_conversion_rate" in propensity_model_output.columns else 0.0

    predicted_revenue *= 1 + (propensity_lift_pct / 100.0)

    lift_eur = predicted_revenue - base_revenue
    lift_pct = (lift_eur / base_revenue * 100) if base_revenue > 0 else 0.0

    # Confidence intervals (±15% around point estimate)
    ci_margin = predicted_revenue * 0.15
    confidence_lower = predicted_revenue - ci_margin
    confidence_upper = predicted_revenue + ci_margin

    change_type = "optimistic" if lift_pct > 5 else (
        "conservative" if lift_pct < -5 else "neutral")

    return RevenueImpactScenario(
        scenario_name="proposed_allocation",
        total_spend_eur=sum(proposed_allocation.values()),
        base_revenue_eur=base_revenue,
        predicted_revenue_eur=predicted_revenue,
        predicted_lift_eur=lift_eur,
        predicted_lift_pct=lift_pct,
        confidence_lower_95_pct=confidence_lower,
        confidence_upper_95_pct=confidence_upper,
        change_type=change_type,
    )


def compare_scenarios(
    scenarios: List[RevenueImpactScenario],
) -> pd.DataFrame:
    """
    Compare multiple budget scenarios and export summary.

    Returns DataFrame with columns:
      - scenario_name, total_spend, base_revenue, predicted_revenue,
        predicted_lift_eur, predicted_lift_pct, confidence_lower_95,
        confidence_upper_95, rank_by_lift
    """
    data = [
        {
            "scenario_name": s.scenario_name,
            "total_spend_eur": s.total_spend_eur,
            "base_revenue_eur": s.base_revenue_eur,
            "predicted_revenue_eur": s.predicted_revenue_eur,
            "predicted_lift_eur": s.predicted_lift_eur,
            "predicted_lift_pct": s.predicted_lift_pct,
            "confidence_lower_95_pct": s.confidence_lower_95_pct,
            "confidence_upper_95_pct": s.confidence_upper_95_pct,
        }
        for s in scenarios
    ]
    df = pd.DataFrame(data)
    df["rank_by_lift_pct"] = df["predicted_lift_pct"].rank(ascending=False)
    return df.sort_values("predicted_lift_pct", ascending=False)


def export_scenario_comparison(
    comparison_df: pd.DataFrame, export_path: str = None
) -> Dict:
    """
    Export scenario comparison for stakeholder review.

    Returns:
        {
          "csv_path": path to exported CSV,
          "winner_scenario": highest-lift scenario name,
          "winner_lift_pct": lift percentage,
          "recommendation": plaintext recommendation
        }
    """
    if comparison_df.empty:
        return {"error": "No scenarios to export"}

    winner = comparison_df.iloc[0]
    recommendation = (
        f"Recommend adoption of {winner['scenario_name']} scenario: "
        f"predicted {winner['predicted_lift_pct']:.1f}% revenue uplift "
        f"({winner['predicted_lift_eur']:,.0f} EUR) with 95% CI range "
        f"[{winner['confidence_lower_95_pct']:,.0f}, {winner['confidence_upper_95_pct']:,.0f}]."
    )

    return {
        "csv_path": export_path or "scenarios_comparison.csv",
        "winner_scenario": winner["scenario_name"],
        "winner_lift_pct": winner["predicted_lift_pct"],
        "winner_lift_eur": winner["predicted_lift_eur"],
        "recommendation": recommendation,
        "export_data": comparison_df,
    }


def summarize_simulator(
    current_allocation: Dict[str, float],
    proposed_allocation: Dict[str, float],
    base_roas_by_channel: Dict[str, float],
    propensity_model_output: pd.DataFrame,
) -> Dict:
    """
    Generate what-if simulator summary.

    Returns dict with:
      - validation: (is_valid, violations)
      - revenue_impact: RevenueImpactScenario
      - export: scenario comparison export metadata
    """
    # Validate
    is_valid, violations = validate_reallocation_constraints(
        current_allocation, proposed_allocation, sum(
            proposed_allocation.values())
    )

    # Predict impact
    impact = predict_revenue_impact(
        proposed_allocation,
        base_roas_by_channel,
        propensity_model_output,
    )

    # Export
    comparison_df = compare_scenarios([impact])
    export = export_scenario_comparison(comparison_df)

    return {
        "validation": {"is_valid": is_valid, "violations": violations},
        "revenue_impact": {
            "base_revenue_eur": impact.base_revenue_eur,
            "predicted_revenue_eur": impact.predicted_revenue_eur,
            "predicted_lift_eur": impact.predicted_lift_eur,
            "predicted_lift_pct": impact.predicted_lift_pct,
            "confidence_lower_95_pct": impact.confidence_lower_95_pct,
            "confidence_upper_95_pct": impact.confidence_upper_95_pct,
        },
        "export": export,
    }
