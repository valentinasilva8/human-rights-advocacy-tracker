"""Load the committed fictional evidence chain."""

from __future__ import annotations

import json
from pathlib import Path

from advocacy_trace.store import EvidenceStore

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "synthetic_chain.json"


def load_fixture(store: EvidenceStore, path: Path | None = None) -> None:
    payload = json.loads((path or FIXTURE_PATH).read_text(encoding="utf-8"))
    for person in payload["participants"]:
        store.add_participant(**person)
    for case in payload["cases"]:
        store.add_case(**case)
    for link in payload["links"]:
        store.link_participant(**link)
    for source in payload["sources"]:
        store.add_source(**source)
    for intervention in payload["interventions"]:
        store.add_intervention(**intervention)
    for argument in payload["arguments"]:
        store.add_argument(**argument)
    for outcome in payload["outcomes"]:
        store.add_outcome_event(**outcome)
    for reception in payload["receptions"]:
        store.add_reception(**reception)
    for link in payload["evidence_links"]:
        store.add_evidence_link(**link)
    for action in payload["reviews"]:
        store.review(**action)
