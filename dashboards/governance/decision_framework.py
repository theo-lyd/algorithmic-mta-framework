"""Decision Governance and Adoption Framework for Phase VI.

Batch 6.3: Governance structure, KPI definitions, monthly rituals, and training.

Includes:
  - Board-level KPI glossary with precise definitions
  - Monthly decision ritual: budget reallocation process
  - Stakeholder training curriculum for CMO, Finance, Growth teams
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime


@dataclass
class KPIDefinition:
    """Standardized KPI definition for executive reporting."""

    kpi_name: str
    domain: str  # "attribution", "efficiency", "health"
    metric_type: str  # "ratio", "absolute", "rate"
    formula: str  # Plain-English formula
    target_value: float
    measurement_unit: str
    frequency: str  # "daily", "weekly", "monthly"
    owner_role: str  # "CMO", "CFO", "Head of Analytics"
    rationale: str  # Why this KPI matters
    caveats: str  # Limitations and edge cases


KPI_GLOSSARY = [
    KPIDefinition(
        kpi_name="ROAS (Return on Ad Spend)",
        domain="efficiency",
        metric_type="ratio",
        formula="Attributed Revenue / Media Spend",
        target_value=3.5,
        measurement_unit="EUR",
        frequency="daily",
        owner_role="CMO",
        rationale="Measures revenue return per EUR spent; core efficiency metric.",
        caveats="Depends on attribution model; compare YoY not cross-channel absolutely.",
    ),
    KPIDefinition(
        kpi_name="Removal Effect (RE) by Channel",
        domain="attribution",
        metric_type="rate",
        formula="1 - P(conversion | channel removed) / P(conversion | baseline)",
        target_value=0.25,  # 25%
        measurement_unit="pct",
        frequency="weekly",
        owner_role="Head of Analytics",
        rationale="Measures true incremental impact; informs budget reallocation.",
        caveats="Estimated from Markov model; requires 30-day lookback.",
    ),
    KPIDefinition(
        kpi_name="Attribution Variance (vs Last-Touch)",
        domain="attribution",
        metric_type="rate",
        formula="(Markov + Linear - LastTouch) / LastTouch * 100",
        target_value=0.15,  # Allow 15% variance
        measurement_unit="pct",
        frequency="weekly",
        owner_role="CMO",
        rationale="Flags significant model divergence; trust indicator.",
        caveats="High variance = model refinement opportunity.",
    ),
    KPIDefinition(
        kpi_name="Revenue Contribution by Channel",
        domain="efficiency",
        metric_type="rate",
        formula="Sum(Attributed Revenue by Channel) / Total Revenue",
        target_value=1.0,  # Sums to 100%
        measurement_unit="pct",
        frequency="daily",
        owner_role="CFO",
        rationale="Allocates revenue fairly; used for P&L reconciliation.",
        caveats="Must reconcile exactly with finance reporting.",
    ),
    KPIDefinition(
        kpi_name="Channel Waste Score",
        domain="efficiency",
        metric_type="ratio",
        formula="(1 - Removal Effect %) * (Spend / Total Budget)",
        target_value=0.05,  # Max 5% waste per channel
        measurement_unit="pct",
        frequency="monthly",
        owner_role="CMO",
        rationale="Identifies channels to reallocate; drives budget efficiency.",
        caveats="Requires reliable removal effect estimates.",
    ),
    KPIDefinition(
        kpi_name="Propensity Model AUC",
        domain="health",
        metric_type="ratio",
        formula="Area Under ROC Curve (7-day conversion prediction)",
        target_value=0.75,
        measurement_unit="dimensionless",
        frequency="weekly",
        owner_role="Head of Analytics",
        rationale="Model quality metric; predicts segment targeting lift.",
        caveats="Monitor for model drift; retrain if AUC < 0.70.",
    ),
    KPIDefinition(
        kpi_name="Data Freshness (Dashboard SLA)",
        domain="health",
        metric_type="absolute",
        formula="Current Time - Latest Data Timestamp",
        target_value=6,  # 6 hours max lag
        measurement_unit="hours",
        frequency="hourly",
        owner_role="Head of Analytics",
        rationale="Ensures decision data is actionable; operational excellence.",
        caveats="Longer delays during holiday periods accepted.",
    ),
]


@dataclass
class MonthlyDecisionRitual:
    """Monthly budget reallocation decision workflow."""

    ceremony_name: str
    frequency: str
    duration_minutes: int
    participants: List[str]
    pre_work: List[str]
    agenda: List[Dict]  # {time_min: int, topic: str, owner: str, output: str}
    decision_criteria: List[str]
    escalation_path: str


MONTHLY_DECISION_RITUAL = MonthlyDecisionRitual(
    ceremony_name="Marketing Budget Council",
    frequency="Last Thursday of each month, 2:00 PM",
    duration_minutes=60,
    participants=[
        "Chief Marketing Officer (CMO) - Chair",
        "Head of Analytics",
        "Finance Controller",
        "Channel Leads (Display, Search, Social, Email)",
    ],
    pre_work=[
        "Prepare executive dashboard 1 week prior (dashboards/metabase)",
        "Run what-if simulator for top 3 scenarios (dashboards/streamlit)",
        "QA KPI reconciliation vs finance (doc/governance/kpi-glossary.md)",
        "Identify issues from Great Expectations checks (quality/contracts/)",
    ],
    agenda=[
        {
            "time_min": 0,
            "topic": "Recall: KPI definitions and targets",
            "owner": "Head of Analytics",
            "output": "Shared understanding of metrics",
        },
        {
            "time_min": 5,
            "topic": "Review: Attribution War view (Markov vs Last-Touch)",
            "owner": "CMO",
            "output": "Channel credit re-evaluation",
        },
        {
            "time_min": 15,
            "topic": "Waste Report: identify low-removal-effect channels",
            "owner": "Head of Analytics",
            "output": "Reallocation candidates",
        },
        {
            "time_min": 25,
            "topic": "Simulator scenarios: present top 3, confidence intervals",
            "owner": "Head of Analytics",
            "output": "Revenue impact estimates",
        },
        {
            "time_min": 40,
            "topic": "Decision: approve budget reallocation or defer",
            "owner": "CMO",
            "output": "Signed allocation document",
        },
        {
            "time_min": 55,
            "topic": "Action items: deployment, communication, monitoring",
            "owner": "Finance Controller",
            "output": "Implementation checklist",
        },
    ],
    decision_criteria=[
        "Predicted lift >= 3% OR waste reduction >= 5 percentage points",
        "All Great Expectations checks must pass (no blocked data)",
        "Finance reconciliation confidence >= 98%",
        "No single channel reallocation > 30% of current spend",
    ],
    escalation_path=(
        "If consensus not reached: defer to next month, CEO optional override with CFO sign-off."
    ),
)


@dataclass
class TrainingModule:
    """Role-based training curriculum."""

    role: str
    module_name: str
    duration_minutes: int
    target_learnings: List[str]
    materials: List[str]  # File paths
    success_criteria: str


TRAINING_CURRICULUM = [
    TrainingModule(
        role="CMO",
        module_name="Attribution Models & Budget Decision Making",
        duration_minutes=90,
        target_learnings=[
            "Understand why last-touch is insufficient for ROAS",
            "Interpret Markov attribution vs alternatives",
            "Use Attribution War view to identify reallocation opportunities",
            "Make data-informed budget decisions using simulator output",
        ],
        materials=[
            "doc/governance/kpi-glossary.md",
            "doc/governance/monthly-decision-ritual.md",
            "dashboards/metabase/README.md",
            "dashboards/streamlit/README.md",
        ],
        success_criteria=(
            "CMO can explain Markov removal effect for >=2 channels and "
            "justify a proposed EUR10k reallocation using simulator output."
        ),
    ),
    TrainingModule(
        role="Finance Controller",
        module_name="Revenue Reconciliation & Attribution Governance",
        duration_minutes=60,
        target_learnings=[
            "Reconcile attributed revenue vs GL recorded revenue",
            "Validate that attributed channel totals sum to actual conversions",
            "Monitor Great Expectations checks for data quality",
            "Escalate data anomalies to Analytics",
        ],
        materials=[
            "doc/governance/kpi-glossary.md",
            "quality/contracts/business_rules_phase5.py",
            "quality/great_expectations/suites/",
            "doc/governance/reconciliation-runbook.md",
        ],
        success_criteria=(
            "Finance can perform revenue reconciliation monthly with <1% variance "
            "and identify and escalate a data quality issue."
        ),
    ),
    TrainingModule(
        role="Growth Manager",
        module_name="Channel Performance Interpretation",
        duration_minutes=45,
        target_learnings=[
            "Read ROAS drilldowns by channel, campaign, segment",
            "Interpret waste score and removal effect for channel optimization",
            "Understand confidence intervals and model limitations",
            "Propose data-driven channel tactics",
        ],
        materials=[
            "dashboards/metabase/README.md",
            "doc/governance/kpi-glossary.md",
            "dashboards/streamlit/README.md",
        ],
        success_criteria=(
            "Growth manager can identify top-performing segment "
            "and propose a EUR5k reallocation with business rationale."
        ),
    ),
]


def validate_kpi_definition(kpi: KPIDefinition) -> Tuple[bool, List[str]]:
    """Validate KPI definition completeness."""
    violations = []
    if not kpi.kpi_name:
        violations.append("KPI name required")
    if kpi.target_value < 0:
        violations.append("Target value must be non-negative")
    if not kpi.owner_role:
        violations.append("Owner role required")
    return len(violations) == 0, violations


def kpi_checklist() -> Dict:
    """Return KPI validation checklist for monthly ritual pre-work."""
    results = {"kpis_checked": len(
        KPI_GLOSSARY), "passed": 0, "failed": 0, "issues": []}
    for kpi in KPI_GLOSSARY:
        is_valid, violations = validate_kpi_definition(kpi)
        if is_valid:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["issues"].append({kpi.kpi_name: violations})
    return results


def monthly_ritual_checklist() -> Dict:
    """Pre-flight checklist for Monthly Decision Ritual."""
    return {
        "ceremony": MONTHLY_DECISION_RITUAL.ceremony_name,
        "next_occurrence": "Last Thursday of current month",
        "pre_work_items": MONTHLY_DECISION_RITUAL.pre_work,
        "participants": MONTHLY_DECISION_RITUAL.participants,
        "decision_criteria_count": len(MONTHLY_DECISION_RITUAL.decision_criteria),
        "status": "ready",
    }


def training_curriculum_summary() -> Dict:
    """Summary of training curriculum across roles."""
    return {
        "total_modules": len(TRAINING_CURRICULUM),
        "total_training_hours": sum(m.duration_minutes for m in TRAINING_CURRICULUM) / 60,
        "roles": [m.role for m in TRAINING_CURRICULUM],
        "modules": [
            {
                "role": m.role,
                "name": m.module_name,
                "duration_min": m.duration_minutes,
                "materials_count": len(m.materials),
                "success_criteria_words": len(m.success_criteria.split()),
            }
            for m in TRAINING_CURRICULUM
        ],
    }


def summarize_governance(
    dashboard_date: str = None, ritual_date: str = None
) -> Dict:
    """Generate governance summary for Phase VI batch 6.3."""
    return {
        "kpi_glossary": kpi_checklist(),
        "monthly_ritual": monthly_ritual_checklist(),
        "training_curriculum": training_curriculum_summary(),
        "governance_artifacts": {
            "kpi_definitions": len(KPI_GLOSSARY),
            "decision_ritual_agenda_items": len(MONTHLY_DECISION_RITUAL.agenda),
            "training_modules": len(TRAINING_CURRICULUM),
            "total_participants": len(set(m.role for m in TRAINING_CURRICULUM)),
        },
        "adoption_readiness": "ready" if kpi_checklist()["failed"] == 0 else "blocked",
    }
