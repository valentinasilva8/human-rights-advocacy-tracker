# Data dictionary

SQLite tables in `advocacy_trace`. Identifiers are text. Dates are text plus a precision of `day` (`YYYY-MM-DD`), `month` (`YYYY-MM`), `year` (`YYYY`), or `unknown`. Unknown precision stores no date value. Publication date, event date, retrieval date, and last-verified date are different columns.

`sensitive` and `is_synthetic` are booleans. Synthetic rows are excluded from real-case summaries. Sensitive rows are excluded from the public export.

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
| unresolved_questions | Open questions shown on the case screen |

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

`author_actor` is who made the argument. A `defense_counsel_described` row cannot name TrialWatch as the author. A `trialwatch_argument` row must name TrialWatch.

`passage` and `location_ref` are required before approval. `review_status` is `proposed`, `approved`, or `rejected`.

## argument_labels

Zero or more labels per argument. Allowed values are `Vagueness`, `Broadness`, `Legality`, `Necessity`, `Proportionality`, and `unmapped—review required`. Approval requires at least one.

## outcome_events

A dated event for one defendant. Adding an appeal does not delete the earlier event. `supersedes_event_id` is a link, not an erasure.

`event_type` is one of: Charges filed, Charges amended, Charges withdrawn, Charges dismissed, Conviction, Acquittal, Appeal filed, Appeal decided, Release, Continued detention, Sentence modification, Retrial ordered, Compensation ordered, Compensation received, Continuing restrictions, New proceeding, No verified recent update.

`evidence_label` is one of: Primary-source supported, Corroborated by independent sources, Single-source report, Conflicting, Unverified.

`No verified recent update`, an unverified label, or an empty event list all summarize as **unknown**. They do not become "still detained," "ongoing," or "advocacy failed."

The store will not accept a call that declares the event date to be the source's publication date.

## reception_observations

How an authority dealt with one argument, if a source supports that observation.

`status` is one of: Explicitly accepted, Partially accepted, Explicitly rejected, Discussed without clear resolution, Not addressed in the available decision, Decision unavailable / insufficient evidence, Not applicable.

`is_recital` marks a passage that only recounts the argument. A recital cannot be stored as Explicitly accepted or Partially accepted.

## evidence_links

Connects a source to an argument, outcome event, or reception. `relationship` is `supports`, `quotes`, `duplicates`, or `conflicts`. A `duplicates` link is not independent corroboration. Independent support is counted by the original source, so two articles that copy one press release count once.

## review_actions

Append-only. `action` is `approve`, `reject`, or `edit`. Each row stores the reviewer, the note, the previous status, and the new status. Nothing in source text can insert this row by itself.
