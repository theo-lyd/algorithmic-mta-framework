"""Batch 3.2 unified identity and customer hash harmonization."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class IdentityResolutionResult:
    resolved_identities: pd.DataFrame
    unresolved_queue: pd.DataFrame


def _hash_token(token: str) -> str:
    return f"cust_{hashlib.sha256(token.encode('utf-8')).hexdigest()[:16]}"


def _confidence(row: pd.Series) -> float:
    if row.get("crm_customer_id"):
        return 0.99
    if row.get("email_hash") and row.get("phone_hash"):
        return 0.95
    if row.get("email_hash"):
        return 0.90
    if row.get("phone_hash"):
        return 0.85
    if row.get("user_pseudo_id"):
        return 0.60
    if row.get("device_id"):
        return 0.50
    return 0.0


def resolve_identity(df: pd.DataFrame) -> IdentityResolutionResult:
    work = df.copy().fillna("")

    crm_map: dict[str, str] = {}
    email_map: dict[str, str] = {}
    phone_map: dict[str, str] = {}
    user_map: dict[str, str] = {}
    device_map: dict[str, str] = {}
    hash_to_crm: dict[str, str] = {}

    resolved_rows: list[dict[str, Any]] = []
    unresolved_rows: list[dict[str, Any]] = []

    for _, row in work.iterrows():
        crm = row.get("crm_customer_id", "")
        email = row.get("email_hash", "")
        phone = row.get("phone_hash", "")
        user = row.get("user_pseudo_id", "")
        device = row.get("device_id", "")

        candidate_hashes = set()
        if crm and crm in crm_map:
            candidate_hashes.add(crm_map[crm])
        if email and email in email_map:
            candidate_hashes.add(email_map[email])
        if phone and phone in phone_map:
            candidate_hashes.add(phone_map[phone])
        if user and user in user_map:
            candidate_hashes.add(user_map[user])
        if device and device in device_map:
            candidate_hashes.add(device_map[device])

        if len(candidate_hashes) > 1:
            unresolved_rows.append(
                {
                    **row.to_dict(),
                    "identity_confidence_score": 0.0,
                    "resolution_status": "unresolved",
                    "reason": "conflicting_identifier_clusters",
                }
            )
            continue

        # Explicit CRM conflict rule:
        # if email/phone already maps to a cluster owned by another CRM id,
        # this record must go to unresolved queue for manual merge review.
        linked_hash = None
        if email and email in email_map:
            linked_hash = email_map[email]
        elif phone and phone in phone_map:
            linked_hash = phone_map[phone]

        if crm and linked_hash and linked_hash in hash_to_crm and hash_to_crm[linked_hash] != crm:
            unresolved_rows.append(
                {
                    **row.to_dict(),
                    "identity_confidence_score": 0.0,
                    "resolution_status": "unresolved",
                    "reason": "conflicting_identifier_clusters",
                }
            )
            continue

        if len(candidate_hashes) == 1:
            customer_hash = next(iter(candidate_hashes))
        else:
            if crm:
                customer_hash = _hash_token(f"crm:{crm}")
            elif email:
                customer_hash = _hash_token(f"email:{email}")
            elif phone:
                customer_hash = _hash_token(f"phone:{phone}")
            elif user:
                customer_hash = _hash_token(f"user:{user}")
            elif device:
                customer_hash = _hash_token(f"device:{device}")
            else:
                unresolved_rows.append(
                    {
                        **row.to_dict(),
                        "identity_confidence_score": 0.0,
                        "resolution_status": "unresolved",
                        "reason": "no_identifiers_available",
                    }
                )
                continue

        if crm:
            crm_map[crm] = customer_hash
            hash_to_crm[customer_hash] = crm
        if email:
            email_map[email] = customer_hash
        if phone:
            phone_map[phone] = customer_hash
        if user:
            user_map[user] = customer_hash
        if device:
            device_map[device] = customer_hash

        confidence = _confidence(row)
        status = "resolved" if confidence >= 0.5 else "unresolved"

        result_row = {
            **row.to_dict(),
            "customer_hash": customer_hash,
            "identity_confidence_score": confidence,
            "resolution_status": status,
            "reason": "",
        }

        if status == "resolved":
            resolved_rows.append(result_row)
        else:
            unresolved_rows.append({**result_row, "reason": "low_confidence"})

    resolved_df = pd.DataFrame(resolved_rows)
    unresolved_df = pd.DataFrame(unresolved_rows)

    if unresolved_df.empty:
        unresolved_df = pd.DataFrame(columns=list(
            work.columns) + ["identity_confidence_score", "resolution_status", "reason"])

    return IdentityResolutionResult(
        resolved_identities=resolved_df,
        unresolved_queue=unresolved_df,
    )


def summarize_resolution(result: IdentityResolutionResult) -> dict[str, Any]:
    resolved = result.resolved_identities
    unresolved = result.unresolved_queue

    return {
        "resolved_rows": int(resolved.shape[0]),
        "unresolved_rows": int(unresolved.shape[0]),
        "unique_customer_hashes": int(resolved["customer_hash"].nunique()) if not resolved.empty else 0,
        "avg_confidence": float(resolved["identity_confidence_score"].mean()) if not resolved.empty else 0.0,
    }
