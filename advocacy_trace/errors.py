"""Explicit failures for review rules and source import."""


class AdvocacyTraceError(Exception):
    """Base error. The message is safe to show in the interface."""


class ValidationError(AdvocacyTraceError):
    """A record breaks an evidence rule and was not stored or approved."""


class MissingCredentialError(AdvocacyTraceError):
    """Automated search was requested and no provider credential is configured."""


class DownloadFailedError(AdvocacyTraceError):
    """A manual URL import did not return a document."""


class UnreadablePdfError(AdvocacyTraceError):
    """A file could not be read as a PDF."""
