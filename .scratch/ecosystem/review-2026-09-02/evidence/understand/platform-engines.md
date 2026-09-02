# Map: platform's engines

Scope: `platform/` unit clone at
`/private/tmp/claude-501/.../scratchpad/units/platform`, tip commit
`46cd775` ("Merge pull request #8 from policy-as-versioned-platform/ticket-55-instrument-faults").
This is a fresh clone of the unit's default branch — not necessarily the exact
commit the TRUTH run=21 line names for `platform` (`46cd775`, which matches).

Method: read every README, every module's `^def`/`^class` index, the core
compose/cage/tier_pr/gate source in full or near-full, greps for
TODO/FIXME/stub/"not yet"/placeholder across the whole tree. Not read
line-by-line in full: `computed-semver/{cage_engine,coverage,corpus_generator,
pairing,comparison_window,release_integrity}.py` (read via docstring + `def`
index only — these five plus `witness_set.py` are 7,197 lines together, the
single largest module by far) and most `identity/`, `access/`, `oscal/` manifest
YAML (read via README + directory listing, not opened file-by-file). Everything
else below is read from source, not inferred from a README alone, unless
marked "per README".

## NORTH-STAR §4 in one paragraph, as the spine

§4's 7-step demo is: (1) a regulator publishes a signed feed → (2) Renovate
bumps an adopter's pin, composition re-prices exposure → (3) a price crosses a
band, cage tier moves, a signed proposal PR opens, a human merges → (4) Flux
reconciles the new cage spec, the workload keeps running caged tighter, the
residual is booked → (5) the twin plays a forward signal and publishes forward
intelligence the platform consumes → (6) provenance is Rekor-verifiable → (7)
one honesty command reports every claim as pass/fail/could-not-look. Everything
below is tagged **on-path** (directly implements one of these seven verbs),
**substrate** (the machinery §4 assumes exists — Kyverno, Flux, SPIRE — but
isn't itself a demo beat), or **beside** (a real, tested capability that
NORTH-STAR §4 does not name as one of the seven steps: human/device access,
break-glass, EUD).

---

## 1. The composition pipeline end to end

This is the mechanism for §4 steps 2-3. One file, `compose/composition.py`
(3,654 lines — the single largest hand-written module after computed-semver's
gate cluster), one entry point `compose(adopter_dir, parent_trees)` at line
2005, called by `cmd_compose` (line 2342) from the CLI, or directly by an
adopter's own CI (per `compose/README.md`, "policy-composition tickets 12-18").

```
party.yaml (adopter)          — party/party_artefact.py check() runs FIRST;
  inherits: [...]                a party artefact that doesn't check out
                                  refuses composition before anything else
        |
        v
resolve_sha() [composition.py:337]
  - controls/implementations: read spec.ref.commit off the adopter's own
    Flux GitRepository pin file (party_artefact.PIN_FILES:
      ("nist","controls") -> gitops/flux-system/gotk-sync-nist.yaml
      ("platform","implementations") -> gitops/platform/platform-pin.yaml)
  - feed/pricing/threat: _resolve_unpinned_sha() [:405] -- git log -1 on the
    party's own tree subdir, or a content sha256 digest for a non-git fixture
        |
        v
check_diamonds() [:786]  -- refuse two edges reaching one (party,kind) at
                             two versions
load_implementations() [:563] per implementations parent
  -> per LIVE version in distribution/versions.yaml's array:
     every ValidatingPolicy/MutatingPolicy/GeneratingPolicy in
     distribution/policies/v<N>/*.yaml, keyed on
     (identity family label, name with -N-N-N version suffix stripped)
  -> _load_guards() [:631]: orphan-guard + governed-namespace-guard, each
     rendered through the parent's OWN offline twin
     (render-orphan-guard.py / render-governed-namespace-guard.py)
load_overlay_add() [:597]  -- the adopter's own party.yaml overlay.add members
        |  merge into `merged: dict[(version,family,base) -> meta]`;
        |  a same-key different-content collision from two publishers is a
        |  "rule-conflict" refusal, dropped from the set, never merged
        v
render_member() [:656]  -- deep-copies the source doc unchanged, stamps
  policy-as-versioned.dev/composed-for + inherited-from + source-path;
  writes spec.validationActions ONLY on a ValidatingPolicy
        |
        v
apply_restatements() [:1069]  -- overlay.restate: only a ValidatingPolicy may
  restate; a WEAKER action (Deny->Audit) is never applied to the rendered
  member (which keeps the inherited action) -- instead it is priced as a
  "declared inability" through graded/cage.py's _cage_engine(), against the
  restating party's OWN party.yaml appetite.tolerance (_appetite() [:826])
        |
        v
_baseline_ids() / resolve_claims() / compute_holes() [:1301]  -- ticket 14:
  the selected NIST baseline resolves against the controls parent's real
  catalog/BASELINE_VERSIONS.json; OSCAL claims (component-definition.json,
  both parents' and the adopter's own) close "holes"; new/recorded/closed
  compared against the LAST SIGNED composed/HEADER.yaml (_previous_header()
  [:1021]) -- None means bootstrap, refuses on nothing
        |
        v
compute_ungoverned() [:751]  -- ticket 15: a Namespace manifest with the
  institution label and no governed:"true" is a new ungoverned namespace,
  same new/recorded/closed shape as holes
        |
        v
compute_prices() [:1934] -> price_parent() [:1520] / price_twin() [:1690] /
  price_quote() [:1803]
  -- ticket 16/21/25: every declared feed/pricing/threat edge is priced
  TWICE (old version's price vs new version's price) through the estate's
  OWN converters (ico's schema/to_fair_scenario.py, platform's
  feeds/to_fair_scenario.py), never a second risk engine. select_tier()
  (graded/cage.py:173) turns the NEW price into a proposed cage tier;
  every value is a real running-cage label now (isolated is the bottom
  rung, ADR-0022 -- nothing is ever "deny" any more).
  exposure_section() [:1882] rolls prices[] into the header's `exposure`.
        |
        v
composed/HEADER.yaml  (advisory; never read by Kyverno) +
composed/policies/v<N>/<name>.yaml (rendered, byte-identical to source once
  provenance annotations are stripped -- render_is_faithful() [:698])
        |
        v
document = {outcome, parents, members, refusals, restatements, cages, holes,
            ungoverned, prices[], limits}   <- what CI reads/commits
```

`verify(adopter_dir, parent_trees)` [:2305] re-renders from a fresh resolution
and diffs byte-for-byte against whatever `composed/` is already committed —
the offline round-trip proof. `selfcheck()` [:2617-3628] is ~1,000 lines: it
builds small synthetic fixture estates (`_write_fixture_platform`,
`_write_fixture_ico`, `_write_fixture_adopter`, `_write_fixture_catalog`) and
is the ONLY place the split-diamond and cross-party-conflict refusal paths are
ever exercised — `limits[]`'s `two-publisher-conflict` entry in the real
document is `"open"` because the real estate pins exactly one implementations
publisher (see composition.py:2120-2126).

### …to the proposer

`wargamer/wargamer.py`'s `wargame_cage_tier(prices, org)` [:158] turns
`compose()`'s `prices[]` into drift rows in the same shape
`wargame_enforcement()` uses. `propose()` [:183] / `_propose_tier()` [:214]
turn a drift row into a proposal dict (`merged: False`, `auto_merge: False`,
always `proposal_kind: "pull_request"` since ADR-0022 killed the issue
branch). `honesty/proposer_bounds.py` (`bound()`) gates WHETHER a proposal
survives (confidence / rate-limit / rejection-learning) — never merges.

`wargamer/tier_pr.py`'s `run()` [:357] is the module that actually lands it:
`find_governed_namespaces()` [:119] locates the adopter's own governed
Namespace manifest by its `policy-as-versioned.dev/governed: "true"` label
(never by a known path), `apply_tier_declaration()` [:210] does a line-level
edit setting `posture.acme.io/tier` on that Namespace document (not a pod, not
a YAML re-dump — comments survive), and `_land()` [:314] force-pushes one
fresh commit to a dedupe branch (`wargamer/retune-tier-<org>-...`) and opens
or updates a PR via `gh`. `disposing_calls()` [:169] is an AST-level self-scan
asserting the module contains no `merge`/`approve`/`close`/`--admin` call
shape — this is the module's own "we could dispose but structurally don't"
proof, and its docstring records a REAL planted regression the scan caught on
2026-08-29 (a `_gh("pr","merge",...)` call that passed the old
attribute-name-only selfcheck).

Selection-policy versioning: `composition.py:_selection_policy_version()`
[:1662] reads a `selection-policy/` package version from the ADOPTER's own
repo (not shipped in `platform/` at all — `SELECTION_POLICY_DIR` is a
constant naming an adopter-side directory), and records it on
`composed/HEADER.yaml`'s `selection-policy` key so a later proposal PR can
name "priced under selection policy vX" (see `tier_pr.py`'s `_pr_body()`).

### …to Flux reconciling it (§4 step 4)

`distribution/versions.yaml` (a flux-operator `ResourceSet`) is the single
edit point: `spec.inputs[0].versions[]` fans out, per element, into a
`GitRepository` (pinned tag+commit) + `Kustomization` (`prune: true`, path
`./policies/v<N>`), plus ONE orphan-guard `ValidatingPolicy` (Deny) whose
allow-list is `range`d from the same array, plus one static
governed-namespace-guard. `render-orphan-guard.py` and
`render-governed-namespace-guard.py` are its offline twins (used by
composition.py, shift-left, and the verify-*.sh beats, which run without
flux-operator in the loop). Today the array declares `4.0.0` alone — see
§2.11 below for why 2.0.0/2.0.1/3.0.0 and two patch backports were retired
rather than fixed in place.

---

## 2. Per-module map

Line counts below are `wc -l` over `*.py`+`*.sh` in that directory (not
including YAML/JSON/markdown). "Real vs fixture" names every stand-in found.

### 2.1 `compose/` — the composition seam — **on-path** (§4 steps 2, 3)
- Purpose: one seam, `compose()`, that resolves an adopter's inherited parents
  to signed content, merges/renders policy members, resolves baseline
  coverage and holes, lints governed namespaces, and re-prices every
  pricing/threat/feed edge.
- Files: `composition.py` (3,654 lines, all logic), `README.md`,
  `verify-composition.sh` (49-line bash beat).
- Inputs: an adopter dir's `party.yaml` + repo tree; `parent_trees: {party ->
  clone path}`. Outputs: `composed/HEADER.yaml`, `composed/policies/v<N>/*.yaml`,
  the evidence document (JSON via CLI).
- Called by: an adopter's own CI (not present in this clone — adopter repos
  are separate units); `wargamer.wargame_cage_tier()` consumes its `prices[]`
  output via the committed `composed/evidence.json`.
- Tests: `selfcheck()` (~1,000 lines) builds 4+ synthetic fixture estates
  and asserts every refusal path (split diamond, rule conflict, dangling
  claim, hole new/recorded/closed, baseline widening, missing instrument,
  pin-containment). `verify-composition.sh` is the CLI-level runnable beat.
- Fixtures standing in for real things: the whole selfcheck estate
  (`_write_fixture_platform`, `_write_fixture_ico`, `_write_fixture_catalog`,
  `_write_fixture_adopter`) is synthetic, not a real party. The real
  estate's own compose (against real driftwood/tuppence/ludlow) is NOT
  exercised inside this repo — this unit ships only the library.
- Known limits, self-reported in the document's own `limits[]`: the
  cross-party-conflict path is `"open"` because only one implementations
  publisher is pinned in the real estate; `_pin_containment_limit()` [:356]
  is a NAMED, unfixed gap dated 2026-08-29 — the header can assert a parent
  SHA that does not actually contain the rendered policy tree, because the
  fix (a merged commit) is "unpushed" as of that comment.
- TODO/stub markers: none in this file beyond the `ponytail:` comment
  convention (this repo's term for "acknowledged, deliberately deferred" —
  6 instances, e.g. `_resolve_unpinned_sha`'s `__pycache__` exclusion note,
  `_fx_feed_version`'s "highest published major" heuristic).

### 2.2 `computed-semver/` — the release-bump gate — **substrate** for cut-release (not itself one of §4's 7 steps, but the mechanism that makes every signed tag honest)
- Purpose: computes whether a policy release's DECLARED semver bump
  (`versions.yaml`'s `bump:` field) matches the REAL bump derivable from
  observed Kyverno admission movement + cage-dial movement, and refuses a
  release that understates itself.
- Files (20 py/sh, 7,197 py lines + 327 sh — by far the largest module):
  `gate.py` (62.7KB, the seam — `run_gate()`), `cage_engine.py` (71.5KB, the
  classification engine, two tracks: ValidatingPolicy admission via
  `rederive_bumps.classify_policy`, and cage/dial spec diff),
  `corpus_generator.py` (46.7KB, builds synthetic probe pods per predicate),
  `coverage.py` (47.9KB, cell/pair counts — explicitly "no percentage
  anywhere"), `pairing.py` (26.2KB), `comparison_window.py` (21.5KB, the ±1
  window), `release_integrity.py` (20.5KB), `witness_set.py` (26.9KB, the
  5 rederive fixtures + 6 named-but-missing real-infra witnesses),
  `generator_standing_check.py` (17.3KB), `rederive_bumps.py` (13.6KB, the
  cs-01 original: the three known-good historical bumps).
- I did not read `cage_engine.py`, `coverage.py`, `corpus_generator.py`,
  `pairing.py`, `comparison_window.py`, `release_integrity.py` in full —
  only their module docstrings and `def`/`class` index. A deeper review of
  this cluster needs a dedicated pass.
- Inputs: `corpus/` (real policy bodies copied verbatim from the sibling
  `policy` org repo at tagged versions — each file's header cites its exact
  source path+tag), `generated-corpus/` (700KB, the synthetic probe pods
  `corpus_generator.py` writes), `evidence/` (72KB, signed gate evidence
  JSON+bundle per cut version). Outputs: the evidence document `cut-release-gate.py`
  signs via `cosign sign-blob` and commits before the tag.
- Called by: `.github/scripts/cut-release-gate.py` imports `gate`,
  `comparison_window`, `corpus_generator` directly.
- Named, disclosed gap: **the 6 real-infrastructure witnesses (SPIRE, Istio,
  OpenBao, Pomerium, Dex, git-server) are not committed anywhere** —
  `witness_set.py`'s own docstring and `verify-witness-set.sh` both print
  this as a GAP, not a silent pass, every run.
- Two fixtures authored (not copied) in `corpus/`: `legal-department.yaml`
  and `no-owner.yaml` (per corpus README note) — no committed fixture in the
  source repo exercises those cases.
- Two other "not a real gap, a genuinely-cannot-yet" markers: `verify-witness-set.sh:12,56`
  ("GAP (not a failure): real-infrastructure witnesses not yet committed"),
  and `generator_standing_check.py`'s documented, permanent (by design)
  independence of the three cs-01 historical fixtures from
  `corpus_generator.py` (they predate the CEL idiom the generator
  recognises — this is disclosed as deliberate, not a bug).

### 2.3 `fair/` — the £ engine — **substrate** (every other engine's shared maths)
- No README.
- `fair.py` (390 lines): pure-stdlib beta-PERT Monte Carlo (`ITERATIONS=10_000`,
  `SEED=42` — deterministic), `simulate()`, `summarize()` (ALE/VaR95/TVaR +
  risk load at 6% cost-of-capital), `sum_prices()` (refuses to sum across
  perspective or currency — the ADR-0021 £-seam invariant every other
  module's `_sum_prices`/summing wraps). `severity.py` (80 lines): a
  lognormal-body/generalised-Pareto-tail severity model for twin forward-intel
  payloads that can't fit a bounded triple.
- Fixtures: `scenarios/driftwood-cart-pii.json`,
  `scenarios/driftwood-twin-heavy-tail.json` — both named per-institution
  demo scenarios, not live telemetry.
- Called by: `risk/enforce.py`, `graded/cage.py`, `tcor/tcor.py`,
  `wargamer/wargamer.py`, `honesty/`, `break-glass/break-glass.py`,
  `access/access.py`, `compose/composition.py` (`_sum_prices` wraps
  `fair.sum_prices`) — essentially every priced decision in the repo funnels
  through this one file.

### 2.4 `wargamer/` — the proposer — **on-path** (§4 step 3)
- Purpose: collects signed feeds + a human/device scenario library,
  war-games deployed controls against current intelligence, proposes
  (never merges) a signed policy PR on drift.
- Files: `wargamer.py` (371 lines — collect/wargame/propose/selfcheck),
  `tier_pr.py` (792 lines — the ticket-17 "last step lands" module, the one
  place in this whole repo that actually commits+pushes+opens a PR),
  `rejection_ledger.py` (288 lines — derives a dedupe/rejection ledger from
  closed-unmerged PRs, never a file), `propose-policy-pr.sh` (69 lines),
  `verify-wargamer.sh` (56 lines).
- Fixtures standing in for real things: `scenarios/human-device.json` (the
  whole human/device/ransomware/PQ scenario library — mixed
  human-seed/ai-generated per entry, asserted in selfcheck),
  `fixtures/threat-register/v3/register.json(.sig)` — a SIGNED but
  demo-authored "driftwood skimmer-campaign LEF uptick" fixture that is the
  only thing that ever drives the module's own drift demo (`CURRENT_FEED`
  constant points straight at it). `CONTROL` dict hardcodes
  `require-nonroot@2.0.0` as "the" deployed enforcement control being
  stress-tested — a fixed demo subject, not something wargamer.py discovers.
- Tests: `wargamer.selfcheck()` asserts the whole collect->wargame->propose
  chain including the "propose never dispose" structural property (asserts
  no `merge`/`dispose` attribute exists). `tier_pr.selfcheck()` [:453-702]
  is a full offline harness: a real local bare-repo "remote" + a stub `gh`
  on PATH that logs every invocation, including the `PLANTED_DISPOSAL`
  regression plant (`_open_or_update_pr` rewritten to call `pr merge
  --squash --admin` and a raw `/merge` REST path) that `disposing_calls()`
  must catch via AST walk, not string grep.
- TODO/stub markers: `rejection-decay.yaml:23` names its own 30-day decay
  window as "not yet tuned against real closes". `tier_pr.py` comments
  self-document a REAL, dated (2026-08-29) planted-and-caught regression
  (see above) rather than hiding it.
- Not on North Star §4 path directly but IS the machinery step 3 names
  ("A proposal PR opens, signed by the proposer's identity"). Explicitly not
  stood up: the actual PR-open needs a live GitHub org push + Actions-create-PRs
  org setting + OIDC/Rekor network — `propose-policy-pr.sh` "stops before
  commit/push/merge" (README, "Not stood up here"). `tier_pr.py` DOES push
  live when run without `--dry-run` — out of scope for this read-only review.

### 2.5 `graded/` — the £-picks-the-tier engine — **on-path** (§4 step 3-4, the tier itself)
- Purpose: named cage tiers (baseline/restricted/quarantine/isolated/infra)
  as deterministic dial expansions; `cage.py`'s `select_tier()` picks the
  loosest tier whose residual fits the org's own signed appetite band,
  clamped up to any adopter `overlay.floor`.
- Files: `cage.py` (main engine, `TIERS` dict, `select_tier` [:173],
  `select` [:190], `oscal_risk` [:241]), `prune-retired.py` (removes orphaned
  per-tier NetworkPolicy objects a retired version left behind), policies
  (`cage-tier.yaml` MutatingPolicy, `cage-netpol.yaml` GeneratingPolicy,
  `priorityclasses.yaml`), `up.sh`, `verify-graded.sh` (622 lines of bash —
  the largest single verify script in the platform tree), `tests/`
  (`kyverno test` matrices).
- **Self-disclosed drift, not fixed**: README states plainly
  `graded/policies/cage-tier.yaml` "still carries only the first three rungs"
  (no `isolated` dial mapping in the live Kyverno body yet) and its reach
  policy is "still one flat egress lockdown" rather than per-tier — `cage.py`'s
  own Python model has 5 tiers, the Kyverno body that actually admits pods
  has fewer/coarser. `verify-graded.sh` step 4 is stated to "report the
  drift" every run rather than pass silently over it.
- Fixtures: `scenarios/driftwood-behind-posture.json` (the one demo
  behind-posture workload scenario used in the README's own worked example
  and by `party` proportionality demos). `waf-placeholder/Dockerfile` — an
  explicit named stand-in for "the estate's actual heavier-WAF sidecar"
  (README: "WAF image ... placeholder").
- Called by: `compose/composition.py` (`_cage_engine()` imports this module
  directly for the restatement-caging path), `wargamer/wargamer.py`
  (`wargame_cage_tier`), `tcor/tcor.py`, `oscal/result2oscal.py`
  (`observation_uuid`/`oscal_risk` — the OSCAL risk-object producer).
- Real, dated live defects fixed and documented in-repo (2026-08-28/29):
  the per-tier `cage-netpol` synchronize/all-namespaces bug (Kyverno's
  watcher deleted every `cage-reach-*` in every OTHER namespace on any one
  caged-pod create), and the priority-admission triple defect across
  2.0.0/2.0.1/3.0.0 that made every declared-but-not-4.0.0 version
  undeployable (see §2.10).

### 2.6 `party/` — the party artefact schema+checker — **substrate** (feeds compose/, wargamer, honesty's reflexive check)
- Purpose: one signed `party.yaml` per party; `party_artefact.py` runs four
  checks in order (schema, pinned-tag agreement, baseline mirror,
  publish-capability). `check()` [:478] is called by `compose()` as the very
  first gate.
- Files: `party_artefact.py` (793 py-line total for the module incl. this
  file), `schema.json` (JSON Schema draft-07, the single source of truth for
  role/kind/floor enums), `verify-party-artefact.sh` (36-line bash beat).
- Real fact: `../party.yaml` (one dir up, the platform's OWN artefact) is
  checked by this same checker — "the platform is a party like any other".
- `PIN_FILES` (party_artefact.py:80): only 2 of the 3 real parent kinds have
  a Flux pin file to check against in THIS estate today —
  `("nist","controls")` and `("platform","implementations")`; `feed` is
  named `UNPINNED_KINDS` and checked separately by ticket-21's
  `verify-feed-contract.sh` (not in this unit — lives per-adopter or in feeds).
- Not stood up here / disclosed gap (`identity/README.md`): the identity
  package's federation fields (`trust_domain`, `bundle_endpoint`,
  `federates_with[]`) are decided to belong on `party.yaml` but
  `schema.json` is `additionalProperties: false` and doesn't accept them yet
  — adding them today would REFUSE every existing party artefact. Currently
  hardcoded as literals in `identity/federation/<org>.yaml` instead — named
  as the same "demand from a literal" defect shape H8-05 already flags.

### 2.7 `distribution/` — Flux version fan-out, orphan-guard, prune — **on-path** (§4 step 4) + **substrate**
- Purpose: `versions.yaml`'s one array is the whole "supported policy
  versions" contract; render scripts are its offline twins.
- Files: `render-version-tree.py` (286 lines — the frozen-tree renderer for
  a released version, self-scoping via `matchConditions`),
  `render-orphan-guard.py` (171 lines), `render-governed-namespace-guard.py`
  (121 lines), `render-and-prove.py` (144 lines — simulates the cs-15 repair
  release), 7 `verify-*.sh` beats (847 sh lines total), `verify/` (a
  precondition doc + extract-tag-fixture harness + `gate.yaml`).
- Versioned policy trees: `v1.0.0` through `v4.0.0` plus `vselfcheck` — but
  **only `4.0.0` is live in `versions.yaml`'s array today**; `v1.0.0`,
  `v2.0.0`, `v2.0.1`, `v3.0.0` sit on disk behind their own signed tags,
  frozen and unedited, retired from the fan-out (see the README's long
  2026-08-29 postmortem, reproduced in §1 above — priority-admission plugin
  defect + the pod-forges-its-own-tier defect via unread `namespaceObject`).
  Two never-cut patch backports (`v2.0.2`, `v3.0.1`) were built, proven to
  fix the priority defect, then retired the SAME day once they exposed the
  deeper tier-forgery defect.
- Called by: `compose/composition.py` (`load_implementations`, via
  `_load_module`/`_load_guards` dynamically importing
  `render-orphan-guard.py` and `render-governed-namespace-guard.py`
  straight out of the parent tree — literally executes the parent's own
  `.py` file); `shift-left/ci-check.py` (reads the same array for the ±1
  window).
- Real dated defect (2026-08-29), disclosed and fixed by retirement not
  patch: 3 declared versions could deploy ZERO pods; `verify-declared-versions-admit.sh`
  is the live-only beat that first surfaced it.

### 2.8 `feeds/` — signed reactive feeds — **on-path** (§4 step 1) + partly superseded
- Per README: **as of 2026-08-28 (eco-system ticket 21) `threat-register`,
  `cve`, `eol` moved to a separate `feeds` repo** as one-envelope-per-feed
  (`<name>/v<MAJOR>/feed.json`). The copies still physically present in this
  `platform/` unit (`threat-register/`, `cve/`, `eol/`, `keys/`,
  `wardley/intel/market-intel.json`) are explicitly named as staying ONLY
  because their consumers (`honesty/verify-honesty.sh`, `wargamer/`,
  `wardley/wardley.py`, the hub's `verify/provenance`, the twin's fixtures,
  composition's `feed_file()` bridge) still read these exact paths — they
  are scheduled for deletion once those consumers are repointed.
- Files: `to_fair_scenario.py` (207 py lines total across feeds/, includes
  `eol_ramp()` — the time-varying EOL ramp, +1x/year past eol_date capped at
  4x), `verify.sh`, `verify-feeds.sh` (111 sh lines total).
- Signing: `sign.sh` (the repo-local ed25519-via-openssl signer) is
  explicitly RETIRED as of ticket cs-27 — replaced by `cosign sign-blob`
  keyless for the one thing this repo signs on an ongoing basis now
  (release-gate evidence). The committed `.sig` files under
  `threat-register/`/`cve/`/`eol/` still verify against
  `keys/feeds-signing-key.pub.pem` unaffected — README states plainly
  "nothing new is signed with `keys/`" (ADR-0023 D3).
- Called by: `wargamer.py` (`BASELINE_FEED` constant points at
  `feeds/threat-register/v1/register.json`), `compose/composition.py`
  (`FEED_CONVERTERS`, the `feed_file()` bridge for the two legacy names).

### 2.9 `tcor/` — Total Cost of Risk + four-move crossover — **substrate** (feeds §4 step 3's tier choice and wargamer's drift math)
- No README-listed py file count beyond `tcor.py` (329 py lines incl.
  scenarios), pure stdlib, no cluster.
- Purpose: `crossover()` computes fix/cage/transfer/deny TCoR and books the
  cheapest; `applicable[]` on a scenario narrows which moves are even
  possible (you cannot fix/cage/deny a third party's stack — only transfer).
- Real, named regression caught in `wargamer.selfcheck()` [wargamer.py:290-309]:
  stripping `applicable` off `hyperscaler-region-concentration` makes the
  engine default `costs.fix` to 0 and nonsensically "fix" a hyperscaler
  outage for ~£3,726 — asserted as the exact number research-05 named as a
  regression, kept in the test on purpose as a tripwire.
- Called by: `wargamer.py` (`wargame_scenarios`), `graded/cage.py`
  (residual+C_cage feeds tcor's control-spend line).

### 2.10 `risk/` — the appetite-band decision (Audit/Deny) — **substrate**
- No README. `enforce.py` (214 lines): `decide()` is the one function —
  `risk_bought = ALE_warn - ALE_deny; verdict = Deny if risk_bought >
  tolerance else Audit`. `tolerance_for(org)` reads the band off the
  ORG'S OWN signed `party.yaml` `appetite.tolerance` — the file
  `risk/appetite.json` is explicitly, actively RETIRED (asserted in
  `enforce.py`'s own `cmd_selfcheck`: `assert not os.path.exists(...
  "appetite.json")`). A party declaring no appetite is a `MissingInstrument`
  that raises, never a silent default.
- `enforce.py`'s own selfcheck asserts, by source-scanning its own imports,
  that this file imports neither `datetime` nor `time` — "the escalation is
  justified by a number, not a timer" is a structurally-enforced property,
  not just a claim.
- Called by essentially everything priced: `wargamer.py`, `graded/cage.py`
  (via the same `_cage_engine`/`_appetite` route composition.py uses),
  `compose/composition.py`, `tcor/tcor.py`, `honesty/reflexive.py`.
- `PR.md` present in this dir — not opened in this pass; likely a
  standing note on a specific pull request. `risk/scenarios/driftwood-cart-pii-tightened.json`
  is a demo fixture for the tightened-triple selfcheck case.

### 2.11 `posture/` — Kyverno→SPIRE posture projection — **substrate/beside** (identity plane, not one of §4's 7 verbs but feeds break-glass/access)
- 0 raw py lines counted (policies are YAML; `up.sh`/`verify-posture-projection.sh`
  are the only scripts, 209 sh lines).
- Purpose: `stamp-posture.yaml` (MutatingPolicy) writes
  `posture.acme.io/version` from the validated policy-version claim,
  unconditionally overwriting any forged input; `posture-trust-boundary.yaml`
  (ValidatingPolicy Deny) refuses any mismatch. A second `ClusterSPIFFEID`
  bakes `posture/vN` as a leading SVID path segment.
- Three-layer trust boundary per README: mutate-overwrites,
  validate-denies, RBAC-absence-of-grant (workload SAs are not granted
  `patch`/`update` on pods) — explicitly documented as "assert the absence
  of a grant, don't author a theatrical unbound deny rule".

### 2.12 `shift-left/` — the pre-merge ±1 version-skew CI check — **on-path** (part of §4 step 2's "re-price before merge" spirit, and the gate every proposal PR must clear)
- Files: `ci-check.py` (160 py lines total incl. `fixtures/`),
  `verify-shift-left.sh`, `ci-workflow.example.yml` (the shape an adopter's
  own `.github/workflows/` wires this into — this repo owns only the check).
- Fixtures: `workload-compliant.yaml`, `workload-flip.yaml`,
  `workload-unversioned.yaml` — 3 small demo pod manifests, exit-0/exit-1
  cases, not real workloads.
- Mechanism: reads `distribution/versions.yaml`'s SAME array
  `render-orphan-guard.py` renders from (no second source of truth),
  computes the ±1 major-line window, runs real `kyverno apply` (not a
  pooled exit code) per version in the window.
- Real dated consequence (README, distribution's own retirement note):
  with only ONE version (`4.0.0`) now declared, this beat's Audit→Deny
  flip check has no ±1 NEIGHBOUR to flip onto, so it now grades
  **could-not-look**, by name, rather than a false pass.

### 2.13 `engine/` — Kyverno + flux-operator install — **substrate**
- 0 py lines; `up.sh`+`verify-engine.sh` (108 sh lines). Two HelmReleases
  only (`kyverno/helmrelease.yaml`, `flux-operator/helmrelease.yaml`).
  README states plainly neither was installed anywhere in the repo before
  this ticket (11), despite two other READMEs naming both as prerequisites
  — i.e. this module exists to fix a real, disclosed ordering gap.

### 2.14 `eud/` — UTM vTPM End-User Devices — **beside**
- 0 py lines; 218 sh lines (`build-vm.sh`, `up.sh`, `verify-eud.sh`,
  `tpm-devid-enroll.sh`). Explicitly narrated demo hardware: UTM/QEMU vTPM
  VMs because the presenting Mac has no real TPM (Secure Enclave is not
  DevID-compatible). README's own "honest caveat": swtpm mints a
  self-signed emulated EK, not a manufacturer-issued one — every VM spec
  and the WHfB runbook repeats this caveat. `iso` paths in `vms/*.json` are
  literal placeholders (README: "point at the actual Windows 11/Linux
  installer ISOs"). `up.sh` never boots a VM or installs an OS (GUI/ISO-gated,
  cannot run headless) — it prepares offline artifacts and prints venue steps.

### 2.15 `break-glass/` — £-proportional posture-gated human access — **beside** (not one of §4's 7 verbs, but the human/device projection of the same appetite-band mechanism)
- `break-glass.py` (226 py lines total incl. scenarios), `assurance-bands.json`
  (the £ thresholds), 4 scenario fixtures
  (`driftwood-read`/`tuppence-write`/`driftwood-bulk-export`/`ludlow-patient-data`
  — named single-state FAIR triples, not live telemetry). No cluster
  resources of its own — "rides on the access plane" per README.
- One code comment flagged by the TODO grep: `break-glass.py:114` — "the
  factor is addable. Device not yet required" (a passkey step-up path that
  doesn't yet mandate a device for that rung — read as a scoping note, not
  necessarily a defect).

### 2.16 `honesty/` — falsifiability, bounded AI, self-governance — **on-path** (§4 step 7, verbatim)
- Purpose (three engines): `calibration.py` (back-test the FAIR model
  against `incidents.json`, Bühlmann credibility recalibration — 691 py
  lines total for the module), `proposer_bounds.py` (confidence/rate-limit/
  learn-from-rejections around `wargamer.wargame()` — the hard backstop
  being that this module too exposes no `merge()`), `reflexive.py` (scores
  the PLATFORM ITSELF through `risk/enforce.py` against the platform's own
  signed `party.yaml` appetite — not a bespoke self-check path).
- Fixtures: `incidents.json` — explicitly authored so driftwood runs HOT
  (actuals above model → recalibrate up) and ludlow runs COLD (actuals below
  → recalibrate down) — a curated fixture, README states plainly "not a live
  SIEM feed". `scenarios/platform-self.json` — the apparatus modelled as a
  workload (controls-off = warn state, controls-on = deny state).
  `rejections.json` — a fixture ledger (superseded in practice by
  `wargamer/rejection_ledger.py`'s DERIVED-from-closed-PRs mechanism per
  ADR-0024, per that module's own docstring — `rejections.json` here reads
  as the earlier, file-based design honesty/ shipped before ADR-0024 moved
  the ledger to be derived rather than stored).
- Not stood up: all checks are offline python asserts + openssl; wiring
  `incidents.json` to a real loss ledger and opening a real recalibration
  PR are both named as deferred to a human/CI step (README, "Not stood up
  here").

### 2.17 `wardley/` — the forward (5th) feed — **on-path** (§4 step 5, the twin's forward signal)
- `wardley.py` (574 py lines total for the module). `build_map()` places
  components on the evolution axis and flags MOVEMENT (crossing a stage
  boundary within a horizon), not static position — the README calls out
  `credential-stuffing-aas` by name as a component that does NOT flag
  because it's already commodity and stationary (no movement to anticipate,
  proving the movement-not-position distinction is real, not asserted).
- Fixtures: `intel/market-intel.json(.sig)` (signed but hand-authored demo
  intel), `enactment.json` — deliberately UNSIGNED and deliberately
  SEPARATE from market-intel.json, gating a defensive-capability's cost
  discount on independently-observed corroboration
  (`declared_by_subject: false`), never the commoditisation claim
  corroborating itself. `pqc-transport-migration` deliberately carries NO
  `enactment.json` entry — the README states a link there would be
  dishonest, and `selfcheck()`/`verify-wardley.sh` plant each corroboration
  violation and assert the credit disappears.
- Calibration dial named as such and NOT free: `ATTACK_COST_COLLAPSE_K` —
  README documents that widening K does not reliably flip a move sooner
  because cage-tier selection is non-monotone in the threat (between K=5
  and K=6, one scenario STOPS drifting); K=4.0 is "measured to sit in a
  stable plateau (3.0-5.0)".
- Feeds into `wargamer.wargame_scenarios()` via `forward_into_wargamer()` —
  reuses the war-gamer's own scenario shape unmodified.

### 2.18 `currency-controller/` — post-admission posture re-evaluation — **on-path** (part of §4 step 4's "keeps running, caged tighter" — closes the admission-time-only snapshot gap)
- `currency.py` (257 py lines total for module): pure-stdlib `select_stale`
  + `deposture_patch` (both unit-tested) + an in-cluster urllib reconcile
  loop, CronJob-scheduled once/minute.
- Mechanism (documented as "the crux"): the re-patch must remove BOTH the
  posture label AND the policy-version claim in one merge-patch, because
  `stamp-posture` would otherwise re-clobber posture back on every UPDATE —
  a single-label patch would be immediately undone by the mutate policy
  that's still watching.
- `--action evict` is named as the blunt alternative to the default
  `deposture`.

### 2.19 `identity/` — SPIRE+Istio+OpenBao+Pomerium as one versioned package — **substrate**
- No standalone `.py` at top level (glob found none; policies/manifests are
  YAML, `gitsign-verifier/` is its own subpackage not walked in this pass).
- Packaged as ONE self-versioned `implementations` artefact
  (`VERSION`=1.1.0, `kustomization.yaml` = membership, `flux-pin.yaml` = the
  shape an adopting org copies). `component-definition.json` carries the
  package's OSCAL claims (ADR-0017: claimed once by whoever ships it, not
  re-claimed per adopter).
- Real, disclosed non-live state: `federation/` (12 `ClusterFederatedTrustDomain`
  objects across 4 clusters) — README states **"None of it is live"**, and
  `verify-federation.sh` is documented to deliberately exit 3 (not pass)
  for three concrete, named reasons: driftwood's SPIRE still runs a single
  shared trust domain `acme.internal` (not yet per-org); tuppence/ludlow run
  KinD with NO SPIRE at all; `spire-server.federation.enabled` is off (and
  turning it on would re-mint the CA and crashloop the agent on its stale
  cached bundle).
- Real, disclosed schema gap: `trust_domain`/`bundle_endpoint`/`federates_with[]`
  are decided (by ADR/ticket) to belong on each party's `party.yaml`, but
  `party/schema.json` is closed (`additionalProperties: false`) and adding
  them today would refuse every existing party artefact — so
  `federation/<org>.yaml` carries them as hardcoded literals instead, named
  as exactly the same defect shape H8-05 already flags elsewhere.
- Dex retirement plan (README, a 5-step ordered plan, none of it done in
  this directory — explicitly "Owner: platform/access", nothing here
  deletes a Dex manifest): today's only human login root is a Dex static
  bcrypt account, and a code comment beside it (in `access/oidc/`) is
  flagged as FALSE by this README — it claims to be "the SAME subject as
  the gitsign committer", which the README states plainly is not true (the
  gitsign signer is a GitHub Actions workflow OIDC subject; no human can
  log in as it).

### 2.20 `access/` — human+device access plane — **beside** (feeds break-glass, not itself a §4 verb)
- `access.py` (151 py lines total for module) — graded ALLOW/STEP_UP/DENY
  by a static `OP_TIER` table × factors (OIDC / WebAuthn / device SVID).
  README names the `OP_TIER` table as static now, with an explicit upgrade
  note: "wire to fair.py's £-crossover if the bar should move live with the
  risk £" — i.e. this table is NOT yet priced the way break-glass.py's
  bands are; access.py's tiers are fixed, break-glass.py's are £-derived.
  This is a real asymmetry between two sibling modules doing similar
  gating.
- Real caveat named twice (WebAuthn attestation `none` vs `direct`+FIDO
  MDS) and calibration-knobs section calls out that a Pomerium chart
  version not present on the Helm repo "leaves the HelmRelease
  un-reconciled forever and no proxy pod is ever created" — a live-observed
  failure mode, not speculative.

### 2.21 `oscal/` — PolicyReport → OSCAL assessment-results up-flow — **on-path** (§4 step 6/7's evidence substrate)
- `result2oscal.py` (452 py lines total for module) — the one
  `component-definition.json` policy↔control map; carries "two ADR-0009
  shims inline" per README (copying `.scope` into `results[].resources`
  because Kyverno ≥1.18 leaves it null, and stripping the `-<version>` name
  suffix so one component-definition covers every coexisting version).
- The join proved, not eyeballed: every observation uses
  `graded/cage.py`'s `observation_uuid(subject, policy)` — one formula,
  so a cage's `risk.related-observations` pointer is byte-identical to the
  observation `result2oscal` emits BY CONSTRUCTION;
  `verify-upflow.sh`/`result2oscal.py --selfcheck` assert this equality
  directly rather than trusting it.
- `fixtures/policyreports.yaml` — three demo-shaped PolicyReports (a
  compliant pod, a `legacy-till` fail case, and a Crossplane RDS pass, to
  show the join is plane-agnostic). `fixtures/component-definition-unknown-control.json`
  — a negative-case fixture. `lint_claims.py` present but not read in this pass.
- The £ deliberately lives elsewhere: the ALE facet is emitted by
  `graded/cage.py`, not here — README: "The £ is not here" is its own
  section heading.

### 2.22 `.github/workflows/` + `.github/scripts/` — the release act — **on-path** (the mechanism §4's provenance step rides on)
- `cut-release.yml` (188 lines): `workflow_dispatch` only (deliberately not
  a standing automation). Two dispatch shapes (single-tag legacy,
  multi-tag `tags` JSON array) normalized by `cut-release-normalize.py` (87
  lines) into one `tags.json` BEFORE anything else runs. Order of operations,
  explicit in the workflow's own comments: (1) install pinned
  gitsign/cosign/kyverno by binary+sha256 checksum, no marketplace action;
  (2) normalize; (3) `cut-release-refuse-existing.sh` (14 lines) — every
  tag checked for existence BEFORE any tag is created; (4)
  `cut-release-gate.py` (407 lines) — the publisher gate, calling
  `computed-semver.gate.run_gate()`, BEFORE `git tag` ("a gate after the
  tag can only burn the number"); (5) evidence uploaded as a run artifact
  ALWAYS (`if: always()` — "a refusal's own evidence matters most"); (6)
  `cut-release-commit-evidence.sh` (27 lines) commits signed evidence
  into a release commit; (7) `cut-release-update-array-commit.sh`
  (102 lines) — a SECOND commit repointing `versions.yaml`'s array element
  at the evidence commit's real SHA (a commit cannot name its own SHA, so
  this is deliberately two commits, not one); (8)
  `cut-release-create-tags.sh` (27 lines) — signs the tag(s) via the
  workflow's own ambient GitHub Actions OIDC identity (gitsign keyless,
  no browser/device-code, no long-lived key); (9)
  `cut-release-push.sh` (34 lines) — ALL tags pushed in one atomic
  `git push`, "either all of them land or none do".
- **No override at any scope, stated explicitly and checked**:
  `cut-release-gate.py`'s own docstring states `CUT_RELEASE_TEST_MODE`
  touches ONLY the `cosign sign-blob` signing mechanic (for a non-Actions
  laptop run), never `run_gate()`/`comparison_window.evaluate()`/
  `release_integrity.refusal()` — "grep this file for the string if in
  doubt: it appears exactly once".
- Multi-tag gate semantics (`cut-release-gate.py` docstring, lines 1-52):
  only `policy/v<semver>` tags enter the gate (a bare platform `vX.Y.Z` tag
  is a different line, skipped outright); gated ONCE PER policy tag, never
  pooled; the comparison window for every tag in one dispatch is the array
  as it stood BEFORE the dispatch (two tags cut together do not see each
  other as predecessors); a refusal on ANY policy tag in the dispatch
  blocks the WHOLE dispatch, no partial commit/tag.
- `release-verify-evidence.py` (53 lines) — reads the evidence back; not
  traced further in this pass.
- Also present, not read in this pass: `fetch.yml` (208 lines), `release.yml`
  (166 lines — per `README.md`, verifies the identity-pinned signature
  against an offline Rekor bundle, runs `shift-left/verify-shift-left.sh`
  as the release gate, publishes the GitHub Release).

---

## 3. Cross-cutting observations

- **The £ has exactly one summing rule and it's enforced, not just
  documented**: `fair.sum_prices()` raises on any mixed
  perspective/currency list; `compose/composition.py:_sum_prices` wraps it
  rather than re-implementing; `party.yaml` comments and `enforce.py`'s own
  selfcheck both assert `risk/appetite.json` no longer exists — the
  platform-held appetite fixture is actively retired (ADR-0021), replaced
  by each party's own signed `appetite.tolerance`.
- **"Propose, never dispose" is asserted three separate ways** across
  `wargamer.py` (attribute-absence check), `tier_pr.py`
  (`disposing_calls()` — an AST walk over string constants and Call nodes,
  with a documented, dated real regression it caught), and
  `honesty/proposer_bounds.py` (the module's own no-`merge()` claim). This
  is a genuinely defence-in-depth structural property, not a single check
  repeated three times.
- **ADR-0022's "no deny rung" is load-bearing across at least 4 modules**:
  `graded/cage.py` (`isolated` replaces `deny` in `TIERS`/`ORDER`),
  `compose/composition.py` (`proposed_as` mark logic, comment: "ADR-0022
  retired the deny rung"), `wargamer/wargamer.py` (`_propose_tier`'s
  docstring: "ADR-0022 retired ADR-0015's issue branch... every proposal
  this module lands is a pull request"), and `distribution/versions.yaml`
  (the governed-namespace-guard's promotion from Audit to Deny is dated the
  same window, 2026-08-28).
- **A cluster of real, dated (2026-08-28/29) live defects were found and
  fixed by RETIREMENT rather than patch**, disclosed at length in
  `distribution/README.md` and mirrored in `graded/README.md`: the
  priority-admission-plugin triple defect (3 versions undeployable), the
  pod-forges-its-own-tier defect (unread `namespaceObject`, live-observed
  reaching the API server from an `isolated` namespace), the
  `cage-netpol` synchronize/all-namespaces bug, and an
  `allowPrivilegeEscalation`/`privileged` pairing defect. All four are
  named as REAL, OBSERVED LIVE, not hypothetical.
- **Two modules disagree on whether an access decision is £-derived**:
  `access/access.py`'s `OP_TIER` table is static (README names this as a
  known upgrade path); `break-glass/break-glass.py`'s bands ARE derived
  from `fair.py`'s carried £. Same identity substrate, two different
  decision disciplines, not obviously reconciled anywhere in this unit.
- **The `feeds/` module is mid-migration**: the README states its own
  contents are staying in place PAST their stated retirement only because
  named consumers (5 of them, enumerated) haven't been repointed yet — this
  is a real, currently-live duplication (feed content exists both here and
  in the separate `feeds` org repo), not a historical note.

---

## 4. What I did not cover / could not look

- `computed-semver/{cage_engine,coverage,corpus_generator,pairing,
  comparison_window,release_integrity}.py` — read via docstring + function
  index only (~4,600 of the module's 7,197 lines not read line-by-line).
  This is the single biggest gap in this map; a reviewer relying on the
  gate's exact classification rules should read these directly.
- `identity/gitsign-verifier/`, `identity/federation/*.yaml`,
  `access/device/*`, `access/oidc/dex-helmrelease.yaml`, `oscal/lint_claims.py`
  — named and characterised from README + grep only, not opened.
- `.github/workflows/fetch.yml`, `.github/workflows/release.yml`,
  `.github/scripts/release-verify-evidence.py` — line counts only, not read.
- I did not run any verify-*.sh script, `tier_pr.py` (would need
  `--dry-run` even to safely execute, and running scripts was not needed to
  produce this static map), or any selfcheck — everything above is read
  from source text, not from an execution I performed. I have not
  cross-checked this unit's git tip (`46cd775`) against the TRUTH run=21
  line's per-unit SHA table beyond noting they match for `platform`.
- I did not read the adopter-side repos (`driftwood`/`tuppence`/`ludlow`)
  at all — several things named here as "the adopter's own X" (selection-policy
  package, twin/forward-intel, governed Namespace manifest, component-definition.json)
  live there, not in this unit, and I have not verified their actual shape
  against what `platform/`'s code expects of them.
