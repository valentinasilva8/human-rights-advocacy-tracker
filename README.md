# Advocacy Trace

Advocacy Trace is a local prototype for reading freedom-of-expression advocacy. It links an argument, the document that made it, any later events in the defendant's case, and the evidence for each of those steps.

It was built for the FAIRTRIAL / TrialWatch x AI Hackathon, Track 3 (Advocacy and Impact). It is an independent hackathon project. It is not endorsed by the Clooney Foundation for Justice, TrialWatch, or Columbia Law School, and it is not an official product of those organizations.

The tool does not give legal advice, decide whether a prosecution was lawful, or estimate whether an argument "worked."

## The question it answers

Show cases where TrialWatch advanced a proportionality argument. What exactly was argued, what response is documented, and what happened to the defendant afterward?

Labels in use: Vagueness, Broadness, Legality, Necessity, and Proportionality. They overlap. Other points stay `unmapped—review required`.

## Setup

Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m advocacy_trace.seed
streamlit run advocacy_trace/app.py
pytest -q
```

No API key is required. Optional variable names are listed in `.env.example`. The demo database is created at `data/demo.sqlite` and is gitignored.

## How to use it

Three screens:

- **Argument Explorer.** Filter reviewed arguments. Unique cases are counted once. Missing reception or a missing later event is shown as a gap. The verified real-case count stays at zero while the only records are synthetic.
- **Case Evidence.** Proceeding, interventions, cited passages, outcome events, reception, last-verified date, and open questions.
- **Review and Learning.** Approve, reject, or edit a proposed row. Each action is stored. The learning brief is an editable draft. The app does not send it.

You can attach a local file on the review screen. A file that is not a PDF, a failed download, or a missing search credential produces an explicit error and does not invent a record. Automated search is not configured.

## Data workflow

1. Identify the proceeding and the defendant.
2. Import the document that contains the argument (a fairness report, brief, or submission). An announcement alone is labeled as an announcement.
3. Record the passage, where it sits in the document, the author, and one or more labels.
4. Separately import later sources for what happened afterward.
5. Record argument reception only where a source shows how an authority dealt with that argument.
6. A person approves the row before it appears in the explorer.

Publication date, event date, retrieval date, and last-verified date are stored separately. Unknown dates stay unknown.

The committed example is fictional: Exampleland v. A. Rivera. It is marked synthetic and is excluded from real-case metrics. Do not add real reports or articles to git. See [docs/source-reuse-policy.md](docs/source-reuse-policy.md).

A separate index lists the public TrialWatch report pages, including 47 graded freedom-of-expression reports: [docs/trialwatch-report-index.md](docs/trialwatch-report-index.md). Those rows are links and fairness grades, not extracted arguments. How that index should and should not be used is in [docs/argument-bank-assessment.md](docs/argument-bank-assessment.md). Proposed clusters from the first six reports are in [docs/first-argument-clusters.md](docs/first-argument-clusters.md). They are not approved and they are not in the demo database.

## TrialWatch pages

`https://cfj.org/trialwatch/trials/` can be read as a category index. It is not a structured case database. Report pages generally link a PDF, and the argument is in that PDF. Scraping the index does not establish later outcomes or whether an authority accepted an argument. Details, robots rules, and the reuse gap are in the source policy.

## Limits

- The annotation guide still needs legal-mentor review.
- No real case has been imported, and no second reviewer has scored classifications. Accuracy on real cases is not measured.
- A favorable event is not evidence that an argument was accepted, and an accepted argument is not evidence that advocacy caused the event.
- Comparisons in the brief are descriptive counts. They include the denominator, unknowns, and the fact that the demo set is synthetic.
- Sensitive rows are omitted from the public export function. Do not commit them in order to hide them in the interface.

## Documents

- [Product brief](docs/product-brief.md)
- [Phased plan](docs/implementation-plan.md)
- [Annotation guide](docs/annotation-guide.md)
- [Data dictionary](docs/data-dictionary.md)
- [Source and reuse policy](docs/source-reuse-policy.md)
- [Evaluation plan](docs/evaluation-plan.md)
- [TrialWatch report index](docs/trialwatch-report-index.md)
- [Argument bank assessment](docs/argument-bank-assessment.md)
- [First argument clusters](docs/first-argument-clusters.md)
