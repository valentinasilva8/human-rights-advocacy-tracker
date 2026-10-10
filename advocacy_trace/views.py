"""Screen data for the explorer, the case view, and the review queue."""

from __future__ import annotations

from advocacy_trace.constants import (
    EVIDENCE_BASIS_PUBLIC,
    PUBLIC_ARGUMENT_ROLES,
    RECEPTION_NOT_ESTABLISHED,
)
from advocacy_trace.dates import chronology
from advocacy_trace.store import EvidenceStore


def explorer_view(
    store: EvidenceStore,
    *,
    label: str | None,
    country: str | None,
    intervention_type: str | None,
    date_from: str | None,
    date_to: str | None,
    review_status: str | None,
    include_synthetic: bool,
) -> dict:
    """Public explorer. Proposed, sensitive, and non-advocacy roles stay out."""

    found = store.search_arguments(
        label=label,
        country=country,
        intervention_type=intervention_type,
        date_from=date_from or None,
        date_to=date_to or None,
        review_status="approved",
        attribution_roles=PUBLIC_ARGUMENT_ROLES,
        include_synthetic=include_synthetic,
        exclude_sensitive=True,
    )
    real = store.search_arguments(
        label=label,
        country=country,
        intervention_type=intervention_type,
        date_from=date_from or None,
        date_to=date_to or None,
        review_status="approved",
        attribution_roles=PUBLIC_ARGUMENT_ROLES,
        include_synthetic=False,
        exclude_sensitive=True,
    )
    rows = []
    for argument in found["arguments"]:
        case = _public_case_fields(store.get_case(argument["case_id"]))
        rows.append(
            {
                "argument": argument,
                "case": case,
                "receptions": _approved_receptions(store, argument["id"]),
                "outcome": store.outcome_summary(case["id"]),
                "gaps": gaps_for_argument(store, argument),
            }
        )
    unknown_outcomes = len(
        {row["case"]["id"] for row in rows if row["outcome"]["status"] == "unknown"}
    )
    filter_note = (
        "real_cases_with_approved_argument counts non-synthetic cases that have an "
        "approved TrialWatch or partner argument matching these filters. "
        "Sensitive cases are excluded. One approved argument does not verify the case."
    )
    return {
        "rows": rows,
        "argument_count": found["argument_count"],
        "unique_cases": found["unique_cases"],
        "real_cases_with_approved_argument": real["unique_cases"],
        "verified_real_cases": real["unique_cases"],
        "hidden_unknown_dates": found["hidden_unknown_dates"],
        "unknown_outcome_cases": unknown_outcomes,
        "note": filter_note,
        "ignored_review_status": review_status,
    }


def case_view(store: EvidenceStore, case_id: str, *, audience: str = "public") -> dict:
    case = store.get_case(case_id)
    if audience == "public" and case["sensitive"]:
        return {
            "omitted": True,
            "reason": "Restricted record. It is omitted from public views.",
            "case": {"id": case_id, "sensitive": True},
            "arguments": [],
            "outcomes": [],
            "receptions_hidden": True,
        }
    arguments = store.arguments_for_case(case_id)
    events = store.outcome_events(case_id)
    if audience == "public":
        arguments = [
            item
            for item in arguments
            if item["review_status"] == "approved" and item["attribution_role"] != "ai_suggested"
        ]
        events = [item for item in events if item["review_status"] == "approved"]
        if not arguments and not events:
            return {
                "omitted": True,
                "reason": "No approved, non-sensitive record is available for public view.",
                "case": {"id": case_id},
                "arguments": [],
                "outcomes": [],
            }
        case = _public_case_fields(case)
    notes = chronology_notes(store.interventions_for_case(case_id), events)
    return {
        "omitted": False,
        "case": case,
        "participants": store.participants_for_case(case_id),
        "interventions": store.interventions_for_case(case_id),
        "arguments": [
            {
                "argument": argument,
                "receptions": (
                    _approved_receptions(store, argument["id"])
                    if audience == "public"
                    else store.receptions_for_argument(argument["id"])
                ),
                "source": _public_source_fields(store, argument["source_id"])
                if argument["source_id"]
                else None,
            }
            for argument in arguments
        ],
        "outcomes": events,
        "outcome_summary": store.outcome_summary(case_id),
        "chronology_notes": notes,
        "gaps": gaps_for_case(store, case_id),
        "research_attempts": (
            store.research_attempts_for_case(case_id) if audience == "internal" else []
        ),
    }


def gaps_for_argument(store: EvidenceStore, argument: dict) -> list[str]:
    """Gaps for one argument. Other arguments in the case are not mixed in."""

    case = store.get_case(argument["case_id"])
    gaps: list[str] = []
    if case["is_synthetic"]:
        gaps.append(
            "Demonstration record. Exampleland is not a real jurisdiction, and this case is excluded from real-case metrics."
        )
    if case["sensitive"]:
        gaps.append("Restricted record. It is omitted from the public export.")
    summary = store.outcome_summary(case["id"])
    if summary["status"] == "unknown":
        gaps.append(summary["statement"])
    if argument["attribution_role"] == "announcement_only":
        gaps.append("This extraction is based on an announcement, not the full document.")
    if (
        argument["review_status"] == "approved"
        and argument["attribution_role"] in PUBLIC_ARGUMENT_ROLES
    ):
        gaps.extend(_reception_gaps(store, argument))
    if argument.get("disclaimer_status") == "not_yet_checked":
        gaps.append("The source has not yet been checked for a disclaimer.")
    elif argument.get("disclaimer_status") == "not_stated_in_source":
        gaps.append("No disclaimer is stated in the source.")
    return gaps


def gaps_for_case(store: EvidenceStore, case_id: str) -> list[str]:
    case = store.get_case(case_id)
    gaps: list[str] = []
    if case["is_synthetic"]:
        gaps.append(
            "Demonstration record. Exampleland is not a real jurisdiction, and this case is excluded from real-case metrics."
        )
    if case["sensitive"]:
        gaps.append("Restricted record. It is omitted from the public export.")
    summary = store.outcome_summary(case_id)
    if summary["status"] == "unknown":
        gaps.append(summary["statement"])
    announced = False
    for argument in store.arguments_for_case(case_id):
        if argument["attribution_role"] == "announcement_only" and not announced:
            gaps.append(
                "At least one extraction is based on an announcement, not the full document."
            )
            announced = True
        if (
            argument["review_status"] == "approved"
            and argument["attribution_role"] in PUBLIC_ARGUMENT_ROLES
        ):
            gaps.extend(_reception_gaps(store, argument))
    return gaps


def _reception_gaps(store: EvidenceStore, argument: dict) -> list[str]:
    reviewed = [
        item
        for item in store.receptions_for_argument(argument["id"])
        if item["review_status"] == "approved"
    ]
    gaps: list[str] = []
    where = argument["location_ref"] or "location missing"
    if not reviewed:
        gaps.append(f"{RECEPTION_NOT_ESTABLISHED} ({where}).")
        return gaps
    for item in reviewed:
        if item["status"] == "Decision unavailable / insufficient evidence":
            gaps.append(f"The available material does not contain a decision on this argument ({where}).")
        if item["status"] == "Decision not yet retrieved":
            gaps.append(f"The decision has not yet been retrieved ({where}). That is not a finding that no decision exists.")
        if item["status"] == "Decision sought but unavailable":
            gaps.append(f"The decision was sought and is unavailable ({where}).")
        if item["status"] == "Document obtained but reasoning insufficient":
            gaps.append(
                f"A document is in hand, and its reasoning is not enough to determine reception ({where})."
            )
        if item["status"] == "Not addressed in the available decision":
            gaps.append(
                f"A reviewer checked the cited decision and the argument was not addressed ({where})."
            )
        if item.get("account_type") == "secondary_account":
            gaps.append(f"This reception is a secondary account, not the authority's own document ({where}).")
        if item["is_recital"]:
            gaps.append(
                f"A reviewed passage recites this argument ({where}). That recital is not recorded as acceptance."
            )
    return gaps


def chronology_notes(interventions: list[dict], events: list[dict]) -> list[str]:
    notes: list[str] = []
    for intervention in interventions:
        for event in events:
            if event["review_status"] != "approved":
                continue
            relation = chronology(
                intervention["intervention_date"],
                intervention["intervention_date_precision"],
                event["event_date"],
                event["event_date_precision"],
            )
            if relation.relation == "intervention_after_event":
                notes.append(
                    f"{intervention['intervention_type']} on {intervention['intervention_date']} "
                    f"comes after {event['event_type']} on {event['event_date']}. "
                    "It is not treated as explaining that earlier event."
                )
            elif relation.relation == "unknown":
                notes.append(
                    f"The order of {intervention['intervention_type']} and {event['event_type']} "
                    "is unknown at the available date precision."
                )
    return notes


def public_preview(store: EvidenceStore, argument_id: str) -> dict:
    """Public shape of one argument if it were approved. This does not approve it.

    Proposed siblings, reviewer notes, unresolved questions, and research notes stay out.
    An absent reception is not described as the court ignoring the argument.
    """

    argument = store.get_argument(argument_id)
    case = store.get_case(argument["case_id"])
    source = None
    if argument.get("source_id"):
        raw = store.get_source(argument["source_id"])
        source = {
            "id": raw["id"],
            "title": raw["title"],
            "url": raw.get("url"),
            "author_actor": raw["author_actor"],
            "document_type": raw["document_type"],
        }
    approved_receptions = _approved_receptions(store, argument_id)
    return {
        "preview_only": True,
        "this_call_approved_nothing": True,
        "stored_review_status": argument["review_status"],
        "argument": {
            "id": argument["id"],
            "summary": argument["summary"],
            "passage": argument["passage"],
            "location_ref": argument["location_ref"],
            "author_actor": argument["author_actor"],
            "attribution_role": argument["attribution_role"],
            "labels": argument["labels"],
            "evidence_basis": argument.get("evidence_basis") or "not_yet_established",
            "evidence_basis_caption": evidence_basis_caption(argument.get("evidence_basis")),
            "public_limitation": argument.get("public_limitation") or "",
        },
        "case": {
            "id": case["id"],
            "title": case["title"],
            "country": case.get("country"),
            "case_number": case.get("case_number"),
        },
        "source": source,
        "receptions": approved_receptions,
        "reception_note": RECEPTION_NOT_ESTABLISHED if not approved_receptions else "",
        "timeline_note": (
            "An incomplete list is not a finding that no other development occurred. "
            "Proposed outcome records are not shown in this preview."
        ),
        "omitted": [
            "observer_note",
            "unresolved_questions",
            "research_attempts",
            "proposed_siblings",
        ],
    }


def evidence_basis_caption(value: str | None) -> str:
    return EVIDENCE_BASIS_PUBLIC.get(value or "not_yet_established", "")


def _approved_receptions(store: EvidenceStore, argument_id: str) -> list[dict]:
    hidden = {"observer_note"}
    return [
        {key: value for key, value in item.items() if key not in hidden}
        for item in store.receptions_for_argument(argument_id)
        if item["review_status"] == "approved"
    ]


def _public_case_fields(case: dict) -> dict:
    return {key: value for key, value in case.items() if key != "unresolved_questions"}


def _public_source_fields(store: EvidenceStore, source_id: str) -> dict:
    source = store.get_source(source_id)
    return {key: value for key, value in source.items() if key != "untrusted_text"}
