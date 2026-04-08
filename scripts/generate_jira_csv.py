#!/usr/bin/env python3
"""
Generate Jira-importable CSV from execution-ready-master-backlog.md.

Why this script:
1. **Automation Over Manual Entry**: Bulk CSV import ensures consistency and prevents human error.
2. **Auditability**: CSV is version-controlled and diff-able for backlog evolution tracking.
3. **Bulk Operations**: Jira CSV import creates all stories at once; UI entry is too slow for 40 items.
4. **Metadata Preservation**: Epics, sprints, labels, and points are embedded and verified programmatically.
5. **Repeatability**: Future backlog changes can regenerate CSV without re-parsing markdown.

Output format: Jira Cloud Standard CSV import (ISO-8859-1 with UTF-8 BOM fallback).
"""

import csv
from pathlib import Path
from typing import List, Dict, Tuple
import sys

# Backlog data extracted from doc/execution-ready-master-backlog.md
BACKLOG_DATA = [
    ("MTA-001", "Foundation", "Dev container and service orchestration baseline", "DE", "AE", 5, "S1", "One-command startup for core stack works on clean environment"),
    ("MTA-002", "Foundation", "Secrets, env strategy, role-based access matrix", "DE", "AE", 3, "S1", "Secrets not hardcoded, access matrix approved"),
    ("MTA-003", "Foundation", "Naming conventions, layer standards, modeling contract", "AE", "DE", 3, "S1", "Standards approved and used by first pipelines"),
    ("MTA-004", "Foundation", "SLA/SLO definitions and incident severity policy", "AE", "DE", 3, "S1", "Freshness, completeness, and error SLOs agreed"),
    ("MTA-005", "Ingestion", "GA4 connector setup with incremental cursor logic", "DE", "AE", 8, "S1", "Incremental sync stable across three runs"),
    ("MTA-006", "Ingestion", "Raw JSON landing and partitioned parquet writer", "DE", "AE", 8, "S1", "Bronze partition output generated and queryable"),
    ("MTA-007", "Ingestion", "Ingestion audit columns and idempotency keys", "DE", "AE", 5, "S2", "No duplicate loads on replay"),
    ("MTA-008", "Ingestion", "Airflow DAG base and schedule orchestration", "DE", "AE", 5, "S2", "DAG succeeds end-to-end on sample day"),
    ("MTA-009", "Ingestion", "Late-arriving data sensor and partition replay logic", "DE", "AE", 8, "S2", "Delayed feed triggers selective reprocessing only"),
    ("MTA-010", "Ingestion", "Reconciliation check expected vs arrived event volumes", "AE", "DE", 5, "S2", "Alert generated on threshold breach"),
    ("MTA-011", "Cleaning", "Encoding detection and UTF normalization pipeline", "AE", "DE", 5, "S3", "Known bad encodings corrected in fixtures"),
    ("MTA-012", "Cleaning", "German string normalization and transliteration rules", "AE", "DE", 5, "S3", "Umlaut handling validated by tests"),
    ("MTA-013", "Cleaning", "Locale-aware financial parsing and abbreviation expansion", "AE", "DE", 8, "S3", "Inputs like 10 Mio converted correctly"),
    ("MTA-014", "Cleaning", "Nested GA4 flattening to canonical silver schema", "AE", "DE", 8, "S3", "Silver tables populated with expected row counts"),
    ("MTA-015", "Core Modeling", "Sessionization with 30-minute inactivity rule", "AE", "DE", 8, "S4", "Deterministic boundary tests pass"),
    ("MTA-016", "Core Modeling", "30-day conversion lookback enforcement", "AE", "DE", 5, "S4", "Out-of-window touches excluded"),
    ("MTA-017", "Core Modeling", "Campaign dimension SCD Type 2 implementation", "AE", "DE", 8, "S4", "Point-in-time joins reproduce prior state"),
    ("MTA-018", "Core Modeling", "Customer hash harmonization and identity rules", "AE", "DE", 8, "S4", "CRM-web linkage quality above threshold"),
    ("MTA-019", "Core Modeling", "Journey path builder using recursive and window logic", "AE", "DE", 8, "S5", "Benchmark user paths are accurate"),
    ("MTA-020", "Core Modeling", "Gold marts for spend, net conversions, and ROAS", "AE", "BI", 8, "S5", "Finance reconciliation passes"),
    ("MTA-021", "Quality", "GE suite for schema and integrity contracts", "AE", "DE", 8, "S5", "Tests fail correctly on injected bad data"),
    ("MTA-022", "Quality", "Attribution conservation test (no ghost revenue)", "AE", "MLE", 5, "S5", "Attributed totals equal actual totals"),
    ("MTA-023", "Attribution", "Baselines: first, last, linear, and time-decay", "MLE", "AE", 8, "S6", "Baseline outputs published and comparable"),
    ("MTA-024", "Attribution", "Markov transition matrix and removal effect engine", "MLE", "AE", 13, "S6", "Stable channel removal scores"),
    ("MTA-025", "Attribution", "Normalization and attributed revenue allocation", "MLE", "AE", 8, "S6", "Revenue by channel reconciles to net total"),
    ("MTA-026", "ML", "Feature store for next-7-day propensity model", "MLE", "AE", 8, "S7", "Versioned feature sets generated daily"),
    ("MTA-027", "ML", "Logistic regression training and calibration", "MLE", "AE", 8, "S7", "AUC and calibration meet thresholds"),
    ("MTA-028", "ML", "Drift monitoring and retraining trigger policy", "MLE", "DE", 5, "S7", "Drift alerts fire on synthetic shift"),
    ("MTA-029", "ML", "User segmentation with K-means and labeling", "MLE", "BI", 8, "S8", "Segments stable and interpretable"),
    ("MTA-030", "Observability", "Monte Carlo freshness, volume, schema monitors", "DE", "AE", 8, "S8", "Alerts route with severity metadata"),
    ("MTA-031", "Observability", "Pixel downtime detector under active spend", "DE", "BI", 5, "S8", "Incident triggers when views collapse"),
    ("MTA-032", "CI/CD", "PR pipeline for dbt tests and GE checkpoints", "DE", "AE", 8, "S8", "Failed checks block merge"),
    ("MTA-033", "BI", "Metabase Attribution War dashboard", "BI", "AE", 8, "S9", "Last-touch vs Markov deltas validated"),
    ("MTA-034", "BI", "Channel waste report and efficiency heatmap", "BI", "AE", 5, "S9", "High-cost low-impact channels highlighted"),
    ("MTA-035", "BI/ML", "Streamlit budget what-if simulator", "BI", "MLE", 13, "S9", "Scenario output aligned with model assumptions"),
    ("MTA-036", "Adoption", "KPI glossary and board-facing metric definitions", "BI", "AE", 5, "S10", "Executive sign-off on metric definitions"),
    ("MTA-037", "Hardening", "Backfill, replay, and disaster recovery drill", "DE", "AE", 8, "S10", "Recovery runbook proven in timed test"),
    ("MTA-038", "Validation", "End-to-end UAT with Marketing and Finance", "BI", "AE", 5, "S10", "Critical defects closed"),
    ("MTA-039", "Impact", "Pre/post budget reallocation experiment framework", "MLE", "BI", 8, "S10", "Uplift measurement approach approved"),
    ("MTA-040", "Closeout", "Thesis evidence pack and reproducibility appendix", "AE", "BI", 5, "S10", "Final package complete"),
]

EPIC_ORDER = [
    "Foundation", "Ingestion", "Cleaning", "Core Modeling", "Quality",
    "Attribution", "ML", "Observability", "CI/CD", "BI", "BI/ML", "Adoption",
    "Hardening", "Validation", "Impact", "Closeout"
]


def generate_jira_csv(output_path: str) -> Tuple[int, int, int]:
    """
    Generate Jira-compatible CSV.
    
    Args:
        output_path: Path to write CSV file.
        
    Returns:
        Tuple of (total_stories, total_points, total_epics).
    """
    rows = []
    total_points = 0
    epics_set = set()
    
    for issue_id, epic, title, primary, support, points, sprint, acceptance in BACKLOG_DATA:
        total_points += points
        epics_set.add(epic)
        
        # Jira CSV format
        # Issue Type, Issue Key, Summary, Description, Epic Link, Labels, Sprint, Story Points, Acceptance Criteria
        labels = f"{primary},{support},mta-backlog,{epic.lower().replace(' ', '-')},{sprint.lower()}"
        
        row = {
            "Issue Type": "Story",
            "Issue Key": issue_id,
            "Summary": f"[{primary}] {title}",
            "Description": f"Primary: {primary} | Support: {support}\n\nAcceptance Criteria: {acceptance}",
            "Epic Link": f"MTA-EPIC-{epic_order_index(epic)}",
            "Labels": labels,
            "Sprint": sprint,
            "Story Points": points,
            "Assignee": "",  # To be filled in Jira
            "Custom Fields": f"Primary Owner: {primary}; Support: {support}",
        }
        rows.append(row)
    
    # Write CSV with UTF-8 encoding
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Issue Type", "Issue Key", "Summary", "Description",
                "Epic Link", "Labels", "Sprint", "Story Points",
                "Assignee", "Custom Fields"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)
    
    return len(BACKLOG_DATA), total_points, len(epics_set)


def epic_order_index(epic: str) -> int:
    """Map epic to numeric ID for linking."""
    try:
        return EPIC_ORDER.index(epic) + 1
    except ValueError:
        return 99


def validate_csv(output_path: str) -> bool:
    """Validate CSV output."""
    with open(output_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    required_fields = {"Issue Type", "Issue Key", "Summary", "Epic Link", "Sprint", "Story Points"}
    if not required_fields.issubset(set(rows[0].keys() if rows else [])):
        print("❌ VALIDATION FAILED: Missing required CSV fields")
        return False
    
    # Check story count
    if len(rows) != 40:
        print(f"❌ VALIDATION FAILED: Expected 40 stories, got {len(rows)}")
        return False
    
    # Check points sum (actual: 273, not the stated 283 in backlog doc)
    total_points = sum(int(row["Story Points"]) for row in rows)
    if total_points != 273:
        print(f"❌ VALIDATION FAILED: Expected 273 total points, got {total_points}")
        return False
    
    # Check sprints
    sprints = set(row["Sprint"] for row in rows)
    expected_sprints = {f"S{i}" for i in range(1, 11)}
    if sprints != expected_sprints:
        print(f"❌ VALIDATION FAILED: Sprint mismatch. Got {sprints}, expected {expected_sprints}")
        return False
    
    print("✅ CSV validation passed:")
    print(f"   - {len(rows)} stories")
    print(f"   - {total_points} total story points")
    print(f"   - {len(sprints)} sprints (S1-S10)")
    print(f"   - All required fields present")
    
    return True


if __name__ == "__main__":
    output_file = Path(__file__).parent.parent / "doc" / "backlog" / "mta-framework-jira-import.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating Jira CSV to: {output_file}")
    total_stories, total_points, total_epics = generate_jira_csv(str(output_file))
    print(f"✅ Generated {total_stories} stories, {total_points} points, {total_epics} epics")
    
    if validate_csv(str(output_file)):
        print(f"\n📁 CSV ready for Jira import: {output_file}")
        sys.exit(0)
    else:
        print("\n❌ CSV validation failed")
        sys.exit(1)
