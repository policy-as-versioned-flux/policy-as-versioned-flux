# Conditional policy, not exemptions (residual risk of permissive branches)

Type: prototype
Status: resolved
Blocked by: 02, 04

## Question

**Reframed 2026-07-23 (human):** exemptions aren't carve-outs — they're **business-as-usual, just
more policy.** Not "the rule says X but team Y is exempt", but "**you may do X if you meet these
conditions**", and *anyone* who meets them may. That kills the thin-end-of-the-wedge (there's no
special favour to expand — it's a rule, applied uniformly), and it *forces you to articulate the
why* (the condition) instead of "because they asked". Pin:

- **Conditions are policy** — team, location, attestation-present, no-PII, data-classification,
  time-bounded ("only for the next 6 months"), etc. All expressible as CEL in the `ValidatingPolicy`
  itself (`matchConditions` / `validations`), *not* a separate exemption object. Kyverno
  `PolicyException` reserved only for a genuine one-off that can't be generalised to a condition (if
  ever).
- **Uniform + attestable** — a conditional permission applies to everyone who meets it; it lives in
  git, versioned and signed, so it's auditable and non-favouritist by construction. Temporal
  conditions handle expiry; the "ratchet down" is a version bump tightening the condition.
- **Residual risk of the permissive branches** — each permissive condition *accepts* some risk;
  that residual £ still feeds the balance-sheet (06) and must be computable per branch. Granting a
  broader condition raises residual; tightening it lowers it — the £ moves.
- **Feeds the war-gamer (13)** — the active conditional permissions are war-gamed too: does the risk
  a condition accepts still hold under the current threat landscape, or should it tighten?

Output: the conditional-policy model (CEL patterns) + how permissive-branch residual risk is
computed and fed back.

## Answer

Settled at the decision level (charting framing + research 08/09). **Exemptions are dissolved into
conditional policy** — not carve-outs but "you may X *if* conditions C" (team/location/attestation/
data-class/time-bound), expressed uniformly in **Kyverno CEL**, versioned like any rule. The
residual risk of each permissive branch still feeds the FAIR £ (04). Mechanically it stays a **git
ledger entry → rendered `PolicyException`** (Flux `prune` on retire + `cleanup.kyverno.io/ttl`
backstop) and the ledger entry **generates the OSCAL `risk`/POA&M object** (09). CEL patterns and the
render template are build-work, not a remaining decision.
