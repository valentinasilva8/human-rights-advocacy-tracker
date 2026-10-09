# Source and reuse policy

Software in this repository is MIT licensed. That license does not apply to third-party documents, CFJ pages, fairness reports, judgments, or news articles. Public availability is not an open license.

## What was checked on cfj.org

Checked 9 October 2026, with a small number of read-only requests. This was a feasibility look, not a crawl.

- `https://cfj.org/robots.txt` allows all user agents, sets `Crawl-delay: 10`, and lists a sitemap.
- `https://cfj.org/trialwatch/trials/` is a server-rendered category hub (Women, Journalists, Democracy Defenders, LGBTQ+ People, Religious and Ethnic Minorities). The WordPress content field for that page is empty. There is no public case API. `https://cfj.org/wp-json/wp/v2/rb_report` and `/wp/v2/reports` return 404.
- The sitemap index is public. At the time of the check it listed about 96 report URLs, 226 news posts, 38 stories, 32 topic pages, and 48 country pages. `/person/` pages in the sample were CFJ people and experts, not a defendant roster.
- A sample report page, Bangladesh v. Shahidul Alam, exposes a title, a short blurb, a "Published" date, and a PDF link. The argument text is in the PDF. The page publication date is not an event date.
- No cfj.org terms-of-use page was found that permits scraping or republication. The privacy notice and imprint are public. Reuse questions go to info@cfj.org, Attn: General Counsel.
- TrialWatch is a registered mark. This prototype does not claim endorsement.

## What a future collector may do

Only after reuse is settled, and only with a narrow allowlist, caching, a delay of at least 10 seconds, and bounded link following. Manual URL or file import remains the default. Do not bypass logins, paywalls, CAPTCHAs, or other access controls.

## What this repository stores

Committed material is the fictional demonstration fixture, a catalog of public report titles and links in [trialwatch-report-index.md](trialwatch-report-index.md), and proposed short excerpts in [first-argument-clusters.md](first-argument-clusters.md). Do not commit full reports, articles, judgments, or sensitive case files. Prefer a source link, a short reviewed excerpt, and a derived record. The cluster note is not an approved record. Keyword tags and A–F grades from another project are notes, not approved arguments or outcomes.

Downloaded files and the local SQLite database stay in ignored directories (`downloads/`, `data/`).

`sensitive` records are omitted from `public_export`. Hiding a row in the interface is not a substitute for keeping it out of a public commit.

Do not collect private contact details, family details, or location information that the advocacy question does not need. Public reporting does not remove risk. A publication review is required before any real case is added.

## How sources are used

TrialWatch pages and documents can show what was argued, by whom, in which document, and when. They generally do not establish later outcomes. Outcomes come from a separate source: a judgment, a public case record, a UN decision, journalism, another human-rights organization, or an attributed public statement. Official announcements are stored as claims when that is all they are.

Two articles that copy one press release are one source, not two confirmations. Store the original when it is identifiable.

Retrieved text is untrusted data. It is not executed and it cannot change review status.

## External research starting points

These are candidate public sites, not confirmed APIs:

- https://wgad-opinions.ohchr.org/
- https://juris.ohchr.org/AdvancedSearch
- https://digitallibrary.un.org/
