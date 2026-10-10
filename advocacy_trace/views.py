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
            "publication_date": raw.get("publication_date"),
            "publication_date_precision": raw.get("publication_date_precision"),
            "rights_note": raw.get("rights_note") or "",
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
            "disclaimer_status": argument.get("disclaimer_status"),
            "disclaimer_text": argument.get("disclaimer_text") or "",
            "remedy_requested": argument.get("remedy_requested") or "",
            "evidence_basis": argument.get("evidence_basis") or "not_yet_established",
            "evidence_basis_caption": evidence_basis_caption(argument.get("evidence_basis")),
            "public_limitation": argument.get("public_limitation") or "",
        },
        "case": {
            "id": case["id"],
            "title": case["title"],
            "country": case.get("country"),
            "court": case.get("court"),
            "case_number": case.get("case_number"),
            "proceeding_note": case.get("proceeding_note") or "",
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


APPEAL_OUTCOME_IDS = (
    "out_pl_appeal_podlesna",
    "out_pl_appeal_prus",
    "out_pl_appeal_gzyra",
)

APPEAL_DECISION_ID = "pl_decision_appeal_2022-01-12"

HFHR_POLISH_PASSAGES = (
    "12 stycznia 2022 r. Sąd Okręgowy w Płocku utrzymał w mocy wyrok uniewinniający trzy aktywistki oskarżone o obrazę uczuć religijnych za to, że w 2019 r. rozpowszechniały naklejki z wizerunkiem Matki Bożej Częstochowskiej z tęczową aureolą. Wyrok jest prawomocny.",
    "Sąd drugiej instancji 12 stycznia 2022 utrzymał w mocy zaskarżony wyrok i uniewinnił aktywistki. Sąd Okręgowy w Płocku zaznaczył w uzasadnieniu, że wniesione apelacje były bezzasadne.",
    "Helsińska Fundacja Praw Człowieka złożyła w sprawie opinię przyjaciela sądu.",
)

HFHR_ENGLISH_TRANSLATION = (
    "On 12 January 2022 the Regional Court in Płock upheld the acquitting judgment of three activists "
    "accused of offending religious feelings for distributing, in 2019, stickers with the image of "
    "Our Lady of Częstochowa with a rainbow halo. The judgment is final. "
    "On 12 January 2022 the second-instance court upheld the appealed judgment and acquitted the activists. "
    "The Regional Court in Płock noted in its reasoning that the appeals that had been filed were unfounded. "
    "The Helsinki Foundation for Human Rights filed an amicus opinion in the case."
)

RP_POLISH_PASSAGES = (
    "Sąd Okręgowy w Płocku utrzymał w mocy wyrok uniewinniający trzy aktywistki oskarżone o obrazę uczuć religijnych.",
    "informuje Helsińska Fundacja Praw Człowieka, która złożyła w sprawie opinię przyjaciela sądu.",
)

RP_ENGLISH_TRANSLATION = (
    "The Regional Court in Płock upheld the acquitting judgment of three activists accused of offending religious feelings. "
    "rp.pl says the Helsinki Foundation for Human Rights, which filed an amicus opinion, is the source of that account."
)

IDENTIFICATION_NOTE = (
    "The HFHR passage does not name Elżbieta Podleśna, Anna Prus, or Joanna Gzyra-Iskandar, "
    "and it does not cite II K 296/20. It identifies three activists, the Regional Court in Płock, "
    "12 January 2022, a charge of offending religious feelings, and 2019 stickers of Our Lady of "
    "Częstochowa with a rainbow halo. OKO.press, a same-day courtroom report, names Elżbieta Podleśna, "
    "Anna Prus, and Joanna Gzyra-Iskandar and says the appellate court on 12 January 2022 upheld the "
    "acquittal. That report supports the identity match. The November 2021 fairness report cites "
    "II K 296/20 as the District Court of Płock trial number for the justification dated 2 March 2021. "
    "II K 296/20 remains the trial number. ARTICLE 19 footnote 1 cites V Ka 418/21 for the 12 January 2022 "
    "judgment from an unofficial translation. That number is recorded only with ARTICLE 19's attribution. "
    "Each row is one defendant's result of the same decision. Three rows are not three decisions."
)

NOT_ACCEPTANCE_NOTE = (
    "Reception of Lisa Davis's report remains unestablished. "
    "pl_rec_legality and pl_rec_proportionality stay proposed, with status "
    "'Decision not yet retrieved'. An appeal result, including this reported affirmance, "
    "does not establish that the court accepted her arguments. "
    "That absence is not a finding that the court ignored the arguments."
)


def appeal_outcome_preview(store: EvidenceStore) -> dict:
    """How the Poland appeal would read beside the two approved arguments.

    This does not approve the outcomes, does not change their evidence label,
    and does not treat the reported result as reception of Lisa Davis's report.
    The live public export still omits these rows.
    """

    approved_ids = ("pl_arg_legality", "pl_arg_proportionality")
    arguments = []
    for argument_id in approved_ids:
        argument = store.get_argument(argument_id)
        arguments.append(
            {
                "id": argument["id"],
                "review_status": argument["review_status"],
                "summary": argument["summary"],
                "passage": argument["passage"],
                "author_actor": argument["author_actor"],
                "attribution_role": argument["attribution_role"],
                "labels": argument["labels"],
                "evidence_basis": argument.get("evidence_basis") or "not_yet_established",
                "evidence_basis_caption": evidence_basis_caption(argument.get("evidence_basis")),
                "public_limitation": argument.get("public_limitation") or "",
                "reception_note": RECEPTION_NOT_ESTABLISHED,
            }
        )
    hfhr = store.get_source("pl_src_hfhr")
    rp = store.get_source("pl_src_rp")
    names = {
        person["id"]: person["name"]
        for person in store.participants_for_case("case_poland")
    }
    amicus = [
        person
        for person in store.participants_for_case("case_poland")
        if person["role_in_case"] == "amicus"
    ]
    rows = []
    for outcome_id in APPEAL_OUTCOME_IDS:
        event = store.get_outcome(outcome_id)
        claim, _quotations = _split_claim(event["description"])
        links = []
        for link in store.evidence_links_for("outcome_event", outcome_id):
            source = store.get_source(link["source_id"])
            links.append(
                {
                    "source_id": source["id"],
                    "title": source["title"],
                    "url": source.get("url"),
                    "author_actor": source["author_actor"],
                    "publication_date": source.get("publication_date"),
                    "relationship": link["relationship"],
                    "provenance": link.get("provenance"),
                }
            )
        rows.append(
            {
                "id": event["id"],
                "stored_review_status": event["review_status"],
                "participant_id": event["participant_id"],
                "participant_name": names.get(event["participant_id"], ""),
                "event_type": event["event_type"],
                "event_date": event["event_date"],
                "event_date_precision": event["event_date_precision"],
                "proposed_public_claim": claim,
                "evidence_label": event["evidence_label"],
                "evidence_basis": event.get("evidence_basis") or "not_yet_established",
                "evidence_basis_caption": evidence_basis_caption(event.get("evidence_basis")),
                "public_limitation": event.get("public_limitation") or "",
                "decision_id": event.get("decision_id"),
                "independent_support_count": store.independent_support_count(outcome_id),
                "sources": links,
            }
        )
    counts = store.decision_counts("case_poland")
    explorer = explorer_view(
        store,
        label=None,
        country="Poland",
        intervention_type=None,
        date_from=None,
        date_to=None,
        review_status="approved",
        include_synthetic=False,
    )
    return {
        "preview_only": True,
        "this_call_approved_nothing": True,
        "approval_gate": (
            "Calling this preview approves nothing. "
            "The approval gate still refuses an Unverified outcome. "
            "A reviewed organization account uses evidence label Single-source report "
            "and evidence basis organization_account. "
            "That is not a primary-source finding. "
            f"Stored label: {rows[0]['evidence_label'] if rows else 'missing'}. "
            f"Stored review status: {rows[0]['stored_review_status'] if rows else 'missing'}."
        ),
        "current_public_explorer": {
            "filter": "Poland, no argument-label filter, so both approved arguments match",
            "argument_count": explorer["argument_count"],
            "unique_cases": explorer["unique_cases"],
            "real_cases_with_approved_argument": explorer["real_cases_with_approved_argument"],
            "argument_ids": [row["argument"]["id"] for row in explorer["rows"]],
            "outcome_status": explorer["rows"][0]["outcome"]["status"] if explorer["rows"] else "unknown",
        },
        "approved_arguments": arguments,
        "if_approved_display": {
            "case_id": "case_poland",
            "alongside": [item["id"] for item in arguments],
            "shared_decision_id": APPEAL_DECISION_ID,
            "appeal_outcome_rows": len(rows),
            "appeal_decisions": 1,
            "decision_count_note": (
                "The three defendant-specific rows share one decision_id. "
                "They are not three decisions. "
                f"The Poland proceeding as stored has {counts['defendants']} defendants, "
                f"{counts['proceedings']} proceeding, {counts['decisions']} decisions, "
                f"{counts['interventions']} intervention, and {counts['outcome_rows']} outcome rows. "
                "HFHR is an amicus participant, not a defendant and not an intervention."
            ),
            "event_date": "2022-01-12",
            "hfhr_publication_date": hfhr.get("publication_date"),
            "date_note": (
                "The event date is 12 January 2022, the court date HFHR states. "
                "The HFHR page is dated 13 January 2022. "
                "rp.pl's publication line is 13.01.2022. "
                "A later page stamp is not a new event. "
                "The publication date is not the event date."
            ),
            "hfhr_source": {
                "id": hfhr["id"],
                "title": hfhr["title"],
                "url": hfhr.get("url"),
                "author_actor": hfhr["author_actor"],
                "publication_date": hfhr.get("publication_date"),
            },
            "polish_passage": list(HFHR_POLISH_PASSAGES),
            "english_translation_label": "English translation",
            "english_translation": HFHR_ENGLISH_TRANSLATION,
            "identification": IDENTIFICATION_NOTE,
            "amicus": {
                "participant_id": amicus[0]["id"] if amicus else "",
                "name": amicus[0]["name"] if amicus else "",
                "role_in_case": amicus[0]["role_in_case"] if amicus else "",
                "brief_retrieved": False,
            },
            "evidence_category": rows[0]["evidence_label"] if rows else "",
            "evidence_basis": "organization_account",
            "evidence_basis_caption": evidence_basis_caption("organization_account"),
            "public_limitation": rows[0]["public_limitation"] if rows else "",
            "rp_pl": {
                "id": rp["id"],
                "url": rp.get("url"),
                "publication_date": rp.get("publication_date"),
                "provenance": "derived_from_shared_original",
                "role": (
                    "rp.pl draws on HFHR's account. It is not an independent confirmation "
                    "and it is not a second origin."
                ),
                "polish_passage": list(RP_POLISH_PASSAGES),
                "english_translation_label": "English translation",
                "english_translation": RP_ENGLISH_TRANSLATION,
            },
            "reception": NOT_ACCEPTANCE_NOTE,
            "defendant_rows": rows,
            "case_counts": counts,
        },
        "omitted_from_this_preview": [
            "proposed_trial_acquittals",
            "tam_records",
            "observer_note",
            "unresolved_questions",
            "research_attempts",
        ],
    }


def _split_claim(description: str) -> tuple[str, str]:
    marker = " Quotation from HFHR"
    if marker not in description:
        return description.strip(), ""
    claim, quotations = description.split(marker, 1)
    return claim.strip(), quotations.strip()


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
