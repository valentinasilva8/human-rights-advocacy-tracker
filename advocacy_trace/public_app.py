"""Public Advocacy Trace screens.

Run with: streamlit run advocacy_trace/public_app.py

This entry does not import the review workflow, internal case view, approval
controls, or source import. Those stay in advocacy_trace.app, which is not
linked from here.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from advocacy_trace.demo_screens import (
    NOT_RECORDED,
    SYNTHETIC_BANNER,
    open_walkthrough_store,
    public_brief,
    public_case,
    public_explorer,
)
from advocacy_trace.seed import open_store

SCREENS = ("Argument Explorer", "Case Evidence", "Advocacy Learning Brief")


def main() -> None:
    st.set_page_config(page_title="Advocacy Trace", layout="wide")
    st.title("Advocacy Trace")
    st.caption(
        "Independent hackathon prototype for reading advocacy evidence. "
        "Not a product of, and not endorsed by, the Clooney Foundation for Justice, "
        "TrialWatch, or Columbia Law School. Not a legal adviser or an outcome predictor."
    )
    pending_screen = st.session_state.pop("pending_screen", None)
    if pending_screen:
        st.session_state.public_screen = pending_screen
    pending_case = st.session_state.pop("pending_case", None)
    if pending_case:
        st.session_state.public_case_id = pending_case
    record_set = st.sidebar.radio(
        "Record set",
        ["Approved records", "Synthetic walkthrough"],
    )
    include_synthetic = record_set == "Synthetic walkthrough"
    store = _walkthrough_store() if include_synthetic else open_store()
    screen = st.sidebar.radio("Screen", SCREENS, key="public_screen")
    filters = _filters(store, include_synthetic)
    explorer = public_explorer(store, include_synthetic=include_synthetic, **filters)
    if screen == "Argument Explorer":
        _explorer(explorer)
    elif screen == "Case Evidence":
        _case(store, explorer)
    else:
        _brief(public_brief(explorer))


def _filters(store, include_synthetic: bool) -> dict:
    preview = public_explorer(store, include_synthetic=include_synthetic)
    fields = preview["filter_fields"]
    st.sidebar.caption(preview["date_rule"])
    label = _choice("Argument", fields["label"])
    country = _choice(
        "Jurisdiction",
        fields["country"],
        include_blank=fields["country_not_recorded"],
        enabled=fields["country_available"],
    )
    stage = _choice(
        "Procedural stage",
        fields["procedural_stage"],
        include_blank=fields["procedural_stage_not_recorded"],
        enabled=fields["procedural_stage_available"],
    )
    intervention = _choice(
        "Intervention type",
        fields["intervention_type"],
        include_blank=fields["intervention_type_not_recorded"],
        enabled=fields["intervention_type_available"],
    )
    date_from = st.sidebar.text_input("From date", placeholder="YYYY-MM-DD")
    date_to = st.sidebar.text_input("To date", placeholder="YYYY-MM-DD")
    return {
        "label": label,
        "country": country,
        "procedural_stage": stage,
        "intervention_type": intervention,
        "date_from": date_from.strip() or None,
        "date_to": date_to.strip() or None,
    }


def _choice(label: str, options: list[str], *, include_blank: bool = False, enabled: bool = True) -> str | None:
    if not enabled:
        st.sidebar.caption(f"{label} is not in the public projection.")
        return None
    values = ["Any", *options]
    if include_blank:
        values.append(NOT_RECORDED)
    selected = st.sidebar.selectbox(label, values)
    if selected == "Any":
        return None
    return selected


def _explorer(explorer: dict) -> None:
    st.header("Argument Explorer")
    _banners(explorer)
    if explorer["date_error"]:
        st.write(explorer["date_error"])
    _counts(explorer["counts"])
    if explorer["outside_selection_count"]:
        st.write(
            f"{explorer['outside_selection_count']} approved argument(s) have a recorded label, "
            "jurisdiction, stage, intervention type, or date outside this selection. "
            "They are omitted from the matched count."
        )
    _rows(explorer["matched_rows"], "Matched approved arguments")
    if explorer["date_unknown_rows"]:
        st.subheader("Date unknown")
        st.write(
            "These approved arguments have no date. They are not in the matched count, "
            "and they are not hidden."
        )
        _rows(explorer["date_unknown_rows"], "Unknown date")
    for key, title in (
        ("country", "Jurisdiction not recorded"),
        ("procedural_stage", "Procedural stage not recorded"),
        ("intervention_type", "Intervention type not recorded"),
    ):
        rows = explorer["unrecorded_rows"][key]
        if rows:
            st.subheader(title)
            st.write("These rows are not in the matched count. The missing value was not invented.")
            _rows(rows, title)


def _rows(rows: list[dict], heading: str) -> None:
    if not rows:
        st.write(f"No rows in {heading.lower()}.")
        return
    for row in rows:
        argument = row["argument"]
        case = row["case"]
        title = f"{case['title']} — {', '.join(argument.get('labels') or [])}"
        with st.expander(title):
            if case["is_synthetic"]:
                st.write(SYNTHETIC_BANNER)
            st.write(argument.get("summary") or "")
            author = row["author"]
            st.write(f"Author: {author['author']}")
            st.write(f"Role: {author['role']}")
            st.write(f"Affiliation: {author['affiliation']}")
            st.write(author["disclaimer"])
            intervention = row.get("intervention") or {}
            st.write(f"Intervention type: {intervention.get('intervention_type') or NOT_RECORDED}")
            st.write(f"Argument date: {row['when']}")
            st.write(f"Documented reception: {row['reception']['statement']}")
            developments = row["developments"]
            if developments["latest"]:
                latest = developments["latest"]
                st.write(
                    f"Latest approved development that can be ordered: "
                    f"{latest.get('event_type')} · {developments['latest_when']}"
                )
            else:
                st.write(developments["latest_note"])
            for event in developments["undated"]:
                st.write(f"Approved development with date unknown: {event.get('event_type')}")
            st.write(developments["statement"])
            if row["public_limitation"]:
                st.write(f"Limitation: {row['public_limitation']}")
            if row["evidence_basis_caption"]:
                st.write(row["evidence_basis_caption"])
            if st.button("Open case evidence", key=f"open-{heading}-{argument['id']}"):
                st.session_state.pending_screen = "Case Evidence"
                st.session_state.pending_case = case["id"]
                st.rerun()


def _case(store, explorer: dict) -> None:
    st.header("Case Evidence")
    _banners(explorer)
    case_ids = explorer["selectable_case_ids"]
    if not case_ids:
        st.write(explorer["empty_real"] or "No case is in this public selection.")
        return
    labels = {}
    for row in explorer["matched_rows"] + explorer["date_unknown_rows"]:
        labels[row["case"]["id"]] = row["case"]["title"]
    for rows in explorer["unrecorded_rows"].values():
        for row in rows:
            labels[row["case"]["id"]] = row["case"]["title"]
    current = st.session_state.get("public_case_id")
    if current not in case_ids:
        current = case_ids[0]
    case_id = st.selectbox(
        "Proceeding",
        case_ids,
        index=case_ids.index(current),
        format_func=lambda item: labels.get(item, item),
    )
    st.session_state.public_case_id = case_id
    view = public_case(store, case_id, st.session_state.get("public_reference_choice"))
    if view.get("omitted"):
        st.write(view["reason"])
        return
    options = [item["id"] for item in _interventions_from_items(view)]
    if not options:
        reference_id = None
    else:
        default = view["reference_intervention"]["id"] if view.get("reference_intervention") else options[0]
        if default not in options:
            default = options[0]
        stored = st.session_state.get("public_reference_choice")
        if stored not in options:
            stored = default
        reference_id = st.selectbox(
            "Reference intervention",
            options,
            index=options.index(stored),
            format_func=lambda item: _intervention_label(view, item),
        )
        st.session_state.public_reference_choice = reference_id
    if reference_id != (view.get("reference_intervention") or {}).get("id"):
        view = public_case(store, case_id, reference_id)
    if view["synthetic_banner"]:
        st.write(view["synthetic_banner"])
    case = view["case"]
    st.write(
        {
            "Jurisdiction": case["country"],
            "Court": case["court"],
            "Case number": case["case_number"],
            "Charges": case["charges"],
            "Procedural stage": case["procedural_stage"],
            "Finality": case["finality"],
        }
    )
    coverage = view["coverage"]
    st.subheader("Coverage")
    st.write(f"Record review date: {coverage['record_review']}")
    st.write(coverage["record_review_note"])
    latest = coverage["latest_documented_event"]
    label = coverage["latest_documented_event_label"]
    st.write(
        "Latest documented event date: "
        + (f"{label} · {latest}" if label else latest)
    )
    st.write(coverage["latest_documented_event_note"])
    st.write(f"Follow-up search coverage: {coverage['follow_up_search_coverage']}")
    if not options:
        st.write("No intervention is in the public record for this case.")
    reference = view.get("reference_intervention")
    if reference:
        st.write(
            f"Reference intervention: {reference['actor']} · {reference['intervention_type'] or NOT_RECORDED} · {reference['when']}"
        )
    if view["other_interventions_note"]:
        st.write(view["other_interventions_note"])
    st.write(view["causation_note"])
    for band_key, band_title in view["bands"].items():
        st.subheader(band_title)
        band_items = [item for item in view["items"] if item["band"] == band_key]
        if not band_items:
            st.write("No approved public record in this band.")
            continue
        for item in band_items:
            st.write(f"{item['title']} · {item['when']}")
    item_ids = [item["id"] for item in view["items"]]
    if item_ids:
        selected = st.selectbox(
            "Chronology item",
            item_ids,
            format_func=lambda item: _item_label(view, item),
        )
        detail = next(item["detail"] for item in view["items"] if item["id"] == selected)
        st.subheader("Selected record")
        st.write(detail["quotation"])
        st.write(f"Location: {detail['location']}")
        st.write(f"Direct link: {detail['url']}")
        if detail.get("limitation"):
            st.write(f"Limitation: {detail['limitation']}")
        if detail.get("evidence_basis_caption"):
            st.write(detail["evidence_basis_caption"])
        if detail.get("evidence_label"):
            st.write(f"Evidence label: {detail['evidence_label']}")
        if detail.get("disposition_note"):
            st.write(detail["disposition_note"])
        for argument in detail.get("linked_arguments") or []:
            st.write(f"{argument['author']['author']} — {argument['author']['role']}")
            st.write(argument["summary"])
            st.write(argument["quotation"])
            st.write(f"Location: {argument['location']}")
            st.write(f"Direct link: {argument['url']}")
            st.write(f"Argument date: {argument['when']}")
            if argument["limitation"]:
                st.write(f"Limitation: {argument['limitation']}")
            if argument["evidence_basis_caption"]:
                st.write(argument["evidence_basis_caption"])
    st.subheader("Argument reception")
    st.write("Reception is separate from case disposition.")
    if not view["receptions"]:
        st.write("No approved argument is in the public record.")
    for reception in view["receptions"]:
        author = reception["author"]
        st.write(f"{author['author']} — {author['role']}")
        st.write(reception["summary"])
        st.write(reception["statement"])
        for record in reception["records"]:
            if record.get("passage"):
                st.write(record["passage"])
            st.write(f"Location: {record.get('location_ref') or NOT_RECORDED}")
            if record.get("public_limitation"):
                st.write(f"Limitation: {record['public_limitation']}")
            if record.get("evidence_basis"):
                st.write(_basis_line(record.get("evidence_basis")))


def _brief(brief: dict) -> None:
    st.header("Advocacy Learning Brief")
    st.write(brief["label"])
    _banners(brief)
    st.write(brief["sample_limit"])
    counts = brief["selection_counts"]
    if counts:
        _counts(counts)
    facts = brief["facts"]
    st.subheader("Documented engagement")
    if not facts["engagement"]:
        st.write("No approved argument is in this selection.")
    for item in facts["engagement"]:
        st.write(item["case_title"])
        st.write(item["summary"])
        author = item["author"]
        st.write(f"Author: {author['author']}")
        st.write(f"Role: {author['role']}")
        st.write(f"Quotation: {item['quotation']}")
        st.write(f"Location: {item['location']}")
        st.write(f"Source: {item['source_title']}")
        st.write(f"Direct link: {item['source_url']}")
    st.subheader("Documented reception")
    if not facts["documented_reception"]:
        st.write("No approved reception is in this selection.")
    for item in facts["documented_reception"]:
        st.write(f"{item['case_title']} · {item['author']}")
        st.write(item["statement"])
        for record in item["records"]:
            if record.get("passage"):
                st.write(record["passage"])
            if record.get("public_limitation"):
                st.write(f"Limitation: {record['public_limitation']}")
    st.subheader("Unknown reception")
    if not facts["unknown_reception"]:
        st.write("Every argument in this selection has an approved reception record.")
    for item in facts["unknown_reception"]:
        st.write(f"{item['case_title']} · {item['author']}")
        st.write(item["statement"])
    st.subheader("Documented developments")
    if not facts["developments"]:
        st.write("No approved development is in this selection.")
    for item in facts["developments"]:
        st.write(f"{item['case_title']} · {item['event_type']} · {item['when']}")
        st.write(item["description"])
        if item["limitation"]:
            st.write(f"Limitation: {item['limitation']}")
        if item["evidence_basis_caption"]:
            st.write(item["evidence_basis_caption"])
        st.write(item["reception_note"])
    st.subheader("Evidence gaps")
    for gap in facts["evidence_gaps"]:
        st.write(gap)
    st.subheader("Documented implementation status")
    st.write(facts["implementation_status"])
    st.subheader("Follow-up questions")
    st.write(brief["suggestions_label"])
    for question in brief["suggestions"]:
        st.write(question)


def _counts(counts: dict) -> None:
    st.write(f"Matched approved arguments: {counts['matched_arguments']}")
    st.write(f"Unique cases in this selection: {counts['unique_cases']}")
    st.write(f"Real cases in this selection: {counts['real_cases']}")
    st.write(f"Demonstration cases in this selection, not real: {counts['demonstration_cases']}")
    st.write(f"Cases in this selection with no verified subsequent outcome: {counts['unknown_outcome_cases']}")
    st.caption(counts["count_note"])


def _banners(payload: dict) -> None:
    if payload.get("synthetic_banner"):
        st.write(payload["synthetic_banner"])
    if payload.get("empty_real"):
        st.write(payload["empty_real"])


def _interventions_from_items(view: dict) -> list[dict]:
    return [item for item in view["items"] if item["kind"] == "intervention"]


def _intervention_label(view: dict, item_id: str) -> str:
    item = next(item for item in view["items"] if item["id"] == item_id)
    return f"{item['title']} · {item['when']}"


def _item_label(view: dict, item_id: str) -> str:
    item = next(item for item in view["items"] if item["id"] == item_id)
    return f"{view['bands'][item['band']]}: {item['title']} · {item['when']}"


def _basis_line(value: str | None) -> str:
    from advocacy_trace.constants import EVIDENCE_BASIS_PUBLIC

    return EVIDENCE_BASIS_PUBLIC.get(value or "not_yet_established", "")


def _walkthrough_store():
    if "public_walkthrough" not in st.session_state:
        folder = Path(tempfile.mkdtemp(prefix="advocacy-trace-walkthrough-"))
        st.session_state.public_walkthrough = open_walkthrough_store(folder / "walkthrough.sqlite")
    return st.session_state.public_walkthrough


if __name__ == "__main__":
    main()
