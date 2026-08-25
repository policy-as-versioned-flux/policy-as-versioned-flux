# 14 — Baseline coverage, control claims and holes

Type: task
Status: resolved
Blocked by: 09, 10, 12

Source: [`spec.md`](../spec.md), *Baselines, control ids and holes*. Decisions:
[ADR-0013](../../../docs/adr/0013-regulator-publishes-baselines-adopter-selects.md),
[ADR-0017](../../../docs/adr/0017-a-control-claim-belongs-to-whoever-ships-the-implementation.md).

## What to build

A regulator's addition reaches the adopter as a refused pull request.

The composition resolves the selected baseline name against the `controls` parent's profiles, walks
nested controls, and fails hard on an unknown id. Control claims merge over every party that ships a
member, including the adopter's own component-definition. A baseline control with no claim is a hole.

Holes compare against the hole list in the last signed composed artefact. A new hole refuses. A
recorded hole records. A filled hole prints as closed. The first composition records every hole and
refuses on none. The estate starts at 285 and the document says so.

Four more refusals. A control removed from the selected set, compared against the last signed
artefact. A baseline widening, such as MODERATE to HIGH. A claim against a policy another party ships.
A claim whose policy exists in no composed member, marked `needs_composition: false`.

The header gains the recorded hole ids. The document gains `holes[]`.

## Acceptance criteria

- [ ] The baseline resolves by name, exact-string, walking nested controls. `ac-6.10` is found.
- [ ] A prefixed or upper-case id is a hard failure, not a hole.
- [ ] Claims merge over every party that ships a member, including the adopter's own component-definition.
- [ ] The first composition of the real estate records 285 holes and refuses on none.
- [ ] A second composition with one new hole refuses and names the id.
- [ ] A second composition with a hole filled marks it closed.
- [ ] An adopter-added control refuses as a new hole, and an adopter claim in its own component-definition fills it.
- [ ] A removed control refuses. A widened baseline refuses.
- [ ] An adopter claim against a parent's policy refuses.
- [ ] A claim whose policy exists nowhere refuses with `needs_composition: false`, and names the two dangling `platform` claims today.
- [ ] The header carries the recorded hole ids, and stripping it leaves the files unchanged.

## Answer

Built in place, inside `platform/compose/composition.py`'s existing `compose()` -- same seam, same
two return values, per spec.md's "One seam". No new module.

**Baseline resolution.** `_catalog_ids(nist_root)`/`_baseline_ids(nist_root, name)` read the
`controls` parent's `catalog/CATALOG_VERSION.json` and `catalog/BASELINE_VERSIONS.json` directly
(ticket 09's real shape), walking nested controls so `ac-6.10` is found. Resolution is
exact-string throughout: `_unknown_id_refusals()` is the one place that decides "absent from the
catalogue", reused for both an adopter's `overlay.controls` addition and a claimed `control-id` --
a hard failure (`unknown-control-id`), never a hole, `needs_composition: false` (a plain lint of
the id against the catalogue would also catch it).

**Control claims.** `_load_claims()` reads an OSCAL component-definition's `Check_Id` props --
duplicated from `oscal/lint_claims.py`'s own reader on purpose (each party's reader stays
self-contained). Claims are gathered from every `implementations` parent's
`oscal/component-definition.json` *and*, new this ticket, the adopter's own
`component-definition.json` next to `party.yaml` (ADR-0017: "next to the party artefact it
signs"). `resolve_claims()` resolves each claim two ways: the claimed policy must be shipped by
*some* composed party (else `dangling-claim`, `needs_composition: false` -- proved against the
real `platform` component-definition's two known-dangling claims,
`ac-6`->`may-run-root-if-attested` and `cm-6`->`require-policy-version`), and it must be shipped
by the *same* party that claims it (else `claim-against-another-partys-policy`,
`needs_composition: true` -- ADR-0017). A control counts as **covered** the moment *any* claim
exists for it, valid or not -- "no claim", not "no valid claim" (spec.md) -- so a dangling or
cross-party claim still closes a hole while separately refusing on its own account.

**Filling an adopter-added control required one real gap closed first: `overlay.add` was declared
in ADR-0017/ticket 11's schema but never wired into `compose()` at all.** `load_overlay_add()`
loads each entry (`{version, manifest: <a full admission-kind document>}`) into the same merged
member set as a parent's members, keyed identically, `source_party` the adopter. This is the only
route by which "an adopter claim... fills it" (ADR-0017) can ever be true, since an adopter may
never claim against a parent's policy.

**Holes.** `compute_holes(selected_set, covered, prev_hole_ids)` -- `prev_hole_ids` is `None` only
on the literal first composition (`_previous_header()` finds no committed
`composed/HEADER.yaml`), and only then does every hole record with no refusal. Proved against the
real estate: driftwood's first composition records exactly **285** holes (MODERATE's 287 minus
`ac-6`/`cm-6`, both claimed -- one validly, one danglingly, both count as coverage), all
`recorded`, `ac-6.10` among them. A fixture estate (`_write_fixture_catalog`/`_write_fixture_platform`/
`_write_fixture_adopter`) proves the rest across repeated runs chained by `_commit_header()`: a
new hole refuses and names it; the same hole, filled by an adopter's own claim against its own
`overlay.add` member, is never a hole at all; a hole filled across two runs closes.

**Removed control / widened baseline.** `check_selected_set()` refuses any id present in the
*previous* signed artefact's `selected-controls` (a new header field) and absent now -- no
exceptions, matching a narrowed baseline (HIGH->MODERATE) for free, since the dropped controls
just show up as removed. `check_baseline_widening()` fires only when the named baseline changed
*and* the new resolved set is a strict superset of the old (MODERATE->HIGH) -- narrowing is left
to `check_selected_set` so the two never double-fire on one change.

**The header** gains `holes` (the currently-open, i.e. not-closed, recorded hole ids) and
`selected-controls` (the full resolved set) -- the durable comparison point every later run reads
via `_previous_header()`, per spec.md's "the header holds... the recorded hole ids". Stripping it
is a no-op on every other rendered file, proved by grep: neither key's text appears anywhere else
in what's rendered.

**One real, pre-existing bug found and fixed in passing** (root cause, not symptom, since it's
shared): `_resolve_unpinned_sha`'s content-digest fallback (ticket 12) picked up the `__pycache__`
bytecode file that `load_implementations()`'s dynamic import of `render-orphan-guard.py` writes to
disk as a side effect, making an unpinned parent's SHA non-deterministic across two `compose()`
calls in one process. Ticket 14's `verify()` round-trip is the first caller to compose the same
non-git fixture tree twice, so it's the first to surface this. Fixed by excluding `__pycache__`
from the digest walk.

`--selfcheck` (`./verify-composition.sh`) covers every acceptance criterion above, against real
files on disk plus a small synthetic catalogue/baseline/claims fixture for the paths the real
estate cannot yet exercise (a new hole, a closed hole, a removed control, a widened baseline, a
cross-party claim). **Ticket 12/13's own prior assertions that the real driftwood/tuppence/ludlow
compose cleanly no longer hold, correctly**: composition now genuinely catches platform's two
already-known-but-previously-invisible dangling claims (ticket 10 named them; fixing them stays
that repo's job) and refuses the real estate's pull request on them today -- exactly spec.md's
opening problem statement. Those assertions are updated to expect exactly those two refusals and
nothing else (`_assert_only_known_dangling`), and the verify()/CLI-writes-files checks moved to
the clean fixture, since the real estate cannot reach `outcome: composed` until that separate
defect is fixed.
