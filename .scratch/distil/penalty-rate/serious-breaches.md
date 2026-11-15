# The ICO penalty rate for a serious customer-data breach at a UK retailer

Filed note: this is the third of three counts. `CHOICE.md` calls it "serious breaches". Its check is `serious-breaches-check.md`, which removes one of the four penalties below: the point becomes 0.38% and the range 0.10% to 2.6%. Where the two differ, the check's figures are the ones `CHOICE.md` uses.

Researcher: own method. All sources fetched on 14 November 2026.

## 1. Answer in brief

- **Point estimate: about 1 in 200 (0.5%).**
- **Defensible range: 0.14% to 2.6%.**
- The class counted: breaches reported to the ICO in 2019 to 2022 by commercial-sector organisations, recorded as cyber incidents, affecting 10,000 or more people.
- The numerator is a count: **four penalties**.
- The denominator is not published cleanly. The ICO records size as first reported, and often as "Unknown". Two published counts bracket it:
  - 394 reports recorded at 10,000 or more. Rate 1.0%. Too high, because large breaches recorded as "Unknown" are missing.
  - 2,957 reports recorded at 10,000 or more, or as "Unknown". Rate 0.14%. Too low, because most "Unknown" reports are small.
- The point estimate sits between them. It assumes 10% to 21% of the "Unknown" reports were large, which gives about 800 reports. That step is an estimate, not a count. Section 6 shows it.
- For "Retail and manufacture" alone the count of penalties is zero or one, depending on whose sector label is used. The data cannot tell retail apart from the rest of the commercial sector.
- The rate over all breach reports is 0.03% (13 of 40,501). That is not the rate for a serious breach.
- The model's current value of 1 is too high by a factor of about 200 (between about 40 and 700 across the range).

## 2. The target, and what was fixed when

**An honest note on order.** I located the sources first. Before I counted anything by stratum I had seen file headers, raw totals and the enforcement listing. I then wrote down a list of candidate classes: all reports; commercial sectors; commercial, cyber, customer data, at 10,000 or more and at 100,000 or more; retail; and reports the ICO chose to investigate. I ran all of them in one pass, about twenty rows. I chose which row to lead with after seeing that table. So the class was not fixed blind.

Two choices were made after seeing numbers, and both are shown so the reader can undo them.

- The class I had named in advance was restricted to customer data. I lead instead with the row for any type of data subject, because two of the four penalties (Interserve, Advanced) concerned employees' or patients' data and the ICO's reasoning in them does not turn on whose data it was. The customer-only row is in section 6.
- I first led with the 394 denominator. A check of where the fined cases sit in the ICO's file (section 6c) showed that numerator and denominator used different size measures. I added the "Unknown" rows and moved the point estimate down.

**The right conditional probability.** P(the ICO issues a monetary penalty notice under UK GDPR or the DPA 2018 | a serious breach of customers' personal data occurs at a mid-sized UK online retailer and is reported to the ICO).

**The ideal numerator.** Penalty notices traced back to breach reports in a fixed set of years, matched to the year the breach was reported, not the year of the notice. A penalty arrives 1.5 to 4 years after the report, so matching by notice year mixes cohorts.

**The ideal denominator.** Breach reports from UK online retailers of similar size, involving customer data, above a seriousness threshold by final size, in the same years. The ICO does not publish this. It publishes no turnover band, no "online" flag and no final size.

**What I considered.**

- *Private sector only.* The ICO's stated policy treats public bodies differently (section 7). A public-sector fine tells us little about a retailer. I restrict to commercial sectors.
- *Retail only.* The right class in principle. Too thin to give a rate. Reported as a check with an exact upper bound.
- *Size threshold.* A serious breach at a retailer with GBP 86 million turnover means thousands to millions of customer records. I use 10,000 or more as the main threshold and 100,000 or more as the second.
- *Cyber incidents only.* An online retailer's serious customer-data breach is an external attack in almost every realistic case. Misdirected emails dominate the other category.
- *Reprimands and enforcement notices.* Counted separately (section 8). They carry no fine.
- *ICO policy.* The fining guidance says the decision is discretionary and fact-specific. No rule gives the rate. It has to be counted.

**Matching rule.** Cohort matching is primary. Calendar-year matching is the cross-check.

## 3. Sources

| # | Source | URL | What it gave |
|---|---|---|---|
| S1 | ICO, Data security incident trends, page updated 26 October 2026 | https://ico.org.uk/action-weve-taken/data-security-incident-trends/ | The limitations text quoted in sections 6 and 9 |
| S2 | ICO, incident trends data file, Q1 2019 to Q3 2026 | https://ico.org.uk/media2/iivgw0b0/data-security-incidents-trends-download-q1-2019-to-q3-2026.csv | 237,713 rows, 89,591 distinct incident references. Every denominator by stratum |
| S3 | ICO, Enforcement action listing | https://ico.org.uk/action-weve-taken/enforcement/ | 232 entries dated 22 January 2022 to 4 November 2026. Monetary penalties in it go back only to 14 December 2022, enforcement notices to 15 February 2023. Read through the page's own search endpoint |
| S4 | ICO, Cyber investigations data sets (22 quarterly files, closures January 2021 to June 2026) | https://ico.org.uk/action-weve-taken/complaints-and-concerns-data-sets/cyber-investigations/ | 961 closed investigations with organisation, outcome, start date and, in later files, the date the breach report was received |
| S5 | ICO, Civil investigations data sets (22 quarterly files) | https://ico.org.uk/action-weve-taken/complaints-and-concerns-data-sets/civil-investigations/ | The same for non-cyber cases |
| S6 | ICO Annual Report 2018/19, HC 2299, July 2019 | https://ico.org.uk/media2/migrated/2615262/annual-report-201819.pdf | "we received 13,840 PDB reports during 2018-19"; "there were no monetary penalties under DPA 2018 in 2018-19" |
| S7 | ICO Annual Report 2019/20, HC 477, July 2020 | https://ico.org.uk/media2/migrated/2618021/annual-report-2019-20-v83-certified.pdf | "Personal Data Breaches - Received 2019/20 11,854" |
| S8 | ICO Annual Report 2020/21, HC 354, July 2021 | https://ico.org.uk/media2/migrated/2620166/hc-354-information-commissioners-ara-2020-21.pdf | "Personal Data Breaches - Received 2020/21 9,532"; "In 2020/21 we issued 3 fines, totalling £39.65m" |
| S9 | ICO Annual Report 2021/22, HC 392, July 2022 | https://ico.org.uk/media2/migrated/4021039/ico-annual-report-2021-22.pdf | "Personal data breaches - Received 2021/22 9571"; "We issued four DPA fines totalling £633k and 33 PECR penalties" |
| S10 | ICO Annual Report 2022/23, HC 1440, July 2023 | https://ico.org.uk/media2/migrated/4025864/annual-report-2022-23.pdf | "Received 9,146"; timeline entries for Clearview, Easylife and Interserve |
| S11 | ICO Annual Report 2023/24, HC 30, July 2024 | https://ico.org.uk/media2/migrated/4030348/annual-report-2023-24.pdf | "11,680 cases reported (2022/23: 9,146)"; "three penalty notices totalling £13,057,500 (2022/23: two penalty notices totalling £7,631,200)"; "Clearview AI £7.553m"; timeline, December 2023, "13 Ministry of Defence fined £350,000" |
| S12 | ICO Annual Report 2024/25, HC 956, July 2025 | https://ico.org.uk/media2/1wyfliqp/annual-report-2025-ico-v4-1-complete.pdf | "12,412 cases reported (2023/24: 11,680)"; "We concluded 43 UK GDPR investigation cases (2023/24: 285 investigation cases)" |
| S13 | ICO Annual Report 2025/26, HC 274, July 2026 | https://ico.org.uk/media2/ybsi5n0j/ico-annual-report-202527.pdf | "17,431 cases reported (2024/25: 12,412)"; "eight UK GDPR penalty notices totalling £32,402,373 (2024/25: two penalty notices totalling £3,826,320)" |
| S14 | ICO, Data Protection Fining Guidance, "Circumstances in which the Commissioner would consider it appropriate to issue a penalty notice" | https://ico.org.uk/about-the-ico/our-information/policies-and-procedures/data-protection-fining-guidance/circumstances-in-which-the-commissioner-would-consider-it-appropriate-to-issue-a-penalty-notice/ | Policy quotes in section 7 |
| S15 | ICO, Statement on the public sector approach, 9 December 2024 | https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2024/12/statement-on-the-public-sector-approach/ | Policy quotes in section 7 |
| S16 | ICO enforcement entry pages and the penalty notices linked from them, 2023 to 2026 | Entry URLs in section 4 | Date, amount, article, people affected, date reported |
| S17 | Archived copies of ICO enforcement pages and the penalty notices linked from them, 2019 to 2022 | web.archive.org URLs in section 4 | The same, for entries the ICO has removed from its live site |

Notes on S3 and S17.

- The live listing holds no monetary penalty before 14 December 2022. The ICO has removed older ones. I filled 2019 to 2022 from the annual reports (S7 to S10), the investigations data sets (S4, S5), and archived copies of the ICO's own pages and notices (S17). An archived copy of an ICO page is the ICO's document, held by a third party.
- I also listed every archived enforcement page address for 2019 to 2023 (288 entries) and read the names. I found no UK GDPR penalty beyond those below.
- The listing carries the ICO's own warning: "incorrect results may be produced due to errors with the dates of some documents added before 31 December 2024". Where the listing date and the notice disagree, I used the notice.

## 4. The numerator: every penalty counted

Each row is one breach event. A joint notice to two companies counts once. "Reported" is the date the breach was reported to the ICO, which sets the cohort year.

Where each cell comes from. The date, sector and one-line description come from the entry page in the last column. Amounts and report dates come from the penalty notice linked on that page, unless the "Reported" cell says otherwise. "Case opened" dates come from the investigations files (S4). Row 12's report date comes from S5. The Marriott notice is a scanned image, so row 3 rests on the entry page and S8.

### 4a. Security-breach penalties under UK GDPR or the DPA 2018, notices issued from 25 May 2018 to 30 September 2026

| # | Organisation | Notice date | Amount | What for | Reported | Class | Entry page |
|---|---|---|---|---|---|---|---|
| 1 | Doorstep Dispensaree Ltd | 20 Dec 2019 | £275,000 | About 500,000 documents with patient data left in unlocked containers | Not a breach report. The medicines regulator told the ICO on 31 July 2018 | Private pharmacy, non-cyber | https://web.archive.org/web/20201204110108/https://ico.org.uk/action-weve-taken/enforcement/doorstep-dispensaree-ltd-mpn/ |
| 2 | British Airways | 16 Oct 2020 | £20,000,000 | Cyber attack on booking site. About 429,612 people | 6 Sep 2018 | Commercial, cyber, customers, 100k+ | https://web.archive.org/web/20211217094110/https://ico.org.uk/action-weve-taken/enforcement/british-airways/ |
| 3 | Marriott International Inc | 30 Oct 2020 | £18,400,000 | Cyber attack on Starwood guest database. 339 million records worldwide | Page: attack "remained undetected until September 2018" | Commercial, cyber, customers, 100k+ | https://web.archive.org/web/20220118213406/https://ico.org.uk/action-weve-taken/enforcement/marriott-international-inc/ |
| 4 | Ticketmaster UK Limited | 13 Nov 2020 | £1,250,000 | Payment-page chat bot compromised. Customers' payment details | Breach ended 23 June 2018. Case opened 25 June 2018 | Commercial (ICO tag: Retail and manufacture), cyber, customers, 100k+ | https://web.archive.org/web/20220701173222/https://ico.org.uk/action-weve-taken/enforcement/ticketmaster-uk-limited/ |
| 5 | Mermaids | 8 Jul 2021 | £25,000 | Internal email group left open to the web | 14 Jun 2019 | Charity, non-cyber | https://web.archive.org/web/20220813004143/https://ico.org.uk/action-weve-taken/enforcement/mermaids/ |
| 6 | HIV Scotland | 22 Oct 2021 | £10,000 | Group email sent without blind copy | 3 Feb 2020 | Charity, non-cyber | https://web.archive.org/web/20230226114923/https://ico.org.uk/action-weve-taken/enforcement/hiv-scotland-mpn/ |
| 7 | Cabinet Office | 2 Dec 2021 | £500,000 | New Year Honours addresses published on 27 Dec 2019 | Notice: "within 72 hours of becoming aware". So late December 2019 | Public, non-cyber | https://web.archive.org/web/20220706132531/https://ico.org.uk/action-weve-taken/enforcement/cabinet-office-mpn/ |
| 8 | Tuckers Solicitors LLP | 10 Mar 2022 | £98,000 | Ransomware. Court bundles published | 25 Aug 2020 | Commercial, cyber, under 10k | https://web.archive.org/web/20231208025915/https://ico.org.uk/action-weve-taken/enforcement/tuckers-solicitors-llp-mpn/ |
| 9 | Tavistock and Portman NHS Foundation Trust | 30 Jun 2022 | £78,400 | Bulk email to 1,781 clinic service users | 6 Sep 2019 | Public, non-cyber | https://web.archive.org/web/20240105213731/https://ico.org.uk/action-weve-taken/enforcement/the-tavistock-portman-nhs-foundation-trust/ |
| 10 | Interserve Group Limited | 24 Oct 2022 | £4,400,000 | Cyber attack found on 2 May 2020. Up to 113,000 employees | Case opened 14 May 2020 | Commercial (ICO tag: Retail and manufacture), cyber, employees, 100k+ | https://web.archive.org/web/20231228145431/https://ico.org.uk/action-weve-taken/enforcement/interserve-group-limited/ |
| 11 | Ministry of Defence | 13 Dec 2023 (S11 timeline) | £350,000 | Email to 265 addresses using "To" not "BCC" | 21 Sep 2021 | Public, non-cyber | https://ico.org.uk/action-weve-taken/enforcement/2024/02/ministry-of-defence-1/ |
| 12 | Central YMCA | 6 Mar 2024 | £7,500 | Email to 166 people in an HIV programme using "CC" | 7 Oct 2022 | Charity, non-cyber | https://ico.org.uk/action-weve-taken/enforcement/2024/04/the-central-young-men-s-christian-association-mpn/ |
| 13 | Police Service of Northern Ireland | 26 Sep 2024 | £750,000 | Spreadsheet with 9,483 officers and staff published | 8 Aug 2023 | Public, non-cyber | https://ico.org.uk/action-weve-taken/enforcement/2024/10/police-service-of-northern-ireland-mpn/ |
| 14 | Advanced Computer Software Group Ltd | 26 Mar 2025 | £3,076,320 (S12) | Ransomware, August 2022. 79,404 people. A processor | Not Advanced's own report. Notice: "The ICO contacted Advanced on 5 August 2022 following widespread media reports" | Commercial, cyber, 10k to 100k | https://ico.org.uk/action-weve-taken/enforcement/2025/03/advanced-computer-software-group-limited/ |
| 15 | DPP Law Ltd | 14 Apr 2025 | £60,000 | Cyber attack. 791 clients and experts. Also late reporting | 17 Jul 2022 | Commercial, cyber, under 10k | https://ico.org.uk/action-weve-taken/enforcement/2025/04/dpp-law-ltd/ |
| 16 | 23andMe, Inc | 5 Jun 2025 | £2,310,000 | Cyber attack. 155,592 UK customers | 15 Oct 2023 | Commercial company, cyber, customers, 100k+. ICO case sector: Health | https://ico.org.uk/action-weve-taken/enforcement/2025/06/23andme/ |
| 17 | Birthlink | 24 Jun 2025 | £18,000 | About 4,800 records destroyed | 8 Sep 2023 | Charity, non-cyber | https://ico.org.uk/action-weve-taken/enforcement/2025/06/birthlink/ |
| 18 | Capita plc and Capita Pension Solutions Ltd | 15 Oct 2025 | £14,000,000 | Cyber attack. 6,656,037 people | 31 Mar 2023 | Commercial, cyber, 100k+ | https://ico.org.uk/action-weve-taken/enforcement/2025/10/capita-plc/ |
| 19 | LastPass UK Ltd | 20 Nov 2025 | £1,228,283 | Cyber attack. About 1.6 million UK customers | 30 Nov 2022 | Commercial, cyber, customers, 100k+ | https://ico.org.uk/action-weve-taken/enforcement/2025/11/lastpass-uk-ltd/ |
| 20 | Police Service of Scotland | 12 Dec 2025 | £66,000 plus a reprimand | Mishandling of sensitive personal information. Law-enforcement part of the DPA 2018 | 30 Jun 2022, late | Public, non-cyber | https://ico.org.uk/action-weve-taken/enforcement/2025/12/police-service-of-scotland/ |
| 21 | South Staffordshire Plc and South Staffordshire Water Plc | 7 May 2026 | £963,900 | Cyber attack. About 633,887 people, customers and employees | 24 Jul 2022 | Commercial, cyber, customers, 100k+ | https://ico.org.uk/action-weve-taken/enforcement/2026/05/south-staffordshire-plc-and-south-staffordshire-water-plc/ |

Cross-checks against the annual reports. They confirm the count in every year.

- 2018/19: none (S6).
- 2020/21: "3 fines, totalling £39.65m". Rows 2, 3 and 4 sum to £39.65m (S8).
- 2021/22: "four DPA fines totalling £633k". Rows 5 to 8 sum to £633,000 (S9).
- 2022/23: "two penalty notices totalling £7,631,200" (S11). Clearview at "£7.553m" (S11) plus row 9 gives £7.631m. Interserve and Easylife are in the same year's timeline (S10) but not in that sentence.
- 2023/24: "three penalty notices totalling £13,057,500" (S11). TikTok plus rows 11 and 12 sum to exactly that.
- 2024/25: "two penalty notices totalling £3,826,320" (S13). Rows 13 and 14 sum to exactly that.
- 2025/26: "eight UK GDPR penalty notices totalling £32,402,373" (S13). Rows 15 to 20 plus MediaLab and Reddit sum to exactly that.
- Row 1 was not found in the 2019/20 report text. It rests on the archived ICO page and notice.

Penalty notices for the commercial cyber cases, which carry the rate.

- Interserve: https://web.archive.org/web/2023/https://ico.org.uk/media/action-weve-taken/mpns/4021951/interserve-group-limited-monetary-penalty-notice.pdf
- South Staffordshire: https://ico.org.uk/media2/xdrfahsw/south-staffordshire-plc-and-south-staffordshire-water-plc-monetary-penalty-notice.pdf
- Advanced: https://ico.org.uk/media2/gdlfddgc/advanced-penalty-notice-20250327.pdf
- LastPass: https://ico.org.uk/media2/xfbl1uaa/lastpass-uk-ltd-penalty-notice.pdf
- Tuckers: https://web.archive.org/web/2022/https://ico.org.uk/media/action-weve-taken/mpns/4019746/tuckers-mpn-20220228.pdf
- DPP Law: https://ico.org.uk/media2/pr4bg5hq/dpp-law-ltd-monetary-penalty-notice.pdf
- Capita: https://ico.org.uk/media2/pv5nhks4/capita-plc-and-cpsl-monetary-penalty-notice.pdf
- 23andMe: https://ico.org.uk/media2/kclbljpo/23andme-penalty-notice.pdf
- British Airways: https://web.archive.org/web/2021/https://ico.org.uk/media/action-weve-taken/mpns/2618421/ba-penalty-20201016.pdf
- Ticketmaster: https://web.archive.org/web/2021/https://ico.org.uk/media/action-weve-taken/2618609/ticketmaster-uk-limited-mpn.pdf

Notice dates that disagree. Row 11: the listing says 26 February 2024; the 2023/24 report says 13 December 2023; the investigations file shows closure on 15 December 2023. Row 13: the notice is dated 26 September 2024; the listing says 3 October 2024.

### 4b. Left out, and why

| Left out | Reason |
|---|---|
| Clearview AI, £7.553m (S11), May 2022 | UK GDPR, but unlawful collection of images. Not a security breach. Under appeal |
| Easylife Ltd, 5 Oct 2022 (amount not fetched) | UK GDPR Article 5(1)(a), profiling of customers. Not a security breach. Tagged Retail and manufacture |
| TikTok, £12,700,000, April 2023 | Children's data used unlawfully. Not a security breach |
| MediaLab.AI (Imgur), £247,590, 4 Feb 2026 | Children's data. Not a security breach |
| Reddit, £14,472,500, 23 Feb 2026 | Children's data. Not a security breach |
| DSG Retail Ltd, £500,000, 9 Jan 2020 | A retailer's cyber breach affecting at least 14 million people. Issued under the old 1998 Act for a breach before 25 May 2018 (the Act is from memory, not fetched; the notice is a scanned image). Outside the period |
| Cathay Pacific, £500,000, March 2020 | As DSG. Old regime (from memory, not fetched) |
| All penalties under the Privacy and Electronic Communications Regulations | Nuisance calls, texts and emails. Not data-breach penalties. The listing holds about 50 from December 2022 on, including three tagged Retail and manufacture (It's OK Ltd, HelloFresh, Coastal Windows) |
| Fines for not paying the data protection fee | Not about a breach |
| Guntrader.UK Ltd | A retail-sector cyber case closed in January 2023 with the outcome "MPN not issued" (S4). No penalty |
| Notices of intent | Not penalties |

### 4c. Appeals, reductions and unpaid penalties

I count a penalty when the notice is issued. I do not remove it if it was later reduced, appealed or not collected. The model term is "draws a penalty", and the published record of later outcomes is patchy.

- 23andMe: the investigations file records "Not recoverable" (S4). Counted.
- Capita, LastPass, Advanced, Interserve, Ticketmaster: recorded as "Paid in full" (S4).
- Doorstep Dispensaree was reduced on appeal, and the Cabinet Office penalty was reduced by agreement (both from memory, not fetched). Neither is in the commercial cyber class, so neither changes the rate.

This choice pushes the rate up a little against a "penalty actually paid" definition.

## 5. The denominator, by year

All counts are distinct incident references in S2. The file has one row per incident per data type, so rows were collapsed to incidents first. Years are calendar years of receipt. 2026 is January to September only.

Definitions.

- *Commercial sectors*: Retail and manufacture; Finance, insurance and credit; General business; Legal; Land or property services; Transport and leisure; Online Technology and Telecoms; Utilities; Marketing; Media.
- *Cyber*: Incident Category = "Cyber".
- *10k+*: bands "10k to 100k" and "100k and above". *100k+*: "100k and above". *Unknown*: band "Unknown".
- *Customers*: data subject type includes "Customers or prospective customers", "Users" or "Subscribers".

| Stratum | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 Q1-Q3 | 2019-22 | 2019-23 | All |
|---|---|---|---|---|---|---|---|---|---|---|---|
| All reports | 12,259 | 9,702 | 9,742 | 8,798 | 11,069 | 12,194 | 13,462 | 12,365 | 40,501 | 51,570 | 89,591 |
| Commercial sectors | 5,725 | 4,333 | 4,114 | 3,597 | 4,769 | 4,911 | 5,725 | 5,239 | 17,769 | 22,538 | 38,413 |
| Commercial, cyber | 1,729 | 1,514 | 1,710 | 1,490 | 2,320 | 2,103 | 2,306 | 2,266 | 6,443 | 8,763 | 15,438 |
| **Commercial, cyber, 10k+** | **86** | **90** | **86** | **132** | 172 | 131 | 176 | 241 | **394** | 566 | 1,114 |
| **Commercial, cyber, size Unknown** | **643** | **598** | **828** | **494** | 576 | 438 | 249 | 175 | **2,563** | 3,139 | 4,001 |
| **Commercial, cyber, 10k+ or Unknown** | **729** | **688** | **914** | **626** | 748 | 569 | 425 | 416 | **2,957** | 3,705 | 5,115 |
| Commercial, cyber, 100k+ | 34 | 29 | 28 | 49 | 51 | 42 | 56 | 95 | 140 | 191 | 384 |
| Commercial, cyber, 100k+ or Unknown | 677 | 627 | 856 | 543 | 627 | 480 | 305 | 270 | 2,703 | 3,330 | 4,385 |
| Commercial, cyber, 10k+, customers | 81 | 79 | 72 | 117 | 117 | 110 | 141 | 203 | 349 | 466 | 920 |
| Commercial, cyber, 10k+ or Unknown, customers | 509 | 461 | 385 | 390 | 383 | 319 | 257 | 285 | 1,745 | 2,128 | 2,989 |
| Retail and manufacture, cyber | 299 | 491 | 521 | 453 | 595 | 772 | 808 | 663 | 1,764 | 2,359 | 4,602 |
| Retail and manufacture, cyber, 10k+ | 10 | 40 | 27 | 37 | 50 | 51 | 66 | 80 | 114 | 164 | 361 |
| Retail and manufacture, cyber, 10k+ or Unknown | 93 | 221 | 273 | 197 | 202 | 213 | 143 | 130 | 784 | 986 | 1,472 |
| Retail and manufacture, cyber, 100k+ | 4 | 9 | 7 | 12 | 15 | 18 | 27 | 25 | 32 | 47 | 117 |
| All reports, decision "Investigation Pursued" | 2,080 | 1,857 | 1,209 | 555 | 594 | 404 | 220 | 168 | 5,701 | 6,295 | 7,087 |

The ICO's annual-report totals, by financial year, beside the same months summed from S2.

| Financial year | Annual report | Source | Same months in S2 |
|---|---|---|---|
| 2018/19 | 13,840 | S6 | not in the file |
| 2019/20 | 11,854 | S7 | 11,531 |
| 2020/21 | 9,532 | S8 | 9,453 |
| 2021/22 | 9,571 | S9 | 9,503 |
| 2022/23 | 9,146 | S10 | 9,100 |
| 2023/24 | 11,680 | S11 | 11,582 |
| 2024/25 | 12,412 | S12 | 12,299 |
| 2025/26 | 17,431 | S13 | 14,078 |

The file runs 1% to 3% below the annual reports until 2024/25, and 19% below in 2025/26. The 2025/26 report says one incident produced a large number of separate reports that year. The file's notes say some cases are moved to another system and left out.

## 6. The rate

### 6a. Which years, and why

**Cohort years 2019 to 2022** in both numerator and denominator.

- Not before 2019. "The data starts at Q1 2019 as incidents were recorded differently prior to this period" (S1). The only count for 25 May to 31 December 2018 is the 2018/19 financial-year total, with no size or sector split.
- Not after 2022. The lag from report to notice in section 4a runs from 1.5 years (Tuckers) to 3.8 years (South Staffordshire). The 2022 cohort has had 3.75 to 4.75 years of follow-up by 30 September 2026. The 2023 cohort has had less than the longest lag seen. Later cohorts have produced no penalties yet and cannot be read.
- The 2022 cohort is itself borderline. I keep it and say so.

### 6b. Penalties by cohort year

| Reported in | Penalties traced to that year | Commercial, cyber | of which final size 10k+ | of which final size 100k+ |
|---|---|---|---|---|
| 2018, from 25 May | Ticketmaster, British Airways, Marriott | 3 | 3 | 3 |
| 2019 | Mermaids, Tavistock and Portman, Cabinet Office | 0 | 0 | 0 |
| 2020 | HIV Scotland, Interserve, Tuckers | 2 | 1 (Interserve) | 1 |
| 2021 | Ministry of Defence | 0 | 0 | 0 |
| 2022 | Police Scotland, DPP Law, South Staffordshire, Advanced, Central YMCA, LastPass | 4 | 3 (South Staffordshire, Advanced, LastPass) | 2 |
| 2023 | Capita, PSNI, Birthlink, 23andMe | 2 | 2 | 2 |
| 2024 to 2026 | none yet | 0 | 0 | 0 |

Doorstep Dispensaree is not in the table. It did not start from a breach report.

Cohort 2019 to 2022, commercial, cyber: six penalties. Four had a final size of 10,000 or more: **Interserve, South Staffordshire, Advanced, LastPass**.

### 6c. The size problem: where the fined cases sit in the ICO's file

The numerator's sizes are final, taken from the penalty notices. The denominator's sizes are as first reported: "Data presented is generally based on the information provided when an organisation initially reports a breach" (S1). I checked whether the fined cases sit in the 10k+ band. The file has no names, so I filtered by quarter, sector, cyber and the decision "Investigation Pursued".

- **South Staffordshire** (reported July 2022, Utilities). One incident matches. Its size is "Unknown". The final size was 633,887.
- **Capita** (reported March 2023, General business). Four incidents match: one at "10k to 100k" and three "Unknown". None is at "100k and above". The final size was 6.6 million.
- **LastPass** (reported November 2022, Online Technology and Telecoms). Seven incidents match: two "Unknown", two at "100k and above", one at "10k to 100k", two smaller. Not decidable.
- **Interserve.** Too many candidates. Not decidable.
- **Advanced.** Not in the file under its own name at all. Advanced was a processor. Its notice says "The ICO contacted Advanced on 5 August 2022 following widespread media reports". The breach reports came from its customers. The file for that quarter shows a cluster of health-sector ransomware reports of unknown size.

So at least one of the four headline penalties was not in the 394. The 394 understates the true number of large breaches, and 4 of 394 overstates the rate.

The published bracket is therefore:

- **Narrow: 394.** Reports recorded at 10k+ on first report.
- **Wide: 2,957.** Those plus every report recorded as "Unknown".

How many of the 2,563 "Unknown" reports were really large? Not published. Two rough readings:

- If "Unknown" reports have the same size mix as reports of known size (394 of 3,880 are 10k+, or 10.2%), about 260 were large. Total about 650.
- The ICO pursued an investigation in 65% of 10k+ reports (256 of 394), 41% of known smaller reports (1,422 of 3,486) and 46% of "Unknown" reports (1,182 of 2,563). If "Unknown" is a mix of the two, about 21% were large, or about 540. Total about 930.

I take **about 800** as the central denominator. This is an estimate with a stated assumption, not an ICO count.

### 6d. Rates, with exact Poisson 95% intervals on the numerator

Headline class: commercial, cyber, final size 10k+, cohort 2019 to 2022. Four penalties.

| Denominator | Penalties | Reports | Rate | 95% interval |
|---|---|---|---|---|
| Narrow, published: recorded 10k+ | 4 | 394 | 1.02% | 0.28% to 2.60% |
| **Central, estimated: recorded 10k+ plus 10% to 21% of Unknown** | **4** | **about 800 (650 to 930)** | **0.5% (0.43% to 0.61%)** | **0.14% to 1.28%** |
| Wide, published: recorded 10k+ or Unknown | 4 | 2,957 | 0.14% | 0.04% to 0.35% |
| Wide, with all six commercial cyber penalties as numerator | 6 | 2,957 | 0.20% | 0.07% to 0.44% |

Sensitivity: without Advanced. Its case did not start from its own breach report, so it is arguably outside the population of reports. With three penalties the rates are 0.76% narrow (3 of 394), about 0.4% central (3 of about 800) and 0.10% wide (3 of 2,957). I keep four in the headline because the breach was reported, by Advanced's customers, and a retailer's processor could put it in the same position.

The same bracket for other choices. "Narrow" uses the recorded band alone. "Wide" adds the Unknown reports.

| Class | Penalties | Narrow reports | Narrow rate | Wide reports | Wide rate |
|---|---|---|---|---|---|
| Commercial, cyber, 100k+, cohort 2019-22 | 3 | 140 | 2.14% | 2,703 | 0.11% |
| Commercial, cyber, 10k+, customer data only, cohort 2019-22 | 2 | 349 | 0.57% | 1,745 | 0.11% |
| Commercial, cyber, 10k+, cohort 2019-23 | 6 | 566 | 1.06% | 3,705 | 0.16% |
| Commercial, cyber, 10k+, calendar match, notices and reports January 2019 to September 2026 | 9 | 1,114 | 0.81% | 5,115 | 0.18% |

Rates that do not depend on size.

| Class | Penalties | Reports | Rate | 95% interval |
|---|---|---|---|---|
| Commercial, cyber, any size, cohort 2019-22 | 6 | 6,443 | 0.09% | 0.03% to 0.20% |
| Commercial, all types, cohort 2019-22 | 6 | 17,769 | 0.03% | 0.01% to 0.07% |
| All sectors, all reports, cohort 2019-22 | 13 | 40,501 | 0.03% | 0.02% to 0.05% |
| All sectors, all reports, calendar match | 21 | 89,591 | 0.02% | 0.01% to 0.04% |

Notes.

- The customer-only row drops Interserve (employees) and Advanced (a processor holding patients' data).
- The 2019-23 row counts 23andMe as commercial. The ICO filed its case under Health, so it is not in that denominator. Without it the narrow rate is 5 of 566 (0.88%).
- The calendar row counts British Airways, Marriott and Ticketmaster against reports from 2019 on, although those breaches were reported in 2018. That is the known flaw of calendar matching.
- Cohort and calendar matching agree closely: 1.0% and 0.8% narrow, 0.14% and 0.18% wide.

### 6e. Retail alone

| Class, cohort 2019-22 | Penalties | Reports | Rate | 95% upper bound |
|---|---|---|---|---|
| Retail and manufacture, cyber, any size | 0 or 1 | 1,764 | 0 to 0.06% | 0.21% if 0; 0.32% if 1 |
| Retail and manufacture, cyber, recorded 10k+ | 0 or 1 | 114 | 0 to 0.88% | 3.2% if 0; 4.9% if 1 |
| Retail and manufacture, cyber, recorded 10k+ or Unknown | 0 or 1 | 784 | 0 to 0.13% | 0.47% if 0; 0.71% if 1 |

- "0 or 1" is Interserve. The ICO's enforcement page tags it "Retail and manufacture". It is an outsourcing and construction group, and the data was employees'. No penalty in the cohort went to a business that sells goods to consumers.
- Ticketmaster is also tagged "Retail and manufacture" and is the closest case to an online retailer: card details skimmed from a payment page. It was reported in June 2018, before the denominator file starts.
- The retail counts are compatible with the commercial rate. They cannot confirm or reject it.

### 6f. The interval

**Low 0.14%, point 0.5%, high 2.6%.**

- **Low, 0.14%.** Four penalties over the wide published denominator (2,957). This treats every size-unknown report as a large breach. The true rate for a large breach cannot reasonably be lower, short of bad luck in four events.
- **High, 2.6%.** The upper Poisson bound on four penalties over the narrow published denominator (394). This treats no size-unknown report as large, which section 6c shows is false, and then allows for sampling error on top. It also leaves room for late penalties on the 2021 and 2022 cohorts and for the 2018 cohort, where three large consumer-facing cyber breaches reported within seven months each drew a penalty.
- **Point, 0.5%.** Four penalties over about 800.
- The interval mixes two kinds of doubt: which denominator, and chance in a count of four. I have not multiplied them at both ends. Doing so gives 0.04% to 2.6%.

## 7. The ICO's stated policy on when it fines

- The decision is discretionary: "The Commissioner will assess each case individually, taking into account the relevant circumstances, before deciding whether it is appropriate to exercise the Commissioner's administrative discretion to issue a penalty notice." (S14)
- Three tests: "the seriousness of the infringement or infringements; any relevant aggravating or mitigating factors; and whether imposing a fine would be effective, proportionate and dissuasive." (S14)
- A fine is one option among several: "the Commissioner will consider whether to impose a fine as well as, or instead of, other corrective measures." (S14)
- Past cases do not bind: "The Commissioner is not bound by previous decisions, but will ensure there is broad consistency in the approach taken". (S14)
- Public bodies are treated differently: "we would increase the use of my wider powers, including warnings, reprimands and enforcement notices, with fines only issued when necessary." and "If the public sector approach had not been applied, the fines could have reached £23.2m, instead of £1.2m." (S15)

What this means for the count. A penalty needs a security failing the ICO judges serious, not merely a breach. A public-sector rate understates what a private firm faces, which is why the headline class is commercial only.

## 8. Reprimands and enforcement notices, as a separate figure

These carry no fine. They are not in the rate.

- **Reprimands, commercial, cyber.** The cyber investigations files (S4) record 23 "Reprimand" outcomes among 961 investigations closed from January 2021 to June 2026. Fifteen went to commercial organisations.
  - Ten have a report date or case start date in 2020 to 2022: Gain Capital, LOQBOX, Swinburne Snowball and Jackson, Direct Clothing Company, Travel Healthcare Insurance Solutions, Nohow International, My Media World, Gap Personnel, Optionis, GRS.
  - Four have no date in the files: Houzz, People's Energy, Blackbaud, Rematch Credit. Their investigations closed in 2021. The year in a case reference is not a report year, so I do not assign them to a cohort.
  - One, Levales Solicitors, was reported in 2023.
- **Penalty or reprimand, commercial cyber reports 2019-22:** between (6 + 10) and (6 + 14) of 6,443, or 0.25% to 0.31%. The reprimand records carry no size band, so this cannot be put on the 10k+ class.
- **Retail.** Three of the ten dated reprimands are retail by the ICO's case sector or by trade: Direct Clothing Company (an online clothing retailer whose payment page was skimmed, the nearest case to the one being priced), Nohow International and Gap Personnel. Three of 1,764 retail cyber reports is 0.17%.
- **This is an undercount.** The files only cover investigations closed from January 2021. The ICO only committed to publishing reprimands "from 2022 onwards" (S3, entry dated 4 October 2022).
- **Enforcement notices.** The listing holds 58, the oldest dated 15 February 2023. A keyword scan of their descriptions left eight that are not plainly about marketing or freedom of information. I read those eight. None went to a commercial organisation for a security breach.

For a retailer, a reprimand has been more likely than a penalty. The record shows three reprimands and no penalty for retail businesses in the cohort.

## 9. What the rate means, and which way each assumption pushes

1. **It is a rate per reported breach.** A breach that is never reported cannot be fined through this route. A serious customer-data breach must be reported, so this matters little here. Direction: neutral.
2. **Size is as first reported, and often unknown.** This is the largest source of doubt. Section 6c deals with it. The central figure depends on the share of "Unknown" reports that were large. A share of 0% gives 1.0%. A share of 100% gives 0.14%.
3. **Reports first recorded as small that later proved large** are not counted in any of the denominators. Direction: true rate **lower**.
4. **Some serious cases are missing from the file.** "Under specific circumstances some cases are transferred to a separate system for review. As a result, these cases, which may include some of the larger and more serious breaches, are not included within this data." (S1) Direction: denominator too small, true rate **lower**.
5. **Right-censoring.** A 2021 or 2022 report could still draw a penalty. Direction: true rate **higher**. One more penalty would move 0.5% to about 0.6%.
6. **The 2018 cohort is left out.** British Airways, Marriott and Ticketmaster were all fined, and all three are consumer-facing online businesses. Direction: true rate **higher** if the ICO still acts as it did in 2018. It may not. See item 9.
7. **Commercial sectors stand in for online retail.** The retail-only count is zero or one. Direction: unknown.
8. **The ICO's sector labels are not consistent.** Interserve is tagged retail on its enforcement page. 23andMe is filed under Health in the case data and General business on its enforcement page. Sector-level rates are fragile. Direction: unknown.
9. **Enforcement posture changes over time.** Reports with the decision "Investigation Pursued" fell from 2,080 in 2019 to 220 in 2025. The ICO "concluded 43 UK GDPR investigation cases (2023/24: 285)" (S12). Against that, 2025/26 saw eight UK GDPR penalty notices, the most in any year (S13). Direction: unknown. A past rate is not a forecast.
10. **Penalty means notice issued.** Reduced, appealed and uncollected penalties are counted. Direction: slightly **higher** than a "paid" rate.
11. **Size of firm.** The twelve fined commercial organisations range from two small law firms to British Airways. There is no sign that a mid-sized firm is treated differently. Direction: unknown.
12. **The rate is not the cost.** Penalties in the commercial cyber class ran from £60,000 to £20 million. The model needs a separate term for amount.
13. **Timing.** The penalty arrives 1.5 to 4 years after the report. A yearly loss model should date or discount it accordingly.

## 10. What I could not fetch

- The final size of reported breaches, or any ICO count of large breaches by final size. This is the gap that matters most.
- A count of breach reports by size or sector for 25 May to 31 December 2018. Only the 2018/19 financial-year total exists (13,840), and it includes about eight weeks before 25 May 2018.
- Any ICO count of breach reports by turnover, or for online retailers as a class.
- The size band of each reprimand case, and the report dates of four reprimand cases.
- The live ICO pages for penalties before December 2022. They have been removed. Archived copies were used.
- The text of the Marriott and DSG Retail notices. Both are scanned images.
- The Easylife penalty amount.
- The exact Clearview amount. The 2023/24 report gives £7.553m.
- The later reductions of the Doorstep Dispensaree and Cabinet Office penalties, and the Act under which DSG Retail and Cathay Pacific were fined. These are stated from memory, marked as such, and not used in any rate.
- Which incident in the file is which organisation. The file has no names, so section 6c is a match by quarter and sector, not an identification.
- The National Archives web archive would not return page text to a plain fetch. The Internet Archive was used instead.
