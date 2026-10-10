# Implementation plan

Updated 9 October 2026. This is the working plan for the evidence tracker. It replaces the earlier phase list that named Kong Raiya as the next real chain and treated comparison as a current screen.

The product question is: what was argued, by whom and through which intervention; what documented response exists; and what happened afterward. The tracker looks for patterns and gaps. It does not claim that an argument caused an outcome.

Live alignment with the Google Doc tab `t.avvzu4g5dzi9` is pending. That tab was not readable. The two uploaded PDFs are not treated as a current copy of it.

## Where this slice stands

The safeguards in the current build are in the store, the explorer, the case screen, and `public_export`. Valentina Silva approved `pl_arg_legality` and `pl_arg_proportionality` on 10 October 2026. On the same date she authorized approval of the three Poland appeal rows as one HFHR organization account, labeled `Single-source report`. Reception of the report stays proposed. A 28 March 2024 Supreme Court report is a separate research lead and is not approved. The current approved-only export is [public-data-contract.md](public-data-contract.md) and [public-export.sample.json](public-export.sample.json). The search log is [research-log.md](research-log.md). The packet is [review-packet.md](review-packet.md).

## What is already in the repository

A synthetic chain, Exampleland v. A. Rivera, exercises approval, chronology, separate proceedings, and duplicate articles. The database is created with `CREATE TABLE IF NOT EXISTS` and is migrated in place. It is not deleted and reseeded to add columns. Real fairness-report PDFs are not in git. Proposed clusters from six reports are notes in [first-argument-clusters.md](first-argument-clusters.md), not approved rows.

## Current build

These steps run together. Research does not wait for the last code step. Real rows from research stay proposed until a person approves them.

1. **Product language and counts.** The brief, the explorer, and the learning brief use the question above. A count says what it counts. One approved argument is not a verified case.
2. **Attribution.** The default explorer shows approved named-expert and partner analysis with author, affiliation, role, and disclaimer. Affiliation alone is not institutional TrialWatch attribution. Defense submissions and authority findings stay distinct. Ingestion cannot grant itself a TrialWatch role or a support check.
3. **Export and public views.** Approval and sensitivity apply to each argument, outcome, and reception in the explorer, the case screen, and `public_export`. Proposed rows, reviewer notes, and research notes stay on the review screen. Approval does not permit republication of a PDF.
4. **Fields the workflow needs.** Principle, application, and remedy (or “not stated”). Disclaimer status distinguishes “not stated in source” from “not yet checked.” A human support check, with reviewer, time, claim, and evidence. Changing claim text, attribution, or supporting evidence returns the row to proposed. Reception statuses separate “not yet retrieved,” “sought but unavailable,” “reasoning insufficient,” and “not addressed in the available decision.” Explicit reception names the authority’s own document or is labeled a secondary account. Evidence links record duplication, shared underlying reporting, same organization, independent corroboration, or unknown. Unknown independence does not add to the support count.
5. **Bounded research.** About 30 minutes, read-only, on Poland v. Podleśna, Prus, and Gzyra-Iskandar and on Hong Kong SAR v. Tam Tak-chi. Record queries and results. “Not found in this search” is not “does not exist.” Prefer a dated intervention and a later development in the same proceeding. A verdict that predates the report is not a response to that report.

## After several reviewed cases

See [cross-case-roadmap.md](cross-case-roadmap.md). Comparison across cases, and any lawyer-facing drafting, wait until several person-approved cases exist. They are not part of this build.

## Not in this build

Bulk PDF ingestion. A draft generator. The Indonesia reform classifier. Success scores or “winning arguments.” A new deployment or a public upload of source files.
