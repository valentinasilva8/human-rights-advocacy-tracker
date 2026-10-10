# Public data contract

This is the current approved-only payload for a frontend. It is `EvidenceStore.public_export(include_synthetic=False)`. The sample is [public-export.sample.json](public-export.sample.json). That file is the export itself. It is not a sketch of a later schema, and it does not include the appeal outcome.

Do not treat this file as a request to another agent, and do not change a frontend framework from it.

## What the export contains now

- `real_case_count`: 1
- `approved_argument_count`: 2
- `cases`: `case_poland` only
- `arguments`: `pl_arg_legality` and `pl_arg_proportionality`
- `outcome_events`: empty
- `receptions`: empty
- `sources`: the fairness-report source for those two arguments
- `interventions`: the Poland fairness-report intervention
- `includes_full_documents`: false

The Poland appeal rows are still proposed. They are not in this export. Reception of Lisa Davis’s report is still proposed, so it is not in this export either. An empty reception list is not a finding that the court ignored the arguments.

## Rules

Approved, non-sensitive arguments, outcomes, and receptions only. AI-suggested arguments are left out. Synthetic cases are left out when `include_synthetic` is false. `unresolved_questions`, `observer_note`, and `untrusted_text` are removed. `research_attempts` are omitted. Approval does not authorize redistribution of a source PDF.

`real_case_count` counts non-synthetic cases that have at least one approved, non-sensitive argument or outcome in the export. It is not a count of verified cases. `approved_argument_count` counts approved non-synthetic arguments, excluding AI suggestions.

`created_at` on a case is the time that local database row was inserted. It is not an event date or a publication date. The sample leaves it blank so the file does not treat one insert time as part of the evidence.

Participants are not a top-level key. The case title names the three defendants. HFHR’s amicus role is stored on the case, and it appears in the appeal review preview, not in this approved-only export.

## Explorer

When the filter matches both approved arguments (no label filter, country Poland or any country), the public explorer reports one real case and two approved arguments. A Proportionality-only filter matches `pl_arg_proportionality` alone. The live outcome summary for that case stays unknown, because the appeal rows are proposed and Unverified.

## Separate from this contract

`appeal_outcome_preview` shows how the reported appeal would read beside the two approved arguments if those outcome rows were later approved. That function does not approve them, and its result is not this export.
