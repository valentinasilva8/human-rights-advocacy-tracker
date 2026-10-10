# Public data contract

This is the current approved-only payload for a frontend. It is `EvidenceStore.public_export(include_synthetic=False)`. The sample is [public-export.sample.json](public-export.sample.json). That file is a current export of the approved records. The handoff is [frontend-handoff.md](frontend-handoff.md).

Do not treat this file as a request to another agent, and do not change a frontend framework from it.

## Shape

- `schema_version`: `"1"`
- `export_generated_at`: when the export was generated. Not an event date and not an approval time.
- `timeline_caption`: “Latest approved event in this dataset.”
- `time_fields`: the distinctions among generation time, event date, publication date, and approval time.

## What the export contains now

- `real_case_count`: 1
- `approved_argument_count`: 2
- `cases`: `case_poland` only
- `arguments`: `pl_arg_legality` and `pl_arg_proportionality`
- `outcome_events`: `out_pl_appeal_podlesna`, `out_pl_appeal_prus`, and `out_pl_appeal_gzyra`, one shared `decision_id` `pl_decision_appeal_2022-01-12`
- `receptions`: empty
- `sources`: the fairness report, HFHR, the 13 January 2022 rp.pl article, OKO.press, and the ARTICLE 19 brief
- `interventions`: the Poland fairness-report intervention
- `includes_full_documents`: false

Each outcome carries `evidence_basis`, `evidence_basis_caption`, `public_limitation`, and `source_links`. A source link’s `publication_date` is the source’s publication date. The outcome’s `event_date` is 12 January 2022.

Reception of Lisa Davis’s report stays proposed, so it is not in this export. An empty reception list is not a finding that the court ignored the arguments. The proposed 28 March 2024 records are not in this export. “Latest approved event in this dataset” is not a claim that the timeline is current.

## Provenance on the approved outcome

HFHR is the organization account of the approved claim. Its link provenance is `unknown` and its scope is `whole_claim`. It is not an independent corroboration of its own sentence.

The 13 January 2022 rp.pl article is `derived_from_shared_original`. It draws on HFHR. It is not an independent origin. It is a different article from the 28 March 2024 rp.pl report, which is not in this export.

OKO.press is provenance `independent` and `support_scope` `identity_and_reported_result`. It supports the defendants’ identity and the reported result that the appellate court upheld the acquittal on 12 January 2022. It does not corroborate that HFHR reported the result, or every other sentence on the outcome record. `independent_support_count` is 0.

ARTICLE 19 is provenance `unknown` and scope `identity`. Footnote 1 is the only attribution for V Ka 418/21.

## Rules

Approved, non-sensitive arguments, outcomes, and receptions only. AI-suggested arguments are left out. Synthetic cases are left out when `include_synthetic` is false. `unresolved_questions`, `observer_note`, and `untrusted_text` are removed. `research_attempts` are omitted. Approval does not authorize redistribution of a source PDF.

`real_case_count` counts non-synthetic cases that have at least one approved, non-sensitive argument or outcome in the export. It is not a count of verified cases. `approved_argument_count` counts approved non-synthetic arguments, excluding AI suggestions.

`created_at` on a case is the time that local database row was inserted. It is not an event date or a publication date. The sample leaves it blank so the file does not treat one insert time as part of the evidence.

Participants are not a top-level key. The case title names the three defendants. HFHR’s amicus role is stored on the case, and it appears in the appeal review preview, not as a separate export key.

## Explorer

When the filter matches both approved arguments (no label filter, country Poland or any country), the public explorer reports one real case and two approved arguments. A Proportionality-only filter matches `pl_arg_proportionality` alone. The outcome summary for that case uses “Latest approved event in this dataset.” The unapproved 2024 rows stay out of that summary because they are proposed and `Unverified`.
