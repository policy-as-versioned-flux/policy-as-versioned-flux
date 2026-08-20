# 14 — The forward layer speaks for one institution in a six-org estate

Type: task
Status: open
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
