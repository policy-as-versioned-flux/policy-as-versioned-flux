# 78 — The proposer can only tighten, the enacted tier is bound to the priced tier, and the proposal is signed

Type: task (AFK)
Status: open
Blocked by: none

## Question

Ticket 74 waits for the first real band crossing. The 2026-09-02 review found that when it comes, the proposer will loosen the cage. `tier_pr.apply_tier_declaration()` writes the proposed tier onto the governed Namespace unconditionally, and nothing under `platform/wargamer/` clamps tighten-only. The proposer fires per price line. Driftwood's only reachable crossing is its threat-register line moving baseline to restricted, which would stamp `restricted` over a namespace declared `isolated`, because the other two lines already select isolated. ADR-0022 says the cage mutation is tighten-only; the proposer is not.

Three builds, all before 74 may fire:

1. Selection over the party, not the line: the tier the proposer writes is the strictest `proposed_tier` across the party's `prices[]`, clamped to the declared `overlay.floor`, and never looser than the current declaration unless the party's aggregate residual justifies it and the PR body says so. Record the rule in the selection-policy package the adopter publishes, and bump its version.
2. One check binds the enacted tier to the priced tier: read `proposed_tier` from `composed/evidence.json` and `posture.acme.io/tier` from the governed Namespace manifest, and refuse a label looser than the strictest priced tier. Wire it into each adopter's shift-left and into the gate.
3. The proposal commit is gitsign-signed with the workflow's Actions identity (reversal 16): copy `twin-sweep.yml`'s gitsign block into `propose-tier.yml` on all three adopters, add `propose-tier.yml` to each adopter's expected-identity regexp, and delete the `"signed": True` literal in `wargamer.py` (ticket 76 item 6).

Done = a test plants a per-line crossing on a party already at isolated and asserts the proposer writes nothing looser; the binding check is in `talk/verify-all.sh`; the first real proposal commit verifies under gitsign against the adopter's own regexp.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R2. Findings: scope/F1 (skeptic's corrected form), twin-validity/TWIN-09, security/SS-08, principles/P5-3. Blocks ticket 74. Whether the selection compares one line or the summed retained residual to the band is pound-engine/PE-05 and Q4 in ticket 75; item 1 takes the strictest-line rule as the safe interim and says so.
