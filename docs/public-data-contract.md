# Public data contract

This is the current approved-only payload for a frontend. It is `EvidenceStore.public_export(include_synthetic=False)`. The sample is [public-export.sample.json](public-export.sample.json). That file is the export itself. It is not a sketch of a later schema, and it does not include the appeal outcome.

Do not treat this file as a request to another agent, and do not change a frontend framework from it.

## What the export contains now

- `real_case_count`: 1
- `approved_argument_count`: 2
- `cases`: `case_poland` only
- `arguments`: `pl_arg_legality` and `pl_arg_proportionality`
- `outcome_events`: `out_pl_appeal_podlesna`, `out_pl_appeal_prus`, and `out_pl_appeal_gzyra`, one shared `decision_id` `pl_decision_appeal_2022-01-12`
- `receptions`: empty
- `sources`: the fairness report, HFHR, rp.pl, OKO.press, and the ARTICLE 19 brief
- `interventions`: the Poland fairness-report intervention
- `includes_full_documents`: false

Reception of Lisa Davis’s report stays proposed, so it is not in this export. An empty reception list is not a finding that the court ignored the arguments. The 28 March 2024 research lead is not in this export. The January 2022 outcome is not a statement that the timeline is complete.

## Rules

Approved, non-sensitive arguments, outcomes, and receptions only. AI-suggested arguments are left out. Synthetic cases are left out when `include_synthetic` is false. `unresolved_questions`, `observer_note`, and `untrusted_text` are removed. `research_attempts` are omitted. Approval does not authorize redistribution of a source PDF.

`real_case_count` counts non-synthetic cases that have at least one approved, non-sensitive argument or outcome in the export. It is not a count of verified cases. `approved_argument_count` counts approved non-synthetic arguments, excluding AI suggestions.

`created_at` on a case is the time that local database row was inserted. It is not an event date or a publication date. The sample leaves it blank so the file does not treat one insert time as part of the evidence.

Participants are not a top-level key. The case title names the three defendants. HFHR’s amicus role is stored on the case, and it appears in the appeal review preview, not in this approved-only export.

## Explorer

When the filter matches both approved arguments (no label filter, country Poland or any country), the public explorer reports one real case and two approved arguments. A Proportionality-only filter matches `pl_arg_proportionality` alone. The outcome summary for that case lists the one approved January 2022 decision. Its statement says an incomplete list is not a finding that no other development occurred.

## Separate from this contract

`appeal_outcome_preview` reads the stored appeal display and does not approve anything. The sample file is the approved-only export.
