"""Partial dates and chronological comparisons."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from advocacy_trace.constants import DATE_PRECISIONS
from advocacy_trace.errors import ValidationError


@dataclass(frozen=True)
class Chronology:
    """Relationship between an intervention date and a later-or-earlier event."""

    relation: str
    intervention_precedes_event: bool
    can_explain_event: bool


def normalize_date(value: str | None, precision: str) -> str | None:
    """Return a canonical partial date, or None when the date is unknown."""

    if precision not in DATE_PRECISIONS:
        raise ValidationError(
            f"Date precision must be one of {', '.join(DATE_PRECISIONS)}."
        )
    if precision == "unknown":
        if value not in (None, ""):
            raise ValidationError(
                "A date marked unknown cannot contain a date value. Leave the date empty."
            )
        return None
    if value is None or str(value).strip() == "":
        raise ValidationError(f"A date with precision '{precision}' needs a value.")
    text = str(value).strip()
    try:
        if precision == "day":
            datetime.strptime(text, "%Y-%m-%d")
        elif precision == "month":
            datetime.strptime(text, "%Y-%m")
        else:
            datetime.strptime(text, "%Y")
    except ValueError as exc:
        raise ValidationError(
            f"Could not read '{text}' as a {precision} date. "
            "Use YYYY-MM-DD, YYYY-MM, or YYYY, or mark the date unknown."
        ) from exc
    return text


def chronology(
    intervention_date: str | None,
    intervention_precision: str,
    event_date: str | None,
    event_precision: str,
) -> Chronology:
    """Decide whether an intervention can sit before an event.

    Same day, same month, or same year is not treated as precedence when the
    available precision cannot order the two moments. A later report cannot
    explain an earlier verdict.
    """

    left = _bound(intervention_date, intervention_precision)
    right = _bound(event_date, event_precision)
    if left is None or right is None:
        return Chronology("unknown", False, False)
    if left[1] < right[0]:
        return Chronology("intervention_before_event", True, True)
    if left[0] > right[1]:
        return Chronology("intervention_after_event", False, False)
    return Chronology("unknown", False, False)


def date_in_filter(
    value: str | None,
    precision: str,
    date_from: str | None,
    date_to: str | None,
) -> bool | None:
    """True or False when the filter can decide. None when the record date is unknown."""

    if not date_from and not date_to:
        return True
    bound = _bound(value, precision)
    if bound is None:
        return None
    if date_from:
        start = _bound(date_from, _guess_precision(date_from))
        if start and bound[1] < start[0]:
            return False
    if date_to:
        end = _bound(date_to, _guess_precision(date_to))
        if end and bound[0] > end[1]:
            return False
    return True


def _guess_precision(value: str) -> str:
    if len(value) == 10:
        return "day"
    if len(value) == 7:
        return "month"
    return "year"


def _bound(value: str | None, precision: str) -> tuple[str, str] | None:
    """Inclusive earliest and latest full dates the partial value could be."""

    if precision == "unknown" or value in (None, ""):
        return None
    if precision == "day":
        return (value, value)
    if precision == "month":
        year, month = int(value[:4]), int(value[5:7])
        if month == 12:
            last = f"{year}-12-31"
        else:
            next_month = datetime(year, month + 1, 1)
            from datetime import timedelta

            last_day = next_month - timedelta(days=1)
            last = last_day.strftime("%Y-%m-%d")
        return (f"{value}-01", last)
    if precision == "year":
        return (f"{value}-01-01", f"{value}-12-31")
    return None
