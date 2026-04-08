"""Phase VII Batch 7.1: production readiness checks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import mean
from typing import Dict, List


@dataclass
class ReplayResult:
    """Replay validation result for a pipeline batch."""

    batch_id: str
    expected_checksum: str
    replay_checksum: str
    matches: bool


@dataclass
class AccessAuditResult:
    """Security and access audit result for a user account."""

    user_id: str
    role: str
    has_mfa: bool
    has_prod_access: bool
    status: str


def _parse_iso(value: str) -> datetime:
    """Parse ISO timestamp in a deterministic way for tests."""
    return datetime.fromisoformat(value)


def run_disaster_recovery_replay_testing(
    replay_runs: List[Dict],
    expected_checksum_by_batch: Dict[str, str],
    max_rto_minutes: float = 45.0,
    max_rpo_minutes: float = 15.0,
) -> Dict:
    """Validate replay determinism and DR recovery objectives.

    Each replay row must include:
      - batch_id, expected_event_count, replay_event_count
      - expected_checksum, replay_checksum
      - failover_start_ts, service_restored_ts, last_durable_commit_ts
    """
    replay_results: List[ReplayResult] = []
    rto_minutes: List[float] = []
    rpo_minutes: List[float] = []
    violations: List[str] = []

    for run in replay_runs:
        batch_id = run["batch_id"]
        expected_checksum = expected_checksum_by_batch.get(
            batch_id, run["expected_checksum"]
        )
        replay_checksum = run["replay_checksum"]
        matches = expected_checksum == replay_checksum

        replay_results.append(
            ReplayResult(
                batch_id=batch_id,
                expected_checksum=expected_checksum,
                replay_checksum=replay_checksum,
                matches=matches,
            )
        )

        if run["replay_event_count"] != run["expected_event_count"]:
            violations.append(
                f"Batch {batch_id} replay count mismatch: "
                f"{run['replay_event_count']} != {run['expected_event_count']}"
            )
        if not matches:
            violations.append(f"Batch {batch_id} checksum mismatch")

        failover_start = _parse_iso(run["failover_start_ts"])
        service_restored = _parse_iso(run["service_restored_ts"])
        last_durable_commit = _parse_iso(run["last_durable_commit_ts"])

        rto = (service_restored - failover_start).total_seconds() / 60.0
        rpo = (failover_start - last_durable_commit).total_seconds() / 60.0
        rto_minutes.append(rto)
        rpo_minutes.append(rpo)

        if rto > max_rto_minutes:
            violations.append(
                f"Batch {batch_id} RTO breach: {rto:.1f}m > {max_rto_minutes:.1f}m"
            )
        if rpo > max_rpo_minutes:
            violations.append(
                f"Batch {batch_id} RPO breach: {rpo:.1f}m > {max_rpo_minutes:.1f}m"
            )

    deterministic_batches = sum(1 for item in replay_results if item.matches)

    return {
        "replay_batches": len(replay_results),
        "deterministic_batches": deterministic_batches,
        "determinism_rate_pct": (
            deterministic_batches /
            len(replay_results) * 100.0 if replay_results else 0.0
        ),
        "avg_rto_minutes": mean(rto_minutes) if rto_minutes else 0.0,
        "avg_rpo_minutes": mean(rpo_minutes) if rpo_minutes else 0.0,
        "max_rto_minutes": max(rto_minutes) if rto_minutes else 0.0,
        "max_rpo_minutes": max(rpo_minutes) if rpo_minutes else 0.0,
        "all_checks_passed": len(violations) == 0,
        "violations": violations,
    }


def run_backfill_stress_tests(
    backfill_windows: List[Dict],
    max_window_runtime_minutes: float = 120.0,
    min_rows_per_second: float = 1500.0,
    max_error_rate_pct: float = 0.5,
) -> Dict:
    """Validate historical backfill windows under stress conditions."""
    runtimes: List[float] = []
    throughputs: List[float] = []
    violations: List[str] = []

    for window in backfill_windows:
        runtime_minutes = float(window["runtime_minutes"])
        rows_processed = float(window["rows_processed"])
        error_rate_pct = float(window["error_rate_pct"])
        throughput = rows_processed / (runtime_minutes * 60.0)

        runtimes.append(runtime_minutes)
        throughputs.append(throughput)

        if runtime_minutes > max_window_runtime_minutes:
            violations.append(
                f"Window {window['window_label']} runtime breach: "
                f"{runtime_minutes:.1f}m > {max_window_runtime_minutes:.1f}m"
            )
        if throughput < min_rows_per_second:
            violations.append(
                f"Window {window['window_label']} throughput breach: "
                f"{throughput:.1f} r/s < {min_rows_per_second:.1f} r/s"
            )
        if error_rate_pct > max_error_rate_pct:
            violations.append(
                f"Window {window['window_label']} error-rate breach: "
                f"{error_rate_pct:.2f}% > {max_error_rate_pct:.2f}%"
            )

    return {
        "windows_tested": len(backfill_windows),
        "avg_runtime_minutes": mean(runtimes) if runtimes else 0.0,
        "max_runtime_minutes": max(runtimes) if runtimes else 0.0,
        "avg_throughput_rows_per_second": mean(throughputs) if throughputs else 0.0,
        "min_throughput_rows_per_second": min(throughputs) if throughputs else 0.0,
        "all_checks_passed": len(violations) == 0,
        "violations": violations,
    }


def run_security_access_audit(
    users: List[Dict],
    role_permissions: Dict[str, List[str]],
    required_prod_permissions: List[str],
    restricted_permissions: List[str],
) -> Dict:
    """Run a least-privilege and MFA audit for production access."""
    audited: List[AccessAuditResult] = []
    violations: List[str] = []

    for user in users:
        user_id = user["user_id"]
        role = user["role"]
        has_mfa = bool(user["mfa_enabled"])
        has_prod_access = bool(user["prod_access"])
        role_perms = role_permissions.get(role, [])

        status = "pass"
        if has_prod_access and not has_mfa:
            status = "fail"
            violations.append(f"{user_id}: production access without MFA")

        if has_prod_access:
            missing_required = [
                perm for perm in required_prod_permissions if perm not in role_perms
            ]
            if missing_required:
                status = "fail"
                violations.append(
                    f"{user_id}: role {role} missing required permissions {missing_required}"
                )

        forbidden = [
            perm for perm in role_perms if perm in restricted_permissions]
        if forbidden:
            status = "fail"
            violations.append(
                f"{user_id}: role {role} has restricted permissions {forbidden}"
            )

        audited.append(
            AccessAuditResult(
                user_id=user_id,
                role=role,
                has_mfa=has_mfa,
                has_prod_access=has_prod_access,
                status=status,
            )
        )

    return {
        "users_audited": len(audited),
        "prod_access_users": sum(1 for user in audited if user.has_prod_access),
        "mfa_compliance_pct": (
            sum(1 for user in audited if (not user.has_prod_access) or user.has_mfa)
            / len(audited)
            * 100.0
            if audited
            else 0.0
        ),
        "all_checks_passed": len(violations) == 0,
        "violations": violations,
    }


def summarize_production_readiness(
    replay_runs: List[Dict],
    expected_checksum_by_batch: Dict[str, str],
    backfill_windows: List[Dict],
    users: List[Dict],
    role_permissions: Dict[str, List[str]],
) -> Dict:
    """Build Batch 7.1 summary used by validator and gate-check evidence."""
    required_prod_permissions = ["read_metrics", "trigger_replay", "view_logs"]
    restricted_permissions = ["drop_production_tables", "write_raw_pii"]

    dr_summary = run_disaster_recovery_replay_testing(
        replay_runs, expected_checksum_by_batch
    )
    backfill_summary = run_backfill_stress_tests(backfill_windows)
    security_summary = run_security_access_audit(
        users,
        role_permissions,
        required_prod_permissions=required_prod_permissions,
        restricted_permissions=restricted_permissions,
    )

    production_signoff_complete = (
        dr_summary["all_checks_passed"]
        and backfill_summary["all_checks_passed"]
        and security_summary["all_checks_passed"]
    )

    return {
        "batch": "7.1",
        "name": "Production Readiness",
        "disaster_recovery": dr_summary,
        "backfill_stress": backfill_summary,
        "security_access": security_summary,
        "required_prod_permissions": required_prod_permissions,
        "restricted_permissions": restricted_permissions,
        "production_signoff_complete": production_signoff_complete,
    }
