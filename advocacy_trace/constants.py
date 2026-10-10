"""Closed vocabularies. Headline argument labels are not extended here."""

ARGUMENT_LABELS = (
    "Vagueness",
    "Broadness",
    "Legality",
    "Necessity",
    "Proportionality",
    "unmapped—review required",
)

ATTRIBUTION_ROLES = (
    "trialwatch_argument",
    "partner_argument",
    "defense_counsel_described",
    "authority_finding",
    "announcement_only",
    "ai_suggested",
)

TRIALWATCH_AUTHORS = frozenset({"trialwatch", "trial watch"})

DOCUMENT_TYPES = (
    "fairness_report",
    "amicus",
    "submission",
    "announcement",
    "judgment",
    "news",
    "un_opinion",
    "other",
)

INTERVENTION_TYPES = (
    "fairness_report",
    "amicus",
    "submission",
    "monitoring",
    "statement",
    "announcement",
)

DATE_PRECISIONS = ("day", "month", "year", "unknown")

REVIEW_STATUSES = ("proposed", "approved", "rejected")

EVENT_TYPES = (
    "Charges filed",
    "Charges amended",
    "Charges withdrawn",
    "Charges dismissed",
    "Conviction",
    "Acquittal",
    "Appeal filed",
    "Appeal decided",
    "Appeal withdrawn",
    "Release",
    "Continued detention",
    "Sentence imposed",
    "Sentence modification",
    "Retrial ordered",
    "Compensation ordered",
    "Compensation received",
    "Continuing restrictions",
    "New proceeding",
    "No verified recent update",
)

NO_UPDATE_EVENT = "No verified recent update"

EVIDENCE_LABELS = (
    "Primary-source supported",
    "Corroborated by independent sources",
    "Single-source report",
    "Conflicting",
    "Unverified",
)

RECEPTION_STATUSES = (
    "Explicitly accepted",
    "Partially accepted",
    "Explicitly rejected",
    "Discussed without clear resolution",
    "Not addressed in the available decision",
    "Decision not yet retrieved",
    "Decision sought but unavailable",
    "Document obtained but reasoning insufficient",
    "Decision unavailable / insufficient evidence",
    "Not applicable",
)

ACCEPTANCE_STATUSES = frozenset({"Explicitly accepted", "Partially accepted"})

RECEPTION_NEEDS_SOURCE = frozenset(
    {
        "Explicitly accepted",
        "Partially accepted",
        "Explicitly rejected",
        "Discussed without clear resolution",
        "Not addressed in the available decision",
        "Document obtained but reasoning insufficient",
    }
)

EXPLICIT_RECEPTION = frozenset(
    {
        "Explicitly accepted",
        "Partially accepted",
        "Explicitly rejected",
        "Discussed without clear resolution",
    }
)

DISCLAIMER_STATUSES = ("not_yet_checked", "not_stated_in_source", "stated")

PROVENANCE_VALUES = (
    "unknown",
    "duplicate_copy",
    "derived_from_shared_original",
    "same_organization_distinct",
    "independent",
)

# How much of the stored claim a link supports. Identity or the reported
# result, alone or together, is not support for every assertion on the record.
SUPPORT_SCOPE_VALUES = (
    "whole_claim",
    "identity",
    "reported_result",
    "identity_and_reported_result",
)

PUBLIC_EXPORT_SCHEMA_VERSION = "1"

TIMELINE_CAPTION = "Latest approved event in this dataset."

ACCOUNT_TYPES = ("not_yet_established", "authority_document", "secondary_account")

EVIDENCE_BASIS = (
    "not_yet_established",
    "author_document",
    "authenticated_judgment",
    "organization_account",
    "official_press_summary",
    "unauthenticated_judgment_copy",
    "response_not_established",
)

EVIDENCE_BASIS_PUBLIC = {
    "not_yet_established": "The basis of this record has not yet been established.",
    "author_document": (
        "This records what the named author wrote in that author's document. "
        "It is not itself a court finding."
    ),
    "authenticated_judgment": "This finding is supported by an authenticated judgment.",
    "organization_account": (
        "An identified organization reported this event. "
        "That is not a finding read from the judgment."
    ),
    "official_press_summary": (
        "An official press summary supports this event. "
        "The summary states that it is not the judgment."
    ),
    "unauthenticated_judgment_copy": (
        "This was read from a judgment copy whose authenticity against an official host "
        "has not been established. The host of the copy is not the author of the judgment."
    ),
    "response_not_established": (
        "A court response to this argument has not been established. "
        "That is not a finding that the court ignored the argument."
    ),
}

PUBLIC_ARGUMENT_ROLES = ("trialwatch_argument", "partner_argument")

NOT_STATED = "not stated"

LINK_RELATIONSHIPS = ("supports", "quotes", "duplicates", "conflicts")
LINK_TARGETS = ("argument", "outcome_event", "reception")

UNKNOWN_OUTCOME_STATEMENT = (
    "No verified subsequent outcome is on record. Unknown is not a finding that "
    "the person is still detained, that the case is ongoing, or that advocacy failed."
)

DATED_OUTCOME_STATEMENT = (
    "Latest approved event in this dataset. "
    "Dated events on record are not a success or failure score, "
    "and they do not show that an argument caused the event. "
    "This is not a claim that the timeline is current."
)

RECEPTION_NOT_ESTABLISHED = (
    "No reviewed record of how an authority received this argument. "
    "That absence is not a finding that the court ignored the argument."
)
