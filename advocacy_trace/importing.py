"""Manual import boundaries. No network calls are made from this module."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

from advocacy_trace.errors import (
    DownloadFailedError,
    MissingCredentialError,
    UnreadablePdfError,
)

Fetcher = Callable[[str], bytes]


def require_search_provider(env: dict[str, str] | None = None) -> str:
    """Return the configured search provider name, or explain how to proceed without one."""

    values = env if env is not None else dict(os.environ)
    provider = str(values.get("SEARCH_PROVIDER", "")).strip()
    key = str(values.get("SEARCH_API_KEY", "")).strip()
    if not provider or not key:
        raise MissingCredentialError(
            "No search provider is configured. Import a source file manually. "
            "SEARCH_PROVIDER and SEARCH_API_KEY are optional and are not required for the demo."
        )
    return provider


def manual_import_url(url: str, fetcher: Fetcher) -> bytes:
    """Import one HTTPS document with a caller-supplied fetcher.

    This function does not crawl, follow links, or retry. The caller decides
    whether a fetch is permitted. Failures stay as download errors.
    """

    if not isinstance(url, str) or not url.startswith("https://"):
        raise DownloadFailedError(
            f"Download failed: the URL must start with https://. Got {url!r}."
        )
    try:
        data = fetcher(url)
    except Exception as exc:
        raise DownloadFailedError(f"Download failed for {url}: {exc}") from exc
    if not isinstance(data, (bytes, bytearray)) or len(data) == 0:
        raise DownloadFailedError(f"Download failed for {url}: the response was empty.")
    return bytes(data)


def read_pdf_excerpt(path: str | Path) -> None:
    """Reject a file that is not a minimally intact PDF.

    This prototype does not extract text from PDFs. A recognized PDF still
    needs a person to paste a short reviewed excerpt. Corrupt files raise
    UnreadablePdfError.
    """

    file_path = Path(path)
    if not file_path.is_file():
        raise UnreadablePdfError(f"Unreadable PDF: no file at {file_path}.")
    try:
        data = file_path.read_bytes()
    except OSError as exc:
        raise UnreadablePdfError(f"Unreadable PDF: could not read {file_path.name}: {exc}") from exc
    if not data.startswith(b"%PDF"):
        raise UnreadablePdfError(
            f"Unreadable PDF: {file_path.name} does not start with a PDF header. "
            "Paste a short reviewed excerpt instead."
        )
    tail = data[-4096:]
    if b"%%EOF" not in data and b"%%EOF" not in tail:
        raise UnreadablePdfError(
            f"Unreadable PDF: {file_path.name} is truncated or has no EOF marker."
        )
