# What to take from the argument bank

The notes in the other repository's argument-bank pipeline, and the open outcomes pull request, were checked against Advocacy Trace. The useful part is the map of public reports. The keyword tags and the "ended well" suggestion are not records this project can approve.

Source repository: [valentinasilva8/fairtrial-ai-hackathon](https://github.com/valentinasilva8/fairtrial-ai-hackathon). Report index: [trialwatch-report-index.md](trialwatch-report-index.md). Outcomes pull request: [fairtrial-ai-hackathon#11](https://github.com/valentinasilva8/fairtrial-ai-hackathon/pull/11).

## Use

- **96 report pages, 94 with a PDF, 90 distinct reports.** This matches the sitemap count already checked here. Two pages have no PDF. Six entries are translations or summaries and must not be counted as extra cases.
- **47 graded reports are marked as freedom-of-expression analyses.** That is the working queue. Cambodia v. Kong Raiya is in it.
- **Grades are stored in the other project with the sentence they were read from.** If a grade is copied here, keep that sentence. A grade of D or F is TrialWatch's fairness assessment of the trial. It is not the sentence imposed, and it is not reception of a proportionality argument.
- **Raw PDFs and verbatim tagged paragraphs stay untracked.** The other project already treats CFJ's PDFs as not republished. This repository does the same.
- **Downloads wait 10 seconds,** which matches `robots.txt`. A future fetcher in this repo, if reuse is accepted, should do the same and should follow linked PDFs rather than the trials hub.
- **Later news can suggest an outcome sentence and a link.** Pull request 11 matches on the full defendant name, skips bail releases and footnote citations, and counts an outcome only after a person fills the label, the source URL, and their name. The wording there is the right one: the outcome followed the work. It does not say the argument caused it.

## Do not import as approved data

- **Keyword categories are not these five labels.** The other pipeline tags `legality_vagueness`, `legitimate_aim`, `necessity_proportionality`, `overbreadth`, `pretrial_detention`, and `fair_trial` when a word appears. That over-tags. On the Kong Raiya PDF, "vague pronouncements" describes the prosecution's evidence, which is not a vagueness argument. Necessity and proportionality are separate reasons in the same report. Advocacy Trace keeps Vagueness, Broadness, Legality, Necessity, Proportionality, and `unmapped—review required`.
- **A tagged paragraph is not yet an argument record.** An approved argument still needs the author, a faithful summary, the reasons, the passage, and a page or paragraph. Partner drafting has to stay visible. The Kong Raiya report says ABA Center for Human Rights staff helped draft it and that the views are not necessarily those of the Clooney Foundation for Justice.
- **`suggested_label` of good, not good, or mixed is not an outcome.** The latest keyword can hide an earlier conviction behind a later release. This project stores dated events. A conviction, an appeal, a suspended sentence, a release, and a UN opinion stay separate. Unknown stays unknown.
- **The year in a CFJ upload path is not the publication date and not the event date.**

## How to move forward

1. Work the 47-report queue one PDF at a time. Do not download all 94 into this repository.
2. First real chain: Cambodia v. Kong Raiya. The PDF is already readable. Four proposed arguments are drafted in the conversation of 9 October 2026 (legality and vagueness of Article 495; breadth, necessity, and proportionality of that article; necessity and proportionality of this prosecution; breadth and proportionality of the Facebook ban). They are partner arguments, not TrialWatch's own wording. The June 2020 conviction is described in the report, which was published later, so the report does not explain that conviction. Reception, on the report's account, is that the judgment did not address the expression defense. That stays a single-source account until the judgment is read. Anything after November 2020 is unknown until a later source is confirmed.
3. Put that chain in the review queue as proposed rows. Approve only after a person checks the passage against the PDF. Leave the PDF out of git.
4. Use news posts only to propose outcome sentences for that same defendant, with the link beside the sentence. A person confirms before the explorer treats the event as verified.
5. Leave the other project's stress-test grades and "likely barred" style verdicts out of this product.
