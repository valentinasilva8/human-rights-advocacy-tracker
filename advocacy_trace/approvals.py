"""Apply approvals a person has already given.

The research file cannot approve itself. This module approves a row only when
the stored text still matches the version that was approved. A mismatch leaves
the row proposed. Outcome approval uses the same review gate as a manual review.
"""

from __future__ import annotations

import json
from pathlib import Path

from advocacy_trace.store import EvidenceStore

APPROVALS_PATH = Path(__file__).resolve().parent / "fixtures" / "human_approvals.json"

_LOCK_FIELDS = (
    "summary",
    "passage",
    "location_ref",
    "author_actor",
    "attribution_role",
    "source_id",
    "remedy_requested",
    "disclaimer_text",
)

_OUTCOME_LOCK_FIELDS = (
    "description",
    "evidence_label",
    "evidence_basis",
    "public_limitation",
    "decision_id",
    "event_type",
    "event_date",
)


def apply_recorded_approvals(store: EvidenceStore, path: Path | None = None) -> list[str]:
    """Approve matching rows. Return the ids approved on this call."""

    payload = json.loads((path or APPROVALS_PATH).read_text(encoding="utf-8"))
    approved_now: list[str] = []
    for item in payload.get("approvals", []):
        argument_id = item["argument_id"]
        if not _exists(store, "arguments", argument_id):
            continue
        argument = store.get_argument(argument_id)
        if not _matches(argument, item, _LOCK_FIELDS):
            continue
        if argument["review_status"] == "approved" and argument["claim_supported"]:
            continue
        store.review(
            "argument",
            argument_id,
            "approve",
            reviewer=item["reviewer"],
            note=item["note"],
            claim_supported=True,
        )
        approved_now.append(argument_id)
    for item in payload.get("outcome_approvals", []):
        outcome_id = item["outcome_id"]
        if not _exists(store, "outcome_events", outcome_id):
            continue
        outcome = store.get_outcome(outcome_id)
        if not _matches(outcome, item, _OUTCOME_LOCK_FIELDS):
            continue
        if outcome["review_status"] == "approved":
            continue
        store.review(
            "outcome_event",
            outcome_id,
            "approve",
            reviewer=item["reviewer"],
            note=item["note"],
            claim_supported=True,
            created_at=item.get("approved_at"),
        )
        approved_now.append(outcome_id)
    return approved_now


def _exists(store: EvidenceStore, table: str, row_id: str) -> bool:
    row = store.conn.execute(
        f"SELECT 1 FROM {table} WHERE id = ?",
        (row_id,),
    ).fetchone()
    return row is not None


def _matches(record: dict, approved: dict, fields: tuple[str, ...]) -> bool:
    for field in fields:
        if record.get(field) != approved[field]:
            return False
    return True
