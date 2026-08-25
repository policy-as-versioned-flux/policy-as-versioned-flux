# Map — policy inherits across parties

Label: `wayfinder:map`. Charted 2026-08-21, split out of
[`computed-semver`](../computed-semver/map.md) after its ticket 09 grew a compliance architecture
that had nothing to do with computing a bump.

## Destination

**A party's effective policy set is composed from other parties' signed, versioned artefacts, and the
composition is refused when it does not hold together.** Policy as a dependency you *extend and mash
up*, not only pin. A regulator publishes **controls**; a publisher ships **implementations**; an
adopter inherits both and adds its own. Pricing and threat parents contribute no rules but move the £.

## Notes

**Why this is its own map.** `computed-semver`'s standing preference warns against letting a refactor
take the release gate hostage. Composition earns exactly one line on that map — *the bump is a
property of a composition, so compute it after composition* — and that line stays there. Everything
else (baselines, OSCAL coverage, caging economics, feed parents, signing a composed artefact) is a
different destination and belongs here.

**Domain.** Read `CONTEXT.md`'s *Party*, *Role*, *Policy*, *Exemption* and *Orphan guard* entries,
`docs/adr/0006` and `docs/adr/0010` (nothing timed applies a verdict; scheduled **proposals** only),
and `docs/adr/0007` (the agent layer prompts editorial review, never edits enforcement). The estate's
own `platform/graded/cage.py`, `platform/risk/appetite.json`, `platform/feeds/` and
`ico/schema/to_fair_scenario.py` are the £ machinery and are not to be re-implemented.

**Standing preferences.**
- **Never an exemption.** A subclass that cannot meet an inherited rule is caged, priced against its
  own appetite band. Deny is the bottom rung, reached by the £. There is no override branch.
- **A feed may re-price. It may never apply.** Every resulting change lands as a reviewed PR.
- **Reuse the estate's engines.** No second risk engine, no second appetite store.
- Honesty over green. Say which findings a plain lint would also have found.

## Decisions so far

- [Does composition hold up?](issues/01-does-composition-hold-up.md) — **yes, and it is a real missing
  layer.** Prototype `spikes/cs-06b-cross-party-composition/` composes the estate as it really is and
  renders back down to the committed per-version files, proven by stripping the composition's own
  additions and comparing. **Caging settles a child that cannot meet a parent, and only that**: two
  parents whose rules disagree is now *refused*, not merged, and is untested across parties because
  the estate has one implementations publisher. The pricing and threat parents are wired and the price
  moves; **no real feed bump changes a decision**. Four gaps found, but only one of them needed
  composition to find.
- [What gets signed?](issues/02-what-gets-signed.md) — **the adopter self-signs, no new mechanism.**
  A composed set is a real, published, signed artefact: the adopter gitsign-signs it exactly as it
  signs any artefact today. A parent's "digest" is its resolved commit SHA, the one Renovate already
  pins, recorded once at the top of the file. Verification stays CI/merge-time only, same floor as
  today. Recorded as [ADR-0012](../../docs/adr/0012-composed-artefact-self-signed-pinned-sha.md) and
  a new **Composed artefact** term in `CONTEXT.md`.
- [Who declares the baseline, and against which catalogue ids](issues/03-baseline-and-catalogue-ids.md)
  — **the regulator publishes named baselines, the adopter selects one, and both key on the bare
  catalogue id.** Baselines are OSCAL profiles, the shape NIST already ships. The split keeps a
  regulator's addition a downstream break, which an adopter-enumerated list would hide, and it keeps
  coverage from going tautological, which a publisher-declared baseline would cause. The estate
  selects **MODERATE**: LOW excludes `ac-6`, one of the two controls it implements. That is **285
  holes on day one**, so a composition refuses on a **new** hole only, against the last signed
  composed artefact, and records the rest. `ac-6.10` is **already in real MODERATE**, so ticket `01`'s
  hypothetical `nist` `v2.0.0` is superseded and the hole is live. The id is `ac-6`, never `AC-6` and
  never `nist-800-53:AC-6`; the resolver never case-folds and never strips. Recorded as
  [ADR-0013](../../docs/adr/0013-regulator-publishes-baselines-adopter-selects.md) and new
  **Baseline** and **Control id** terms in `CONTEXT.md`.
- [Whether an unlabelled pod is denied](issues/04-unlabelled-pod-denial.md) — **the committed guard is
  right, and `CONTEXT.md` was wrong about the guard but right that a hole exists.** Absence of the
  claim label covers three situations the guard cannot tell apart, so **absence is never the deny
  trigger**: the guard judges a claim, and only a claim. Two independent facts forbid the prose. The
  guard is cluster-scoped over every `Pod`, so deny-on-absence bricks the cluster. And `currency.py`'s
  de-posture patch, its "ONLY durable re-patch", is an `UPDATE` that names "orphan-guard is out of
  scope" as the reason it works. A de-postured pod is **caged, keeps running, and is priced** — the
  standing preference in miniature. The **locked-door claim was false, not narrow**: omit the label and
  no gate matches you. A sibling `ValidatingPolicy` closes that, scoped by
  `policy-as-versioned.dev/governed: "true"` and matching **`CREATE` only**, so de-posture stays legal.
  **A plain read of the two files finds this. Composition was not needed.** Recorded as
  [ADR-0014](../../docs/adr/0014-unclaimed-is-caged-governed-namespace-requires-claim.md), an amended
  **Orphan guard** entry, and new **Governed namespace** and **De-postured** terms in `CONTEXT.md`.

- [The proposer](issues/05-the-proposer.md) — **a proposer already exists, the adopter runs it, and
  it now opens the PR.** `platform/wargamer/` is already the bounded proposer, and
  `propose-policy-pr.sh` already stops one step short on purpose. The missing pieces were the last
  step and the target line. A cage-tier drift becomes a third drift row on the war-gamer. The
  **adopter** runs it in its own repo, on its own `GITHUB_TOKEN`, calling the war-gamer through its
  pinned `platform` dependency, because a cross-org credential is the one ADR-0007 records the estate
  never built. The PR edits `posture.acme.io/tier` on a workload manifest, which is the label the
  engine reads. A merged Renovate pin bump starts a run, and **no clock ever does**. A **sixth gap**:
  `select_tier` returns `deny`, the label cannot carry it, and the policy coerces it to `baseline`,
  so a merged Deny would invert the proposal in silence. Recorded as
  [ADR-0015](../../docs/adr/0015-adopter-runs-the-proposer-and-it-opens-the-pr.md) and a new
  **Proposer** term in `CONTEXT.md`. **A plain read of three files finds all of it.**

- [Composing the five unversioned live policies](issues/06-composing-the-remaining-policies.md) —
  **it holds up, every kind renders back down faithfully, and four of the five are no longer
  unversioned.** `cs-12`'s renderer now emits `cage-tier`, `cage-netpol`, `stamp-posture` and
  `posture-trust-boundary` into every version tree. The fifth, the orphan guard, **cannot** be
  versioned: it is the aggregate over the array, so composition carries a second numbering axis under
  the `platform-machinery` identity `cs-22` gave it. Three findings. **An action is a
  `ValidatingPolicy` concept**, so the `Audit < Deny` ladder is meaningless for three of the six
  members and **a subclass cannot tighten a mutate** — the tier is the only knob and ADR-0015's
  proposer is the only thing that turns it. **The identity label is a family, not a key**, so the old
  resolver overwrote in silence and had not fired only by luck. **Mutation ordering is inherited, not
  declared**, and is ruled `platform` machinery. Two estate facts: `cs-16` deleted `policy/policies/`,
  so gap 2 **renames rather than shrinks**, and the same-version-two-trees question is **closed**.
  **The spike would not run at all before this ticket** — it had rotted against the estate it reads.
  Recorded as [ADR-0016](../../docs/adr/0016-a-subclass-never-restates-a-mutate.md).

## Not yet specified

Nothing. The original five fog items all graduated to tickets
[`02`](issues/02-what-gets-signed.md), [`03`](issues/03-baseline-and-catalogue-ids.md),
[`04`](issues/04-unlabelled-pod-denial.md), [`05`](issues/05-the-proposer.md) and
[`06`](issues/06-composing-the-remaining-policies.md). Ticket `03` surfaced
[`07`](issues/07-adopter-added-controls.md), specifiable at once. The governed-namespace patch
graduated to [`08`](issues/08-composed-artefact-declares-governed-namespaces.md) after ticket `06`
settled the doubt that held it back: the composed set **mixes scopes**, so the namespace set is
composition business rather than `platform` machinery.

## Out of scope

- **Computing the version bump.** That is [`computed-semver`](../computed-semver/map.md). This map
  owes it one fact and no more.
- **Repairing the named gaps.** Four from ticket [`01`](issues/01-does-composition-hold-up.md), a
  fifth from ticket [`04`](issues/04-unlabelled-pod-denial.md), and a sixth from ticket
  [`05`](issues/05-the-proposer.md). The fifth is the governed-namespace claim requirement, which
  nothing builds today. The sixth is the `cage-tier` policy coercing an unknown tier label to
  `baseline`, so a merged `deny` label produces the loosest cage instead of the tightest. They are
  defects in the `platform` repo, found from the hub. Naming them, and specifying the fifth, is this
  map's job. Fixing them is that repo's. Ticket [`06`](issues/06-composing-the-remaining-policies.md)
  **renamed the second**: `cs-16` deleted `policy/policies/`, so `ac-6` now claims a policy that
  exists nowhere. The gap did not shrink.
- **Declaring the order the composed members run in.** Ticket
  [`06`](issues/06-composing-the-remaining-policies.md) found that two of the six members mutate:
  `stamp-posture` writes the label `posture-trust-boundary` validates, and `cage-tier` writes the
  label `cage-netpol` generates from. A flat per-version render states neither dependency. Kyverno
  runs the mutating webhook before the validating webhook, which is what makes it work.
  **That is `platform` machinery.** A second implementations publisher is what would expose it, and
  the estate has one. Ruled out of scope, recorded in
  [ADR-0016](../../docs/adr/0016-a-subclass-never-restates-a-mutate.md).
