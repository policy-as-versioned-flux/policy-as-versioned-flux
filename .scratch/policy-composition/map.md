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

- [What fills a control the adopter adds itself](issues/07-adopter-added-controls.md) — **a signed
  OSCAL control claim from whoever ships the implementation, and an adopter-added hole is an
  ordinary new hole.** The prototype let an adopter add a policy but never claim a control, so an
  added control had no route out. Now any party's claim fills it: an inherited publisher, the
  adopter's own member, or a third pinned publisher. The self-created hole refuses like any new
  hole, ticket `03`'s widening edge at size one, and clears in the same reviewed PR. The claim lives
  in the adopter's own component-definition. Shipping a member adds **no obligation** ADR-0012 did
  not already impose: no separate axis, no separate pin. An adopter may never claim against another
  party's policy and may never remove a control it added. Recorded as
  [ADR-0017](../../docs/adr/0017-a-control-claim-belongs-to-whoever-ships-the-implementation.md)
  and a new **Control claim** term in `CONTEXT.md`.

- [Does a composed artefact declare its governed namespaces](issues/08-composed-artefact-declares-governed-namespaces.md)
  — **no. The `governed: "true"` label on the adopter's own Namespace manifest is the declaration.**
  The manifest already sits in the adopter's signed repo, under the tag ADR-0012 reuses, so a list
  in the composed artefact would be duplicated state, the thing ADR-0013 rejected. The composed
  artefact records the set as advisory metadata only. A composition refuses a **new** ungoverned
  adopter namespace, one with the `institution` label and no `governed` label, and records a
  pre-existing one. The set narrows the `CREATE` claim rule and nothing else. Only the adopter adds
  a namespace, by hand. The proposer never proposes one. Recorded as
  [ADR-0018](../../docs/adr/0018-the-namespace-manifest-is-the-governed-declaration.md) and an
  amended **Governed namespace** entry in `CONTEXT.md`.

- [`nist` publishes named baselines](issues/09-nist-publishes-named-baselines.md) — **built.** LOW,
  MODERATE and HIGH ship beside the catalogue in the `nist` repo as OSCAL profiles (bare ids, one
  `href` each), with a verify beat that resolves every id against the catalogue and a fixture that
  proves an unknown id fails. MODERATE resolves 287 controls and holds `ac-6`, `cm-6` and `ac-6.10`;
  LOW excludes `ac-6`. Verified locally; **not yet released** — the `nist` repo's changes are
  uncommitted there and no gitsign-signed tag has been cut, so the acceptance criterion that
  Renovate can pin the release is still open. No new ADR; implements ADR-0013.
- [`platform`'s control claims use bare ids](issues/10-platform-control-claims-use-bare-ids.md) —
  **built.** `component-definition.json` now writes `ac-6`/`cm-6`, never `nist-800-53:AC-6`, and its
  `source` href names the `nist` party and a catalogue path, not a bare local path with no version.
  A new `lint_claims.py`/`verify-claims.sh` resolves every claim two ways — policy name against the
  shipped version trees, control id against the pinned catalogue — and names the two dangling claims
  (`cm-6`→`require-policy-version`, `ac-6`→`may-run-root-if-attested`) as `EXPECTED-RED` rather than
  silencing them; that gap is a separate `platform` defect, already out of scope above. Verified
  locally; **not yet landed** — same open question as ticket 09, the `platform` repo's changes are
  uncommitted there. No new ADR; implements ADR-0013 and ADR-0017.
- [The party artefact, and the three adopters declare themselves](issues/11-party-artefact-and-adopter-declarations.md)
  — **built.** `platform/party/schema.json` and `party_artefact.py` (new) check a party artefact's
  shape, its declared parent versions against the adopter's own Flux pins, and its baseline against
  the `nist` pin ConfigMap's advisory mirror, naming the two currently-unpinned kinds (`ico/pricing`,
  `platform/threat`) rather than silently skipping them. Each of `driftwood`, `tuppence` and `ludlow`
  gained a `party.yaml` selecting MODERATE, the `governed: "true"` label on its `Namespace`, a
  `baselineName` mirror, and a shift-left step running the check on every pull request. `--selfcheck`
  passes 15 asserts; the real `check` passes end to end against all three adopters' actual files.
  Verified locally; **not yet landed** — same open question as tickets 09 and 10, the `platform` and
  adopter repos' changes are uncommitted there. No new ADR; implements ADR-0012, ADR-0013 and
  ADR-0018.
- [The seam, and a composed artefact that renders back down faithfully](issues/12-the-seam-and-a-faithful-composed-artefact.md)
  — **built.** `platform/compose/composition.py` (new), one entry point: `compose(adopter_dir,
  parent_trees) -> (document, rendered_files)`. Resolves every parent to a commit SHA — the two
  Flux-pinned kinds read `spec.ref.commit` off the adopter's own pin, the two unpinned kinds
  (`pricing`, `threat`) resolve by reading the party directly. Loads every admission member of
  every live policy version keyed on **(identity family, name with its version stripped)** —
  the prototype's real bug was keying on `(family, version)` alone, silently dropping a second
  member of one family (`cage-tier`/`cage-netpol`, both `graded-enforcement`). Renders every
  member back unchanged plus advisory-only additions; `validationActions` now written **only**
  onto a `ValidatingPolicy`, never invented on a mutate or a generate. One separate advisory
  header carries the composed marker, every parent SHA once, the baseline and the governed
  namespace names. `--selfcheck` composes the real `driftwood` against its real pinned parents:
  all 15 live members plus the orphan guard render back byte-identical; a `verify()` mode
  re-renders and diffs byte-for-byte against committed files. No diamond, conflict, restatement,
  hole or namespace refusal yet — those are tickets 13-16's, held out deliberately so their
  future fields don't inherit a differently-shaped placeholder. Verified locally; **not yet
  landed** — same open question as tickets 09-11. No new ADR; implements ADR-0012 and ADR-0016.
- [Structural refusals, restatement, and caging a declared inability](issues/13-structural-refusals-restatement-and-caging.md)
  — **built, inside the same `compose()`.** Three structural refusals: a **split diamond**
  (two of the adopter's own edges reaching one `(party, kind)` at two versions — the real estate
  has no data source for a further-hop diamond, so a fixture proves it), a **cross-party rule
  conflict** (two `implementations` parents supplying one `(family, name, version)` with different
  content — never merged, never last-wins, dropped entirely, proved with a two-publisher fixture),
  and a **restatement of a mutate or a generate** (ADR-0016, proved against the real `cage-tier`).
  Restatement collapses the prototype's two parallel lists into one: `overlay.restate`'s weaker
  action *is* the declared inability. A stricter restatement overwrites the rendered action
  (proved: driftwood's `require-nonroot` Audit→Deny); a weaker one prices instead, through the
  real `cage.py`/`appetite.json`, and the render keeps the inherited action — reproducing the
  prototype's own driftwood/tuppence/ludlow → baseline/baseline/quarantine table exactly, against
  the real `driftwood-root-residual.json` scenario. The composed artefact carries no tier field
  itself; `cage-tier.yaml`'s own inherited CEL body reading `posture.acme.io/tier` off the
  workload is the runtime mechanism, unchanged and distinct from a declared verdict — an
  exact-key check, not a substring one, is what tells the two apart. The two-publisher limit
  prints from `len(implementations_parties)` every run: open at driftwood's real one, closed at
  the fixture's two. No new ADR; implements ADR-0016.
- [Baseline coverage, control claims and holes](issues/14-baseline-coverage-and-holes.md) --
  **built, inside the same `compose()`, and it makes the real estate's first defect visible for
  real.** The selected baseline resolves against the `controls` parent's real `catalog/
  BASELINE_VERSIONS.json`, walking nested controls (`ac-6.10` found); a prefixed or upper-case id
  is a hard failure, not a hole, `needs_composition: false`. Control claims now merge over every
  party that ships a member, including the adopter's own `component-definition.json` next to its
  `party.yaml` -- which required wiring `overlay.add` into `compose()` for the first time, since
  ADR-0017's "an adopter claim... fills it" has no route without it. A control counts as covered
  the moment *any* claim exists, valid or not, so a **hole is "no claim", not "no valid claim"**;
  a dangling or cross-party claim is a separate refusal on its own account
  (`dangling-claim`/`claim-against-another-partys-policy`). Proved against the real estate:
  driftwood's first composition records exactly **285 holes**, refuses on none of them, and
  **does** refuse on `platform`'s own two known-dangling claims (`ac-6`->`may-run-root-if-
  attested`, `cm-6`->`require-policy-version`) -- the first time composition has actually blocked
  the real estate's own pull request, which is the whole point spec.md opens with. A small
  synthetic catalogue/baseline/platform fixture, chained across runs by committing the header
  between them, proves the rest: a new hole refuses and names it; the same addition, claimed by
  the adopter against its own `overlay.add` member in the same run, is never a hole at all; a hole
  filled across two runs closes; a control that leaves the selected set refuses, narrowed baseline
  included for free; a named-baseline widening (MODERATE->HIGH shape) refuses with no override and
  doesn't double-fire as a removal; an adopter claim against a parent's policy refuses. The header
  gains `holes` and `selected-controls` -- the durable comparison point every later run reads --
  and stripping it changes nothing else rendered. One real pre-existing bug found and fixed in
  passing: an unpinned parent's content-digest SHA (ticket 12) was not stable across two `compose()`
  calls in one process, because it picked up a `__pycache__` file the orphan-guard's dynamic import
  writes as a side effect; ticket 14's `verify()` round-trip is what first exercises that path.
  Ticket 12/13's own prior assertions that the real driftwood/tuppence/ludlow compose cleanly no
  longer hold, correctly, and are updated to expect exactly platform's two known refusals and
  nothing else. No new ADR; implements ADR-0013 and ADR-0017.
- [The governed namespace lint](issues/15-governed-namespace-lint.md) -- **built, inside the same
  `compose()`, as the exact hole shape applied to a different signal.** `ungoverned_namespaces()`
  walks the adopter's own `Namespace` manifests for one that carries `institution` and not
  `governed: "true"`; a namespace with no `institution` label at all is never a candidate.
  `compute_ungoverned()` compares that set against the last signed composed artefact's own
  recorded set (a new `ungoverned-namespaces` header key): new refuses and names it, recorded does
  not, one that gains the label prints closed, and no committed header at all is the same
  bootstrap case ticket 14's holes use -- the first composition records every ungoverned namespace
  and refuses on none. Against the real estate this records **zero**: ticket 11 already landed
  `governed: "true"` on all three adopters' `Namespace` manifests, so the "first composition
  records three ungoverned namespaces" case spec.md opens with never actually fires there -- a
  fixture chain proves every acceptance criterion instead. The document gains `ungoverned[]`, the
  header gains `ungoverned-namespaces`; the composed artefact still carries no namespace list of
  its own, and neither namespace set is read by anything composition renders. No new ADR;
  implements ADR-0014 and ADR-0018.
- [Pricing and threat parents re-price, and never apply](issues/16-pricing-and-threat-parents-reprice.md)
  -- **built, inside the same `compose()`.** `compute_prices()` prices every declared
  `pricing`/`threat` edge twice, every run, through the estate's own machinery only: `ico`'s own
  converter (the fixed `uk-gdpr`/`lower-tier` entry) for `pricing`, `_threat_scenario()` --
  already ticket 13's -- for `threat`, both through `graded/cage.py`'s real `select()` against the
  adopter's own appetite band. "Old" is the version the last signed artefact's own header recorded
  for that `(party, kind)`; nothing to compare against yet (the first composition, or no prior edge
  of that kind) prices old and new at the same version -- an honest "no move", proved on real
  driftwood's very first run. Proved chained across two runs on the real estate: a pricing bump
  `v1->v2` moves driftwood's uncaged `uk-gdpr/lower-tier` exposure £16.9M->£9.0M through ico's
  converter, a threat bump moves tuppence's exposure £222,574->£326,139 (the register's own
  tuppence-only changelog) through the feeds module -- both land on `deny` before and after on the
  real bands, so the document prints `changed: false`, honestly reproducing the prototype's own
  finding that the wiring moves and the real outcome does not. No real band anywhere straddles a
  boundary, so the crossing case (`deny -> quarantine`) is proved directly against `price_parent()`
  with a £1,000,000 fixture band. A proposed `deny` is marked `proposed_as: "issue"`, every other
  tier `"label"` -- the mark, not the act; composition opens nothing, ticket 17 wires the proposer
  that reads it. No rendered file changes on any price move (byte comparison, `HEADER.yaml`
  excluded by design -- it legitimately carries the bumped parent's new SHA). No wall clock, no
  scheduler anywhere in the module (verified as an import-statement scan, not a prose match). The
  document gains `prices[]`. No new ADR; implements ADR-0006, ADR-0010 and ADR-0015.
- [The proposer opens the tier pull request](issues/17-the-proposer-opens-the-tier-pr.md) --
  **built.** `wargamer.py` gains `wargame_cage_tier(prices, org)`, a third drift row read
  straight off ticket 16's `prices[]`, carrying `tolerance`/`risk_bought_current` in the same
  shape an enforcement row does so `proposer_bounds.confidence()` needs no second formula.
  `propose()` branches a cage-tier row into a label-PR proposal or (for a proposed `deny`) an
  issue proposal with no label change at all. New module `platform/wargamer/tier_pr.py` is the
  one script in the estate that does not stop at the diff: it reads the adopter's own committed
  `composed/evidence.json`, bounds it through `proposer_bounds.py` unchanged, and lands the
  survivor -- a textual (not re-dumped) edit to the flow-style `labels: {...}` map that already
  claims a policy version, one fresh commit force-pushed to a per-subject branch (the branch
  name is the dedupe key), then `gh pr create`/`edit` or `gh issue create`/`edit`. No
  `merge()`/`approve()`/`dispose()` anywhere in the chain, offline-proved (local bare-git
  remote + a stub `gh` on PATH) in `tier_pr.py`'s own `selfcheck`. Each adopter gets
  `.github/workflows/propose-tier.yml`: a merged pin-bump PR or `workflow_dispatch`, no
  schedule. `propose-policy-pr.sh`/`bump-nist-pin.sh` are unchanged and still stop at the diff;
  both READMEs now say so and point at `tier_pr.py`. The false "gitsign identity at commit
  time" claim in `wargamer.py`'s docstring and `propose()` comment is corrected. No new ADR;
  implements ADR-0015.

- [Wiring composition into adopter CI, and signing](issues/18-wire-composition-into-adopter-ci-and-sign.md)
  -- **built and landed for real, on all three adopters.** Each of `driftwood`, `tuppence` and
  `ludlow` gained a `compose-check` job: recomposes on every pull request, fails on a refusal or a
  byte-diff against the committed `composed/` files, and posts the document as the job summary --
  proved on real pull requests, not just locally. The release workflow (`cut-release.yml`) now
  re-renders and verifies before any tag is cut, the same reasoning ADR-0011 already gives the
  publisher gate. Each adopter carries one real, gitsign-signed tag (`v1.1.0`) covering its first
  composed artefact: 285 recorded holes, 0 refusals, `tuppence` also recording its one genuine
  pre-existing ungoverned namespace (`tuppence-reset`).

  Landing this surfaced two real, separate defects, both fixed, not routed around. `platform`'s own
  `ac-6`/`cm-6` claims (ticket 10's named dangling pair) were genuinely fixed: `ac-6`'s stale
  duplicate dropped (the same rule already lives under `require-nonroot`), and `cm-6` now claims a
  real, newly-built `governed-namespace-requires-claim` `ValidatingPolicy` -- ADR-0014's own named
  fifth gap, closed for real rather than left as a permanent EXPECTED-RED. Separately, three policy
  versions (`2.0.0`, `2.0.1`, `3.0.0`) had been cut before the publisher gate (ADR-0011) existed and
  carried no evidence at all; `cut-release.yml` gained a `backfill_evidence_only` mode that computes
  and signs real evidence for an already-tagged version without moving the tag (tags stay immutable),
  used once per version, in dependency order, so each backfill's own predecessor comparison is real.

  The adopter gate (ADR-0011, ticket cs-28's own per-adopter scripts -- three genuinely independent
  implementations, not one shared file) now reads each adopter's own composed artefact as its
  subject: `versions_from_composed_evidence()` diffs the committed `composed/evidence.json` member
  set between a pull request's base and head commits, instead of reading `platform`'s raw
  `distribution/versions.yaml` array directly. A version retired from the composed set classifies
  major with no separate policy-diff case, fixture-proved end to end for all three adopters.

  No new ADR; implements ADR-0011, ADR-0012 and ADR-0014.

## Spec

[`spec.md`](spec.md), written 2026-08-25 from the eight resolved tickets. Status `ready-for-agent`.
Implementation is tickets `09` to `18`, cut from the spec on 2026-08-25.

```mermaid
flowchart LR
  09[09 nist baselines] --> 11[11 party artefact + adopters] --> 12[12 seam + faithful render]
  12 --> 13[13 refusals + caging] --> 16[16 re-price] --> 17[17 proposer PR]
  12 --> 14[14 holes]
  12 --> 15[15 governed lint]
  09 --> 14
  10[10 platform bare ids] --> 14
  14 & 15 & 16 --> 18[18 adopter CI + sign + bump]
```

## Not yet specified

Nothing.

## Out of scope

- **Computing the version bump.** That is [`computed-semver`](../computed-semver/map.md). This map
  owes it one fact and no more.
- **Repairing the named gaps.** Four from ticket [`01`](issues/01-does-composition-hold-up.md), a
  fifth from ticket [`04`](issues/04-unlabelled-pod-denial.md), and a sixth from ticket
  [`05`](issues/05-the-proposer.md). They are defects in the `platform` repo, found from the hub.
  Naming them, and specifying the fifth, was this map's job; fixing them was that repo's -- ticket
  [`18`](issues/18-wire-composition-into-adopter-ci-and-sign.md) crossed that line on purpose, once
  landing composition for real meant the gaps were no longer hypothetical. The fifth (the governed-
  namespace claim requirement) is fixed: `governed-namespace-requires-claim`, a real
  `ValidatingPolicy`, built and shipped. Ticket [`06`](issues/06-composing-the-remaining-policies.md)
  **renamed the second**: `cs-16` deleted `policy/policies/`, so `ac-6` claimed a policy that existed
  nowhere; also fixed by ticket 18, by dropping the stale duplicate claim (the same rule already
  lives under `require-nonroot`, claimed separately). The sixth -- `cage-tier` coercing an unknown
  tier label to `baseline`, so a merged `deny` label produces the loosest cage instead of the
  tightest -- remains open; ticket 18 did not touch it.
- **Declaring the order the composed members run in.** Ticket
  [`06`](issues/06-composing-the-remaining-policies.md) found that two of the six members mutate:
  `stamp-posture` writes the label `posture-trust-boundary` validates, and `cage-tier` writes the
  label `cage-netpol` generates from. A flat per-version render states neither dependency. Kyverno
  runs the mutating webhook before the validating webhook, which is what makes it work.
  **That is `platform` machinery.** A second implementations publisher is what would expose it, and
  the estate has one. Ruled out of scope, recorded in
  [ADR-0016](../../docs/adr/0016-a-subclass-never-restates-a-mutate.md).
