"""Add columns in place. Do not delete an existing database."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "synthetic_chain.json"

_COLUMN_ADDITIONS = {
    "arguments": {
        "institutional_affiliation": "TEXT NOT NULL DEFAULT ''",
        "disclaimer_status": "TEXT NOT NULL DEFAULT 'not_yet_checked'",
        "disclaimer_text": "TEXT NOT NULL DEFAULT ''",
        "principle": "TEXT NOT NULL DEFAULT ''",
        "application": "TEXT NOT NULL DEFAULT ''",
        "remedy_requested": "TEXT NOT NULL DEFAULT ''",
        "claim_supported": "INTEGER NOT NULL DEFAULT 0",
    },
    "reception_observations": {
        "account_type": "TEXT NOT NULL DEFAULT 'not_yet_established'",
        "reasoning_checked": "INTEGER NOT NULL DEFAULT 0",
    },
    "evidence_links": {
        "provenance": "TEXT NOT NULL DEFAULT 'unknown'",
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
