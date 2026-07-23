# Regulator-as-upstream-dependency: machine-readable control & penalty artifacts

Type: prototype
Status: resolved
Blocked by: 02

## Question

Design how the two regulator orgs publish **versioned, machine-readable artifacts** that
institutions consume as pinned dependencies — completing the dependency graph at the top
(regulator → institution → team, Renovate-bumpable at every hop). Pin:

- **`policy-as-versioned-nist` (controls, real):** how do institutions consume the genuine 800-53
  OSCAL catalog as a pinned dependency? Mirror vs submodule vs Renovate-tracked release. This is the
  "already real today" beat — NIST literally ships controls-as-code.
- **`policy-as-versioned-ico` (penalties, modelled):** design `penalties@vYYYY.N` — a machine-readable
  schedule of **real public** fine magnitudes (GDPR maxima, ICO enforcement amounts, HIPAA tiers,
  PCI). Format (OSCAL? a bespoke schema? both?), signing/provenance (same gitsign+Rekor transport),
  and how a bump ("regulator raises fines") flows down to re-tune each institution's £ risk and
  therefore its proportionate controls.
- **The consumption seam** — how an institution *pins* a regulator artifact version, how Renovate
  opens the bump PR, and how the shift-left check (03) surfaces "your penalty schedule is stale".
- **Honesty markers** — the artifacts must be unmistakably demo (the `policy-as-versioned-` prefix)
  and the penalty data traceably sourced from real public figures, never invented rulings.

Output: the artifact formats + the pin/consume/bump seam + a rough prototype of `ico/penalties`.

## Answer

Regulators are **versioned, signed upstream dependencies**, consumed like any feed. **`nist` = real
OSCAL** controls (native). **`ico` penalties = a small bespoke, signed, versioned schema**
(regime → violation-type → fine formula/cap) that feeds the FAIR **loss-magnitude** directly
(2026-07-23) — *not* force-fit into OSCAL, which models controls/assessment, not fine schedules.
Both are pinned+signed and bump like a dependency, so a regulator change arrives as a reviewable PR.
The `endoflife.date` EOL feed and CVE feeds ride the same "versioned upstream" pattern. Schema shape
+ ingestion are build-work.
