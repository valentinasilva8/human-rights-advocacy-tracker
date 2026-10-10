# Research log

Searches on 9 October 2026. Read-only. About one pass over Poland v. Podleśna, Prus, and Gzyra-Iskandar and Hong Kong SAR v. Tam Tak-chi, plus the two fairness-report PDFs already in hand. This is not a finding that unopened documents do not exist.

Proposed rows from this log are in `advocacy_trace/fixtures/proposed_research.json`. They are not approved.

## Poland

**Query:** Podleśna Prus Gzyra-Iskandar appeal Article 196 Płock November 2021 rainbow Virgin Mary court decision.

**Report read:** *Poland vs. Elzbieta Podlesna, Anna Prus, and Joanna Gzyra-Iskandar* (November 2021), Lisa Davis, with ABA Center for Human Rights staff. Cover date is a month. The executive summary says the report is released in advance of the prosecution’s appeal, “the hearing for which is scheduled for November 10.” That sentence does not repeat the year. Trial acquittal is cited as District Court of Płock, II K 296/20, justification dated 2 March 2021. That acquittal is before the report.

**Opened:**

- HFHR, 13 January 2022, [Tęcza nie obraża](https://hfhr.pl/aktualnosci/tecza-nie-obraza-wyrok-uniewinnienie). Says the Regional Court in Płock on 12 January 2022 upheld the acquittal and that the appeals were unfounded. HFHR says it filed an amicus. The amicus PDF was not opened.
- Rzeczpospolita, publication line 13.01.2022, [Zapadł prawomocny wyrok](https://www.rp.pl/prawo-karne/art19284511-zapadl-prawomocny-wyrok-ws-matki-bozej-z-teczowa-aureola). The lede states the same affirmance. The article says HFHR informs the account of the court’s reasons. Stored as derived from that HFHR account, not as an independent origin.

**Not retrieved:**

- TVN24 URL identified as a lead. A follow-up fetch timed out. No TVN24 passage is stored. Next search: open that URL or the judgment.
- The appeal judgment. Not found in the pages opened. Do not treat that as “the court did not address the report.”

**Contradiction / dependency:** rp.pl is not a second independent account of the reasons, because it attributes them to HFHR. HFHR and rp.pl agree on the result and the date. Neither is the judgment.

## Tam Tak-chi

**Query:** Tam Tak-chi sedition appeal judgment after April 2022 HKSAR DCCC 927.

**Report read:** *Hong Kong SAR v. Tam Tak-chi* (May 2022), Elizabeth Wilmshurst. Disclaimer: the assessment is the author’s and not necessarily the Clooney Foundation for Justice’s. Conviction in March 2022. Sentence of 40 months and HK$5,000 delivered 20 April 2022. The report is later than both.

**Opened:**

- Court of Appeal, CACC 62/2022, [2024] HKCA 231, 7 March 2024, from a [Columbia-hosted copy](https://globalfreedomofexpression.columbia.edu/wp-content/uploads/2023/07/March-2024-Tam-Tak-Chi-Judgment.pdf). Hearing 4 July 2023. Refuses leave and dismisses the appeals against conviction and sentence. Paragraph 145 holds that Crimes Ordinance ss. 9 and 10 satisfy proportionality, answering counsel (Philip Dykes SC). Recites Reasons for Verdict 2 March 2022, [2022] HKDC 208, and Reasons for Sentence 20 April 2022, [2022] HKDC 343. Text search: no Wilmshurst, TrialWatch, or Clooney.
- Court of Final Appeal, [2025] HKCFA 4, FACC 12/2024, 6 March 2025, from a BabelCite copy. Appeal dismissed. Holds that the prosecution need not prove an intention to incite violence. Text search: no Wilmshurst, TrialWatch, or Clooney. Official host not confirmed.

**Not retrieved:**

- RTHK URL `https://news.rthk.hk/rthk/en/component/k2/1794531-20250306.htm` returned 404. No RTHK passage is stored. A missing page is not a finding that no story was published.
- The trial reasons themselves, as a separate document. The dates above are recitals in the Court of Appeal judgment and in the fairness report.

The name search does not establish that the courts never took up the report’s substance without naming it. The correction pass below moves the dismissal quotations onto the outcome rows. Reception of the May 2022 report stays unestablished.

## Correction pass, 9 October 2026

This pass did not add cases. It did not approve any row. The approval packet is `docs/review-packet.md`, which is a different document from this log.

**Sentence type.** `out_tam_sentence` is now “Sentence imposed.” The evidence links, including the Court of Appeal copy and the official press summary, stay attached. The fictional Rivera reduction remains “Sentence modification.”

**Reception separated from outcome.** The Court of Appeal dismissal at paragraph 168, and the sentence-appeal dismissal at paragraph 177, are on `out_tam_ca`. The Court of Final Appeal dismissal at paragraph 84 is on `out_tam_cfa`. `tam_rec_breadth` and `tam_rec_sentence` no longer quote those dismissals. No passage was identified that links either court to Elizabeth Wilmshurst’s report. That is `response_not_established`, not a finding that the court ignored the report.

**Dykes.** Paragraph 139 is counsel’s proportionality submission: section 9 is a disproportionate restriction because the prosecution need not prove an incitement to violence. Paragraphs 132–145 answer that limb. Paragraph 145’s holding is the proportionality test. Paragraph 131 rejects the legal-certainty submissions. Paragraphs 90–102 reject reading an intention to incite violence into the offence and leave constitutionality open. Paragraph 146 onward is a separate slogan argument. The stored reception is the proportionality limb only. Counsel is not the fairness report.

**Official-source checks.**

- legalref search for CACC 62/2022: the search URL returned an internal server error, and the opened results did not include CACC 62/2022 or [2025] HKCFA 4. Other 2022 appeal numbers and the National Security Law case against 47 people are different proceedings. Not retrieved is not “the judgment does not exist.” Columbia hosts a copy. Columbia did not author the judgment. The copy remains unauthenticated.
- Official press summary, not the judgment: [HKSAR v TAM TAK CHI, [2022] HKDC 343](https://legalref.judiciary.hk/doc/judg/html/vetted/other/ch/2020/DCCC000927E_2020_files/DCCC000927E_2020ES.htm). The page says “This summary is not part of the Judgment.” Date of sentence 20 April 2022. Total sentence 40 months and a HK$5,000 fine. The page itemizes counts. That itemization is not Wilmshurst’s claim. Counsel at sentence is Edwin Choy SC leading Jeffrey Tam and others, not Philip Dykes SC. The full reasons were not opened.
- orzeczenia.ms.gov.pl: the Article 196 appeal was not returned. Nearby Płock files II Ko 28/21 (4 January 2022) and II Ko 37/21 (18 January 2022) are different cases. The Poland appeal rows stay `Unverified`. The proposed wording is “HFHR reported…”. HFHR is recorded as an amicus participant because it reported filing an amicus. The brief was not retrieved. rp.pl stays `derived_from_shared_original`. One organization’s account plus a derivative article is evidence. It is not zero evidence, and it is not an authenticated judgment.

**What stays internal.** Search queries, the name-search note, and unresolved questions stay off public views. `public_limitation` is what a public user would see beside a claim.

## Poland links and trial number, 10 October 2026

The report page is https://cfj.org/reports/poland-vs-elzbieta-podlesna-anna-prus-and-joanna-gzyra-iskandar/. It says Published 21 January 2022. The PDF linked from that page is https://cfj.org/wp-content/uploads/2023/07/trial-observation-report-poland-lgbt.pdf. The cover says November 2021. The downloaded PDF is the same file previously read for the passages.

Footnote 2 on printed p. 3 cites District Court of Plock, Justification for a Judgment, Case No. II K 296/20, March 2, 2021. That is the trial number. No appeal docket number was found in the report. The appeal rows are not relabeled with II K 296/20 as if it were the appeal case number.

The author and disclaimer are on printed p. 1, PDF page 2. The boxed disclaimer includes the sentence that nothing in the report should be considered legal advice for specific cases. Remedies are not in the legality passage. They appear on printed p. 4 and again on printed p. 31 under the conclusion and under “Recommendations from Professor Lisa Davis.”

On 10 October 2026 Valentina Silva approved `pl_arg_legality` and `pl_arg_proportionality`. The approval is stored only while the claim, quotation, remedy text, and disclaimer still match the text she reviewed. The HFHR and rp.pl quotations stay on the proposed appeal rows. They were not approved. rp.pl was read again on 10 October 2026. Its publication line is still 13.01.2022. The page also showed an update stamp of 10.10.2026. The lede still says the Regional Court in Płock upheld the acquittal, and it still attributes the account to HFHR.

## Appeal-outcome packet, 10 October 2026

The packet for `out_pl_appeal_podlesna`, `out_pl_appeal_prus`, and `out_pl_appeal_gzyra` was prepared for review. It did not approve those rows. The HFHR page does not name the three defendants or cite II K 296/20. rp.pl stays `derived_from_shared_original`.

## Appeal account approval, 10 October 2026

Valentina Silva authorized approval of those three rows as one shared decision, `pl_decision_appeal_2022-01-12`. The review is AI-assisted. She did not personally inspect the appeal judgment. The assistant did not retrieve the HFHR page again for this approval. The HFHR quotations already in the record were retained on the HFHR source.

The approval gate refuses `Unverified`. The smallest change that uses the existing gate is evidence label `Single-source report` with evidence basis `organization_account`. That is not `Primary-source supported`. The public claim is: HFHR reported that the Regional Court in Płock upheld the three defendants' acquittal on 12 January 2022.

OKO.press, read 10 October 2026, [Tęcza nie obraża](https://oko.press/tecza-nie-obraza-prawomocny-wyrok-sadu-apelacyjnego-w-plocku), is a same-day courtroom report by Maciek Piasecki and Agnieszka Jędrzejczyk. It names Elżbieta Podleśna, Anna Prus, and Joanna Gzyra-Iskandar and says the appellate court on 12 January 2022 upheld the district-court acquittal. It does not cite HFHR, and it says OKO.press transmitted the hearing. Provenance stays `independent` because it is a separate newsroom. `support_scope` is `identity_and_reported_result`. That supports the identity and the reported court result. It does not corroborate that HFHR reported the result, HFHR’s amicus statement, or every sentence on the outcome record, so it does not raise `independent_support_count`. The count is 0. The evidence label stays `Single-source report` because the approved claim is HFHR’s attributed account. The January 2022 rp.pl article remains `derived_from_shared_original`.

ARTICLE 19’s brief, [Amicus_Poland-Rainbow-Holy-Mary_EN.pdf](https://www.article19.org/wp-content/uploads/2024/03/Amicus_Poland-Rainbow-Holy-Mary_EN.pdf), footnote 1, cites Ref. No. V Ka 418/21 for a 12 January 2022 judgment of the District Court in Płock, Fifth Criminal Appeals Division, from an unofficial translation. V Ka 418/21 is stored only with that attribution. II K 296/20 remains the trial number. The brief is captioned Case no. V KK 430/22. That caption is not verified against a judgment. Its provenance stays `unknown`, so it does not raise the independence count.

Reception rows `pl_rec_legality` and `pl_rec_proportionality` stay proposed. The outcome does not establish acceptance or rejection of Lisa Davis’s arguments.

Amnesty Slovakia, 28 March 2024, [Elżbieta Podleśna sa dočkala spravodlivosti](https://www.amnesty.sk/elzbieta-podlesna-sa-dockala-spravodlivosti/), says the Supreme Court rejected the state authorities’ appeal against the January 2022 acquittal. That wording collapses two different actions. It is not the basis of the proposed claims below, and it is not part of the January approval.

## Supreme Court packet, 10 October 2026

The same proceeding was checked on two pages read that day. [KPH](https://kph.org.pl/tecza-nie-obraza-koncowy-wyrok-sadu-najwyzszego-ws-aktywistek-oskarzonych-o-obraze-uczuc-religijnych/) and a separate [rp.pl article](https://www.rp.pl/prawo-karne/art40078891-jest-decyzja-sn-bez-kary-za-matke-boska-z-teczowa-aureola) name Elżbieta Podleśna, Joanna Gzyra-Iskandar, and Anna Prus, the Płock District Court acquittal of March 2021, and the Płock regional-court affirmance of January 2022. This 2024 rp.pl article does not cite HFHR and is not the 13 January 2022 article.

KPH reports two actions. The District Prosecutor in Płock’s cassation was effectively withdrawn, and the day was not stated. One Supreme Court order of 28 March 2024, cited as V KK 430/22, dismissed as obviously groundless the cassations of counsel for Kaja Godek and Tadeusz Łebkowski. Those are two challengers in one reported disposition, not two decisions. KPH uses both `postanowienie` and `wyrok`. rp.pl says the Płock prosecution withdrew its cassation “w ostatnich dniach,” and that on Thursday the remaining cassations of Kaja Godek and the Płock priest were dismissed as obviously groundless. rp.pl does not spell Łebkowski. The publication line 28.03.2024 14:43 is not the withdrawal date.

The order was not retrieved. The rows are proposed and `Unverified`. They are not in the public export. The packet is [supreme-court-2024-review-packet.md](supreme-court-2024-review-packet.md). The public caption for approved events is “Latest approved event in this dataset.”
