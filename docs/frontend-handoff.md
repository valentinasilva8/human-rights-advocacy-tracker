# Frontend handoff

This is the approved-only payload a frontend can read. It does not change a frontend framework, and it does not ask another agent to deploy.

## Where the records are

- Branch: `cursor/evidence-review-safeguards-5c2e`
- Existing pull request: https://github.com/valentinasilva8/human-rights-advocacy-tracker/pull/5
- The commit SHA is the tip of that branch after this handoff. The approval commit that preceded it is `de0656ab3737c2bdfc78d2c15b417d85ca26c97d`.

## The sample is the export

[public-export.sample.json](public-export.sample.json) was generated from `EvidenceStore.public_export(include_synthetic=False)` after the recorded approvals were applied. It is the current approved records. It is not illustrative sample data.

- `schema_version` is `"1"`. That identifies this export shape.
- `export_generated_at` is when this file was generated. In this file that time is `2026-10-10T01:06:38+00:00`.
- That generation time is not an event date. The approved event date is `2022-01-12`.
- It is not an approval time. The appeal approval time, stored on the review action and not copied into this file, is `2026-10-10T00:48:39+00:00`.
- `time_fields` states those distinctions in the export itself.
- `timeline_caption` is “Latest approved event in this dataset.” That caption is not a claim that the case timeline is current, and it is not the phrase “latest case development.”

`created_at` on the case is blank in the sample because it is the local insert time of a database row. It is not evidence.

## What the export contains

- One real case: `case_poland`. `real_case_count` is 1.
- Two approved arguments: `pl_arg_legality` and `pl_arg_proportionality`. `approved_argument_count` is 2.
- Three defendant-specific outcome rows: `out_pl_appeal_podlesna`, `out_pl_appeal_prus`, and `out_pl_appeal_gzyra`.
- Those three rows share one decision, `pl_decision_appeal_2022-01-12`. They are not three decisions.
- `receptions` is empty. There are no approved receptions.

Each public outcome includes `evidence_basis` (`organization_account`), `evidence_basis_caption`, `public_limitation`, and `source_links`. Each source link has the source URL, publication date, relationship, provenance, and `support_scope`.

## What stays out

Proposed rows, including the 2024 Supreme Court records, are not in the export. Sensitive cases, `unresolved_questions`, `observer_note`, `untrusted_text`, and `research_attempts` are not in the export. The Amnesty Slovakia URL, the KPH URL, and the 28 March 2024 rp.pl URL are not in the export. Approval does not include the source PDF.

The contract detail is [public-data-contract.md](public-data-contract.md).
