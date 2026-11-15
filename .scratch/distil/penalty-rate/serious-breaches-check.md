# Check of the own-method count of the ICO penalty rate

Filed note: the count checked below is `serious-breaches.md`. `CHOICE.md` calls it "serious breaches" and uses this check's corrected figures.

Checker's report. All sources fetched on 15 November 2026.

## 1. Verdict

- The count mostly holds. Every denominator I recomputed matches the ICO file exactly (section 5 lists them). Every figure I checked matches its source page, and the Poisson arithmetic is right. I found no missed UK GDPR security-breach penalty.
- One choice changes the headline. The researcher kept Advanced Computer Software Group in the numerator and disclosed it as a judgement, with a three-penalty sensitivity. I decide it the other way. The notice says Advanced was a processor, had no duty to report and did not report. So its fine does not arise from a breach report by the fined organisation, and it falls outside the researcher's own class ("breaches reported to the ICO by commercial-sector organisations").
- **Corrected headline: 3 penalties, not 4.**
  - Point: 3 of about 800 = **0.38%, about 1 in 270** (was 0.5%).
  - Low: 3 of 2,957 = **0.10%** (was 0.14%).
  - High: **2.6%, unchanged.** Section 6 explains why.
- Five smaller errors, overstatements or gaps are listed in section 4. None of them changes the rate.

## 2. The target, written down before checking numbers

- **The right conditional probability.** P(the ICO issues a monetary penalty to the retailer under UK GDPR or the DPA 2018 | a serious breach of customers' personal data at a mid-sized UK online retailer, reported to the ICO).
- **The best numerator.** Penalties to the controller whose breach it was. Commercial organisations only. Cyber or other security failures that hit customer data. Matched to the year the breach was reported. A penalty to someone else (a processor, say) is not a penalty to the retailer.
- **The best denominator.** Reports by commercial controllers in the same years, cyber, above a size threshold by final size, one count per breach event. The ICO does not publish final size, events or an "online retail" flag. The nearest published counts are recorded size bands per report in the data security incident trends file.
- **Choices I would test.**
  - Private sector or retail only: the public-sector approach (statement of 9 December 2024) makes public fines a poor guide.
  - A size threshold.
  - Reprimands and enforcement notices as a separate figure.
  - The ICO's fining policy, which is discretionary and gives no rate.
- The researcher's target and class match this, except for including Advanced (section 3) and including employee data (Interserve). The customer-only row covers the second point.

## 3. The numerator

### 3a. Headline penalties, checked against the notices

| Organisation | Notice | Amount | People | Reported | Check |
|---|---|---|---|---|---|
| Interserve Group Ltd | 24 Oct 2022 | £4,400,000 | "up to 113,000 employees" | Self-reported, 2020 (attack 30 Mar to 2 May 2020) | Holds. Archived notice: "The amount of the penalty is £4,400,000"; "The infringement was self-reported in a timely manner to the Commissioner and NCA by Interserve." Archived entry page: "Date 24 October 2022 Type Monetary penalties Sector Retail and manufacture". Cyber investigations file: start 14/05/2020, "Paid in full". |
| LastPass UK Ltd | 20 Nov 2025 | £1,228,283 | about 1.6 million UK | 30 Nov 2022 | Holds. Notice: "a penalty of £1,228,283"; "On 30 November 2022, LastPass submitted a personal data breach". |
| South Staffordshire Plc and South Staffordshire Water Plc | 7 May 2026 | £963,900 | about 633,887 | 24 Jul 2022 | Holds. Notice para 20: "South Staffordshire reported a personal data breach to the ICO on 24 July 2022." Para 24: "approximately 633,887 UK data subjects". |
| Advanced (fined entities: Advanced Health and Care Ltd and Aston Midco Ltd) | 26 Mar 2025 | £3,076,320 | 79,404 | **Not reported by Advanced** | Figures hold. **I exclude it.** See 3b. |

Notice URLs:

- Interserve: https://web.archive.org/web/2023/https://ico.org.uk/media/action-weve-taken/mpns/4021951/interserve-group-limited-monetary-penalty-notice.pdf
- LastPass: https://ico.org.uk/media2/xfbl1uaa/lastpass-uk-ltd-penalty-notice.pdf
- South Staffordshire: https://ico.org.uk/media2/xdrfahsw/south-staffordshire-plc-and-south-staffordshire-water-plc-monetary-penalty-notice.pdf
- Advanced: https://ico.org.uk/media2/gdlfddgc/advanced-penalty-notice-20250327.pdf

### 3b. Why Advanced comes out

The Advanced notice says:

- Para 17: "In relation to the Incident, AHC was acting as a data processor ... The Commissioner has therefore considered Advanced's obligations in the context of its role as a data processor only."
- Para 32: "The UK GDPR does not impose any obligations on data processors to notify the Commissioner of a personal data breach."
- Para 33: "The ICO contacted Advanced on 5 August 2022 following widespread media reports of disruption to NHS services."
- Para 37: "Advanced notified all potentially impacted data controller customer entities on 5 August 2022."
- Para 40: "personal data was exfiltrated from Staffplan and Caresys only with 16 data controllers impacted." Para 112 speaks of "Advanced's healthcare data controller customer entities, for example NHS 111".

The main reason needs no inference. The fined organisation did not report the breach and had no duty to. Whatever reports exist came from its customers, the controllers, and the fine went to someone else.

A second reason is my reading, not a fact I could confirm. The controllers were care and health providers, so their reports most likely sit under Health or Social care in the incident file, not in the commercial denominator. The file has no names, so this cannot be confirmed. For scale: in Q3 2022 there are 31 Health cyber reports with the decision "Investigation Pursued", 20 of them of unknown size.

It also answers a different question. The model asks whether the retailer is fined. A processor's fine is not the retailer's fine. The researcher's argument for keeping it ("a retailer's processor could put it in the same position") is about the processor's risk, not the retailer's.

The researcher already gave the three-penalty figures as a sensitivity: 0.76% narrow, about 0.4% central, 0.10% wide. Those become the headline.

### 3c. Searching for missed or wrongly counted penalties

- **Live enforcement listing.** I read it through the page's own search endpoint. It holds 232 entries from 22 January 2022 to 4 November 2026: 65 tagged monetary penalties, 58 enforcement notices and 104 reprimands. The researcher's figures of 232 entries and 58 enforcement notices hold. Apart from PECR and other marketing penalties, the only UK GDPR penalties listed are the ones already in the researcher's tables: South Staffordshire, Reddit, MediaLab, Police Scotland, LastPass, Capita, Birthlink, 23andMe, DPP Law, Advanced, PSNI, Central YMCA, MoD and TikTok. Allay Claims (15 January 2026) is "unsolicited SMS", so it is PECR, which is right. None missed.
- **Cyber investigations data sets** (22 quarterly files, https://ico.org.uk/action-weve-taken/complaints-and-concerns-data-sets/cyber-investigations/). Penalty-type outcomes: British Airways and Marriott ("Civil monetary penalty pursued"), Tuckers ("Fine - higher tier"), Ticketmaster, Interserve, Capita, LastPass and OneAdvanced ("Paid in full"), and 23andMe ("Not recoverable"). Guntrader is "MPN not issued". All are accounted for in the report.
- **Civil investigations data sets** (https://ico.org.uk/action-weve-taken/complaints-and-concerns-data-sets/civil-investigations/). I parsed all 44 CSV files on the page, investigations and incidents together; 21 of them are named as investigations files. Penalty-type outcomes: HIV Scotland, Cabinet Office, Mermaids, Tavistock and Portman, TikTok, MoD, Central YMCA, PSNI, Birthlink, Imgur, Reddit, Police Scotland, plus Trustopia ("Not recoverable"; a PECR case, so rightly left out). No commercial security-breach penalty is missing.
- **The annual-report totals** reconcile exactly with the researcher's list:
  - 2020/21: BA plus Marriott plus Ticketmaster = £39.65m.
  - 2021/22: four fines = £633k.
  - 2023/24: TikTok plus MoD plus Central YMCA = £13,057,500.
  - 2024/25: PSNI plus Advanced = £3,826,320.
  - 2025/26: eight notices = £32,402,373. I re-added them: 60,000 + 2,310,000 + 18,000 + 14,000,000 + 1,228,283 + 66,000 + 247,590 + 14,472,500 = 32,402,373.
- **Numerator cut-off.** The live listing shows no UK GDPR security penalty between 30 September and 4 November 2026. Its only monetary penalty in that window is Bluon Energy (4 November 2026), a PECR case.
- **Before December 2022** the live listing holds no penalties. My search for that period rests on the investigations data sets (closures from January 2021) and the annual-report totals. I did not repeat the researcher's read of 288 archived enforcement page addresses.
- Exclusions (PECR, old-regime DSG and Cathay, non-security UK GDPR cases) are right.

## 4. Other errors and overstatements (no effect on the rate)

1. **"Cross-checks ... confirm the count in every year" is overstated.** The 2022/23 sentence, "two penalty notices totalling £7,631,200", is in the 2022/23 report's "Civil investigations" paragraph. It covers Clearview and Tavistock. It does not count Interserve, a cyber case. The 2022/23 report supports Interserve only through its timeline ("24 Interserve fined £4.4m"). For 2019/20, Doorstep Dispensaree is not in the report, as the researcher admits. The count is right; the claim of confirmation in every year is not.
2. **The second "Unknown" reading is mis-computed.** Using the researcher's own shares, (1,182/2,563 − 1,422/3,486) / (256/394 − 1,422/3,486) = 22.0%, not 21%. That gives about 564 large reports, not 540, and a total of about 958, not 930. The central range is 650 to 960. The point of 800 still sits inside it.
3. **Police Scotland is described as "law-enforcement part of the DPA 2018".** The notice finds infringements under both Part 3 of the DPA and the UK GDPR (Articles 5(1)(f), 32(1), 25 and 33). Its report date of 30 June 2022 holds: "The breach was not reported until 30 June 2022". It is public sector and not in the headline.
4. **The lag range is stated too widely.** Section 6a says the lag from report to notice "in section 4a runs from 1.5 years (Tuckers) to 3.8 years (South Staffordshire)". Two rows in the researcher's own table 4a have shorter lags:
   - PSNI: reported 8 August 2023, notice 26 September 2024, about 1.1 years. The civil file confirms the received date of 08/08/2023.
   - Central YMCA: reported 7 October 2022, notice 6 March 2024, about 1.4 years. The civil file confirms 07/10/2022.

   The range holds for the commercial cyber rows only. The shortest of those is Tuckers, at 1.5 years. The 3.8-year maximum (South Staffordshire, 24 July 2022 to 7 May 2026) holds. The cohort cut-off at 2022 still stands.
5. **A missing assumption: reports versus events.** The numerator counts one penalty per breach event. The denominator counts reports. One supply-chain incident can produce many reports from different controllers (Capita and Advanced are examples). So the denominator over-counts events, and the per-event rate is **higher** than the per-report rate. Section 9 of the report does not list this.

## 5. The denominator and the years, checked

I downloaded the incident file (https://ico.org.uk/media2/iivgw0b0/data-security-incidents-trends-download-q1-2019-to-q3-2026.csv). It has 237,713 data rows and 89,591 distinct references. No reference has more than one sector, size, category or year. I used the same sector list and bands as the researcher. Every figure below matches the report exactly.

| Stratum | 2019 | 2020 | 2021 | 2022 | 2019-22 |
|---|---|---|---|---|---|
| All reports | 12,259 | 9,702 | 9,742 | 8,798 | 40,501 |
| Commercial, cyber | 1,729 | 1,514 | 1,710 | 1,490 | 6,443 |
| Commercial, cyber, 10k+ | 86 | 90 | 86 | 132 | 394 |
| Commercial, cyber, Unknown size | 643 | 598 | 828 | 494 | 2,563 |
| Commercial, cyber, 10k+ or Unknown | 729 | 688 | 914 | 626 | 2,957 |
| Commercial, cyber, 100k+ | 34 | 29 | 28 | 49 | 140 |
| Commercial, cyber, 10k+, customers | 81 | 79 | 72 | 117 | 349 |
| Retail and manufacture, cyber, 10k+ | 10 | 40 | 27 | 37 | 114 |

- I also recomputed the other rows of the researcher's table 5, and they match:
  - all-reports and commercial-sectors rows for every year;
  - every column of the 2023 to 2026 figures;
  - retail cyber any size (1,764) and retail cyber 100k+ (4, 9, 7, 12; total 32);
  - "Investigation Pursued" by year (2,080, 1,857, 1,209, 555, 594, 404, 220, 168).
- The financial-year sums from the file match the researcher's "same months" column: 11,531 (2019/20), 9,453, 9,503, 9,100, 11,582, 12,299 and 14,078 (2025/26).
- Investigation shares hold: 256 of 394, 1,182 of 2,563 and 1,422 of 3,486.
- The cyber investigations files hold 961 non-blank rows when read with a proper CSV parser, which matches the researcher's 961.
- The section 6c matches hold:
  - Q3 2022, Utilities, cyber, Investigation Pursued: one incident, size "Unknown".
  - Q1 2023, General business: four incidents, one at 10k to 100k and three Unknown.
  - Q4 2022, Online Technology and Telecoms: seven incidents with the size mix stated.
- The S1 limitations text is quoted correctly: "The data starts at Q1 2019 as incidents were recorded differently prior to this period"; "Data presented is generally based on the information provided when an organisation initially reports a breach"; "these cases, which may include some of the larger and more serious breaches, are not included within this data". The page shows "26 October 2026 – Data updated to Q3 2026".
- **Years match.** The numerator is penalties traced to breaches reported in 2019 to 2022. The denominator is reports received in 2019 to 2022. The cohort years of the three remaining headline penalties are 2020, 2022 and 2022, and each was checked against its notice.
- The annual-report denominators hold: 13,840 (2018/19), 11,854, 9,532, "9571", 9,146, 11,680, 12,412 and 17,431. One small ICO inconsistency: the 2022/23 report's chart gives 2020/21 as 9,523, not 9,532. It does not affect anything.

## 6. The rate and the interval, corrected

Exact Poisson 95% limits: 3 events gives 0.619 to 8.767. 4 events gives 1.090 to 10.242. 6 events gives 2.202 to 13.060.

| Reading | Penalties | Reports | Rate | 95% interval |
|---|---|---|---|---|
| Narrow, published (recorded 10k+) | 3 | 394 | 0.76% | 0.16% to 2.23% |
| **Central, estimated (about 800; range 650 to 960)** | **3** | **about 800** | **0.38% (0.31% to 0.46%)** | **0.08% to 1.10%** |
| Wide, published (recorded 10k+ or Unknown) | 3 | 2,957 | 0.10% | 0.02% to 0.30% |
| Customer data only, narrow / wide | 2 | 349 / 1,745 | 0.57% / 0.11% | |
| 100k+, narrow / wide | 3 | 140 / 2,703 | 2.14% / 0.11% | |
| Researcher's headline, with Advanced, narrow | 4 | 394 | 1.02% | 0.28% to 2.60% |
| Sensitivity: add the 2018 cohort (BA, Marriott, Ticketmaster) to the narrow reading, with an estimated 2018 denominator of about 50 (seven months at the 2019 rate of 86 a year; my estimate, not an ICO count) | 6 | about 444 | about 1.35% | up to about 2.9% |

**Corrected interval: 0.10% to 2.6%, point 0.38%.**

- **Low, 0.10%.** The researcher's rule applied to three penalties: the wide published denominator. Customer-only wide (0.11%) and 100k+ wide (0.11%) sit just above it.
- **High, 2.6%, kept.** The researcher's rule applied to three penalties would give 2.2%. I do not lower it, for three reasons:
  - 2.2% barely holds the 100k+ narrow point rate of 2.14%.
  - The 2021 and 2022 cohorts are right-censored. South Staffordshire took 3.8 years, so one more penalty from them is plausible.
  - Including the 2018 cohort, the most retail-like cases (BA and Ticketmaster: card data taken from consumer web pages), pushes the narrow upper limit to about 2.9%.
- So 2.6% is a judgement, not a bound computed from three penalties. It holds every point rate from the alternative choices above: 2.14%, about 1.35%, 1.02%, 0.88% retail and 0.76%.
- **Is the original interval wide enough?** At the top, yes for point rates. The 2018-cohort sensitivity exceeds it (about 2.9%) only once Poisson sampling error is added. At the bottom, 0.14% did not hold the three-penalty wide reading (0.10%) or the customer-only wide reading (0.11%). It should drop to 0.10%.

## 7. Reprimands and enforcement notices, checked

- The cyber files hold 23 "Reprimand" outcomes. Fifteen went to commercial organisations: Houzz, Blackbaud, Rematch Credit, People's Energy, Direct Clothing, Swinburne Snowball and Jackson, Gain Capital, LOQBOX, Travel Healthcare Insurance Solutions, My Media World, Nohow, Gap Personnel, Optionis, GRS and Levales.
- Ten have a received or start date in 2020 to 2022, and four have no date. Both counts hold.
- One caution: for Gain Capital, LOQBOX, Swinburne, Direct Clothing and Travel Healthcare, the date is the investigation start, not the report date. Some could be 2019 reports.
- 16 to 20 of 6,443 gives 0.25% to 0.31%. 3 of 1,764 gives 0.17%. The arithmetic holds.
- The listing confirms the ICO's commitment "to publish all reprimands from 2022 onwards" (entry dated 4 October 2022). The oldest enforcement notice is dated 15 February 2023 (It's OK Ltd, a PECR case), which also holds.

## 8. Policy quotes, checked

All quoted text was found on the pages:

- Fining guidance (https://ico.org.uk/about-the-ico/our-information/policies-and-procedures/data-protection-fining-guidance/circumstances-in-which-the-commissioner-would-consider-it-appropriate-to-issue-a-penalty-notice/):
  - "assess each case individually ..."
  - "the seriousness of the infringement or infringements; any relevant aggravating or mitigating factors; and whether imposing a fine would be effective, proportionate and dissuasive"
  - "as well as, or instead of, other corrective measures"
  - "not bound by previous decisions"
- Public-sector statement (https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2024/12/statement-on-the-public-sector-approach/):
  - "with fines only issued when necessary"
  - "the fines could have reached £23.2m, instead of £1.2m"

## 9. Which way the remaining assumptions push

The researcher's section 9 is sound. Add:

- **Reports, not events** (section 4, item 5). The true per-event rate is **higher**.
- **Fixing Advanced.** This removes an upward bias from the original headline.
- **2018 cohort excluded.** This is the single choice that most lowers the rate. All three penalties traced to that cohort were consumer-facing cyber breaches. Direction: **higher**, if the ICO's 2018 to 2020 posture still applies.

## 10. What I could not check

- Whether Interserve's report sits under "Retail and manufacture" in the incident file. The file has no names.
- The final size of any report in the file, and any count by final size.
- A denominator for 25 May to 31 December 2018. The 2018 figure in section 6 is my estimate and is not used in the corrected point.
- The Marriott notice text (scanned image). I checked the archived entry page only: "Date 30 October 2020", "£18.4million", "remained undetected until September 2018".
- The notices behind the report dates of Mermaids, HIV Scotland, Cabinet Office and Tavistock, and Doorstep Dispensaree's regulator referral date. I fetched only the entry pages and the investigations files. None of these is in the headline.
- The Easylife amount, the Clearview entry page, and the DSG and Cathay regime. Not fetched by me either. None is used in the rate.
- I did not repeat the researcher's read of 288 archived enforcement page addresses for 2019 to 2023.
- I did fetch these, and they hold:
  - Entry pages, by date, amount and description:
    - archived: Doorstep Dispensaree (20 December 2019, £275,000, sector Health), Mermaids (8 July 2021, £25,000), HIV Scotland (22 October 2021), Cabinet Office (2 December 2021, £500,000), Tavistock and Portman (30 June 2022, 1,781 service users), Ticketmaster (13 November 2020, £1.25 million, sector Retail and manufacture) and British Airways (16 October 2020, £20m);
    - live: MoD (listed 26 February 2024, £350,000), Central YMCA (6 March 2024, 166 people), PSNI (listed 3 October 2024, £750,000), Birthlink (24 June 2025, £18,000), TikTok (15 May 2023, £12,700,000), Reddit (23 February 2026, £14,472,500), MediaLab (4 February 2026, £247,590), Advanced (26 March 2025, £3.07m, sector General business), LastPass and South Staffordshire.
  - British Airways notice: "approximately 429,612 individuals"; "notifying the Commissioner of the Attack on 6 September 2018"; "final penalty ... £20 million".
  - Ticketmaster notice: "£1,250,000.00"; incident "25 May 2018 to 23 June 2018".
  - Tuckers notice: "£98,000"; "25 August 2020 is the date on which Tuckers reported the breach".
  - DPP Law notice: £60,000, 791 people, breach report 17 July 2022.
  - Capita notice: £14,000,000, 6,656,037 people, "reported the incident to the Commissioner at 18:30 on 31 March 2023".
  - 23andMe notice: £2,310,000, 155,592 UK customers, first notified 15 October 2023.
