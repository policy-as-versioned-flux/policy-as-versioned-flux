# 13 — Structural refusals, restatement, and caging a declared inability

Type: task
Status: resolved
Blocked by: 12

Source: [`spec.md`](../spec.md), *Resolution*, *Restatement and caging*. Decisions:
[ADR-0016](../../../docs/adr/0016-a-subclass-never-restates-a-mutate.md), ticket
[`01`](01-does-composition-hold-up.md).

## What to build

A composition that does not hold together is refused, and a subclass that cannot meet a parent is
caged.

Three structural refusals. A split diamond, where two edges reach one parent at two versions. Two
sources supplying one rule with different content, named with both sources and both contents. A
restatement of a mutate or a generate.

Restatement on a `ValidatingPolicy`. A stricter action is accepted and appears in the rendered file.
A weaker action is a declared inability. The composition calls the estate's own cage engine with that
party's own appetite band. The rendered action stays the inherited one. The cage tier, residual and
band print per party. The composed artefact carries no tier and no tier floor.

The document gains `refusals[]` with `needs_composition`, `restatements[]` and `cages[]`. The
two-publisher conflict path is a limit, emitted with the count of pinned implementations publishers.

## Acceptance criteria

- [ ] A split diamond refuses and names both edges.
- [ ] Two sources for one rule with different content refuse and name both sources and both contents.
- [ ] A restatement of a mutate or a generate refuses.
- [ ] A stricter restatement is accepted and the rendered file carries the stricter action.
- [ ] A weaker restatement is caged, and the rendered file carries the inherited action.
- [ ] The same weaker restatement prices three parties to the tiers the prototype's table shows, from the estate's own cage engine and appetite bands.
- [ ] No tier and no tier floor appears anywhere in the rendered artefact.
- [ ] `refusals[]` carries `needs_composition` on every entry.
- [ ] The two-publisher limit prints open at one publisher and closed at two. A fixture with two publishers proves the closed case.

## Answer

Built in place, inside `platform/compose/composition.py`'s existing `compose()` — same seam, same two
return values, per spec.md's "One seam". No new module.

**Split diamond.** `check_diamonds(edges)` groups the adopter's own `inherits` edges by `(party, kind)`
and refuses when one pair carries more than one declared version, naming every edge. The real estate
has no second data source recording a further-hop parent's own pin (`platform` ships no `party.yaml`),
so the diamond this estate can manifest today is two direct edges — which is also the literal reading
of "every path ... must resolve to one version" — and a transitive walk into a hypothetical
`platform/party.yaml` was not built for a case nothing here can produce (YAGNI). Proved with a fixture:
driftwood's own `ico/pricing` edge duplicated at `v1`/`v2` (chosen over `nist/controls` specifically
because `ico/pricing` carries no Flux pin, so a second declared version can't also trip the unrelated
tag-mismatch refusal `party_artefact.check_tags` already owns).

**Cross-party rule conflict.** The `implementations`-loading loop (ticket 12) now merges every parent's
members into one dict keyed on `(version, family, name)` instead of rendering per-edge; a second source
supplying the same key with different content is refused — both sources and both full contents named
in `detail` — and the key is dropped from the composed set entirely (never merged, never last-wins).
Proved with a two-publisher fixture (`impl-a`/`impl-b`, same family+name+version, one `Audit` one
`Deny`). The **two-publisher limit** is emitted every run from `len(implementations_parties)`: `open`
at driftwood's real one, `closed` at the fixture's two.

**Restatement.** `apply_restatements()` matches each `overlay.restate` entry (`name`, `version`,
`action`, optional `scenario`/`workload`/`why` — same shape the prototype's `restate`/`cannot_satisfy`
proposed, collapsed into one list per this ticket's framing: a weaker restatement *is* the declared
inability, not a second parallel list) against the merged member set. A match on a `MutatingPolicy` or
`GeneratingPolicy` refuses (`restatement-of-non-validating`, ADR-0016) — proved against the real
`cage-tier`. On a `ValidatingPolicy`, `Audit<Deny` decides: stricter is accepted and overwrites the
rendered action (proved: driftwood's `require-nonroot@2.0.0` Audit→Deny, rendered file carries `Deny`);
weaker leaves the rendered member untouched (still the inherited action) and is priced instead.

**Caging.** A weaker restatement calls `graded/cage.py`'s real `select()` against the party's own
`risk/appetite.json` band, `mode="warn"`, priced from the restate entry's own `scenario` path (resolved
against `platform/`, the prototype's own convention) or, failing that, the pinned threat feed. No band,
or no scenario and no threat parent, is its own named refusal rather than a guess. Proved against the
real `posture-trust-boundary@2.0.0` (`Deny`) restated `Audit`, priced from the real
`policy/scenarios/driftwood-root-residual.json`, across all three real adopters — reproducing the
prototype's own table exactly: driftwood→`baseline`, tuppence→`baseline`, ludlow→`quarantine`. The
rendered file keeps `Deny` in every case. `cages[]` carries `changed`, compared against the last
committed `composed/evidence.json` if one exists (same new/recorded shape tickets 14/15 use, one field
simplified to a boolean since a cage has no status ladder) — untested against a real second run, since
nothing in the estate has a committed composed artefact yet (ticket 18's job).

**No tier, no tier floor.** Verified as: composition's own added keys (`composed-for`,
`inherited-from`, `source-path`, the header) never carry a tier field or value. (A broader
"the string 'tier' never appears" check was tried and rightly failed: `cage-tier.yaml`'s own inherited
CEL body legitimately reads `posture.acme.io/tier` off the workload at admission — that is the runtime
dial-selection mechanism composition carries unchanged, not a declared verdict, and the exact-key check
is what tells the two apart.)

`--selfcheck` (`./verify-composition.sh`) covers every acceptance criterion above against real files on
disk, SKIPping with exit 0 when `.estate-clone` is absent, per spec.md's Testing Decisions.
