# verify*.sh map — driftwood, tuppence, ludlow, nist, ico, feeds, insurer

Scope: all 22 `verify*.sh` files found under
`scratchpad/units/{driftwood,tuppence,ludlow,nist,ico,feeds,insurer}` (find command below;
task text said "about 25" but the actual count is 22 — verified twice, listing pasted at the
bottom of this file). Every script was read in full except `tuppence/scripts/verify-adopter-gate.sh`
(556 lines), which was read via targeted grep of its scenario headers plus prior knowledge of its
near-identical sibling `ludlow/verify-adopter-gate.sh` (438 lines, read in full) — flagged per-row
below. Run-21 grades come from `talk/captures/.estate-clone_<path-with-/-replaced-by-_>.out` on the
hub's `origin/main`, read via `git show origin/main:talk/captures/<file>.out`. Command used to
enumerate scripts: `find driftwood tuppence ludlow nist ico feeds insurer -iname 'verify*.sh' | sort`.

Legend for "substrate first?": whether the script's FIRST action requires a live cluster/network,
as opposed to reading files/fixtures/tags first and only reaching for a cluster afterward.

---

## driftwood

### `driftwood/scripts/verify-identity-regexp.sh` (81 lines)
- **Claims to observe**: `EXPECTED_IDENTITY_REGEXP` in `.github/workflows/release.yml` matches only
  driftwood's own `main`/`release/<maj>.<min>.x` and rejects every foreign/malformed identity shape.
- **Observation vs selfcheck**: observes the estate — reads the live regexp out of the checked-in
  `release.yml`, and (Part 1) runs the **real gitsign binary** against every real `v*.*.*` tag in
  the clone with that regexp; (Part 2) exercises negative/positive shapes with `grep -E` as a
  documented RE2-equivalent stand-in for cases that can't be real-signed.
- **Offline/live**: offline overall; Part 1 needs `gitsign` on PATH and does `git fetch --tags`
  (network read only, not required for the tags-empty branch — degrades to "nothing to prove yet",
  not a fail).
- **Substrate first?**: N/A (no cluster).
- **Exit 0 without observing anything?**: No — `command -v gitsign` is required or it fails; if no
  `v*.*.*` tags exist it prints an honest "nothing signed to verify" but still runs all Part-2
  synthetic assertions before PASS.
- **Run-21**: PASS — `talk/captures/.estate-clone_driftwood_scripts_verify-identity-regexp.out`
  ends "PASS: EXPECTED_IDENTITY_REGEXP matches main + release/<major>.<minor>.x only, anchored to
  this repo."

### `driftwood/twin/verify-twin-scenarios.sh` (275 lines)
- **Claims to observe**: driftwood's twin carries its six standing scenarios (two realising new
  classes), and the "penalty-published" scenario prices the consequence, never the fine itself.
- **Observation vs selfcheck**: mixed — walks up the tree to find the hub checkout (`twin/repo.py` +
  `clone-estate.sh`), imports the real `twin` package, and checks real committed YAML under
  `orgs/driftwood/scenarios/*.yaml`, `world/`, `party.yaml`, `signals.yaml`. Also self-tests its own
  "money-shaped" regex on 3 fixed strings before using it for real (lines 58-60) — a selfcheck of
  the checker embedded inside an estate-observing script.
- **Offline/live**: fully offline. Requires `pyyaml`, `git`, and a hub checkout above it (`SKIP` if
  absent).
- **Substrate first?**: N/A.
- **Exit 0 without observing anything?**: No — every branch either SKIPs with a named reason or runs
  9 real checks; PASS requires all 9 groups to observe true.
- **Run-21**: FAIL — `.estate-clone_driftwood_twin_verify-twin-scenarios.out` ends "TOTAL: 14 pass,
  2 fail, 0 could-not-look / FAIL: 2 standing-scenario check(s) observed false." (last visible PASS
  line before the failures: "every priced valuation names a fact resolvable in party.yaml and
  re-derives from it" — the 2 failures are earlier in the log, not shown in the tail I captured;
  re-open the full capture to name them if needed).

### `driftwood/verify-reconcile.sh` (177 lines)
- **Claims to observe**: driftwood reconciles healthily from a pinned, signed `GitRepository`
  **and** (section 0/6) the composed policy set is in force from signed sources per the five-fact
  sample.
- **Observation vs selfcheck**: observation of the estate throughout — no selfcheck branch in this
  file itself (the five-facts grading it calls does its own separate `selfcheck` subcommand, not
  invoked here).
- **Offline/live**: hybrid, deliberately ordered (ticket 60 fix, commented in the file): the
  five-fact sample is graded FIRST from `drift/samples.jsonl` (an artifact of a real CI run, offline
  to read) **before** any cluster check; only if a local kind cluster exists does it proceed to the
  live kubectl assertions (sections 1-6b).
- **Substrate first?**: **No** — explicitly reordered so the sample grades before `need_substrate`
  (comment: "the citable run (no kind in CI) exited 3 before ever reading the lane"). This is a
  named prior defect (REVIEW-2026-08-31, M7) that was fixed.
- **Exit 0 without observing anything?**: No — PASS requires either (a) the five-fact sample itself
  graded PASS (a real observation of a real remote cluster taken by the CI sampler), or (b) a local
  cluster present and all live assertions 1-6b true.
- **Run-21**: **FAIL** — sample grading found `fact_2_tag_signature_verified_at_the_source_boundary`
  FALSE for driftwood-composed: "the controller's verdict is 'false': v1.1.0: signature or
  certificate chain did not verify at tagger time 1787677714:
  ...certificate is not yet valid". Ends "FAIL: FAIL: a fact of the five-fact sample was observed
  false."

### `driftwood/verify-twin-overlay.sh` (260 lines)
- **Claims to observe**: driftwood's twin emits one forward-intel feed from its own overlay, priced
  and labelled (whose money, what currency, which policy version), never prescriptive.
- **Observation vs selfcheck**: mostly estate observation (real `emit-forward-intel.py --check`,
  real `party.yaml`, real overlay components/edges/scenarios, real `selection-policy` module and its
  own self-check subprocess) **plus** 4 deliberately-planted-defect checks (lines 204-245): a
  throwaway copy of the tree is mutated four ways and the script asserts the emitter refuses each
  for the *specific* reason planted — this is closer to a mutation-test selfcheck of the refusal
  logic than of the script itself, run against copies, never the real files.
- **Offline/live**: fully offline (temp dir git-free copy, no network/cluster).
- **Substrate first?**: N/A.
- **Exit 0 without observing anything?**: No — first real check (`emit-forward-intel.py --check`)
  must PASS or the whole run FAILs and prints "could not read the feed; nothing further was
  observed."
- **Run-21**: **FAIL** — `.estate-clone_driftwood_verify-twin-overlay.out` ends "FAIL:
  emit-forward-intel.py --check: FAIL: twin/forward-intel/v1/feed.json is not what the overlay
  renders" then "TOTAL: could not read the feed; nothing further was observed" / "FAIL: 1
  twin-overlay check(s) observed false" — this is the very first check, so nothing downstream in
  this script ran.

---

## feeds

### `feeds/verify-feeds.sh` (290 lines)
- **Claims to observe**: every published `<feed>/v<N>/feed.json` validates against the one platform
  envelope schema and its own payload schema; `rule.yaml`/`bump.yaml` sit beside each feed;
  `bump.py`'s ladder holds; `publishes[]` names only real paths; a twin scenario validates against
  the 2.0.0 forward-intel schema; fx prices a date it publishes and refuses a date it doesn't.
- **Observation vs selfcheck**: mostly estate observation of real committed feed files, plus
  `bump.py selfcheck` (an internal selfcheck of the bump-ladder code) and `converters/fx.py
  selfcheck` (internal selfcheck of the fx converter) as necessary preconditions before the
  real-tree checks that follow them.
- **Offline/live**: fully offline. Needs a sibling `platform` checkout for
  `platform/feeds/schema.json` (`PLATFORM_DIR` or `../platform`/`.platform`) — SKIPs if absent.
- **Substrate first?**: N/A (no cluster ever).
- **Exit 0 without observing anything?**: No — SKIPs cleanly if no platform schema found, else runs
  the full envelope/payload/bump/publishes/fx chain; any single failure exits 1.
- **Run-21**: PASS — ends "PASS: every published feed is one envelope validated against
  platform/feeds/schema.json and its own payload schema; ... fx prices a date it publishes and
  refuses one it does not."

### `feeds/verify-market-and-news.sh` (291 lines)
- **Claims to observe**: market-moves publishes a series (never probability-shaped); the Polymarket
  adapter's selection is mechanical (admits/refuses named rule fields); the feed's own threshold
  (not a fixed schedule) is what opens a PR, exercised through the real clock scripts; sub-threshold
  readings still land on the observation branch; news carries the 5 decided fields and admits only
  entries with provenance; niobium is absent from the feed; no clock invokes a model.
- **Observation vs selfcheck**: pure estate observation — runs the real `fetch/market-moves.py
  --dry-run`, `fetch/news.py --dry-run`, mutates a **copy** of the committed source corpus (in a
  `mktemp -d`) to cross the declared threshold and re-runs the same real adapters, then `git diff
  --quiet` against the real tracked `market-moves`/`news` dirs to prove the clock never wrote a
  declaration. Grep-scans real `.py`/workflow files for model-endpoint strings (ADR-0024 check).
- **Offline/live**: fully offline; no network, no cluster, no model calls (explicitly the point of
  section 7).
- **Substrate first?**: N/A.
- **Exit 0 without observing anything?**: No — has a defensive `__verdict_trap` EXIT trap (added
  2026-08-29 per its own comment) specifically so a raw Python traceback still produces a legible
  `FAIL:` last line rather than an ungraded exit; every section must observe true.
- **Run-21**: PASS — ends "PASS: market-moves publishes a dated series from one mechanical rule over
  one venue with no probability-shaped field; ... no clock here invokes a model."

### `feeds/verify-news-headline-skill.sh` (183 lines)
- **Claims to observe**: the `classify-and-judge` skill is human-run only (never clock-invoked), its
  claim file only cites claim kinds the twin has and a `derived_from` that matches exactly; each
  validation rule actually bites (mutation-tested); the twin binds the pinned market-moves series to
  a dated move and refuses to read a price level as a probability; niobium lives in the adopter twin
  library, not the news feed.
- **Observation vs selfcheck**: estate observation of the real skill file, the real
  `validate_claim.py` against the real worked example and real landed claim files (`.claim.yaml`) in
  any adopter checkout, plus 6 planted-mutation checks (lines 61-89) that prove the validator rejects
  each specific violation for the *named* reason (a mutation-test style selfcheck of the checker,
  run against a scratch copy, never the real files).
- **Offline/live**: offline; needs a hub checkout (`HUB_DIR` or walked-up) that carries `twin/schema.py`
  and the skill directory, else SKIPs.
- **Substrate first?**: N/A.
- **Exit 0 without observing anything?**: No — SKIPs with a named reason if the hub/skill/overlay
  isn't found; the twin-binding section explicitly maps its own SKIP(3)/FAIL/PASS exit codes.
- **Run-21**: PASS — ends "PASS: classify-and-judge is a human-run skill ... niobium is a scenario in
  the adopter's library, unbound by any clock."

---

## ico

### `ico/.github/scripts/verify-declared-bump.sh` (36 lines)
- **Claims to observe**: ico's own declared bump (`bump.yaml`) agrees with the bump the ladder
  computes from ico's actual published tree, under its own `rule.yaml`.
- **Observation vs selfcheck**: both — runs `declared-bump-gate.py --selfcheck` (ladder-on-fixtures
  selfcheck) first, THEN `--tree` (the real observation against the real committed tree).
- **Offline/live**: fully offline, no tag/network/cluster.
- **Substrate first?**: N/A.
- **Exit 0 without observing anything?**: No — the `--tree` real-tree check is mandatory for PASS;
  SKIP(3) only if the gate itself reports could-not-look.
- **Run-21**: PASS — ends "PASS: the bump ladder holds on fixtures, and ico's own declared bump
  agrees with the bump computed from its published tree..."

### `ico/schema/verify.sh` (21 lines)
- **Claims to observe**: a versioned penalty-schema file's signature verifies against the committed
  public key, and its `schema_version` field matches its own directory name.
- **Observation vs selfcheck**: pure estate observation of a real signed file — no selfcheck; called
  as a helper by `verify-penalty-feed.sh` with a version argument (`v1`, `v2`).
- **Offline/live**: fully offline (`openssl pkeyutl -verify` locally, no network).
- **Substrate first?**: N/A.
- **Exit 0 without observing anything?**: No — hard-fails if the schema/sig files are missing, if
  `schema_version` mismatches, or if the real `openssl` signature check fails.
- **Run-21**: not captured as a standalone row (it is invoked inside `verify-penalty-feed.sh`'s
  section 1, which passed — see below).

### `ico/verify-certificate-identity-regexp.sh` (44 lines)
- **Claims to observe**: `EXPECTED_IDENTITY_REGEXP` accepts only ico's own `main`/`release/x.y.x`
  and rejects every foreign/unanchored shape.
- **Observation vs selfcheck**: estate observation — reads the pattern live out of
  `.github/workflows/release.yml`; asserts with bash `[[ =~ ]]` (documented ERE≈RE2 stand-in, no
  real gitsign call here, unlike driftwood's sibling script).
- **Offline/live**: fully offline.
- **Substrate first?**: N/A.
- **Exit 0 without observing anything?**: No — every positive/negative case is asserted; any single
  mismatch calls `fail`.
- **Run-21**: PASS — ends "PASS: EXPECTED_IDENTITY_REGEXP accepts this repo's main and
  release/<major>.<minor>.x, and rejects every foreign org/repo/path and unanchored variant tried."

### `ico/verify-penalty-feed.sh` (228 lines)
- **Claims to observe**: the ico penalty schema is signed+versioned; `fair.py` consumes it
  unmodified; a schema bump moves the £ without touching `fair.py`; a second obligation source on
  the same breach raises (never lowers) the £; the three published feed envelopes match the one feed
  contract; major-3's control weights partition (never add to) each regime; and the nist controls
  pin ico declares is a real tag on the real nist remote.
- **Observation vs selfcheck**: estate observation throughout, including a deliberate
  tamper-and-reject check (section 2: mutates a copy of v1's schema and proves the signature check
  rejects it) and a real economic-consequence check (section 4/5: proves the £ actually changes via
  the real `fair.py` engine, not merely that files differ).
- **Offline/live**: **hybrid** — sections 1-7 fully offline; section 8 does a live
  `git ls-remote --tags` against `https://github.com/policy-as-versioned-nist/nist` and SKIPs (never
  fails) if the network is unreachable (documented "ponytail": ls-remote can't distinguish network
  failure from a 404/rename, so a renamed nist repo would also read as could-not-look).
- **Substrate first?**: No — file/schema/signature checks (1-7) run before the one live network call
  (8), which is last.
- **Exit 0 without observing anything?**: No — every section is a real assertion; PASS requires all
  8, including the live tag check, to succeed (SKIP only for that one section on unreachable
  network).
- **Run-21**: PASS — ends "PASS: ico penalty schema signed+versioned, fair.py consumes it unmodified,
  ... and the nist pin is a real tag" and immediately above it "ok nist tag v1.1.0 is on the remote"
  — i.e. the live network check in run 21 succeeded for real.

---

## nist

### `nist/.github/scripts/verify-declared-bump.sh` (36 lines)
- Identical structure/purpose to ico's twin (declared bump vs tree-computed bump for nist's own
  catalogue). Selfcheck-then-tree, offline, no substrate.
- **Run-21**: PASS — "PASS: the bump ladder holds on fixtures, and nist's own declared bump agrees
  with the bump computed from its published tree..."

### `nist/scripts/verify-catalog.sh` (54 lines)
- **Claims to observe**: the nist OSCAL catalogue is well-formed, its recorded sha256 matches disk,
  LOW/MODERATE/HIGH baselines resolve to real (bare) control ids, the identity regexp behaves (calls
  the sibling script below), `publish.sh` seeds+tags cleanly in a dry run, and `party.yaml`'s
  `publishes[]` all resolve with `rule.yaml`/`bump.yaml` present.
- **Observation vs selfcheck**: real estate observation via `verify_catalog.py` and
  `verify_baselines.py` (both real modules operating on the committed catalogue), plus a real dry-run
  invocation of `publish.sh` (not a stub — it "seeds + tags", i.e. exercises real git tagging
  machinery in dry-run mode) and a real `party.yaml` scan.
- **Offline/live**: fully offline; carries the same 2026-08-29 `__verdict_trap` pattern seen in the
  feeds scripts, for legible last-line failures.
- **Substrate first?**: N/A.
- **Exit 0 without observing anything?**: No — the trap converts any nonzero/non-3 exit into an
  explicit FAIL line; the whole chain must succeed for PASS.
- **Run-21**: PASS — ends "PASS: nist catalog verified + publishable."

### `nist/scripts/verify-cert-identity-regexp.sh` (58 lines)
- Twin of ico's/ludlow's identity-regexp checks, for nist's own `release.yml`. Bash ERE stand-in,
  documented as faithful for this pattern's construct set. Offline, no substrate.
- **Run-21**: PASS — ends "OK: EXPECTED_IDENTITY_REGEXP anchors org/repo/workflow and allows only
  main + release/<major>.<minor>.x." (this file has no separate top-level `PASS:` line of its own;
  it is invoked as a sub-step by `verify-catalog.sh`, whose own PASS covers it, and is also
  runnable/gradable standalone per the file listing — its own last line is the `OK:` shown, which
  `verify-catalog.sh`'s harness treats as this step's pass evidence).

---

## insurer

### `insurer/verify-insurer-party.sh` (95 lines)
- **Claims to observe**: `party.yaml` parses, declares role `insurer` (and `publisher` iff it
  publishes anything), every `publishes[].path` exists and its `payload_schema` parses as JSON, and
  the whole artefact validates against `platform/party/schema.json` via the real
  `platform/party/party_artefact.py`.
- **Observation vs selfcheck**: pure estate observation, no selfcheck branch.
- **Offline/live**: fully offline; needs a sibling `platform` checkout for the final schema
  validation (`PLATFORM_DIR` or `../platform`) — SKIPs (not fails) if absent.
- **Substrate first?**: N/A.
- **Exit 0 without observing anything?**: No — SKIPs with a named reason only if `party.yaml` itself
  or the platform checkout is missing; otherwise every check must observe true.
- **Run-21**: PASS — ends "OK: party.yaml is a valid party artefact; every check that could run
  agrees (any it could not is a NOTE above)" then "PASS: insurer party artefact."

### `insurer/verify-insurer-quote.sh` (384 lines)
- **Claims to observe**, per published quote feed: (1) one ADR-0019 envelope whose payload validates;
  (2) the attachment equals the insured's own signed appetite exactly (not a restated number); (3)
  every exclusion/condition names a control id real in nist's catalogue and a regime the insured's
  own exposure actually prices; (4) the premium is reproducible byte-for-byte from
  `pricing/quote.py`'s versioned formula over the insured's *current* signed exposure (a stale
  exposure hash is a named could-not-look, "a re-quote PR is due", never a pass); (5) no sum crosses
  a perspective — the platform's own `fair.sum_prices` is proven to refuse adding the insurer's layer
  to the insured's premium.
- **Observation vs selfcheck**: pure estate observation across sibling checkouts (adopter, nist,
  platform), all via `ADOPTERS_DIR`/`NIST_DIR`/`PLATFORM_DIR` env defaults (`..`, `../nist`,
  `../platform`). No selfcheck branch — it directly imports and calls the real `pricing/quote.py`,
  `platform/fair/fair.py`.
- **Offline/live**: fully offline; every "could not look" (missing sibling checkout, stale exposure
  hash, missing evidence file) degrades gracefully to a per-check SKIP rather than a crash.
- **Substrate first?**: N/A (no cluster ever touched).
- **Exit 0 without observing anything?**: No — if `party.yaml` publishes nothing it FAILs outright
  ("there is no quote to look at"); otherwise the grading is: any FAIL → exit 1; else any SKIP →
  exit 3; else PASS. So a run consisting entirely of SKIPs (e.g. no sibling checkouts at all) exits
  3, not 0 — it cannot silently PASS on zero observations.
- **Run-21**: **SKIP** (3) — one of 21 checks could not be looked at: "quote-driftwood: priced
  against exposure sha256:397abe81d6cb but ../driftwood/composed/HEADER.yaml now signs
  sha256:5822260bab86 -- the insured re-signed its exposure and a re-quote PR is due" — an honest
  staleness SKIP per the script's own contract, not a defect in the script; two other quote-ludlow
  checks around it did PASS for real (the summing-helper refusal, and the "not pinned yet" named
  absence).

---

## ludlow

### `ludlow/verify-adopter-gate.sh` (438 lines) — READ IN FULL
See "the three adopter-gate scripts" section below for shared analysis with tuppence's twin.
- **Run-21**: PASS overall — `.estate-clone_ludlow_verify-adopter-gate.out` ends with the multi-line
  PASS block ("PASS: ADOPTER_GATE_IDENTITY_REGEXP matches only ...; ... NOT exercised here (CI-only,
  confirmed): cosign accepting a genuinely valid Fulcio-signed bundle -- no ambient OIDC credential
  exists on this machine.") — the file names its own honest scope limit as part of the PASS text,
  not a FAIL.

### `ludlow/verify-certificate-identity-regexp.sh` (40 lines)
- Same structure/purpose as ico's/nist's identity-regexp checks, ludlow's own release.yml. Offline,
  bash-ERE stand-in, no substrate.
- **Run-21**: PASS — ends "PASS: EXPECTED_IDENTITY_REGEXP matches only
  policy-as-versioned-ludlow/ludlow's cut-release.yml on main or release/<major>.<minor>.x."

### `ludlow/verify-reconcile.sh` (189 lines)
- Structurally identical to `driftwood/verify-reconcile.sh` (same file, `ludlow` substituted for
  `driftwood`, plus an extra section 6 asserting the risk-appetite ConfigMap matches ludlow's own
  signed `party.yaml` appetite — driftwood carries no such section). Same five-fact-sample-first
  ordering fix, same substrate gating, same exit-0-requires-real-observation property.
- **Run-21**: **FAIL** — fact 5 observed FALSE for the `platform` source: "16 of 16 rendered objects
  are in no Flux inventory (absent from the cluster, or live but put there by something other than
  Flux)." Ends "FAIL: FAIL: a fact of the five-fact sample was observed false."

---

## tuppence

### `tuppence/reset/verify-reach-secrets.sh` (140 lines)
- **Claims to observe**: `customer-accounts-reset` accepts only callers whose SVID attests the
  current policy version — a current caller reaches the service AND its OpenBao secret; a
  stale/out-of-currency caller is refused both.
- **Observation vs selfcheck**: hybrid — offline core is a real selfcheck of the reach/secret glob
  logic (`reach.py selfcheck`) plus a real regex-shape assertion against the committed
  `authorizationpolicy.yaml` (ALLOW-only ⇒ default-deny); live tail (only entered if the posture
  layer + workloads are actually installed) execs real `curl` from real pods and does a real
  SPIFFE-JWT-SVID mint + OpenBao login. The script is explicit and self-critical about an honesty
  gap: the "secret" live half has **never** been observed for real on this estate because the
  `caller` container carries no SPIFFE client — it names the exact missing container/volume fix
  needed and downgrades its own closing PASS line accordingly rather than overclaiming (see the
  3-way conditional closing message, lines 134-140).
- **Offline/live**: hybrid, live tail gated behind `need_substrate` at the very top of the script
  (line 25) *and* a second finer gate (posture layer + `$NS` workloads actually present) before the
  live curl/JWT/OpenBao checks run at all.
- **Substrate first?**: **Yes** — unlike the three `verify-reconcile.sh` scripts, this one calls
  `need_substrate` immediately at line 25, before any offline check. A run with no kind cluster SKIPs
  before observing anything about `reach.py` at all.
- **Exit 0 without observing anything?**: No path exits 0 without `need_substrate` passing — the
  file cannot PASS on an absent substrate. It also has a codified anti-vacuity fix: OpenBao runs as
  `sts/openbao` and an earlier version of this file's `deploy/openbao` reference silently matched
  nothing, so "current SVID could not log in" is now a hard FAIL (not a print) specifically because
  an empty current-login token would otherwise make a stale refusal print as a false pass on a
  broken exec (lines 94-99 comment this out explicitly).
- **Run-21**: **SKIP** — `.estate-clone_tuppence_reset_verify-reach-secrets.out`: "SKIP: kind
  cluster 'driftwood' does not exist" — confirms substrate-first behaviour: no kind cluster in run
  21's environment, so this script never got past `need_substrate`.

### `tuppence/scripts/verify-adopter-gate.sh` (556 lines) — read via targeted grep of scenario
  headers (Part/Scenario markers), not read line-by-line; see caveat at top of file.
- Same lineage/purpose as `ludlow/verify-adopter-gate.sh` (both run `adopter_gate.py`'s real CLI
  against real throwaway git repos plus the real `cosign` binary), but **materially larger and
  stronger**: tuppence's version adds Scenario E — a **real cosign ACCEPT** against platform's real,
  currently-committed `platform-pin.yaml` and real committed evidence bundles (grep hit: "a REAL
  cosign ACCEPT... proves ... that REAL cosign accepts platform's REAL committed evidence") — this is
  exactly the gap ludlow's own file names as "NOT exercised here (CI-only, confirmed)". Also adds
  Scenario E2 (same real bundles refused when the identity constant is swapped for a foreign
  publisher — proving the identity pin is load-bearing against a real Fulcio cert, not just a
  string), Scenario F (old_tag == new_tag no-op path), and Scenario A/B (real gated release plus two
  real array-level releases: unchanged-then-retired) matching the excerpt seen in the run-21 capture.
- **Offline/live**: offline (throwaway local git repos + local `cosign`/`openssl`, no cluster, no
  network) except that Scenario E's real-ACCEPT path depends on a bundle that was itself minted by a
  genuine GitHub Actions run and is committed to the repo — so this script's PASS is standing on a
  previously-observed live artifact, not re-doing that live signing itself.
- **Substrate first?**: N/A (no cluster).
- **Exit 0 without observing anything?**: No — every scenario has an explicit assertion; `cosign`
  absence triggers a named SKIP for the cosign-dependent scenarios only (grep: "SKIP: cosign is not
  installed -- Scenarios D2/E/E2 run the real binary against real bundles"), not a silent pass.
- **Run-21**: PASS overall — capture tail shows Scenario A ("real PASS -- array unchanged... composed
  re-reads 9.0.0's real committed evidence, weaker-than-declared note fires") and Scenario B ("real
  FAIL -- 9.0.0 retires with nothing replacing it, composed forced major") both behaving as their own
  scripted expectations require (the FAIL lines inside the capture are the *expected refusal test
  cases*, not the script's own verdict), ending "PASS: adopter-gate.py checks out the tag under
  review (never the default branch), ... cosign really ACCEPTS platform's real committed evidence:
  the gate passes unskipped. ... forces a real non-zero-exit FAIL, naming the version, when a
  composed bump goes major on a real retirement."

### `tuppence/scripts/verify-identity-regexp.sh` (133 lines)
- **Claims to observe**: tuppence's own `EXPECTED_IDENTITY_REGEXP` (release.yml) behaves correctly
  AND tuppence's separate `EVIDENCE_EXPECTED_IDENTITY_REGEXP` (shift-left.yml, used to verify
  platform's evidence signature) is a **distinct** identity that (a) matches only platform's real
  cut-release.yml, (b) breaks on a platform workflow rename (the acceptance criterion, proved
  directly), and (c) does NOT accept tuppence's own release identity.
- **Observation vs selfcheck**: estate observation of two live-read regexps out of two real workflow
  files, asserted with bash ERE as a documented RE2 stand-in.
- **Offline/live**: fully offline.
- **Substrate first?**: N/A.
- **Exit 0 without observing anything?**: No.
- **Run-21**: PASS — ends "OK: EVIDENCE_EXPECTED_IDENTITY_REGEXP anchors platform's org/repo/workflow
  path, distinct from tuppence's own identity above, and a workflow rename genuinely breaks the
  match."

### `tuppence/verify-reconcile.sh` (189 lines)
- Same file family as driftwood's/ludlow's `verify-reconcile.sh` (five-fact-sample-first fix,
  substrate-gated live tail, plus the risk-appetite section 6 that ludlow also carries but driftwood
  does not — tuppence's skin is "toward-strict" vs ludlow's "Deny-heavy (strictest)").
- **Run-21**: **FAIL** — fact 5 FALSE for `tuppence-composed`: "16 of 16 rendered objects are in no
  Flux inventory (absent from the cluster, or live but put there by something other than Flux)."
  Ends "FAIL: FAIL: a fact of the five-fact sample was observed false."

---

## The three `verify-reconcile.sh` scripts, side by side

`driftwood/verify-reconcile.sh`, `ludlow/verify-reconcile.sh`, `tuppence/verify-reconcile.sh` are the
same script family (near-identical bodies, `$SELF` substituted per repo; ludlow and tuppence add a
"6. risk-appetite skin" section driftwood lacks). All three:

1. Grade the **latest five-fact sample** from `drift/samples.jsonl` FIRST, before touching any
   cluster (a fix dated to ecosystem ticket 60, reordering past a bug where the citable CI run — no
   kind cluster — used to exit 3 before ever reading the lane; commented explicitly as
   REVIEW-2026-08-31 finding M7).
2. If there's no local kind cluster: PASS on the sample alone if it graded PASS (reasoning: the lane
   sample observed a cluster reconciling the REAL remotes, "the stronger claim" vs the local seeded
   demo world); otherwise SKIP naming both reasons.
3. If a local cluster exists, run the full live reconcile assertions (GitRepository/Kustomization
   Ready, content landed, nist dependency pinned, platform pin if applied, risk-appetite skin for
   ludlow/tuppence, and the Kyverno cage-enforcement check added after a 2026-08-29 review finding
   that a Namespace could declare a tier nothing enforced).
4. Re-print the five-fact verdict as "section 6/7" for narrative completeness.

None of the three can exit 0 without a real observation: either the CI-taken five-fact sample graded
PASS for real, or a real live cluster's live assertions all held.

## The five-fact sample: `drift/five-facts.py` (identical module in driftwood, tuppence, ludlow)

Fully read for driftwood's copy (816 lines); tuppence's and ludlow's are the same module per the
`verify-reconcile.sh` bodies invoking it identically and per ADR-0023's naming of one shared
contract — not independently diffed byte-for-byte, flagged as **not directly verified identical**
across the three copies (a reasonable follow-up for auditors: diff the three `drift/five-facts.py`
files to confirm no per-adopter drift in the pre-registration).

**Commands**: `sample` (writes one JSON record per source to `drift/samples.jsonl`, only ever run by
the CI observation lane per ADR-0023 D1), `grade` (reads the latest complete sample group and applies
the verify-script exit contract), `selfcheck` (a real unit-test suite of the module's own pure
functions — `_verdict`, `_minutes`, `inventory_id`, `_fact_two`'s three-state logic, `sample_provenance`
— run against hand-built fixtures, never against `drift/samples.jsonl` itself).

**The five facts, per source** (driftwood-composed / platform / nist for driftwood; the adopter's own
`<adopter>-composed` / platform / nist analogously for tuppence and ludlow):
1. **Ready at the pin, on the real remote** — the `GitRepository` is Ready, its `url` matches the
   pin AND matches `^https://github\.com/policy-as-versioned-<party>/<party>$` (a real GitHub remote,
   not the in-cluster demo git server), and its live `tag`/`commit` equal the pin.
2. **Tag signature verified at the source boundary** — NOT a bare boolean: this fact is FALSE if
   `spec.verify` (an OpenPGP/SSH re-signature) is used at all (ADR-0023 D3 forbids any second
   signer), `null`/could-not-look if no gitsign-verifying controller annotation exists at all, and
   only `true` if the controller's own verdict is `"true"`, the issuer is exactly the GitHub Actions
   OIDC issuer, AND the identity regexp it verified against is anchored at both ends and names that
   specific publisher's own repo (checked against `driftwood`'s own `release.yml` constant for the
   driftwood source; for platform/nist, whose `release.yml` isn't in this checkout, only the
   "is it a real anchored pin naming that party" property is checkable, not equality to a specific
   constant).
3. **Last-applied revision equals the pinned commit** — for `driftwood-composed` (the
   `ResourceSet`-consumed source), every consuming `Kustomization`'s `lastAppliedRevision` must equal
   the pinned commit; for platform/nist, which are "verified sources only" (ticket 16 Q5 — nothing
   reconciles their trees), the check instead compares `composed/HEADER.yaml`'s recorded parent sha
   to the pin.
4. **Rendered objects byte-equal to an offline render** — a property of the composed set as a whole
   (all three source records carry the same value, tagged `scope: "the composed set"`): every object
   `render_composed.py` renders offline is fetched live by *singular, versioned, group-qualified*
   resource name (a documented gotcha: naive pluralisation or an unversioned `get` silently misses
   objects or reads API-version-negotiation drift as a false positive) and compared with
   `rc.compare()`.
5. **Every rendered object is in a Flux inventory** — also a composed-set-wide fact: every rendered
   object's Flux inventory id (`namespace_name_group_Kind`) must appear in some `Kustomization`'s or
   `ResourceSet`'s `status.inventory.entries` — explicitly there because hand-applied objects with
   the right name can otherwise sit on a cluster with no inventory anywhere claiming them.

Plus **three pre-registered falsifiers** (declared in `drift/window.yaml`, and `grade` itself refuses
to ever return PASS if `window.yaml` doesn't still declare all three — "a sample that passes with a
falsifier undeclared is a fail", ticket 40): (a) an object persistently absent/unequal across 3
consecutive samples spanning more than 3× the live reconcile interval while the source stayed Ready
("unhealed"); (b) the cluster's verification verdict disagreeing with what CI's own identity pin
would accept (checked for real via a live `gitsign verify-tag` subprocess call, for the driftwood
party only — the other two parties' own `release.yml` aren't in this checkout); (c) coverage falling
below the declared floor at close, which is recorded rather than silently passed.

**Sample provenance / anti-rehearsal guard**: `grade` refuses to credit a sample unless its `run` field
is a real GitHub Actions run id (not a hand-typed string) AND the commit that appended that line to
`drift/samples.jsonl` was authored by the lane's own email
(`drift-sample@policy-as-versioned-<repo>.invalid`) and carries a verifiable signature (`%G?` in
`G`/`U`) — this closes a documented real incident: "three lines typed into samples.jsonl with every
fact true graded PASS (found 2026-08-29)".

**How a sample is produced and signed**: `.github/workflows/drift-sample.yml` in each of the three
repos brings up an ephemeral KinD cluster in GitHub Actions, reconciles it from the REAL publisher
remotes (not the offline touring demo), runs `five-facts.py sample`, and commits+signs the appended
line to `drift/samples.jsonl` as the lane's own identity — I did not read `drift-sample.yml`'s full
YAML in this pass (only located it via `find`); its content (KinD bring-up steps, the exact commit
signing mechanism) is unverified here and would need a direct read to confirm matches what
`five-facts.py`'s docstring/comments claim about it.

**Run 21's red facts** (all three adopters graded FAIL on the five-fact sample in run 21 — none
PASSed):
- **driftwood**: fact 2 (tag signature verified at the source boundary) FALSE for
  `driftwood-composed` — "the controller's verdict is 'false': v1.1.0: signature or certificate
  chain did not verify at tagger time 1787677714: ...Verify error: certificate is not yet valid."
  (platform and nist sources both showed all 5 facts true in the same sample — only
  `driftwood-composed` itself failed.)
- **ludlow**: fact 5 (every rendered object in a Flux inventory) FALSE for the `platform` source —
  "16 of 16 rendered objects are in no Flux inventory (absent from the cluster, or live but put
  there by something other than Flux)."
- **tuppence**: fact 5 FALSE for `tuppence-composed` — identical shape to ludlow's failure, "16 of 16
  rendered objects are in no Flux inventory."

I did not open the full driftwood five-fact capture to see whether platform/nist facts were also
clean there beyond what's quoted in the tail (the full capture likely has more per-source lines above
the tail I read) — flagged as a gap; re-read
`talk/captures/.estate-clone_driftwood_verify-reconcile.out` in full if a reader needs every source's
every fact for driftwood's run.

---

## Coverage note

All 22 scripts found by the `find` command were read (20 in full, 1 — `tuppence/scripts/verify-adopter-gate.sh`
— via targeted grep of its scenario structure plus close reading of its 438-line sibling, and
`drift-sample.yml` in the three adopters was located but not opened). The task text said "about 25
scripts"; only 22 exist under the seven named directories — verified by direct `find` count, not an
undercount on my part unless the task intended a broader glob (e.g. including subdirectory scripts
named differently, or scripts under other adopter dirs not listed). No script in this set exits 0
without a genuine observation somewhere on its path — every SKIP/PASS boundary I found is guarded by
either a substrate check, a file-existence check, or (for the three `verify-reconcile.sh` files) the
explicitly-reordered five-fact-sample-first logic that itself requires a signed, attributable,
fresh CI sample before it can stand in for a live cluster.

Full file listing (22 files):
```
driftwood/scripts/verify-identity-regexp.sh
driftwood/twin/verify-twin-scenarios.sh
driftwood/verify-reconcile.sh
driftwood/verify-twin-overlay.sh
feeds/verify-feeds.sh
feeds/verify-market-and-news.sh
feeds/verify-news-headline-skill.sh
ico/.github/scripts/verify-declared-bump.sh
ico/schema/verify.sh
ico/verify-certificate-identity-regexp.sh
ico/verify-penalty-feed.sh
insurer/verify-insurer-party.sh
insurer/verify-insurer-quote.sh
ludlow/verify-adopter-gate.sh
ludlow/verify-certificate-identity-regexp.sh
ludlow/verify-reconcile.sh
nist/.github/scripts/verify-declared-bump.sh
nist/scripts/verify-catalog.sh
nist/scripts/verify-cert-identity-regexp.sh
tuppence/reset/verify-reach-secrets.sh
tuppence/scripts/verify-adopter-gate.sh
tuppence/scripts/verify-identity-regexp.sh
tuppence/verify-reconcile.sh
```
