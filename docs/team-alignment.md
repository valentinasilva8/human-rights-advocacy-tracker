# Same page with the other TrialWatch work

Checked 9 October 2026 against two local exports of teammate notes. Those files are not in git. The notes describe work on [valentinasilva8/fairtrial-ai-hackathon](https://github.com/valentinasilva8/fairtrial-ai-hackathon), including pull request 11, and a lawyer-screen mockup for the Fatia and Haris case. This repository is Advocacy Trace. The source pipeline matches. The record of an argument, and the thing the screen is for, do not.

## Already the same

- The queue is CFJ's sitemap: 96 report pages, 94 PDFs with extractable text, about 47 graded freedom-of-expression trial reports. Thematic reports and ungraded trials stay out of that core count.
- Fetches wait 10 seconds. PDFs and full report text stay out of git. The year in an upload path is not the publication date.
- A web page is a summary. The argument, the grade line, and the citations are in the PDF.
- Keyword tags are rough. A paragraph can match "legality" from a word that is not a legality argument. A person confirms the tag.
- The analysis in a fairness report is the named expert's or the drafting partner's. It is not automatically what defense counsel argued, and the reports say it is not necessarily the Clooney Foundation's view.
- A grade is TrialWatch's fairness assessment of the trial. It is not the verdict and not the sentence.
- Later news is a lead. Match the defendant's full name. A surname match is unsafe. Bail is not an acquittal. A footnote is not an outcome. Another person's result is not this defendant's result. A person fills the confirmation.
- Wording already used on that side is the right wording: the outcome followed the work. The argument did not cause it.
- A sentence with no source is rejected. An authority named inside a report is "cited in the report" until someone reads the decision. An unsettled legal point stays unclaimed. The Fatia and Haris mockup already does this for Luhut's complaint.

## Not the same, and this is the shared rule

**Labels.** Their extractor merges legality with vagueness, and necessity with proportionality, and it also tags legitimate aim, overbreadth, criminal penalty, pretrial detention, and fair trial. Advocacy Trace keeps five headline labels, which overlap: Vagueness, Broadness, Legality, Necessity, Proportionality. Overbreadth is Broadness. A criminal-penalty sentence is Proportionality when the report is talking about severity. Legitimate aim, pretrial detention, fair trial, assembly, and discrimination stay `unmapped—review required` until the team decides to add a headline. Do not add one in the extractor.

**Outcomes.** Their sheet suggests good, not good, mixed, or unknown. Their own check marks several suggestions wrong or unclear: Poland may have been appealed, Altınel's acquittal was a different case, Manseri's "released" was the report, Thach Setha's sentence was cut off at "The Court acquitted Mr." Store a dated event instead: convicted, acquitted, appeal filed, appeal pending, charges struck out, released on bail, released after sentence credit. Unknown stays unknown. "Pending" is only pending as of the source's date.

**What the screen is for.** Their Saturday plan applies past TrialWatch arguments to current Indonesian ITE cases, ranks toward cases that "ended well," and drafts a combined argument or UN letter. Advocacy Trace answers a different question: what was argued, what response is documented, and what happened to the defendant afterward. It does not predict, it does not score success, and it does not carry over an earlier "likely barred / still prosecutable" classifier. A draft generator can sit on top of approved rows. Every sentence keeps a source tag. "What should happen" is text a lawyer edits. It is not a determination by the tool.

**Who argued.** Do not write "TrialWatch argued" as the default. Name the author on the report: ABA Center staff, Arthur Traldi, Alex Conte, Lisa Davis, Elizabeth Wilmshurst, Michael Hamilton. The first six reports read here are proposed clusters in [first-argument-clusters.md](first-argument-clusters.md). Three Cambodia Article 495 reports share a paragraph. That is one drafting pattern, not three independent authorities.

**Counts.** Count unique cases. A case with five tagged paragraphs is one case. Do not lead with "2 to 5 of 47 ended well." Show the similar cases, each with its dated outcome and its unknowns. Confirmed favorable endings can be marked on the row. They do not become a success rate and they do not hide the other cases.

## How the two pieces fit

| Their piece | Use it here as |
| --- | --- |
| Report index, grade line, 10-second fetch, PDF kept local | Already the queue. Do not commit the PDFs. |
| Keyword counts | A hint for which PDF to read next. Not an approved label. |
| News sentences, full-name match, `verified_by` | The outcome lead for a named defendant. Proposed until a person checks the page. |
| Poland acquittal plus a later "must now prepare" line | Matches the November 2021 report: acquittal on 2 March 2021, appeal not decided in that report. |
| Fatia and Haris mockup: green verified, blue from the report, amber check the primary | The same evidence ladder. Map green to an approved primary source, blue to the report alone, amber to a citation not yet opened. |
| Gemini connecting sentences | Allowed only as `ai_suggested` and `proposed`, and only where each claim has a page that contains it. |

Fatia and Haris can be added later as a proposed evidence record under these rules. The old Indonesian ITE verdict style does not come with it.

## What we will not merge in

- The good / not good / mixed column, as a stored outcome.
- A search page that shows only cases that ended well.
- Institutional attribution to TrialWatch when the report names a partner or an expert.
- Approval of a keyword tag without the passage, the page, the author, and a person.
