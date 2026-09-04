---
status: accepted
---

> **Superseded in part, 2026-09-03 (ticket 38, built).** The new-hole refusal, the widening refusal and the self-created-hole refusal are gone: a hole is priced and printed as a delta, keyed (source, id) across every controls parent. The bare catalogue id, the exact-string rule and the removal refusal stand. The supersession is recorded by ticket 39's superseding ADR, which takes its number when it is written.

# The regulator publishes named baselines, the adopter selects one, and both key on the bare catalogue id

Nothing in the estate declares **which** controls apply. `nist` ships 1196 at `v1.0.0`
(`CATALOG_VERSION.json`, `controlCount: 1196`) and the estate implements two. Without that
declaration a composition cannot tell an implemented control from an ignored one, so a required
control that nothing claims is undetectable. Separately, the estate carries four spellings of the
same control id: the catalogue's `ac-6`, its own display labels `AC-6` and `AC-06`, and
`nist-800-53:AC-6` in `estate/platform/oscal/component-definition.json`. Nothing resolves one against
the other today, so the mismatch is latent and breaks the first resolver that tries.

**The declaration is split.** The regulator publishes **named** baselines as OSCAL profiles, signed
and versioned like any other artefact it publishes. The adopter **selects one by name**, in the party
artefact it gitsign-signs under [ADR-0012](0012-composed-artefact-self-signed-pinned-sha.md). The
regulator knows the catalogue but not the system, so it cannot pick. The adopter pays the £ when a
control is missing, so selection is the risk-bearing act. The adopter may **add** controls to the
selected baseline and may **never remove** one, because a removal is an exemption by another name.

**The key is the bare catalogue id**, exactly as the catalogue writes it: `ac-6`. The catalogue is
named once, by the `source` or `href` on the enclosing block. Resolution is exact-string, with no
case-folding and no prefix-stripping, and an unknown id is a hard failure.

A baseline control that nothing implements is a **hole**. The composition refuses on a **new** hole
and records a pre-existing one, comparing against the adopter's last signed composed artefact.

## Considered options

**Who declares the baseline**

- **Regulator publishes named, adopter selects (chosen).** Preserves the finding that a regulator's
  addition is a downstream build break: add a control to a named baseline and every adopter that
  selected that name breaks. It is also what NIST really does, so the LOW, MODERATE and HIGH profiles
  exist already and need no new format.
- **The publisher declares it.** Rejected: coverage becomes tautological. The required set would be
  defined as the set already covered, so the one gap that needs composition to find could never be
  found.
- **The adopter enumerates its own control list.** Rejected: a regulator's addition becomes invisible,
  which is the single property the composition exists to give.

**Which baseline this estate selects**

- **MODERATE (chosen).** Holds both `ac-6` and `cm-6`, and `ac-6.10` besides. 287 controls against 2
  implemented, so 285 recorded holes on day one.
- **LOW.** Rejected on the facts: LOW excludes `ac-6`, so selecting it would drop one of the two
  controls the estate actually implements.
- **A bespoke baseline sized to what is implemented.** Rejected: the publisher tautology again, moved
  to the regulator.

**The control id form**

- **Bare catalogue id, catalogue named by the enclosing href (chosen).** One authority for the id,
  one place naming the catalogue. This is what OSCAL does and what the real NIST baseline profiles do.
- **Keep a normalised prefix, `nist-800-53:ac-6`.** Rejected: the prefix names the catalogue a second
  time, and duplicated state is what disagreed in the first place.
- **Case-fold and strip on resolution.** Rejected: forgiving normalisation is how the mismatch stayed
  latent. The cure must not be more of it.

**When a hole refuses**

- **Refuse on a new hole, record a pre-existing one (chosen).** The comparison set is the adopter's
  last signed composed artefact, so no new store, and the hole list is signed evidence.
- **Refuse on any hole.** Rejected: 285 holes on day one would deny the whole estate for ever. That
  is a wall, not a gate.
- **Refuse on a hole-count threshold.** Rejected for the reason `computed-semver` ticket 04 already
  gave against a coverage percentage: a threshold invites tuning the corpus until it passes.

## Consequences

- **Three artefacts must change, in three repos.** `nist` must publish the named baselines it ships
  none of today. `estate/platform/oscal/component-definition.json` must drop the `nist-800-53:` prefix
  and the upper case, and its `source` href must name the parent party rather than read as a local
  path with no version. Each adopter's party artefact must carry the selected baseline name, mirrored
  into `gitops/apps/nist-pin-configmap.yaml` as a `baselineName` key.
- **The estate starts at 285 holes and says so.** The first composition records every hole id and
  refuses on none, because the prior hole set is empty. That first signed artefact is the comparison
  point from then on.
- **`ac-6.10` is a live hole, not a hypothetical one.** It is already in the real MODERATE baseline,
  so it needs no catalogue bump to appear. The `cs-06b` prototype modelled it as a hypothetical `nist`
  `v2.0.0` addition, and that modelling is superseded.
- **An adopter widening its own selection refuses, and gets no override.** MODERATE to HIGH adds 83
  controls at once. The refusal is the intended signal, cleared in a reviewed PR.
- **The resolver must walk nested `controls`.** `ac-6.10` is a child of `ac-6`, so a group-level scan
  misses every enhancement.
- **The prototype's case-folding check is void.** It is asserted against a hand-authored baseline in
  the prefixed form, not against the real catalogue, so it must be rewritten.
