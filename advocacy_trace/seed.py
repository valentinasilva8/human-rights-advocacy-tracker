"""Create the local demo database from the fictional fixture."""

from __future__ import annotations

import os
from pathlib import Path

from advocacy_trace.fixture import load_fixture
from advocacy_trace.store import EvidenceStore

ROOT = Path(__file__).resolve().parents[1]


def database_path() -> Path:
    configured = os.environ.get("ADVOCACY_TRACE_DB", "").strip()
    if configured:
        return Path(configured)
    return ROOT / "data" / "demo.sqlite"


def open_store(path: Path | None = None) -> EvidenceStore:
    db_path = path or database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not db_path.exists()
    store = EvidenceStore(db_path)
    if is_new:
        load_fixture(store)
    from advocacy_trace.approvals import apply_recorded_approvals
    from advocacy_trace.research import load_proposed_research

    load_proposed_research(store)
    apply_recorded_approvals(store)
    return store


def main() -> None:
    path = database_path()
    existed = path.exists()
    store = open_store(path)
    store.close()
    if existed:
        print(f"Migrated the existing database at {path}. Existing rows were kept.")
    else:
        print(f"Seeded demonstration database at {path}")


if __name__ == "__main__":
    main()
