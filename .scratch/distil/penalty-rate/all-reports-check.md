# Check of the "all reports" penalty rate

Filed note: "the count" below is `all-reports.md`. The choice built on the three counts is `CHOICE.md`.

Checked on 15 November 2026. I re-fetched the sources the count cites and tested each figure against the page or file. I also searched the ICO's enforcement records myself for penalties the count might have missed or should not have counted. Nothing below comes from memory unless marked "from memory, not fetched". Those items are not used in any figure.

## Verdict

- **The count holds.** The rate, the list of 20 penalties, the denominator of 95,466 and the main interval all check out against the primary sources.
- **Corrected rate: 0.000209** (20 / 95,466). **Corrected interval: 0.000128 to 0.000400.** Both are the same as the original.
- **One error, in a sensitivity row only.** The "1998 Act penalties added, FY 2018/19 to 2025/26" row counts 31 penalties. It should count 36 to 37. Five 1998-Act security penalties, plus one judgement call, fall between 5 April and 23 May 2018. That is inside the financial-year window, but the count left them out. The corrected row is 0.000377 to 0.000388, not 0.000325. Its Poisson upper limit is about 0.00053, not 0.00046. The main rate does not change, because the method leaves out 1998-Act penalties.
- Because of that error, the report's sentence "Point estimates run from 0.00021 to 0.00033" should read "0.00019 to 0.00039" once the borderline-exclusion variant (below) and the corrected 1998 row are included. Every point estimate still lies inside the interval.

## 1. Denominator: every figure found

I downloaded all eight annual reports from the URLs the count gives and extracted the text.

| FY | Count's figure | What the file says | Found? |
|---|---|---|---|
| 2018/19 | 13,840 | "we received 13,840 PDB reports during 2018-19, an increase from 3,311 in 2017-18" | Yes |
| 2019/20 | 11,854 | Chart "Personal Data Breaches - Received": "2019/20 11,854" (page 65) | Yes |
| 2020/21 | 9,532 | Chart "Personal Data Breaches - Received": "2020/21 9,532" | Yes |
| 2021/22 | 9,571 | 2021/22 report chart: "2021/22 9571" | Yes |
| 2022/23 | 9,146 | Table row "Received 9,146 9,571 9,523"; chart "2022/23 9146" | Yes |
| 2023/24 | 11,680 | "with 11,680 cases reported (2022/23: 9,146), an increase of 28%" | Yes |
| 2024/25 | 12,412 | "with 12,412 cases reported (2023/24: ..." and table "Received 9,146 11,680 12,412" | Yes |
| 2025/26 | 17,431 | "with 17,431 cases reported (2024/25: 12,412) - an increase of 40%" | Yes |

- Sum: 95,466. Correct.
- The 9,523 / 9,532 mismatch in the 2022/23 report is real, as the count says. The 2020/21 and 2021/22 reports both print 9,532. Using 9,532 is right.
- Small note: in the 2020/21 report the chart's year labels come out scrambled in the text layer ("2018/19 11,854"), but the 2020/21 bar is 9,532. No effect.

Trends CSV (`https://ico.org.uk/media2/iivgw0b0/data-security-incidents-trends-download-q1-2019-to-q3-2026.csv`). I counted distinct "BI Reference" values myself.

- 89,591 distinct reports. 2019: 12,259. 2020: 9,702. 2021: 9,742. 2022: 8,798. 2023: 11,069. 2024: 12,194. 2025: 13,462. 2026 Q1 to Q3: 12,365. 2019 to 2025: 77,226. All match.
- No reference appears in more than one quarter, so de-duplicating on BI Reference is safe.
- By financial year the file gives 2019/20: 11,531, 2020/21: 9,453, 2021/22: 9,503, 2022/23: 9,100, 2023/24: 11,582, 2024/25: 12,299, 2025/26: 14,078. That is 97% to 99.5% of the annual reports, and 81% for 2025/26. Matches the count's claim.
- Decisions, 2019 to 2025: Informal Action Taken 42,532, No Further Action 26,190 (together 68,722, 89%), Investigation Pursued 6,919, Not Yet Assigned 1,583, Regulatory action taken 2. Matches. Across the whole file, "Regulatory action taken" covers 3 reports (2 in 2024, 1 in 2026). Matches.
- The largest quarter is 4,604 (2026 Q3). Matches.
- The trends page (`https://ico.org.uk/action-weve-taken/data-security-incident-trends/`) says: "The data starts at Q1 2019 as incidents were recorded differently prior to this period", "Under specific circumstances some cases are transferred to a separate system for review. As a result, these cases, which may include some of the larger and more serious breaches, are not included within this data", and "the data is presented in calendar years and quarters". All quoted correctly.
- The 2025/26 annual report says: "Q2 alone seeing the receipt of over 6,000 reports, a significant number of which related to a single incident, with each affected organisation submitting their own report". Quoted correctly.

## 2. Numerator: every row checked

### The annual-report reconciliation

| FY | Annual report sentence (found) | Members | Sum checks |
|---|---|---|---|
| 2018/19 | "there were no monetary penalties under DPA 2018 in 2018-19" | none | yes |
| 2019/20 | "2019/2020 saw the issue of the first penalty notices under the Data Protection Act 2018 for non-compliance" | Doorstep Dispensaree | no number given |
| 2020/21 | "In 2020/21 we issued 3 fines, totalling £39.65m." | BA 20m + Marriott 18.4m + Ticketmaster 1.25m | 39.65m, yes |
| 2021/22 | "We issued four DPA fines totalling £633k" | 25,000 + 10,000 + 500,000 + 98,000 | 633,000, yes |
| 2022/23 | "two penalty notices totalling £7,631,200"; "one penalty notice, totalling £4.4 million" | Clearview 7,552,800 + Tavistock 78,400; Interserve 4,400,000 | yes |
| 2023/24 | "three penalty notices totalling £13,057,500" | TikTok 12,700,000 + MoD 350,000 + YMCA 7,500 | yes |
| 2024/25 | "We issued two UK GDPR penalty notices totalling £3,826,320" | PSNI 750,000 + Advanced 3,076,320 | yes |
| 2025/26 | "eight UK GDPR penalty notices totalling £32,402,373" | 60,000 + 2,310,000 + 18,000 + 14,000,000 + 1,228,283 + 66,000 + 247,590 + 14,472,500 | 32,402,373, yes |

The Clearview amount is confirmed in its notice: "The amount of the penalty is £7,552,800".

### Each counted penalty

Rows 1 to 10, archived ICO entry pages (UK Government Web Archive, the URLs the count gives). Each page gives the date and amount the count states:

- Doorstep Dispensaree: "Date 20 December 2019 ... fined a London-based pharmacy £275,000 for failing to ensure the security of special category data". I ran OCR on page 1 of the scanned notice: "DATA PROTECTION ACT 2018", "s.155 Data Protection Act 2018", "amount of the fine is £275,000".
- British Airways: "Date 16 October 2020 ... fined British Airways (BA) £20m".
- Marriott: "Date 30 October 2020 ... £18.4million".
- Ticketmaster: "Date 13 November 2020 ... £1.25 million".
- Mermaids: page "Date 08 July 2021". Notice: "Dated the 5th day of July 2021", "amount of the monetary penalty is £25,000".
- HIV Scotland: page "Date 22 October 2021". Notice: "Dated the 18th day of October 2021", "£10,000".
- Cabinet Office: page "Date 02 December 2021 ... fined the Cabinet Office £500,000". Archived ICO news: "issued its fine to the Cabinet Office on 15 November 2021" and "agreed to reduce the £500,000 Monetary Penalty Notice (MPN) ... to £50,000".
- Tuckers: page "Date 10 March 2022". Notice: "Dated the 28th day of February 2022", "£98,000".
- Tavistock & Portman: page "Date 30 June 2022 ... bulk emails to 1,781 Gender Identity Clinic service users". Notice: "Dated the 9th day of June 2022", "£78,400".
- Interserve: page "Date 24 October 2022". Notice: "Dated the 19th day of October 2022.", "£4,400,000".

Rows 11 to 21, live ICO site. The descriptions in the ICO's own search results match the count. I opened the notices:

- MoD: "Dated: The 7th day of December 2023". The listing date is 26 February 2024. The count's use of the notice date is right, and it keeps the row in FY 2023/24 either way.
- Central YMCA: "Dated the 6th day of March 2024", "£7,500".
- PSNI: cover "26 September 2024".
- Advanced: cover "26 MARCH 2025". FY 2024/25, which the 2024/25 annual report confirms.
- DPP Law: "14 April 2025". 23andMe: "5 June 2025", page "£2,310,000". Birthlink: "24 June 2025". Capita: "15 October 2025", page "a combined £14m". LastPass: "20 November 2025". Police Scotland: "12 December 2025". South Staffordshire (out of window): page "£963,900", date 7 May 2026.

Borderline rows. Both meet the method's definition:

- Birthlink notice: "Birthlink contravened Articles 5(1)(f) and 32(1)-(2) of the UK GDPR". It also cites Article 33 and "the personal data breach".
- Police Scotland notice: "The infringements of Articles 5(1)(f), 32(1), 5(1)(c), 25(1)-(2)". It refers to "the personal data breach".

Exclusions checked:

- The four 1998-Act penalties in the calendar window (Newham, Life at Parliament View, DSG Retail, Cathay Pacific): I ran OCR on page 1 of each notice. Each reads "DATA PROTECTION ACT 1998". Leaving them out is right under the method.
- TikTok, MediaLab and Reddit are not security cases. The live list says Reddit infringed "Articles 5(1)(a), 6, and 8, and Article 35" and MediaLab "Articles 5(1)(a), 6, 8 and 35". Leaving them out is right. Clearview and Easylife (filed as "mpn-article-5-1-a") are also correctly left out.

### Search for missed penalties (my own)

- **Live ICO list.** I pulled the ICO enforcement list through the page's own search service (`https://ico.org.uk/api/search`). With the "Monetary penalties" filter it returns 65 entries. With no filter it returns 232. I screened every description for marketing-rule (PECR) wording. The only non-PECR monetary penalties are the 11 security rows (11 to 21) plus TikTok, MediaLab and Reddit. That makes 14, as the count says. The entries filed under other types that mention a fine are PECR fines, Proceeds of Crime confiscations and one prosecution. None is a missed data-breach penalty.
- **Archived entry pages, 2019 to 2022.** I took every ICO enforcement entry page the UK Government Web Archive captured in 2019 to 2023 (391 pages, found through the archive's index at `https://webarchive.nationalarchives.gov.uk/ukgwa/cdx?url=ico.org.uk/action-weve-taken/enforcement/*`). I read the date, type and description on each. 103 are monetary penalties dated 1 January 2019 to 31 December 2022. I screened their descriptions with the same marketing-rule wording test I used on the live list. The only ones left are: Newham (4 Apr 2019), True Visions (10 Apr 2019, "unfair and unlawful filming"), Bounty (11 Apr 2019, "sharing personal data unlawfully"), Life at Parliament View (19 Jul 2019), Doorstep Dispensaree, DSG Retail, Cathay Pacific, BA, Marriott, Ticketmaster, Mermaids, HIV Scotland, Cabinet Office, Royal Mail Group (8 Mar 2022, no description on the page; its notice says "Regulation 22 of the Privacy and Electronic Communications", so it is a marketing penalty), Tuckers, Clearview, Tavistock and Interserve. Every 2018-Act security penalty on that list is in the count. None is missing.
- **Old penalty files.** I also listed the archived notice files in the ICO's old notice folder (`ico.org.uk/media/action-weve-taken/mpns/`, 260 distinct files, 2016 to March 2024). I classified these by file name only and did not open them. They show nothing the entry pages do not. One file, `easylife-limited-mpn-article-5-1-a-20221004.pdf`, has no entry page in the archive I read. It is an Article 5(1)(a) notice (fairness), not a security notice, so it does not affect the count. But it means the 2022/23 annual-report sentences ("two penalty notices" plus "one penalty notice") may not list every UK GDPR notice of that year. So the to-the-pound match is weaker evidence of completeness for 2022/23 than for the other years.
- The live list starts on 14 December 2022, and my entry-page read runs to 31 December 2022, so the two together cover the whole window. These checks are a substitute for the count's own crawl, not a replication of it. They cover only what the archive holds. The weakest year is still 2019/20, where the annual report gives no number.

## 3. Years and arithmetic

- Numerator by notice date, FY 2018/19 to 2025/26: 0, 1, 3, 4, 2, 2, 2, 6 = 20. Correct.
- Calendar 2019 to 2025: 1, 3, 3, 3, 1, 2, 7 = 20. Correct.
- The denominator uses the same financial years. The years match.
- Rates: 20/95,466 = 0.0002095. 20/81,626 = 0.000245. 20/77,226 = 0.000259. 21/89,591 = 0.000234. Lag 2: 19/65,623 = 0.000290. Lag 3: 16/53,943 = 0.000297. 1998 Act added, calendar: 24/77,226 = 0.000311. All correct.
- Exact (Garwood) 95% limits for 20 events: 12.217 to 30.888. Correct. 12.217/95,466 = 0.000128. 30.888/77,226 = 0.000400. Correct.
- Business, charity and public counts (11, 4, 5), "seven in calendar 2025", and "41,523 of 95,466 from 2023/24 on" are all correct.

### The error: 1998-Act sensitivity, financial-year window

The count adds 11 1998-Act security penalties: seven listed between 25 May and 31 December 2018, plus four in 2019 to 2020. But the financial-year window starts on 1 April 2018. I read every archived ICO enforcement entry captured in 2018 and 2019 (264 entry pages). Five more 1998-Act security penalties, and one judgement call, fall between 1 April and 24 May 2018:

| Organisation | ICO page date | Amount | What for (page wording) | Archived page |
|---|---|---|---|---|
| Humberside Police | 5 Apr 2018 | £130,000 | "disks containing a video interview of an alleged rape victim went missing" | `https://webarchive.nationalarchives.gov.uk/ukgwa/20180524151946mp_/https://ico.org.uk/action-weve-taken/enforcement/humberside-police/` |
| Crown Prosecution Service | 16 May 2018 | £325,000 | "lost unencrypted DVDs containing recordings of police interviews" | `https://webarchive.nationalarchives.gov.uk/ukgwa/20180524151726mp_/https://ico.org.uk/action-weve-taken/enforcement/crown-prosecution-service/` |
| University of Greenwich | 21 May 2018 | £120,000 | "'serious' security breach involving the personal data of nearly 20,000 people" | `https://webarchive.nationalarchives.gov.uk/ukgwa/20180524151739mp_/https://ico.org.uk/action-weve-taken/enforcement/the-university-of-greenwich/` |
| Yahoo! UK Services | 21 May 2018 | £250,000 | "computer network was compromised as the result of a cyber-attack in November 2014" | `https://webarchive.nationalarchives.gov.uk/ukgwa/20181009113708mp_/https://ico.org.uk/action-weve-taken/enforcement/yahoo-uk-services-ltd/` |
| Bayswater Medical Centre | 23 May 2018 | £35,000 | "left highly sensitive medical information in an empty building" | `https://webarchive.nationalarchives.gov.uk/ukgwa/20180524151725mp_/https://ico.org.uk/action-weve-taken/enforcement/bayswater-medical-centre/` |
| Royal Borough of Kensington and Chelsea (judgement call) | 16 Apr 2018 | £120,000 | "unlawfully identified 943 people who owned vacant properties" | `https://webarchive.nationalarchives.gov.uk/ukgwa/20180524151730mp_/https://ico.org.uk/action-weve-taken/enforcement/the-royal-borough-of-kensington-and-chelsea/` |

The Kensington and Chelsea page does not say whether this was a security failure or an unlawful disclosure on purpose, so it is a judgement call. The same goes for Facebook (24 October 2018, £500,000, "serious breaches of data protection law", `https://webarchive.nationalarchives.gov.uk/ukgwa/20190212140233mp_/https://ico.org.uk/action-weve-taken/enforcement/facebook-ireland-ltd/`).

Corrected row: 31 + 5 = 36 (0.000377), or 37 with Kensington and Chelsea (**0.000388**), or 38 with Facebook as well (0.000398). For 37 the Poisson interval is 0.000273 to 0.000534.

This changes a sensitivity only. It does not change the rate or the interval, because the method counts 2018-Act penalties only. It does show that the "1998 Act added" reading sits at the top edge of the interval, not in the middle of it.

The 2018/19 annual report says the ICO "issued 22 monetary penalty notices (MPNs) for breaches of the DPA 1998". My archive read finds 15 non-PECR 1998-Act penalties in FY 2018/19. I could not close that gap. It touches only this sensitivity.

## 4. Is the interval wide enough?

The test is whether the interval holds the rate under the other reasonable choices. It does.

| Choice | Rate | Inside 0.000128 to 0.000400? |
|---|---|---|
| Main | 0.000209 | yes |
| Drop FY 2018/19 | 0.000245 | yes |
| Calendar 2019 to 2025 | 0.000259 | yes |
| Calendar 2019 to Q3 2026 | 0.000234 | yes |
| Lag 2 years | 0.000290 | yes |
| Lag 3 years | 0.000297 | yes |
| Drop the two borderline rows (18 / 95,466) | 0.000189 | yes |
| Drop Doorstep Dispensaree (19 / 95,466) | 0.000199 | yes |
| 1998 Act added, calendar | 0.000311 | yes |
| 1998 Act added, FY (corrected, 36 to 38) | 0.000377 to 0.000398 | yes, near the top |

Some Poisson limits of these variants fall outside the interval: 0.000112 at the low end (18 events on 95,466), and 0.00045 to 0.00053 at the high end (lag and 1998-Act variants). The count already says that variants break the same-years rule up to 0.00048. With the correction, that figure is 0.00053. That is a reason to describe the upper edge as soft. It is not a reason to widen the main interval, since every point estimate is inside it.

### An independent ICO figure the count did not use

The ICO's annual reports give the share of closed breach cases where a penalty was "pursued":

- 2018/19 report, page 29, chart "Personal Data Breaches - Outcomes": "Civil monetary penalty pursued 0.05%" (of 12,385 closed). The text says "Only a very small minority of cases (less than 1%) led to action beyond that ... or civil monetary penalties being pursued."
- 2019/20 report, page 66: "Civil monetary penalty pursued 0.03%" (of 12,789 closed).

As rates these are about 0.0005 and 0.0003. They measure penalties pursued, not imposed, and per closed case, not per report received. In 2018/19 they can only be 1998-Act cases, because no 2018-Act penalty was issued that year. So they cannot replace the count. But they are the same order of size. The 2019/20 figure (0.00025 to 0.00035 once rounding is allowed for) sits inside the interval. The 2018/19 figure sits above it. That is consistent with the 1998-Act sensitivity above, and it is another reason to treat 0.00040 as a soft upper edge. The 2021/22 figure "Regulatory action taken 0.02%" is about complaints, not breach reports, so it does not apply.

## 5. What the count says about meaning

The count's list of assumptions and their directions is sound. I add three points:

- **Penalties for breaches nobody reported.** A penalised breach that never reached the ICO as a breach report is in the numerator but not the denominator. That pushes the rate up slightly. Doorstep Dispensaree may be such a case. That it was found by another regulator and not reported is from memory, not fetched; the ICO page does not say how the case arose. Dropping it gives 0.000199, inside the interval.
- **The trends file under-counts the larger cases.** The ICO says the larger cases may be held in a separate system. The annual-report denominator does not have this problem, so the main rate is not affected.
- **The ICO's own "pursued" share** (section 4) supports the count's order of size.

## Not checked or not reproduced

- The count's 3,387 archive captures, 258 penalty entries and 118 non-penalty entries. I did not repeat that crawl. Instead I read the archived entry pages captured in 2018 to 2023 (264 and 391 pages) and listed the archive's notice files by name.
- Whether the archive's captures miss an entry page. Easylife's October 2022 notice file exists but I found no entry page for it.
- The statement that the archive and the live list "agree" from December 2022 to October 2024.
- Notice dates inside the BA, Marriott and Ticketmaster notices. The page dates fall well inside one year, so the year does not depend on them.
- Appeal or payment status of each penalty, apart from the Cabinet Office cut to £50,000. The count's statement that Doorstep Dispensaree's fine was cut on appeal is from memory, not fetched. I did not fetch it either. It does not change the count.
- Reconciling the 22 DPA 1998 penalties in the 2018/19 annual report with the 15 non-PECR ones I found in the archive.
- Whether the "single incident" reports of 2025/26 are the ones missing from the trends file. No ICO page says so.

## Sources fetched (15 November 2026)

- ICO annual reports 2018/19 to 2025/26, at the eight URLs the count lists (the first three from the UK Government Web Archive).
- ICO data security incident trends page and CSV: `https://ico.org.uk/action-weve-taken/data-security-incident-trends/`
- ICO enforcement list through its search service: `https://ico.org.uk/action-weve-taken/enforcement/`
- Live ICO entry pages and notices for 23andMe, Capita, MoD, Central YMCA, PSNI, Advanced, DPP Law, Birthlink, LastPass and Police Scotland, at the URLs the count lists.
- Archived ICO entry pages and notices for rows 1 to 10, Clearview, Newham, Life at Parliament View, DSG Retail and Cathay Pacific, and the Cabinet Office news item, at the URLs the count lists.
- Archived ICO entry pages for Humberside Police, Kensington and Chelsea, CPS, University of Greenwich, Yahoo! UK, Bayswater Medical Centre, Bible Society, Facebook and Uber. Pattern: `https://webarchive.nationalarchives.gov.uk/ukgwa/<timestamp>mp_/https://ico.org.uk/action-weve-taken/enforcement/<name>/`
- The web archive's index of ICO notice files: `https://webarchive.nationalarchives.gov.uk/ukgwa/cdx?url=ico.org.uk/media/action-weve-taken/mpns/*`
