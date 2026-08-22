---
status: accepted
---

# Release gate: compute the bump, refuse a weaker declaration, no override

Two gates evaluate every policy bump against a corpus of workloads and derive **major / minor /
patch** from observed verdict movement, rather than trusting the number a human typed into the
release workflow. The **publisher gate** runs inside `cut-release.yml`, before `git tag`: it
evaluates the candidate policy set and every supported lower version against a generated corpus,
observes how the cage spec each pod receives moves between versions, and derives the bump from that
movement. The **adopter gate** runs inside each institution's `shift-left.yml`, on the Renovate bump
pull request: it does not recompute the publisher's answer — a second answer to the same question has
no tie-breaker — but verifies the publisher's signed evidence against an identity the institution
holds itself, then computes that institution's own composed bump across every party it consumes. Both
gates **refuse a declared bump weaker than the computed one and permit a stronger one**; neither ever
rewrites the declared number. We chose this over trusting the declared bump, even though a human
typed it in good faith, because `CONTEXT.md`'s major/minor/patch definitions already describe verdict
movement on currently-compliant workloads, and nothing before this gate ever tested that the declared
number matched what actually moved — the faithful-floor release line shipped two version-mechanics
mistakes found by review, twice, not by CI.

## Considered options

- **Compute the bump from observed movement and refuse a weaker declaration (chosen).** The gate
  evaluates the candidate against a generated corpus, observes how the cage spec each pod receives
  moves between versions, and derives the bump `CONTEXT.md` already defines. A declared bump weaker
  than computed refuses the release; a stronger one is permitted and the discrepancy is printed. The
  gate always emits and signs its evidence, including when it refuses.
- **Trust the declared bump, test it after the fact (rejected — status quo).** A human types the
  number, then authors a fixture that agrees with it. That is post-hoc justification, not derivation,
  and it already missed version-mechanics gaps that only review caught, not CI.
- **Compute the bump and rewrite the declared number (rejected).** Would remove the human's editorial
  judgement entirely, and let a corpus with an unstated coverage hole silently set the wrong number
  with no review point to catch it. The gate refuses; it never rewrites.
- **Allow an override at some scope (rejected).** See "No override", below.

## No override

There is no override, at any scope, for anyone. `CONTEXT.md` already bans exemptions — a carve-out
for a named workload — at any scope, under any name. An override on this gate is the same shape
wearing a different label: evidence, a signature and an expiry attached to a decision to admit
something the rule would otherwise refuse. That is the exemptions ledger this estate already deleted
(`.scratch/govern-what-you-dont-control/issues/05-remove-the-exemption-ledger.md`). The only relief
valve is over-declaring — a publisher may always ship a stronger bump than the gate computed — and any
disagreement with the computed bump is resolved by a reviewed pull request to the generator or the
policy, exactly as `CONTEXT.md` already requires for changing what gets enforced.

## Consequences

- **[ADR-0002](0002-adoption-pinned-plus-renovate-pr.md) gains evidence, not a new gate.** ADR-0002
  already makes the reviewed pull request the only way a new version lands; before this gate, the
  reviewer approved a version string and a diff with no way to see which workloads changed verdict.
  This gate's signed evidence — verified by the adopter gate against its own held identity — is what
  the reviewer now reads alongside the diff. Neither gate weakens or bypasses the reviewed-PR
  requirement; the review is still where a disagreement with the computed bump gets resolved.
- **A refusal is signed too.** The gate emits and signs its evidence on refusal as well as on success —
  a refusal is the most valuable output it produces, not a silent dead end.
- **The publisher gate runs before `git tag`.** The release workflow refuses to move a tag once cut, so
  a late refusal would burn a version number; this gate has to run, and refuse, before that point.
- **The adopter gate does not recompute the publisher's answer.** It verifies the publisher's signed
  evidence against an identity the institution holds itself, then computes its own composed bump
  across every party it consumes — a second, independent recomputation of the same question would have
  no tie-breaker against the publisher's.
- **A coverage hole is grounds for a reviewed PR, never for an override.** The gate states what it
  didn't reach; it does not let an unreached case become a reason to bypass the rule.
