# 82 — Licence, attribution and disclaimers

Type: task (AFK build, HITL decision on named individuals)
Status: open
Blocked by: none

## Question

Nine public repositories, no legal realism assessed. The hub holds the thesis, 24 ADRs, NORTH-STAR, the truth surface and 56,000 lines of Python under no licence at all, while every unit is Apache-2.0. The nist repo redistributes the NIST SP 800-53 rev 5.2.0 catalogue, a US Government work, under a blanket Apache-2.0 licence with no NOTICE and no attribution. Ico's signed payload says `authority: ICO (Information Commissioner's Office)` and no README, party artefact or org description anywhere says the party is a demonstration and not the regulator. The twin's public corpus names eleven real firms and four living Intel chief executives beside scored fraud and failure probabilities, and publishes a probability about a listed issuer.

1. Add `LICENSE` (Apache-2.0, matching the units) at the hub root and one line in README.
2. Add a NOTICE to nist attributing the catalogue to NIST and stating its public-domain status.
3. Add a `DISCLAIMER.md` to ico and nist and one line in every README and party artefact: a demonstration party, not affiliated with the named authority. Add a gate check that every party artefact carries the line.
4. The owner decides whether the twin corpus keeps named living individuals, and whether the Intel scenario needs a "not investment research" line. Record the decision against NORTH-STAR §6's exclusion of real surveillance data.

Done = `gh api .../license` returns Apache-2.0 for the hub; the NOTICE and disclaimers exist and are checked; the named-individuals decision is recorded with a reason.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R11. Findings: operability/O5, completeness C5 and C10. Cheap, and a precondition for every purpose in ticket 75 Q1 except a private talk.
