# ICO penalty rate per personal data breach report: the "all reports" count

Filed note: this is the first of three counts. Its check is `all-reports-check.md`, which corrects one sensitivity row and leaves the rate as it is. The choice built on the three counts is `CHOICE.md`.

Fetched and counted on 14 November 2026. Every figure below was read from a page or file fetched that day. Nothing in the rate comes from memory.

## The answer

- **Rate: 0.00021 per report** (20 penalties over 95,466 reports). That is about 1 penalty for every 4,800 breach reports.
- **Defensible interval: 0.00013 to 0.00040** (1 in 7,800 to 1 in 2,500). Sensitivity checks that break the "same years in both" rule reach 0.00048.
- The model's current value is 1. The count says it is about 5,000 times too high as a rate over all reports.
- This is the lowest defensible rate. It is a rate over every report, most of which are small. It is not the rate for a serious breach at a large retailer. See "What the rate means".

## Method

- Numerator: every ICO monetary penalty under UK GDPR or the Data Protection Act 2018 (section 155) that was for a failure to keep personal data secure or for a personal data breach. Counted by the date on the penalty notice.
- Denominator: every personal data breach report the ICO received, from the ICO's own counts.
- Window: ICO financial years 2018/19 to 2025/26 (1 April 2018 to 31 March 2026), the same in both.

Why these years:

- The ICO's annual reports are its complete count of breach reports received. They are by financial year. Eight complete years exist.
- 2018/19 is the first year of mandatory reporting. It starts 54 days before 25 May 2018. The year before, the ICO received 3,311 reports in total, so those 54 days add a few hundred reports at most to a denominator of 95,466. I left them in and say so.
- The ICO's other count, the "data security incident trends" file, is by calendar year. It starts at Q1 2019 and leaves some cases out (see "Denominator"). I use it as a second window, 2019 to 2025, not as the main one.
- The main window ends at 31 March 2026 because that is the last complete year in the annual reports.

## Numerator: the list

20 penalties in the main window. One more after it (row 21), used only in a variant.

"Notice date" is the date on the notice itself where I could read it. "ICO page date" is given where it differs.

| # | Organisation | Notice date | Amount | What it was for | FY | Calendar year |
|---|---|---|---|---|---|---|
| 1 | Doorstep Dispensaree Ltd | 17 Dec 2019 (file name; ICO page 20 Dec 2019) | £275,000 | About 500,000 patient documents left in unlocked containers outside a pharmacy | 2019/20 | 2019 |
| 2 | British Airways | 16 Oct 2020 | £20,000,000 | Cyber attack; details of more than 400,000 customers | 2020/21 | 2020 |
| 3 | Marriott International Inc | 30 Oct 2020 | £18,400,000 | Cyber attack on Starwood guest records, undetected until 2018 | 2020/21 | 2020 |
| 4 | Ticketmaster UK Limited | 13 Nov 2020 | £1,250,000 | Customers' payment details exposed through a chat bot on the payment page | 2020/21 | 2020 |
| 5 | Mermaids | 5 Jul 2021 (ICO page 8 Jul) | £25,000 | Charity's emails with users' data viewable through search engines | 2021/22 | 2021 |
| 6 | HIV Scotland | 18 Oct 2021 (ICO page 22 Oct) | £10,000 | Group email that showed all recipients' addresses | 2021/22 | 2021 |
| 7 | Cabinet Office | 15 Nov 2021 (ICO page 2 Dec) | £500,000, later cut to £50,000 | New Year Honours recipients' home addresses published online | 2021/22 | 2021 |
| 8 | Tuckers Solicitors LLP | 28 Feb 2022 (ICO page 10 Mar) | £98,000 | Ransomware attack on a law firm | 2021/22 | 2022 |
| 9 | Tavistock & Portman NHS Foundation Trust | 9 Jun 2022 (ICO page 30 Jun) | £78,400 | Bulk email that revealed 1,781 clinic users' addresses | 2022/23 | 2022 |
| 10 | Interserve Group Limited | 19 Oct 2022 (ICO page 24 Oct) | £4,400,000 | Cyber attack; data of up to 113,000 employees | 2022/23 | 2022 |
| 11 | Ministry of Defence | 7 Dec 2023 (ICO page 26 Feb 2024) | £350,000 | Emails sent with addresses in "To" instead of "BCC"; 265 addresses disclosed | 2023/24 | 2023 |
| 12 | The Central YMCA | 6 Mar 2024 | £7,500 | Email with "CC" instead of "BCC" to people in an HIV support programme | 2023/24 | 2024 |
| 13 | Police Service of Northern Ireland | 26 Sep 2024 (ICO page 3 Oct) | £750,000 | Staff data published on a public website by mistake | 2024/25 | 2024 |
| 14 | Advanced Computer Software Group Ltd | 26 Mar 2025 | £3,076,320 | Ransomware attack on a data processor; 79,404 people | 2024/25 | 2025 |
| 15 | DPP Law Ltd | 14 Apr 2025 | £60,000 | Cyber attack on a law firm; also late reporting (Article 33) | 2025/26 | 2025 |
| 16 | 23andMe, Inc | 5 Jun 2025 | £2,310,000 | Cyber attack in 2023; 155,592 UK users | 2025/26 | 2025 |
| 17 | Birthlink | 24 Jun 2025 | £18,000 | Charity destroyed about 4,800 personal records without authority | 2025/26 | 2025 |
| 18 | Capita plc and Capita Pension Solutions Ltd | 15 Oct 2025 | £14,000,000 | Cyber attack in 2023; over 6 million people. One breach, two entities, counted once | 2025/26 | 2025 |
| 19 | LastPass UK Ltd | 20 Nov 2025 | £1,228,283 | Backup database with data of about 1.6 million UK customers taken | 2025/26 | 2025 |
| 20 | Police Service of Scotland | 12 Dec 2025 | £66,000 | Unauthorised disclosure of a witness's phone data; also late reporting | 2025/26 | 2025 |
| 21 | South Staffordshire Plc and South Staffordshire Water Plc | 7 May 2026 | £963,900 | Cyber incident; about 633,887 people. Outside the main window | 2026/27 | 2026 |

Count by financial year: 0, 1, 3, 4, 2, 2, 2, 6 (2018/19 to 2025/26). Total 20.

Count by calendar year: 1, 3, 3, 3, 1, 2, 7 (2019 to 2025). Total 20. Plus 1 in 2026 up to 30 September.

### Source for each row

Rows 1 to 10 are no longer on the live ICO site. I read them from the UK Government Web Archive copies of the ICO's own pages. Rows 11 to 21 are on the live ICO site.

1. `https://webarchive.nationalarchives.gov.uk/ukgwa/20200203120358mp_/https://ico.org.uk/action-weve-taken/enforcement/doorstep-dispensaree-ltd-mpn/` : "has fined a London-based pharmacy £275,000 for failing to ensure the security of special category data." Notice (same archive, `.../media/action-weve-taken/mpns/2616742/doorstop-mpn-20191217.pdf`), page 1: "a penalty notice under s.155 Data Protection Act 2018 ... The amount of the fine is £275,000".
2. `https://webarchive.nationalarchives.gov.uk/ukgwa/20201106201915mp_/https://ico.org.uk/action-weve-taken/enforcement/british-airways/` : "Date 16 October 2020 ... has fined British Airways (BA) £20m for failing to protect the personal and financial details of more than 400,000 of its customers."
3. `https://webarchive.nationalarchives.gov.uk/ukgwa/20201106202146mp_/https://ico.org.uk/action-weve-taken/enforcement/marriott-international-inc/` : "Date 30 October 2020 ... The ICO has fined Marriott International Inc £18.4million for failing to keep millions of customers' personal data secure."
4. `https://webarchive.nationalarchives.gov.uk/ukgwa/20201116050700mp_/https://ico.org.uk/action-weve-taken/enforcement/ticketmaster-uk-limited/` : "Date 13 November 2020 ... The ICO has fined Ticketmaster UK Limited £1.25 million for failing to protect customers' payment details."
5. `https://webarchive.nationalarchives.gov.uk/ukgwa/20210712111323mp_/https://ico.org.uk/action-weve-taken/enforcement/mermaids/` : "has fined transgender charity Mermaids £25,000 for failing to keep the personal data of its users secure." Notice `mermaids-mpn-20210705.pdf`: "Dated the 5th day of July 2021".
6. `https://webarchive.nationalarchives.gov.uk/ukgwa/20211101063509mp_/https://ico.org.uk/action-weve-taken/enforcement/hiv-scotland-mpn/` : "Scottish charity fined for contraventions of Articles 5(1)(f), 32(1) and 32(2) of the UK GDPR." Notice `mpn-hiv-scotland-20211018.pdf`: "The amount of the monetary penalty is £10,000." and "Dated the 18th day of October 2021".
7. `https://webarchive.nationalarchives.gov.uk/ukgwa/20230601132022mp_/https://ico.org.uk/action-weve-taken/enforcement/cabinet-office-mpn/` : "fined the Cabinet Office £500,000 for disclosing postal addresses of the 2020 New Year Honours recipients online ... In November 2022, the ICO has agreed to reduce the £500,000 Monetary Penalty Notice to £50,000, which the Cabinet Office agreed to pay." ICO news of 3 November 2022 (archived at `.../ukgwa/20230201000000mp_/https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2022/11/ico-and-cabinet-office-reach-agreement-on-new-year-honours-data-breach-fine/`): "issued its fine to the Cabinet Office on 15 November 2021".
8. `https://webarchive.nationalarchives.gov.uk/ukgwa/20220312060418mp_/https://ico.org.uk/action-weve-taken/enforcement/tuckers-solicitors-llp-mpn/` : "Tuckers Solicitors LLP contravened Article 5(1)(f) of the GDPR." Notice `tuckers-mpn-20220228.pdf`: "amount of the monetary penalty is £98,000", "Tuckers became aware on 24 August 2020 of a ransomware attack", "Dated the 28th day of February 2022".
9. `https://webarchive.nationalarchives.gov.uk/ukgwa/20220911064456mp_/https://ico.org.uk/action-weve-taken/enforcement/the-tavistock-portman-nhs-foundation-trust/` : "the Trust used Outlook to send bulk emails to 1,781 Gender Identity Clinic service users. The Trust failed to comply with Chapter II GDPR, specifically Articles 5(1)(f), and 32(1) & (2)." Notice: "The amount of the penalty is £78,400", "Dated the 9th day of June 2022".
10. `https://webarchive.nationalarchives.gov.uk/ukgwa/20230201115412mp_/https://ico.org.uk/action-weve-taken/enforcement/interserve-group-limited/` : "failed to process personal data in a manner that ensured appropriate security ... vulnerable to a cyber-attack ... affected the personal data of up to 113,000 employees". Notice: "The amount of the penalty is £4,400,000.", "Dated the 19th day of October 2022."
11. `https://ico.org.uk/action-weve-taken/enforcement/2024/02/ministry-of-defence-1/` : "265 unique email addresses were disclosed in breach of GDPR Article 5(1)(f). The MOD were fined £350,000." Notice `https://ico.org.uk/media2/5vdd103u/ministry-of-defence-monetary-penalty-notice.pdf`: "Dated: The 7th day of December 2023".
12. `https://ico.org.uk/action-weve-taken/enforcement/2024/04/the-central-young-men-s-christian-association-mpn/` : "The Central YMCA have been fined £7,500 and issued a reprimand." Notice: "contraventions of Articles 5(1)(f) and 32(1) and (2) of the UK GDPR", "Dated the 6th day of March 2024".
13. `https://ico.org.uk/action-weve-taken/enforcement/2024/10/police-service-of-northern-ireland-mpn/` : "has been fined £750,000 for infringing Articles 5(1)(f), 32(1) and (2) of the UK GDPR". Notice cover: "26 September 2024".
14. `https://ico.org.uk/action-weve-taken/enforcement/2025/03/advanced-computer-software-group-limited/` : "has fined Advanced Computer Software Group Ltd (Advanced) £3.07m for security failings that put the personal information of 79,404 people at risk." Exact amount from the 2024/25 annual report: "a penalty notice to the value of £3,076,320".
15. `https://ico.org.uk/action-weve-taken/enforcement/2025/04/dpp-law-ltd/` : "has fined law firm DPP Law Ltd £60,000 for its infringements of Articles 5(1)(f), 32(1), 32(2) and 33(1) of the UK GDPR".
16. `https://ico.org.uk/action-weve-taken/enforcement/2025/06/23andme/` : "has fined 23andMe, Inc £2,310,000 for infringements of Articles 5(1)(f) and 32(1) of the UK GDPR".
17. `https://ico.org.uk/action-weve-taken/enforcement/2025/06/birthlink/` : "has fined Scottish charity Birthlink £18,000 after it destroyed approximately 4,800 personal records". Notice: infringed "Article 5(1)(f) ... Article 32(1)-(2) ... Article 33".
18. `https://ico.org.uk/action-weve-taken/enforcement/2025/10/capita-plc/` : "has fined Capita plc and Capita Pension Solutions Ltd a combined £14m following a cyber attack in April 2023".
19. `https://ico.org.uk/action-weve-taken/enforcement/2025/11/lastpass-uk-ltd/` : "£1,228,283 penalty issued to password management provider LastPass UK Ltd on 20 November 2025 in respect of infringements of Article 5(1)(f) and Article 32(1)(f) UK GDPR."
20. `https://ico.org.uk/action-weve-taken/enforcement/2025/12/police-service-of-scotland/` : "has fined the Police Service of Scotland £66,000 and issued a Reprimand". Notice: "infringements of Articles 5(1)(f), 32(1), 5(1)(c), 25(1)-(2) ... and Article 33 UK GDPR", "the unauthorised disclosure of that personal data".
21. `https://ico.org.uk/action-weve-taken/enforcement/2026/05/south-staffordshire-plc-and-south-staffordshire-water-plc/` : "has imposed a fine of £963,900 ... for the infringement of Article 5(1)(f) and Article 32(1) of the UK General Data Protection Regulation."

### How the list was built, and how I know it is complete

- Live ICO enforcement list (`https://ico.org.uk/action-weve-taken/enforcement/`, type "Monetary penalties"): 65 entries on 14 November 2026. The oldest is dated 14 December 2022. I read all 65 descriptions. 51 are marketing-rule penalties. 14 are UK GDPR penalties. Of those 14, 11 are about security or a breach (rows 11 to 21).
- I also pulled the list with no type filter (232 entries) to look for fines filed under another type. I found none that changes the count.
- For 2018 to 2022 I fetched the archived copies of the same ICO list from the UK Government Web Archive (`https://webarchive.nationalarchives.gov.uk/ukgwa/*/https://ico.org.uk/action-weve-taken/enforcement/`). I fetched 3,387 distinct captures of the list and its paging URLs, dated 24 May 2018 to January 2025. Their union holds 258 monetary penalty entries dated 2016 to 2024. I read every entry dated after 1 May 2018.
- The archive and the live list overlap from December 2022 to October 2024 and agree.
- The ICO's listing dates are not always the notice date. The ICO says so on the page: "When searching by date, incorrect results may be produced due to errors with the dates of some documents added before 31 December 2024." The Ministry of Defence entry is dated 26 February 2024 but the notice is dated 7 December 2023. I used notice dates. Only that one row changes its calendar year.

The count agrees with what the annual reports say, year by year:

| FY | Annual report says | My list of UK GDPR penalties for that year | Security or breach |
|---|---|---|---|
| 2018/19 | "there were no monetary penalties under DPA 2018 in 2018-19" | none | 0 |
| 2019/20 | "2019/2020 saw the issue of the first penalty notices under the Data Protection Act 2018" (no number given) | Doorstep Dispensaree | 1 |
| 2020/21 | "In 2020/21 we issued 3 fines, totalling £39.65m." | BA, Marriott, Ticketmaster (£39.65m) | 3 |
| 2021/22 | "We issued four DPA fines totalling £633k" | Mermaids, HIV Scotland, Cabinet Office, Tuckers (£633,000) | 4 |
| 2022/23 | "two penalty notices totalling £7,631,200" and, for the cyber team, "one penalty notice, totalling £4.4 million" | Clearview AI (£7,552,800) and Tavistock (£78,400), together £7,631,200; Interserve (£4,400,000); plus Easylife (see below) | 2 |
| 2023/24 | "three penalty notices totalling £13,057,500" | TikTok, MoD, Central YMCA (£13,057,500) | 2 |
| 2024/25 | "We issued two UK GDPR penalty notices totalling £3,826,320" | PSNI, Advanced (£3,826,320) | 2 |
| 2025/26 | "eight UK GDPR penalty notices totalling £32,402,373" | DPP Law, 23andMe, Birthlink, Capita, LastPass, Police Scotland, MediaLab, Reddit (£32,402,373) | 6 |

The totals for 2020/21 to 2025/26 match to the pound. The Clearview amount is from its notice: "The amount of the penalty is £7,552,800" (`https://webarchive.nationalarchives.gov.uk/ukgwa/20220601125939id_/https://ico.org.uk/media/action-weve-taken/mpns/4020436/clearview-ai-inc-mpn-20220518.pdf`).

I also read the 118 archived entries dated 25 May 2018 to the end of 2022 that are not tagged as monetary penalties. None is a data protection penalty filed under the wrong type.

### Notice files read

Dates and amounts quoted from "the notice" above come from these files.

- Row 1: `https://webarchive.nationalarchives.gov.uk/ukgwa/20200203120358id_/https://ico.org.uk/media/action-weve-taken/mpns/2616742/doorstop-mpn-20191217.pdf`
- Row 5: `https://webarchive.nationalarchives.gov.uk/ukgwa/20210712111323id_/https://ico.org.uk/media/action-weve-taken/mpns/2620171/mermaids-mpn-20210705.pdf`
- Row 6: `https://webarchive.nationalarchives.gov.uk/ukgwa/20211101063509id_/https://ico.org.uk/media/action-weve-taken/mpns/4018736/mpn-hiv-scotland-20211018.pdf`
- Row 8: `https://webarchive.nationalarchives.gov.uk/ukgwa/20220312060418id_/https://ico.org.uk/media/action-weve-taken/mpns/4019746/tuckers-mpn-20220228.pdf`
- Row 9: `https://webarchive.nationalarchives.gov.uk/ukgwa/20220911064456id_/https://ico.org.uk/media/action-weve-taken/mpns/4020812/the-tavistock-portman-nhs-foundation-trust-mpn.pdf`
- Row 10: `https://webarchive.nationalarchives.gov.uk/ukgwa/20230201115412id_/https://ico.org.uk/media/action-weve-taken/mpns/4021951/interserve-group-limited-monetary-penalty-notice.pdf`
- Row 11: `https://ico.org.uk/media2/5vdd103u/ministry-of-defence-monetary-penalty-notice.pdf`
- Row 12: `https://ico.org.uk/media2/migrated/4029420/central-ymca-monetary-penalty-notice.pdf`
- Row 13: `https://ico.org.uk/media2/migrated/4031177/psni-penalty-notice.pdf`
- Row 14: `https://ico.org.uk/media2/gdlfddgc/advanced-penalty-notice-20250327.pdf` (cover: "26 MARCH 2025")
- Row 15: `https://ico.org.uk/media2/pr4bg5hq/dpp-law-ltd-monetary-penalty-notice.pdf` (cover: "14 April 2025")
- Row 16: `https://ico.org.uk/media2/kclbljpo/23andme-penalty-notice.pdf` (cover: "5 June 2025")
- Row 17: `https://ico.org.uk/media2/bvljtpy2/birthlink-mpn.pdf` (cover: "24 June 2025")
- Row 18: `https://ico.org.uk/media2/pv5nhks4/capita-plc-and-cpsl-monetary-penalty-notice.pdf` (cover: "15 October 2025")
- Row 19: `https://ico.org.uk/media2/xfbl1uaa/lastpass-uk-ltd-penalty-notice.pdf` (cover: "20 November 2025")
- Row 20: `https://ico.org.uk/media2/b1kcsxom/police-scotland-reprimand-and-penalty-notice.pdf` (cover: "12 December 2025")
- Row 21: `https://ico.org.uk/media2/xdrfahsw/south-staffordshire-plc-and-south-staffordshire-water-plc-monetary-penalty-notice.pdf` (cover: "7 May 2026")

### What I left out, and why

- **Marketing-rule penalties (PECR).** Nuisance calls, texts and emails. 51 on the live list and about 130 in the archive since May 2018. They are not data-breach penalties.
- **UK GDPR penalties that were not about security.** Clearview AI (May 2022, scraping faces), Easylife (October 2022, profiling customers; Article 5(1)(a)), TikTok (2023, children's data), MediaLab.AI (4 February 2026, £247,590, children's data), Reddit (23 February 2026, £14,472,500, children's data).
- **Penalties for not paying the data protection fee.** These are under the 2018 Act but have nothing to do with a breach.
- **Penalties under the Data Protection Act 1998 issued after 25 May 2018.** They are for breaches before mandatory reporting began, and the method says UK GDPR or the 2018 Act only. Four fall inside the calendar window. I checked the first page of each notice and each is headed "DATA PROTECTION ACT 1998": London Borough of Newham (4 April 2019, £145,000), Life at Parliament View (19 July 2019, £80,000), DSG Retail (9 January 2020, £500,000), Cathay Pacific (4 March 2020, £500,000). Dates are the ICO page dates. The four notice files are under `https://webarchive.nationalarchives.gov.uk/ukgwa/`: `20190603122905id_/https://ico.org.uk/media/action-weve-taken/mpns/2614724/mpn-london-borough-of-newham-20190401.pdf`, `20191002140557id_/https://ico.org.uk/media/action-weve-taken/mpns/2615396/mpn-life-at-parliament-view-limited-20190717.pdf`, `20200203120357id_/https://ico.org.uk/media/action-weve-taken/mpns/2616891/dsg-mpn-20200107.pdf`, `20200323175650id_/https://ico.org.uk/media/action-weve-taken/mpns/2617314/cathay-pacific-mpn-20200210.pdf`. Seven more security penalties are listed between 25 May and 31 December 2018 (Bible Society, Gloucestershire Police, IICSA, Equifax, Bupa, Heathrow, Uber); the 2018/19 annual report says no 2018 Act penalty was issued that year, so they are 1998 Act penalties. I use these eleven only in a "what if" variant. DSG Retail matters for the question asked: it is a large UK retailer, fined after a cyber attack on its tills that affected at least 14 million people, and it sits in this left-out group.
- **Notices of intent.** Not counted. Only final penalty notices.
- **Reprimands, enforcement notices and prosecutions.** Not monetary penalties.

Judgement calls:

- **Reduced penalties still count.** The Cabinet Office penalty was cut from £500,000 to £50,000 by agreement. The breach still drew a penalty, so it counts as one.
- **Unpaid or appealed penalties still count.** The term being priced is the chance of a penalty being imposed. I did not check whether each was paid or is under appeal.
- **Two entities, one breach, one count.** Capita and South Staffordshire.
- **Borderline rows kept in.** Birthlink (records destroyed, not leaked) and Police Scotland (a disclosure inside a misconduct case). Both notices find breaches of Articles 5(1)(f), 32 and 33, so they meet the definition. Without them the main count is 18.

## Denominator: breach reports received

### Main: ICO annual reports, by financial year

| FY | Reports received | Sentence or cell | Source |
|---|---|---|---|
| 2018/19 | 13,840 | "we received 13,840 PDB reports during 2018-19, an increase from 3,311 in 2017-18" | Annual report 2018/19, HC 2299, 8 July 2019, p. 28 |
| 2019/20 | 11,854 | Chart "Personal Data Breaches - Received": "2019/20 11,854" | Annual report 2019/20, HC 477, 16 July 2020, p. 65 |
| 2020/21 | 9,532 | Chart "Personal Data Breaches - Received": "2020/21 9,532" | Annual report 2020/21, HC 354, 7 July 2021, p. 54 |
| 2021/22 | 9,571 | Chart "Personal data breaches - Received": "2021/22 9571" | Annual report 2021/22, HC 392, 12 July 2022, p. 54 |
| 2022/23 | 9,146 | Table row "Received 9,146 9,571 9,523" | Annual report 2022/23, HC 1440, 13 July 2023, p. 72 |
| 2023/24 | 11,680 | "with 11,680 cases reported (2022/23: 9,146), an increase of 28%" | Annual report 2023/24, HC 30, 18 July 2024, p. 40 |
| 2024/25 | 12,412 | "with 12,412 cases reported (2023/24: 11,680), an increase of 6%" | Annual report 2024/25, HC 956, July 2025, p. 44 |
| 2025/26 | 17,431 | "with 17,431 cases reported (2024/25: 12,412) - an increase of 40%" | Annual report 2025/26, HC 274, July 2026, p. 57 |
| **Total** | **95,466** | | |

Note: the 2022/23 report prints 2020/21 as 9,523 in one table and 9,532 in the chart beside it. The 2020/21 and 2021/22 reports both say 9,532. I used 9,532.

File URLs:

- 2018/19: `https://webarchive.nationalarchives.gov.uk/ukgwa/20211004204223id_/https://ico.org.uk/media/about-the-ico/documents/4017979/annual-report-201819.pdf`
- 2019/20: `https://webarchive.nationalarchives.gov.uk/ukgwa/20211004204223id_/https://ico.org.uk/media/about-the-ico/documents/2618021/annual-report-2019-20-v83-certified.pdf`
- 2020/21: `https://webarchive.nationalarchives.gov.uk/ukgwa/20211004204223id_/https://ico.org.uk/media/about-the-ico/documents/2620166/hc-354-information-commissioners-ara-2020-21.pdf`
- 2021/22: `https://ico.org.uk/media2/migrated/4021039/ico-annual-report-2021-22.pdf`
- 2022/23: `https://ico.org.uk/media2/migrated/4025864/annual-report-2022-23.pdf`
- 2023/24: `https://ico.org.uk/media2/migrated/4030348/annual-report-2023-24.pdf`
- 2024/25: `https://ico.org.uk/media2/1wyfliqp/annual-report-2025-ico-v4-1-complete.pdf`
- 2025/26: `https://ico.org.uk/media2/ybsi5n0j/ico-annual-report-202527.pdf`

The first three are no longer on the ICO site. I fetched the ICO's own files from the UK Government Web Archive.

### Second count: the ICO "data security incident trends" file, by calendar year

Source: `https://ico.org.uk/media2/iivgw0b0/data-security-incidents-trends-download-q1-2019-to-q3-2026.csv`, linked from `https://ico.org.uk/action-weve-taken/data-security-incident-trends/`. The page says "26 October 2026 – Data updated to Q3 2026" and "the data is presented in calendar years and quarters".

The file has 237,713 rows. One report can sit on several rows. The page says: "some reports hold multiple characteristics ... and as such appear on multiple rows". I counted distinct values of the "BI Reference" column. That gives 89,591 reports.

| Calendar year | Distinct reports |
|---|---|
| 2019 | 12,259 |
| 2020 | 9,702 |
| 2021 | 9,742 |
| 2022 | 8,798 |
| 2023 | 11,069 |
| 2024 | 12,194 |
| 2025 | 13,462 |
| **2019 to 2025** | **77,226** |
| 2026, Q1 to Q3 | 12,365 |

Limits of this file, in the ICO's words:

- "The data starts at Q1 2019 as incidents were recorded differently prior to this period." So it has nothing for 25 May to 31 December 2018.
- "Under specific circumstances some cases are transferred to a separate system for review. As a result, these cases, which may include some of the larger and more serious breaches, are not included within this data."

I checked the file against the annual reports by adding its quarters into financial years. It holds 97% to 99.5% of the annual-report count for 2019/20 to 2024/25. For 2025/26 it holds only 81% (14,078 against 17,431). The 2025/26 annual report gives a likely reason, under the performance measure "We will refer or close 80% of PDB reports within 30 days" (I did not note the page number): "Total numbers of breach reports increased in 2025/26, with Q2 alone seeing the receipt of over 6,000 reports, a significant number of which related to a single incident, with each affected organisation submitting their own report." The trends file shows no quarter above 4,604. So a block of reports about that one incident seems to be in the annual report count and not in the file. That is my reading, not an ICO statement. For the latest year the file is short, and the annual reports are the better count of "every report received". That is why the annual reports are the main denominator.

## The rate

Main: 20 penalties / 95,466 reports = **0.000209**, about 1 in 4,800.

Other reasonable choices:

| Variant | Penalties | Reports | Rate | 1 in |
|---|---|---|---|---|
| **Main: FY 2018/19 to 2025/26, annual reports** | 20 | 95,466 | 0.000209 | 4,773 |
| Drop the start-up year: FY 2019/20 to 2025/26 | 20 | 81,626 | 0.000245 | 4,081 |
| Calendar 2019 to 2025, trends file | 20 | 77,226 | 0.000259 | 3,861 |
| Calendar 2019 to 30 September 2026, trends file | 21 | 89,591 | 0.000234 | 4,266 |
| Lag of 2 years: reports FY 2018/19 to 2023/24, notices FY 2020/21 to 2025/26 | 19 | 65,623 | 0.000290 | 3,454 |
| Lag of 3 years: reports FY 2018/19 to 2022/23, notices FY 2021/22 to 2025/26 | 16 | 53,943 | 0.000297 | 3,371 |
| What if 1998 Act security penalties are added (calendar 2019 to 2025) | 24 | 77,226 | 0.000311 | 3,218 |
| What if 1998 Act security penalties are added (FY 2018/19 to 2025/26) | 31 | 95,466 | 0.000325 | 3,080 |

The first four rows have the same years in the numerator and the denominator. The last four do not, or change the numerator's definition. They are sensitivities.

Point estimates run from 0.00021 to 0.00033. No reasonable choice of years moves the rate outside that band.

By single year the rate swings a lot, because the counts are tiny: from 0 (2018/19) to 0.00042 (2021/22) by financial year, and from 0.00008 (2019) to 0.00052 (2025) by calendar year. One year is not a usable estimate.

### The interval

- Exact (Garwood) 95% Poisson interval on a count of 20: 12.22 to 30.89.
- On the main denominator: **0.000128 to 0.000324** (1 in 7,800 to 1 in 3,100).
- Low end of my interval: 0.000128. This is the Poisson lower limit on the widest denominator (12.22 / 95,466).
- High end of my interval: 0.000400. This is the Poisson upper limit on the narrowest window that still has the same years in both: calendar 2019 to 2025 (30.89 / 77,226).
- **Interval: 0.00013 to 0.00040.** It is the envelope of the Poisson intervals across the four same-year windows in the table.
- Above the interval, as sensitivities only: the Poisson upper limit is 0.00046 if the 1998 Act penalties are added, and 0.00048 on the 3-year-lag variant (25.98 / 53,943). The lag variants use different years in the numerator and the denominator, so they are outside the method's rule. They show which way the truth lies, not where the interval ends.

The reports are treated as a fixed number and the penalties as a Poisson count. With a rate this small that is the same as an exact binomial interval to three figures.

## What the rate means, and what pushes it

This is the rate at which one breach report, taken at random from all reports, is followed by a penalty. Each assumption below is listed with the direction it pushes the rate.

1. **Most reports are small.** The trends file shows what the ICO did with each report. Of the 77,226 reports in 2019 to 2025, 68,722 (89%) are marked "No Further Action" or "Informal Action Taken". 6,919 (9%) are marked "Investigation Pursued". 1,583 are "Not Yet Assigned" and 2 are "Regulatory action taken". A serious breach at a company with £86 million turnover is not a random report. Its chance of a penalty is higher than this rate, and this method cannot say how much higher. **The rate is too low for a serious breach.**
2. **A penalty comes years after the breach.** Examples from the fetched pages and notices: Cabinet Office, breach 27 December 2019, notice 15 November 2021. Interserve, attack March to May 2020, notice October 2022. Ministry of Defence, breach in 2021, notice December 2023. Advanced, attack August 2022, notice March 2025. Capita, attack 2023, notice October 2025. LastPass, incident August 2022, notice November 2025. Birthlink, records destroyed April 2021, notice June 2025. The gap is about 2 to 4 years. So reports from 2023/24 onward have not yet had time to draw their penalties, and they are 41,523 of the 95,466. **Same-year counting pushes the rate down.** The lag variants (0.00029 to 0.00030) show the size: about 40% higher than the main rate.
3. **The first year had no penalties by construction.** 2018/19 has 13,840 reports and zero penalties under the new law, because no case could finish that fast. **Pushes the rate down.** Dropping it gives 0.000245.
4. **Reports are rising while penalties follow old reports.** 2025/26 has 17,431 reports, 40% more than the year before. **Pushes the rate down.**
5. **One breach can be many reports.** A breach at a supplier can be reported by each client. Advanced and Capita both held data on behalf of other organisations: the ICO page says Advanced "processes people's personal information on behalf of these organisations". The numerator counts breaches and the denominator counts reports. The 2025/26 annual report says that in one quarter "a significant number" of over 6,000 reports "related to a single incident, with each affected organisation submitting their own report". I did not check that each penalised breach arrived as exactly one report. **The per-breach rate is higher than the per-report rate.** If a few thousand of the 17,431 reports in 2025/26 are one incident, the main rate is understated by a few percent for that reason alone.
6. **The numerator covers every sector, not retail.** Of the 20, 11 were businesses, 4 were charities and 5 were public bodies. Since June 2022 the ICO has cut or replaced fines for public bodies. The Cabinet Office cut was explained as "our new approach to working more effectively with public authorities". The 2022/23 annual report says the trial "would have resulted in three fewer reprimands and the equivalent rise in penalty notices". **This holds the all-sector count down, but does not bear on a retailer.**
7. **Enforcement policy changes.** Seven of the 20 penalties are dated in calendar 2025 alone. If that pace holds, the future rate is higher than the eight-year average. If 2025 was a cluster of old cases finishing together, it is not. **Unknown direction; recent years point up.**
8. **Counting by imposed, not paid.** Reduced and appealed penalties count as 1. **Pushes the rate up** against a "penalty finally paid in full" reading. With 20 penalties, removing one moves the rate by 5%.
9. **1998 Act penalties left out.** In 2018 to 2020 the ICO was still fining pre-GDPR breaches under the old Act. Those breaches are not in the denominator, so leaving them out is consistent. A model that wants "ICO fines per year over reports per year" would add them. **Leaving them out pushes the rate down;** adding them gives 0.00031 to 0.00033.

A cross-check that the trends file cannot be used as a numerator: its "Decision Taken" column shows "Regulatory action taken" for only 3 of 89,591 reports (2 in 2024, 1 in 2026). The ICO says the larger cases are moved to another system and left out of the file. The penalty list has to come from the enforcement pages, as here.

Plain reading for the model: 0.0002 is a floor for the "penalty rate" term, not a best estimate for a serious retail breach. The true figure for this retailer lies between this floor and whatever a narrower denominator (serious or investigated breaches only) gives.

## Not found, not checked, or from memory

- **Reason for the 2025/26 gap** between the trends file (14,078) and the annual report (17,431). The annual report describes a single incident with many reports. No ICO page says those reports are the ones missing from the file. The number of reports tied to that incident is not stated.
- **A count of 2018 Act penalties in the 2019/20 annual report.** The report gives no number. The one penalty for that year rests on the archived ICO list alone.
- **Reports received between 25 May 2018 and 31 March 2019 only.** No ICO figure found. The 2018/19 figure covers the full financial year from 1 April 2018.
- **Appeal and payment status of each penalty.** Checked only for the Cabinet Office. Doorstep Dispensaree's penalty was reduced on appeal to £92,000: from memory, not fetched, and not used in the rate.
- **The notice date inside the Doorstep Dispensaree notice.** The notice is a scanned image. I read page 1 but not the dated page. The date 17 December 2019 comes from the ICO's file name. The ICO page date is 20 December 2019. Either way it is 2019 and FY 2019/20.
- **Notice dates inside the British Airways, Marriott and Ticketmaster notices.** Not opened. Dates are the ICO page dates. All three fall well inside one year.
- **The 1998 Act "what if" list is not reconciled** to the annual report count of 22 such penalties in 2018/19. It is used only as a sensitivity.
- **Completeness before December 2022 rests on the web archive.** If the ICO issued a penalty and never listed it on its enforcement page, I would not see it. The annual report totals for 2020/21 and 2021/22 match my list to the pound, which makes a missing penalty in those years unlikely.

## Sources fetched (all on 14 November 2026)

- ICO, Data security incident trends page and CSV: `https://ico.org.uk/action-weve-taken/data-security-incident-trends/`
- ICO, Enforcement action list (live) and each penalty page and notice named above: `https://ico.org.uk/action-weve-taken/enforcement/`
- ICO annual reports 2021/22 to 2025/26 (ICO site) and 2018/19 to 2020/21 (ICO files held by the UK Government Web Archive); list at `https://ico.org.uk/about-the-ico/our-information/annual-reports/`
- UK Government Web Archive captures of the ICO enforcement list, its entry pages and notices, 2018 to 2025: `https://webarchive.nationalarchives.gov.uk/ukgwa/*/https://ico.org.uk/action-weve-taken/enforcement/`
- ICO news, 3 November 2022, "ICO and Cabinet Office reach agreement on New Year Honours data breach fine" (archived copy).

No secondary source was used for any figure.
