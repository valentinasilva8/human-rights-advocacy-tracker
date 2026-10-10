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
