# 04 — How is incomplete coverage stated rather than implied?

Type: grilling
Status: resolved
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

## Answer

Resolved by grilling, 2026-08-22, over three rounds. Two environment facts drove it, and one of them
corrects a decision taken in ticket 03.

**The shape in one line: the gate publishes no coverage percentage at all. It publishes counts, and a
list of what it did not look at, and every entry on that list carries a stable id so a reviewer can
see which holes are new.**

### The two facts

1. **The full combination space is over four million; the built set is tens.** The eight live policies
   hold roughly twelve judged expressions. Three outcomes each, two pin states and four tier values
   give a space in the millions. Ticket 03 combines the axes pairwise, so the built set is tens of
   entries. Any whole-space ratio is therefore near zero. It reads as catastrophe and it means
   nothing.
2. **A judged validation expression cannot be given a name.** Kyverno's `validations[]` entries carry
   `expression` and `message` only, following the ValidatingAdmissionPolicy schema. Only
   `matchConditions` and `variables` carry names. This decides what a stable id can be derived from.

### 1. What the gate publishes

- **No percentage.** A percentage invites a threshold, and a threshold invites tuning the corpus until
  it passes. That is the failure this map exists to kill. The output is raw counts plus an explicit
  **not-looked-at list**.
- **Coverage is defined over predicate expressions only**, which means `matchConditions` and
  `validations`. This **corrects ticket 03's wording**. Its "per CEL expression: satisfied, violated,
  absent" model only fits predicates. Several live expressions are variables that return strings or
  objects, so "satisfied" is meaningless for them. `cage-tier`'s `rawTier` returns a tier string, its
  `dial` returns a map, and its mutation expression rebuilds the container list.
- **A variable is covered when an enumerated axis spans its value space.** `rawTier` is covered,
  because ticket 03's tier axis exists for exactly that reason. `dial` and the container rewrite have
  no axis, so they are named in the not-looked-at list. No new axis is added.
- **Two measurements, two jobs.** **Cells** are each predicate expression against satisfied, violated
  and absent. The generator makes cells complete by construction, so a gap is a defect, not a
  statistic. **Pairs** are the axis combinations actually built.
- **The pairwise gap is stated in one sentence and two counts**, never as a whole-space ratio. The
  sentence is "axes were combined pairwise, so no three-way interaction was built". The counts are
  pairs built and pairs possible. That ratio sits near one hundred percent and is honest at the level
  the generator works at.

### 2. What an unreached expression means

- **It fails the build and the gate names the expression.** Under ticket 03's generator an unreached
  predicate is a generator defect, not a corpus gap. The precautionary escalation to major that this
  ticket's bullet assumed is the wrong instrument.
- **Genuinely unreachable expressions get a declared exclusion, in two tiers.** If the gate can prove
  nothing reaches the expression, the entry is a **proved exclusion**. If it cannot prove that, the
  entry is a **declared hole** and it prints in the not-looked-at list every release, for ever. A
  human may declare a hole. A human may not promote one to proved. That keeps the exclusion file from
  becoming the escape hatch that brings curation back.
- Consequence, accepted: if CEL unreachability turns out to be impractical to prove, every exclusion
  is a declared hole. The design degrades safely, because the honest outcome is the noisy one.

### 3. What can fail the build

**No coverage threshold, ever.** Three binary gates instead:

1. An unreached predicate expression fails.
2. A witness shape missing from the generated spine fails. Ticket 03 already settled this.
3. Movement traced to an unversioned policy fails. Ticket 03 already settled this too.

The pairwise gap never blocks a release. It is stated.

### 4. Where it surfaces

**One source, three views.** CI writes one signed evidence JSON, using the `feeds/sign.sh` shape
ticket 03 settled. CI renders it to markdown in the Renovate PR body. The release notes link the
signed file. ADR-0002 makes the reviewed PR the non-negotiable moment, so **the PR body is the view
that gets the design effort**.

The evidence carries **nine fields, none optional**:

1. The declared bump and the computed bump. Ticket 05 decides where the declared bump is read from.
2. Per-policy verdict movement.
3. Three entry counts: old subject, new subject, union.
4. Generator version.
5. Corpus checksum.
6. Wall-clock.
7. The not-looked-at list.
8. The derived limits with their counts.
9. The per-institution matrix from ticket 03.

**The gate always emits the evidence and always signs it, including when it refuses.** The outcome
field carries `refused` and names the reason, and every other field is populated as far as the run
got. A gate that emits nothing on failure trains people not to run it, and a refusal is the most
valuable thing this gate produces.

### 5. A hole has a stable identity

A reviewer does not need to know whether holes exist. They need to know whether **this** hole is new.

- Each not-looked-at entry carries a **stable id, derived from a hash of the normalised expression
  text**, scoped by the identity family and by the policy name with its version stripped. Both scopes
  come from ticket 06.
- The two alternatives are unusable. `message` embeds the version literal, for example "pods on
  policy-version 2.0.0 must set runAsNonRoot". A list index invents holes on a reorder.
- Normalising removes the version literal, which ticket 06 already requires the gate to treat as
  unproven. The unchanged rule in `require-nonroot` therefore keeps its id from 1.0.0 to 2.0.0, and
  the changed rule gets a new one.
- The PR body shows each hole as carried over, new, or closed since the last release. **A new hole in
  a release that claims patch is a strong signal to the reviewer.**

### 6. The four stated limits are derived, not written

A hand-written prose list of limits rots, because it survives the condition that created it.

- **Each limit is emitted by the check that would remove it, with its current count.** Example: "tier
  axis synthetic: 0 of 47 corpus pods map to a priced scenario". When the count changes, the sentence
  changes itself.
- **A limit never vanishes.** When its count reaches zero it prints as **closed**, with the count that
  closed it. This is stateless and it is diffable. A limit leaves the output only when someone deletes
  the check, which is a reviewed change.
- The four limits ticket 03 named all get this treatment: the synthetic tier axis, deny being
  unobservable at admission, the claim-less composite reporting "no cage spec", and the gate being
  able to fail for a reason unrelated to the release.

### What this ticket did not decide

- **Where the gate runs, and who verifies the signature.** Ticket 05 owns both.
- **Where the declared bump is read from.** Tag, `versions.yaml`, or PR title. Ticket 05 owns it.
- **`CONTEXT.md` was not edited.** *Hole*, *proved exclusion* and *predicate expression* are terms of
  one gate that does not exist yet. `CONTEXT.md` is the thesis glossary and stays free of them.
