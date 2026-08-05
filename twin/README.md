# `twin`

Build tickets 01–08, 10 and 12 of `.scratch/twin/`. One dated signal binds to a component; one
scenario execution emits forecasts — plural; one recorded outcome scores them under proper scoring
rules; any artefact recomputes from its own pins. Scoring is in the first slice rather than
retrofitted, because without it we cannot tell whether any later capability helped, and because
scoring dictates what every other component must record.

**This is 10 of 77 build tickets.** What is not built is listed below and, more usefully, is named
inside every artefact the tool emits.

## Run it

```sh
bash twin/demo.sh                        # the whole loop, from a clean checkout
./bin/twin verify                        # the invariant suite
./bin/twin verify <artefact> --repo R    # recompute that artefact from its own pins
./bin/twin validate --repo R             # every object against its closed schema
./bin/twin graph --repo R --org netflix  # the typed knowledge graph
./bin/twin grade                         # computed depth grades, with evidence
```

The tool itself needs only python3, PyYAML and git — all already used by `estate/`. The checks want a
venv, pinned to the same versions CI uses:

```sh
python3 -m venv .venv
.venv/bin/pip install 'pyyaml==6.0.3' 'pytest==9.0.0' 'mypy==1.14.1' 'types-PyYAML==6.0.12.20250516'
.venv/bin/python -m pytest -q
.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
```

## The loop

```mermaid
flowchart LR
  subgraph repo["model repository — git-versioned text, the source of truth"]
    W["world layer<br/>components · propositions · world models"]
    O["org overlay<br/>components · signals · claims · scenarios · outcomes"]
    O -- "may reference, at a pinned world ref" --> W
    W -. "never references" .-> O
  end

  B["behavioural overlay<br/><i>separate unit · DPIA · advisory only</i>"]

  S["<b>twin sense</b><br/>dated signal + grade-5 claim"] --> BS["bound-signal"]
  R["<b>twin run</b><br/>scenario at a declared time"] --> FB["forecast-bundle<br/><i>forecasts, always a list</i>"]
  C["<b>twin score</b><br/>proper rules, as-consumed only"] --> SC["score-card<br/><i>names the bundle by pin</i>"]
  G["<b>twin graph</b>"] --> GR["graph<br/><i>components · people · typed edges</i>"]

  repo --> S & R & C & G
  FB -- "by sha256, never by path" --> C
  B -. "no route from anything above" .-> G

  BS & FB & SC & GR --> A["attestation sidecar<br/>runtime · no human hands"]
  A --> V["<b>twin verify artefact</b><br/><i>recompute the chain from pins</i>"]
```

Every artefact carries its pins, an authored/derived mark, and the computed depth grade of every
capability that produced it. Machine-varying facts — wall clock, host, interpreter — are absent
from the artefact and live in the sidecar, which is what lets identical pins give identical bytes
across architectures.

## What is honestly built

Depth grades are computed from the acceptance criteria of the owning **decision** ticket. Nothing
reaches `full`, and nothing can be typed as `full`.

| capability | decision ticket | grade | ticked |
|---|---|---|---|
| `domain-model` | 07 | stub | 0 / 7 |
| `provenance` | 14 | partial | 1 / 4 |
| `honest-build` | 20 | partial | 1 / 4 |
| `sense-move` | 11 | partial | 1 / 8 |
| `scenario-engine` | 13 | partial | 1 / 7 |

**4 of 30**, so every artefact carries an overall depth of `stub`. Two criteria were ticked in this
round and both were withdrawn after audit, each having rested on one clause of a multi-clause
criterion — the same ground on which three were withdrawn in the previous round. `./bin/twin grade`
prints every unticked criterion by name, and each surviving tick names its evidence and the build
ticket that earned it.

**Scoring and calibration are outside this ledger.** No capability file is owned by a decision ticket
that governs scoring, so build ticket 08's work does not appear in the 30. That is a hole in the
honesty instrument itself, not a claim that the work is done.

## The invariants

`./bin/twin verify` — 15 pass, 0 fail, 6 pending, 1 skipped and not faked. `pytest -q` — 218 tests
across seams 1 and 2.

| live | pending, with the ticket that activates it |
|---|---|
| `store_rebuildable_from_git` | `grade_5_only_path_never_prices` (19) |
| `identical_pins_identical_bytes` | `ruin_class_absent_not_priced` (28) |
| `every_artefact_marked` | `prefilter_precedes_pricing` (28) |
| `every_capability_depth_graded` | `as_consumed_admits_no_post_T_fact` (36) |
| `world_never_references_overlay` | `price_levels_never_probabilities` (59) |
| `no_collapse_mechanism` | `standing_library_covers_committed_classes` (69) |
| `no_recommended_action_field` | |
| `derived_never_human_signed` (structural) | |
| `only_as_consumed_scores` | |
| `no_special_category_slot` | |

A live invariant that skips counts as a failure, and so does a harness guard that skips without
declaring itself skippable. Pending is the only honest way to not assert something, and it is declared
in `invariants/manifest.yaml` where it can be seen. Two guards may skip, and both say why:
`cross_architecture_determinism` needs the CI matrix, and `hash_changes_are_authorised` needs two
committed versions of the manifest to compare.

The manifest also declares, per invariant, the **field names it refuses** — read from there rather than
from the code, because a check that derives its expectation from the thing it is checking is a tautology
and deleting a refusal would silently shrink it.

One invariant is narrower than its name suggests, and says so in the manifest.
`no_special_category_slot` guarantees there is **no field** for Article 9 data: the schemas are closed,
so compliance is an impossibility of representation. Values are additionally screened against a named
list — but `cohort` and `metric` are free identifiers, so a protected group can still be described in
words nobody listed. That screen is a net, not a proof.

## What a hostile model repository cannot do

The YAML in a model repository is authored by users and may arrive from another tenant, so the reader
treats it as untrusted. It cannot execute code through repository-local git config (`core.fsmonitor`,
hooks), smuggle a git option through a ref or a `world_ref`, expand a YAML alias bomb into the artefact,
pin the world layer to a ref that moves, hide a file from the listing through `core.quotePath`, or hide
a subtree behind a submodule. Each is refused with a sentence, and each has a test. The one thing it
*can* still do is describe a protected group in free text — a cohort or a metric identifier is not an
enumerable space — and put whatever it likes into a signal's own fields, which flow into the artefact
verbatim. An artefact is exactly as sensitive as the model repository it came from.

## What is not built

Named here so the skeleton cannot quietly become the definition of done.

- **No causal layer.** Structural dependencies only. Nothing propagates, nothing intervenes, there
  is no Monte-Carlo and no depth attenuation. (Build tickets 17, 20–22.)
- **No £.** No FAIR engine, no PERT sampling, no TVaR, no constraint pre-filter, no trade-off
  curve. The four pricing invariants are pending and there is nothing for them to guard yet.
  (23–33.)
- **The information regime is a tag, not a gate.** Every forecast declares its regime and only
  `as-consumed` scores — but nothing refuses a fact dated after T, so `as-consumed` is currently a
  claim the model repository makes rather than a property the engine enforces. The artefact says
  so, in `regime.gated`. (36.)
- **No rewind, no intervention, no backtest.** The two primitives the engine composes from are
  absent; `run` is time-forward with an authored belief and no inference. (35, 37.)
- **Forecast probabilities are read from a world model's declared belief.** Nothing infers them.
  This is the honest stub: the plumbing is real, the judgement is authored.
- **Calibration is one score card, not a record.** Brier and log loss are proper and regime-tagged,
  but there are no reliability diagrams over volume (09), no contamination discount (40) and no
  hindsight-resistance inversion (41). The answer-key format carries the `contamination` slot the
  discount will read; nothing computes it.
- **No signing.** `signature` is null and says so; the authored/derived split is enforced
  structurally but not cryptographically. (11.)
- **No skills, and therefore no seam 3.** The six skills are non-deterministic by construction and
  need their own eval harness; none exists, so skill regression would currently go silent. (42.)
- **No substrate.** The content-hash reference form round-trips against nothing. (48–51.)
- **The two-architecture determinism check has never run.** The CI matrix is declared and the
  golden digests are committed; the claim is wired, not proven.
- **The subjects are fixtures.** Netflix and Intel here are toy value chains with invented
  numbers, exercising the shape and nothing else. The real flagship work is tickets 71–77.
- **Sensing is a dead end.** Nothing consumes a bound signal: a signal cannot move an inferred
  position and cannot change a forecast. The spec's skeleton is "signal → binds to a component →
  **an inferred position moves** → execution"; the middle step is missing, so `sense` and `run`
  are two verbs over one repository rather than one loop.
- **Attestations are write-only.** A sidecar is emitted and nothing ever reads one back or
  verifies it, so it provides no tamper-evidence even in principle yet. (11.)
- **Overlay-to-overlay isolation has tests but no invariant.** The constitution's sixteen cover
  the world→overlay direction, not tenant→tenant reads, and the manifest may not grow a
  seventeenth without the constitution changing first.
- **Cross-machine verification has never run.** The `reproduce-elsewhere` CI job emits a score card
  on x86_64 Linux and recomputes it on arm64 macOS. Declared and wired; unproven. This and the
  two-architecture leg are the two acceptance criteria left unticked across tickets 01–12.
- **The graph has no causal edges.** `needs`, `maintains`, `knows` and `owns` are the whole
  vocabulary; there is no direction, sign, lag, elasticity or evidence grade. (17.)
- **Two named entity types are missing.** Decision ticket 07 names `Asset`/`DataAsset` and
  `Response`/`Control` in the core ontology; neither has a schema, which is why domain-model's
  first criterion stays unticked.

## Layout

```
twin/
  cli.py          seam 1 — the artefact CLI, the primary boundary
  verbs.py        sense / run / score / graph
  schema.py       the closed typed schema; Article 9 has no slot because there is no slot
  scoring.py      Brier and log loss, and the declared quantisation
  reproduce.py    recompute an artefact, and its chain, from its own pins
  repo.py         the pinned model repository; reads go through a git tree, never the worktree
  model.py        world layer, org overlays, the typed graph, the gated behavioural unit
  artefact.py     the envelope; forbidden field names refused at emission
  attest.py       attestation sidecars — where machine-varying facts go
  grades.py       depth grades as computed checklists
  blob.py         content-hash references for bulk substrate
  index.py        the derived index — a store, and therefore never authoritative
  canon.py        canonical serialisation
  fixtures.py     the deterministic fixture model repository
  capabilities/   one checklist per decision ticket that has code
  invariants/     manifest, harness, checks, golden digests
  demo.sh         the end-to-end
```

Code here is **disposable by default**. The durable artefacts are the versioned model repository
and the decision record under `.scratch/twin/`; replacing this code is normal, and the tests
assert on emitted artefacts rather than internals so that they do not become the sunk cost that
resists the rewrite.
