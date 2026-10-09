# Evaluation plan

## What automated tests check

`pytest` checks the evidence rules the store can enforce:

- An approved argument has a passage, a location, a source, and at least one label.
- An approved outcome has a supporting source link and is not unverified.
- One case can hold several arguments, and case counts use unique proceedings.
- A described defense argument is not stored as TrialWatch's argument.
- A recital is not stored as acceptance.
- An intervention dated after a verdict does not count as preceding it.
- A publication date is not written as the event date.
- No events, or only "No verified recent update," stays unknown.
- An appeal does not delete the earlier decision.
- Two proceedings for one person stay two cases.
- A duplicate article does not increase the independent-source count.
- Sensitive rows are left out of the public export.
- Unverified and synthetic rows are left out of verified real-case summaries.
- Untrusted source text cannot approve a record.
- Missing search credentials, a failed download, and a file that is not a readable PDF raise an explicit error.

These tests do not measure legal accuracy.

## What a second reviewer should check

On a small set of real extractions, after documents are imported locally and not before, a second reviewer should mark each item correct or incorrect for:

- argument label, including overlap and unmapped items
- attribution (TrialWatch, partner, counsel described in a report, authority, announcement-only, AI suggestion)
- the quotation and the page or paragraph location
- the event type, the event date, and the defendant it concerns

Report the counts that reviewer actually marked. Do not publish an estimated accuracy, a confidence score, or a success rate.

No second-reviewer set exists in this version. Actual classification accuracy on real cases is **not measured**.

## What would block expanding the dataset

- The annotation guide has not had legal-mentor review.
- Reuse permission for CFJ documents is unresolved.
- A candidate case has an argument source but no separate look at later developments. That case can still be included, with outcome and reception left unknown.
- A record would identify a sensitive matter and the publication review is unfinished.
