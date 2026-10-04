CVE v3 replaces the illustrative catalogue with captured CISA KEV records joined to NVD CVSS severity and FIRST EPSS. FX 1.1.0 replaces illustrative August rates with the authentic HMRC table. Threat-register v4 publishes the cited scheduled-agent credential-misuse frequency row and requires the subscriber's own magnitude.

Data provenance:

- CVE: 1,733 KEV records, CISA catalog `2026.10.02`, FIRST score date `2026-10-03`. The replay corpus preserves the builder inputs and SHA256 hashes of the original CISA/NVD/FIRST responses. Missing joined records refuse. Existing severity magnitude bands remain the publisher's declared inputs.
- FX: 141 rates for `2026-08`, foreign units per GBP1, rebuilt exactly from [HMRC's August CSV](https://www.trade-tariff.service.gov.uk/api/v2/exchange_rates/files/monthly_csv_2026-8.csv). Raw SHA256: `8da9e83a830282c94cbcb31779cbeb93d7a2a739d1bb898cbec62182b7b29fad`. This historical table claims no October rates.
- Threat-register: the new row discloses its cited grade-3 frequency basis and what could not be observed. Headline magnitudes and scenarios remain v3's; no subscriber magnitude is fabricated.

Validation:

- Both release gates pass: `verify-feeds.sh` against the workflows' exact platform `v2.0.1` / `533dccb0a823001b396fd60ab08014bf75065a37`, and `verify-market-and-news.sh`.
- A real local git fixture still fails when a model credential is introduced. The detector permits only the reviewed NVD data-credential identifier.
- Primary CVE builder/selfcheck and exact corpus rebuild pass; EPSS-only changes compute `none`, severity changes `patch`.
- FX exact CSV rebuild and missing/invalid-month refusals pass. Unchanged CVE/FX replay computes `none` and preserves the EPSS date.
- Nine older major payload files retain their exact bytes. Declared bumps compute CVE `major`, FX `minor`, threat-register `major`.

After review and merge, proposed workflow cuts are `cve/v3.0.0`, `fx/v1.1.0`, and `threat-register/v4.0.0`. This source change cuts no tag, changes no adopter pin, and grants no workload risk binding. Preparation was performed by Codex with no human at the keyboard.
