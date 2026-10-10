"""Load proposed real records. This module never approves them."""

from __future__ import annotations

import json
from pathlib import Path

from advocacy_trace.store import EvidenceStore

PROPOSED_PATH = Path(__file__).resolve().parent / "fixtures" / "proposed_research.json"


def load_proposed_research(store: EvidenceStore, path: Path | None = None) -> None:
    payload = json.loads((path or PROPOSED_PATH).read_text(encoding="utf-8"))
    for person in payload["participants"]:
        if not _exists(store, "participants", person["id"]):
            store.add_participant(**person)
    for case in payload["cases"]:
        if not _exists(store, "cases", case["id"]):
            store.add_case(**case)
    for link in payload["links"]:
        store.link_participant(**link)
    for source in payload["sources"]:
        if not _exists(store, "sources", source["id"]):
            store.add_source(**source)
    for intervention in payload["interventions"]:
        if not _exists(store, "interventions", intervention["id"]):
            store.add_intervention(**intervention)
    for argument in payload["arguments"]:
        if _exists(store, "arguments", argument["id"]):
            continue
        store.add_argument(**argument)
        if store.get_argument(argument["id"])["review_status"] != "proposed":
            raise RuntimeError("Research import must leave arguments proposed.")
    for outcome in payload["outcomes"]:
        if not _exists(store, "outcome_events", outcome["id"]):
            store.add_outcome_event(**outcome)
    for reception in payload["receptions"]:
        if not _exists(store, "reception_observations", reception["id"]):
            store.add_reception(**reception)
    for link in payload["evidence_links"]:
        if not _exists(store, "evidence_links", link["id"]):
            store.add_evidence_link(**link)
    for attempt in payload["research_attempts"]:
        if not _exists(store, "research_attempts", attempt["id"]):
            store.add_research_attempt(**attempt)


def _exists(store: EvidenceStore, table: str, row_id: str) -> bool:
    row = store.conn.execute(f"SELECT 1 FROM {table} WHERE id = ?", (row_id,)).fetchone()
    return row is not None
