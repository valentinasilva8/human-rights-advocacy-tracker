"""Apply approvals a person has already given.

The research file cannot approve itself. This module approves a row only when
the stored claim, quotation, remedy text, and disclaimer still match the text
that was approved. A mismatch leaves the row proposed.
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


def apply_recorded_approvals(store: EvidenceStore, path: Path | None = None) -> list[str]:
    """Approve matching rows. Return the ids approved on this call."""

    payload = json.loads((path or APPROVALS_PATH).read_text(encoding="utf-8"))
    approved_now: list[str] = []
    for item in payload["approvals"]:
        argument_id = item["argument_id"]
        if not _exists(store, argument_id):
            continue
        argument = store.get_argument(argument_id)
        if not _matches(argument, item):
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
    return approved_now


def _exists(store: EvidenceStore, argument_id: str) -> bool:
    row = store.conn.execute(
        "SELECT 1 FROM arguments WHERE id = ?",
        (argument_id,),
    ).fetchone()
    return row is not None


def _matches(argument: dict, approved: dict) -> bool:
    for field in _LOCK_FIELDS:
        if argument.get(field) != approved[field]:
            return False
    return True
