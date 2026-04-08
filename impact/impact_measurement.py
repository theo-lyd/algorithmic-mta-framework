"""Phase VII Batch 7.2: business impact measurement logic."""

from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import mean, pstdev
from typing import Dict, List
import pandas as pd


@dataclass
class ImpactDelta:
    """Key impact delta metrics for pre/post reallocation."""

    pre_roas: float
    post_roas: float
    roas_uplift_pct: float
    pre_waste_rate_pct: float
    post_waste_rate_pct: float
    waste_reduction_pct: float


def design_pre_post_reallocation_experiment(
    pre_period: pd.DataFrame,
    post_period: pd.DataFrame,
    min_observations: int = 28,
) -> Dict:
    """Design and validate a pre/post experiment for reallocation impact."""
    if len(pre_period) < min_observations or len(post_period) < min_observations:
        raise ValueError(
            f"Insufficient observations: pre={len(pre_period)}, post={len(post_period)}, "
            f"required={min_observations}"
        )

    required_columns = {"date", "spend_eur", "revenue_eur", "waste_eur"}
    if not required_columns.issubset(set(pre_period.columns)):
        raise ValueError("Pre period is missing required columns")
    if not required_columns.issubset(set(post_period.columns)):
        raise ValueError("Post period is missing required columns")

    return {
        "hypothesis": "Reallocation improves ROAS and reduces waste.",
        "null_hypothesis": "No improvement in ROAS and waste after reallocation.",
        "pre_days": int(len(pre_period)),
        "post_days": int(len(post_period)),
        "min_observations_required": min_observations,
        "guardrails": {
            "spend_stability_max_delta_pct": 20.0,
            "tracking_integrity_required": True,
            "channel_coverage_required": True,
        },
        "design_valid": True,
    }


def measure_roas_uplift_and_waste_reduction(
    pre_period: pd.DataFrame,
    post_period: pd.DataFrame,
) -> ImpactDelta:
    """Measure ROAS uplift and waste reduction from pre/post periods."""
    pre_spend = float(pre_period["spend_eur"].sum())
    pre_revenue = float(pre_period["revenue_eur"].sum())
    pre_waste = float(pre_period["waste_eur"].sum())

    post_spend = float(post_period["spend_eur"].sum())
    post_revenue = float(post_period["revenue_eur"].sum())
    post_waste = float(post_period["waste_eur"].sum())

    pre_roas = pre_revenue / pre_spend if pre_spend else 0.0
    post_roas = post_revenue / post_spend if post_spend else 0.0
    roas_uplift_pct = ((post_roas - pre_roas) / pre_roas *
                       100.0) if pre_roas else 0.0

    pre_waste_rate_pct = (pre_waste / pre_spend * 100.0) if pre_spend else 0.0
    post_waste_rate_pct = (post_waste / post_spend *
                           100.0) if post_spend else 0.0
    waste_reduction_pct = (
        (pre_waste_rate_pct - post_waste_rate_pct) / pre_waste_rate_pct * 100.0
        if pre_waste_rate_pct
        else 0.0
    )

    return ImpactDelta(
        pre_roas=pre_roas,
        post_roas=post_roas,
        roas_uplift_pct=roas_uplift_pct,
        pre_waste_rate_pct=pre_waste_rate_pct,
        post_waste_rate_pct=post_waste_rate_pct,
        waste_reduction_pct=waste_reduction_pct,
    )


def _normal_cdf(value: float) -> float:
    """Approximate standard normal CDF without scipy dependency."""
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def quantify_confidence_and_sensitivity(
    pre_period: pd.DataFrame,
    post_period: pd.DataFrame,
    assumptions: Dict[str, float],
) -> Dict:
    """Quantify confidence interval and sensitivity around measured uplift."""
    pre_daily_roas = (pre_period["revenue_eur"] /
                      pre_period["spend_eur"]).tolist()
    post_daily_roas = (post_period["revenue_eur"] /
                       post_period["spend_eur"]).tolist()

    pre_mean = mean(pre_daily_roas)
    post_mean = mean(post_daily_roas)
    uplift = post_mean - pre_mean

    pre_std = pstdev(pre_daily_roas) if len(pre_daily_roas) > 1 else 0.0
    post_std = pstdev(post_daily_roas) if len(post_daily_roas) > 1 else 0.0
    standard_error = math.sqrt(
        (pre_std ** 2) / len(pre_daily_roas) +
        (post_std ** 2) / len(post_daily_roas)
    )

    z_score = uplift / standard_error if standard_error > 0 else 0.0
    p_value_two_tailed = max(
        0.0, min(1.0, 2.0 * (1.0 - _normal_cdf(abs(z_score)))))

    ci_low = uplift - 1.96 * standard_error
    ci_high = uplift + 1.96 * standard_error

    attr_error_pct = float(assumptions.get("attribution_error_pct", 10.0))
    elasticity_error_pct = float(assumptions.get("elasticity_error_pct", 8.0))
    combined_error_pct = attr_error_pct + elasticity_error_pct

    uplift_pct = ((post_mean - pre_mean) / pre_mean *
                  100.0) if pre_mean else 0.0
    sensitivity_low = uplift_pct - combined_error_pct
    sensitivity_high = uplift_pct + combined_error_pct

    return {
        "daily_roas_mean_pre": pre_mean,
        "daily_roas_mean_post": post_mean,
        "daily_roas_delta": uplift,
        "daily_roas_delta_ci_95": [ci_low, ci_high],
        "z_score": z_score,
        "p_value_two_tailed": p_value_two_tailed,
        "statistically_significant_at_95": p_value_two_tailed < 0.05,
        "sensitivity_uplift_range_pct": [sensitivity_low, sensitivity_high],
        "assumptions": assumptions,
    }


def summarize_impact_measurement(
    pre_period: pd.DataFrame,
    post_period: pd.DataFrame,
    assumptions: Dict[str, float],
) -> Dict:
    """Build Batch 7.2 summary for evidence and gate checks."""
    experiment = design_pre_post_reallocation_experiment(
        pre_period, post_period)
    impact_delta = measure_roas_uplift_and_waste_reduction(
        pre_period, post_period)
    confidence = quantify_confidence_and_sensitivity(
        pre_period, post_period, assumptions)

    return {
        "batch": "7.2",
        "name": "Impact Measurement",
        "experiment_design": experiment,
        "impact_delta": {
            "pre_roas": impact_delta.pre_roas,
            "post_roas": impact_delta.post_roas,
            "roas_uplift_pct": impact_delta.roas_uplift_pct,
            "pre_waste_rate_pct": impact_delta.pre_waste_rate_pct,
            "post_waste_rate_pct": impact_delta.post_waste_rate_pct,
            "waste_reduction_pct": impact_delta.waste_reduction_pct,
        },
        "confidence": confidence,
        "business_value_quantified": (
            impact_delta.roas_uplift_pct > 0
            and impact_delta.waste_reduction_pct > 0
            and confidence["statistically_significant_at_95"]
        ),
    }
