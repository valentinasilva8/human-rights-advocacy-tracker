# Appeal-outcome review packet

Valentina Silva approved `pl_arg_legality` and `pl_arg_proportionality` on 10 October 2026. She also authorized approval of the three Poland appeal rows as one HFHR organization account. Every other real row remains `proposed`, including reception of Lisa Davis’s report. Nothing here authorizes deployment or redistribution of a PDF.

The current approved-only export is [public-data-contract.md](public-data-contract.md) and [public-export.sample.json](public-export.sample.json). Pull request 4 is on `cursor/evidence-review-safeguards-5c2e`.

## What is already public

With no argument-label filter, and with country set to Poland, the public explorer shows one real case and two approved arguments: `pl_arg_legality` and `pl_arg_proportionality`. `real_cases_with_approved_argument` is 1. A Proportionality-only filter matches only `pl_arg_proportionality`. The approved-only export has `real_case_count` 1, `approved_argument_count` 2, and three outcome rows for one decision.

## Public preview if the appeal is approved

`appeal_outcome_preview` does not itself approve a row. The stored appeal rows are approved as `Single-source report` with basis `organization_account`. The gate still refuses an Unverified outcome. The dated-outcome statement says an incomplete list is not a finding that no other development occurred.

Beside the two approved arguments, the three defendant rows would show one shared decision, `pl_decision_appeal_2022-01-12`. They would not count as three decisions. Each row would carry the HFHR-attributed claim, the organization-account caption, and this public limitation:

“HFHR reported this result. The appeal judgment itself was not retrieved. This is an organization account, not a finding read from the judgment.”

The preview states that reception of Lisa Davis’s report remains unestablished and that the reported affirmance does not establish acceptance of her arguments. It leaves out the proposed trial acquittals, the Tam records, reviewer notes, unresolved questions, and search notes.

## 1. `pl_arg_legality`

**Approved public claim.** Lisa Davis’s fairness report argues that Article 196 is not precise and is so broad that it gives the authorities unfettered discretion.

**Report page.** [Poland vs. Elzbieta Podlesna, Anna Prus, and Joanna Gzyra-Iskandar](https://cfj.org/reports/poland-vs-elzbieta-podlesna-anna-prus-and-joanna-gzyra-iskandar/). The page says Published 21 January 2022.

**PDF.** [trial-observation-report-poland-lgbt.pdf](https://cfj.org/wp-content/uploads/2023/07/trial-observation-report-poland-lgbt.pdf). The cover says November 2021. This is the file the passages were read from.

**Quotation.** “Article 196 is not precise, clear, or accessible. In criminalizing acts that “offend the religious feelings of other persons” through public insult, by nature a subjective concept, Article 196 is so broad as to afford the authorities unfettered discretion in its application, making it ripe for abuse.”

**Paraphrase.** The report treats “offending religious feelings” as too subjective a criminal standard.

**Location.** Printed p. 3, PDF page 4.

**Author and role.** Lisa Davis. `partner_argument`. Affiliation: City University of New York; TrialWatch Expert Panel. ABA Center for Human Rights staff helped draft the report. The stated disclaimer says the views are the authors’, not the ABA House of Delegates or Board of Governors, and not necessarily those of the Clooney Foundation for Justice.

**Dates and proceeding.** PDF cover: November 2021, month precision. The CFJ report page says Published 21 January 2022. Those are different dates. The stored argument date remains the cover month. II K 296/20 is the trial case number. Footnote 2 on printed p. 3 cites “District Court of Plock, Justification for a Judgment, Case No. II K 296/20, March 2, 2021.” An appeal docket has not been verified. Defendants: Elżbieta Podleśna, Anna Prus, Joanna Gzyra-Iskandar.

**Proposed label.** Legality and Broadness. The passage states both lack of precision and breadth. They were not collapsed into one label.

**Evidence basis.** `author_document`. The check is a reading of the author’s report. It is not a check of a judgment.

**Public limitation.** “This is what the named author wrote. It is not a court finding. No reviewed record establishes how a court received the argument. That absence is not a finding that the court ignored it.”

**Remedy, cited separately.** The legality passage on printed p. 3 does not request a remedy.

Quotation, printed p. 4, PDF page 5: “The prosecution’s appeal in the present case, which is scheduled to be heard on November 10, should likewise be rejected.” And: “While the legislature should repeal Article 196, which – as described above – does not conform with international and regional standards…”

Quotation, printed p. 31, PDF page 32, conclusion: “on November 10 the appellate court in Plock should dismiss the prosecution’s appeal against the acquittal.”

Same page, under “Recommendations from Professor Lisa Davis.” To the Polish legislature: “Article 196 and other laws functionally criminalizing expressions of solidarity with the LGBTIQ+ community should be repealed.” To the Polish judiciary: “the court should dismiss the prosecution’s appeal against the acquittal of Podlesna, Prus, and Gzyra-Iskandar.”

The November 10 sentence does not restate the year.

**Status.** Approved on 10 October 2026. This section is the approved argument that would sit beside the appeal. It is not part of the appeal decision.

## 2. `pl_arg_proportionality`

**Approved public claim.** Lisa Davis’s fairness report argues that the prosecution failed necessity and proportionality because the posters were not an exceptionally grave speech offense.

**Report page and PDF.** Same two links as `pl_arg_legality`.

**Quotation.** “Third, the case against the accused failed to meet necessity and proportionality requirements. With respect to this requirement, international and regional bodies have made clear that criminal prosecutions for speech offenses should be reserved for exceptionally grave acts, such as incitement to genocide and terrorism. The accused’s posting of stickers and posters featuring a rainbow halo clearly did not rise to this level of gravity.”

**Paraphrase.** The report reserves criminal speech prosecutions for exceptionally grave acts and says these posters did not meet that threshold.

**Location.** Printed p. 4, PDF page 5.

**Author, role, dates, proceeding.** Same as `pl_arg_legality`.

**Proposed label.** Necessity and Proportionality. The passage uses both words. They were not collapsed.

**Evidence basis.** `author_document`.

**Public limitation.** Same author-document limitation as `pl_arg_legality`.

**Remedy, cited separately.** The necessity sentences do not themselves tell the court what to do. The repeal and November 10 requests, and the recommendations to the legislature and the judiciary, are the quotations in section 1. They are on printed p. 4 and printed p. 31.

**Status.** Approved on 10 October 2026. This section is the other approved argument that would sit beside the appeal. It is not part of the appeal decision.

## 3. Reported appeal outcome

One decision, three defendant rows: `out_pl_appeal_podlesna`, `out_pl_appeal_prus`, `out_pl_appeal_gzyra`. Shared `decision_id`: `pl_decision_appeal_2022-01-12`.

Counts for the Poland proceeding: 3 defendants, 1 proceeding, 2 decisions (the 2 March 2021 acquittal and this reported appeal), 1 intervention (the fairness report), 6 outcome rows. HFHR is an amicus participant, not a fourth defendant and not a second intervention document. The amicus brief was not retrieved.

**Approved public claim, the same on each of the three rows.** HFHR reported that the Regional Court in Płock upheld the three defendants' acquittal on 12 January 2022.

**HFHR source.** [https://hfhr.pl/aktualnosci/tecza-nie-obraza-wyrok-uniewinnienie](https://hfhr.pl/aktualnosci/tecza-nie-obraza-wyrok-uniewinnienie). Source id `pl_src_hfhr`. The page is dated 13.01.2022. Stored publication date: 2022-01-13.

**Original Polish passage.**

“12 stycznia 2022 r. Sąd Okręgowy w Płocku utrzymał w mocy wyrok uniewinniający trzy aktywistki oskarżone o obrazę uczuć religijnych za to, że w 2019 r. rozpowszechniały naklejki z wizerunkiem Matki Bożej Częstochowskiej z tęczową aureolą. Wyrok jest prawomocny.”

“Sąd drugiej instancji 12 stycznia 2022 utrzymał w mocy zaskarżony wyrok i uniewinnił aktywistki. Sąd Okręgowy w Płocku zaznaczył w uzasadnieniu, że wniesione apelacje były bezzasadne.”

“Helsińska Fundacja Praw Człowieka złożyła w sprawie opinię przyjaciela sądu.”

**English translation.** On 12 January 2022 the Regional Court in Płock upheld the acquitting judgment of three activists accused of offending religious feelings for distributing, in 2019, stickers with the image of Our Lady of Częstochowa with a rainbow halo. The judgment is final. On 12 January 2022 the second-instance court upheld the appealed judgment and acquitted the activists. The Regional Court in Płock noted in its reasoning that the appeals that had been filed were unfounded. The Helsinki Foundation for Human Rights filed an amicus opinion in the case.

**How the passage identifies the same three defendants and proceeding.** The HFHR passage does not name Elżbieta Podleśna, Anna Prus, or Joanna Gzyra-Iskandar, and it does not cite II K 296/20. It identifies three activists, the Regional Court in Płock, 12 January 2022, a charge of offending religious feelings, and 2019 stickers of Our Lady of Częstochowa with a rainbow halo. The November 2021 fairness report names those three defendants and cites II K 296/20 as the District Court of Płock trial number for the justification dated 2 March 2021. The three appeal rows use that match. II K 296/20 is not stored as an appeal docket. No appeal docket has been verified.

**Event date and publication date.** The event date is 12 January 2022, the court date HFHR states. The HFHR article’s publication date is 13 January 2022. Those are different dates. The publication date is not stored as the event date.

**Amicus.** HFHR is participant `pl_hfhr`, role `amicus`. The page says HFHR filed an amicus opinion. The brief was not retrieved. HFHR is not a fourth defendant and not an intervention document. The intervention count remains the fairness report only.

**rp.pl.** [https://www.rp.pl/prawo-karne/art19284511-zapadl-prawomocny-wyrok-ws-matki-bozej-z-teczowa-aureola](https://www.rp.pl/prawo-karne/art19284511-zapadl-prawomocny-wyrok-ws-matki-bozej-z-teczowa-aureola). Publication line 13.01.2022. A re-read on 10 October 2026 showed an update stamp of 10.10.2026. That stamp is not a new event. The lede still attributes the account to HFHR.

**Original Polish passage from rp.pl.** “Sąd Okręgowy w Płocku utrzymał w mocy wyrok uniewinniający trzy aktywistki oskarżone o obrazę uczuć religijnych.” “informuje Helsińska Fundacja Praw Człowieka, która złożyła w sprawie opinię przyjaciela sądu.”

**English translation.** The Regional Court in Płock upheld the acquitting judgment of three activists accused of offending religious feelings. rp.pl says the Helsinki Foundation for Human Rights, which filed an amicus opinion, is the source of that account.

rp.pl’s provenance on each appeal row is `derived_from_shared_original`. It draws on HFHR’s account. It is not an independent confirmation. OKO.press is provenance `independent` after a reading of its same-day courtroom report, which does not cite HFHR. `independent_support_count` is 1. ARTICLE 19’s brief stays `unknown` and does not add to that count.

**Evidence category and public limitation.** The approval gate refuses `Unverified`. The reviewed category is evidence label **Single-source report** and evidence basis `organization_account`. That is an identified organization’s account. It is not `Primary-source supported` and not a finding read from the judgment. Public limitation, stored on each row: “HFHR reported this result. The appeal judgment itself was not retrieved. This is an organization account, not a finding read from the judgment. HFHR is an amicus participant; the brief was not retrieved. rp.pl draws on the HFHR account and is not an independent origin. OKO.press is a separate same-day courtroom report that names the three defendants and supports that identity match; it is not the judgment. This outcome does not establish acceptance or rejection of Lisa Davis's arguments. It is not a statement that 12 January 2022 is the latest known development. An incomplete list is not a finding that no other development occurred.”

**Reception of Lisa Davis’s report.** `pl_rec_legality` and `pl_rec_proportionality` stay proposed. Status: Decision not yet retrieved. Evidence basis: `response_not_established`. The reported appeal result does not establish that the court accepted her arguments. The absence of a reviewed reception is not a finding that the court ignored the arguments.

**Decision.** Valentina Silva authorized approval on 10 October 2026 as an AI-assisted review. She did not personally inspect the appeal judgment. The assistant did not retrieve the HFHR page again. The approved wording is the sentence in the claim above. Review action time: 2026-10-10T00:48:39+00:00.

## 4. Tam counsel and reception

`tam_arg_dykes` and `tam_rec_dykes`. This is Philip Dykes SC, not Elizabeth Wilmshurst and not the May 2022 fairness report.

**Proposed public claim.** Counsel argued that section 9 imposes a disproportionate restriction on freedom of expression because the prosecution does not need to prove an incitement to violence. The Court of Appeal copy holds that sections 9 and 10, and the sedition charges, satisfy the proportionality test.

**Source.** Court of Appeal of the High Court of the HKSAR, CACC 62/2022, [2024] HKCA 231, judgment 7 March 2024, hearing 4 July 2023. Copy read at [Columbia Global Freedom of Expression](https://globalfreedomofexpression.columbia.edu/wp-content/uploads/2023/07/March-2024-Tam-Tak-Chi-Judgment.pdf). The court authored the judgment. Columbia hosts this copy. A third-party host is not automatically a secondary account of someone else’s report. Authenticity against an official host is still not established: a legalref check on 9 October 2026 did not retrieve CACC 62/2022.

**Argument quotation.** “Mr Dykes argued that section 9 imposes a disproportionate restriction on the right to freedom of expression because the prosecution does not need to prove an incitement to violence.”

**Paraphrase.** The stored claim is only that proportionality submission.

**Argument location.** Paragraph 139.

**Reception quotation.** “In conclusion, we hold that sections 9 and 10 of the CO and accordingly the Sedition Charges satisfy the proportionality test.”

**Paraphrase.** On this copy, the court rejects the proportionality challenge to sections 9 and 10.

**Reception location.** Paragraphs 132–145; the holding is paragraph 145.

**What paragraph 145 does not establish.** Paragraph 131 says the court rejects counsel’s submissions that section 9 fails the “prescribed by law” requirement. Paragraphs 90–102 reject reading an intention to incite violence into the offence and say constitutionality is a separate question. Paragraph 146 onward is a slogan-meaning argument. Those parts are not this reception.

**Remedy, cited separately.** Paragraph 3, not paragraph 139: “The applicant now seeks leave to appeal against the conviction of the Sedition Charges only and the sentences for both the Sedition Charges and the Public Order Charges.”

**Author and role.** Philip Dykes SC. `defense_counsel_described`. Counsel for Tam Tak-chi in the Court of Appeal. Argument date stored as the hearing date, 4 July 2023.

**Proceeding.** HKSAR v. Tam Tak-chi, DCCC 927, 928 and 930 of 2020, on appeal as CACC 62/2022.

**Proposed label and reception.** Proportionality only. Reception status proposed as Explicitly rejected. `reasoning_checked` is false. `account_type` is `not_yet_established` because the copy is not authenticated. Evidence basis: `unauthenticated_judgment_copy`. Approval of an explicit rejection needs a reviewer’s reasoning check and an account type. This row does not have those, so it cannot be approved as it stands.

**Public limitation.** “This is counsel's proportionality limb only, as the judgment summarizes it at paragraph 139. Paragraph 145 holds that sections 9 and 10 satisfy the proportionality test. It does not establish rejection of the legal-certainty argument, which the same judgment addresses at paragraph 131, or the slogan argument from paragraph 146. Philip Dykes SC is counsel in the appeal, not the author of the May 2022 fairness report. The text was read from a Columbia-hosted copy. A check of the official legal reference site on 9 October 2026 did not retrieve CACC 62/2022, so authenticity is not established.”

**Recommendation.** Ready for review of the narrowed wording. It is not in the first set, because the copy is not authenticated and the reception check is still open.

## Records that stay proposed

No claim below is approved. The appeal rows are the decision in front of you. The others are not part of this step.

| Record | Status |
| --- | --- |
| `out_pl_appeal_podlesna`, `out_pl_appeal_prus`, `out_pl_appeal_gzyra` | Approved as one HFHR organization account. Label `Single-source report`. |
| `out_pl_acquit_*` | The report cites a 2 March 2021 acquittal that predates the report. The judgment was not retrieved. Shared decision `pl_decision_trial_2021-03-02`. |
| `pl_rec_legality`, `pl_rec_proportionality` | Decision not yet retrieved. The HFHR account is not reception of the report and is not acceptance of Lisa Davis’s arguments. |
| `tam_arg_breadth`, `tam_arg_sentence` | Report claims. The sentence quotation covers political speech and organising an unauthorised assembly together. It does not divide the sentence by count. |
| `tam_rec_breadth`, `tam_rec_sentence` | Response not established. Dismissal quotations sit on the outcomes. |
| `out_tam_sentence` | “Sentence imposed,” 20 April 2022. Official press summary of [2022] HKDC 343 says it is not the judgment. |
| `out_tam_conviction`, `out_tam_ca`, `out_tam_cfa` | Dates and dismissals read from unauthenticated copies. Dismissals are outcomes, not reception of the May 2022 report. |
| `tam_arg_dykes`, `tam_rec_dykes` | Counsel’s proportionality limb. Not this decision. |

## Approved outcome wording

These three records are one decision, `pl_decision_appeal_2022-01-12`. Approved wording, the same on each row:

HFHR reported that the Regional Court in Płock upheld the three defendants' acquittal on 12 January 2022.

1. `out_pl_appeal_podlesna`
2. `out_pl_appeal_prus`
3. `out_pl_appeal_gzyra`

A 28 March 2024 Amnesty Slovakia report is logged as research lead `pl_search_amnesty_2024`. It is not approved and is not in the public export.
