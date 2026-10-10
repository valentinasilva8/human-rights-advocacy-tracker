# Approval packet

This packet does not approve any record. Every real row remains `proposed`. Nothing here authorizes deployment, a pull request, or redistribution of a PDF.

Quotation and paraphrase are labeled separately. A requested remedy that sits outside the argument passage has its own citation.

Recommendations are only: **ready for review**, **needs correction**, or **blocked on evidence**.

The two records to review first are at the end. They are `pl_arg_legality` and `pl_arg_proportionality`.

## Public preview

`public_preview` does not approve the row. For `pl_arg_legality`, still stored as `proposed`, it returns the claim, the source link, the evidence basis, and the public limitation. It does not return the proposed appeal outcomes, the other arguments, reviewer notes, unresolved questions, or search queries. Real-case count in the public export remains 0.

```json
{
  "preview_only": true,
  "this_call_approved_nothing": true,
  "stored_review_status": "proposed",
  "argument": {
    "id": "pl_arg_legality",
    "author_actor": "Lisa Davis",
    "attribution_role": "partner_argument",
    "evidence_basis": "author_document",
    "evidence_basis_caption": "This records what the named author wrote in that author's document. It is not itself a court finding.",
    "public_limitation": "This is what the named author wrote. It is not a court finding. No reviewed record establishes how a court received the argument. That absence is not a finding that the court ignored it."
  },
  "reception_note": "No reviewed record of how an authority received this argument. That absence is not a finding that the court ignored the argument.",
  "timeline_note": "An incomplete list is not a finding that no other development occurred. Proposed outcome records are not shown in this preview."
}
```

The full preview also includes the passage, printed page, and the report URL. It does not say that the court ignored the argument, and it does not imply that an incomplete timeline means nothing else happened.

## 1. `pl_arg_legality`

**Proposed public claim.** Lisa Davis’s fairness report argues that Article 196 is not precise and is so broad that it gives the authorities unfettered discretion.

**Source.** [Poland vs. Elzbieta Podlesna, Anna Prus, and Joanna Gzyra-Iskandar](https://cfj.org/reports/poland-vs-elzbieta-podlesna-anna-prus-and-joanna-gzyra-iskandar/)

**Quotation.** “Article 196 is not precise, clear, or accessible. In criminalizing acts that “offend the religious feelings of other persons” through public insult, by nature a subjective concept, Article 196 is so broad as to afford the authorities unfettered discretion in its application, making it ripe for abuse.”

**Paraphrase.** The report treats “offending religious feelings” as too subjective a criminal standard.

**Location.** Printed p. 3, PDF page 4.

**Author and role.** Lisa Davis. `partner_argument`. Affiliation: City University of New York; TrialWatch Expert Panel. ABA Center for Human Rights staff helped draft the report. The stated disclaimer says the views are the authors’, not the ABA House of Delegates or Board of Governors, and not necessarily those of the Clooney Foundation for Justice.

**Dates and proceeding.** Report cover: November 2021, month precision. Proceeding: District Court of Płock, II K 296/20. Defendants: Elżbieta Podleśna, Anna Prus, Joanna Gzyra-Iskandar.

**Proposed label.** Legality and Broadness. The passage states both lack of precision and breadth. They were not collapsed into one label.

**Evidence basis.** `author_document`. The check is a reading of the author’s report. It is not a check of a judgment.

**Public limitation.** “This is what the named author wrote. It is not a court finding. No reviewed record establishes how a court received the argument. That absence is not a finding that the court ignored it.”

**Remedy, cited separately.** The legality passage does not request a remedy.

Quotation, printed p. 4, PDF page 5: “While the legislature should repeal Article 196, which – as described above – does not conform with international and regional standards…” and “The prosecution’s appeal in the present case, which is scheduled to be heard on November 10, should likewise be rejected.”

Quotation, printed p. 31, PDF page 32: “on November 10 the appellate court in Plock should dismiss the prosecution’s appeal against the acquittal.”

The November 10 sentence does not restate the year.

**Recommendation.** Ready for review. The claim is about what the report says.

## 2. `pl_arg_proportionality`

**Proposed public claim.** Lisa Davis’s fairness report argues that the prosecution failed necessity and proportionality because the posters were not an exceptionally grave speech offense.

**Source.** Same report URL as `pl_arg_legality`.

**Quotation.** “Third, the case against the accused failed to meet necessity and proportionality requirements. With respect to this requirement, international and regional bodies have made clear that criminal prosecutions for speech offenses should be reserved for exceptionally grave acts, such as incitement to genocide and terrorism. The accused’s posting of stickers and posters featuring a rainbow halo clearly did not rise to this level of gravity.”

**Paraphrase.** The report reserves criminal speech prosecutions for exceptionally grave acts and says these posters did not meet that threshold.

**Location.** Printed p. 4, PDF page 5.

**Author, role, dates, proceeding.** Same as `pl_arg_legality`.

**Proposed label.** Necessity and Proportionality. The passage uses both words. They were not collapsed.

**Evidence basis.** `author_document`.

**Public limitation.** Same author-document limitation as `pl_arg_legality`.

**Remedy, cited separately.** The necessity paragraph does not itself tell the court what to do. The repeal and November 10 requests are the quotations in section 1, on the same printed p. 4 and again in the conclusion on printed p. 31.

**Recommendation.** Ready for review. The claim is about what the report says.

## 3. Reported appeal outcome

One decision, three defendant rows: `out_pl_appeal_podlesna`, `out_pl_appeal_prus`, `out_pl_appeal_gzyra`. Shared `decision_id`: `pl_decision_appeal_2022-01-12`.

Counts for the Poland proceeding: 3 defendants, 1 proceeding, 2 decisions (the 2 March 2021 acquittal and this reported appeal), 1 intervention (the fairness report), 6 outcome rows. HFHR is an amicus participant, not a fourth defendant and not a second intervention document. The amicus brief was not retrieved.

**Proposed public claim.** HFHR reported that on 12 January 2022 the Regional Court in Płock upheld the acquittal of Elżbieta Podleśna, Anna Prus, and Joanna Gzyra-Iskandar and said the appeals were unfounded.

**Source.** [HFHR, 13 January 2022](https://hfhr.pl/aktualnosci/tecza-nie-obraza-wyrok-uniewinnienie)

**Quotation (original).** “12 stycznia 2022 r. Sąd Okręgowy w Płocku utrzymał w mocy wyrok uniewinniający trzy aktywistki oskarżone o obrazę uczuć religijnych…”

**Quotation (original).** “Sąd drugiej instancji 12 stycznia 2022 utrzymał w mocy zaskarżony wyrok i uniewinnił aktywistki. Sąd Okręgowy w Płocku zaznaczył w uzasadnieniu, że wniesione apelacje były bezzasadne.”

**Translation.** On 12 January 2022 the Regional Court in Płock upheld the acquitting judgment of three activists accused of offending religious feelings. The second-instance court upheld the appealed judgment and acquitted the activists. The Regional Court in Płock noted in its reasons that the appeals were unfounded.

**Amicus quotation (original).** “Helsińska Fundacja Praw Człowieka złożyła w sprawie opinię przyjaciela sądu.”

**Translation.** The Helsinki Foundation for Human Rights filed an amicus opinion in the case.

**Location.** HFHR web page dated 13.01.2022. No printed or PDF page. The appeal judgment itself has no page cite because it was not retrieved.

**Author and role.** Helsinki Foundation for Human Rights, reporting the court’s result and its own amicus. HFHR is not the court. rp.pl, 13 January 2022, [Zapadł prawomocny wyrok](https://www.rp.pl/prawo-karne/art19284511-zapadl-prawomocny-wyrok-ws-matki-bozej-z-teczowa-aureola), draws on that HFHR account. Its provenance is `derived_from_shared_original`. It is not a second independent origin.

**Dates and proceeding.** Event date 12 January 2022. HFHR publication date 13 January 2022. Proceeding II K 296/20. The November 2021 report is earlier than this reported decision. The report is not treated as the cause of the decision. Reception of the report stays “decision not yet retrieved.”

**Proposed outcome type.** Appeal decided. Evidence label remains **Unverified**. Evidence basis: `organization_account`.

The label was not changed. Unverified blocks approval. Changing it to Single-source report or Primary-source supported would only make approval possible, and the judgment still has not been read. HFHR’s page is evidence. The independent-origin count is 0 because rp.pl is derived from HFHR. Zero independent origins is not zero evidence.

**Why “HFHR reported” rather than a verified court finding.** The source check is a reading of HFHR’s own page, plus rp.pl’s attribution of the reasons to HFHR. A search of orzeczenia.ms.gov.pl on 9 October 2026 did not return this Article 196 appeal. Nearby Płock files II Ko 28/21 and II Ko 37/21 are different cases. The judgment was not compared with an official text.

**Public limitation.** “HFHR reported this result. The appeal judgment was not retrieved, including from a check of the official Polish judgment portal. rp.pl draws on the HFHR account and is not an independent origin. Zero independent origins is not zero evidence. This is not a documented response to the fairness report.”

**Recommendation.** Blocked on evidence if the claim would be a court finding. The HFHR-reported wording can be reviewed as the proposed display text, and it cannot be approved while the label stays Unverified.

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

These are not in the first review set. No claim below is approved.

| Record | Why it is not in the first set |
| --- | --- |
| `out_pl_appeal_*` | Blocked on evidence as a court finding. Label stays Unverified. |
| `out_pl_acquit_*` | The report cites a 2 March 2021 acquittal that predates the report. The judgment was not retrieved. Shared decision `pl_decision_trial_2021-03-02`. |
| `pl_rec_legality`, `pl_rec_proportionality` | Decision not yet retrieved. The HFHR account is not reception of the report. |
| `tam_arg_breadth`, `tam_arg_sentence` | Report claims. The sentence quotation covers political speech and organising an unauthorised assembly together. It does not divide the sentence by count. Remedy is not stated in those passages. The conclusion on printed p. 51, PDF page 52, grades the trial D and does not state a court order. |
| `tam_rec_breadth`, `tam_rec_sentence` | Response not established. Dismissal quotations sit on the outcomes. |
| `out_tam_sentence` | Now “Sentence imposed,” 20 April 2022. Official press summary of [2022] HKDC 343 says it is not the judgment and confirms 40 months and HK$5,000. The itemization on that page is not the report’s claim. |
| `out_tam_conviction`, `out_tam_ca`, `out_tam_cfa` | Dates and dismissals read from unauthenticated copies, except the sentence summary above. Dismissals are outcomes, not reception of the May 2022 report. |
| `tam_arg_dykes`, `tam_rec_dykes` | Presented above. Not the first set. |

## Review first

1. `pl_arg_legality`
2. `pl_arg_proportionality`

Both are ready for review as claims about what Lisa Davis’s report says. Approving either one is a separate decision, and this packet does not make it.
