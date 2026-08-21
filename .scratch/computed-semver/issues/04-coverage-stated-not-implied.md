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

## Comments

Unblocked 2026-08-21 by [ticket 03](03-what-is-the-corpus.md), which hands this ticket three things.

**A coverage vocabulary.** A **shape** is the tuple of outcomes each subject CEL expression gives on
a pod, plus whether its pin is inside the version array. Coverage is therefore workloads over
expressions, and it is well-defined because ticket 03 narrowed "corpus" to the workload population
only — the policy bodies are the *subject*, and a corpus cannot cover itself.

**Numbers the gate already has.** Ticket 03 refused a corpus size ceiling on the grounds that silent
truncation is the bug this map exists to kill, and settled that the gate publishes the entry count and
the wall-clock instead. It also generates from **both** subjects and unions them, so there are three
counts to publish (old, new, union) — a large union means the policy surface moved a lot, which is
itself a signal to a reviewer.

**Four stated limits, already named and needing a home in the output.**

1. The tier axis is synthetic. Two FAIR scenarios exist in the estate, both driftwood's.
2. Deny is unobservable at admission — `cage-tier` never denies — so the bottom rung is proved by a
   function test on `select_tier`, not by corpus observation. The output must say which.
3. A claim-less composite reports "no cage spec", deliberately, to keep ticket 08's spun-out question
   open rather than closing it by omission.
4. The gate can fail for a reason unrelated to the release: movement tracing to one of the five live
   Kyverno policies that carry no version at all.

Question 2 of this ticket — what an unreached rule means — is now sharper, not answered. Ticket 03's
generator enumerates satisfied/violated/absent *per expression*, so "no workload reached this rule"
should be impossible for any expression the generator can see. That makes an unreached rule a
**generator** defect rather than a corpus gap, which is a different escalation from the one this
ticket's bullet assumes.
