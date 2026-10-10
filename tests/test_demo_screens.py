"""Public demo screens stay on approved projections."""

from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import advocacy_trace.demo_screens as demo_screens
import advocacy_trace.public_app as public_app
from advocacy_trace.demo_screens import (
    open_walkthrough_store,
    public_brief,
    public_case,
    public_explorer,
)
from advocacy_trace.store import EvidenceStore

SECRET_MARKERS = (
    "PRIVATE-CASE-QUESTION",
    "PRIVATE-OBSERVER-NOTE",
    "INTERNAL-PROPOSED-SECRET",
    "INTERNAL-PROPOSED-OUTCOME",
    "PRIVATE-SEARCH-NOTE",
)


def _walkthrough(tmp_path: Path) -> EvidenceStore:
    return open_walkthrough_store(tmp_path / "walkthrough.sqlite")


def _strings(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(_strings(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return "\n".join(_strings(item) for item in value)
    return ""


def test_walkthrough_filters_counts_and_brief_stay_together(tmp_path):
    store = _walkthrough(tmp_path)
    explorer = public_explorer(store, include_synthetic=True)
    assert explorer["counts"]["matched_arguments"] == 4
    assert explorer["counts"]["unique_cases"] == 2
    assert explorer["counts"]["real_cases"] == 0
    assert explorer["counts"]["demonstration_cases"] == 2
    assert "TrialWatch's argument" not in _strings(explorer)

    proportionality = public_explorer(store, label="Proportionality", include_synthetic=True)
    assert [row["argument"]["id"] for row in proportionality["matched_rows"]] == ["arg_chen_prop"]
    brief = public_brief(proportionality)
    assert [item["argument_id"] for item in brief["facts"]["engagement"]] == ["arg_chen_prop"]
    assert brief["selection_counts"]["matched_arguments"] == 1
    assert brief["selection_counts"]["real_cases"] == 0
    assert "cannot support a general or cross-case conclusion" in brief["sample_limit"]
    assert "Not a human-reviewed brief" in brief["label"]

    southferry = public_explorer(store, country="Southferry", include_synthetic=True)
    assert southferry["counts"]["unique_cases"] == 1
    assert southferry["matched_rows"][0]["case"]["id"] == "case_walk_adeyemi"

    trial = public_explorer(store, procedural_stage="trial", include_synthetic=True)
    assert [row["argument"]["id"] for row in trial["matched_rows"]] == ["arg_adeyemi_broad"]

    amicus = public_explorer(store, intervention_type="amicus", include_synthetic=True)
    assert amicus["counts"]["matched_arguments"] == 1

    may = public_explorer(store, date_from="2023-05-01", date_to="2023-05-31", include_synthetic=True)
    matched_ids = {row["argument"]["id"] for row in may["matched_rows"]}
    unknown_ids = {row["argument"]["id"] for row in may["date_unknown_rows"]}
    assert matched_ids == {"arg_chen_prop", "arg_chen_vague"}
    assert unknown_ids == {"arg_chen_undated"}
    assert any(row["when"] == "2023-05 (month)" for row in may["matched_rows"])
    assert all("2023-05-01" not in row["when"] for row in may["matched_rows"])
    assert may["counts"]["matched_arguments"] == 2
    assert "date unknown" in may["date_rule"]
    scoped = public_brief(may)
    assert {item["argument_id"] for item in scoped["facts"]["engagement"]} == matched_ids
    assert "arg_chen_undated" not in _strings(scoped["facts"]["engagement"])


def test_chronology_keeps_unknown_order_out_of_the_before_band(tmp_path):
    store = _walkthrough(tmp_path)
    case = public_case(store, "case_walk_chen", "int_chen_report")
    bands = {item["id"]: item["band"] for item in case["items"]}
    assert bands["out_chen_conviction"] == "before"
    assert bands["out_chen_charges"] == "unknown"
    assert bands["out_chen_appeal"] == "after"
    assert bands["int_chen_statement"] == "unknown"
    assert bands["int_chen_report"] == "reference"
    assert case["reference_intervention"]["id"] == "int_chen_report"
    assert "caused" in case["causation_note"]
    appeal = next(item for item in case["items"] if item["id"] == "out_chen_appeal")
    assert "authenticity" in appeal["detail"]["limitation"]
    assert "not a finding about how an authority received" in appeal["detail"]["disposition_note"]
    receptions = {item["argument_id"]: item for item in case["receptions"]}
    assert receptions["arg_chen_prop"]["established"] is False
    assert "ignored the argument" in receptions["arg_chen_prop"]["statement"]
    assert receptions["arg_chen_vague"]["established"] is True
    assert "public unease" in receptions["arg_chen_vague"]["records"][0]["passage"]
    assert "not a reception of the proportionality argument" in _strings(receptions["arg_chen_vague"])
    coverage = case["coverage"]
    assert coverage["record_review"] == "2024-06 (month)"
    assert "not proof that the timeline is complete" in coverage["record_review_note"]
    assert coverage["latest_documented_event"] == "2024-02 (month)"
    assert coverage["follow_up_search_coverage"] == "Follow-up search coverage is not in the public record."
    assert "2023-01-15 (day)" in _strings(case)
    assert "2023 (year)" in _strings(case)


def test_brief_does_not_treat_a_dismissal_as_reception(tmp_path):
    store = _walkthrough(tmp_path)
    brief = public_brief(public_explorer(store, include_synthetic=True))
    facts = brief["facts"]
    unknown_ids = {item["argument_id"] for item in facts["unknown_reception"]}
    assert "arg_chen_prop" in unknown_ids
    assert "arg_chen_undated" in unknown_ids
    documented_ids = {item["argument_id"] for item in facts["documented_reception"]}
    assert documented_ids == {"arg_chen_vague"}
    dismissal = next(item for item in facts["developments"] if item["event_id"] == "out_chen_appeal")
    assert "dismissed" in dismissal["description"]
    assert "not a reception finding" in dismissal["reception_note"]
    assert "dismissed the conviction appeal" not in _strings(facts["documented_reception"])
    assert facts["implementation_status"].startswith("No documented implementation status")
    assert "not a finding that implementation failed" in facts["implementation_status"]
    assert "not established findings" in brief["suggestions_label"]
    assert "authenticity" in _strings(facts["evidence_gaps"])


def test_empty_real_selection_excludes_synthetic_and_proposed_rows(tmp_path):
    store = _walkthrough(tmp_path)
    store.add_research_attempt(
        case_id="case_walk_chen",
        query="later appeal",
        place="synthetic catalog",
        result="not opened",
        note="PRIVATE-SEARCH-NOTE",
        searched_on="2026-10-09",
        is_synthetic=True,
    )
    explorer = public_explorer(store, include_synthetic=False)
    brief = public_brief(explorer)
    blob = "\n".join(
        [
            _strings(explorer),
            _strings(brief),
            _strings(public_case(store, "case_walk_chen", "int_chen_report")),
        ]
    )
    assert explorer["counts"]["matched_arguments"] == 0
    assert explorer["counts"]["real_cases"] == 0
    assert explorer["counts"]["demonstration_cases"] == 0
    assert explorer["empty_real"]
    assert "Mina Okonkwo" not in _strings(explorer)
    assert "cannot support a general or cross-case conclusion" in brief["sample_limit"]
    for marker in SECRET_MARKERS:
        assert marker not in blob


def test_proposed_real_row_is_not_in_the_public_models(tmp_path):
    store = EvidenceStore(tmp_path / "proposed.sqlite")
    store.add_participant(id="person_real", name="A. Proposed")
    store.add_case(
        id="case_real",
        title="Poland v. Proposed",
        country="Poland",
        procedural_stage="appeal",
        is_synthetic=False,
    )
    store.link_participant("case_real", "person_real", "defendant")
    store.add_source(
        id="src_real",
        title="Unapproved report",
        document_type="fairness_report",
        author_actor="A. Author",
        is_synthetic=False,
    )
    store.add_intervention(
        id="int_real",
        case_id="case_real",
        actor="A. Author",
        intervention_type="fairness_report",
        attribution_basis="document_authored",
        source_id="src_real",
    )
    store.add_argument(
        id="arg_real",
        case_id="case_real",
        intervention_id="int_real",
        source_id="src_real",
        author_actor="A. Author",
        attribution_role="partner_argument",
        summary="INTERNAL-PROPOSED-SECRET",
        passage="INTERNAL-PROPOSED-SECRET",
        location_ref="p. 1",
        labels=["Proportionality"],
        is_synthetic=False,
    )
    explorer = public_explorer(store, include_synthetic=True)
    case = public_case(store, "case_real", None)
    assert explorer["matched_rows"] == []
    assert "INTERNAL-PROPOSED-SECRET" not in _strings(explorer)
    assert "INTERNAL-PROPOSED-SECRET" not in _strings(case)
    assert case["omitted"] is True


def test_recorded_poland_approvals_are_the_only_real_public_rows(tmp_path):
    from advocacy_trace.seed import open_store

    store = open_store(tmp_path / "approved.sqlite")
    assert store.get_argument("pl_arg_legality")["review_status"] == "approved"
    assert store.get_argument("pl_arg_proportionality")["review_status"] == "approved"
    assert store.get_argument("tam_arg_breadth")["review_status"] == "proposed"

    explorer = public_explorer(store, include_synthetic=False)
    brief = public_brief(explorer)
    case = public_case(store, "case_poland", "pl_int_report")
    blob = "\n".join([_strings(explorer), _strings(brief), _strings(case)])
    assert {row["argument"]["id"] for row in explorer["matched_rows"]} == {
        "pl_arg_legality",
        "pl_arg_proportionality",
    }
    assert explorer["counts"]["real_cases"] == 1
    assert explorer["counts"]["unique_cases"] == 1
    assert explorer["counts"]["demonstration_cases"] == 0
    assert explorer["counts"]["matched_arguments"] == 2
    assert explorer["counts"]["unknown_outcome_cases"] == 0
    assert explorer["export_counts"]["schema_version"] == "1"
    assert explorer["export_counts"]["timeline_caption"] == "Latest approved event in this dataset."
    generated = explorer["export_counts"]["export_generated_at"]
    assert generated and "2022-01-12" not in generated
    assert explorer["export_counts"]["real_case_count"] == 1
    assert explorer["export_counts"]["approved_argument_count"] == 2
    assert explorer["export_counts"]["reception_count"] == 0
    assert set(explorer["export_counts"]["outcome_event_ids"]) == {
        "out_pl_appeal_podlesna",
        "out_pl_appeal_prus",
        "out_pl_appeal_gzyra",
    }
    assert "do not approve or verify the case" in explorer["case_scope_note"]
    assert "success rate" in explorer["counts"]["count_note"]

    by_id = {row["argument"]["id"]: row for row in explorer["matched_rows"]}
    legality = by_id["pl_arg_legality"]
    proportionality = by_id["pl_arg_proportionality"]
    assert "Article 196 is not precise" in legality["argument"]["passage"]
    assert legality["argument"]["location_ref"] == "Fairness report, printed p. 3, PDF page 4"
    assert set(legality["argument"]["labels"]) == {"Legality", "Broadness"}
    assert "necessity and proportionality requirements" in proportionality["argument"]["passage"]
    assert proportionality["argument"]["location_ref"] == "Fairness report, printed p. 4, PDF page 5"
    assert set(proportionality["argument"]["labels"]) == {"Necessity", "Proportionality"}
    for row in (legality, proportionality):
        assert row["when"] == "2021-11 (month)"
        assert row["author"]["author"] == "Lisa Davis"
        assert "City University of New York" in row["author"]["affiliation"]
        assert "American Bar Association" in row["author"]["disclaimer"]
        assert "should likewise be rejected" in row["argument"]["remedy_requested"]
        assert "Recommendations from Professor Lisa Davis" in row["argument"]["remedy_requested"]
        assert row["argument"]["passage"] not in row["argument"]["remedy_requested"]
        links = {link["label"]: link["url"] for link in row["source"]["links"]}
        assert links["Report page"] == (
            "https://cfj.org/reports/poland-vs-elzbieta-podlesna-anna-prus-and-joanna-gzyra-iskandar/"
        )
        assert links["PDF"] == (
            "https://cfj.org/wp-content/uploads/2023/07/trial-observation-report-poland-lgbt.pdf"
        )
        assert row["source"]["when"] == "2021-11 (month)"
        assert "rights_note" not in row["source"]

    assert case["court_reception_note"].startswith("Court reception of the report is not established")
    assert "not acceptance and it is not rejection" in case["court_reception_note"]
    assert case["chronology_note"].startswith("The public chronology is incomplete")
    appeal = next(item for item in case["items"] if item["kind"] == "outcome")
    assert appeal["id"] == "pl_decision_appeal_2022-01-12"
    assert appeal["when"] == "2022-01-12 (day)"
    assert appeal["band"] == "after"
    assert "3 defendant-specific rows" in appeal["detail"]["defendants_note"]
    assert "Podleśna, Prus, and Gzyra-Iskandar" in appeal["detail"]["defendants_note"]
    assert "HFHR reported" in appeal["detail"]["quotation"]
    assert "judgment itself was not retrieved" in appeal["detail"]["limitation"]
    assert "not a statement that 12 January 2022 is the latest known development" in appeal["detail"]["limitation"]
    assert "does not establish acceptance or rejection" in appeal["detail"]["limitation"]
    labels = {link["label"] for link in appeal["detail"]["links"]}
    urls = {link["url"] for link in appeal["detail"]["links"]}
    by_url = {link["url"]: link for link in appeal["detail"]["links"]}
    assert "Helsinki Foundation for Human Rights (organization account)" in labels
    hfhr_url = "https://hfhr.pl/aktualnosci/tecza-nie-obraza-wyrok-uniewinnienie"
    rp_url = "https://www.rp.pl/prawo-karne/art19284511-zapadl-prawomocny-wyrok-ws-matki-bozej-z-teczowa-aureola"
    oko_url = "https://oko.press/tecza-nie-obraza-prawomocny-wyrok-sadu-apelacyjnego-w-plocku"
    article_url = "https://www.article19.org/wp-content/uploads/2024/03/Amicus_Poland-Rainbow-Holy-Mary_EN.pdf"
    assert hfhr_url in urls
    assert rp_url in urls
    assert oko_url in urls
    assert article_url in urls
    hfhr = by_url[hfhr_url]
    assert hfhr["support_scope"] == "whole_claim"
    assert hfhr["publication_when"] == "2022-01-13 (day)"
    assert any(
        "On 12 January 2022 the Regional Court in Płock upheld the acquitting judgment" in passage["text"]
        for passage in hfhr["passages"]
        if passage["kind"] == "translation"
    )
    assert any(passage["kind"] == "quotation" for passage in hfhr["passages"])
    oko = by_url[oko_url]
    assert oko["support_scope"] == "identity_and_reported_result"
    assert oko["provenance"] == "independent"
    assert oko["publication_when"] == "2022-01-12 (day)"
    assert "does not corroborate the whole claim" in oko["note"]
    rp = by_url[rp_url]
    assert rp["support_scope"] == "whole_claim"
    assert rp["provenance"] == "derived_from_shared_original"
    assert "Not an independent origin" in rp["note"]
    article = by_url[article_url]
    assert article["support_scope"] == "identity"
    assert article["publication_when"] == "2024-03 (month)"
    article_text = " ".join(passage["text"] for passage in article["passages"])
    assert "V Ka 418/21" in article_text
    assert all("2024" not in item["when"] for item in case["items"])
    january = public_explorer(store, include_synthetic=False, date_from="2022-01-01", date_to="2022-01-31")
    assert january["counts"]["matched_arguments"] == 0
    november = public_explorer(store, include_synthetic=False, date_from="2021-11-01", date_to="2021-11-30")
    assert {row["argument"]["id"] for row in november["matched_rows"]} == {
        "pl_arg_legality",
        "pl_arg_proportionality",
    }
    proportionality = public_explorer(store, include_synthetic=False, label="Proportionality")
    assert {row["argument"]["id"] for row in proportionality["matched_rows"]} == {"pl_arg_proportionality"}
    assert proportionality["counts"]["real_cases"] == 1
    sample = json.loads((Path(__file__).resolve().parents[1] / "docs" / "public-export.sample.json").read_text())
    assert sample["schema_version"] == "1"
    assert sample["export_generated_at"] == "2026-10-10T01:06:38+00:00"
    assert sample["timeline_caption"] == "Latest approved event in this dataset."
    assert case["coverage"]["latest_documented_event"] == "2022-01-12 (day)"
    assert case["coverage"]["latest_documented_event_note"] == (
        "Latest approved event in this dataset. "
        "This is not a claim that it is the latest development in the case."
    )
    assert case["case"]["proceeding_note"].startswith("II K 296/20 is the trial case number")
    assert all(item["established"] is False for item in case["receptions"])
    assert len(brief["facts"]["developments"]) == 1
    assert brief["facts"]["developments"][0]["event_id"] == "pl_decision_appeal_2022-01-12"
    assert brief["facts"]["documented_reception"] == []
    assert {item["argument_id"] for item in brief["facts"]["unknown_reception"]} == {
        "pl_arg_legality",
        "pl_arg_proportionality",
    }
    assert all(item["remedy_note"].endswith("not an impact finding.") for item in brief["facts"]["engagement"])
    assert "Follow-up search coverage is not in the public record." in brief["facts"]["evidence_gaps"]
    assert "not a finding that implementation failed" in brief["facts"]["implementation_status"]
    walkthrough = public_explorer(_walkthrough(tmp_path), include_synthetic=True)
    assert "pl_arg_legality" not in _strings(walkthrough)
    assert walkthrough["synthetic_banner"]
    for marker in (
        "Wilmshurst",
        "Private comparison",
        "orzeczenia.ms.gov.pl",
        "tam_arg_breadth",
        "TVN24",
        "PRIVATE-SEARCH-NOTE",
        "Amnesty",
        "28 March 2024",
        "2024-03-28",
        "Historical analysis",
        "did not personally inspect",
        "did not retrieve",
        "V KK 430/22",
        "Supreme Court",
        "not part of the January 2022 approval",
        "pl_search_amnesty",
        "out_pl_acquit",
        "KPH",
        "rights_note",
        "observer_note",
        "unresolved_questions",
    ):
        assert marker not in blob, marker


def test_public_entry_cannot_reach_internal_review():
    source = inspect.getsource(public_app)
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
            imported.update(f"{node.module}.{alias.name}" for alias in node.names)
    forbidden_modules = {
        "advocacy_trace.app",
        "advocacy_trace.importing",
        "advocacy_trace.views",
        "advocacy_trace.research",
    }
    assert imported.isdisjoint(forbidden_modules)
    for token in (
        "public_preview",
        'audience="internal"',
        "audience='internal'",
        "review_queue",
        "require_search_provider",
        "read_pdf_excerpt",
        ".review(",
        "add_research_attempt",
    ):
        assert token not in source
    screen_source = inspect.getsource(demo_screens)
    assert "public_preview" not in screen_source
    assert 'audience="internal"' not in screen_source
    assert "audience='internal'" not in screen_source
    assert "research_attempts" not in screen_source


def test_public_app_screens_exclude_internal_controls(tmp_path, monkeypatch):
    monkeypatch.setenv("ADVOCACY_TRACE_DB", str(tmp_path / "demo.sqlite"))
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "advocacy_trace" / "public_app.py",
        default_timeout=60,
    )
    app.run()
    assert not app.exception
    text = _app_text(app)
    assert "Matched approved arguments: 2" in text
    assert "Real cases with an approved argument in this selection: 1" in text
    assert "does not approve or verify the case" in text
    assert "Lisa Davis" in text
    assert "Article 196 is not precise" in text
    assert "necessity and proportionality requirements" in text
    assert "2021-11 (month)" in text
    assert "trial-observation-report-poland-lgbt.pdf" in text
    assert "cfj.org/reports/poland-vs-elzbieta-podlesna" in text
    assert "On 12 January 2022 the Regional Court in Płock upheld the acquitting judgment" in text
    assert "Source publication date: 2022-01-13 (day)" in text
    assert "It is not the event date." in text
    assert "Support scope is identity and the reported result." in text
    assert "V Ka 418/21" in text
    assert "Wilmshurst" not in text
    assert "Private comparison" not in text
    assert "did not retrieve" not in text
    assert "V KK 430/22" not in text
    assert "Amnesty" not in text
    assert "Approve" not in text
    assert [radio.options for radio in app.sidebar.radio if radio.label == "Screen"] == [
        ["Argument Explorer", "Case Evidence", "Advocacy Learning Brief"]
    ]
    assert not any(button.label == "Approve" for button in app.button)

    app.sidebar.radio[1].set_value("Case Evidence").run()
    text = _app_text(app)
    assert "Court reception of the report is not established" in text
    assert "not acceptance and it is not rejection" in text
    assert "The public chronology is incomplete" in text
    assert "2022-01-12 (day)" in text
    assert "HFHR reported" in text
    assert "3 defendant-specific rows" in text
    assert "Latest approved event in this dataset" in text
    assert "not a claim that it is the latest development" in text
    assert "II K 296/20 is the trial case number" in text
    assert "No approved public record in this band." in text
    appeal = next(box for box in app.selectbox if box.label == "Chronology item")
    appeal.set_value("pl_decision_appeal_2022-01-12").run()
    text = _app_text(app)
    assert "Source quotation" in text
    assert "English translation of the source passage" in text
    assert "judgment itself was not retrieved" in text
    assert "https://hfhr.pl/aktualnosci/tecza-nie-obraza-wyrok-uniewinnienie" in text
    assert "Source publication date: 2024-03 (month)" in text
    assert "It is not the event date." in text
    assert "V KK 430/22" not in text
    assert "Supreme Court" not in text
    assert "did not retrieve" not in text
    assert "Amnesty" not in text
    assert "Wilmshurst" not in text
    assert not any(button.label == "Approve" for button in app.button)

    app.sidebar.radio[1].set_value("Argument Explorer").run()
    argument = next(box for box in app.sidebar.selectbox if box.label == "Argument")
    argument.set_value("Proportionality").run()
    text = _app_text(app)
    assert "Matched approved arguments: 1" in text
    assert "Real cases with an approved argument in this selection: 1" in text
    assert "necessity and proportionality requirements" in text
    assert "Article 196 is not precise" not in text
    argument.set_value("Any").run()

    app.sidebar.radio[1].set_value("Advocacy Learning Brief").run()
    text = _app_text(app)
    assert "Not a human-reviewed brief" in text
    assert "cannot support a general or cross-case conclusion" in text
    assert "not an impact finding" in text
    assert "2022-01-12 (day)" in text
    assert "Latest approved event in this dataset" in text
    assert "not a claim that it is the latest development" in text
    assert "HFHR reported" in text
    assert "judgment itself was not retrieved" in text
    assert "3 defendant-specific rows" in text
    assert "Amnesty" not in text
    assert "Article 196 is not precise" in text
    assert "Wilmshurst" not in text

    app.sidebar.radio[1].set_value("Argument Explorer").run()
    app.sidebar.radio[0].set_value("Synthetic walkthrough").run()
    from_box = next(box for box in app.sidebar.text_input if box.label == "From date")
    from_box.set_value("2023-05-01").run()
    to_box = next(box for box in app.sidebar.text_input if box.label == "To date")
    to_box.set_value("2023-05-31").run()
    text = _app_text(app)
    assert "Synthetic demonstration" in text
    assert "Matched approved arguments: 2" in text
    assert "Date unknown" in text
    assert "Article 196 is not precise" not in text
    assert "INTERNAL-PROPOSED" not in text

    app.sidebar.radio[1].set_value("Case Evidence").run()
    text = _app_text(app)
    assert "Relative timing unknown" in text
    assert "not proof that the timeline is complete" in text
    assert "Follow-up search coverage is not in the public record." in text
    appeal = next(box for box in app.selectbox if box.label == "Chronology item")
    appeal.set_value("out_chen_appeal").run()
    text = _app_text(app)
    assert "authenticity against an official host" in text
    assert "not a finding about how an authority received" in text

    app.sidebar.radio[1].set_value("Advocacy Learning Brief").run()
    text = _app_text(app)
    assert "Not a human-reviewed brief" in text
    assert "cannot support a general or cross-case conclusion" in text
    assert "not established findings" in text
    assert not any(button.label == "Approve" for button in app.button)


def _app_text(app) -> str:
    values = []
    for elements in (app.header, app.subheader, app.markdown, app.caption, app.text):
        values.extend(element.value for element in elements)
    return "\n".join(values)
