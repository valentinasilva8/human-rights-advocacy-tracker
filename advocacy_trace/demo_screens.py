"""Public screen models for Advocacy Trace.

This module reads approved public projections only. It does not approve
records, seed approvals, or change stored evidence. Recorded approvals are
applied by open_store, which the evidence agent owns.

The evidence agent keeps views, the store, constants, migrations, approval,
and the evidence fixtures. Public rendering lives here so the two sides do
not both edit app.py.

Fields still absent from the public case projection, left for the evidence
agent. The argument-only preview does not wait on them:

- Follow-up search coverage is stored on research attempts, and the public
  case projection omits those attempts. Public screens say the coverage is
  not in the public record.
- No public field states implementation status. A missing update is not
  shown as failed implementation.
- An approved outcome does not carry a source URL on the public case
  projection. The direct link is shown only when an argument source already
  includes one. Outcome source links are not invented.
"""

from __future__ import annotations

import re
from pathlib import Path

from advocacy_trace.constants import (
    ARGUMENT_LABELS,
    EVIDENCE_BASIS_PUBLIC,
    RECEPTION_NOT_ESTABLISHED,
)
from advocacy_trace.dates import chronology, date_in_filter, normalize_date
from advocacy_trace.errors import ValidationError
from advocacy_trace.fixture import load_fixture
from advocacy_trace.store import EvidenceStore
from advocacy_trace.views import case_view, explorer_view

WALKTHROUGH_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "demo_ui.json"
HEADLINE_LABELS = tuple(label for label in ARGUMENT_LABELS if label != "unmapped—review required")
NOT_RECORDED = "not recorded"
SAMPLE_LIMIT = (
    "This selection cannot support a general or cross-case conclusion. "
    "The number of approved records does not change that limit."
)
BRIEF_LABEL = "Automatically assembled from approved records. Not a human-reviewed brief."
FOLLOW_UP_COVERAGE = "Follow-up search coverage is not in the public record."
IMPLEMENTATION_STATUS = (
    "No documented implementation status is in this public selection. "
    "Missing evidence is not a finding that implementation failed."
)
DATE_RULE = (
    "A month or year matches when its possible calendar range overlaps the filter. "
    "The stored precision is shown unchanged, and a missing day is not invented. "
    "With no date filter, dated and undated approved rows are both listed. "
    "With a date filter, unknown dates stay visible, are labeled date unknown, "
    "and are left out of the matched count."
)
CAUSATION_NOTE = (
    "The order of these records is not a finding that an intervention caused a later event."
)
EMPTY_REAL = (
    "No approved real records match this selection. Proposed records are not shown. "
    "This empty result is not a finding that nothing happened."
)
SYNTHETIC_BANNER = (
    "Synthetic demonstration. These records are fictional. "
    "They are excluded from real-case counts."
)
CASE_SCOPE = (
    "The rows in this selection are approved arguments. "
    "They do not approve or verify the case."
)
COURT_RECEPTION_NOT_ESTABLISHED = (
    "Court reception of the report is not established. "
    "No approved reception record is in this public selection. "
    "That absence is not acceptance and it is not rejection."
)
LATEST_IN_DATASET = (
    "Latest approved event in this dataset. "
    "This is not a claim that it is the latest development in the case."
)
CHRONOLOGY_INCOMPLETE = (
    "The public chronology is incomplete. "
    "It shows approved records only. "
    "Outcomes and receptions that have not been approved are omitted. "
    "A missing record is not a finding that a court accepted or rejected an argument, "
    "and it is not a finding that nothing else happened."
)
REMEDY_NOTE = (
    "Requested remedy, cited separately from the quotation. "
    "This is the author's request. It is not a court outcome and it is not an impact finding."
)
_URL_RE = re.compile(r"https://[^\s)>\"]+")
ROLE_TEXT = {
    "trialwatch_argument": "institutional advocacy, with TrialWatch named as the author",
    "partner_argument": "named expert or partner",
    "defense_counsel_described": "defense counsel, as described in a source",
    "authority_finding": "authority finding",
    "announcement_only": "announcement only",
    "ai_suggested": "model suggestion",
}

_ARGUMENT_KEYS = (
    "id",
    "case_id",
    "intervention_id",
    "summary",
    "passage",
    "location_ref",
    "author_actor",
    "attribution_role",
    "institutional_affiliation",
    "disclaimer_status",
    "disclaimer_text",
    "labels",
    "argument_date",
    "argument_date_precision",
    "remedy_requested",
    "public_limitation",
    "evidence_basis",
    "is_synthetic",
    "review_status",
)
_RECEPTION_KEYS = (
    "id",
    "status",
    "passage",
    "location_ref",
    "account_type",
    "is_recital",
    "public_limitation",
    "evidence_basis",
    "review_status",
)
_SOURCE_KEYS = (
    "id",
    "title",
    "url",
    "author_actor",
    "document_type",
    "publication_date",
    "publication_date_precision",
    "rights_note",
)
_EVENT_KEYS = (
    "id",
    "decision_id",
    "participant_id",
    "event_type",
    "event_date",
    "event_date_precision",
    "description",
    "evidence_label",
    "public_limitation",
    "evidence_basis",
    "procedural_stage",
    "is_synthetic",
    "review_status",
)


def open_walkthrough_store(path: str | Path) -> EvidenceStore:
    """Load the synthetic walkthrough into a new database.

    The seeded demo database and the proposed research file are not used.
    """

    store = EvidenceStore(path)
    load_fixture(store, WALKTHROUGH_FIXTURE)
    return store


def public_explorer(
    store: EvidenceStore,
    *,
    label: str | None = None,
    country: str | None = None,
    procedural_stage: str | None = None,
    intervention_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    include_synthetic: bool = False,
) -> dict:
    """Approved public rows, filtered once for the screen, the counts, and the brief."""

    requested_from, requested_to = date_from, date_to
    date_error = _date_error(date_from, date_to)
    if date_error:
        date_from = None
        date_to = None
    export = store.public_export(include_synthetic=include_synthetic)
    outcome_links = _outcome_links(store, export)
    found = explorer_view(
        store,
        label=None,
        country=None,
        intervention_type=None,
        date_from=None,
        date_to=None,
        review_status="approved",
        include_synthetic=include_synthetic,
    )
    cases = _public_cases(store, {row["case"]["id"] for row in found["rows"]})
    prepared = [
        _prepare_row(row, cases.get(row["case"]["id"]), outcome_links)
        for row in found["rows"]
    ]
    matched, date_unknown, unrecorded, outside = _partition(
            prepared,
            label=label,
            country=country,
            procedural_stage=procedural_stage,
            intervention_type=intervention_type,
            date_from=date_from,
            date_to=date_to,
        )
    counts = _counts(matched)
    return {
        "audience": "public",
        "include_synthetic": include_synthetic,
        "synthetic_banner": SYNTHETIC_BANNER if include_synthetic else "",
        "empty_real": EMPTY_REAL if counts["real_cases"] == 0 and not include_synthetic else "",
        "case_scope_note": CASE_SCOPE if counts["matched_arguments"] else "",
        "date_rule": DATE_RULE,
        "date_error": date_error,
        "filters": {
            "label": label,
            "country": country,
            "procedural_stage": procedural_stage,
            "intervention_type": intervention_type,
            "date_from": requested_from or None,
            "date_to": requested_to or None,
        },
        "filter_fields": _filter_fields(prepared),
        "matched_rows": matched,
        "date_unknown_rows": date_unknown,
        "unrecorded_rows": unrecorded,
        "outside_selection_count": outside,
        "counts": counts,
        "export_counts": {
            "real_case_count": export.get("real_case_count", 0),
            "approved_argument_count": export.get("approved_argument_count", 0),
            "outcome_event_ids": [item["id"] for item in export.get("outcome_events") or []],
            "reception_count": len(export.get("receptions") or []),
        },
        "selectable_case_ids": _case_ids(matched, date_unknown, unrecorded),
        "contract_gaps": _contract_gaps(),
    }


def public_case(
    store: EvidenceStore,
    case_id: str,
    reference_intervention_id: str | None = None,
) -> dict:
    """Four chronology bands against one named reference intervention."""

    view = case_view(store, case_id, audience="public")
    if view.get("omitted"):
        return {
            "audience": "public",
            "omitted": True,
            "reason": view.get("reason") or "No approved public record is available.",
            "case_id": case_id,
            "items": [],
            "contract_gaps": _contract_gaps(),
        }
    case = view["case"]
    interventions = list(view.get("interventions") or [])
    reference = _reference(interventions, reference_intervention_id)
    export = store.public_export(include_synthetic=bool(case.get("is_synthetic")))
    items = _chronology_items(
        view,
        reference,
        _outcome_links(store, export),
        case.get("title") or "",
    )
    coverage = _coverage(case, items)
    receptions = _case_receptions(view)
    return {
        "audience": "public",
        "omitted": False,
        "synthetic": bool(case.get("is_synthetic")),
        "synthetic_banner": SYNTHETIC_BANNER if case.get("is_synthetic") else "",
        "case": {
            "id": case.get("id"),
            "title": case.get("title"),
            "country": case.get("country") or NOT_RECORDED,
            "court": case.get("court") or NOT_RECORDED,
            "case_number": case.get("case_number") or NOT_RECORDED,
            "charges": case.get("charges") or NOT_RECORDED,
            "procedural_stage": case.get("procedural_stage") or NOT_RECORDED,
            "finality": case.get("finality") or NOT_RECORDED,
            "proceeding_note": case.get("proceeding_note") or "",
        },
        "case_scope_note": CASE_SCOPE,
        "court_reception_note": "" if any(item["established"] for item in receptions) else COURT_RECEPTION_NOT_ESTABLISHED,
        "chronology_note": CHRONOLOGY_INCOMPLETE,
        "reference_intervention": _intervention_public(reference) if reference else None,
        "other_interventions_note": (
            "Other interventions stay visible in their own bands. "
            "They are not the reference intervention."
            if len(interventions) > 1
            else ""
        ),
        "causation_note": CAUSATION_NOTE,
        "bands": {
            "before": "Before the reference intervention",
            "reference": "Reference intervention",
            "after": "After the reference intervention",
            "unknown": "Relative timing unknown",
        },
        "items": items,
        "receptions": receptions,
        "coverage": coverage,
        "gaps": [gap for gap in view.get("gaps") or [] if "PRIVATE" not in gap],
        "contract_gaps": _contract_gaps(),
    }


def public_brief(explorer: dict) -> dict:
    """Deterministic brief for the same selection the explorer counted."""

    rows = explorer.get("matched_rows") or []
    engagement = [_engagement(row) for row in rows]
    documented = []
    unknown = []
    for row in rows:
        if row["reception"]["established"]:
            documented.append(_reception_fact(row))
        else:
            unknown.append(
                {
                    "argument_id": row["argument"]["id"],
                    "case_title": row["case"]["title"],
                    "author": row["author"]["author"],
                    "statement": RECEPTION_NOT_ESTABLISHED,
                }
            )
    developments = _developments(rows)
    gaps = _evidence_gaps(rows, explorer)
    return {
        "audience": "public",
        "label": BRIEF_LABEL,
        "sample_limit": SAMPLE_LIMIT,
        "synthetic_banner": explorer.get("synthetic_banner") or "",
        "empty_real": explorer.get("empty_real") or "",
        "selection_counts": explorer.get("counts") or {},
        "facts": {
            "engagement": engagement,
            "documented_reception": documented,
            "unknown_reception": unknown,
            "developments": developments,
            "evidence_gaps": gaps,
            "implementation_status": IMPLEMENTATION_STATUS,
        },
        "suggestions": _suggestions(unknown, gaps),
        "suggestions_label": "Follow-up questions are suggestions, not established findings.",
    }


def _public_cases(store: EvidenceStore, case_ids: set[str]) -> dict[str, dict]:
    found = {}
    for case_id in case_ids:
        view = case_view(store, case_id, audience="public")
        if not view.get("omitted"):
            found[case_id] = view
    return found


def _prepare_row(row: dict, case_payload: dict | None, outcome_links: dict[str, list[dict]] | None = None) -> dict:
    argument = _pick(row["argument"], _ARGUMENT_KEYS)
    case = row["case"]
    interventions = {
        item["id"]: item for item in (case_payload or {}).get("interventions") or []
    }
    intervention = interventions.get(argument.get("intervention_id") or "")
    events = _group_events([_pick(event, _EVENT_KEYS) for event in row["outcome"].get("events") or []])
    for event in events:
        event["links"] = _links_for_rows(outcome_links, event.get("defendant_row_ids") or [])
        event["defendants_note"] = _defendants_note(event, case.get("title") or "")
    receptions = [_pick(item, _RECEPTION_KEYS) for item in row.get("receptions") or []]
    source = None
    if case_payload:
        for item in case_payload.get("arguments") or []:
            if item["argument"]["id"] == argument.get("id") and item.get("source"):
                source = _public_source(_pick(item["source"], _SOURCE_KEYS))
                break
    return {
        "argument": argument,
        "author": _author(argument),
        "case": {
            "id": case.get("id"),
            "title": case.get("title"),
            "country": case.get("country") or "",
            "procedural_stage": case.get("procedural_stage") or "",
            "is_synthetic": bool(case.get("is_synthetic")),
        },
        "intervention": _intervention_public(intervention) if intervention else None,
        "source": source,
        "reception": _reception_summary(receptions),
        "developments": _development_summary(events),
        "public_limitation": argument.get("public_limitation") or "",
        "evidence_basis": argument.get("evidence_basis") or "not_yet_established",
        "evidence_basis_caption": _basis(argument.get("evidence_basis")),
        "when": _format_date(argument.get("argument_date"), argument.get("argument_date_precision")),
    }


def _partition(
    rows: list[dict],
    *,
    label: str | None,
    country: str | None,
    procedural_stage: str | None,
    intervention_type: str | None,
    date_from: str | None,
    date_to: str | None,
) -> tuple[list[dict], list[dict], dict[str, list[dict]], int]:
    matched: list[dict] = []
    date_unknown: list[dict] = []
    unrecorded: dict[str, list[dict]] = {
        "country": [],
        "procedural_stage": [],
        "intervention_type": [],
    }
    outside = 0
    date_active = bool(date_from or date_to)
    for row in rows:
        argument = row["argument"]
        if label and label not in (argument.get("labels") or []):
            outside += 1
            continue
        country_state = _field_state(row["case"].get("country"), country)
        stage_state = _field_state(row["case"].get("procedural_stage"), procedural_stage)
        intervention_value = (row.get("intervention") or {}).get("intervention_type")
        intervention_state = _field_state(intervention_value, intervention_type)
        if "other" in {country_state, stage_state, intervention_state}:
            outside += 1
            continue
        date_state = date_in_filter(
            argument.get("argument_date"),
            argument.get("argument_date_precision") or "unknown",
            date_from,
            date_to,
        )
        if date_state is False:
            outside += 1
            continue
        blank_bucket = False
        if country_state == "blank":
            unrecorded["country"].append(row)
            blank_bucket = True
        if stage_state == "blank":
            unrecorded["procedural_stage"].append(row)
            blank_bucket = True
        if intervention_state == "blank":
            unrecorded["intervention_type"].append(row)
            blank_bucket = True
        if date_active and date_state is None:
            date_unknown.append(row)
            blank_bucket = True
        if not blank_bucket:
            matched.append(row)
    return matched, date_unknown, unrecorded, outside


def _field_state(value: str | None, selected: str | None) -> str:
    if not selected:
        return "match"
    blank = not str(value or "").strip()
    if selected == NOT_RECORDED:
        return "match" if blank else "other"
    if blank:
        return "blank"
    return "match" if value == selected else "other"


def _counts(rows: list[dict]) -> dict:
    case_ids = {row["case"]["id"] for row in rows}
    real_cases = {row["case"]["id"] for row in rows if not row["case"]["is_synthetic"]}
    demonstration_cases = case_ids - real_cases
    unknown_outcomes = {
        row["case"]["id"]
        for row in rows
        if row["developments"]["status"] == "unknown"
    }
    return {
        "matched_arguments": len(rows),
        "unique_cases": len(case_ids),
        "real_cases": len(real_cases),
        "demonstration_cases": len(demonstration_cases),
        "unknown_outcome_cases": len(unknown_outcomes),
        "count_note": (
            "Real cases and demonstration cases are counted separately. "
            "Demonstration cases are not real matters. "
            "A real case in this count has an approved argument. "
            "That does not approve or verify the case, and it is not a success rate."
        ),
    }


def _case_ids(matched: list[dict], date_unknown: list[dict], unrecorded: dict[str, list[dict]]) -> list[str]:
    titles: dict[str, str] = {}
    pool = list(matched) + list(date_unknown)
    for rows in unrecorded.values():
        pool.extend(rows)
    for row in pool:
        titles.setdefault(row["case"]["id"], row["case"]["title"] or row["case"]["id"])
    return sorted(titles, key=lambda case_id: (titles[case_id], case_id))


def _filter_fields(rows: list[dict]) -> dict:
    countries = sorted({row["case"]["country"] for row in rows if row["case"].get("country")})
    stages = sorted({row["case"]["procedural_stage"] for row in rows if row["case"].get("procedural_stage")})
    interventions = sorted(
        {
            row["intervention"]["intervention_type"]
            for row in rows
            if row.get("intervention") and row["intervention"].get("intervention_type")
        }
    )
    blank_country = any(not row["case"].get("country") for row in rows)
    blank_stage = any(not row["case"].get("procedural_stage") for row in rows)
    blank_intervention = any(not row.get("intervention") for row in rows)
    return {
        "label": list(HEADLINE_LABELS),
        "country": countries,
        "country_available": True,
        "country_not_recorded": blank_country,
        "procedural_stage": stages,
        "procedural_stage_available": True,
        "procedural_stage_not_recorded": blank_stage,
        "intervention_type": interventions,
        "intervention_type_available": True,
        "intervention_type_not_recorded": blank_intervention,
        "date_available": True,
    }


def _chronology_items(
    view: dict,
    reference: dict | None,
    outcome_links: dict[str, list[dict]] | None = None,
    case_title: str = "",
) -> list[dict]:
    items: list[dict] = []
    arguments_by_intervention: dict[str, list[dict]] = {}
    for item in view.get("arguments") or []:
        argument = _pick(item["argument"], _ARGUMENT_KEYS)
        if argument.get("review_status") not in (None, "approved"):
            continue
        if argument.get("attribution_role") not in {"trialwatch_argument", "partner_argument", "defense_counsel_described", "authority_finding", "announcement_only"}:
            continue
        intervention_id = argument.get("intervention_id") or ""
        arguments_by_intervention.setdefault(intervention_id, []).append(
            {
                "argument": argument,
                "source": _public_source(_pick(item.get("source") or {}, _SOURCE_KEYS)) if item.get("source") else None,
                "receptions": [_pick(reception, _RECEPTION_KEYS) for reception in item.get("receptions") or []],
            }
        )
    for intervention in view.get("interventions") or []:
        band = "reference" if reference and intervention["id"] == reference["id"] else _band(reference, intervention.get("intervention_date"), intervention.get("intervention_date_precision") or "unknown")
        linked = arguments_by_intervention.get(intervention["id"], [])
        links = _links_from_entries(linked)
        items.append(
            {
                "id": intervention["id"],
                "kind": "intervention",
                "band": band,
                "title": f"{intervention.get('actor') or 'Actor not recorded'} · {intervention.get('intervention_type') or NOT_RECORDED}",
                "when": _format_date(intervention.get("intervention_date"), intervention.get("intervention_date_precision")),
                "detail": {
                    "quotation": intervention.get("description") or "No description is in the public record.",
                    "location": NOT_RECORDED,
                    "url": links[0]["url"] if links else "Direct link is not in the public record.",
                    "links": links,
                    "limitation": "",
                    "evidence_basis_caption": "",
                    "linked_arguments": [
                        _argument_detail(entry) for entry in linked
                    ],
                },
            }
        )
    approved = [
        _pick(event, _EVENT_KEYS)
        for event in view.get("outcomes") or []
        if event.get("review_status") == "approved"
    ]
    for picked in _group_events(approved):
        links = _links_for_rows(outcome_links, picked.get("defendant_row_ids") or [])
        defendants_note = _defendants_note(picked, case_title)
        items.append(
            {
                "id": picked.get("decision_id") or picked.get("id") if len(picked.get("defendant_row_ids") or []) > 1 else picked.get("id"),
                "kind": "outcome",
                "band": _band(reference, picked.get("event_date"), picked.get("event_date_precision") or "unknown"),
                "title": picked.get("event_type") or "Development",
                "when": _format_date(picked.get("event_date"), picked.get("event_date_precision")),
                "summary_lines": [line for line in (defendants_note, picked.get("description") or "") if line],
                "detail": {
                    "quotation": picked.get("description") or "No description is in the public record.",
                    "location": NOT_RECORDED,
                    "url": links[0]["url"] if links else "Direct link is not in the public record.",
                    "links": links,
                    "defendants_note": defendants_note,
                    "limitation": picked.get("public_limitation") or "",
                    "evidence_basis_caption": _basis(picked.get("evidence_basis")),
                    "evidence_label": picked.get("evidence_label") or NOT_RECORDED,
                    "disposition_note": (
                        "This is a later development in the proceeding. "
                        "It is not a finding about how an authority received an argument. "
                        "Court reception of the report is not established."
                    ),
                },
            }
        )
    return items


def _band(reference: dict | None, value: str | None, precision: str) -> str:
    if reference is None:
        return "unknown"
    relation = chronology(
        reference.get("intervention_date"),
        reference.get("intervention_date_precision") or "unknown",
        value,
        precision or "unknown",
    )
    if relation.relation == "intervention_before_event":
        return "after"
    if relation.relation == "intervention_after_event":
        return "before"
    return "unknown"


def _reference(interventions: list[dict], requested: str | None) -> dict | None:
    if not interventions:
        return None
    by_id = {item["id"]: item for item in interventions}
    if requested and requested in by_id:
        return by_id[requested]
    dated = [
        item
        for item in interventions
        if item.get("intervention_date") and item.get("intervention_date_precision") not in (None, "unknown")
    ]
    if not dated:
        return interventions[0]
    return sorted(dated, key=lambda item: (item["intervention_date"], item["id"]))[0]


def _coverage(case: dict, items: list[dict]) -> dict:
    review = _format_date(case.get("last_verified_on"), case.get("last_verified_on_precision"))
    candidates = []
    for item in items:
        if item["kind"] == "outcome":
            candidates.append(
                {
                    "label": item["title"],
                    "date": _raw_date(item),
                    "precision": _raw_precision(item),
                    "when": item["when"],
                }
            )
        elif item["kind"] == "intervention" and item["when"] != "date unknown":
            candidates.append(
                {
                    "label": item["title"],
                    "date": _raw_date(item),
                    "precision": _raw_precision(item),
                    "when": item["when"],
                }
            )
    latest, note = _latest(candidates)
    return {
        "record_review": review,
        "record_review_note": (
            "This is when the record was last reviewed. "
            "It is not proof that the timeline is complete through that date."
        ),
        "latest_documented_event": latest["when"] if latest else "not recorded",
        "latest_documented_event_label": latest["label"] if latest else "",
        "latest_documented_event_note": LATEST_IN_DATASET if latest else note,
        "follow_up_search_coverage": FOLLOW_UP_COVERAGE,
    }


def _raw_date(item: dict) -> str | None:
    when = item["when"]
    if when == "date unknown":
        return None
    return when.split(" (", 1)[0]


def _raw_precision(item: dict) -> str:
    when = item["when"]
    if when == "date unknown" or "(" not in when:
        return "unknown"
    return when.split("(", 1)[1].rstrip(")")


def _latest(candidates: list[dict]) -> tuple[dict | None, str]:
    dated = [item for item in candidates if item.get("date") and item.get("precision") != "unknown"]
    if not dated:
        return None, "No documented date can be ordered. Unknown dates are not treated as the latest."
    winners = []
    for candidate in dated:
        if all(
            candidate is other
            or chronology(
                other["date"],
                other["precision"],
                candidate["date"],
                candidate["precision"],
            ).relation
            == "intervention_before_event"
            for other in dated
        ):
            winners.append(candidate)
    if len(winners) == 1:
        return winners[0], "Only a date that falls wholly after the others is called the latest."
    return None, "More than one documented date overlaps, so none is shown as the latest."


def _case_receptions(view: dict) -> list[dict]:
    rows = []
    for item in view.get("arguments") or []:
        argument = _pick(item["argument"], _ARGUMENT_KEYS)
        if argument.get("review_status") not in (None, "approved"):
            continue
        receptions = [_pick(reception, _RECEPTION_KEYS) for reception in item.get("receptions") or []]
        summary = _reception_summary(receptions)
        rows.append(
            {
                "argument_id": argument.get("id"),
                "author": _author(argument),
                "summary": argument.get("summary") or "",
                "established": summary["established"],
                "statement": summary["statement"],
                "records": summary["records"],
            }
        )
    return rows


def _engagement(row: dict) -> dict:
    source = row.get("source") or {}
    links = list(source.get("links") or _source_links(source))
    remedy = (row["argument"].get("remedy_requested") or "").strip()
    return {
        "argument_id": row["argument"]["id"],
        "case_title": row["case"]["title"],
        "summary": row["argument"].get("summary") or "",
        "author": row["author"],
        "intervention_type": (row.get("intervention") or {}).get("intervention_type") or NOT_RECORDED,
        "quotation": row["argument"].get("passage") or "",
        "location": row["argument"].get("location_ref") or NOT_RECORDED,
        "remedy": remedy,
        "remedy_note": REMEDY_NOTE if remedy else "",
        "source_title": source.get("title") or NOT_RECORDED,
        "source_url": links[0]["url"] if links else "Direct link is not in the public record.",
        "links": links,
        "when": row["when"],
    }


def _reception_fact(row: dict) -> dict:
    return {
        "argument_id": row["argument"]["id"],
        "case_title": row["case"]["title"],
        "author": row["author"]["author"],
        "statement": row["reception"]["statement"],
        "records": row["reception"]["records"],
    }


def _developments(rows: list[dict]) -> list[dict]:
    seen: set[str] = set()
    found = []
    for row in rows:
        for event in row["developments"]["events"]:
            key = event.get("decision_id") or event.get("id")
            if key in seen:
                continue
            seen.add(key)
            found.append(
                {
                    "case_title": row["case"]["title"],
                    "event_id": event.get("decision_id") or event.get("id"),
                    "event_type": event.get("event_type"),
                    "when": _format_date(event.get("event_date"), event.get("event_date_precision")),
                    "description": event.get("description") or "",
                    "defendants_note": event.get("defendants_note") or "",
                    "links": event.get("links") or [],
                    "limitation": event.get("public_limitation") or "",
                    "evidence_basis_caption": _basis(event.get("evidence_basis")),
                    "dataset_note": LATEST_IN_DATASET,
                    "reception_note": (
                        "This development is not a reception finding. "
                        "Court reception of the report is not established. "
                        "Reception is recorded only in the reception sections."
                    ),
                }
            )
    return found


def _evidence_gaps(rows: list[dict], explorer: dict) -> list[str]:
    gaps = []
    for row in rows:
        if row.get("public_limitation"):
            gaps.append(f"{row['case']['title']}: {row['public_limitation']}")
        for event in row["developments"]["events"]:
            if event.get("public_limitation"):
                gaps.append(f"{event.get('event_type')}: {event['public_limitation']}")
        for reception in row["reception"]["records"]:
            if reception.get("public_limitation"):
                gaps.append(reception["public_limitation"])
    if explorer.get("date_unknown_rows"):
        gaps.append(
            f"{len(explorer['date_unknown_rows'])} approved argument(s) have an unknown date "
            "and are outside this date selection. They remain listed on the explorer."
        )
    gaps.append(FOLLOW_UP_COVERAGE)
    return gaps


def _suggestions(unknown: list[dict], gaps: list[str]) -> list[str]:
    suggestions = [
        "Which approved source, if any, shows how an authority dealt with each argument whose reception is unknown?",
        "Which later sources were searched for developments, and what period did that search cover?",
    ]
    if not unknown:
        suggestions[0] = (
            "Where a reception is documented, which surrounding paragraphs limit how far that finding reaches?"
        )
    if gaps:
        suggestions.append("Which public limitations would change if the missing source were obtained?")
    return suggestions


def _development_summary(events: list[dict]) -> dict:
    dated = []
    undated = []
    for event in events:
        when = _format_date(event.get("event_date"), event.get("event_date_precision"))
        record = {**event, "when": when}
        if when == "date unknown":
            undated.append(record)
        else:
            dated.append(
                {
                    "label": event.get("event_type") or "Development",
                    "date": event.get("event_date"),
                    "precision": event.get("event_date_precision") or "unknown",
                    "when": when,
                    "event": record,
                }
            )
    latest, note = _latest(dated)
    return {
        "status": "dated_events" if events else "unknown",
        "events": events,
        "latest": latest["event"] if latest else None,
        "latest_when": latest["when"] if latest else "",
        "latest_note": LATEST_IN_DATASET if latest else note,
        "undated": undated,
        "statement": (
            "Dated approved events in this dataset are listed with the precision that was stored. "
            "They are not a success or failure score, and they do not show that an argument caused the event. "
            "An incomplete list is not a finding that no other development occurred."
            if events
            else (
                "No verified subsequent outcome is on record. Unknown is not a finding that "
                "the person is still detained, that the case is ongoing, or that advocacy failed."
            )
        ),
    }


def _reception_summary(receptions: list[dict]) -> dict:
    if not receptions:
        return {
            "established": False,
            "statement": RECEPTION_NOT_ESTABLISHED,
            "records": [],
        }
    parts = []
    for reception in receptions:
        account = reception.get("account_type") or "not_yet_established"
        prefix = "Recital, not acceptance. " if reception.get("is_recital") else ""
        parts.append(f"{prefix}{reception.get('status')} · {account}")
    return {
        "established": True,
        "statement": "; ".join(parts),
        "records": receptions,
    }


def _author(argument: dict) -> dict:
    status = argument.get("disclaimer_status") or "not_yet_checked"
    if status == "stated":
        disclaimer = argument.get("disclaimer_text") or "A disclaimer is stated in the source."
    elif status == "not_stated_in_source":
        disclaimer = "No disclaimer is stated in the source."
    else:
        disclaimer = "The source has not yet been checked for a disclaimer."
    return {
        "author": argument.get("author_actor") or "author not recorded",
        "role": ROLE_TEXT.get(argument.get("attribution_role") or "", argument.get("attribution_role") or NOT_RECORDED),
        "role_code": argument.get("attribution_role"),
        "affiliation": argument.get("institutional_affiliation") or "affiliation not recorded",
        "disclaimer": disclaimer,
    }


def _argument_detail(entry: dict) -> dict:
    argument = entry["argument"]
    source = entry.get("source") or {}
    links = list(source.get("links") or _source_links(source))
    remedy = (argument.get("remedy_requested") or "").strip()
    return {
        "id": argument.get("id"),
        "author": _author(argument),
        "summary": argument.get("summary") or "",
        "quotation": argument.get("passage") or "",
        "location": argument.get("location_ref") or NOT_RECORDED,
        "remedy": remedy,
        "remedy_note": REMEDY_NOTE if remedy else "",
        "url": links[0]["url"] if links else "Direct link is not in the public record.",
        "links": links,
        "source_title": source.get("title") or NOT_RECORDED,
        "when": _format_date(argument.get("argument_date"), argument.get("argument_date_precision")),
        "limitation": argument.get("public_limitation") or "",
        "evidence_basis_caption": _basis(argument.get("evidence_basis")),
        "labels": argument.get("labels") or [],
    }


def _public_source(source: dict) -> dict:
    public = dict(source)
    public["links"] = _source_links(public)
    public["when"] = _format_date(public.get("publication_date"), public.get("publication_date_precision"))
    public.pop("rights_note", None)
    return public


def _source_links(source: dict | None) -> list[dict]:
    """Report page from the public URL, plus any other https links in the rights note."""

    if not source:
        return []
    found: list[dict] = []
    seen: set[str] = set()

    def add(url: str, *, from_url_field: bool) -> None:
        cleaned = url.strip().rstrip(").,;")
        if not cleaned.startswith("https://") or cleaned in seen:
            return
        seen.add(cleaned)
        found.append({"url": cleaned, "label": _link_label(cleaned, from_url_field=from_url_field)})

    primary = str(source.get("url") or "")
    if primary:
        add(primary, from_url_field=True)
    for match in _URL_RE.findall(str(source.get("rights_note") or "")):
        add(match, from_url_field=False)
    return found


def _links_from_entries(entries: list[dict]) -> list[dict]:
    found: list[dict] = []
    seen: set[str] = set()
    for entry in entries:
        for link in (entry.get("source") or {}).get("links") or _source_links(entry.get("source")):
            if link["url"] in seen:
                continue
            seen.add(link["url"])
            found.append(link)
    return found


def _link_label(url: str, *, from_url_field: bool) -> str:
    path = url.split("?", 1)[0].split("#", 1)[0].lower()
    if path.endswith(".pdf"):
        return "PDF"
    if from_url_field:
        return "Report page"
    return "Source page"


def _intervention_public(intervention: dict | None) -> dict | None:
    if not intervention:
        return None
    return {
        "id": intervention.get("id"),
        "actor": intervention.get("actor") or "actor not recorded",
        "intervention_type": intervention.get("intervention_type") or "",
        "when": _format_date(intervention.get("intervention_date"), intervention.get("intervention_date_precision")),
        "description": intervention.get("description") or "",
    }


def _basis(value: str | None) -> str:
    return EVIDENCE_BASIS_PUBLIC.get(value or "not_yet_established", EVIDENCE_BASIS_PUBLIC["not_yet_established"])


def _format_date(value: str | None, precision: str | None) -> str:
    if not value or precision in (None, "", "unknown"):
        return "date unknown"
    return f"{value} ({precision})"


def _date_error(date_from: str | None, date_to: str | None) -> str:
    try:
        for value in (date_from, date_to):
            if value:
                normalize_date(value, _input_precision(value))
    except ValidationError as exc:
        return str(exc)
    return ""


def _input_precision(value: str) -> str:
    if len(value) == 10:
        return "day"
    if len(value) == 7:
        return "month"
    if len(value) == 4:
        return "year"
    raise ValidationError(
        f"Could not read '{value}' as a date. Use YYYY-MM-DD, YYYY-MM, or YYYY."
    )


def _group_events(events: list[dict]) -> list[dict]:
    """Collapse defendant-specific rows that share one decision_id."""

    groups: dict[str, dict] = {}
    order: list[str] = []
    for event in events:
        key = (event.get("decision_id") or "").strip() or event.get("id") or ""
        if key not in groups:
            order.append(key)
            groups[key] = {
                "id": event.get("id"),
                "decision_id": (event.get("decision_id") or "").strip(),
                "event_type": event.get("event_type"),
                "event_date": event.get("event_date"),
                "event_date_precision": event.get("event_date_precision"),
                "description": event.get("description") or "",
                "public_limitation": event.get("public_limitation") or "",
                "evidence_basis": event.get("evidence_basis"),
                "evidence_label": event.get("evidence_label"),
                "review_status": event.get("review_status"),
                "defendant_row_ids": [],
            }
        row_id = event.get("id")
        if row_id and row_id not in groups[key]["defendant_row_ids"]:
            groups[key]["defendant_row_ids"].append(row_id)
    return [groups[key] for key in order]


def _defendants_note(event: dict, case_title: str) -> str:
    row_ids = event.get("defendant_row_ids") or []
    if len(row_ids) < 2:
        return ""
    named = f" The case title names them: {case_title}." if case_title else ""
    return (
        f"One approved event. {len(row_ids)} defendant-specific rows share it. "
        f"They are not separate decisions.{named}"
    )


def _outcome_links(store: EvidenceStore, export: dict) -> dict[str, list[dict]]:
    """Source links for outcome ids that the approved export already includes."""

    sources = {item["id"]: item for item in export.get("sources") or []}
    allowed = {item["id"] for item in export.get("outcome_events") or []}
    found: dict[str, list[dict]] = {}
    for outcome_id in allowed:
        links = []
        seen: set[str] = set()
        for link in store.evidence_links_for("outcome_event", outcome_id):
            source = sources.get(link["source_id"])
            url = str((source or {}).get("url") or "").strip()
            if not url or url in seen:
                continue
            seen.add(url)
            links.append(
                {
                    "url": url,
                    "label": _outcome_source_label(source, link),
                    "note": _provenance_note(link.get("provenance")),
                }
            )
        found[outcome_id] = links
    return found


def _links_for_rows(outcome_links: dict[str, list[dict]] | None, row_ids: list[str]) -> list[dict]:
    found: list[dict] = []
    seen: set[str] = set()
    for row_id in row_ids:
        for link in (outcome_links or {}).get(row_id) or []:
            if link["url"] in seen:
                continue
            seen.add(link["url"])
            found.append(link)
    return found


def _outcome_source_label(source: dict, link: dict) -> str:
    author = source.get("author_actor") or "Source"
    if link.get("provenance") == "derived_from_shared_original":
        return f"{author} (not an independent origin)"
    if source.get("author_actor") == "Helsinki Foundation for Human Rights":
        return f"{author} (organization account)"
    return author


def _provenance_note(provenance: str | None) -> str:
    if provenance == "derived_from_shared_original":
        return "Draws on the same account. Not an independent origin."
    if provenance == "independent":
        return "Separate report in this export. Not the judgment."
    return ""


def _pick(row: dict, keys: tuple[str, ...]) -> dict:
    return {key: row.get(key) for key in keys}


def _contract_gaps() -> list[str]:
    return [
        FOLLOW_UP_COVERAGE,
        IMPLEMENTATION_STATUS,
        "Approved outcomes do not include a direct source link on the public case projection.",
    ]
