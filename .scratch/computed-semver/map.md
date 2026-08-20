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

## Not yet specified

- **Where the gate runs after the six-org split.** The other effort is splitting the estate into six
  repos; whether this gate lives in the policy repo's CI, the platform release pipeline, or a
  cross-org check depends on decisions not yet taken over there.
- **Whether the Renovate bump PR should carry the computed evidence.** ADR-0002 makes the reviewed PR
  the non-negotiable gate — a reviewer seeing "this bump is major, here are the three workloads that
  flip" is strictly better than seeing a version number. Shape unclear until the gate exists.
- **Whether the corpus itself needs versioning and signing.** It becomes evidence, and every other
  piece of evidence in this estate is signed and tamper-checked.

## Out of scope

- **Rewriting the old faithful-floor estate.** It is being archived by the other effort. Read-only
  source of validation fixtures here.
- **Policy inheritance as a general refactor.** Only the narrow question "does the delta need it?" is
  in scope; shipping `extends` across every policy file is its own effort if it wins.
