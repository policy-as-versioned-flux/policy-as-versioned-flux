# 09 — Proportionality comparison (the money shot)

**What to build:** The *same* control resolves to Audit in `driftwood` and Deny in `ludlow` because their £ differ — proportionality proven by comparison. The load-bearing live beat.

**Blocked by:** 07, 08

**Status:** done (2026-08-20) — `estate/verify/proportionality/verify-proportionality.sh` PASSes offline

- [x] The same control (encrypt-at-rest / no-EOL-log4j) is Audit in `driftwood`, Deny in `ludlow` — `risk_bought £21,107 | driftwood band £40,000 -> Audit | ludlow band £5,000 -> Deny`; `policies/encrypt-at-rest-driftwood.yaml` carries `validationActions: [Audit]`, `-ludlow.yaml` carries `[Deny]`, bodies differ only by the action + org labels (≤6 diff lines, asserted)
- [x] `verify-proportionality.sh` asserts the divergent verdicts and the £ that drives them — full run: `PASS: same control, same £ (risk_bought £21107) — Audit in driftwood, Deny in ludlow.` Live dry-run tail self-skips (reachable kubeconfig contexts exist but have no Kyverno CRDs installed) — offline proof is what actually carries this AC

## Comments

- 2026-08-20 (audit mo-02): the ticket calls itself "the load-bearing live beat" but `verify-proportionality.sh` is actually in the OFFLINE array of `estate/talk/verify-all.sh` and its offline proof is what PASSes; note the script's optional live tail is slow (~90-150s) against stale `kind-*` kubeconfig contexts before it gives up and reports "reachable but Kyverno CRDs not installed" — those contexts are not a working live estate (see ticket 02). Status corrected from `ready-for-agent` to `done` on the offline proof, which the repo's own house convention treats as sufficient.
