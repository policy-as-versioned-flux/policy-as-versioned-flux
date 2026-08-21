# Map — the version number computes itself

Label: `wayfinder:map`. Charted 2026-08-20.

## Destination

**A policy release states its bump and is refused if the evidence disagrees.** The release gate
evaluates the candidate version and its predecessor against a corpus, observes how verdicts move on
currently-compliant workloads, derives **major / minor / patch** from `CONTEXT.md`'s existing
definition, and fails the release when the declared bump contradicts what was measured.

The same rule binds the **platform's own version**, not just the policy body — a platform bump
changes the version array, which changes which policies run, which changes verdicts. The distribution
layer does not get to exempt itself from the rule it distributes.

## Notes

**Why this is worth doing.** `CONTEXT.md` already defines semver by **verdict impact on
currently-compliant workloads** rather than author intent — the hard half, and it is done. But the
bump is still an editorial judgement: faithful-floor's *Cut 2.0.0 + 2.1.1 releases exercising semver
meaning* asserted each bump and then authored a fixture proving it. The proof is post-hoc
justification, not derivation. That same ticket records version-mechanics gaps found "by review, not
by CI", twice. This map inverts the flow.

**Domain.** Read `CONTEXT.md`'s *Policy version* entry (the rule), `docs/adr/0002` (pinned + reviewed
Renovate PR — the review gate is non-negotiable and this must not weaken it), and
`estate/platform/shift-left/` (the offline evaluation primitive already exists:
`verify-shift-left.sh` runs one workload against two versions via `kyverno apply`).

**Standing preferences.**
- **Inheritance is not the destination.** Policies-that-`extends`-policies is a real DRY win and a
  separate idea. It enters this map only if the rule-set delta proves unreadable without it — see the
  ticket that tests exactly that. Do not let a refactor of every policy file hostage the release gate.
- **Build in the new `estate/`; mine the old faithful-floor estate for test material.** Its
  1.0.0 / 2.0.0 / 2.0.1 / 2.1.1 line is signed, live-proved, and is the validation set.
- **The engine must reproduce a human's correct answer before it is trusted to give its own.**
- Honesty over green — a gate that passes because the corpus missed the case is this estate's
  favourite bug, and it has three already. Coverage must be stated, not implied.
- Skills each session should consult: `/grilling`, `/domain-modeling`.

## Decisions so far

<!-- index of closed tickets; one line each, linking the ticket that holds the detail -->

- [What counts as a "verdict", given Audit is not a pass](issues/02-what-counts-as-a-verdict.md) —
  compliant means *admitted*; refusal is not a class but the **bottom rung** of the cage ladder; and
  **every workload is always caged — the cage *spec* is what changes**, so the engine compares specs,
  not verdict enums. The bump is institution-relative (the rung is picked against the consuming org's
  band), so **tag the strictest band and publish the per-institution matrix as evidence**. Two things
  fell out: the code contradicts always-caged, and COTS/unversioned workloads are a permanent
  population needing their own effort.
- [What represents "currently-compliant workloads"](issues/03-what-is-the-corpus.md) — the corpus is a
  **generated** population of plain pods owned by `platform`, enumerated **per CEL expression**
  (satisfied/violated/absent) across two more axes: the **version pin** (in/out of the version array)
  and the **tier label** (absent/baseline/restricted/quarantine). A second **witness** set of real
  workloads proves the generator, and **a witness shape the generator missed fails the build** — the
  repair is always the generator, never the fixture. That is what stops curation toward a wanted bump.
  Generated from **both** subjects and unioned, so a retirement is visible. The corpus is not signed:
  it is regenerated and diffed in CI, and the **evidence output** is what gets signed. Three findings
  fell out: `cage-tier` is label-driven so **no residual is ever invented**; the subject is **every**
  Kyverno policy that reaches a pod, so **five of the eight live policies carry no version and the
  gate must fail when movement traces to one**; and deny is unobservable at admission, so the bottom
  rung is proved by function test and said so.

- [Does inheritance earn its place](issues/06-does-inheritance-earn-its-place.md) — **answers a
  narrower question than the map meant; see the
  [`policy-composition` map](../policy-composition/map.md).** For
  a policy version extending *its own predecessor*: **no, a rendered diff is enough.** Not because
  the diff is clean, but because **the
  gate never classifies from the delta**: major/patch come from verdict movement, minor from presence
  plus `validationActions`, and cs-03's generator wants the *list* of CEL expressions, not a
  comparison. The delta is only evidence prose for the reviewer. Four findings the gate must carry:
  parse the YAML (19 of the 30 changed lines in the named pair are comments); **the identity label is
  a family name, not a unique key** — `graded-enforcement` and `posture` each group different
  unversioned policies, so pair on `(identity, name-with-version-stripped)` and **fail** on an
  unversioned member; compare rules as a set; and treat a version-literal difference as unproven.
  Prototype: `spikes/cs-06-inheritance-vs-diff/`. The claim "inheritance leaves this map" is
  **withdrawn** — that was the narrow reading.
- **The bump is a property of a composition, not of a file** — from the cross-party composition work,
  which is now its own map: [`policy-composition`](../policy-composition/map.md). An adopter's
  effective rule set is inherited from several parties, so **the gate computes the bump after
  composition**. A regulator's *addition* is a downstream build break. A **retired array element is a
  downstream major with no policy diff at all**. cs-01's method is **extended, not unchanged**: its
  verdict-movement half works as-is on composed sets, but a composition also refuses on **coverage**
  with zero verdict movement, a second structural axis just as cs-01's minor finding was a first. The
  publisher still tags **one** bump at the strictest band with the per-institution matrix as evidence,
  exactly as cs-02 settled; composition is the mechanism behind that matrix. Everything else that came
  out of that work — baselines, OSCAL coverage, caging economics, feed parents, signing — is on the
  other map, because this map's own preference says a refactor must not take the gate hostage.

## Not yet specified

- **Where the gate runs after the six-org split.** The other effort is splitting the estate into six
  repos; whether this gate lives in the policy repo's CI, the platform release pipeline, or a
  cross-org check depends on decisions not yet taken over there.
- **Whether the Renovate bump PR should carry the computed evidence.** ADR-0002 makes the reviewed PR
  the non-negotiable gate — a reviewer seeing "this bump is major, here are the three workloads that
  flip" is strictly better than seeing a version number. Shape unclear until the gate exists.
- **Whether `distribution/policies/` and `policy/policies/` are one version line.** Two trees in the
  same repo each declare their own `v1.0.0`, and `versions.yaml` reconciles only the first. The corpus
  ticket makes the gate refuse a same-version-different-content collision, which surfaces the answer
  rather than deciding it.
- **Where a priced residual for a real workload comes from.** The tier axis is synthetic by design
  (ticket 03), and the estate holds two FAIR scenarios in total, both driftwood's. Nothing maps a pod
  to a scenario. Not blocking this map, but the cage half of the model is proved on synthetic input
  until it exists.

*Settled since charting: how the COTS/unversioned shim changes the corpus, and whether the corpus
needs versioning and signing — both in [ticket 03](issues/03-what-is-the-corpus.md).*

## Out of scope

- **Rewriting the old faithful-floor estate.** It is being archived by the other effort. Read-only
  source of validation fixtures here.
- **Policy inheritance, of either kind.** Shipping `extends` across every policy file for DRY reasons
  is its own effort. Cross-party composition is a different thing again and has its own map:
  [`policy-composition`](../policy-composition/map.md). This map takes one fact from it and no more.
