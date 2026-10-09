"""SQLite store for cases, arguments, outcomes, reception, and review."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from advocacy_trace.constants import (
    ACCEPTANCE_STATUSES,
    ARGUMENT_LABELS,
    ATTRIBUTION_ROLES,
    DOCUMENT_TYPES,
    EVIDENCE_LABELS,
    EVENT_TYPES,
    INTERVENTION_TYPES,
    LINK_RELATIONSHIPS,
    LINK_TARGETS,
    NO_UPDATE_EVENT,
    RECEPTION_NEEDS_SOURCE,
    RECEPTION_STATUSES,
    REVIEW_STATUSES,
    TRIALWATCH_AUTHORS,
    UNKNOWN_OUTCOME_STATEMENT,
)
from advocacy_trace.dates import date_in_filter, normalize_date
from advocacy_trace.errors import ValidationError

SCHEMA = """
CREATE TABLE IF NOT EXISTS cases (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    country TEXT,
    court TEXT,
    case_number TEXT,
    charges TEXT,
    proceeding_type TEXT,
    procedural_stage TEXT,
    finality TEXT,
    sensitive INTEGER NOT NULL DEFAULT 0 CHECK (sensitive IN (0, 1)),
    is_synthetic INTEGER NOT NULL DEFAULT 0 CHECK (is_synthetic IN (0, 1)),
    opened_on TEXT,
    opened_on_precision TEXT NOT NULL DEFAULT 'unknown',
    last_verified_on TEXT,
    last_verified_on_precision TEXT NOT NULL DEFAULT 'unknown',
    unresolved_questions TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS participants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS case_participants (
    case_id TEXT NOT NULL REFERENCES cases(id),
    participant_id TEXT NOT NULL REFERENCES participants(id),
    role_in_case TEXT NOT NULL,
    PRIMARY KEY (case_id, participant_id, role_in_case)
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT,
    document_type TEXT NOT NULL,
    author_actor TEXT NOT NULL,
    publication_date TEXT,
    publication_date_precision TEXT NOT NULL DEFAULT 'unknown',
    retrieval_date TEXT,
    retrieval_date_precision TEXT NOT NULL DEFAULT 'unknown',
    fingerprint TEXT,
    extraction_version TEXT,
    rights_note TEXT NOT NULL DEFAULT '',
    duplicate_of_source_id TEXT REFERENCES sources(id),
    is_synthetic INTEGER NOT NULL DEFAULT 0 CHECK (is_synthetic IN (0, 1)),
    untrusted_text TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS interventions (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES cases(id),
    source_id TEXT REFERENCES sources(id),
    actor TEXT NOT NULL,
    intervention_type TEXT NOT NULL,
    intervention_date TEXT,
    intervention_date_precision TEXT NOT NULL DEFAULT 'unknown',
    description TEXT NOT NULL DEFAULT '',
    attribution_basis TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS arguments (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES cases(id),
    intervention_id TEXT REFERENCES interventions(id),
    source_id TEXT REFERENCES sources(id),
    author_actor TEXT NOT NULL,
    attribution_role TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    reasons TEXT NOT NULL DEFAULT '',
    passage TEXT NOT NULL DEFAULT '',
    location_ref TEXT NOT NULL DEFAULT '',
    legal_authorities TEXT NOT NULL DEFAULT '',
    argument_date TEXT,
    argument_date_precision TEXT NOT NULL DEFAULT 'unknown',
    review_status TEXT NOT NULL DEFAULT 'proposed',
    is_synthetic INTEGER NOT NULL DEFAULT 0 CHECK (is_synthetic IN (0, 1))
);

CREATE TABLE IF NOT EXISTS argument_labels (
    argument_id TEXT NOT NULL REFERENCES arguments(id),
    label TEXT NOT NULL,
    PRIMARY KEY (argument_id, label)
);

CREATE TABLE IF NOT EXISTS outcome_events (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES cases(id),
    participant_id TEXT NOT NULL REFERENCES participants(id),
    event_type TEXT NOT NULL,
    event_date TEXT,
    event_date_precision TEXT NOT NULL DEFAULT 'unknown',
    description TEXT NOT NULL,
    procedural_stage TEXT,
    finality TEXT,
    evidence_label TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'proposed',
    supersedes_event_id TEXT REFERENCES outcome_events(id),
    is_synthetic INTEGER NOT NULL DEFAULT 0 CHECK (is_synthetic IN (0, 1))
);

CREATE TABLE IF NOT EXISTS reception_observations (
    id TEXT PRIMARY KEY,
    argument_id TEXT NOT NULL REFERENCES arguments(id),
    case_id TEXT NOT NULL REFERENCES cases(id),
    status TEXT NOT NULL,
    source_id TEXT REFERENCES sources(id),
    passage TEXT NOT NULL DEFAULT '',
    location_ref TEXT NOT NULL DEFAULT '',
    observer_note TEXT NOT NULL DEFAULT '',
    review_status TEXT NOT NULL DEFAULT 'proposed',
    is_recital INTEGER NOT NULL DEFAULT 0 CHECK (is_recital IN (0, 1)),
    is_synthetic INTEGER NOT NULL DEFAULT 0 CHECK (is_synthetic IN (0, 1))
);

CREATE TABLE IF NOT EXISTS evidence_links (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(id),
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relationship TEXT NOT NULL,
    independent INTEGER NOT NULL DEFAULT 1 CHECK (independent IN (0, 1))
);

CREATE TABLE IF NOT EXISTS review_actions (
    id TEXT PRIMARY KEY,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    action TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    prior_status TEXT,
    new_status TEXT
);
"""

BOOL_FIELDS = ("sensitive", "is_synthetic", "is_recital", "independent")
_IGNORED_PAYLOAD_KEYS = frozenset(
    {
        "review_status",
        "system",
        "instruction",
        "instructions",
        "approve_all",
        "sql",
        "role",
    }
)


def fields_for_outcome_from_source(source: dict) -> dict:
    """Date fields for an outcome mentioned in a source.

    The publication date is returned beside the event date so callers can see
    both. It is never copied into the event date.
    """

    return {
        "event_date": None,
        "event_date_precision": "unknown",
        "source_publication_date": source.get("publication_date"),
    }


class EvidenceStore:
    """Linked evidence records. Review is append-only and approval is gated."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def add_participant(
        self,
        *,
        name: str,
        description: str = "",
        id: str | None = None,
    ) -> str:
        participant_id = id or _new_id("person")
        self._require_text(name, "Participant name")
        self.conn.execute(
            "INSERT INTO participants (id, name, description) VALUES (?, ?, ?)",
            (participant_id, name.strip(), description.strip()),
        )
        self.conn.commit()
        return participant_id

    def add_case(
        self,
        *,
        title: str,
        country: str | None = None,
        court: str | None = None,
        case_number: str | None = None,
        charges: str | None = None,
        proceeding_type: str | None = None,
        procedural_stage: str | None = None,
        finality: str | None = None,
        sensitive: bool = False,
        is_synthetic: bool = False,
        opened_on: str | None = None,
        opened_on_precision: str = "unknown",
        last_verified_on: str | None = None,
        last_verified_on_precision: str = "unknown",
        unresolved_questions: str = "",
        id: str | None = None,
    ) -> str:
        case_id = id or _new_id("case")
        self._require_text(title, "Case title")
        opened = normalize_date(opened_on, opened_on_precision)
        verified = normalize_date(last_verified_on, last_verified_on_precision)
        self.conn.execute(
            """
            INSERT INTO cases (
                id, title, country, court, case_number, charges, proceeding_type,
                procedural_stage, finality, sensitive, is_synthetic, opened_on,
                opened_on_precision, last_verified_on, last_verified_on_precision,
                unresolved_questions, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                title.strip(),
                _blank(country),
                _blank(court),
                _blank(case_number),
                _blank(charges),
                _blank(proceeding_type),
                _blank(procedural_stage),
                _blank(finality),
                int(bool(sensitive)),
                int(bool(is_synthetic)),
                opened,
                opened_on_precision,
                verified,
                last_verified_on_precision,
                unresolved_questions.strip(),
                _now(),
            ),
        )
        self.conn.commit()
        return case_id

    def link_participant(self, case_id: str, participant_id: str, role_in_case: str) -> None:
        self._get_case(case_id)
        self._must("participants", participant_id, "Participant")
        self._require_text(role_in_case, "Role in case")
        self.conn.execute(
            """
            INSERT OR IGNORE INTO case_participants (case_id, participant_id, role_in_case)
            VALUES (?, ?, ?)
            """,
            (case_id, participant_id, role_in_case.strip()),
        )
        self.conn.commit()

    def add_source(
        self,
        *,
        title: str,
        document_type: str,
        author_actor: str,
        url: str | None = None,
        publication_date: str | None = None,
        publication_date_precision: str = "unknown",
        retrieval_date: str | None = None,
        retrieval_date_precision: str = "unknown",
        fingerprint: str | None = None,
        extraction_version: str | None = None,
        rights_note: str = "",
        duplicate_of_source_id: str | None = None,
        is_synthetic: bool = False,
        id: str | None = None,
    ) -> str:
        source_id = id or _new_id("source")
        self._require_text(title, "Source title")
        self._require_text(author_actor, "Source author")
        self._one_of(document_type, DOCUMENT_TYPES, "Document type")
        if duplicate_of_source_id:
            self._must("sources", duplicate_of_source_id, "Original source")
        published = normalize_date(publication_date, publication_date_precision)
        retrieved = normalize_date(retrieval_date, retrieval_date_precision)
        self.conn.execute(
            """
            INSERT INTO sources (
                id, title, url, document_type, author_actor, publication_date,
                publication_date_precision, retrieval_date, retrieval_date_precision,
                fingerprint, extraction_version, rights_note, duplicate_of_source_id,
                is_synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                title.strip(),
                _blank(url),
                document_type,
                author_actor.strip(),
                published,
                publication_date_precision,
                retrieved,
                retrieval_date_precision,
                _blank(fingerprint),
                _blank(extraction_version),
                rights_note.strip(),
                duplicate_of_source_id,
                int(bool(is_synthetic)),
            ),
        )
        self.conn.commit()
        return source_id

    def add_intervention(
        self,
        *,
        case_id: str,
        actor: str,
        intervention_type: str,
        attribution_basis: str,
        source_id: str | None = None,
        intervention_date: str | None = None,
        intervention_date_precision: str = "unknown",
        description: str = "",
        id: str | None = None,
    ) -> str:
        intervention_id = id or _new_id("intervention")
        self._get_case(case_id)
        self._require_text(actor, "Intervention actor")
        self._require_text(attribution_basis, "Attribution basis")
        self._one_of(intervention_type, INTERVENTION_TYPES, "Intervention type")
        if source_id:
            self._must("sources", source_id, "Source")
        when = normalize_date(intervention_date, intervention_date_precision)
        self.conn.execute(
            """
            INSERT INTO interventions (
                id, case_id, source_id, actor, intervention_type, intervention_date,
                intervention_date_precision, description, attribution_basis
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                intervention_id,
                case_id,
                source_id,
                actor.strip(),
                intervention_type,
                when,
                intervention_date_precision,
                description.strip(),
                attribution_basis.strip(),
            ),
        )
        self.conn.commit()
        return intervention_id

    def add_argument(
        self,
        *,
        case_id: str,
        author_actor: str,
        attribution_role: str,
        summary: str = "",
        reasons: str = "",
        passage: str = "",
        location_ref: str = "",
        legal_authorities: str = "",
        labels: list[str] | None = None,
        intervention_id: str | None = None,
        source_id: str | None = None,
        argument_date: str | None = None,
        argument_date_precision: str = "unknown",
        is_synthetic: bool = False,
        id: str | None = None,
    ) -> str:
        argument_id = id or _new_id("argument")
        case = self._get_case(case_id)
        self._check_attribution(author_actor, attribution_role)
        if intervention_id:
            self._must("interventions", intervention_id, "Intervention")
        if source_id:
            self._must("sources", source_id, "Source")
        when = normalize_date(argument_date, argument_date_precision)
        chosen = self._clean_labels(labels or [])
        synthetic = bool(is_synthetic or case["is_synthetic"])
        self.conn.execute(
            """
            INSERT INTO arguments (
                id, case_id, intervention_id, source_id, author_actor, attribution_role,
                summary, reasons, passage, location_ref, legal_authorities, argument_date,
                argument_date_precision, review_status, is_synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'proposed', ?)
            """,
            (
                argument_id,
                case_id,
                intervention_id,
                source_id,
                author_actor.strip(),
                attribution_role,
                summary.strip(),
                reasons.strip(),
                passage.strip(),
                location_ref.strip(),
                legal_authorities.strip(),
                when,
                argument_date_precision,
                int(synthetic),
            ),
        )
        for label in chosen:
            self.conn.execute(
                "INSERT INTO argument_labels (argument_id, label) VALUES (?, ?)",
                (argument_id, label),
            )
        self.conn.commit()
        return argument_id

    def add_outcome_event(
        self,
        *,
        case_id: str,
        participant_id: str,
        event_type: str,
        description: str,
        evidence_label: str,
        event_date: str | None = None,
        event_date_precision: str = "unknown",
        procedural_stage: str | None = None,
        finality: str | None = None,
        supersedes_event_id: str | None = None,
        is_synthetic: bool = False,
        date_is_publication_date: bool = False,
        id: str | None = None,
    ) -> str:
        if date_is_publication_date:
            raise ValidationError(
                "Publication date cannot be stored as the event date. "
                "Record the event date separately, or leave it unknown."
            )
        event_id = id or _new_id("outcome")
        case = self._get_case(case_id)
        self._must("participants", participant_id, "Defendant")
        self._require_text(description, "Outcome description")
        self._one_of(event_type, EVENT_TYPES, "Event type")
        self._one_of(evidence_label, EVIDENCE_LABELS, "Evidence label")
        if supersedes_event_id:
            earlier = self._must("outcome_events", supersedes_event_id, "Earlier outcome")
            if earlier["case_id"] != case_id:
                raise ValidationError(
                    "An appeal or later event must stay on the same proceeding as the earlier decision."
                )
        when = normalize_date(event_date, event_date_precision)
        synthetic = bool(is_synthetic or case["is_synthetic"])
        self.conn.execute(
            """
            INSERT INTO outcome_events (
                id, case_id, participant_id, event_type, event_date, event_date_precision,
                description, procedural_stage, finality, evidence_label, review_status,
                supersedes_event_id, is_synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'proposed', ?, ?)
            """,
            (
                event_id,
                case_id,
                participant_id,
                event_type,
                when,
                event_date_precision,
                description.strip(),
                _blank(procedural_stage),
                _blank(finality),
                evidence_label,
                supersedes_event_id,
                int(synthetic),
            ),
        )
        self.conn.commit()
        return event_id

    def add_reception(
        self,
        *,
        argument_id: str,
        case_id: str,
        status: str,
        source_id: str | None = None,
        passage: str = "",
        location_ref: str = "",
        observer_note: str = "",
        is_recital: bool = False,
        is_synthetic: bool = False,
        id: str | None = None,
    ) -> str:
        reception_id = id or _new_id("reception")
        argument = self._must("arguments", argument_id, "Argument")
        if argument["case_id"] != case_id:
            raise ValidationError("Reception must stay on the same case as the argument.")
        case = self._get_case(case_id)
        self._one_of(status, RECEPTION_STATUSES, "Reception status")
        if is_recital and status in ACCEPTANCE_STATUSES:
            raise ValidationError(
                "A court's recital of an argument is not acceptance. "
                "Store it as discussed, not addressed, or decision unavailable."
            )
        if status in RECEPTION_NEEDS_SOURCE and not source_id:
            raise ValidationError(
                f"Reception status '{status}' needs a source. "
                "Use 'Decision unavailable / insufficient evidence' when the decision is missing."
            )
        if source_id:
            self._must("sources", source_id, "Source")
        synthetic = bool(is_synthetic or case["is_synthetic"])
        self.conn.execute(
            """
            INSERT INTO reception_observations (
                id, argument_id, case_id, status, source_id, passage, location_ref,
                observer_note, review_status, is_recital, is_synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'proposed', ?, ?)
            """,
            (
                reception_id,
                argument_id,
                case_id,
                status,
                source_id,
                passage.strip(),
                location_ref.strip(),
                observer_note.strip(),
                int(bool(is_recital)),
                int(synthetic),
            ),
        )
        self.conn.commit()
        return reception_id

    def add_evidence_link(
        self,
        *,
        source_id: str,
        target_type: str,
        target_id: str,
        relationship: str,
        independent: bool | None = None,
        id: str | None = None,
    ) -> str:
        link_id = id or _new_id("link")
        self._must("sources", source_id, "Source")
        self._one_of(target_type, LINK_TARGETS, "Evidence target type")
        self._one_of(relationship, LINK_RELATIONSHIPS, "Evidence relationship")
        self._target_exists(target_type, target_id)
        if relationship == "duplicates":
            independent = False
        if independent is None:
            independent = True
        self.conn.execute(
            """
            INSERT INTO evidence_links (
                id, source_id, target_type, target_id, relationship, independent
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (link_id, source_id, target_type, target_id, relationship, int(bool(independent))),
        )
        self.conn.commit()
        return link_id

    def review(
        self,
        target_type: str,
        target_id: str,
        action: str,
        reviewer: str,
        note: str = "",
        edits: dict | None = None,
    ) -> str:
        """Record a human review. Source text cannot call this."""

        if action not in {"approve", "reject", "edit"}:
            raise ValidationError("Review action must be approve, reject, or edit.")
        self._require_text(reviewer, "Reviewer")
        if target_type not in {"argument", "outcome_event", "reception"}:
            raise ValidationError("Review target must be an argument, outcome event, or reception.")
        table = _table_for(target_type)
        current = self._must(table, target_id, target_type.replace("_", " ").title())
        prior = current["review_status"]
        if edits:
            self._apply_edits(target_type, target_id, edits)
            current = self._must(table, target_id, target_type)
        if action == "approve":
            self._assert_approvable(target_type, target_id)
            new_status = "approved"
        elif action == "reject":
            new_status = "rejected"
        else:
            new_status = prior
        self._one_of(new_status, REVIEW_STATUSES, "Review status")
        self.conn.execute(
            f"UPDATE {table} SET review_status = ? WHERE id = ?",
            (new_status, target_id),
        )
        action_id = _new_id("review")
        self.conn.execute(
            """
            INSERT INTO review_actions (
                id, target_type, target_id, action, reviewer, note, created_at,
                prior_status, new_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                action_id,
                target_type,
                target_id,
                action,
                reviewer.strip(),
                note.strip(),
                _now(),
                prior,
                new_status,
            ),
        )
        self.conn.commit()
        return action_id

    def ingest_untrusted_text(self, source_id: str, text: str) -> None:
        """Store retrieved text as data. It does not change any review status."""

        self._must("sources", source_id, "Source")
        self.conn.execute(
            "UPDATE sources SET untrusted_text = ? WHERE id = ?",
            (text, source_id),
        )
        self.conn.commit()

    def propose_from_untrusted_payload(self, case_id: str, payload: dict) -> str:
        """Create a proposed argument from a model or page payload.

        Instruction-like keys are ignored. Review status is always proposed,
        including when the payload asks to approve itself.
        """

        if not isinstance(payload, dict):
            raise ValidationError("An extraction payload must be a record of fields, not instructions.")
        cleaned = {
            key: value
            for key, value in payload.items()
            if key not in _IGNORED_PAYLOAD_KEYS and not str(key).startswith("_")
        }
        role = str(cleaned.get("attribution_role") or "ai_suggested")
        if role not in ATTRIBUTION_ROLES or role == "trialwatch_argument":
            role = "ai_suggested"
        labels = cleaned.get("labels") or ["unmapped—review required"]
        if isinstance(labels, str):
            labels = [labels]
        return self.add_argument(
            case_id=case_id,
            author_actor=str(cleaned.get("author_actor") or "Unattributed extraction"),
            attribution_role=role,
            summary=str(cleaned.get("summary") or ""),
            reasons=str(cleaned.get("reasons") or ""),
            passage=str(cleaned.get("passage") or ""),
            location_ref=str(cleaned.get("location_ref") or ""),
            legal_authorities=str(cleaned.get("legal_authorities") or ""),
            labels=[str(label) for label in labels],
            source_id=cleaned.get("source_id"),
            intervention_id=cleaned.get("intervention_id"),
        )

    def get_case(self, case_id: str) -> dict:
        return self._get_case(case_id)

    def get_argument(self, argument_id: str) -> dict:
        row = self._must("arguments", argument_id, "Argument")
        row["labels"] = self.labels_for(argument_id)
        return row

    def get_outcome(self, event_id: str) -> dict:
        return self._must("outcome_events", event_id, "Outcome")

    def labels_for(self, argument_id: str) -> list[str]:
        rows = self.conn.execute(
            "SELECT label FROM argument_labels WHERE argument_id = ? ORDER BY label",
            (argument_id,),
        ).fetchall()
        return [row["label"] for row in rows]

    def list_cases(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM cases ORDER BY title").fetchall()
        return [_row(row) for row in rows]

    def list_arguments(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM arguments ORDER BY id").fetchall()
        result = []
        for row in rows:
            item = _row(row)
            item["labels"] = self.labels_for(item["id"])
            result.append(item)
        return result

    def arguments_for_case(self, case_id: str) -> list[dict]:
        return [item for item in self.list_arguments() if item["case_id"] == case_id]

    def interventions_for_case(self, case_id: str) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT * FROM interventions
            WHERE case_id = ?
            ORDER BY COALESCE(intervention_date, '9999'), id
            """,
            (case_id,),
        ).fetchall()
        return [_row(row) for row in rows]

    def participants_for_case(self, case_id: str) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT participants.*, case_participants.role_in_case
            FROM participants
            JOIN case_participants ON case_participants.participant_id = participants.id
            WHERE case_participants.case_id = ?
            ORDER BY participants.name
            """,
            (case_id,),
        ).fetchall()
        return [_row(row) for row in rows]

    def receptions_for_argument(self, argument_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM reception_observations WHERE argument_id = ? ORDER BY id",
            (argument_id,),
        ).fetchall()
        return [_row(row) for row in rows]

    def review_queue(self) -> dict:
        return {
            "arguments": [item for item in self.list_arguments() if item["review_status"] == "proposed"],
            "outcomes": [
                item for item in self._all("outcome_events") if item["review_status"] == "proposed"
            ],
            "receptions": [
                item
                for item in self._all("reception_observations")
                if item["review_status"] == "proposed"
            ],
        }

    def get_source(self, source_id: str) -> dict:
        return self._must("sources", source_id, "Source")

    def arguments_for_actor(self, actor: str) -> list[dict]:
        """Arguments made by an actor, not arguments a report merely describes."""

        if actor.strip().lower() in TRIALWATCH_AUTHORS:
            return [
                item
                for item in self.list_arguments()
                if item["attribution_role"] == "trialwatch_argument"
            ]
        return [
            item
            for item in self.list_arguments()
            if item["author_actor"] == actor and item["attribution_role"] == "partner_argument"
        ]

    def outcome_events(self, case_id: str, participant_id: str | None = None) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT * FROM outcome_events
            WHERE case_id = ?
            ORDER BY COALESCE(event_date, '9999'), id
            """,
            (case_id,),
        ).fetchall()
        events = [_row(row) for row in rows]
        if participant_id:
            events = [event for event in events if event["participant_id"] == participant_id]
        return events

    def cases_for_participant(self, participant_id: str) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT cases.* FROM cases
            JOIN case_participants ON case_participants.case_id = cases.id
            WHERE case_participants.participant_id = ?
            ORDER BY cases.title
            """,
            (participant_id,),
        ).fetchall()
        return [_row(row) for row in rows]

    def evidence_links_for(self, target_type: str, target_id: str) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT * FROM evidence_links
            WHERE target_type = ? AND target_id = ?
            ORDER BY id
            """,
            (target_type, target_id),
        ).fetchall()
        return [_row(row) for row in rows]

    def independent_support_count(self, event_id: str) -> int:
        """Count distinct original sources. Copies of one report count once."""

        origins: set[str] = set()
        for link in self.evidence_links_for("outcome_event", event_id):
            if link["relationship"] != "supports" or not link["independent"]:
                continue
            source = self._must("sources", link["source_id"], "Source")
            origins.add(source["duplicate_of_source_id"] or source["id"])
        return len(origins)

    def outcome_summary(self, case_id: str, participant_id: str | None = None) -> dict:
        events = [
            event
            for event in self.outcome_events(case_id, participant_id)
            if event["review_status"] == "approved"
            and event["event_type"] != NO_UPDATE_EVENT
            and event["evidence_label"] != "Unverified"
        ]
        if not events:
            return {
                "status": "unknown",
                "statement": UNKNOWN_OUTCOME_STATEMENT,
                "events": [],
            }
        return {
            "status": "dated_events",
            "statement": (
                "Dated events are on record. They are not a success or failure score, "
                "and they do not show that an argument caused the event."
            ),
            "events": events,
        }

    def search_arguments(
        self,
        *,
        label: str | None = None,
        country: str | None = None,
        intervention_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        review_status: str | None = "approved",
        attribution_role: str | None = "trialwatch_argument",
        include_synthetic: bool = True,
    ) -> dict:
        hidden_unknown_dates = 0
        matched = []
        interventions = {item["id"]: item for item in self._all("interventions")}
        cases = {item["id"]: item for item in self.list_cases()}
        for argument in self.list_arguments():
            case = cases[argument["case_id"]]
            if review_status and argument["review_status"] != review_status:
                continue
            if attribution_role and argument["attribution_role"] != attribution_role:
                continue
            if not include_synthetic and (argument["is_synthetic"] or case["is_synthetic"]):
                continue
            if label and label not in argument["labels"]:
                continue
            if country and case.get("country") != country:
                continue
            intervention = interventions.get(argument["intervention_id"])
            if intervention_type:
                if not intervention or intervention["intervention_type"] != intervention_type:
                    continue
            in_range = date_in_filter(
                argument["argument_date"],
                argument["argument_date_precision"],
                date_from,
                date_to,
            )
            if in_range is None:
                hidden_unknown_dates += 1
                continue
            if in_range is False:
                continue
            matched.append(argument)
        return {
            "arguments": matched,
            "argument_count": len(matched),
            "unique_cases": len({item["case_id"] for item in matched}),
            "hidden_unknown_dates": hidden_unknown_dates,
        }

    def summarize(self, label: str, *, include_synthetic: bool) -> dict:
        """Descriptive counts. Synthetic rows never enter the real-case figure."""

        found = self.search_arguments(
            label=label,
            review_status="approved",
            attribution_role="trialwatch_argument",
            include_synthetic=include_synthetic,
        )
        case_ids = sorted({item["case_id"] for item in found["arguments"]})
        unknown_cases = []
        verified_outcomes = []
        for case_id in case_ids:
            summary = self.outcome_summary(case_id)
            if summary["status"] == "unknown":
                unknown_cases.append(case_id)
            for event in summary["events"]:
                if include_synthetic or not event["is_synthetic"]:
                    verified_outcomes.append(event)
        synthetic_cases = [
            case["id"] for case in self.list_cases() if case["is_synthetic"]
        ]
        unverified = [
            event
            for event in self._all("outcome_events")
            if event["evidence_label"] == "Unverified" or event["review_status"] != "approved"
        ]
        return {
            "label": label,
            "unique_cases": len(case_ids),
            "argument_count": found["argument_count"],
            "unknown_outcome_cases": len(unknown_cases),
            "case_ids": case_ids,
            "outcomes": verified_outcomes,
            "excluded_synthetic_cases": 0 if include_synthetic else len(synthetic_cases),
            "excluded_unverified_outcomes": len(unverified) if not include_synthetic else 0,
            "causation": False,
            "note": (
                "Counts are descriptive. They are not a success rate. "
                "Multiple arguments in one case count once toward unique cases. "
                "Unknown outcomes stay in the denominator."
            ),
        }

    def verified_summary(self, label: str) -> dict:
        return self.summarize(label, include_synthetic=False)

    def public_export(self, *, include_synthetic: bool = False) -> dict:
        """Export records that are safe to share. Sensitive rows are always omitted."""

        all_cases = self.list_cases()
        sensitive = [case for case in all_cases if case["sensitive"]]
        cases = [
            case
            for case in all_cases
            if not case["sensitive"] and (include_synthetic or not case["is_synthetic"])
        ]
        case_ids = {case["id"] for case in cases}
        arguments = [
            item for item in self.list_arguments() if item["case_id"] in case_ids
        ]
        outcomes = [
            item for item in self._all("outcome_events") if item["case_id"] in case_ids
        ]
        payload = {
            "cases": cases,
            "arguments": arguments,
            "outcome_events": outcomes,
            "real_case_count": len([case for case in cases if not case["is_synthetic"]]),
            "omitted_sensitive_count": len(sensitive),
        }
        encoded = json.dumps(payload)
        for case in sensitive:
            if case["id"] in encoded or case["title"] in encoded:
                raise ValidationError(
                    "Public export included a sensitive case. Remove it from the export payload."
                )
        return payload

    def learning_brief(self, *, include_synthetic: bool) -> str:
        summary = self.summarize("Proportionality", include_synthetic=include_synthetic)
        real = self.verified_summary("Proportionality")
        lines = [
            "Advocacy Trace learning brief",
            "",
            "This draft is for a person to edit. The application does not send or publish it.",
            "It does not claim that an argument caused an outcome.",
            "It does not rank arguments or report a success rate.",
            "",
            "Proportionality arguments in this view",
            f"Unique cases: {summary['unique_cases']}",
            f"Arguments in those cases: {summary['argument_count']}",
            f"Cases with no verified subsequent outcome: {summary['unknown_outcome_cases']}",
            f"Verified real cases: {real['unique_cases']}",
            f"Synthetic cases excluded from the real-case count: {real['excluded_synthetic_cases']}",
            "",
            "Documented sequences, where the demo or reviewed rows have them, are chronological only.",
            "A reception status of discussed, not addressed, or decision unavailable is a result, not a hole to be filled with an acquittal.",
            "",
            "Follow-up questions",
            "- Which real fairness reports contain a proportionality passage with a page cite?",
            "- Which of those proceedings have a later judgment or other external source?",
            "- Where is reception still unknown?",
            "",
            summary["note"],
        ]
        return "\n".join(lines)

    def _assert_approvable(self, target_type: str, target_id: str) -> None:
        if target_type == "argument":
            argument = self.get_argument(target_id)
            if not argument["passage"]:
                raise ValidationError(
                    "An approved argument needs a traceable supporting passage."
                )
            if not argument["location_ref"]:
                raise ValidationError(
                    "An approved argument needs a page, paragraph, or other location."
                )
            if not argument["source_id"]:
                raise ValidationError("An approved argument needs a source document.")
            if not argument["summary"] or not argument["reasons"]:
                raise ValidationError(
                    "An approved argument needs a summary and the reasons given in the source."
                )
            if not argument["labels"]:
                raise ValidationError("An approved argument needs at least one label.")
            self._check_attribution(argument["author_actor"], argument["attribution_role"])
            return
        if target_type == "outcome_event":
            event = self.get_outcome(target_id)
            if event["evidence_label"] == "Unverified":
                raise ValidationError(
                    "An unverified outcome cannot be approved. Leave the outcome unknown "
                    "or attach adequate evidence and change the evidence label."
                )
            supports = [
                link
                for link in self.evidence_links_for("outcome_event", target_id)
                if link["relationship"] == "supports"
            ]
            if not supports:
                raise ValidationError(
                    "An approved outcome needs source evidence. "
                    "Add a supporting evidence link before approval."
                )
            return
        reception = self._must("reception_observations", target_id, "Reception")
        if reception["is_recital"] and reception["status"] in ACCEPTANCE_STATUSES:
            raise ValidationError("A recital cannot be approved as acceptance.")
        if reception["status"] in RECEPTION_NEEDS_SOURCE:
            if not reception["source_id"] or not reception["passage"]:
                raise ValidationError(
                    "An approved reception finding needs a source passage."
                )

    def _apply_edits(self, target_type: str, target_id: str, edits: dict) -> None:
        allowed = {
            "argument": {
                "summary",
                "reasons",
                "passage",
                "location_ref",
                "legal_authorities",
                "author_actor",
                "attribution_role",
            },
            "outcome_event": {"description", "event_type", "evidence_label", "procedural_stage", "finality"},
            "reception": {"status", "passage", "location_ref", "observer_note"},
        }[target_type]
        unknown = set(edits) - allowed - {"labels"}
        if unknown:
            raise ValidationError(
                "Those fields cannot be edited here: " + ", ".join(sorted(unknown))
            )
        if target_type == "argument":
            current = self.get_argument(target_id)
            author = edits.get("author_actor", current["author_actor"])
            role = edits.get("attribution_role", current["attribution_role"])
            self._check_attribution(author, role)
            if "labels" in edits:
                labels = self._clean_labels(list(edits["labels"]))
                self.conn.execute(
                    "DELETE FROM argument_labels WHERE argument_id = ?",
                    (target_id,),
                )
                for label in labels:
                    self.conn.execute(
                        "INSERT INTO argument_labels (argument_id, label) VALUES (?, ?)",
                        (target_id, label),
                    )
        assignments = []
        values: list[object] = []
        for key, value in edits.items():
            if key not in allowed:
                continue
            if key == "event_type":
                self._one_of(value, EVENT_TYPES, "Event type")
            if key == "evidence_label":
                self._one_of(value, EVIDENCE_LABELS, "Evidence label")
            if key == "attribution_role":
                self._one_of(value, ATTRIBUTION_ROLES, "Attribution role")
            if key == "status":
                self._one_of(value, RECEPTION_STATUSES, "Reception status")
            assignments.append(f"{key} = ?")
            values.append(value.strip() if isinstance(value, str) else value)
        if assignments:
            values.append(target_id)
            self.conn.execute(
                f"UPDATE {_table_for(target_type)} SET {', '.join(assignments)} WHERE id = ?",
                values,
            )

    def _check_attribution(self, author_actor: str, attribution_role: str) -> None:
        self._require_text(author_actor, "Argument author")
        self._one_of(attribution_role, ATTRIBUTION_ROLES, "Attribution role")
        author_key = author_actor.strip().lower()
        if attribution_role == "defense_counsel_described" and author_key in TRIALWATCH_AUTHORS:
            raise ValidationError(
                "A defense argument described in a report cannot be attributed to TrialWatch. "
                "Name counsel as the author and keep the role defense_counsel_described."
            )
        if attribution_role == "authority_finding" and author_key in TRIALWATCH_AUTHORS:
            raise ValidationError(
                "An authority's finding cannot be stored as TrialWatch's argument."
            )
        if attribution_role == "trialwatch_argument" and author_key not in TRIALWATCH_AUTHORS:
            raise ValidationError(
                "A TrialWatch argument must name TrialWatch as the author. "
                "Use partner_argument, defense_counsel_described, or another role instead."
            )

    def _clean_labels(self, labels: list[str]) -> list[str]:
        chosen: list[str] = []
        for label in labels:
            self._one_of(label, ARGUMENT_LABELS, "Argument label")
            if label not in chosen:
                chosen.append(label)
        return chosen

    def _get_case(self, case_id: str) -> dict:
        return self._must("cases", case_id, "Case")

    def _must(self, table: str, row_id: str, label: str) -> dict:
        if table not in {
            "cases",
            "participants",
            "sources",
            "interventions",
            "arguments",
            "outcome_events",
            "reception_observations",
        }:
            raise ValidationError(f"Unknown record type {table}.")
        row = self.conn.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,)).fetchone()
        if row is None:
            raise ValidationError(f"{label} '{row_id}' was not found.")
        return _row(row)

    def _all(self, table: str) -> list[dict]:
        rows = self.conn.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
        return [_row(row) for row in rows]

    def _target_exists(self, target_type: str, target_id: str) -> None:
        self._must(_table_for(target_type), target_id, target_type.replace("_", " ").title())

    @staticmethod
    def _require_text(value: str, label: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{label} is required.")

    @staticmethod
    def _one_of(value: str, allowed: tuple[str, ...], label: str) -> None:
        if value not in allowed:
            raise ValidationError(
                f"{label} must be one of: {', '.join(allowed)}. Got {value!r}."
            )


def _table_for(target_type: str) -> str:
    return {
        "argument": "arguments",
        "outcome_event": "outcome_events",
        "reception": "reception_observations",
    }[target_type]


def _row(row: sqlite3.Row | None) -> dict:
    if row is None:
        raise ValidationError("Expected a database row.")
    data = dict(row)
    for key in BOOL_FIELDS:
        if key in data and data[key] is not None:
            data[key] = bool(data[key])
    return data


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _blank(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None
