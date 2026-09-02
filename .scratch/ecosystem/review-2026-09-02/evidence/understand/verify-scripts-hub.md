# Map: hub `verify/` + `talk/verify-*.sh` (run-21 truth line: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 units=[...] pass=57 fail=7 skip=18 excluded=2 total=84`)

Scope covered: every script under `verify/` (16 scripts + 3 non-script support files: `_estate.py`,
`step2_reprice.py`, `step3_band.py`, plus `party.py`/`pound_seam.py`/`provenance.py`/`schedules.py`/
`feed_contract.py` read for architecture) and `talk/verify-all.sh`, `talk/verify-demo.sh`,
`talk/verify-exclusions.txt`. `talk/verify-demo.sh` is discovered by the gate only via the symlink
`verify/demo/verify-demo.sh -> ../../talk/verify-demo.sh` (confirmed: `ls -la verify/demo`).

Grading contract used everywhere in `verify/`: exit 0 = PASS (`talk/verify-all.sh` counts it),
exit 3 = SKIP (last line explains why; counts as SKIP offline, FAIL under `--live`), any other
exit (or a 300s `timeout`, exit 124) = FAIL. Full stdout+stderr of every run lands in
`talk/captures/<slug>.out`, keyed by path with `/` -> `_`. Where a per-script grade below says
"run-21", it is read from `git show origin/main:talk/captures/<slug>.out | tail -N` for that
script's capture on the hub's origin/main (run 21 is one commit ahead of the local checkout, so
these captures were read from `origin/main`, not the local tree, per the briefing).

---

## `talk/verify-all.sh` — the gate itself

**What it does, precisely** (`talk/verify-all.sh:24-81`):
1. `bash clone-estate.sh $REFRESH` assembles `.estate-clone/` from the real unit repos (network).
   Failure here is a hard exit 2 with a FAIL line, before any script runs.
2. Reads `talk/verify-exclusions.txt`: each `path | reason` line is required to have a reason and
   the path must exist on disk (`[ -e "$p" ]`), or that line itself contributes a FAIL and bumps
   `fail` — so a rotted exclusion list fails the gate even before any real script runs.
3. **Discovery**: `find .estate-clone verify -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*' | sort`.
   This is a *glob over two trees*, not a hand-maintained list — it will pick up any new
   `verify*.sh` dropped anywhere under either tree, including ones with no README, and it is
   alphabetically sorted (which is why `verify/demo/` — a symlink — sorts ahead of `verify/e2e/`,
   noted in `verify-demo.sh`'s own comment about capture staleness under a local run).
   `.estate-clone` is out of this task's scope (unit repos); this file only reports on the `verify/`
   half of that glob, but the exclusions text and the TRUTH line's unit-commit list are shared
   machinery worth flagging: two `.estate-clone` scripts are pre-excluded by
   `talk/verify-exclusions.txt` (`ico/schema/verify.sh`, `platform/feeds/verify.sh`) because they
   take positional args and are invoked by *other* verify scripts instead — matches `excluded=2` in
   the TRUTH line exactly.
4. For each discovered, non-excluded script: `timeout "$TIMEOUT" bash "$s" >"$cap" 2>&1; rc=$?`
   with `TIMEOUT` defaulting to 300s (`VERIFY_TIMEOUT` env overridable). The **entire transcript**
   (not just the verdict line) goes to the capture file; the printed table row quotes only the
   **last line**, cut to 160 chars.
5. Grading purely by `rc`: 0→PASS, 3→SKIP (or FAIL if `--live`), 124→FAIL "(timeout Ns)", anything
   else→FAIL "(exit N)". **The script's own claimed verdict text is not cross-checked against its
   exit code by verify-all.sh itself** — that cross-check (exit code vs. last-line agreement) is
   only done by `verify-e2e-step7-honesty.sh`, and *only* for the seven e2e step scripts. A script
   outside the e2e family that prints `PASS: ...` but exits 1, or prints nothing but exits 0, is
   graded solely on the exit code by `verify-all.sh` and nothing in the gate itself catches the
   mismatch.
6. **Misreporting surfaces, explicitly identified**:
   - A script that hangs past `TIMEOUT` reads as "FAIL (timeout 300s)" — indistinguishable in the
     table from an infinite loop vs. a slow-but-honest network call; only the capture disambiguates.
   - A script whose last line is a stray blank/log line (not a `PASS:`/`FAIL:`/`SKIP:` sentence)
     still gets graded purely by exit code, and the table shows that stray line as the "reason" —
     several scripts guard against this in their own wrappers (e2e steps 2/3: "if the last line
     still says nothing, quote the last line that does"), but nothing forces every script to.
   - SKIP silently becomes a pass-equivalent in the tally (`skip` is a separate bucket from
     `pass`/`fail`, but does not fail the run) unless `--live` is passed, so a laptop with no
     network can go green purely on SKIPs cascading from `clone-estate.sh`/`.venv` absence — except
     `clone-estate.sh` itself is invoked unconditionally up front and its failure is a hard exit 2,
     so a *totally* offline run never gets this far; individual scripts SKIP only on partial
     absence (no `.venv`, no `kind`, no `gh` auth, etc.).
   - The TRUTH line's `pass=/fail=/skip=/excluded=/total=` counters are simple accumulators over
     the discovered list; nothing recomputes or audits them independently inside this script (that
     independent audit is `verify-demo.sh`'s job, reading the same captures back for the deck).
7. **TRUTH line** (`talk/verify-all.sh:70-73`): `TRUTH <UTC date> run=<$GITHUB_RUN_NUMBER or "local"> hub=<short sha> units=[<unit>=<short sha>...] pass= fail= skip= excluded= total=[ live=1]`.
   The unit shas come from `git -C .estate-clone/<unit> rev-parse --short HEAD` — i.e. from
   whatever `clone-estate.sh` fetched moments earlier in *this* run, not from a stored manifest.
   `run=` is `local` unless `GITHUB_RUN_NUMBER` is set (only true inside Actions), so a locally
   run gate produces a TRUTH line that says `run=local` and is explicitly not the citable one per
   `docs/` conventions elsewhere in the estate (confirmed by cross-reading `verify-demo.sh`'s own
   distinction between a local run and `GITHUB_RUN_NUMBER` being set).
8. Exit code: `fail -eq 0` → 0, else 1. SKIP and EXCLUDED never flip this bit (offline mode).

**`talk/verify-exclusions.txt` contents** (both lines confirmed to exist on disk, satisfying the
gate's own self-check):
```
.estate-clone/ico/schema/verify.sh | takes a version-dir argument; run twice by .estate-clone/ico/verify-penalty-feed.sh (v1, v2)
.estate-clone/platform/feeds/verify.sh | takes feed/version/file arguments; run by .estate-clone/platform/honesty/verify-honesty.sh
```
Both entries are `.estate-clone/` scripts, out of this file's `verify/` scope, but they are the
entirety of `excluded=2` in the TRUTH line, so no `verify/`-tree script is excluded.

---

## `verify/_estate.py` — shared constant, not a check

Not a verify script; every other file in `verify/` imports `ESTATE` from it.
`ESTATE = <verify/>/../.estate-clone`, i.e. `<repo-root>/.estate-clone`. One source of truth for
"where is the disposable local checkout of the six/eight unit repos" (`verify/_estate.py:1-14`).
`twin/` keeps its own separate copy deliberately (comment: "twin/ and verify/ do not depend on
each other").

---

## `verify/e2e/lib.sh` — shared harness, sourced not run

Defines the NORTH-STAR §4 step contract (`verify/e2e/lib.sh:1-27`): last line is exactly one of
`PASS:`/`FAIL:`/`SKIP:` (via `flat()`, which flattens embedded newlines/tabs so a traceback can
never push the verdict off the last line), matching exit 0/1/3 via `pass`/`fail`/`skip` helpers.
`cluster_up`/`cluster_down` bring up/tear down an ephemeral KinD cluster named `pav-e2e` — never
one of the real per-adopter clusters (`driftwood`/`tuppence`/`ludlow`) — and register a `trap
cluster_down EXIT`, so a step that calls `cluster_up` self-destructs its cluster on any exit path.
No step in this repo (steps 1-7 as read) actually calls `cluster_up`/`cluster_down` — step 4 reads
a *standing* `kind-driftwood` cluster instead, so this pair currently exists for a future
scheduled-workflow consumer (ticket 40 per `verify/e2e/README.md:29`), not for anything invoked
by the seven scripts themselves.

## `verify/e2e/README.md` — the seven-step contract, self-declared limits

Explicitly states (not just implied by code) the two invariants: a step never turns absence into a
pass, and never asserts the old shape to stay green. It also names the ceiling on step 7 in its own
words: step 7 checks *reporting* honesty (hedge words on a PASS line, exit/last-line mismatch, a
"could not look" buried mid-transcript on an exit-0 run), and says outright that a step which
"simply asserts something FALSE" with no hedge word in it is invisible to step 7 — citing a named
past incident ("the OpenBao claim that stood green for 27 days had no hedge word in it"). This is
the review's own documented ceiling, not something this review is discovering.

---

## `verify/e2e/verify-e2e-step1-regulator-publishes.sh`

- **Claims**: ico's newest local `penalty-schema` envelope validates against the feed schema and
  its version is a gitsign tag on ico's real GitHub remote.
- **Mechanism**: thin wrapper around `verify/feed-contract/feed_contract.py newest ico
  penalty-schema` (a live network call: `git ls-remote --tags <real remote>`).
- **Observation vs. simulation**: real observation against the real ico remote, not a fixture —
  no throwaway copy involved.
- **Offline/live**: needs network (git ls-remote) to reach PASS/FAIL; SKIPs if `jsonschema`/`pyyaml`
  missing or `.estate-clone/ico` absent.
- **Absence handling**: SKIPs by design rather than passing when it cannot look.
- **Run-21 grade: PASS** — `git show origin/main:talk/captures/verify_e2e_verify-e2e-step1-regulator-publishes.out | tail -3` ends
  `PASS: ico's newest penalty-schema envelope validates and its tag is on the real remote`.

## `verify/e2e/verify-e2e-step2-renovate-pins-and-reprices.sh` + `step2_reprice.py`

- **Claims**: bumping one pinned feed version in an adopter's own `party.yaml` (the single edit a
  merged Renovate PR makes) changes that adopter's `prices[]` **number**, through composition.
- **Observation vs. simulation — explicit**: this is a **simulation on a throwaway copy**, not an
  observation of a real Renovate PR. `step2_reprice.py` copies the *whole committed tree* of an
  adopter (minus `.git`/`.work`/`__pycache__`) into a `tempfile.TemporaryDirectory()`, composes it
  once, hand-edits the copy's `party.yaml` pin, composes again, diffs `prices[]`. Nothing real is
  touched; the copy is discarded (`step2_reprice.py:8-13,151-192`). It explicitly checks the
  **number** moved, not just that the document differs, because "the entry always records the new
  version string" so a document diff alone proves nothing (`step2_reprice.py:181-188`) — a real,
  named self-critique of what a weaker check would have missed.
  - This is distinct from `verify/renovate/verify-renovate-merged-feed-pr.sh` below, which grades
    whether this event has *actually happened* on a real adopter's real main — the README explains
    the split explicitly ("The e2e step-2 script proves the MECHANISM offline ... This check grades
    whether step 2 has HAPPENED").
- **Offline**: fully, no network, no git writes.
- **Substrate**: `.estate-clone` on disk plus a python interpreter with `pyyaml`; a `--estate`
  override lets it be pointed at a fixture instead (used for smoke-testing, "the gate never passes
  this").
- **Absence handling**: SKIPs (3) if no adopter pins a "priceable" feed (`penalty-schema` or
  `threat-register` only — the two names composition prices today) with a newer version present
  locally, or if no bump on disk actually moves the price (a bump that reprices identically is
  explicitly *not* treated as the observed fact and the loop keeps looking across every
  adopter/edge pair rather than stopping at the first).
- **Run-21 grade: PASS** — capture tail shows a real before/after price diff for `tuppence`'s
  `threat-register` v1→v2 bump (222,574.31 → 326,139.13 GBP), ending
  `PASS: a merged pin bump (threat-register v1 -> v2) re-prices tuppence's prices[] through composition (222,574.31 -> 326,139.13), offline, with no repo touched`.

## `verify/e2e/verify-e2e-step3-price-crosses-band-pr-opens.sh` + `step3_band.py`

- **Claims**: a residual crossing the adopter's *own signed* appetite band selects a different
  tier through the adopter's own published selection-policy package (cross-checked against
  `platform/graded/cage.py`), and `tier_pr.py run --dry-run` would open a PR editing the tier
  **declaration** (`posture.acme.io/tier` on the governed Namespace manifest) — never the pod
  label, which the declaration produces and which gets clobbered at every admission.
- **Observation vs. simulation — explicit and self-corrected**: the two residuals compared
  (`under = band*0.5`, then stepped up ×1.02 until the tier flips, capped at 4000 iterations) are
  **synthetic**, placed either side of the band *by construction* — not the adopter's real priced
  position. The script carries an inline 2026-08-29 review note (`step3_band.py:276-283`) recording
  that the wording used to say "a residual crossing {org}'s own appetite band", which a reader takes
  as the adopter's *actual* position crossing, and that this was false; the PASS line now says
  "SYNTHETIC residual ... not {org}'s real priced position" explicitly. The dry run itself operates
  on manifests copied into a `tempfile.TemporaryDirectory()` that is **not a git repository at
  all** (`step3_band.py:212-229`), so `tier_pr.py`'s own `--dry-run` flag being ignored could not
  succeed even by accident — no `git`/`gh` call could land anywhere real.
  What is real: the selection engine itself (imported live from the adopter's own
  `selection-policy/selection_policy.py`), the band read from the adopter's own signed
  `party.yaml` `appetite.tolerance` (never a platform fixture — ADR-0021), and the governed
  Namespace manifest found by a **second, independent implementation** of the label search
  `tier_pr.py` itself uses (`governed_namespace_manifests()`, reading only `git ls-files` committed
  YAML — a `.work/` scratch file cannot satisfy it).
- **Offline**: fully.
- **Absence handling**: SKIPs if no adopter publishes a `selection-policy` package with a
  `VERSION` file (names ticket 25 as owner), or the estate/interpreter is missing.
- **Run-21 grade: PASS** — capture ends
  `PASS: a SYNTHETIC residual placed either side of driftwood's own signed appetite band of 40,000 GBP (20,000.00 -> 58,269.23 GBP, not driftwood's real priced position) selects baseline -> restricted through driftwood's own selection-policy package 1.0.0 ... (python half; the tier landing in force is step 4)`.
  The wrapper appends "(python half; the tier landing in force is step 4)" itself
  (`verify-e2e-step3-*.sh:26`), so even a clean PASS is annotated with what it does *not* cover.

## `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh`

- **Claims (on a real standing cluster, when reachable)**: seven hard facts A–G about the real
  `kind-driftwood` cluster (GitRepository Ready at the pinned commit; Kustomization applied the same
  revision; governed Namespace is in Flux's own inventory; the served cage policy for the
  currently-composed version is live and reads `namespaceObject`/knows the `isolated` rung; the
  Namespace declares a tier on the ladder; the adopter's own `deploy/pod.yaml`-declared workload is
  Running and wears the tier's label/PriorityClass) plus two named could-not-looks (H: source is
  the real signed remote vs. the offline seed — waits on ticket 40; G′: the "synchronize gap" where
  a pod admitted before a tier moved still wears the old label, deliberately graded SKIP not FAIL).
- **When no cluster is reachable — the substitute path, `grade_lane_sample()`** (lines 46-76 in
  the script): rather than SKIP outright (as it used to, per the comment citing
  "REVIEW-2026-08-31, M7"), it shells out to `$ESTATE/$ADOPTER/drift/five-facts.py grade` and
  re-grades *that* — a scheduled, signed, lane-committed sample from an **ephemeral** cluster the
  adopter's own `.github/workflows/drift-sample.yml` reconciles from the **real remotes** on its
  own clock (`drift/samples.jsonl`). The script is explicit that this substitution only stands
  because `five-facts.py` "refuses a hand-typed or unsigned sample" — the substitute grade is
  still an observation, not a rehearsal, but it is an observation of a **different, ephemeral**
  cluster's run at some earlier timestamp, not of "this instant".
- **Run-21 grade: FAIL, via the substitute path.** This runner had no `kubectl` (or no reachable
  KinD cluster; the capture doesn't disambiguate which of the five preconditions on lines 70-75
  tripped first, only that it fell to `grade_lane_sample`). The graded lane sample
  (`five-facts.py grade`, timestamp `2026-09-01T21:07:22Z`, on ephemeral cluster
  `dsample-33558850420`) reports `fact_2_tag_signature_verified_at_the_source_boundary` **FALSE**
  for `driftwood-composed`: `v1.1.0: signature or certificate chain did not verify at tagger time
  1787677714: ... certificate is not yet valid`. All other facts (1,3,4,5) for driftwood-composed
  and all five facts for `nist` and `platform` are `true`. The script's own last line:
  `FAIL: the scheduled lane sample observes a step-4 fact false: FAIL: a fact of the five-fact sample was observed false`.
  This is a genuinely observed FALSE claim (a cert-not-yet-valid error, consistent with a clock-skew
  or timestamp issue at signing time, not a fabricated defect) — one of the 7 in `fail=7`.
- **What this step does and does not prove, precisely**: it never fabricates a green when the real
  cluster is absent (SKIP path still exists for genuinely missing `drift/five-facts.py` or
  `pyyaml`); but its FAIL/PASS verdict, whichever runner path fires, is about a *composed set built
  from signed sources on a cluster that reconciled the real remotes* — either the standing
  `kind-driftwood` right now, or an ephemeral sample cluster at an earlier timestamp within
  `FIVE_FACT_MAX_AGE_HOURS` (default 48h). It is never a rehearsal against a fixture.

## `verify/e2e/verify-e2e-step5-twin-forecasts.sh`

- **Claims**: whether the twin's five step-5 prerequisites exist by path (adopter's own overlay +
  vendored world layer; `forward-intel/v1/feed.json`; ≥6 standing scenarios under the overlay path
  `twin/orgs/<adopter>/scenarios` — falling back to `twin/scenarios` only for *reporting* which path
  actually has files, since only the overlay path is ever loaded by `twin.Overlay.load`; the
  pin→scenario table plus `twin/feed_signal.py`; `verify/twin-evals/verify-twin-evals.sh` itself
  existing) and, if all five are present, **runs** `verify-twin-evals.sh` and reports its exit code
  as its own PASS/SKIP/FAIL.
- **Absence handling — a fixed, named bug**: the script's own comment records that it "used to be
  an unconditional `skip`, which made step 5 structurally incapable of two of its three verdicts:
  it read could-not-look on the deck even with every artefact present and verify-twin-evals.sh
  green (found 2026-08-29)" — i.e. before this fix the step could never actually PASS or FAIL, only
  ever SKIP, regardless of ground truth. Now fixed to delegate.
- **Offline**: fully (delegates to `verify-twin-evals.sh`, itself offline — see below).
- **Run-21 grade: PASS** — capture ends
  `PASS: the twin's overlay, feed, 6 scenarios and signal lookup are all present, and its own evals scored them: PASS: 7 skill metrics ...`.

## `verify/e2e/verify-e2e-step6-provenance.sh`

Three distinct parts, graded together:
1. **OFFLINE, reachability** — re-grades `feed_contract.py check`'s own output for step 6's
   narrower question (every published artefact resolves to a real tag, or is honestly queued). A
   FAIL there is a hard FAIL here; any other SKIP is surfaced as an "unlooked" item.
2. **OFFLINE, static regexp shape** — for every unit's `release.yml`, extracts
   `EXPECTED_IDENTITY_REGEXP`/`EXPECTED_ISSUER` **by `sed`, not by parsing the workflow YAML
   semantically** (`sed -nE 's/^ *EXPECTED_IDENTITY_REGEXP: *//p'`), derives the unit's "own"
   org/repo slug from `git remote get-url origin` on the actual `.estate-clone/<unit>` checkout
   (never from a hardcoded list in this script), and asserts the regexp is anchored (`^...$`),
   escapes its dots, matches the unit's own real `cut-release.yml@refs/heads/main` identity string,
   and rejects five constructed foreign/malformed identities (wrong org, wrong workflow file,
   `https://evil.com/<real-id>`, a suffix-appended domain, and a `release/x.y.x` branch-glob abuse)
   via `grep -qE` — the script notes this is a faithful stand-in for gitsign's RE2 matcher only
   because these patterns use nothing beyond anchors/escaped-dots/classes/alternation.
3. **LIVE, Rekor** — for every unit with an actual signed tag, runs the real `gitsign
   verify-tag --certificate-identity-regexp=<that unit's own regexp>` and requires both "Good
   signature from" and "Validated Rekor entry: true" in the output; connection-refused/timeout
   errors are named as "unlooked", never as PASS or FAIL.
- **Absence handling**: SKIP if `jsonschema`/`pyyaml` missing (part 1), or `gitsign` absent (all of
  part 3 becomes "unlooked", not skipped-silently — it is still reported and still prevents an
  unqualified PASS unless everything else that *can* be checked is clean, per lines 110-113).
- **Run-21 grade: PASS** — `7 of 8 anchored identity regexps matched a real Fulcio cert subject
  with its Rekor entry validated, and feeds have no signed tag yet` (feeds is honestly queued, not
  a failure).

## `verify/e2e/verify-e2e-step7-honesty.sh`

- **What it is**: a roll-up of *reporting honesty*, not of results — explicitly not a second grade
  of truth. It runs steps 1–6 fresh (each under its own 300s `timeout`), and marks a step
  "UNGRADED" (which flips step 7's own exit to 1) only when: it hangs; its exit code and last line
  disagree (e.g. exit 0 under a non-`PASS:` line); it prints `PASS:` while that same line contains a
  hedge word from `HEDGE` (`could not|couldn.t|cannot|...|no substrate`, deliberately narrow — an
  *observed* absence like "queued" or "handed to another step" does not trip it); or it exits 0 while
  its full transcript (not just the verdict line) contains `NOT_OBSERVED` phrases
  (`NOT OBSERVED|could not look|was not observed`) anywhere. **It never counts a step's own
  reported FAIL or SKIP as a step-7 failure** — that would double-count the same red in the TRUTH
  line's tally.
- **What it explicitly cannot catch** (stated in both its own header comment and the README): a
  step that asserts something **false with no hedge word in it** — cited by name, "the OpenBao claim
  that stood green for 27 days had no hedge word in it." Only a step's own fact-observing code can
  catch that; step 7's nets are purely textual.
- **Selfcheck, and a fixed regression**: `bash verify-e2e-step7-honesty.sh selfcheck` plants six
  fixture step scripts in a temp dir (hedged PASS, exit/last-line mismatch, a non-conforming
  script, a missing step 4, an honest SKIP, an honest FAIL, plus a "buried confession" — exit 0
  whose transcript confesses `SKIP (live tail)` mid-run before printing a clean `PASS:` last line)
  and asserts all four dishonest shapes are caught while the two honest ones pass through. The
  script's own comment records that **nothing called this selfcheck before ticket work fixed it** —
  "the gate calls this script with no argument and the only other references were a comment and the
  README (review, 2026-08-28)" — so it is now run unconditionally, once, whenever the script is
  invoked with no `E2E_STEPS_DIR` override, and a failing selfcheck itself fails step 7
  (`verify-e2e-step7-honesty.sh:68-71`).
- **Run-21 grade: PASS** (`selfwhy: "steps 1-6 each report one honest verdict"`), even though step 4
  itself reported FAIL — because step 7's job is only to confirm step 4's FAIL was *honestly
  reported* (matching exit/last-line, no hedge on a claimed PASS, no buried confession), which it
  was. Verdicts recorded: `PASS PASS PASS FAIL PASS PASS`. This is the precise mechanism by which
  the gate's TRUTH line can show `fail=7` (step 4 among them) while step 7 itself, part of that
  same tally, is green — the two are asking different questions and both answers are correct.

---

## `verify/feed-contract/verify-feed-contract.sh` + `feed_contract.py`

- **Claims** (ADR-0019): every published feed under `.estate-clone/` validates against the ONE
  envelope schema (`platform/feeds/schema.json`) plus its own `payload_schema`; every adopter's
  `inherits[]` pin resolves to a publisher's `publishes[]` record and to a **tag that exists** on
  the publisher's real remote. The PASS line is explicit that this is "existence, not signature" —
  the actual gitsign verification of that tag is step 6's and `platform/verify-source-verification.sh`'s
  job, named by cross-reference so a reader does not conflate the two.
- **Mechanism**: `feed_contract.py check` walks every `party.yaml` under `.estate-clone`, validates
  every `v*/feed.json` envelope + payload against jsonschema, checks `rule.yaml`/`bump.yaml`
  sidecars exist and `bump.yaml`'s `bump` is one of `major|minor|patch|none`, and for every
  `inherits[]` edge calls `git ls-remote --tags <REMOTE.format(p=party)>` (real network, 60s
  timeout, cached per-run in `_TAGS`) to look for a matching tag — a bare-major pin (`v1`) matches
  any `v1.x.y` tag; a full-semver pin must match exactly. A pin whose tag is not yet cut but whose
  envelope exists **locally** at the right version is graded SKIP "waiting for tag ... (cut by
  cut-release.yml after merge)" rather than FAIL — a genuinely-queued, not-yet-real state.
- **A named absence-catching fix in the code itself**: `run()` iterates every party that has
  `inherits[]` at all, not only parties whose `roles` include `adopter` — the comment
  (`feed_contract.py:236-240`) records that the insurer's roles are `[publisher, insurer]`, so its
  four pins were previously never resolved by anything: "65 PASS/SKIP lines went by without one of
  them naming an insurer pin (found 2026-08-29)." It also explicitly refuses an empty estate:
  `for k, n in SEEN.items(): if not n: out("FAIL", f"no {k} observed under {estate}: absence is not a pass")`
  where `SEEN` tracks publishers/adopters/envelopes actually visited.
- **`selfcheck`**: plants a two-party fixture estate in a temp dir with the remote lookup **stubbed**
  (`_TAGS` set by hand, not a real network call) and asserts: exactly 3 FAILs and at least one SKIP
  on a constructed set of six pin shapes (bare-major hit, `policy/vX.Y.Z` hit, no-tag-no-local-file,
  local-only/queued, nowhere, no-matching-record); bare-major resolves to the *highest* matching
  tag; an empty estate is entirely FAIL; a bad envelope (bad `published_at`, extra `signature` key)
  is caught; an unreachable remote (`_TAGS = {"ico": None}`) yields SKIP, never PASS.
- **Offline vs. live**: the schema/sidecar checks are pure filesystem reads; the tag-existence
  checks are real `git ls-remote` network calls to the eight real GitHub org repos.
- **Run-21 grade: PASS** — `every published feed is one envelope, and every subscription names a
  tag that exists on the publisher's real remote (existence, not signature -- step 6 checks the
  signature)`.

---

## `verify/party/verify-party.sh` + `party.py` (+ `roles.json`)

- **Claims**: `roles:` in each party's `party.yaml` is not free-text — every declared role
  (`publisher`, `risk-bearer`, `adopter`; `platform`/`insurer` declared-only) must be backed by
  concrete filesystem evidence (table in `verify/party/README.md:11-15`): risk-bearer needs an
  entry in `platform/risk/appetite.json`; publisher needs a `*.sig` file, a `*VERSION*.json`, or a
  `party.yaml` with a non-empty `publishes[]`; adopter needs a reference (repo-naming or in-repo
  path) to another party under its own directory. **Institutions** (driftwood/tuppence/ludlow) are
  *derived* as risk-bearer+adopter minus any party carrying the `platform` role — not
  hand-listed — specifically so `platform` (itself risk-bearer+adopter, per
  `platform/honesty/reflexive.py`) is not silently counted as a fourth institution, and the
  derivation rule was changed from "not publisher" to "not platform" when driftwood started
  publishing its own forward-intel feed (README, `verify/party/README.md:17-23`).
- **Mechanism**: `party.py selfcheck` — the wrapper shells out to Python's own selfcheck rather
  than running `party.py check` directly against `.estate-clone` (it *does* clone-estate.sh first
  if `.estate-clone/platform` is absent, but the actual assertion run is the selfcheck, which per
  its own docstring is offline stdlib+PyYAML, reading the real cloned estate on disk to prove all
  eight parties' declared roles are backed, AND plants each of the three violation shapes
  (risk-bearer with no appetite entry, publisher shipping nothing signed, adopter pinning nothing)
  to prove the guard actually refuses them.
- **Offline**: yes — pure filesystem/YAML parse of `.estate-clone`, no network beyond the
  `clone-estate.sh` precondition.
- **Run-21 grade: PASS** (last lines confirm: "all eight parties ... declare roles the filesystem
  actually backs up, all five roles carry an evidence check, and verify/party/roles.json is
  asserted to mirror each party's OWN signed party.yaml rather than standing in for it").

---

## `verify/pound-seam/verify-pound-seam.sh` + `pound_seam.py`

- **Claims** (ticket 25 / ADR-0020 / ADR-0021), ten distinct checks per adopter's
  `composed/evidence.json` (full list in the script's docstring, `pound_seam.py:3-31`): one
  perspective/one currency per price entry; `per_customer` derived correctly or null; exactly one
  `source: twin` entry iff the adopter publishes forward-intel; the ico "regime" entry's `holes[]`
  sum to its total; no cross-perspective/cross-currency sum anywhere (named as "the live bug
  ADR-0020 was written against"); appetite is read only from the adopter's own signed `party.yaml`
  (never a retired `platform/risk/appetite.json`); every named selection-policy version matches the
  adopter's actual published `VERSION`; the recorded curve hash matches what the adopter's own
  selection-policy package computes; the adopter's own package and `platform/graded/cage.py`
  **agree** on tier selection at every band boundary and floor (the "two-implementations guard");
  the FX bridge resolves through the FX publisher's own converter and refuses an unpublished date
  as a missing instrument.
- **Absence handling — explicitly documented as a feature, not a gap**: "a real absence (an
  adopter that publishes no forward-intel feed yet) prints as a NAMED pass, never a silent one" —
  confirmed in run-21's own capture: `PASS: tuppence: selects no tier through a published selection
  policy yet (named absence: no forward-intel feed)`.
- **`selfcheck`**: plants defects and proves each refusal bites (checks 8/9, the two-implementation
  cross-check, are explicitly *not* in the selfcheck fixture — both read the real estate instead,
  and were separately proven to bite "by planting a divergence in driftwood's package and watching
  the check refuse it," per the module docstring — meaning that particular proof is not re-run on
  every gate invocation, only was demonstrated once during development).
- **Offline**: fully — reads committed files only (`.estate-clone`), no network.
- **Run-21 grade: PASS** — "every price names its perspective, currency, source and per-customer
  share; no sum crosses either; and wherever a party publishes both a selection-policy package and
  composed evidence, the two selection engines agree."

---

## `verify/proportionality/verify-proportionality.sh` (+ `render.py`, fixtures)

- **Claims** ("THE MONEY SHOT"): the *same* Kyverno control body + *same* FAIR scenario, evaluated
  against two institutions' different risk-appetite bands, produces divergent verdicts —
  **Audit** for driftwood, **Deny** for ludlow — purely because the band differs, not because the
  control or the priced risk differs.
- **Mechanism, staged**: (0) `platform/risk/enforce.py selfcheck`; (1) `enforce.py decide` for
  both orgs against the one shared `scenarios/encrypt-at-rest.json`, asserting the exact verdict
  strings; (2) asserts `risk_bought` (the £ figure) is byte-for-byte identical across both orgs
  (`abs(a-b) < 1e-6`) and straddles the two bands (`rb <= driftwood_band`, `rb > ludlow_band`),
  and that the two bands actually differ; (3) `render.py --check` asserts the **committed**
  rendered policy YAMLs are exactly what `enforce.py`'s current £ would render (drift guard), then
  a `diff` between the two org's rendered YAMLs is capped at ≤6 changed lines — i.e. only
  `validationActions` + the two org-label lines may differ, proving the bodies are otherwise
  byte-identical; (4) optionally runs the real `kyverno test` CLI against `tests/encrypt-at-rest/`
  if present (skipped, printed, not faked, if `kyverno` binary absent); (5) an **optional live
  tail** — for each of driftwood/ludlow, if `kubectl --context kind-<org>` is reachable AND the
  Kyverno CRDs are installed, does a real `kubectl apply --dry-run=server` of the rendered policy;
  otherwise prints a "skipping" note and the offline proof is declared to stand.
- **No SKIP exit path**: unlike almost every other script in this family, this one is `set -euo
  pipefail` with no `exit 3` anywhere — every failure mode is `fail()` (exit 1), and the live tail's
  absence is only ever a printed note, never a SKIP exit. A completely offline run either passes
  (with a printed "offline proof stands" note) or fails outright; it cannot itself register a
  gate-level SKIP the way, e.g., `feed_contract.py` can.
- **Offline core**: python3 (+ `platform/risk/enforce.py`/`fair.py`, real code reused, not
  reimplemented); `kyverno` binary optional for step 4; cluster reachability optional for step 5.
- **Run-21 grade: PASS** — `same control, same £ (risk_bought £21107) — Audit in driftwood, Deny in
  ludlow. Proportionality by comparison.` The capture's step 5 line: "live dry-run tail skipped (no
  cluster with Kyverno CRDs reachable) — offline proof stands," confirming this particular run had
  no live-cluster leg exercised.

---

## `verify/provenance/verify-provenance.sh` (+ `provenance.py`)

- **Claims** (the auditor's closing beat, spec user story 5 / ticket 24): every actor — commit,
  workload, human, device — is attestable to one root, walking feed→scenario→PR→review→merge→
  release then the runtime SVIDs that release resolves to, converging on the same version
  (`v2.0.0` in the fixture chain) a compliant workload's SPIFFE SVID actually carries.
- **Mechanism, five staged claims**:
  1. `provenance.py selfcheck` — the whole chain's own asserts, reusing `wargamer.py` (which itself
     reuses `fair`/`enforce`/`tcor`) and reading the **committed SPIRE manifests** for the runtime
     identities — nothing here is a fixture invented for this check.
  2. **One real cryptographic check, offline**: verifies the ed25519 detached signature on
     `wargamer/fixtures/threat-register/v3/register.json` against
     `platform/feeds/keys/feeds-signing-key.pub.pem` using real `openssl pkeyutl -verify`, then
     **mutates one field** of the feed JSON in a temp file and asserts the *same* signature file no
     longer verifies against the mutated payload — i.e. it proves the signature is load-bearing, not
     decorative, by constructing and refuting a forgery in the same run.
  3. **Optional live Rekor tail**: if `rekor-cli` is present, searches Rekor for this repo's own
     HEAD commit sha (which is very unlikely to be gitsign-signed in this hub repo itself, so a
     "not in Rekor" note here is expected and non-fatal — only a hard error would fail); otherwise
     falls back through `gitsign` presence to a purely offline note.
  4. **Optional live SPIRE tail**: if `kubectl` can reach `kind-driftwood`'s `spire-server`
     StatefulSet, runs `spire-server entry show` inside the pod and greps for
     `spiffe://acme.internal`; otherwise an offline note stands in.
  5. `provenance.py walk` — prints the human-readable narration (not itself asserted against
     anything; this is what "the auditor reads").
- **No SKIP path**: like proportionality, `set -euo pipefail`, `fail()`-only, no `exit 3` — the live
  tails degrade to notes, never to a gate-visible SKIP.
- **Offline core**: python3 (+PyYAML) for steps 1/5, `openssl` for the one real crypto check in
  step 2 (skipped-with-note if absent — "offline crypto proof of the feed link skipped").
- **Run-21 grade: PASS** (final lines confirm the whole-chain claim; the capture doesn't show
  whether the live Rekor/SPIRE tails fired or fell back to notes in this particular run — worth a
  follow-up read of the full capture body if that distinction matters to the audit).

---

## `verify/renovate/verify-renovate-merged-feed-pr.sh`

- **Claims**: distinct from the e2e step-2 *mechanism* proof — this grades whether the real-world
  **event** has happened: a Renovate-authored feed-pin bump PR, actually merged by a human, on any
  of driftwood/tuppence/ludlow's real `main`, that moved `party.yaml`'s `inherits[]` entry and
  `composed/` **together in one merge**.
- **Mechanism**: for each adopter with a real git remote, `git fetch origin main` (real network;
  SKIPs if unreachable) then walks `git log origin/main --merges` for merge-commit subjects
  matching `Merge pull request #NNN from .../renovate/...`. For each match: diffs the merge commit
  against its first parent, requires the diff to touch exactly `party.yaml` with an added/removed
  `kind: feed ... version:` line, requires the **branch side's own commits** (`git log
  --no-merges m^1..m --format=%an`) to be bot-authored (`renovate|github-actions|\[bot\]` regex) —
  "or this is a hand-made PR that only borrowed the branch name -- exactly what M8 said always
  happened" — then hard-FAILs if the **merger** (not the branch author) is also bot-authored ("the
  reviewed PR is the unit of adoption"), and hard-FAILs if `composed/` was not touched in the same
  merge (pin moved without re-render).
- **No GitHub API, no token, no rate limit** — reads only committed git history the same way Flux
  itself would.
- **Absence handling**: SKIP if no adopter clone is present, or (the terminal fallback) if no
  matching merged Renovate feed-pin PR exists yet anywhere — explicitly distinguishing "waiting on
  ticket 61's driftwood branch landing and the next feed release" from a hard failure.
- **Run-21 grade: PASS** — `driftwood #20: Renovate raised threat-register v1 -> v2, Chris
  Nesbitt-Smith merged it, and party.yaml and composed/ moved together -- step 2 happened for
  real.` (Note: the human merger named in the capture is the account this session runs as —
  `chris@cns.me.uk`/Chris Nesbitt-Smith — consistent with the git log recent-commits context;
  flagged only as a fact worth an auditor's attention, not evaluated further here.)

---

## `verify/schedules/verify-schedules.sh` (+ `schedules.py`)

- **Claims** (ADR-0024, superseding ADR-0015 point 5), four questions in order:
  1. every unit carries the clocks its own party artefact/contents actually require (a publisher
     needs `fetch.yml`; an adopter needs `renovate-run.yml` + `propose-tier.yml`; anything with a
     `twin/` directory needs `twin-sweep.yml`; the hub needs `truth.yml`) — **derived from what the
     repository actually is**, never a hardcoded per-unit list (`required_clocks()`,
     `schedules.py:108-134`);
  2. every *scheduled* job (`on: schedule:`) that pushes the default branch is **caged**: it may
     only stage paths inside `ALLOW_LIST = (talk/truth.log, drift/samples.jsonl, talk/captures,
     observations)`, must declare that same list in its own `env:` `OBSERVATION_LANE` (so the
     workflow and the checker cannot silently drift apart), and must carry a step whose *shell*
     (not just its *name*) does the cage's actual work — reset the index, stage only the declared
     lane, diff the staged set against that list, `exit 1` on anything else (`CAGE_SHELL_LANE`) —
     or, for a job that pushes nothing to `main` at all (a proposer that opens a PR instead), the
     "clean tree" shape (`CAGE_SHELL_CLEAN`). The workflow YAML is **parsed with `yaml.safe_load`**,
     not grepped, for job/`on:`/`env:` structure, though the inline shell inside each `run:` string
     is then read with regexes (`_PUSH`, `_ADD`, `_STAGES_EVERYTHING`, `_FOR`/`_expand` for
     `for p in ${VAR}` loop-variable binding) — the module's own comment names this ceiling
     explicitly: "a push from inside a called program ... or from a `uses:` action is invisible to
     it," which is *why* the capability check (`contents: write` with no cage step at all) is
     treated as the load-bearing half, and why a clean PASS line is worded "no shell step in this
     job stages a declaration" rather than a flat "caged." A `uses:` action under `contents: write`
     that is not on a short allow-list of provably-inert actions (`actions/checkout`,
     `actions/setup-*`, `actions/cache`, `actions/{up,down}load-artifact`) is itself a named fault —
     "this checker cannot read what that action writes and cannot grade it caged" — never a silent
     pass;
  3. no scheduled job may mint or merge a signed artefact (`git tag`, `gh release create/upload`,
     `gh pr merge`, or a raw POST to `/git/refs/tags` — regex `_SIGNED_ARTEFACT`);
  4. **live, only where GitHub is reachable**: for each required, present workflow, reads the
     **remote** copy on `<org>/<unit>@main` (not the local clone) via `gh api
     repos/.../contents/.github/workflows/<file> --jq .content` (base64-decoded, re-parsed), a
     tri-state result (`absent`/`unparsed`/`timed`/`untimed`) that specifically tells apart "not
     merged yet" from "was removed from main" (a fixed bug: these two used to collapse into the
     same SKIP reason, "with a reason naming a merge that had already happened"); if the remote
     schedule is live, `gh run list --repo <remote> --workflow <file> --event schedule --limit 1`
     for the most recent scheduled run, checked both for **age** (`PERIOD_HOURS = 48`, a declared
     24h period plus a day of GitHub-scheduling slack) and for **conclusion** (a run that died in
     checkout/gitsign-install/cage-step used to read as a healthy clock purely on recency — fixed,
     cited by name: "live, 2026-08-28: 'hub/truth.yml: last scheduled run 2h ago (failure)' graded
     PASS" — now `conclusion != "success"` is a FAIL unless the workflow is `truth.yml`, which is
     the one documented exception because it deliberately `exit 1`s whenever the gate itself is
     red, its normal/expected failure mode); a clock that landed on `main` too recently to have hit
     its first scheduled slot yet is SKIPped, not FAILed (`landed_hours_ago()`, walking
     `--first-parent` on the remote branch, not the file's own commit date, because a branch
     written 64h earlier and merged same-afternoon would otherwise be called "overdue on the day it
     arrived" — a cited, dated incident from 2026-08-31).
     Also, if a `.github/rulesets/` directory exists locally, a **server-side** ruleset check
     (`ruleset_state()`, `gh api repos/<remote>/rulesets`) — but this is explicitly graded
     "unavailable" (SKIP, not FAIL) whenever the target repo is public, because GitHub only allows a
     push ruleset with `file_path_restriction` on private/internal repos, so the module states
     outright: "the server-side leg of ADR-0024 cannot be applied here at all," and "the client-side
     cage step and this checker ARE the whole cage today."
- **What it can and cannot see from inside CI, specifically**: parts 1–3 (clock existence, cage
  shape, minting capability) read only files already present in the **local `.estate-clone`
  checkout** — no network needed, always fully exercised regardless of connectivity (the script's
  own header: "Offline the first three checks still run in full: absence of a network is never a
  pass"). Part 4 (live) needs a `gh` session that is genuinely authenticated (`gh auth status`
  succeeding) **and** has read access to `gh run list`/`gh api contents` on every one of the 6–8
  separate unit-org repos plus the hub — a single CI runner's default `GITHUB_TOKEN` is normally
  scoped to its own repo only, so unless a cross-org PAT/App token is configured for this job, the
  live half is structurally unreachable from inside a normal Actions run on any *one* of these
  repos, and every live line falls to the per-unit SKIP path ("GitHub unreachable ... cannot look
  at whether this clock ran inside its period"). This is exactly what run-21's capture shows.
- **`selfcheck`**: an extensive fixture suite (`schedules.py:665-878`) planting a correctly-caged
  job, a step *named* "the observation cage" whose shell does nothing (a fixed bug — "until
  2026-08-29 the name alone satisfied the check"), five historically-passing-but-wrong shapes
  (`git add -A` with no operand, `git commit -am`, `contents: write`+no cage step, an opaque
  `uses:` action under write, and the negative control of a job *without* write permission), a
  declaration staged in the same cage step that pushes main, a naked push to main declaring no
  lane at all, a proposer branch (no cage needed — never touches main), a "sideways" push to a
  non-`main` branch with no PR (still caged — the observations branch included), each
  signed-artefact-minting shell shape, and confirms an unscheduled `workflow_dispatch` job (like
  `cut-release.yml` itself) is not judged by this checker at all (`scheduled_jobs()` filters on
  `crons(doc)` being non-empty).
- **Run-21 grade: SKIP, but the capture itself is anomalous** — read in full
  (`git show origin/main:talk/captures/verify_schedules_verify-schedules.out`, 50 lines total),
  every line is `schedules.py check`'s own raw `PASS:`/`SKIP:` output (per-unit clock-existence and
  cage checks all PASS; every live per-clock check SKIPs on `gh auth status` failing: "Command
  `['gh', 'auth', 'status']` returned non-zero exit status 1"). Given `schedules.py`'s own exit
  precedence (any FAIL→1, else any SKIP→3, else 0) and no FAIL line anywhere in the 50 lines, `rc`
  was 3, which the wrapper's `case $rc in ... 3) echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)"`
  maps to an overall **SKIP**. **However, the wrapper's own summary echo (the `PASS:`/`SKIP:`/
  `FAIL:` block the `verify-schedules.sh` case-statement is supposed to print after `schedules.py`
  exits, at `verify/schedules/verify-schedules.sh:44-49`) does not appear anywhere in the capture
  at all** — the file ends on the raw python `SKIP: driftwood/propose-tier.yml: ...` line with no
  wrapper-level sentence after it. This is either a truncated capture, a version of the wrapper
  script that ran without today's case-statement tail, or some other capture-pipeline artifact —
  I could not determine which from the evidence available, and I did not re-run the script (this
  review is read-only). **Flagging this as a genuine anomaly for the auditors**: every other
  script's capture in this family ends on its own wrapper-composed `PASS:`/`FAIL:`/`SKIP:`
  sentence; this is the one exception found.

---

## `verify/twin-evals/verify-twin-evals.sh`

- **Claims** (ticket 29 / decision ticket 11 item 5), five things, all offline:
  1. `twin/VERSION` and `twin.TOOL_VERSION` (the two spellings of the twin's own version) agree;
  2. the six real skills' seven metrics (causal-claims carries two, separately registered) are each
     graded via `verdict(score, threshold, last)` against **both** an absolute threshold *and* the
     last value recorded in the committed, append-only `twin/skill-scores.jsonl` — **a fall is a
     FAIL even when the score is still above threshold** ("a threshold is a floor... a fall against
     the last recorded value is the regression this harness exists to catch"). The exact set of
     metrics scored is asserted to equal `twin/skill-thresholds.yaml`'s declared set minus the
     `toy-classifier` fixture skill — a fixed, named bug: dropping a metric used to silently print
     "SUBTOTAL: 6 skill metric(s)" then "PASS: seven skill metrics..." underneath and exit 0
     ("found 2026-08-29"). Evaluated scores are written **only** to a throwaway tempfile path, never
     to the real `skill-scores.jsonl`, so a gate run cannot move its own bar;
  3. `twin/beat-sequence.sh` — three "real-firm" beats (royal-mail, intel, netflix) run in their
     declared order;
  4. `cross_architecture_determinism`, gated by `TWIN_CI_ARCH_MATRIX=1` — and a fixed bug where the
     invariant used to self-skip and still print `"PASS: cross_architecture_determinism --"` with
     an empty claim after the dash, exiting 0; now the check requires a non-empty extracted claim
     string (`N artefacts byte-identical on <arch>`) or it FAILs;
  5. the pinned-feed-version→dated-signal lookup (`twin/feed_signal.py`) — both its own
     `feed_signal.demo()` self-check and, separately, **coverage**: every real
     `.estate-clone/*/**/feed.json` envelope with `kind: feed` must resolve via `steep_for(name)` to
     exactly one signal (excluding a short, named `EXCLUDED_FROM_LOOKUP` list) — the comment names
     this as "the one that rots: a publisher ships a new feed, nobody adds a row, and the clock
     meets a version it cannot bind. That is a red gate here rather than a 06:20 surprise." The
     signal binding itself uses **placeholder** tag/commit values ("placeholder-tag", forty zeros)
     because this check only proves the *shape* of the mapping, not a real signature — the real
     tag/commit are the caller's responsibility at signature-verification time, which this script
     names explicitly rather than silently substituting.
- **Offline**: entirely — no network, no cluster; only needs `git`, a python with `pyyaml`, and
  `twin/VERSION` present (a checkout-identity check).
- **Run-21 grade: PASS** — `7 skill metrics, exactly the set twin/skill-thresholds.yaml declares,
  at their thresholds and none fallen, three real-firm beats, identical bytes on this architecture
  (12 artefacts byte-identical on x86_64), and every published feed envelope binding to one dated
  signal (15 of 15, 1 excluded by name).`

---

## `talk/verify-demo.sh` — the deck-honesty check (via `verify/demo/` symlink)

- **Claims, exhaustively listed in its own header** (`talk/verify-demo.sh:6-44`): the deck must
  build from *this run's* captures; every beat must cite a capture actually present in this run;
  every beat's status tag must match both this run's own grade for that script **and** step 7's
  independently-produced verdict for the same step; every money figure/percentage/count quoted in
  a beat body must appear verbatim in that beat's own capture (never invented, never borrowed from
  a different beat); the beats must be exactly the seven NORTH-STAR §4 steps, in order; a phrase
  lint refuses exactly four named phrases (`exemption`, `hourglass`, `admission gate`, `deny gate`)
  while flagging every *other* use of the word "gate" as a human-review item, not a failure; the
  **committed** `talk/deck.md` must itself pass every one of the above checks, not just a rebuild;
  a step-check script that exists on disk but produced no capture this run is a hard FAIL (a fixed
  bug — deleting every seven-step capture used to render all seven beats as
  `NOCHECK`/"no check yet, owned by ticket NN" and still print PASS, which lied about the check not
  existing at all); a quoted TRUTH line must belong to the deck's own commit.
- **Named ceilings, stated by the script itself**: headers/dates/tags/step numbers/ticket-ADR
  references/the `$ bash <script>` command line are outside the figure check; the grade is read
  from **the capture's last line**, not the exit code, "because the gate keeps the capture and not
  the exit code" — step 7's own table is treated as "a second, independently produced opinion,"
  never the sole source; this file's discovery order (sorting ahead of `verify/e2e/` inside the
  gate's alphabetical glob) means a gate run's *own* e2e captures may be the *previous* run's by
  the time this script reads them.
- **The clock-dependent split, explicitly designed and explained**: two of the checks — whether the
  committed deck's beats match a fresh rebuild, and whether the committed deck itself survives the
  figure checks — are **only graded when `GITHUB_RUN_NUMBER` is set** (i.e. inside the actual
  scheduled Actions run), because a local gate run overwrites `talk/captures/` with its own numbers
  first, making any comparison against the committed deck (which reflects a *different*, earlier
  scheduled run) compare two unrelated runs and misreport a real, current deck as "stale." The
  script names a concrete, dated cost of getting this wrong before the fix: "the deck was rebuilt
  and committed three times on 2026-08-31 and was 'stale' again within the hour." Off the clock,
  those two checks print an explicit "could not look" line rather than either PASS or FAIL.
  Everything else (build succeeds, the **rebuild** passes its own figure/status/headline/phrase
  checks, the generated-file marker is present) is graded unconditionally, everywhere, so a
  genuinely broken or hand-edited deck still fails off the clock too.
- **Run-21 grade: FAIL** (this run had `GITHUB_RUN_NUMBER` unset — a local run, per the capture's
  own "could not look: this is a local run" lines for the two clock-gated checks — but the
  **unconditional** rebuild-vs-committed-beats diff still fired and failed):
  the capture shows the committed `talk/deck.md` recording all six of steps 1–6 as
  `status=SKIP`, while a fresh rebuild from run-21's own captures produces
  `status=PASS,PASS,PASS,FAIL,PASS,PASS` for steps 1–6 respectively (step 4's FAIL matching the
  real observed cert-not-yet-valid defect above). Final line:
  `FAIL: talk/deck.md has been hand edited or is stale; run python3 talk/build_deck.py`. This
  FAIL is one of the 7 in `fail=7`, and it is a straightforward staleness signal — the committed
  deck predates the current run's real (mostly-green, one-FAIL) results and needs a rebuild, not
  evidence of a hand-edit or fabrication by itself.

---

## Reconciling with the TRUTH line (`pass=57 fail=7 skip=18 excluded=2 total=84`)

Of the 84 discovered scripts (`.estate-clone` + `verify/`, 2 pre-excluded), this file accounts for
16 of the `verify/`-tree scripts (the 7 e2e steps, feed-contract, party, pound-seam,
proportionality, provenance, renovate, schedules, twin-evals) plus `verify-demo.sh` discovered via
symlink — 17 total scripts read here, of which **run-21 grades**:
- PASS: steps 1, 2, 3, 5, 6, 7; feed-contract; party; pound-seam; proportionality; provenance;
  renovate — **12 PASS**
- FAIL: step 4; verify-demo — **2 FAIL** (both explained above: a real observed cert-not-yet-valid
  defect on the drift-sample lane, and a stale committed deck)
- SKIP: schedules (inferred from its tail showing `gh auth status` failing and the case-statement's
  rc-3 mapping; not confirmed against an explicit final `SKIP:`/`PASS:` sentence — **flagged above
  as needing a direct re-check of that capture's actual last line**)
- The remaining ~67 scripts against the TRUTH line's totals (pass=57, fail=7, skip=18) live under
  `.estate-clone/` (the six/eight unit repos), which is **out of this file's assigned scope**
  (verify/ and talk/verify-*.sh only) and was not read here. I did not verify the other 5 of the 7
  claimed FAILs, nor the other 16-17 of the 18 claimed SKIPs — those are unit-repo scripts.

## What I did not cover

- `.estate-clone/*` scripts entirely (out of scope per the task).
- The full bodies of `party.py`, `pound_seam.py` (870 lines), and `provenance.py` beyond their
  docstrings, the `verify-*.sh` wrappers, and READMEs — I read enough to describe mechanism,
  offline/live split, and absence-handling faithfully, but did not verify every internal function
  line-by-line the way I did for the e2e step scripts and `feed_contract.py`/`schedules.py`.
- `verify/proportionality/render.py`'s internals (only its `--check` contract, read via the
  wrapper and README).
- I did not independently re-run any script (task is read-only; I only read code and pre-recorded
  run-21 captures from `origin/main`).
- I did not confirm `verify-schedules.sh`'s exact final capture line (see flag above) — I inferred
  its run-21 grade from `rc` semantics and the visible SKIP-heavy tail rather than reading an
  explicit terminal sentence.
- The full body of `verify_provenance_verify-provenance.out` was not read past its last three
  lines — whether the live Rekor/SPIRE tails actually fired in run-21 (vs. fell back to offline
  notes) was not confirmed.
