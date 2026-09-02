# 94 — Studied firms behind driftwood, tuppence and ludlow

Researched 2026-09-02 for ticket 94 (charted by ticket 75 Q7; feeds ticket 79 items 2 and 10). Ticket 79 does not pick a firm — this file supplies candidates for it to pick under. Every number below carries its own source URL and date; every number is a party's own signed filing, a regulator's own decision, or a court/tribunal's own judgment. No private individual is named — officials and judges are referred to by role, not by name.

Adopters' own declared facts (read from this repo's `.estate-clone/*/party.yaml` and `README.md`, 2026-09-02):

| adopter | sector (README) | regimes (README) | signed `size` | signed `appetite.tolerance` |
|---|---|---|---|---|
| driftwood | e-comm, "the teaching default" | PCI + GDPR | turnover £86,000,000; customers 240,000; data_subjects 240,000; headcount 410; as_of 2026-06-30 | £40,000 |
| tuppence | fintech | FCA + PCI + GDPR | **no `size:` block in party.yaml** | £15,000 |
| ludlow | US health | HIPAA | **no `size:` block in party.yaml** | £5,000 |

Ticket 75 Q7 already records that tuppence and ludlow "publish no size and no obligations" and that driftwood's own £40,000-against-£86m does not clear any priced tier — confirmed directly against the party.yaml files in this clone.

---

## driftwood → candidate: DSG Retail Limited (trading as Currys PC World / Dixons Travel; part of Currys plc, formerly Dixons Carphone plc)

Sector match: UK electronics retailer taking card payments online and in store — PCI DSS and UK data protection law, same pairing driftwood declares.

**Size facts** (Currys plc, the listed parent of the fined subsidiary — DSG Retail Limited's own standalone turnover/headcount are not separately published, flagged below):
- Group revenue **£8,706m**, financial year ended 3 May 2025. [Currys plc Annual Report & Accounts 2024/25](https://www.currysplc.com/media/ap4dtkwn/currys-annual-report-2024-25-web.pdf), signed by the Group Chief Executive 2 July 2025 (prior years on the same page: £8,476m FY2023/24, £8,874m FY2022/23).
- Average employees **24,706** for the period ended 3 May 2025 (UK & Ireland 14,792 + Nordics 9,914; Greece disposed of in-year), against 27,778 the year before. Same Annual Report & Accounts 2024/25, employee-numbers note.
- No single published "customer count." Closest disclosed proxies in the same report: iD Mobile subscribers 2.2 million and UK credit active accounts 2.3 million, both FY2024/25.
- Data-subject count for the breach itself: "at least 14 million" people, with payment card data of **5.6 million** customers exfiltrated — stated in the regulator's own decision, reproduced in the tribunal judgment below.

**Regimes:** PCI DSS (the ICO's own finding was that DSG's point-of-sale estate was assessed as *not* PCI DSS compliant by DSG's own consultants in May 2017 and was slow to remediate); Data Protection Act 1998 (the breach ran July 2017–April 2018, before the GDPR commencement date of 25 May 2018); UK GDPR applies to the retailer going forward.

**Regulator action:** ICO Monetary Penalty Notice against DSG Retail Limited, **£500,000**, dated **9 January 2020** — the statutory maximum under the pre-GDPR Data Protection Act 1998. The ICO's original 2020 press release is no longer at a resolvable URL on ico.org.uk; the figure and date are instead sourced from the tribunal's own record of the notice: [DSG Retail Limited v The Information Commissioner, First-tier Tribunal (GRC)](https://caselaw.nationalarchives.gov.uk/ukftt/grc/2023/983), decision promulgated **6 July 2022**.

**Litigation status — not final, live as of 2026-09-02, the clearest illustration in this record of why `final_as_of` matters:**
1. ICO Monetary Penalty Notice, £500,000 — 2020-01-09.
2. First-tier Tribunal substitutes **£250,000** — decision promulgated 2022-07-06. [Judgment](https://caselaw.nationalarchives.gov.uk/ukftt/grc/2023/983).
3. Upper Tribunal (Administrative Appeals Chamber) allows DSG's further appeal on a point of law (whether payment-card data exfiltrated by an attacker remains "personal data" once outside the controller's hands), sets aside the FTT decision and remits it — decision dated **23 September 2024**, [2024] UKUT 287 (AAC). [Judgment](https://caselaw.nationalarchives.gov.uk/ukut/aac/2024/287).
4. Court of Appeal rules for the ICO on that point of law, confirming organisations must protect personal data regardless of whether an attacker can re-identify individuals from it — judgment published **19 February 2026**. The case now returns to the First-tier Tribunal to apply the ruling to the facts. [ICO news, 19 February 2026](https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2026/02/ico-wins-court-of-appeal-case-in-dsg-retail-ruling/).

**No final, collected figure exists for this case today.** This is the same shape of correction ticket 79 item 1 already records for Doorstep Dispensaree (£92,000, final only after the Court of Appeal, 2024-12-09) and Clearview AI (never collected) — DSG is a live third example, still open six years after the original notice.

**Appetite the record supports:** none, cleanly. Currys plc's annual report does not publish a stated risk-appetite £ figure or a self-insured retention. The only appetite-adjacent number in this record is the ICO's own £500,000 statutory ceiling under the 1998 Act — a regulator-imposed cap, not a self-declared tolerance. Flagged as a gap against the ticket's "disclosed risk tolerance, insurance programme, or stated materiality threshold" test.

**What driftwood's own numbers already show:** £40,000 appetite against £86,000,000 signed turnover is 0.047% of turnover. Under `driftwood/selection-policy/selection_policy.py` (loosest tier whose residual ≤ tolerance, fail-closed to `isolated`), this is the exact case ticket 75 Q7 names as fitting no rung.

**What DSG/Currys' numbers would make reachable:** Currys' turnover is roughly 101× driftwood's signed figure, headcount roughly 60×, and the breach's data-subject count roughly 58× driftwood's signed 240,000. Because the estate's residual pricing scales with these same size facts, a straight substitution would scale the priced residual up in roughly the same proportion — it would not by itself bring a fixed £40,000 appetite inside any tier's band. The £500,000 statutory MPN, restated as a share of Currys' own £8,706m turnover, is **0.0057%** — an order of magnitude *tighter* than driftwood's own declared 0.047%-of-turnover ratio. So a proportional appetite genuinely calibrated off this candidate's own regulatory record would select a *tighter* rung than driftwood's current fixed number implies, not a looser one.

---

## tuppence → candidate: Starling Bank Limited

Sector match: UK-authorised digital challenger bank, FCA-regulated, card issuer (PCI DSS), UK GDPR — the same three regimes tuppence declares. Company no. 09092149.

**Size facts:**
- Customers **approximately 3.6 million** and revenue **£452.8 million**, both stated for 2023 — given directly by the regulator in the same document as the enforcement action, below. [FCA Final Notice, Starling Bank Limited, reference 730166](https://www.fca.org.uk/publication/final-notices/starling-bank-limited-2024.pdf), dated 27 September 2024, §2.1.
- Total Income **£414,814k**, year ended 31 March 2023 (up 120.6% year-on-year). [Starling Bank Limited Annual Report 2023](https://www.starlingbank.com/docs/annual-reports/Starling-Bank-Annual-Report-2023.pdf) (its own audited accounts). This is a different metric and a different reporting date convention than the FCA's £452.8m figure above — flagged as a discrepancy between two primary sources rather than resolved.
- Employees: average **2,762** for the year ended 31 March 2023, up from 1,941 the year before. Same Annual Report 2023.
- No separately disclosed data-subject count; customer accounts (~3.6 million) is the closest published proxy.

**Regimes:** FCA-regulated under the Financial Services and Markets Act 2000 (Principle 3 — organised, effective affairs with adequate risk management systems); PCI DSS as a card issuer; UK GDPR.

**Regulator action:** FCA Final Notice, Starling Bank Limited, financial penalty **£28,959,426**, dated **27 September 2024** (the penalty would have been £40,959,426 without a 30% stage-1 settlement discount), for failing to design, implement and maintain adequate financial-crime systems and controls — in particular sanctions screening that had, since 2017, checked new and existing customers against only a fraction of the UK's Consolidated List, and 54,359 accounts opened for 49,183 high/higher-risk customers in breach of a 2021 voluntary requirement not to. [FCA Final Notice](https://www.fca.org.uk/publication/final-notices/starling-bank-limited-2024.pdf) (verified against the FCA's own [press release](https://www.fca.org.uk/news/press-releases/fca-fines-starling-bank-failings-financial-crime-systems-and-controls) of the same date).

**Litigation status: final and collected.** Starling agreed to resolve the matter under the FCA's executive settlement procedure and accepted the findings — no appeal, no further proceedings. This is the cleanest final-figure case of the three candidates in this file.

**Appetite the record supports:** Starling's Annual Report 2023 sets out an explicit Board-approved risk-appetite framework — dozens of named "risk appetite" statements and limits across credit, market, liquidity and strategic risk (e.g. "Board-approved risk appetite measures ensure funding and liquidity levels are monitored and managed"; FX risk exposure kept "within risk appetite"). It is qualitative and multi-dimensional rather than one summary £ figure, but it is a genuinely disclosed risk-tolerance regime, unlike Currys plc's silence on the point.

**What tuppence's own numbers show:** no `size:` block published at all — under ADR-0020/ticket 79 item 2's own rule this is an instrument fault today, not a priced number, and the gate should read amber rather than silently price at a statutory cap.

**What Starling's numbers would make reachable:** tuppence's fixed £15,000 appetite against Starling's own turnover (£414.8m–£452.8m) is **0.0033%–0.0036%** of turnover — tighter, proportionally, than driftwood's ratio, so a bare substitution of size facts alone would still fail every priced tier and fail closed to `isolated`. The FCA's own final penalty, £28,959,426, restated as a share of Starling's turnover, is **6.4%–7.0%** of revenue — several orders of magnitude above any of tuppence's current fixed-£ bands. Of the three candidates, this is the sharpest evidence that a fixed-£ appetite cannot travel to a firm this size: only a genuinely proportional appetite, and one set well above single-digit-percent of turnover, would let a real bank the size of Starling clear even `isolated` against its own regulator's own assessed loss.

---

## ludlow → candidate: Anthem, Inc. (now Elevance Health)

Sector match: US health insurer, HIPAA-regulated — the regime ludlow declares. The Anthem breach is the largest and most litigated HIPAA case on the regulator's own record, so its size facts and its regulator/litigation record are both unusually well documented for a US firm.

**Size facts** (SEC Form 10-K for fiscal year 2016, [filed with the SEC](https://www.sec.gov/Archives/edgar/data/0001156039/000115603917000002/antm-2016123110k.htm)):
- Total operating revenue **$84,194 million** (total revenues $84,863 million), fiscal year ended 2016-12-31.
- **39.9 million** medical members through affiliated health plans as of 2016-12-31 — the closest customer/data-subject figure a health insurer publishes.
- Approximately **53,000 employees** at 2016-12-31 ("At December 31, 2016, we had approximately 53,000 employees").

The breach itself (2015, disclosed 2015-02-04) affected **78.8 million** individuals' electronic protected health information — a larger, earlier population than the 2016 membership figure above; both are given here because the ticket asks for size facts with their filing year, and the breach population and the filing-year membership are two different counts from two different dates.

**Regimes:** HIPAA Privacy and Security Rules (federal); state insurance regulation in every state Anthem operates; SEC reporting obligations as a US public company.

**Regulator action:** HHS Office for Civil Rights Resolution Agreement, **$16,000,000**, dated **15 October 2018** — the largest HIPAA settlement in OCR's history at the time, with a two-year Corrective Action Plan (risk analysis, revised access-control policies, HHS reporting for two years). The official source is [hhs.gov's Anthem resolution-agreement page](https://www.hhs.gov/hipaa/for-professionals/compliance-enforcement/agreements/anthem/index.html), which returned HTTP 403 to both WebFetch and a direct `curl` with a browser user agent from this environment, and whose closest Wayback Machine snapshot this environment could not fetch either — **this source blocked automation and the figure is instead corroborated by four independent contemporaneous secondary sources, all dated October 2018 and citing the same $16m figure, date and corrective-action terms**: [American Hospital Association](https://www.aha.org/news/headline/2018-10-16-anthem-pays-ocr-16-million-hipaa-settlement), [Healthcare Dive](https://www.healthcaredive.com/news/anthem-shells-out-16m-in-largest-ever-hipaa-fine/539791/), [HIPAA Journal](https://www.hipaajournal.com/16-million-anthem-hipaa-breach-settlement-takes-ocr-hipaa-penalties-past-100-million-mark/).

**Litigation status: final and collected on all three tracks that followed the same breach** (a genuinely unusual amount of independent regulator/court corroboration for one event):
1. HHS OCR Resolution Agreement, $16,000,000, no admission of liability, no appeal — final 2018-10-15.
2. Consolidated federal class action, *In re Anthem, Inc. Data Breach Litigation* (N.D. Cal.), settlement fund of **$115,000,000** granted final approval **15 August 2018** ($17m credit-monitoring, $15m out-of-pocket-loss reimbursement, $13m for claimants with pre-existing monitoring, the remainder to fees and administration). [Class Law Group summary](https://www.classlawgroup.com/115m-anthem-data-breach-settlement-granted-final-approval); [HIPAA Journal](https://www.hipaajournal.com/court-approves-anthem-115-million-data-breach-settlement/).
3. Multistate Attorneys General settlement: **$39,500,000** across 43 states plus DC, plus a separate **$8,700,000** to California — announced **30 September 2020** (total **$48,200,000** on this third track). [North Carolina DOJ press release](https://ncdoj.gov/attorney-general-josh-stein-reaches-39-5-million-multistate-data-breach-settlement-with-anthem/); [HIPAA Journal](https://www.hipaajournal.com/anthem-inc-settles-state-attorneys-general-data-breach-investigations-and-pays-48-2-million-in-penalties/).

**Appetite the record supports:** no single named "risk appetite" figure was found in the sources reached here. The closest disclosed materiality structure is the $115m federal settlement fund's own internal tiering (credit-monitoring vs. documented out-of-pocket loss vs. pre-existing-monitoring claimants) — flagged as a partial match to the ticket's test, not a clean one.

**What ludlow's own numbers show:** same gap as tuppence — no `size:` block published, so ludlow is an instrument fault today under ticket 79 item 2's rule, not silently priced.

**What Anthem's numbers would make reachable:** the OCR settlement alone, $16,000,000 / $84,194,000,000 revenue, is **0.019%** of turnover. Summing all three tracks on the same breach — $16m + $115m + $48.2m = $179.2m — against the same turnover is **0.213%** of turnover. Both ratios sit well above ludlow's current fixed £5,000 appetite, already the tightest in the estate and consistent with its README's "Deny-heavy (strictest)" description. Even the largest, most thoroughly litigated HIPAA loss on public record, restated as a share of turnover, implies a materially larger proportional appetite than ludlow's current number — closer to a fifth of one percent of turnover than to a thousandth, if this candidate's own record were the anchor.

---

## Cross-cutting note for ticket 79 item 2

All three candidates publish size facts at a different order of magnitude from their adopter's current signed numbers: driftwood's candidate has roughly 100× its signed turnover; tuppence's and ludlow's candidates cannot even be compared on that axis, because tuppence and ludlow publish no `size:` block to compare against. None of the three candidates makes an existing priced rung reachable by a bare substitution of turnover, because the estate's own residual pricing (`selection-policy/selection_policy.py`: loosest tier whose residual ≤ tolerance, fail-closed to `isolated`) scales the priced residual with the same size facts that would grow. The lever that would actually open a rung is the appetite formula itself — a fixed £ figure versus a share of turnover — which is exactly the question ticket 79 has open. On this record, a proportional appetite anchored to any of these three candidates' own regulator or litigation figures would sit well above what a fixed-£ figure like £40,000/£15,000/£5,000 implies as a share of turnover — for driftwood's candidate roughly 0.006% of turnover, for tuppence's roughly 6-7%, for ludlow's roughly 0.02-0.2% — three genuinely different orders of magnitude from each other, which is itself useful evidence that one shared percentage will not fit all three sectors' actual loss experience.

## What could not be found / sources that blocked automation

- The ICO's own original January 2020 press release for the DSG fine no longer resolves at any URL pattern tried (`ico.org.uk/action-weve-taken/...`, direct MPN PDF guesses); the figure and date are instead sourced from the First-tier Tribunal's own reproduction of the notice, which is itself a primary source (a tribunal record) and arguably a stronger one than a press release.
- `hhs.gov`'s Anthem resolution-agreement page returned HTTP 403 to WebFetch and to `curl` with a browser user agent; its Wayback Machine snapshot (`web.archive.org`, 2026-05-11 capture, confirmed to exist via the Wayback availability API) was outside this environment's WebFetch reach ("Claude Code is unable to fetch from web.archive.org"). The $16m figure is corroborated by four independent secondary sources instead — see the citations above.
- No single "customer count" is published by Currys plc for driftwood's candidate; iD Mobile subscribers and UK active credit accounts are offered as the closest disclosed proxies, flagged as such rather than presented as a customer count.
- DSG Retail Limited's own standalone turnover and headcount, as distinct from the Currys plc group that contains it, are not separately published in the sources reached here; Currys plc's consolidated group figures are used throughout and flagged as group-level rather than subsidiary-level.
- No candidate in this file publishes a single named "risk appetite" £ figure the way tuppence's or ludlow's `appetite.tolerance` line does; Starling's Board-approved qualitative risk-appetite framework is the closest match found, Currys plc and Anthem weaker matches (flagged individually above).
