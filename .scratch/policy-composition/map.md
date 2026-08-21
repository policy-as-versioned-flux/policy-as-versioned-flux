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

## Not yet specified

- **What gets signed.** Each party signs its own artefact. A composed set is a new artefact. The
  render must be reproducible from signed parent digests, or a verifier loses the chain.
- **Who declares the baseline, and against which catalogue ids.** The prototype's `nist-800-53:AC-6`
  form matches neither the catalogue's case nor its lack of a prefix.
- **Whether an unlabelled pod is denied.** `CONTEXT.md:129` says the orphan guard denies a *missing*
  label. The committed guard's `matchConditions` skip unlabelled pods entirely, and nothing else
  denies them. One of the two is wrong.
- **The proposer.** Section 9b of the prototype prints a proposed tier. Nothing raises the PR.
- **Composing the five unversioned live policies.** The prototype composes 3 of the 8 that `cs-03`
  found.

## Out of scope

- **Computing the version bump.** That is [`computed-semver`](../computed-semver/map.md). This map
  owes it one fact and no more.
- **Repairing the four gaps.** They are defects in the `platform` repo, found from the hub. Naming
  them is this map's job. Fixing them is that repo's.
