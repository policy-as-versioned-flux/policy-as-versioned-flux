# ICO penalty rate for a cyber breach: cyber incidents only

Filed note: this is the second of three counts. Its check is `cyber-only-check.md`, which leaves the rate as it is. The choice built on the three counts is `CHOICE.md`.

Method: cyber incidents only. Everything below was fetched on 14 November 2026 unless marked otherwise.

## 1. The answer

- **Point estimate: 0.053% per cyber report.** That is 10 penalties over 18,897 reports, or about 1 in 1,900.
- **Defensible interval: 0.024% to 0.14%.** That is about 1 in 4,200 to 1 in 700.
- As a probability, on the same scale as the model's current value of 1: 0.00053, with 0.00024 to 0.0014.
- The current model value of 1 is too high by a factor of roughly 700 to 4,200, if the unit is "one cyber breach report to the ICO".
- The unit matters. This is a rate over all cyber reports, most of them small. For a large breach the rate is about ten times higher (section 7). It is still far below 1.

## 2. What was counted

- **Numerator.** Monetary penalty notices given by the ICO under section 155 of the Data Protection Act 2018 for infringements of the GDPR or UK GDPR, where the infringement was exposed by an attack from outside: hacking, ransomware, credential theft, a compromised website or payment page. One event counts once, even when two companies were named in the notice.
- **Denominator.** Personal data breach reports that the ICO classes as "Cyber" in its data security incident trends data set, counted per calendar year.
- **Years.** Calendar 2019 to 2025, for both. Reasons:
  - The ICO data set starts at Q1 2019. The ICO says: "The data starts at Q1 2019 as incidents were recorded differently prior to this period."
  - 2026 has three quarters only, and its count is still filling in (section 5).
  - Starting in 2019 loses no penalty. The ICO annual report for 2018/19 says: "while there were no monetary penalties under DPA 2018 in 2018-19, there were many under DPA 1998."
- **Two ways of matching.** A penalty arrives 1.5 to 3.8 years after the report (median 2.5 years, from the 11 notices below). So I give two cuts:
  - **Flow rate**: notices dated in the window, over reports received in the window.
  - **Cohort rate**: reports received in a year that later drew a penalty, over reports received in that year, for years old enough to have matured.

## 3. The numerator: the list

Eleven penalties from 25 May 2018 to 14 November 2026. Ten have a notice date in 2019 to 2025. All are under section 155 of the Data Protection Act 2018. Amounts are the final notice amounts, not the earlier notices of intent.

| # | Organisation | Notice date | Amount | Reported to ICO | What it was for |
|---|---|---|---|---|---|
| 1 | British Airways plc | 16 Oct 2020 | £20,000,000 | 6 Sep 2018 | Attacker entered the network and took customer and payment card data from the booking site. |
| 2 | Marriott International Inc | 30 Oct 2020 | £18,400,000 | 22 Nov 2018 | Attacker installed a web shell in the Starwood reservation network in 2014; found in 2018. |
| 3 | Ticketmaster UK Limited | 13 Nov 2020 | £1,250,000 | 23 Jun 2018 | Malicious code in a third-party chat bot on the online payment page. |
| 4 | Tuckers Solicitors LLP | 28 Feb 2022 | £98,000 | 25 Aug 2020 | Ransomware attack on a law firm; 24,712 court bundles encrypted, 60 released on criminal marketplaces. |
| 5 | Interserve Group Limited | 19 Oct 2022 | £4,400,000 | 5 May 2020 | Phishing email led to malware and compromise of HR data of up to 113,000 staff. |
| 6 | Advanced Computer Software Group Ltd (and two group companies) | 26 Mar 2025 | £3,076,320 | Not stated in the notice. Incident 2 to 4 Aug 2022 | Ransomware attack on a software supplier to the NHS, through an account without multi-factor authentication. A processor. |
| 7 | DPP Law Ltd | 14 Apr 2025 | £60,000 | 17 Jul 2022 | Brute force attack on an administrator account; data of 791 people put on the dark web. |
| 8 | 23andMe, Inc | 5 Jun 2025 | £2,310,000 | Oct 2023 | Credential stuffing attack; data of 155,592 UK users. |
| 9 | Capita plc and Capita Pension Solutions Ltd (one event) | 15 Oct 2025 | £14,000,000 (£8m + £6m) | 31 Mar 2023 | Malicious file on a staff device, then ransomware; over 6 million people's data. |
| 10 | LastPass UK Ltd | 20 Nov 2025 | £1,228,283 | 30 Nov 2022 | Threat actor took a backup database with data of about 1.6 million UK customers. |
| 11 | South Staffordshire Plc and South Staffordshire Water Plc (one event) | 7 May 2026 | £963,900 | 24 Jul 2022 | Phishing gave access in 2020; data of about 633,887 people exfiltrated. |

Where each row came from (the penalty notice itself in every case, fetched from the ICO site):

1. `https://ico.org.uk/media2/migrated/2618421/ba-penalty-20201016.pdf`. Dated 16 October 2020. "This Penalty Notice is given to British Airways plc ('BA') pursuant to section 155 and Schedule 16 to the Data Protection Act 2018". "The amount of the penalty that the Commissioner has decided to impose ... is £20m." "BA notified the Commissioner of the Attack on 6 September 2018."
2. `https://ico.org.uk/media2/migrated/2618524/marriott-international-inc-mpn-20201030.pdf`. Dated 30 October 2020. "The amount of the penalty that the Commissioner has decided to impose ... is £18.4 million." "Marriott notified the Commissioner of the Attack on 22 November 2018." "The Attacker installed a web shell on a device within the Starwood network on 29 July 2014."
3. `https://ico.org.uk/media2/migrated/2618609/ticketmaster-uk-limited-mpn.pdf`. Dated 13 November 2020. "The amount of the penalty that the Commissioner has decided to impose is £1,250,000.00." "Ticketmaster initially notified the Commissioner of the Attack on 23 June 2018".
4. `https://ico.org.uk/media2/migrated/4019746/tuckers-mpn-20220228.pdf`. "Dated the 28th day of February 2022". "The amount of the monetary penalty is £98,000." "Tuckers became aware on 24 August 2020 of a ransomware attack on its systems". "25 August 2020 is the date on which Tuckers reported the breach to the Commissioner".
5. `https://ico.org.uk/media2/migrated/4021951/interserve-group-limited-monetary-penalty-notice.pdf`. "Dated the 19th day of October 2022." "The amount of the penalty is £4,400,000." "On 30 March 2020, a phishing email was sent to Interserve Construction Limited's accounts team mailbox". "On 5 May 2020 Interserve submitted a personal data breach notification to the Commissioner."
6. `https://ico.org.uk/media2/gdlfddgc/advanced-penalty-notice-20250327.pdf`. Dated 26 March 2025. "to pay the Commissioner £3,076,320". "The Threat Actor also deployed ransomware, with the earliest evidence of execution taking place on 4 August 2022". "Advanced notified all potentially impacted data controller customer entities on 5 August 2022." Page: `https://ico.org.uk/action-weve-taken/enforcement/2025/03/advanced-computer-software-group-limited/`.
7. `https://ico.org.uk/media2/pr4bg5hq/dpp-law-ltd-monetary-penalty-notice.pdf`. Page date 14 April 2025: "The Information Commissioner has fined law firm DPP Law Ltd £60,000 for its infringements of Articles 5(1)(f), 32(1), 32(2) and 33(1) of the UK GDPR". Notice: "there was evidence to suggest brute force attempts on its network as early as 19 February 2022". "43 days after the Cyber Incident, DPP reported the personal data breach to the Commissioner" (heading: 17 July 2022). Page: `https://ico.org.uk/action-weve-taken/enforcement/2025/04/dpp-law-ltd/`.
8. `https://ico.org.uk/media2/kclbljpo/23andme-penalty-notice.pdf`. Dated 5 June 2025. "the Commissioner has concluded that a penalty of £2,310,000 adequately reflects the seriousness of the Infringements". "personal data breach which 23andMe first reported to both regulators in October 2023". Page: `https://ico.org.uk/action-weve-taken/enforcement/2025/06/23andme/`: "following a large-scale cyber attack in 2023".
9. `https://ico.org.uk/media2/pv5nhks4/capita-plc-and-cpsl-monetary-penalty-notice.pdf`. Dated 15 October 2025. "requires Capita plc to pay a penalty of £8,000,000, and Capita Pension Solutions Limited ('CPSL') a penalty of £6,000,000". "Capita reported the incident to the Commissioner at 18:30 on 31 March 2023". Page: `https://ico.org.uk/action-weve-taken/enforcement/2025/10/capita-plc/`.
10. `https://ico.org.uk/media2/xfbl1uaa/lastpass-uk-ltd-penalty-notice.pdf`. Dated 20 November 2025. "On 30 November 2022, LastPass submitted a personal data breach report to the ICO". Page: `https://ico.org.uk/action-weve-taken/enforcement/2025/11/lastpass-uk-ltd/`: "£1,228,283 penalty issued to password management provider LastPass UK Ltd on 20 November 2025 ... allowed a threat actor to exfiltrate personal data relating to approximately 1.6 million UK customers from its backup database."
11. `https://ico.org.uk/media2/xdrfahsw/south-staffordshire-plc-and-south-staffordshire-water-plc-monetary-penalty-notice.pdf`. Dated 7 May 2026. "to pay the Commissioner a penalty of £963,900". "initial access occurred on 11 September 2020 through a successful phishing campaign". "South Staffordshire reported a personal data breach to the ICO on 24 July 2022." Page: `https://ico.org.uk/action-weve-taken/enforcement/2026/05/south-staffordshire-plc-and-south-staffordshire-water-plc/`.

### How I know the list is complete

Three independent ICO sources agree.

- **The live ICO enforcement listing.** `https://ico.org.uk/action-weve-taken/enforcement/` (its search endpoint returned 232 entries, 14 December 2022 to 4 November 2026 for monetary penalties). I read every entry typed "Monetary penalties". The ICO has removed older monetary penalties from this listing.
- **UK Government Web Archive captures of the same ICO listing**, 50 rows each, overlapping, covering November 2018 to January 2023:
  - 3 February 2020: `https://webarchive.nationalarchives.gov.uk/ukgwa/20200203120408mp_/https://ico.org.uk/action-weve-taken/enforcement?rows=50`
  - 1 February 2021: `https://webarchive.nationalarchives.gov.uk/ukgwa/20210201165955mp_/https://ico.org.uk/action-weve-taken/enforcement?rows=50`
  - 15 April 2021: `https://webarchive.nationalarchives.gov.uk/ukgwa/20210415203210mp_/https://ico.org.uk/action-weve-taken/enforcement?rows=50`
  - 9 March 2022: `https://webarchive.nationalarchives.gov.uk/ukgwa/20220309174832mp_/https://ico.org.uk/action-weve-taken/enforcement?rows=50`
  - 3 October 2022: `https://webarchive.nationalarchives.gov.uk/ukgwa/20221003101330mp_/https://ico.org.uk/action-weve-taken/enforcement?rows=50`
  - 1 February 2023: `https://webarchive.nationalarchives.gov.uk/ukgwa/20230201110435mp_/https://ico.org.uk/action-weve-taken/enforcement?rows=50`
- **ICO annual reports**, which count data protection penalties per financial year:

| Year (April to March) | What the report says | Cyber among them |
|---|---|---|
| 2018/19 | "while there were no monetary penalties under DPA 2018 in 2018-19, there were many under DPA 1998." | 0 |
| 2019/20 | No count stated. The archived listing shows one DPA 2018 penalty (Doorstep Dispensaree, 20 Dec 2019). | 0 |
| 2020/21 | "GDPR fines. In 2020/21 we issued 3 fines, totalling £39.65m." | 3 (BA, Marriott, Ticketmaster) |
| 2021/22 | "We issued four DPA fines totalling £633k and 33 PECR penalties totalling £2.9m." | 1 (Tuckers) |
| 2022/23 | "Within the 2022/23 financial year, the cyber team has delivered seven reprimands ... The team also issued one penalty notice, totalling £4.4 million." | 1 (Interserve) |
| 2023/24 | "We also issued three penalty notices totalling £13,057,500 (2022/23: two penalty notices totalling £7,631,200)." | 0 |
| 2024/25 | "We issued two UK GDPR penalty notices totalling £3,826,320 (2023/24: three penalty notices totalling £13,057,500)." | 1 (Advanced) |
| 2025/26 | "eight UK GDPR penalty notices totalling £32,402,373 (2024/25: two penalty notices totalling £3,826,320)" | 4 (DPP Law, 23andMe, Capita, LastPass) |
| 2026/27 to 14 Nov 2026 | Live listing only. | 1 (South Staffordshire) |

The amounts add up. The eight notices of 2025/26 that I found on the listing sum to exactly £32,402,373. The three of 2023/24 sum to exactly £13,057,500. The two of 2024/25 sum to exactly £3,826,320. The four of 2021/22 sum to £633,000.

Annual report URLs:
- 2018/19: `https://ico.org.uk/media2/migrated/2615262/annual-report-201819.pdf`
- 2019/20: `https://ico.org.uk/media2/migrated/2618021/annual-report-2019-20-v83-certified.pdf`
- 2020/21: `https://ico.org.uk/media2/migrated/2620166/hc-354-information-commissioners-ara-2020-21.pdf`
- 2021/22: `https://ico.org.uk/media2/migrated/4021039/ico-annual-report-2021-22.pdf`
- 2022/23: `https://ico.org.uk/media2/migrated/4025864/annual-report-2022-23.pdf`
- 2023/24: `https://ico.org.uk/media2/migrated/4030348/annual-report-2023-24.pdf`
- 2024/25: `https://ico.org.uk/media2/1wyfliqp/annual-report-2025-ico-v4-1-complete.pdf`
- 2025/26: `https://ico.org.uk/media2/ybsi5n0j/ico-annual-report-202527.pdf`

## 4. What I left out, and why

**Left out because the cause was not an outside attack** (all are DPA 2018 or UK GDPR penalties):

| Organisation | Date | Amount | Cause | Source |
|---|---|---|---|---|
| Doorstep Dispensaree Ltd | 20 Dec 2019 | £275,000 | Paper records left in unlocked crates. | Notice: `https://ico.org.uk/media2/migrated/2616742/doorstop-mpn-20191217.pdf` |
| Mermaids | 8 Jul 2021 | £25,000 | Internal email group left searchable online. | Notice: `https://ico.org.uk/media2/migrated/2620171/mermaids-mpn-20210705.pdf` |
| HIV Scotland | 22 Oct 2021 | £10,000 | Email sent with addresses visible. | Annual report 2021/22 |
| Cabinet Office | 2 Dec 2021 | £500,000 | Honours list addresses published online by mistake. | Annual report 2021/22 |
| Clearview AI Inc | 26 May 2022 | "£7.5m" | Scraping of images; not a breach. | Archived listing, capture 3 Oct 2022 |
| Tavistock and Portman NHS Foundation Trust | 30 Jun 2022 | Amount not fetched | Bulk email to clinic users. | Archived listing, capture 3 Oct 2022 |
| Easylife Limited | 5 Oct 2022 | Amount not fetched | Unlawful profiling of customers; not a breach. | Archived listing, capture 1 Feb 2023 |
| TikTok | 15 May 2023 (listing date) | £12,700,000 | Children's data; not a breach. | Live listing |
| Ministry of Defence | 13 Dec 2023 (annual report); listing shows 26 Feb 2024 | £350,000 | Email sent with addresses visible. | Live listing |
| Central YMCA | 6 Mar 2024 | £7,500 | Email sent with addresses visible. | Live listing |
| Police Service of Northern Ireland | 3 Oct 2024 | £750,000 | Spreadsheet released in a freedom of information reply. | Live listing and notice |
| Birthlink | 24 Jun 2025 | £18,000 | Records destroyed in error. | Live listing |
| Police Service of Scotland | 12 Dec 2025 | £66,000 | Excessive extraction of a phone's contents. | Live listing and notice |
| MediaLab.AI, Inc (Imgur) | 4 Feb 2026 | £247,590 | Children's data; not a breach. | Live listing |
| Reddit, Inc | 23 Feb 2026 | £14,472,500 | Children's data; not a breach. | Live listing |

**Left out because the penalty was under the Data Protection Act 1998, not UK GDPR.** These followed outside attacks and their notices fall after 25 May 2018. But the conduct was before that date, the maximum was £500,000, and their reports are not in the denominator years.

| Organisation | Date | Amount | Source |
|---|---|---|---|
| Equifax Ltd | 20 Sep 2018 | £500,000 | Annual report 2018/19: "£500,000 fine against Equifax Ltd, relating to a cyber security incident". Date from the archived ICO trends page, capture 3 June 2019. |
| Uber | 26 Nov 2018 | £385,000 | Annual report 2018/19; archived listing |
| Life at Parliament View Ltd | 19 Jul 2019 | £80,000 | Notice: `https://ico.org.uk/media2/migrated/2615396/mpn-life-at-parliament-view-limited-20190717.pdf` (an open file server, then a ransom demand) |
| DSG Retail Ltd | 7 Jan 2020 | £500,000 | Notice: `https://ico.org.uk/media2/migrated/2616891/dsg-mpn-20200107.pdf`. "monetary penalty under section 55A of the Data Protection Act 1998". Reported 8 June 2018. |
| Cathay Pacific Airways Ltd | 10 Feb 2020 | £500,000 | Notice: `https://ico.org.uk/media2/migrated/2617314/cathay-pacific-mpn-20200210.pdf`. "monetary penalty under section 55A of the Data Protection Act 1998". |

DSG Retail is the nearest thing to the modelled firm: a retailer whose tills were compromised. It is excluded only on legal basis. If DSG and Cathay Pacific were added, the flow rate would be 12 over 18,897, or 0.064%. That is inside my interval.

**Left out by type.** All penalties under the Privacy and Electronic Communications Regulations (nuisance calls, texts and emails). All penalties for not paying the data protection fee.

**Judgement calls.**
- **Appeals and reductions.** I count a penalty if the notice was issued, at the notice amount. British Airways and Marriott were cut from proposed £183.39m and £99.2m to £20m and £18.4m; I count each once, at the final figure. Advanced, Capita and South Staffordshire settled and agreed not to appeal (stated in their notices). I did not fetch appeal outcomes for the other eight. If one were overturned, the count falls by one. The count, not the pounds, drives the rate.
- **Collection.** The 2020/21 annual report says of British Airways and Marriott: "Both of these CMPs have agreed payment plans". I did not check collection for the others. I did not exclude any penalty for non-payment.
- **Processors.** Advanced was fined as a processor. Its customers, not Advanced, were the controllers who report. I kept it. Without it the flow rate is 9 over 18,897, or 0.048%.
- **Two-company notices.** Capita and South Staffordshire each count once.

## 5. The denominator: ICO cyber reports by year

Source: ICO, "Data security incident trends", `https://ico.org.uk/action-weve-taken/data-security-incident-trends/`. Page note: "26 October 2026 – Data updated to Q3 2026". Data file: `https://ico.org.uk/media2/iivgw0b0/data-security-incidents-trends-download-q1-2019-to-q3-2026.csv`.

The file has 237,713 rows. One report appears on several rows, one per data type. The ICO says so: "some reports hold multiple characteristics ... and as such appear on multiple rows". I counted distinct values of "BI Reference": 89,591 reports. No report had conflicting year or category across its rows. The cyber count is the number of distinct reports with "Incident Category" equal to "Cyber".

| Calendar year | Cyber reports | All reports | Cyber share |
|---|---|---|---|
| 2019 | 2,346 | 12,259 | 19% |
| 2020 | 2,190 | 9,702 | 23% |
| 2021 | 2,589 | 9,742 | 27% |
| 2022 | 2,156 | 8,798 | 25% |
| 2023 | 3,319 | 11,069 | 30% |
| 2024 | 3,116 | 12,194 | 26% |
| 2025 | 3,181 | 13,462 | 24% |
| **2019 to 2025** | **18,897** | 77,226 | 24% |
| 2026, Q1 to Q3 only | 3,270 | 12,365 | 26% |

Cyber reports by ICO incident type, 2019 to Q3 2026: phishing 9,433; ransomware 5,013; other cyber incident 4,171; unauthorised access 1,973; malware 1,025; brute force 509; denial of service 43.

### Checks on the denominator

- **Against the ICO's older quarterly file.** `https://ico.org.uk/media2/migrated/2616136/data-security-figures-201819q4.csv` covers January to March 2019. It gives a grand total of 3,263; phishing 205; ransomware 43; malware 17; brute force 12. My count from the current file for Q1 2019 is 3,372; phishing 207; ransomware 44; malware 19; brute force 12. The small gap is later revision. The method of counting holds.
- **Against annual reports.** Reports received per financial year, annual report against my count from the file: 2019/20 11,854 against 11,531; 2020/21 9,532 against 9,453; 2021/22 9,571 against 9,503; 2022/23 9,146 against 9,100; 2023/24 11,680 against 11,582; 2024/25 12,412 against 12,299; 2025/26 17,431 against 14,078. The file holds 97% to 99% of reports up to March 2025, and only 81% for 2025/26. The 2025/26 annual report says the open caseload rose to "6,317 at year end (2024/25: 1,518)". So the 2025 and 2026 counts in the file are still low.
- **The cyber label moved.** In 2019 the file classes 778 of 876 "Unauthorised access" reports as cyber. In 2024 it classes 50 of 1,329 as cyber. The older quarterly files also put "Hardware/Software Misconfig" under cyber; the current file puts it under non-cyber. The ICO says: "The way we categorise incidents as cyber or non-cyber within the dashboard is currently under review ... caution should be taken when drawing conclusions from the split of incident category."
- **Some serious cases are missing.** The ICO says: "Under specific circumstances some cases are transferred to a separate system for review. As a result, these cases, which may include some of the larger and more serious breaches, are not included within this data."

### 2018

The three largest penalties followed reports made in 2018, before the data set starts. The ICO's older files give part of the 2018 picture, on the older classification:
- April to June 2018: 414 cyber incidents. `https://ico.org.uk/media2/migrated/2259977/data-security-incident-trends-q1-201819.csv`
- July to September 2018: 675 cyber incidents. `https://ico.org.uk/media2/migrated/2553819/data-security-trends-csv.csv`
- October to December 2018: not found. The ICO page of previous reports does not list that quarter, and neither does its 2019 archive capture.

So a window from 25 May 2018 cannot be built from fetched figures alone. I did not use one.

## 6. The rate and the interval

Intervals are exact 95% Poisson intervals on the numerator, divided by the denominator.

| Cut | Penalties | Cyber reports | Rate | Exact 95% interval |
|---|---|---|---|---|
| **A. Flow, notices and reports 2019 to 2025 (primary)** | 10 | 18,897 | **0.053%** | 0.025% to 0.097% |
| B. Flow, 2019 to Q3 2026 | 11 | 22,167 | 0.050% | 0.025% to 0.089% |
| C. Flow, 2020 to 2025 (drop 2019, when no notice could yet exist) | 10 | 16,551 | 0.060% | 0.029% to 0.111% |
| D. Flow, 2019 to 2025, only penalties whose report is inside the window (drops BA, Marriott, Ticketmaster) | 7 | 18,897 | 0.037% | 0.015% to 0.076% |
| E. Cohort, reports received 2019 to 2022 | 6 | 9,281 | 0.065% | 0.024% to 0.141% |
| **F. Cohort, reports received 2019 to 2023** | 8 | 12,600 | **0.063%** | 0.027% to 0.125% |
| G. As A, but leaving "Unauthorised access" out of the cyber count in every year | 10 | 17,013 | 0.059% | 0.028% to 0.108% |
| H. As A, but adding "Hardware/software misconfiguration" to the cyber count, as the old files did | 10 | 20,671 | 0.048% | 0.023% to 0.089% |

Numerator and denominator side by side, by calendar year (penalties by notice date, reports by date received):

| Year | Cyber penalties | Cyber reports |
|---|---|---|
| 2019 | 0 | 2,346 |
| 2020 | 3 | 2,190 |
| 2021 | 0 | 2,589 |
| 2022 | 2 | 2,156 |
| 2023 | 0 | 3,319 |
| 2024 | 0 | 3,116 |
| 2025 | 5 | 3,181 |
| **2019 to 2025** | **10** | **18,897** |
| 2026 to date | 1 | 3,270 (Q1 to Q3) |

The cohort by year of report:

| Year reported | Later penalised | Cyber reports | Note |
|---|---|---|---|
| 2018 (from 25 May) | 3: Ticketmaster, BA, Marriott | not in the data set | |
| 2019 | 0 | 2,346 | |
| 2020 | 2: Interserve, Tuckers | 2,190 | |
| 2021 | 0 | 2,589 | |
| 2022 | 4: DPP Law, South Staffordshire, Advanced, LastPass | 2,156 | Advanced placed by incident date |
| 2023 | 2: Capita, 23andMe | 3,319 | May still gain cases |
| 2024 | 0 | 3,116 | Too young |
| 2025 | 0 | 3,181 | Too young |

**How I set the interval.**
- Point: cut A, 0.053%. It uses the most data and needs no judgement on which years are mature.
- One rule: the envelope of the exact Poisson bounds on cuts A, E and F. A is the primary flow cut. E and F are the cohort cuts. E is the only fully mature cohort: the longest lag seen is 3.8 years, so reports from 2023 may still gain a penalty.
- Low: 0.024%. The lower bound of cut E.
- High: 0.14%. The upper bound of cut E.
- The point estimates across all reasonable cuts run from 0.037% to 0.065%. The choice of cut moves the answer less than the small count does.
- Even this interval is on the narrow side. The yearly counts of penalties (0, 3, 0, 2, 0, 0, 5) are lumpier than a Poisson process would give. Cases arrive in clusters.
- Cut D reaches down to 0.015%. I do not defend that: it throws away three real penalties and keeps their years.
- One single year sits outside the interval: 2025 alone gives 5 over 3,181, or 0.16% (section 7).

## 7. What this rate means, and what it does not

Each assumption, and which way it pushes the rate:

- **It is a rate per report, not per serious breach.** Most cyber reports are small: a phished mailbox, a few records. At least nine of the eleven penalised breaches touched more than 10,000 people (all but DPP Law, and Tuckers, where the notice gives files, not people). The ICO file records the number of people affected at first report. Reports classed cyber with 10,000 or more people affected, 2019 to 2025: 1,203. Penalties in 2019 to 2025 for breaches of that size: 8. That gives about 0.7% (exact 95% interval 0.3% to 1.3%). This is outside my method and is rougher: size is "Unknown" for 5,626 of the 18,897 cyber reports, and the ICO says the size field is a "point in time reflection" of the first report. Two more faults push this figure too high. Three of its eight penalties (BA, Marriott, Ticketmaster) were reported in 2018, outside that denominator. And the ICO moves some larger cases to a separate system, which matters more against 1,203 reports than against 18,897. Treat it as an order of magnitude. Direction: for a large breach, the all-report rate is too **low**, by roughly ten times.
- **It is not a retail rate.** None of the eleven is a shop. Ticketmaster and British Airways are the nearest: a compromised online payment page and booking site. "Retail and manufacture" sent 3,939 cyber reports in 2019 to 2025, the largest sector. The ICO's own "Decision Taken" field shows "Regulatory action taken" on 3 of 89,591 reports, none of them cyber; I did not use that field, because its coding changes over the years. Direction: unknown. The data cannot show whether a retailer is more or less likely to be fined than the average.
- **Penalties lag.** Reports from 2024 and 2025 sit in the denominator of cut A, but their penalties cannot have arrived yet. Reports from 2018 are not in the denominator, but their penalties are in the numerator. These two effects pull opposite ways. Reports have grown, so on balance cut A is slightly too **low**; cut F corrects for that and gives 0.063%.
- **Recent years are undercounted in the file.** About a fifth of 2025/26 reports are not yet in it. Direction: cut A and cut B slightly too **high**.
- **Large cases may be missing from the file.** The ICO moves some serious cases to another system. A penalised breach may not be in the denominator at all. Direction: slightly too **high**. The effect is tiny in a count of thousands.
- **Reports are not events.** One attack on a supplier produces many reports, one from each customer. Capita and Advanced are examples. Direction: too **low** as a rate per event.
- **The cyber label is unstable.** See section 5. Cuts G and H show the effect: 0.048% to 0.059%.
- **Only reported breaches count.** A breach found by the ICO but never reported is in neither figure. A breach never found is in neither. Direction: none on the rate per report.
- **The past may not hold, and the years are lumpy.** Five of the eleven penalties have a 2025 date. Five over the 3,181 cyber reports of 2025 is 0.16%, above my interval. I do not adopt it, because 2023 and 2024 had no cyber penalty at all: 2023 to 2025 together give 5 over 9,616, or 0.052%, the same as the long run. By year of report the picture is also uneven: 2 penalties from 7,125 reports in 2019 to 2021 (0.028%), 6 from 5,475 in 2022 to 2023 (0.11%). In June 2022 the ICO moved to fewer fines for public bodies; that does not reach a private retailer. The annual report for 2024/25 shows the funnel: "In our cyber-related work, we completed 15 investigations and managed 61 incidents this year. The team triaged 1,746 reports". Direction: if the pace of 2025 holds, the point estimate is too **low**, and the true figure is nearer the top of my interval.
- **A penalty is not the only cost of ICO attention.** Reprimands are far more common: the cyber team "delivered seven reprimands" and one penalty in 2022/23. This rate does not price them.

For the model: if the penalty term multiplies the yearly chance of any reportable cyber breach, use 0.053% with 0.024% to 0.14%. If it multiplies the chance of a large breach of customer data, the size-conditional figure of roughly 0.3% to 1.3% is the nearer one, and it is weaker evidence.

## 8. Not found, or not fetched

- ICO cyber incident counts for October to December 2018. Not found.
- A count of DPA 2018 penalties in the 2019/20 annual report. The report gives none. I relied on the archived ICO listing for that year.
- Appeal outcomes and payment status for Ticketmaster, Tuckers, Interserve, DPP Law, 23andMe and LastPass. Not fetched.
- The date Advanced, or its customers, reported the August 2022 attack to the ICO. Not in the notice text I searched.
- Exact amounts for Clearview AI, Easylife and Tavistock and Portman. Not fetched. They are excluded, so they do not affect the rate.
- From memory, not fetched, and not used in the rate: DSG Retail's penalty was reduced on appeal; Ticketmaster appealed its penalty.
- The ICO's Power BI dashboard was not read. I used the ICO's download of the same data.

## 9. Sources

Primary, all fetched 14 November 2026:

- ICO, Data security incident trends page and data file (updated 26 October 2026). URLs in section 5.
- ICO, older quarterly incident files for 2018/19. URLs in section 5.
- ICO, enforcement listing and its search endpoint, `https://ico.org.uk/action-weve-taken/enforcement/`, and the eleven enforcement pages and penalty notices in section 3.
- ICO, penalty notices for the excluded cases named in section 4.
- ICO annual reports 2018/19 to 2025/26. URLs in section 3.
- UK Government Web Archive captures of the ICO enforcement listing, capture dates in section 3.

No secondary source supplied any figure used here.
