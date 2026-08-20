# 14 — The forward layer speaks for one institution in a six-org estate

Type: task
Status: resolved
Blocked by: none

## Question

`estate/platform/wardley/wardley.py:137` hardcodes `"org": "driftwood"` in `forward_signal()`, and
both `forward_into_wargamer()` and the scenario path derive their tolerance from that single string
(`wardley.py:153`, `:194`). Every forward claim the estate makes is therefore **driftwood's**.

This is a correctness bug anywhere; on a map whose destination is *six real organisations* it is a
contradiction of the thesis. Verified during the scenario-slate research: at ludlow's band phishing
does **not** drift, and ransomware drifts **at base** — so the forward verdicts the demo shows are not
merely incomplete for other institutions, they are different.

**The job:** make the forward layer per-institution. Emit a forward signal per org (or take the org as
a parameter and run the set), so `verify-wardley.sh` reports each institution's own drift, and the
war-gamer proposes against the right band. Consider what this means for the proposal count the demo
quotes — three institutions may produce three different sets, and that is the honest answer.

**Also fix `selfcheck()`'s vacuous assertion while you are in this file** (delegated from the
vacuous-gate sweep, which deliberately does not touch `wardley.py` to avoid colliding with this
ticket). It asserts `credential-stuffing-aas` "must not signal (no movement)", but that component has
`base_risk: null` and `forward_signal()` skips any component lacking a `base_risk` *before* it
considers movement — so the assertion cannot fail for the reason it claims. The scenario-slate
research supplies a replacement control case (`nb-refining-capacity`) that carries a real `base_risk`
and still emits nothing, which is the assertion worth making.

Do this **before** the slate lands (ticket 06), or the new components bake the same
single-institution assumption in behind four more entries.

## Answer

Resolved 2026-08-20. `forward_signal(intel, org)` and `forward_into_wargamer(intel, org)` now
take the org as a required argument (no more hardcoded `"driftwood"`); `forward_signal_all()`
and `forward_into_wargamer_all()` run the set, reading the three institutions from
`../risk/appetite.json` so the org list can't drift from the bands it's priced against.
`wardley.py forward-signal` / `wargame` run all three institutions by default, `--org <name>`
for one. `verify-wardley.sh` step 4 now prints and asserts each institution's own drift, plus a
divergence check (driftwood and ludlow must not drift on the identical set) so the per-org fix
is machine-checked, not just re-run three times under different labels. Confirmed the exact
claim in the ticket: at ludlow's band phishing does not drift and ransomware already drifts at
the reactive base; driftwood ends up with 2 proposals, tuppence and ludlow with 1 each (4 total,
not "3 × the driftwood count") — the honest proposal-count answer the ticket asked for.

`selfcheck()`'s vacuous `credential-stuffing-aas` assertion is fixed in place, not replaced with
`nb-refining-capacity` (that's ticket 06's data, and this ticket is meant to land first): a
synthetic clone of the same stationary component, given a real `base_risk`, still doesn't
signal — isolating the actual "no commoditising movement" gate instead of relying on the
component's coincidental `base_risk: null`.

Evidence: `bash estate/platform/wardley/verify-wardley.sh` passes (5/5 sections), including the
new per-institution divergence assertions in sections 4 and selfcheck's section 3b/4.
