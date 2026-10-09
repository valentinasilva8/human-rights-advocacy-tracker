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
    "Release",
    "Continued detention",
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
    }
)

LINK_RELATIONSHIPS = ("supports", "quotes", "duplicates", "conflicts")
LINK_TARGETS = ("argument", "outcome_event", "reception")

UNKNOWN_OUTCOME_STATEMENT = (
    "No verified subsequent outcome is on record. Unknown is not a finding that "
    "the person is still detained, that the case is ongoing, or that advocacy failed."
)
