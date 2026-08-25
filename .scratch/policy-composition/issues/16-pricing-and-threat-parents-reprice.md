# 16 — Pricing and threat parents re-price, and never apply

Type: task
Status: resolved
Blocked by: 13

Source: [`spec.md`](../spec.md), *Pricing, threat and the proposer*. Decisions:
[ADR-0006](../../../docs/adr/0006-deterministic-policy-no-time-conditions.md),
[ADR-0010](../../../docs/adr/0010-sunset-scheduled-proposals-not-application.md),
[ADR-0015](../../../docs/adr/0015-adopter-runs-the-proposer-and-it-opens-the-pr.md).

## What to build

A bump to a `pricing` or `threat` parent moves the price, and the document shows it. Nothing else
moves.

The composition prices each caged workload through the estate's own machinery. The `ico` penalty
schema goes through `ico`'s own converter. The threat, CVE and EOL feeds go through the feeds module.
No second risk engine, no second appetite store. For each party it prints the old price, the new
price, the old tier and the proposed tier. A price move that changes no tier prints as no change.

A proposed tier of `deny` is marked as an issue subject, never a label value. The composition itself
opens nothing. Ticket `17` wires the proposer.

The document gains `prices[]`.

## Acceptance criteria

- [x] An `ico` penalty-schema bump moves the uncaged exposure on the `uk-gdpr lower-tier` entry through `ico`'s own converter.
- [x] A threat-register bump moves the exposure through the feeds module.
- [x] On the estate's real bands, both bumps print no tier change, and the document says so.
- [x] A fixture band that a bump crosses prints a proposed tier.
- [x] A proposed `deny` is marked as an issue subject and never as a label value.
- [x] No rendered file changes on any price move. A byte comparison proves it.
- [x] The composition calls no scheduler and reads no wall clock except through an explicit `--as-of` argument passed to the feeds module.

## Answer

Built, inside the same `compose()` (`.estate-clone/platform/compose/composition.py`, extended in
place — no new module, same seam ticket 12 established: `compose(adopter_dir, parent_trees) ->
(document, rendered_files)`).

**Every declared `pricing`/`threat` edge is priced twice, every run.** `compute_prices()` walks the
party artefact's own `inherits` list; for each `pricing`/`threat` edge it calls `price_parent()`,
which prices the SAME fixed subject at two versions through the estate's own machinery and no
other: `ico`'s own converter (`schema/to_fair_scenario.py build ... uk-gdpr lower-tier` — the fixed
entry spec.md's own acceptance wording names) for a `pricing` edge, and `_threat_scenario()` —
already ticket 13's, reused unchanged — for a `threat` edge. Both go through `graded/cage.py`'s
real `select()`, `mode="warn"`, against the adopter's own `risk/appetite.json` band read by ticket
13's `_appetite_tolerance()`. No second risk engine, no second appetite store.

**"Old" is the version the last signed composed artefact's own header recorded** for that
`(party, kind)` (`_previous_parent_version()`, one more field of `_previous_header()` ticket 14/15
already read). No prior header, or no prior edge of that kind, means nothing to compare a bump
against yet: old and new both price at this run's own version — an honest "no move", not a skipped
computation. This runs on the FIRST composition too (proved: real driftwood's very first run
already carries two `prices[]` entries, both `changed: false`, `old_version == new_version`).

**Proved against the real estate, chained across two runs** (the same `_commit_header` pattern
tickets 14/15 use): a `party.yaml` pricing pin bumped `v1 -> v2` moves driftwood's uncaged
`uk-gdpr/lower-tier` exposure (£16.9M -> £9.0M) through `ico`'s own converter; a `threat` pin bumped
`v1 -> v2` moves tuppence's exposure (£222,574 -> £326,139, the register's own tuppence-only
changelog) through the feeds module. On both, driftwood's/tuppence's REAL bands land on `deny`
before and after — the document prints `changed: false`, honestly, matching the prototype's own
finding that the wiring moves and the real-estate outcome does not. No real appetite band anywhere
in the estate straddles a boundary on either real bump, so the crossing case is proved directly
against `price_parent()` with a fixture band (£1,000,000): `deny -> quarantine`, `changed: true`.

**A proposed `deny` is marked `proposed_as: "issue"`, every other tier `"label"`** — ADR-0015:
`select_tier` can return `deny`, and the `cage-tier` MutatingPolicy coerces any label value it
doesn't recognise to `baseline`, so a merged `tier: deny` label would invert the proposal in
silence. This is the mark, not the act: composition itself opens nothing here, exactly as spec.md
says — ticket 17 wires the proposer that reads this mark.

**No rendered file changes on any price move.** Pricing/threat edges carry no rule and are never
looped into `load_implementations`/the members-render step (by construction, unchanged since
ticket 12) — proved as a byte comparison of every rendered file except `HEADER.yaml` (which, by
design, DOES carry the bumped parent's new SHA/version in its `parents[]` — advisory-only, never
read by Kyverno, the same file every prior ticket already excludes from its own "nothing else
changes" assertions).

**No wall clock, no scheduler.** Neither converter this section calls takes an `--as-of` at all —
`ico`'s `build` and the feeds module's `threat` subcommand are both timeless; an `eol` parent kind
does not exist in the party artefact schema, so composition never has occasion to pass one.
Verified as an import-statement scan of composition.py's own real code (`import datetime`, `from
datetime`, `import time`, `import sched`, `import croniter` — none present), not a prose
substring match, which would false-positive on this very check's own forbidden-token list and on
this docstring's own description of the rule.

The document gains `prices[]` (`source`, `kind`, `old_version`/`new_version`,
`old_price`/`new_price`, `old_tier`/`proposed_tier`, `changed`, `proposed_as`).

Review gate: PASS (`./verify-composition.sh` exit 0, every prior ticket's assertions still hold
plus five new `OK` lines for this ticket; SKIPs exit 0 when `.estate-clone` is absent).
