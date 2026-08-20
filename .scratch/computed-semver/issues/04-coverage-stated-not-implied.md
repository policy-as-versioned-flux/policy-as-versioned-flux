# 04 — How is incomplete coverage stated rather than implied?

Type: grilling
Status: open
Blocked by: 03

## Question

No corpus is exhaustive, so every computed bump is really "major/minor/patch **as far as we looked**".
A gate that reports a clean bump without saying how hard it looked is this estate's signature bug —
it has three confirmed instances of assertions that pass by not looking, and it argues publicly that
governance tools lie by showing green ticks.

**Decide:**

1. **What the gate publishes alongside the bump.** Corpus size and version? Which policy expressions
   were exercised and which were never reached by any workload? A coverage figure over the CEL
   expressions the policy body contains?
2. **What an unreached rule means.** If a new `Deny` rule matches nothing in the corpus, the observed
   evidence says "minor" while the rule is plainly capable of being major. Does the gate refuse to
   compute, compute-with-a-warning, or escalate to major on the precautionary principle?
3. **Whether low coverage can block a release.** A threshold is a policy decision with teeth: too
   strict and nobody can ship, too loose and the number is theatre.
4. **Where it surfaces.** The release notes, the Renovate PR body, the gate output — or all three.
   ADR-0002 makes the reviewed PR the non-negotiable moment, so that is the audience that matters.

The estate's honesty story is the reason this map exists; a computed bump that hides its own
uncertainty would be worse than the editorial judgement it replaces.
