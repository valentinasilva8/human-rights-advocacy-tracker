"""Screen data for the explorer, the case view, and the review queue."""

from __future__ import annotations

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
    found = store.search_arguments(
        label=label,
        country=country,
        intervention_type=intervention_type,
        date_from=date_from or None,
        date_to=date_to or None,
        review_status=review_status,
        attribution_role="trialwatch_argument",
        include_synthetic=include_synthetic,
    )
    verified = store.verified_summary(label or "Proportionality")
    rows = []
    for argument in found["arguments"]:
        case = store.get_case(argument["case_id"])
        rows.append(
            {
                "argument": argument,
                "case": case,
                "receptions": store.receptions_for_argument(argument["id"]),
                "outcome": store.outcome_summary(case["id"]),
                "gaps": gaps_for_argument(store, argument),
            }
        )
    unknown_outcomes = len(
        {row["case"]["id"] for row in rows if row["outcome"]["status"] == "unknown"}
    )
    return {
        "rows": rows,
        "argument_count": found["argument_count"],
        "unique_cases": found["unique_cases"],
        "verified_real_cases": verified["unique_cases"],
        "hidden_unknown_dates": found["hidden_unknown_dates"],
        "unknown_outcome_cases": unknown_outcomes,
        "note": verified["note"],
    }


def case_view(store: EvidenceStore, case_id: str) -> dict:
    case = store.get_case(case_id)
    arguments = store.arguments_for_case(case_id)
    events = store.outcome_events(case_id)
    notes = chronology_notes(store.interventions_for_case(case_id), events)
    return {
        "case": case,
        "participants": store.participants_for_case(case_id),
        "interventions": store.interventions_for_case(case_id),
        "arguments": [
            {
                "argument": argument,
                "receptions": store.receptions_for_argument(argument["id"]),
                "source": store.get_source(argument["source_id"]) if argument["source_id"] else None,
            }
            for argument in arguments
        ],
        "outcomes": events,
        "outcome_summary": store.outcome_summary(case_id),
        "chronology_notes": notes,
        "gaps": gaps_for_case(store, case_id),
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
        and argument["attribution_role"] == "trialwatch_argument"
    ):
        gaps.extend(_reception_gaps(store, argument))
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
            and argument["attribution_role"] == "trialwatch_argument"
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
        gaps.append(f"No reviewed record of how an authority received this argument ({where}).")
        return gaps
    for item in reviewed:
        if item["status"] == "Decision unavailable / insufficient evidence":
            gaps.append(f"The available material does not contain a decision on this argument ({where}).")
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
