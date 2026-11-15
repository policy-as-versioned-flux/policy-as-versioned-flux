# Check of the count "ICO penalty rate for a cyber breach: cyber incidents only"

Filed note: the count checked below is `cyber-only.md`. The choice built on the three counts is `CHOICE.md`.

I checked one count. I did not make a new one. Every source below was fetched on 14 or 15 November 2026. I downloaded the files and read the text myself. I did not rely on a summary.

## 1. Verdict

- **The count holds.** I could not break the numerator, the denominator or the arithmetic.
- Numerator: 10 penalties dated 2019 to 2025. I found none they missed and none they should have left out under their own rule.
- Denominator: 18,897 cyber reports, 2019 to 2025. I recounted it from the ICO file and got the same number for every year.
- Rate: 10 / 18,897 = 0.0529% (0.000529).
- Interval: 0.024% to 0.14% (0.000237 to 0.001407). It holds the rate under every reasonable multi-year choice I tried.
- The errors I found are small. They are dates and wording on excluded cases, and one completeness check that is weaker than they claim. None of them changes a number in the rate.
- One sensitivity they did not compute: if the year-to-year clumping is allowed for, the top of the interval stays at 0.14% but the bottom falls to about 0.014% (section 7). I record this as a model choice, not an error.

**Corrected figures: equal to theirs. Rate 0.053%, interval 0.024% to 0.14%.**

## 2. The denominator, recounted

Source page: `https://ico.org.uk/action-weve-taken/data-security-incident-trends/`. It says "26 October 2026 – Data updated to Q3 2026". It links one data file: `https://ico.org.uk/media2/iivgw0b0/data-security-incidents-trends-download-q1-2019-to-q3-2026.csv`.

I downloaded the file and counted it with my own script.

- Rows: 237,713. Distinct "BI Reference": 89,591. No report has rows that disagree on year, quarter, category, type, size, sector or decision. This matches their report.
- Distinct reports with "Incident Category" = "Cyber", by the file's "Year" field:

| Year | Theirs | Mine | All reports (mine) |
|---|---|---|---|
| 2019 | 2,346 | 2,346 | 12,259 |
| 2020 | 2,190 | 2,190 | 9,702 |
| 2021 | 2,589 | 2,589 | 9,742 |
| 2022 | 2,156 | 2,156 | 8,798 |
| 2023 | 3,319 | 3,319 | 11,069 |
| 2024 | 3,116 | 3,116 | 12,194 |
| 2025 | 3,181 | 3,181 | 13,462 |
| **2019 to 2025** | **18,897** | **18,897** | 77,226 |
| 2026 Q1 to Q3 | 3,270 | 3,270 | 12,365 |

Other figures in their report that I reproduced from the same file:
- Cyber by type, 2019 to Q3 2026: phishing 9,433; ransomware 5,013; other cyber 4,171; unauthorised access 1,973; malware 1,025; brute force 509; denial of service 43. All match.
- "Unauthorised access" classed as cyber: 778 of 876 in 2019, 50 of 1,329 in 2024. Both match.
- Their cut G (leave unauthorised access out every year): 17,013. Matches.
- Their cut H (add "Hardware/software misconfiguration", which the file puts under non-cyber in every year): 20,671. Matches.
- Cyber reports with 10k to 100k or 100k and above affected, 2019 to 2025: 1,203. Matches. Size "Unknown" for 5,626 of them. Matches.
- "Retail and manufacture" cyber reports 2019 to 2025: 3,939. Matches.
- "Regulatory action taken": 3 reports in the whole file, all non-cyber. Matches.
- Q1 2019 in the current file: 3,372 reports; phishing 207, ransomware 44, malware 19, brute force 12. All match.

The legacy file `https://ico.org.uk/media2/migrated/2616136/data-security-figures-201819q4.csv` gives "Grand Total,3263", "Phishing,205", "Ransomware,43", "Malware,17", "Brute Force,12". All match their report.

The 2018 files also match: `https://ico.org.uk/media2/migrated/2259977/data-security-incident-trends-q1-201819.csv` has a cyber "Grand Total" of 414. `https://ico.org.uk/media2/migrated/2553819/data-security-trends-csv.csv` has a cyber "Grand Total" of 675.

Is "Year" the year the report was received? The page does not say so in plain words. But the financial-year counts from the file sit close to the annual reports' "received" counts. That supports their reading. My counts from the file, against the annual report:

| Financial year | File (mine) | Annual report, "received" |
|---|---|---|
| 2019/20 | 11,531 | 11,854 |
| 2020/21 | 9,453 | 9,532 |
| 2021/22 | 9,503 | 9,571 ("Personal data breaches - Received 2021/22 9571") |
| 2022/23 | 9,100 | 9,146 |
| 2023/24 | 11,582 | 11,680 ("with 11,680 cases reported (2022/23: 9,146)") |
| 2024/25 | 12,299 | 12,412 |
| 2025/26 | 14,078 | 17,431 ("with 17,431 cases reported (2024/25: 12,412)") |

These match their table. The 2025/26 report gives "a higher caseload of 6,317 at year end (2024/25:1,518)". That matches too. One small oddity in the ICO's own figures: the 2022/23 annual report gives 2020/21 receipts as both 9,532 and 9,523 on the same page. It does not matter here.

The page's limitations text matches their quotes word for word, including:
- "The data starts at Q1 2019 as incidents were recorded differently prior to this period."
- "The way we categorise incidents as cyber or non-cyber within the dashboard is currently under review."
- "Under specific circumstances some cases are transferred to a separate system for review. As a result, these cases, which may include some of the larger and more serious breaches, are not included within this data."
- "some reports hold multiple characteristics ... and as such appear on multiple rows".

## 3. The numerator: each notice read again

I downloaded each penalty notice from the URL they give and searched its text.

| # | Organisation | Their date and amount | What the notice says | Result |
|---|---|---|---|---|
| 1 | British Airways plc | 16 Oct 2020, £20m | Header "16 October 2020"; "pursuant to section 155 and Schedule 16 to the Data Protection Act 2018"; "is £20m"; "BA notified the Commissioner of the Attack on 6 September 2018." | Confirmed |
| 2 | Marriott International Inc | 30 Oct 2020, £18.4m | "Dated the 30th day of October 2020"; "is £18.4 million"; "Marriott notified the Commissioner of the Attack on 22 November 2018"; "installed a web shell on a device within the Starwood network on 29 July 2014". | Confirmed |
| 3 | Ticketmaster UK Limited | 13 Nov 2020, £1,250,000 | "Dated the 13th day of November 2020"; "is £1,250,000.00"; "initially notified the Commissioner of the Attack on 23 June 2018"; malicious code in the Inbenta chat bot. | Confirmed |
| 4 | Tuckers Solicitors LLP | 28 Feb 2022, £98,000 | "Dated the 28th day of February 2022"; "The amount of the monetary penalty is £98,000"; "25 August 2020 is the date on which Tuckers reported the breach to the Commissioner"; "24,712 related to court bundles; of the encrypted bundles, 60 were exfiltrated". | Confirmed. The notice also says 24,711 in another paragraph. That is the ICO's own slip. |
| 5 | Interserve Group Limited | 19 Oct 2022, £4,400,000 | "Dated the 19th day of October 2022"; "The amount of the penalty is £4,400,000"; "On 30 March 2020, a phishing email was sent"; "up to 113,000 employees"; "On 5 May 2020 Interserve submitted a personal data breach notification to the Commissioner." | Confirmed |
| 6 | Advanced Computer Software Group Ltd and two group companies | 26 Mar 2025, £3,076,320 | Header "26 MARCH 2025"; "to pay the Commissioner £3,076,320"; ransomware "earliest evidence of execution taking place on 4 August 2022"; "Advanced has agreed not to appeal". | Confirmed. I found no date of the report to the ICO either. |
| 7 | DPP Law Ltd | 14 Apr 2025, £60,000 | Header and "Dated: 14 April 2025"; "to pay the Commissioner £60,000"; "brute force attempts on its network as early as 19 February 2022"; "791 individuals"; "17 July 2022 ... 43 days after the Cyber Incident, DPP reported the personal data breach to the Commissioner." | Confirmed |
| 8 | 23andMe, Inc | 5 Jun 2025, £2,310,000 | Header "5 June 2025"; "a penalty of £2,310,000"; "first reported to both regulators in October 2023"; credential stuffing; "155,592 UK-based customers". | Confirmed |
| 9 | Capita plc and Capita Pension Solutions Ltd | 15 Oct 2025, £8m + £6m | Header "15 October 2025"; "£8,000,000 ... £6,000,000"; "Capita reported the incident to the Commissioner at 18:30 on 31 March 2023"; "a malicious JavaScript file"; "6,656,037 individuals"; "agreed not to appeal". | Confirmed |
| 10 | LastPass UK Ltd | 20 Nov 2025, £1,228,283 | Header "20 November 2025"; "to pay the Commissioner a penalty of £1,228,283"; "On 30 November 2022, LastPass submitted a personal data breach report to the ICO"; "1,631,410 UK-based LastPass customers". | Confirmed. The amount is in the notice itself, not only on the web page as they say. |
| 11 (outside window) | South Staffordshire Plc and South Staffordshire Water Plc | 7 May 2026, £963,900 | "Dated 7 May 2026"; "a penalty of £963,900"; "cyber-attack incident which began on 11 September 2020"; "reported a personal data breach to the ICO on 24 July 2022"; "approximately 633,887 UK data subjects"; "agreed not to appeal". | Confirmed |

Notice URLs, as they cite them, all fetched:
- `https://ico.org.uk/media2/migrated/2618421/ba-penalty-20201016.pdf`
- `https://ico.org.uk/media2/migrated/2618524/marriott-international-inc-mpn-20201030.pdf`
- `https://ico.org.uk/media2/migrated/2618609/ticketmaster-uk-limited-mpn.pdf`
- `https://ico.org.uk/media2/migrated/4019746/tuckers-mpn-20220228.pdf`
- `https://ico.org.uk/media2/migrated/4021951/interserve-group-limited-monetary-penalty-notice.pdf`
- `https://ico.org.uk/media2/gdlfddgc/advanced-penalty-notice-20250327.pdf`
- `https://ico.org.uk/media2/pr4bg5hq/dpp-law-ltd-monetary-penalty-notice.pdf`
- `https://ico.org.uk/media2/kclbljpo/23andme-penalty-notice.pdf`
- `https://ico.org.uk/media2/pv5nhks4/capita-plc-and-cpsl-monetary-penalty-notice.pdf`
- `https://ico.org.uk/media2/xfbl1uaa/lastpass-uk-ltd-penalty-notice.pdf`
- `https://ico.org.uk/media2/xdrfahsw/south-staffordshire-plc-and-south-staffordshire-water-plc-monetary-penalty-notice.pdf`

Every counted case was an attack from outside: hacking, ransomware, phishing, brute force, credential stuffing or malicious code on a payment page. Every one is a section 155 penalty under the GDPR or UK GDPR. By notice date: 2020 has 3, 2022 has 2, 2025 has 5, and 2019, 2021, 2023 and 2024 have 0. That is 10.

## 4. Did they miss any? My own search

### December 2022 to November 2026: the live ICO listing

The enforcement page loads its list from a search service on the same site. I called it myself and read all 10 pages: 232 entries, the newest dated 4 November 2026. That total matches theirs.

- Monetary penalty entries that are not marketing (PECR) cases: TikTok (15 May 2023), Ministry of Defence (26 Feb 2024), Central YMCA (6 Mar 2024), Police Service of Northern Ireland (3 Oct 2024), Advanced (26 Mar 2025), DPP Law (14 Apr 2025), 23andMe (5 Jun 2025), Birthlink (24 Jun 2025), Capita (15 Oct 2025), LastPass (20 Nov 2025), Police Service of Scotland (12 Dec 2025), MediaLab.AI (4 Feb 2026), Reddit (23 Feb 2026), South Staffordshire (7 May 2026).
- All other monetary penalties in the listing are PECR cases: calls, texts or emails. For example, Elderly Aids Limited (6 Aug 2026): "Contravention of Regulations 21 and 24"; Bluon Energy Ltd (4 Nov 2026): "unsolicited live direct marketing calls".
- I also searched every entry, of every type, for "cyber", "ransom", "hack", "attack", "phish", "threat actor" and "breach". No other data protection monetary penalty came up. Every other match was a reprimand, an enforcement notice or a PECR penalty.
- Between June and November 2026 (after the South Staffordshire notice) there is no new data protection penalty. There are only PECR penalties.

So their list for this period is complete. Their excluded list for this period matches the listing too.

### November 2018 to December 2022: archived copies of the listing

I fetched the six UK Government Web Archive captures they cite. Each shows the 50 newest entries of all types, newest first. Here is the date range each one shows:

| Capture | Oldest entry shown | Newest entry shown |
|---|---|---|
| 3 Feb 2020 | 16 Nov 2018 | 15 Jan 2020 |
| 1 Feb 2021 | 28 Nov 2018 | 28 Jan 2021 |
| 15 Apr 2021 | 10 May 2019 | 5 Mar 2021 |
| 9 Mar 2022 | 5 Mar 2021 | 8 Mar 2022 |
| 3 Oct 2022 | 15 Sep 2021 | 30 Sep 2022 |
| 1 Feb 2023 | 7 Mar 2022 | 14 Dec 2022 |

The ranges overlap with no gap. The last one ends on 14 December 2022, the date of the oldest entry in the live listing. So there is no hole in the coverage.

Non-marketing monetary penalties in the captures: Uber (26 Nov 2018), Grove Pension Solutions (26 Mar 2019), London Borough of Newham (4 Apr 2019), True Visions Productions (10 Apr 2019), Bounty (UK) Ltd (11 Apr 2019), Life at Parliament View (19 Jul 2019), Doorstep Dispensaree (20 Dec 2019), DSG Retail (9 Jan 2020), Cathay Pacific (4 Mar 2020), British Airways (16 Oct 2020), Marriott (30 Oct 2020), Ticketmaster (13 Nov 2020), Mermaids (8 Jul 2021), HIV Scotland (22 Oct 2021), Cabinet Office (2 Dec 2021), Tuckers (10 Mar 2022), Clearview AI (26 May 2022), Tavistock and Portman (30 Jun 2022), Easylife (5 Oct 2022), Interserve (24 Oct 2022). The dates are listing dates, not notice dates.

Grove, Newham, True Visions and Bounty are not in their report. They do not need to be. All four are dated before 25 May 2019, and each concerns conduct before the UK GDPR, not an outside attack. The 2018/19 annual report confirms there were "no monetary penalties under DPA 2018 in 2018-19". Their omission changes nothing, but a complete exclusion list would name them.

None of the cases in these captures is a cyber penalty under the GDPR that they missed.

### Annual reports

I fetched all eight annual reports at the URLs they give and searched the text.

- 2018/19: "there were no monetary penalties under DPA 2018 in 2018-19". Confirmed. Also "£500,000 fine against Equifax Ltd, relating to a cyber security incident". Confirmed.
- 2019/20: gives no count of penalties. It says "2019/2020 saw the issue of the first penalty notices under the Data Protection Act 2018 for non-compliance" and that for BA and Marriott "The regulatory process is ongoing". Confirmed.
- 2020/21: "In 2020/21 we issued 3 fines, totalling £39.65m." £20m + £18.4m + £1.25m = £39.65m. Confirmed. Also "Both of these CMPs have agreed payment plans". Confirmed.
- 2021/22: "We issued four DPA fines totalling £633k". £25,000 + £10,000 + £500,000 + £98,000 = £633,000. Confirmed. HIV Scotland "led to a £10,000 fine". Confirmed.
- 2022/23: "the cyber team has delivered seven reprimands ... The team also issued one penalty notice, totalling £4.4 million." Confirmed. That is Interserve.
- 2023/24: "three penalty notices totalling £13,057,500 (2022/23: two penalty notices totalling £7,631,200)". Confirmed. TikTok £12,700,000 + MoD £350,000 + Central YMCA £7,500 = £13,057,500. The cyber section reports "eight reprimands" and no penalty.
- 2024/25: "two UK GDPR penalty notices totalling £3,826,320". PSNI £750,000 + Advanced £3,076,320 = £3,826,320. Confirmed. Also "we completed 15 investigations and managed 61 incidents this year. The team triaged 1,746 reports". Confirmed.
- 2025/26: "eight UK GDPR penalty notices totalling £32,402,373". Confirmed. The eight listing amounts sum to exactly that: £60,000 + £2,310,000 + £18,000 + £14,000,000 + £1,228,283 + £66,000 + £247,590 + £14,472,500.

**A gap in their reconciliation, now closed.** They did not reconcile 2022/23. The 2022/23 report says the civil investigations team "issued one enforcement notice and two penalty notices totalling £7,631,200". I fetched the two notices from the 1 February 2023 archive capture:
- Clearview AI: "The amount of the penalty is £7,552,800".
- Tavistock and Portman: "The amount of the penalty is £78,400", "Dated the 9th day of June 2022".

£7,552,800 + £78,400 = £7,631,200 exactly. Together with the cyber team's one notice (Interserve, £4.4m), 2022/23 reconciles. There are no hidden cyber penalties.

**A caution on "match to the pound".** The annual report totals are not exhaustive. Easylife's UK GDPR notice ("The amount of the penalty is £1,350,000", Article 5(1)(a), notice file dated 4 October 2022) falls in 2022/23. It is in neither the £7,631,200 nor the £4.4m. So a matching total proves that the cases named are in the total. It does not prove that no case sits outside it. For cyber cases the cyber team's own sentence in each report closes the gap for 2022/23 and 2023/24. For other years the listings carry the proof.

## 5. The excluded cases

I fetched the notices for the excluded cases they cite.

- DSG Retail: "a monetary penalty under section 55A of the Data Protection Act 1998" (the text extraction reads "SSA"); "£500,000"; "Dated the 7th day of January 2020"; "DSG first notified the Commissioner that it had suffered a cyber attack on 8 June 2018." Exclusion on legal basis confirmed. Note that DSG reported after 25 May 2018, but its conduct ended on 25 April 2018. That is why the 1998 Act applied.
- Cathay Pacific: section 55A of the 1998 Act; "£500,000"; "Dated the 10th day of February 2020". Confirmed.
- Life at Parliament View: "DATA PROTECTION ACT 1998"; a hacker demanded a ransom. Confirmed. I could not find £80,000 in the notice text because of scan quality. The 3 February 2020 archive capture says "Life at Parliament View Ltd fined £80,000". Confirmed there.
- Doorstep Dispensaree: section 155; "£275,000"; "47 unlocked crates". Confirmed. Not an attack.
- Mermaids: section 155; "£25,000"; documents "searchable and viewable online by third parties through internet search engine results". Confirmed. Not an attack.

Their judgement calls are stated and reasonable: they count at the notice amount, ignore appeals and collection, keep Advanced (a processor), and count Capita and South Staffordshire once each. Their side numbers are correct:
- Without Advanced: 9 / 18,897 = 0.048%.
- With DSG and Cathay added: 12 / 18,897 = 0.064%.

## 6. Do the years match?

- Both parts of the primary cut use calendar 2019 to 2025: notices by notice date, reports by year received. The windows match.
- The populations do not fully match. Three counted notices (BA, Marriott, Ticketmaster) arise from reports made in 2018, which are outside the denominator. Reports from 2024 and 2025 are in the denominator but have had no time to draw a penalty. They say both things openly and give cut D (7 / 18,897) and the cohort cuts E and F to show the effect. I agree with how they handle it.
- Starting in 2019 loses no penalty. The 2018/19 annual report's sentence is confirmed.

## 7. Arithmetic and the interval

I recomputed every cut with exact 95% Poisson bounds (chi-square method):

| Cut | Count / reports | Rate | Exact 95% | Theirs |
|---|---|---|---|---|
| A (primary) | 10 / 18,897 | 0.0529% | 0.0254% to 0.0973% | same |
| B | 11 / 22,167 | 0.0496% | 0.0248% to 0.0888% | same |
| C | 10 / 16,551 | 0.0604% | 0.0290% to 0.1111% | same |
| D | 7 / 18,897 | 0.0370% | 0.0149% to 0.0763% | same |
| E | 6 / 9,281 | 0.0646% | 0.0237% to 0.1407% | same |
| F | 8 / 12,600 | 0.0635% | 0.0274% to 0.1251% | same |
| G | 10 / 17,013 | 0.0588% | 0.0282% to 0.1081% | same |
| H | 10 / 20,671 | 0.0484% | 0.0232% to 0.0890% | same |
| Large breaches (context) | 8 / 1,203 | 0.665% | 0.287% to 1.310% | same |
| 2025 alone | 5 / 3,181 | 0.157% | 0.051% to 0.367% | same point |

The sums check: 2,346 + 2,190 + 2,589 + 2,156 = 9,281; plus 3,319 = 12,600; plus 3,116 + 3,181 = 18,897; plus 3,270 = 22,167.

**Is the interval wide enough?** The test: does 0.024% to 0.14% hold the rate under the other reasonable choices?
- Every multi-year point estimate I tried lies inside: cuts A to H (0.037% to 0.065%), without Advanced (0.048%), with DSG and Cathay (0.064%), and the cohort of reports from 2022 and 2023 (6 / 5,475 = 0.11%).
- Only single years lie outside: 2025 alone (0.16%) and the 2022 cohort alone (4 / 2,156 = 0.19%). They disclose and reject the 2025 figure for a sound reason: 2023 and 2024 had no cyber penalty.
- So the interval passes the test as set.

**Sensitivity they did not compute.** They say the yearly counts (0, 3, 0, 2, 0, 0, 5) are lumpier than Poisson, but they do not adjust for it. I measured it. Against counts in proportion to each year's reports, Pearson chi-square is 16.1 on 6 degrees of freedom, a dispersion factor of about 2.7. If the exact bounds are scaled by that factor, cut A becomes about 0.014% to 0.14%. The top stays where they put it. The bottom falls to about the lower bound of their cut D. This rests on seven yearly counts and one model choice, so I do not call their interval wrong. But a reader should know the low end is the softer of the two.

## 8. Errors found

None of these changes the count, the rate or the interval.

1. Wrong dates on excluded cases. Three excluded cases are cited to their notices but carry the date of the web listing:
   - Doorstep Dispensaree: "Dated the 17th Day of December 2019", not 20 December.
   - Mermaids: "Dated the 5th day of July 2021", not 8 July.
   - Life at Parliament View: "Dated the 17th day of July 2019", not 19 July.
   For counted cases they used the notice date, so the rule is not applied the same way to both lists.
2. LastPass: they say the amount came "from the ICO enforcement page". The notice itself states "a penalty of £1,228,283". This understates their evidence. It is not a wrong figure.
3. Their annual report table quotes the 2022/23 comparative "(2022/23: two penalty notices totalling £7,631,200)" as if it were the year's total. It counts only the civil investigations team, which was Clearview and Tavistock. It leaves out Interserve (cyber team) and Easylife. Their "match to the pound" check is therefore weaker than they say, as explained in section 4.
4. Their exclusion list leaves out four non-PECR penalties that are in the archived listing: Grove Pension Solutions, London Borough of Newham, True Visions Productions and Bounty (UK) Ltd, all dated March or April 2019. Each falls before any DPA 2018 penalty and is not an attack case, so the count is unaffected.
5. Amounts they marked "not fetched": Clearview £7,552,800 (the listing says "£7.5m"), Tavistock and Portman £78,400 (notice dated 9 June 2022) and Easylife £1,350,000. All three are excluded, so the rate is unaffected.

## 9. Things I found that they did not use

- **The ICO's own outcome rate.** The 2018/19 annual report gives "Civil monetary penalty pursued" for 0.05% of closed breach reports. The 2019/20 report gives 0.03% of the 12,789 reports "Finished". These cover all reports, not only cyber ones, and they count penalties "pursued", not issued. Both lie inside their interval. That is an independent check on the order of size.
- **Sector tags.** The archived listing files Ticketmaster and Interserve under "Retail and manufacture". The ICO's own sector tag therefore puts two of the ten in the modelled firm's sector. Ticketmaster's case, a compromised online payment page, is the nearest to "an attacker takes an online shop's customer data". This softens their line that none of the counted penalties is against a shop, though it does not change the rate.

## 10. What the rate means

I agree with their section 7. In short:
- It is a rate per cyber report, and most reports are small. For a large breach the rate is roughly ten times higher (about 0.7%, weak evidence, biased high). This is the biggest caveat for the model.
- Penalties arrive about 1.5 to 4 years after the report. The recent cohorts are not complete.
- The file is short of recent reports (about 81% of 2025/26 receipts). This pushes cuts A and B slightly high.
- The cyber label has moved over time. Cuts G and H bound the effect at 0.048% to 0.059%.
- One attack on a supplier produces many reports (Advanced, Capita). This pushes a per-event rate up compared with the per-report rate.

## 11. Could not check

- Appeal outcomes for the counted penalties. A secondary source (a law firm note found by search) says Ticketmaster appealed and the tribunal stayed the appeal in April 2021 (case EA/2020/0359/FP). I did not fetch a primary tribunal decision, and I did not use this. Under their rule (count the notice as issued) it changes nothing.
- Collection of 23andMe's penalty, given the company's insolvency process, which the notice mentions. Not checked.
- The 23andMe enforcement page sentence "following a large-scale cyber attack in 2023". The listing returned no description for that entry, and I did not fetch the page. The notice itself confirms the attack.
- The notices for PSNI and Police Service of Scotland. I saw only the listing summaries, which support the exclusions.
- The archived ICO trends page they used for Equifax's date (20 September 2018). Not fetched. Equifax is excluded, so the rate is unaffected.
- The October to December 2018 cyber count. They could not find it, and neither did I look further. Not used in the rate.

## 12. Corrected figures

- Numerator: 10 (unchanged).
- Denominator: 18,897 cyber reports, 2019 to 2025 (unchanged).
- Rate: 0.053%, a probability of 0.000529 (unchanged).
- Interval: 0.024% to 0.14%, probabilities 0.000237 to 0.001407 (unchanged). If the yearly clumping is allowed for, the low end could fall to about 0.014%. The high end does not move.
