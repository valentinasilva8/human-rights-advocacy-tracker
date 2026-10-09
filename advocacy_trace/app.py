"""Three local screens: explorer, case evidence, and review."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from advocacy_trace.constants import ARGUMENT_LABELS, INTERVENTION_TYPES
from advocacy_trace.errors import MissingCredentialError, UnreadablePdfError, ValidationError
from advocacy_trace.importing import read_pdf_excerpt, require_search_provider
from advocacy_trace.seed import open_store
from advocacy_trace.views import case_view, explorer_view

HEADLINE_LABELS = [label for label in ARGUMENT_LABELS if label != "unmapped—review required"]


def main() -> None:
    st.set_page_config(page_title="Advocacy Trace", layout="wide")
    st.title("Advocacy Trace")
    st.caption(
        "Independent hackathon prototype for reading advocacy evidence. "
        "Not a product of, and not endorsed by, the Clooney Foundation for Justice, "
        "TrialWatch, or Columbia Law School. Not a legal adviser or an outcome predictor."
    )
    store = open_store()
    screen = st.sidebar.radio(
        "Screen",
        ["Argument Explorer", "Case Evidence", "Review and Learning"],
    )
    st.sidebar.info(
        "The loaded example is fictional (Exampleland v. A. Rivera) and is excluded from real-case counts."
    )
    if screen == "Argument Explorer":
        _explorer(store)
    elif screen == "Case Evidence":
        _case(store)
    else:
        _review(store)


def _explorer(store) -> None:
    st.header("Argument Explorer")
    st.write(
        "TrialWatch arguments only. A report's description of counsel's argument is not listed here. "
        "Counts use unique cases."
    )
    countries = sorted({case["country"] for case in store.list_cases() if case.get("country")})
    filters = st.columns(4)
    with filters[0]:
        label = st.selectbox("Argument", ["Proportionality", *HEADLINE_LABELS[0:4], "Any"], index=0)
    with filters[1]:
        country = st.selectbox("Country", ["Any", *countries])
    with filters[2]:
        intervention = st.selectbox("Intervention", ["Any", *INTERVENTION_TYPES])
    with filters[3]:
        status = st.selectbox("Verification", ["approved", "proposed", "rejected", "Any"])
    dates = st.columns(2)
    with dates[0]:
        date_from = st.text_input("From (YYYY-MM-DD)", "")
    with dates[1]:
        date_to = st.text_input("To (YYYY-MM-DD)", "")
    include_synthetic = st.checkbox("Include labeled demonstration records", value=True)
    chosen_label = None if label == "Any" else label
    view = explorer_view(
        store,
        label=chosen_label,
        country=None if country == "Any" else country,
        intervention_type=None if intervention == "Any" else intervention,
        date_from=date_from.strip(),
        date_to=date_to.strip(),
        review_status=None if status == "Any" else status,
        include_synthetic=include_synthetic,
    )
    metrics = st.columns(4)
    metrics[0].metric("Arguments", view["argument_count"])
    metrics[1].metric("Unique cases", view["unique_cases"])
    metrics[2].metric("Verified real cases", view["verified_real_cases"])
    metrics[3].metric("Cases with unknown outcome", view["unknown_outcome_cases"])
    st.caption(view["note"])
    if view["verified_real_cases"] == 0:
        st.warning(
            "Verified real cases: 0. Demonstration rows are not real matters and do not enter this count."
        )
    if view["hidden_unknown_dates"]:
        st.info(
            f"{view['hidden_unknown_dates']} argument(s) have an unknown date and are hidden by this date filter."
        )
    if not view["rows"]:
        st.info("No arguments match these filters.")
    for row in view["rows"]:
        argument = row["argument"]
        case = row["case"]
        title = f"{case['title']} — {', '.join(argument['labels'])}"
        with st.expander(title, expanded=False):
            for gap in row["gaps"]:
                st.warning(gap)
            st.subheader("What was argued")
            st.text(argument["summary"])
            st.text(argument["passage"])
            st.caption(f"Location: {argument['location_ref']} · Author: {argument['author_actor']}")
            st.write(argument["reasons"])
            if argument["legal_authorities"]:
                st.caption(argument["legal_authorities"])
            st.subheader("Documented response")
            if not row["receptions"]:
                st.warning("No reception record. Unknown reception is a result, not acceptance.")
            for reception in row["receptions"]:
                st.text(f"{reception['status']} ({reception['review_status']})")
                if reception["is_recital"]:
                    st.warning("This passage recites the argument. Recital is not acceptance.")
                if reception["passage"]:
                    st.text(reception["passage"])
            st.subheader("What happened afterward")
            st.text(row["outcome"]["statement"])
            for event in row["outcome"]["events"]:
                when = event["event_date"] or "date unknown"
                st.text(f"{event['event_type']} · {when} · {event['evidence_label']}")
                st.text(event["description"])


def _case(store) -> None:
    st.header("Case Evidence")
    show_restricted = st.checkbox("Show restricted records", value=False)
    cases = [
        case
        for case in store.list_cases()
        if show_restricted or not case["sensitive"]
    ]
    if not cases:
        st.info("No cases to show.")
        return
    labels = {case["id"]: case["title"] for case in cases}
    options = list(labels)
    default_index = options.index("case_rivera") if "case_rivera" in options else 0
    case_id = st.selectbox(
        "Proceeding",
        options,
        index=default_index,
        format_func=lambda item: labels[item],
    )
    view = case_view(store, case_id)
    case = view["case"]
    if case["sensitive"]:
        st.warning("Restricted record. Public export omits this proceeding even if it is visible here.")
    if case["is_synthetic"]:
        st.info("Synthetic demonstration. Not a real case.")
    for gap in view["gaps"]:
        st.warning(gap)
    st.subheader("Proceeding")
    st.write(
        {
            "Country": case.get("country") or "unknown",
            "Court": case.get("court") or "unknown",
            "Case number": case.get("case_number") or "unknown",
            "Charges": case.get("charges") or "unknown",
            "Stage": case.get("procedural_stage") or "unknown",
            "Finality": case.get("finality") or "unknown",
            "Last verified": _dated(case.get("last_verified_on"), case.get("last_verified_on_precision")),
        }
    )
    if case["unresolved_questions"]:
        st.subheader("Unresolved questions")
        st.warning(case["unresolved_questions"])
    st.subheader("Defendants and participants")
    if view["participants"]:
        for person in view["participants"]:
            st.text(f"{person['name']} · {person['role_in_case']}")
    else:
        st.text("No participants recorded.")
    st.subheader("Interventions")
    for intervention in view["interventions"]:
        st.text(
            f"{intervention['actor']} · {intervention['intervention_type']} · "
            f"{_dated(intervention['intervention_date'], intervention['intervention_date_precision'])}"
        )
        st.write(intervention["description"])
    for note in view["chronology_notes"]:
        st.warning(note)
    st.subheader("Arguments and passages")
    for item in view["arguments"]:
        argument = item["argument"]
        st.markdown(f"**{argument['author_actor']}** · `{argument['attribution_role']}`")
        st.text(argument["summary"] or "(no summary yet)")
        st.text(argument["passage"] or "(no passage yet — cannot be approved)")
        st.caption(
            f"{argument['location_ref'] or 'location missing'} · "
            f"{', '.join(argument['labels']) or 'no label'} · {argument['review_status']}"
        )
        if item["source"]:
            source = item["source"]
            st.caption(
                f"Source: {source['title']} · published {_dated(source['publication_date'], source['publication_date_precision'])}"
            )
        for reception in item["receptions"]:
            prefix = "Recital, not acceptance. " if reception["is_recital"] else ""
            st.text(f"Reception: {prefix}{reception['status']}")
            if reception["passage"]:
                st.text(reception["passage"])
    st.subheader("Outcome events")
    st.text(view["outcome_summary"]["statement"])
    if not view["outcomes"]:
        st.warning("No outcome events. The outcome stays unknown.")
    for event in view["outcomes"]:
        st.text(
            f"{event['event_type']} · event {_dated(event['event_date'], event['event_date_precision'])} · "
            f"{event['evidence_label']} · {event['review_status']}"
        )
        st.write(event["description"])
        if event["supersedes_event_id"]:
            st.caption(
                f"Links to earlier event {event['supersedes_event_id']} without deleting it."
            )
        for link in store.evidence_links_for("outcome_event", event["id"]):
            source = store.get_source(link["source_id"])
            kind = "duplicate, not independent" if link["relationship"] == "duplicates" else link["relationship"]
            st.caption(
                f"Source {source['title']} ({kind}). "
                f"Publication date {_dated(source['publication_date'], source['publication_date_precision'])} "
                "is not the event date."
            )


def _review(store) -> None:
    st.header("Review and Learning")
    st.write(
        "Proposed classifications and outcome updates stay here until a named reviewer acts. "
        "Approving a row records that action. The learning brief is not sent."
    )
    reviewer = st.text_input("Reviewer name", value="")
    queue = store.review_queue()
    options: list[tuple[str, str, str]] = []
    for argument in queue["arguments"]:
        options.append(("argument", argument["id"], f"Argument · {argument['summary'] or argument['id']}"))
    for event in queue["outcomes"]:
        options.append(("outcome_event", event["id"], f"Outcome · {event['event_type']} · {event['description'][:80]}"))
    for reception in queue["receptions"]:
        options.append(("reception", reception["id"], f"Reception · {reception['status']}"))
    if not options:
        st.success("The review queue is empty.")
    else:
        selected = st.selectbox("Proposed record", options, format_func=lambda item: item[2])
        target_type, target_id, _label = selected
        record = _queue_record(queue, target_type, target_id)
        st.text(str(record.get("summary") or record.get("description") or record.get("passage") or ""))
        if target_type == "argument" and not record.get("passage"):
            st.warning("This argument has no supporting passage, so it cannot be approved.")
        columns = st.columns(2)
        if columns[0].button("Approve"):
            _act(store, target_type, target_id, "approve", reviewer)
        if columns[1].button("Reject"):
            _act(store, target_type, target_id, "reject", reviewer)
        with st.form("edit-record"):
            summary = st.text_area("Summary or description", value=_editable_text(record))
            passage = st.text_area("Passage", value=record.get("passage") or "")
            location = st.text_input("Location", value=record.get("location_ref") or "")
            save = st.form_submit_button("Save edit")
        if save:
            edits = _edits_for(target_type, summary, passage, location)
            _act(store, target_type, target_id, "edit", reviewer, edits=edits)

    st.subheader("Import a source file")
    st.caption("Manual import only. The file stays in the local downloads folder and is not committed.")
    upload = st.file_uploader("PDF or text", type=None)
    if upload is not None:
        folder = Path("downloads")
        folder.mkdir(exist_ok=True)
        destination = folder / Path(upload.name).name
        destination.write_bytes(upload.getvalue())
        if destination.suffix.lower() == ".pdf":
            try:
                read_pdf_excerpt(destination)
            except UnreadablePdfError as exc:
                st.error(str(exc))
            else:
                st.info(
                    "The PDF header is intact, but this prototype does not extract PDF text. "
                    "Paste a short reviewed excerpt into the edit form."
                )
        else:
            st.info(f"Stored {destination.name} locally. Paste a reviewed excerpt into the queue if you use it.")
    url = st.text_input("Source URL", value="")
    if st.button("Check automated fetch"):
        try:
            require_search_provider()
        except MissingCredentialError as exc:
            st.error(str(exc))
        else:
            st.error(
                "Automated download is not enabled in this version, even if a credential is present. "
                "Import the file manually."
            )
        if url:
            st.caption(f"URL not fetched: {url}")

    st.subheader("Learning brief")
    include_demo = st.checkbox("Draft from demonstration records as well as real cases", value=True)
    if "learning_brief" not in st.session_state:
        st.session_state.learning_brief = store.learning_brief(include_synthetic=include_demo)
    if st.button("Regenerate draft"):
        st.session_state.learning_brief = store.learning_brief(include_synthetic=include_demo)
    st.text_area("Editable draft", height=360, key="learning_brief")
    st.caption("This draft stays in the session. The app does not publish or send it.")


def _act(store, target_type: str, target_id: str, action: str, reviewer: str, edits: dict | None = None) -> None:
    try:
        store.review(target_type, target_id, action, reviewer, edits=edits)
    except ValidationError as exc:
        st.error(str(exc))
        return
    st.rerun()


def _queue_record(queue: dict, target_type: str, target_id: str) -> dict:
    bucket = {
        "argument": queue["arguments"],
        "outcome_event": queue["outcomes"],
        "reception": queue["receptions"],
    }[target_type]
    return next(item for item in bucket if item["id"] == target_id)


def _editable_text(record: dict) -> str:
    return record.get("summary") or record.get("description") or ""


def _edits_for(target_type: str, summary: str, passage: str, location: str) -> dict:
    if target_type == "argument":
        return {"summary": summary, "passage": passage, "location_ref": location}
    if target_type == "outcome_event":
        return {"description": summary}
    return {"passage": passage, "location_ref": location, "observer_note": summary}


def _dated(value: str | None, precision: str | None) -> str:
    if not value or precision == "unknown":
        return "unknown"
    return f"{value} ({precision})"


main()
