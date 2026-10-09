# Phased implementation plan

The phases below follow the hackathon brief. This repository completes the local scaffold and one synthetic end-to-end chain. It does not import real TrialWatch documents.

## Phase 1 — Source feasibility

Done as a coverage note, not as a dataset. See [source-reuse-policy.md](source-reuse-policy.md).

`https://cfj.org/trialwatch/trials/` is a category hub. Public sitemaps expose report, news, story, topic, and country URLs. A sampled report page has a title, a short blurb, a publication date, and a PDF link. The argument text is in the PDF. News posts are often announcements. No public terms page was found that grants republication. Real cases stay out of the repository until one evidence chain is chosen and reviewed, and until reuse is clearer.

## Phase 2 — Classification guide

The annotation guide is in [annotation-guide.md](annotation-guide.md). It is flagged for legal-mentor review. The five labels are not expanded in this version.

## Phase 3 — One end-to-end case

Implemented with a fictional record, `Exampleland v. A. Rivera`. It has a TrialWatch proportionality argument with a page citation, a separately sourced later outcome, a reception record that is not treated as acceptance, and a human review action. The next real chain should replace this only after mentor review of the guide and a publication check.

## Phase 4 — Assisted extraction

Not started. Structured model output, when added, must quote only passages that exist in the source and must land in the review queue as proposed records. Retrieved text is data, never an instruction.

## Phase 5 — Outcome research

Not started. Manual file import works. Automated search is an empty adapter that reports a missing credential instead of calling a network service. Duplicate articles and mismatched proceedings are represented in the data model.

## Phase 6 — Argument comparison

The explorer filters reviewed records and shows unique-case counts, unknown outcomes, and synthetic exclusions. The learning brief is editable and is not sent.

## Phase 7 — Demo and documentation

The demo runs from the committed synthetic fixture and needs no live API. Six to ten reviewed real cases are not in this version. Known gaps are listed in the README and the source policy.
