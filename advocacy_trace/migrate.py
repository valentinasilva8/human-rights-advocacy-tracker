"""Add columns in place. Do not delete an existing database."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "synthetic_chain.json"
RESEARCH_PATH = Path(__file__).resolve().parent / "fixtures" / "proposed_research.json"

_COLUMN_ADDITIONS = {
    "arguments": {
        "institutional_affiliation": "TEXT NOT NULL DEFAULT ''",
        "disclaimer_status": "TEXT NOT NULL DEFAULT 'not_yet_checked'",
        "disclaimer_text": "TEXT NOT NULL DEFAULT ''",
        "principle": "TEXT NOT NULL DEFAULT ''",
        "application": "TEXT NOT NULL DEFAULT ''",
        "remedy_requested": "TEXT NOT NULL DEFAULT ''",
        "public_limitation": "TEXT NOT NULL DEFAULT ''",
        "evidence_basis": "TEXT NOT NULL DEFAULT 'not_yet_established'",
        "claim_supported": "INTEGER NOT NULL DEFAULT 0",
    },
    "outcome_events": {
        "public_limitation": "TEXT NOT NULL DEFAULT ''",
        "evidence_basis": "TEXT NOT NULL DEFAULT 'not_yet_established'",
        "decision_id": "TEXT",
    },
    "reception_observations": {
        "account_type": "TEXT NOT NULL DEFAULT 'not_yet_established'",
        "public_limitation": "TEXT NOT NULL DEFAULT ''",
        "evidence_basis": "TEXT NOT NULL DEFAULT 'not_yet_established'",
        "reasoning_checked": "INTEGER NOT NULL DEFAULT 0",
    },
    "evidence_links": {
        "provenance": "TEXT NOT NULL DEFAULT 'unknown'",
    },
    "cases": {
        "proceeding_note": "TEXT NOT NULL DEFAULT ''",
    },
    "review_actions": {
        "claim_text": "TEXT NOT NULL DEFAULT ''",
        "evidence_ref": "TEXT NOT NULL DEFAULT ''",
        "claim_supported": "INTEGER NOT NULL DEFAULT 0",
        "is_simulated": "INTEGER NOT NULL DEFAULT 0",
    },
}


def migrate(conn: sqlite3.Connection) -> None:
    existing_tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    added: set[tuple[str, str]] = set()
    for table, columns in _COLUMN_ADDITIONS.items():
        if table not in existing_tables:
            continue
        present = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        for name, declaration in columns.items():
            if name not in present:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {declaration}")
                added.add((table, name))
    if "research_attempts" not in existing_tables:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS research_attempts (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                searched_on TEXT,
                searched_on_precision TEXT NOT NULL DEFAULT 'day',
                query TEXT NOT NULL,
                place TEXT NOT NULL,
                result TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                is_synthetic INTEGER NOT NULL DEFAULT 0
            )
            """
        )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (id TEXT PRIMARY KEY, applied_at TEXT)"
    )
    _preserve_existing_records(
        conn,
        demote_legacy_real=("arguments", "claim_supported") in added,
    )
    _apply_review_readiness(conn)
    _apply_poland_preview(conn)
    _keep_article_quotations(conn)
    _record_appeal_account(conn)
    conn.commit()


def _migration_applied(conn: sqlite3.Connection, migration_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM schema_migrations WHERE id = ?",
        (migration_id,),
    ).fetchone()
    return row is not None


def _mark_migration(conn: sqlite3.Connection, migration_id: str) -> None:
    conn.execute(
        "INSERT INTO schema_migrations (id, applied_at) VALUES (?, ?)",
        (migration_id, datetime.now(timezone.utc).replace(microsecond=0).isoformat()),
    )


def _preserve_existing_records(conn: sqlite3.Connection, *, demote_legacy_real: bool) -> None:
    """Fill simulated demo rows from the fixture. Do not bless real approvals."""

    if "arguments" not in {
        row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }:
        return
    if demote_legacy_real and not _migration_applied(conn, "demote_legacy_real_approvals_v1"):
        conn.execute(
            """
            UPDATE arguments
            SET review_status = 'proposed', claim_supported = 0
            WHERE is_synthetic = 0 AND review_status = 'approved'
            """
        )
        _mark_migration(conn, "demote_legacy_real_approvals_v1")
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    arguments = {item["id"]: item for item in fixture["arguments"]}
    links = {item["id"]: item for item in fixture["evidence_links"]}
    for row in conn.execute("SELECT id, is_synthetic, review_status FROM arguments"):
        argument_id, synthetic, status = row
        if not synthetic:
            continue
        fixture_row = arguments.get(argument_id)
        if fixture_row is None:
            continue
        conn.execute(
            """
            UPDATE arguments
            SET institutional_affiliation = COALESCE(NULLIF(institutional_affiliation, ''), ?),
                disclaimer_status = CASE
                    WHEN disclaimer_status = 'not_yet_checked' THEN ?
                    ELSE disclaimer_status
                END,
                disclaimer_text = COALESCE(NULLIF(disclaimer_text, ''), ?),
                principle = COALESCE(NULLIF(principle, ''), ?),
                application = COALESCE(NULLIF(application, ''), ?),
                remedy_requested = COALESCE(NULLIF(remedy_requested, ''), ?)
            WHERE id = ? AND is_synthetic = 1
            """,
            (
                fixture_row.get("institutional_affiliation", ""),
                fixture_row.get("disclaimer_status", "not_stated_in_source"),
                fixture_row.get("disclaimer_text", ""),
                fixture_row.get("principle", ""),
                fixture_row.get("application", ""),
                fixture_row.get("remedy_requested", ""),
                argument_id,
            ),
        )
        approved = conn.execute(
            """
            SELECT 1 FROM review_actions
            WHERE target_type = 'argument' AND target_id = ? AND action = 'approve'
              AND reviewer = 'synthetic-reviewer'
            """,
            (argument_id,),
        ).fetchone()
        if approved and status == "approved":
            conn.execute(
                "UPDATE arguments SET claim_supported = 1 WHERE id = ?",
                (argument_id,),
            )
    conn.execute(
        """
        UPDATE review_actions
        SET is_simulated = 1
        WHERE reviewer = 'synthetic-reviewer'
        """
    )
    if "evidence_links" not in {
        row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }:
        return
    for row in conn.execute("SELECT id, relationship, provenance FROM evidence_links"):
        link_id, relationship, provenance = row
        fixture_link = links.get(link_id)
        if fixture_link and fixture_link.get("provenance"):
            conn.execute(
                "UPDATE evidence_links SET provenance = ? WHERE id = ?",
                (fixture_link["provenance"], link_id),
            )
            continue
        if provenance in (None, "", "unknown") and relationship == "duplicates":
            conn.execute(
                "UPDATE evidence_links SET provenance = 'duplicate_copy' WHERE id = ?",
                (link_id,),
            )


def _apply_review_readiness(conn: sqlite3.Connection) -> None:
    """Correct proposed research rows once. Do not approve them or touch synthetic rows.

    Fresh databases have no research rows yet. The migration is still marked applied
    so a later open does not overwrite a reviewer's edit. New ids are inserted by the
    research loader, which skips ids that already exist.
    """

    if _migration_applied(conn, "review_readiness_v1"):
        return
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if RESEARCH_PATH.exists():
        payload = json.loads(RESEARCH_PATH.read_text(encoding="utf-8"))
        _update_proposed_arguments(conn, tables, payload.get("arguments", []))
        _update_proposed_outcomes(conn, tables, payload.get("outcomes", []))
        _update_proposed_receptions(conn, tables, payload.get("receptions", []))
        _update_case_notes(conn, tables, payload.get("cases", []))
    _mark_migration(conn, "review_readiness_v1")


def _update_proposed_arguments(conn: sqlite3.Connection, tables: set[str], rows: list[dict]) -> None:
    if "arguments" not in tables:
        return
    for item in rows:
        current = conn.execute(
            "SELECT review_status, is_synthetic FROM arguments WHERE id = ?",
            (item["id"],),
        ).fetchone()
        if current is None or current[0] != "proposed" or current[1]:
            continue
        conn.execute(
            """
            UPDATE arguments
            SET summary = ?, reasons = ?, passage = ?, location_ref = ?,
                legal_authorities = ?, principle = ?, application = ?,
                remedy_requested = ?, public_limitation = ?, evidence_basis = ?
            WHERE id = ? AND review_status = 'proposed' AND is_synthetic = 0
            """,
            (
                item.get("summary", ""),
                item.get("reasons", ""),
                item.get("passage", ""),
                item.get("location_ref", ""),
                item.get("legal_authorities", ""),
                item.get("principle", ""),
                item.get("application", ""),
                item.get("remedy_requested", ""),
                item.get("public_limitation", ""),
                item.get("evidence_basis", "not_yet_established"),
                item["id"],
            ),
        )
        if "argument_labels" not in tables:
            continue
        conn.execute("DELETE FROM argument_labels WHERE argument_id = ?", (item["id"],))
        for label in item.get("labels") or []:
            conn.execute(
                "INSERT INTO argument_labels (argument_id, label) VALUES (?, ?)",
                (item["id"], label),
            )


def _update_proposed_outcomes(conn: sqlite3.Connection, tables: set[str], rows: list[dict]) -> None:
    if "outcome_events" not in tables:
        return
    for item in rows:
        current = conn.execute(
            "SELECT review_status, is_synthetic FROM outcome_events WHERE id = ?",
            (item["id"],),
        ).fetchone()
        if current is None or current[0] != "proposed" or current[1]:
            continue
        conn.execute(
            """
            UPDATE outcome_events
            SET event_type = ?, description = ?, evidence_label = ?,
                procedural_stage = ?, finality = ?, public_limitation = ?,
                evidence_basis = ?, decision_id = ?
            WHERE id = ? AND review_status = 'proposed' AND is_synthetic = 0
            """,
            (
                item["event_type"],
                item["description"],
                item["evidence_label"],
                item.get("procedural_stage"),
                item.get("finality"),
                item.get("public_limitation", ""),
                item.get("evidence_basis", "not_yet_established"),
                item.get("decision_id"),
                item["id"],
            ),
        )


def _update_proposed_receptions(conn: sqlite3.Connection, tables: set[str], rows: list[dict]) -> None:
    if "reception_observations" not in tables:
        return
    for item in rows:
        current = conn.execute(
            "SELECT review_status, is_synthetic FROM reception_observations WHERE id = ?",
            (item["id"],),
        ).fetchone()
        if current is None or current[0] != "proposed" or current[1]:
            continue
        conn.execute(
            """
            UPDATE reception_observations
            SET status = ?, source_id = ?, passage = ?, location_ref = ?,
                observer_note = ?, account_type = ?, public_limitation = ?,
                evidence_basis = ?, reasoning_checked = 0
            WHERE id = ? AND review_status = 'proposed' AND is_synthetic = 0
            """,
            (
                item["status"],
                item.get("source_id"),
                item.get("passage", ""),
                item.get("location_ref", ""),
                item.get("observer_note", ""),
                item.get("account_type", "not_yet_established"),
                item.get("public_limitation", ""),
                item.get("evidence_basis", "not_yet_established"),
                item["id"],
            ),
        )


def _apply_poland_preview(conn: sqlite3.Connection) -> None:
    """Record that II K 296/20 is the trial docket. Do not approve the arguments."""

    if _migration_applied(conn, "poland_trial_docket_v1"):
        return
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if RESEARCH_PATH.exists() and "cases" in tables:
        payload = json.loads(RESEARCH_PATH.read_text(encoding="utf-8"))
        cases = {item["id"]: item for item in payload.get("cases", [])}
        poland = cases.get("case_poland")
        if poland and "proceeding_note" in {
            row[1] for row in conn.execute("PRAGMA table_info(cases)")
        }:
            conn.execute(
                """
                UPDATE cases
                SET proceeding_note = ?
                WHERE id = 'case_poland' AND is_synthetic = 0
                """,
                (poland.get("proceeding_note", ""),),
            )
        if "arguments" in tables:
            wanted = {
                item["id"]: item
                for item in payload.get("arguments", [])
                if item["id"] in {"pl_arg_legality", "pl_arg_proportionality"}
            }
            for item_id, item in wanted.items():
                current = conn.execute(
                    "SELECT review_status, is_synthetic FROM arguments WHERE id = ?",
                    (item_id,),
                ).fetchone()
                if current is None or current[0] != "proposed" or current[1]:
                    continue
                conn.execute(
                    """
                    UPDATE arguments
                    SET public_limitation = ?, remedy_requested = ?, disclaimer_text = ?
                    WHERE id = ? AND review_status = 'proposed' AND is_synthetic = 0
                    """,
                    (
                        item.get("public_limitation", ""),
                        item.get("remedy_requested", ""),
                        item.get("disclaimer_text", ""),
                        item_id,
                    ),
                )
        if "sources" in tables:
            for item in payload.get("sources", []):
                if item["id"] != "pl_src_report":
                    continue
                conn.execute(
                    "UPDATE sources SET rights_note = ? WHERE id = 'pl_src_report'",
                    (item.get("rights_note", ""),),
                )
    _mark_migration(conn, "poland_trial_docket_v1")


def _keep_article_quotations(conn: sqlite3.Connection) -> None:
    """Keep HFHR and rp.pl quotations on the proposed appeal rows. Do not approve them."""

    if _migration_applied(conn, "article_quotations_v1"):
        return
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if RESEARCH_PATH.exists() and "outcome_events" in tables:
        payload = json.loads(RESEARCH_PATH.read_text(encoding="utf-8"))
        wanted = {
            "out_pl_appeal_podlesna",
            "out_pl_appeal_prus",
            "out_pl_appeal_gzyra",
        }
        for item in payload.get("outcomes", []):
            if item["id"] not in wanted:
                continue
            current = conn.execute(
                "SELECT review_status, is_synthetic FROM outcome_events WHERE id = ?",
                (item["id"],),
            ).fetchone()
            if current is None or current[0] != "proposed" or current[1]:
                continue
            conn.execute(
                """
                UPDATE outcome_events
                SET description = ?
                WHERE id = ? AND review_status = 'proposed' AND is_synthetic = 0
                """,
                (item["description"], item["id"]),
            )
    _mark_migration(conn, "article_quotations_v1")


def _record_appeal_account(conn: sqlite3.Connection) -> None:
    """Narrow the proposed appeal claim and record the reviewed organization account.

    This does not approve the rows. Approval stays in the recorded-approval file.
    An already approved row is left as stored.
    """

    if _migration_applied(conn, "appeal_account_approval_v1"):
        return
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if RESEARCH_PATH.exists() and "outcome_events" in tables:
        payload = json.loads(RESEARCH_PATH.read_text(encoding="utf-8"))
        wanted = {
            "out_pl_appeal_podlesna",
            "out_pl_appeal_prus",
            "out_pl_appeal_gzyra",
        }
        for item in payload.get("outcomes", []):
            if item["id"] not in wanted:
                continue
            current = conn.execute(
                "SELECT review_status, is_synthetic FROM outcome_events WHERE id = ?",
                (item["id"],),
            ).fetchone()
            if current is None or current[0] != "proposed" or current[1]:
                continue
            conn.execute(
                """
                UPDATE outcome_events
                SET description = ?, evidence_label = ?, public_limitation = ?,
                    evidence_basis = ?, finality = ?, decision_id = ?
                WHERE id = ? AND review_status = 'proposed' AND is_synthetic = 0
                """,
                (
                    item["description"],
                    item["evidence_label"],
                    item.get("public_limitation", ""),
                    item.get("evidence_basis", "organization_account"),
                    item.get("finality"),
                    item.get("decision_id"),
                    item["id"],
                ),
            )
        if "cases" in tables and "proceeding_note" in {
            row[1] for row in conn.execute("PRAGMA table_info(cases)")
        }:
            for item in payload.get("cases", []):
                if item["id"] != "case_poland":
                    continue
                conn.execute(
                    "UPDATE cases SET proceeding_note = ? WHERE id = 'case_poland' AND is_synthetic = 0",
                    (item.get("proceeding_note", ""),),
                )
        if "sources" in tables:
            for item in payload.get("sources", []):
                if item["id"] not in {"pl_src_hfhr", "pl_src_rp"}:
                    continue
                conn.execute(
                    "UPDATE sources SET rights_note = ? WHERE id = ?",
                    (item.get("rights_note", ""), item["id"]),
                )
    _mark_migration(conn, "appeal_account_approval_v1")


def _update_case_notes(conn: sqlite3.Connection, tables: set[str], rows: list[dict]) -> None:
    if "cases" not in tables:
        return
    for item in rows:
        conn.execute(
            """
            UPDATE cases
            SET unresolved_questions = ?
            WHERE id = ? AND is_synthetic = 0
            """,
            (item.get("unresolved_questions", ""), item["id"]),
        )
