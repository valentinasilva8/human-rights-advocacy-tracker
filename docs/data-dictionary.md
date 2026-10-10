# Data dictionary

SQLite tables in `advocacy_trace`. Identifiers are text. Dates are text plus a precision of `day` (`YYYY-MM-DD`), `month` (`YYYY-MM`), `year` (`YYYY`), or `unknown`. Unknown precision stores no date value. Publication date, event date, retrieval date, and last-verified date are different columns.

`sensitive` and `is_synthetic` are booleans. Synthetic rows are excluded from real-case summaries. Sensitive rows, proposed rows, reviewer notes, and research notes are excluded from public screens and from the public export. Approval does not include the source file.

## cases

One proceeding. A person can appear in more than one case. Cases are not merged because they share a defendant.

| Column | Meaning |
| --- | --- |
| id, title | Stable id and human title |
| country, court, case_number, charges | Proceeding identity. Empty means unknown |
| proceeding_type, procedural_stage, finality | Stage and finality. Not a success label |
| sensitive | Restricted from public export |
| is_synthetic | Fictional demonstration row |
| opened_on, opened_on_precision | When the proceeding opened, if known |
| last_verified_on, last_verified_on_precision | When a person last checked the record |
| unresolved_questions | Open questions. Shown on the internal review screen. Omitted from public views and from the public export |

## participants and case_participants

A participant is a person or organization independent of any one case. `case_participants.role_in_case` is the role in that proceeding, such as `defendant`.

## sources

A document or page. `document_type` is one of `fairness_report`, `amicus`, `submission`, `announcement`, `judgment`, `news`, `un_opinion`, `other`.

`publication_date` is when the source was published. It is not the date of the event the source describes. `duplicate_of_source_id` points at the earlier source when this one repeats it. `fingerprint` and `extraction_version` mark a specific capture so a later text change does not silently keep an old citation. `untrusted_text` is stored as data and is omitted from the public export.

## interventions

A dated act by an actor in a case: `fairness_report`, `amicus`, `submission`, `monitoring`, `statement`, or `announcement`. `attribution_basis` records how authorship is known, such as `document_authored` or `described_in_report`.

## arguments

One argument advanced or described in a source.

`attribution_role` is one of:

- `trialwatch_argument`
- `partner_argument`
- `defense_counsel_described`
- `authority_finding`
- `announcement_only`
- `ai_suggested`

`author_actor` is who made the argument. A `defense_counsel_described` row cannot name TrialWatch as the author. A `trialwatch_argument` row is institutional and must name TrialWatch. A named expert stays a `partner_argument` under their own name. Affiliation does not change that role.

`institutional_affiliation` is stored separately. `disclaimer_status` is `not_yet_checked`, `not_stated_in_source`, or `stated`. `stated` requires `disclaimer_text` from the source. Do not invent a disclaimer to fill `not_yet_checked`.

`principle`, `application`, and `remedy_requested` are required before approval. The text `not stated` is a real value when the source is silent.

`claim_supported` is set only by a human approval that records the check. A quotation and a page are not enough. Untrusted extraction cannot set it. If the claim, attribution, or supporting evidence changes after approval, the row returns to `proposed` and `claim_supported` is cleared.

`passage` and `location_ref` are required before approval. `review_status` is `proposed`, `approved`, or `rejected`.

`public_limitation` is displayed beside an approved claim. `evidence_basis` says what kind of source supports it. Neither field is a private reviewer note.

## argument_labels

Zero or more labels per argument. Allowed values are `Vagueness`, `Broadness`, `Legality`, `Necessity`, `Proportionality`, and `unmapped—review required`. Approval requires at least one.

## outcome_events

A dated event for one defendant. Adding an appeal does not delete the earlier event. `supersedes_event_id` is a link, not an erasure.

`event_type` is one of: Charges filed, Charges amended, Charges withdrawn, Charges dismissed, Conviction, Acquittal, Appeal filed, Appeal decided, Release, Continued detention, Sentence imposed, Sentence modification, Retrial ordered, Compensation ordered, Compensation received, Continuing restrictions, New proceeding, No verified recent update.

`Sentence imposed` is the original sentence. `Sentence modification` is a later change to a sentence already imposed. An original sentence is not stored as a modification because the list used to lack the first type.

`decision_id` groups defendant-specific rows that come from one decision. Counting defendants, proceedings, decisions, and interventions stays separate from the outcome-row count.

`evidence_basis` is one of: `not_yet_established`, `author_document`, `authenticated_judgment`, `organization_account`, `official_press_summary`, `unauthenticated_judgment_copy`, `response_not_established`. It is shown with the claim. It does not replace `evidence_label`. An organization account can stay `Unverified`. Zero independent origins is not zero evidence.

`public_limitation` is the evidence limit that stays beside the claim in a public view. It is not a reviewer note. `observer_note`, `unresolved_questions`, and `research_attempts` stay internal.

`evidence_label` is one of: Primary-source supported, Corroborated by independent sources, Single-source report, Conflicting, Unverified.

`No verified recent update`, an unverified label, or an empty event list all summarize as **unknown**. They do not become "still detained," "ongoing," or "advocacy failed."

The store will not accept a call that declares the event date to be the source's publication date.

## reception_observations

How an authority dealt with one argument, if a source supports that observation.

`status` is one of: Explicitly accepted, Partially accepted, Explicitly rejected, Discussed without clear resolution, Not addressed in the available decision, Decision not yet retrieved, Decision sought but unavailable, Document obtained but reasoning insufficient, Decision unavailable / insufficient evidence, Not applicable.

`account_type` is `not_yet_established`, `authority_document`, or `secondary_account`. An explicit response needs the authority's own document, or `secondary_account` when the record is someone else's report of it. A court judgment is the right document for court reception. Another authority can be documented by that authority's own document.

`reasoning_checked` is a reviewer's check of the reasoning. It is required before approving “Not addressed in the available decision,” an explicit response, or “Document obtained but reasoning insufficient.” “Decision not yet retrieved” and “Decision sought but unavailable” mean the decision's reasoning is not in hand. They are not findings that nothing exists.

`public_limitation` and `evidence_basis` on a reception use the same vocabularies as on an outcome. A dismissal quotation belongs on the outcome. It is not, by itself, reception of an argument. `response_not_established` is not a public statement that the court ignored the argument.

`is_recital` marks a passage that only recounts the argument. A recital cannot be stored as Explicitly accepted or Partially accepted.

## evidence_links

Connects a source to an argument, outcome event, or reception. `relationship` is `supports`, `quotes`, `duplicates`, or `conflicts`.

`provenance` is `unknown`, `duplicate_copy`, `derived_from_shared_original`, `same_organization_distinct`, or `independent`. The support count uses only `independent` origins for that claim. A selected independent flag does not raise the count. Unknown provenance stays unknown. Two documents from one organization can both be kept; they are not two independent origins. A duplicate copy counts once, with the original.

## review_actions

Append-only. `action` is `approve`, `reject`, or `edit`. Each row stores the reviewer, the time, the note, the previous status, the new status, the claim text, the evidence location, and whether the support check was made. `is_simulated` marks the fictional reviewer `synthetic-reviewer`. Nothing in source text can insert this row by itself.

## research_attempts

One search: query, place, date, and result. A result of not found in this search is not a finding that a document does not exist. These rows are internal. They are omitted from public views and from `public_export`.
