# Engineering quality and maintainability — assessment

Auditor pass, 2026-09-02. Read-only. Every number below is from a command I ran or a file I
opened in this session; where I could not look I say so.

Baseline: TRUTH 2026-09-02T10:11Z run=21 hub=7b92990, units as named in the brief. The eight
fresh clones match the run-21 SHAs exactly except driftwood (clone `67bfc7a`, one drift-sampler
commit ahead of run-21's `6cf0671`); nothing below depends on that delta.

---

## 1. The measurements

### 1.1 Size

| Where | python | shell | yaml/yml | tests (py) |
|---|---:|---:|---:|---:|
| hub `twin/` `verify/` `talk/` | 37,610 | 2,486 | 2,668 | — |
| hub `tests/` | — | — | — | 18,623 |
| eight unit repos | 28,490 | 11,246 | 21,356 | 0 |
| **total** | **66,100** | **13,732** | **24,024** | **18,623** |

`122,479` lines of code and test in total (`find … -exec cat | wc -l`, excluding `.git`,
`__pycache__`, and the exclusions listed). Documentation on top of that: `49,656` lines of
tracked markdown under `.scratch/`, plus `3,839` lines across `docs/`, `CONTEXT.md`,
`NORTH-STAR.md`, `README.md`. Prose is roughly 1.4× the hand-written hub code.

Per-unit python/shell/yaml (`find … | wc -l`):

```
platform py=19066 sh=6097 yaml=8146 yml=579 json=1766
driftwood py=2649 sh=1256 yaml=2736 yml=1528
tuppence  py=2422 sh=1260 yaml=1865 yml=1290
ludlow    py=2270 sh=866  yaml=1584 yml=1293
feeds     py=935  sh=764  yaml=206  yml=425
insurer   py=436  sh=479  yaml=277  yml=535
ico       py=373  sh=345  yaml=51   yml=418
nist      py=339  sh=179  yaml=38   yml=385
```

Largest modules: `twin/fixtures.py` 5,951 L; `twin/invariants/harness.py` 4,738 L;
`platform/compose/composition.py` 3,654 L; `twin/cli.py` 2,133 L;
`platform/computed-semver/cage_engine.py` 1,492 L; `twin/verbs.py` 1,520 L;
`platform/computed-semver/gate.py` 1,134 L.

### 1.2 Tests

`.venv/bin/python -m pytest -q` (pytest-timeout is not installed, so `--timeout=600` was
rejected; I ran without it):

```
1 failed, 1550 passed in 693.95s (0:11:33)
FAILED tests/test_invariant_suite.py::test_the_suite_is_green
```

Identical result in CI on the same hub commit (`gh run view 33615039125 --log-failed`):
`1 failed, 1550 passed in 115.13s`. The one failure is
`flux_coverage_floor_is_still_reachable`, a pre-registered, owned finding (build ticket 70).
The companion invariant job reports `70 passed, 1 failed, 3 skipped` — an improvement on the
twin map's recorded "70 pass / 2 fail": `drift_window_is_actually_being_sampled` is now green.

**All 1,551 pytest tests import only `twin.*`.** `grep -rl "verify/\|talk/\|build_deck\|pound_seam"
tests/*.py` returns nothing. `verify/` (3,261 py lines) and `talk/` (477 py lines) — the gate
instrument itself — have no pytest coverage at all.

**All eight unit repos have zero tests in any framework.** `grep -rl 'def test_' --include='*.py'`
across the eight clones returns `0` files. No pytest, no unittest, no lint config, no CI lint or
typecheck job (`ls -a <unit> | grep -icE 'ruff|mypy|flake8|pyproject|pre-commit'` = 0 for all
eight; `grep -rl "pytest\|mypy\|ruff\|shellcheck" <unit>/.github/workflows/` = 0 for all eight).

What stands in for tests in the units is the in-module `selfcheck()` function plus the
`verify*.sh` scripts. Measured by AST:

```
platform  python=19066  selfcheck=5171 (27%)  31 selfcheck funcs
ludlow    python=2270   selfcheck=443  (20%)
tuppence  python=2422   selfcheck=410  (17%)
feeds     python=935    selfcheck=162  (17%)
driftwood python=2649   selfcheck=410  (15%)
ico       python=373    selfcheck=67   (18%)
insurer   python=436    selfcheck=77   (18%)
nist      python=339    selfcheck=25   (7%)
```

These are single monolithic functions, not suites. `gate.py`'s `selfcheck` is 597 of the file's
1,134 lines (53%); `composition.py`'s is 1,009 of 3,654 (28%); `coverage.py`'s 374 of 976 (38%).

### 1.3 The verify surface

86 `verify*.sh` scripts (18 hub + 68 units; `find … -name 'verify*.sh'`). 49 define their own
`pass`/`fail`/`skip`/`say` grading helpers; 24 source a shared lib. Five distinct `lib.sh`
copies exist (`platform/lib.sh` 46 L, `verify/e2e/lib.sh` 26 L, and three 38-line
`scripts/lib.sh` in the adopters that are byte-identical after party-name normalisation).

40 of 86 have no reachable `exit 3` (SKIP) path even after resolving sourced libs. For genuinely
offline scripts that is honest; for the six named in §2.2 it is not.

### 1.4 Duplication

Cross-adopter file comparison (`driftwood`/`tuppence`/`ludlow`), code files only
(`.py .sh .yml .yaml`), after normalising every occurrence of the party name to `PARTY`:

```
identical after normalisation : 15
genuinely drifted             : 24
```

The 15 identical: `read-two-pins.py`, the five generated `composed/policies/v4.0.0/*.yaml`,
`governed-namespace-guard.yaml`, `orphan-guard.yaml`, `git-server/deployment.yaml`, two
configmaps, two `kustomization.yaml`, `scripts/lib.sh`, `scripts/render_composed.py`.

Drift magnitude in the load-bearing shared logic (normalised diff, lines changed):

| file | lines | d↔t | t↔l |
|---|---:|---:|---:|
| `.github/workflows/shift-left.yml` | 394 | 259 | 302 |
| `.github/workflows/propose-tier.yml` | 279 | 78 | 58 |
| `drift/five-facts.py` | 802 | 61 | 0 |
| `verify-reconcile.sh` | 189 | 36 | 4 |
| `.github/workflows/drift-sample.yml` | 269 | 11 | 4 |
| adopter gate | 661 / 1087 / 1213 | 1254 | 1416 (l↔t) |

The cage-tier policy exists in nine files. Eight are legitimate: five versioned copies in
`platform/distribution/policies/v{2.0.0,2.0.1,3.0.0,4.0.0,vselfcheck}/` (multi-version
coexistence is the thesis), plus three adopter copies that are byte-identical to
`platform/distribution/policies/v4.0.0/cage-tier.yaml` modulo the `composed-for` label and two
provenance annotations (`inherited-from`, `source-path`) — i.e. genuinely generated, not
copy-pasted. The ninth, `platform/graded/policies/cage-tier.yaml` (262 L), is a separate
hand-written implementation of the same concept and is behind the served one (§2.6).

### 1.5 Determinism

Every stochastic path I found is explicitly seeded: `random.Random(SEED)` in
`platform/fair/fair.py:132,324`, `random.Random(int(rule["sample_seed"]))` in
`feeds/fetch/market-moves.py:62`, `random.Random(recipe.seed)` in `twin/substrate.py:125`,
`twin/substrate_generator.py:119`, `twin/pert.py:225`, `twin/benchmark.py:205`. The single
`os.urandom` (`twin/substrate.py:137`) is the deliberately non-deterministic generator path,
contrasted in the module docstring against `generate_deterministic`.

Verified empirically: two consecutive `python3 fair/fair.py summary
fair/scenarios/driftwood-cart-pii.json` runs produced byte-identical output (`diff -q` →
IDENTICAL), including `ale=19558.549772440045`.

CI corroborates: the twin workflow's `determinism` matrix passed on all three of
`ubuntu-24.04-arm/aarch64`, `ubuntu-24.04/x86_64`, `macos-14/arm64` in run 33615039125, as did
`reproduce-elsewhere`.

### 1.6 Error handling

AST scan of 261 `except` handlers across hub and units: **zero bare `except:`**. 45 handlers
either swallow silently or are bare-equivalent, and the great majority are the negative-test
idiom inside `selfcheck` (`try: bad_thing(); raise AssertionError(...) except Refused: pass`) —
`twin/invariants/harness.py` and `checks.py` account for 29 of the 45. Four sit in production
paths and are examined in §2.9 and §2.12.

Shell: 8 of `twin`+`verify`+`talk`'s 24 scripts use `set -euo pipefail`; the rest use
`set -uo pipefail` or `set -u`. That is deliberate — a graded script must run all its checks and
then decide, not abort on the first non-zero — and `verify/e2e/lib.sh:5` documents the contract.
`|| true` appears 8 times in the hub.

### 1.7 Languages, tools and CLIs a maintainer needs

File types in the code surface: `yaml` (486 files), `py` (242), `sh` (128), `json` (97),
`yml` (36), plus Dockerfile, PEM/SIG/bundle, JSONL, Mermaid.

External tools guarded by an explicit `command -v` somewhere in the estate: `kubectl` (11
sites), `kyverno` (10), `python3` (9), `git` (7), `kind` (5), `gitsign` (4), `docker` (3),
`openssl` (2), and one each of `swtpm`, `spire-agent`, `qemu-img`, `gh`, `cosign`. Add the tools
the truth workflow installs or invokes but does not guard: `flux`, `cosign`, `jq`, `curl`,
`tar`, `sha256sum`, plus `node`/`npx`/`marp` for the deck, `renovate` in the self-hosted
adopter clocks, `bao` and `istioctl` in tuppence's reset lane. Realistically a second engineer
needs: Python 3.12, bash, git + gitsign, Docker, kind, kubectl, Flux, Kyverno CLI, cosign, gh,
Node/marp, and (for tuppence) OpenBao and Istio — around **13 tools across 4 runtimes**, plus
familiarity with Kyverno CEL, OSCAL, Flux `ResourceSet`, Sigstore/Rekor, and FAIR risk maths.

### 1.8 Commit hygiene and bus factor

Fix-of-fix churn, the brief's wordlist (`correct|was wrong|mis-ordered|actually`), commit
**subjects** only:

```
hub, last 200 commits : 11 / 200  (5.5%)   [correct=9, mis-ordered=1, actually=1, "was wrong"=0]
driftwood (93 total)  :  2
ludlow    (53 total)  :  2
tuppence  (60 total)  :  1
platform  (102 total) :  0
nist / ico / feeds / insurer : 0
```

Including commit bodies the hub figure rises to 45/200, but that count is contaminated by
legitimate uses ("the guard correctly refuses"); I do not rely on it.

The subject-line rate is low. The correction load has instead been pushed **into the code as
dated comments**: 363 occurrences of a `2026-0[6-9]-DD` date inside `.py`/`.sh`/`.yml` across
hub and units, and 180 comment lines matching
`incident|used to|silently|false pass|regression|was passing|never actually|planted`. That is a
deliberate and, in my view, admirable convention — but it is also a defect-density measurement,
and it is 180 recorded self-corrections in 66k lines of Python.

Zero `TODO`/`FIXME`/`XXX`/`HACK` anywhere in the estate. They have been replaced by the
project-private marker `ponytail:` — 152 occurrences across ≥24 modules — which is **not defined
in `CONTEXT.md`** (`grep -ci ponytail CONTEXT.md` → 0) and appears once, in passing prose, in
`docs/adr/0015-…:94`.

Bus factor: **1.** `git shortlog -sne --all` on the hub: 408 commits by
`Chris Nesbitt-Smith <chris@cns.me.uk>`, 17 by the `truth surface` bot. Every unit repo is the
same shape: one human identity plus a release/sampler bot (platform 98+4, driftwood 89+4,
tuppence 58+2, ludlow 51+2, nist 14, ico 14, feeds 8, insurer 7). Combined with the
`github-live` map's finding (zero branch protection on all nine repos; every human PR authored
and merged by the same account), no second reviewer has ever read this code.

### 1.9 Type discipline

`882/994` functions in hub `twin/verify/talk` carry a return annotation (88%); `610/873` in the
units (69%). mypy is configured only for `twin`+`tests`+`conftest.py`, and only in the hub.

---

## 2. Findings

### EQ-01 (critical) — Zero automated tests, types or lint in all eight unit repos, and in the gate itself

**Claim.** 28,490 lines of Python and 11,246 lines of shell in the eight unit repos, plus 3,738
lines of Python in the hub's `verify/` and `talk/`, are covered by no test framework, no type
checker and no linter. Their only automated coverage is in-module `selfcheck()` functions
(7,000 lines, 24% of unit Python) executed by `verify*.sh` scripts graded solely by process exit
code.

**Evidence.**
- `grep -rl 'def test_' --include='*.py'` across the eight clones → 0 files.
- `ls -a <unit> | grep -icE 'ruff|mypy|flake8|pyproject|pre-commit'` → 0 for all eight.
- `grep -rl "pytest\|mypy\|ruff\|shellcheck" <unit>/.github/workflows/` → 0 for all eight.
- `grep -rl "verify/\|talk/\|build_deck\|pound_seam" tests/*.py` → no matches; the 1,551 hub
  tests import `twin.*` only.
- `.github/workflows/twin.yml:64` runs `mypy twin tests conftest.py` — `verify/` and `talk/` are
  not in the argument list.
- AST measurement of `selfcheck` share, §1.2.

**Consequence.** A change to `composition.py` (3,654 L), `gate.py` (1,134 L) or
`adopter-gate.py` (1,087 L) is validated by running one shell script whose whole verdict is one
exit code. There is no way to run one assertion, no failure isolation, no coverage number, no
parametrisation, and no static check that a refactor kept the types. `selfcheck` at 53% of
`gate.py` means half the file is test code that no test runner can address.

**Not a repeat.** REVIEW-2026-08-31 does not raise this; it is about gate colour, not about
whether the code is testable.

**Remedy (smallest honest).** Add `pytest` + `mypy` to `platform`'s CI on the modules that
already have a `selfcheck` seam — `selfcheck()` can be invoked from a single `test_selfcheck.py`
per module in a day, which buys failure isolation and a runner without rewriting a line of
logic. Then extend the hub's existing `typecheck` job's argument list to include `verify talk`.

---

### EQ-02 (major, instrument) — Six verify scripts print `SKIP` and exit 0, which the gate grades PASS

**Claim.** `platform/computed-semver/` contains six scripts that, when the `kyverno` CLI is
absent, print a line beginning `SKIP:` and then `exit 0`. `talk/verify-all.sh` grades by exit
code (`case $rc in 0) … PASS`), so on any runner without kyverno these six would be counted as
observed-true. This is the exact defect class the estate's own code names and fixed elsewhere.

**Evidence.**
- `talk/verify-all.sh:61-62`: `case $rc in 0) printf '%-70s PASS\n' "$s"; pass=$((pass+1));;`
- The same file's header, lines 6-13: *"0 PASS observed true / 3 SKIP could not look … Nothing is
  faked: a live tail that cannot see its cluster must exit 3, not 0."*
- `platform/computed-semver/verify-gate.sh:11-13`, `verify-cage-engine.sh:12-14`,
  `verify-comparison-window.sh:11-13`, `verify-rederive-bumps.sh:9-11`,
  `verify-generator-standing-check.sh:18-20`, `verify-corpus-generator.sh:34-36` — each is
  `if ! command -v kyverno …; then echo "SKIP: …"; exit 0`.
- Automated sweep across all 86 verify scripts (`SKIP` echo followed within 4 lines by
  `exit 0`) returns exactly these six and nothing else.
- `verify-witness-set.sh:68-70` is a seventh, worse variant: it prints its `SKIP (step 5)` text
  mid-file and falls through to the end of the script (exit 0), so the SKIP is not even the last
  line the gate would quote.
- The fix exists twenty lines away in a sibling directory:
  `platform/distribution/verify-render-version-tree.sh:23-27` reads *"exit 3, not 0.
  verify-all.sh grades 0 as PASS, so exiting 0 here reported 'the coexistence proof holds' on any
  runner without the CLI — a check that passes on absence, the exact class the 2026-08-25
  incident came from."*

**Live impact today: none.** `.github/workflows/truth.yml:46-47` installs kyverno 1.18.2 pinned
by SHA256, and run 21's log shows all six PASS with real kyverno output, so no number on TRUTH
run 21 is wrong. This is a latent fault, armed the first time the clock runs without kyverno.

**Ownership.** REVIEW-2026-08-31's minor list names *"Silent-PASS-on-missing-kyverno in
render-version-tree"* — one script, since fixed. Six siblings in a different directory carry the
same defect and each one's comment cites the others as the reason for the convention. No open
ticket names `computed-semver/`. This is an **orphan**.

**Remedy.** Change `exit 0` to `exit 3` in six files, and make `verify-witness-set.sh` exit 3
when step 5 could not look. Seven one-line edits.

---

### EQ-03 (critical) — The three adopters are copy-pasted, have genuinely diverged, and improvements do not cross

**Claim.** Of 39 code files present in ≥2 adopters, only 15 are identical after party-name
normalisation; 24 have genuinely diverged. The divergence is not cosmetic: the module that
decides the estate's central drift claim, `drift/five-facts.py`, has a real feature in driftwood
that tuppence/ludlow lack and a real fix in tuppence/ludlow that driftwood lacks. Every future
fix to shared adopter logic must be written three times.

**Evidence.**
- Normalised md5 comparison (§1.4): 15 identical, 24 drifted.
- `drift/five-facts.py` — tuppence and ludlow are byte-identical after normalisation (`t↔l`
  normdiff = 0 lines); driftwood differs by 61 lines. The diff shows:
  - **driftwood only:** `WINDOW_CLUSTER = "kind-driftwood"` plus a `cluster_name ==
    WINDOW_CLUSTER` guard on `reachable`, and a `subjects` block sampling three live cluster
    objects. The docstring explains why: a sample taken on the wrong cluster must contribute a
    coverage hole, "which is why a CI run on an ephemeral cluster cannot inflate build ticket
    64's coverage."
  - **tuppence/ludlow only:** an `_org()` helper reading the party name from `party.yaml` with
    the comment *"never typed twice and never guessed from a directory name that a checkout can
    rename"* — driftwood still hard-codes its own name in five places, and an extra
    reachability probe with the comment *"a missing Kustomization reads as NotFound, which is an
    answer, not a failure to reach."*
  - Neither copy has both improvements.
- The adopter gate is three independent programs: `driftwood/.github/scripts/adopter-gate.py`
  (1,087 L), `tuppence/.github/scripts/adopter-gate.py` (661 L),
  `ludlow/.github/scripts/adopter_gate.py` (1,213 L — note the underscore; the filename itself
  drifted). Normalised diffs: d↔t 1,254 lines, l↔t 1,416, d↔l 1,752 — i.e. essentially disjoint
  implementations.
- `.github/workflows/shift-left.yml`: 397/394/388 lines, normalised diff 259 (d↔t) and 302
  (t↔l). The named steps differ in count and in order: driftwood has 16 named steps including two
  labelled "bug fix #1"/"bug fix #2"; tuppence has 12 and runs the version cross-check *after*
  the adopter gate rather than before; ludlow has 15 including a step the other two do not
  have at all, *"fail the required check if the adopter gate refused"* (ludlow line 273).
- I checked whether ludlow's extra step covers a hole in the others: it does not — driftwood
  propagates the gate's exit via `status=${PIPESTATUS[0]}; exit "${status}"`
  (`shift-left.yml:172-174`). So this is three valid designs for one job, not a bug — which is
  exactly the maintenance cost being described.
- The `adopters` map's own note is corroborated: `.github/scripts/adopter-gate.py` is
  documented in-repo as having "evolved independently".

**Consequence.** Three copies × the whole adopter surface is the largest single tax on this
estate. It also degrades the truth surface's meaning: run 21's three `verify-reconcile` FAILs
are graded by two different builds of the grading engine.

**Ownership.** Not owned. No open ticket proposes extracting shared adopter logic. Ticket 42
(resolved) back-ported one specific fix (`gotk-sync.yaml` path) to two of three repos and
explicitly not to driftwood, the repo where the bug was found — an instance of the same
disease.

**Remedy.** The estate already has the mechanism: `platform` publishes signed, versioned
artefacts that adopters render via the identical `render_composed.py`. Move `five-facts.py`,
`verify-reconcile.sh` and the adopter-gate core into `platform` as a published, tagged, pinned
package, and let the adopters render/pin it the way they already render `composed/policies/`.
That is the thesis applied to its own tooling.

---

### EQ-04 (major) — The only quality gate that exists has failed 25 runs in a row, and one of its three reds is a one-line fix

**Claim.** `.github/workflows/twin.yml` is the estate's sole pytest/mypy gate. It has failed
every run in the pulled window (25/25 per the `github-live` map; I confirmed the three most
recent). On the exact hub commit named in TRUTH run 21 (`7b92990`) three of its eight jobs are
red: `tests`, `invariants`, `typecheck`. The typecheck red is a single unused `type: ignore`.

**Evidence.**
- `gh run list --workflow=twin.yml --limit 3` → all `failure`, head SHAs `7b92990`, `ce4be49`,
  `e7981a5`.
- `gh run view 33615039125 --json jobs`: `tests failure`, `invariants failure`,
  `typecheck failure`; `demo`, `reproduce-elsewhere` and all three `determinism` legs `success`.
- `gh run view 33615039125 --log-failed`:
  `twin/feed_signal.py:232: error: Unused "type: ignore" comment [unused-ignore]` /
  `Found 1 error in 1 file (checked 159 source files)`.
- Reproduced locally: `.venv/bin/python -m mypy twin tests conftest.py --ignore-missing-imports
  --warn-unused-ignores` → the identical single error.
- The `tests` and `invariants` reds are the same owned finding
  (`flux_coverage_floor_is_still_reachable`, build ticket 70), which is honest.

**Consequence.** A workflow that is red for a known-and-accepted reason cannot signal a new
regression: the typecheck red arrived and was invisible because the workflow was already red.
This is the "saturated signal" failure REVIEW-2026-08-31's M14 named for the TRUTH line;
it is now true of the twin gate too, and M14's ticket 59 is still open.

**Remedy.** Delete the stale `# type: ignore` on `twin/feed_signal.py:232` (one line), and mark
the known-red invariant as expected so the job's colour tracks new information — or split it so
that `flux_coverage_floor_is_still_reachable` reports amber rather than failing the run.

---

### EQ-05 (major) — 30 of 82 captures end with no verdict line, and the convention is enforced on 6 scripts

**Claim.** The estate's grading convention is that a script's last line is `PASS:`/`FAIL:`/
`SKIP:` and carries the reason. 30 of the 82 run-21 captures on `origin/main` violate it. The
check that enforces the convention, `verify/e2e/verify-e2e-step7-honesty.sh`, is scoped to the
six `verify/e2e/` step scripts only.

**Evidence.**
- Script over `git ls-tree origin/main talk/captures/` reading each file's last non-blank line:
  30 of 82 do not begin `PASS:`/`FAIL:`/`SKIP:`. Examples: `verify-gate.out` ends on a
  1,500-character `selfcheck ok: …` sentence; `verify-composition.out` and
  `verify-party-artefact.out` end on an ANSI-coloured `==>` progress line;
  `verify-cut-release-tags.out` ends `the clean nu…`.
- `talk/verify-all.sh:60` sets `last="$(tail -1 "$cap" | cut -c1-160)"` and prints it as the
  reason on every FAIL and SKIP row — so a FAILing script without a verdict line reports a random
  trailing fragment as its diagnosis.
- `verify/e2e/verify-e2e-step7-honesty.sh:5-11` states it fails a step whose script "ends on
  something that is not PASS:/FAIL:/SKIP:"; line 32 sets
  `STEPS="${E2E_STEPS_DIR:-$E2E_DIR}"`, i.e. `verify/e2e/` only.
- Related sloppiness in the same surface: three run-21 FAIL rows read
  `FAIL: FAIL: a fact of the five-fact sample was observed false` — a doubled prefix from the
  three `verify-reconcile.sh` copies (`grep -c 'FAIL: FAIL:'` = 3).

**Live impact today.** All 30 currently PASS, so no reason line is being misread on run 21. The
cost is diagnosability the first time one of them goes red — and 21 of the estate's scripts have
been red for long stretches.

**Ownership.** Not owned as a class. Not raised by REVIEW-2026-08-31 (its M-list is about
specific reds, not the convention's scope).

**Remedy.** Widen `verify-e2e-step7-honesty.sh`'s structural check — "exit code agrees with a
verdict-prefixed last line" — from the six e2e steps to all 86 discovered scripts, and let it
report the offenders. It is the same loop `verify-all.sh` already runs.

---

### EQ-06 (major) — 15 of 18 SKIPs on the citable clock reduce to two root causes, and one is that the clock never provisions a cluster

**Claim.** The citable instrument is structurally unable to observe roughly a sixth of its own
checks, because `.github/workflows/truth.yml` never creates a Kubernetes cluster and never
installs `kind`.

**Evidence.**
- Run-21 grade table extracted from `gh run view 33616685427 --log`: `PASS=57 FAIL=7 SKIP=18`,
  matching the TRUTH line exactly.
- Bucketing the 18 SKIP reasons: **12** cite `kind cluster 'driftwood' is not listed by kind get
  clusters` or `kind cluster 'driftwood' does not exist`; **3** cite
  `distribution/versions.yaml declares one version (4.0.0)`; **1** cites `GitHub unreachable`
  (`gh auth status` non-zero); the remaining 2 are `verify-publisher-gate` part c and
  `verify-insurer-quote`'s staleness SKIP.
- `grep -nE 'kind create|kind |cluster|flux install|docker' .github/workflows/truth.yml` returns
  **nothing** — the workflow installs gitsign, kyverno, cosign and flux binaries but stands up no
  substrate.
- `verify/e2e/lib.sh:23` has a `cluster_up()` that would create an ephemeral `pav-e2e` cluster,
  but it opens with `command -v kind >/dev/null && docker info … || skip "substrate absent"`, and
  kind is never installed by the clock.
- The fact is recorded — `.scratch/ecosystem/issues/03-the-truth-surface.md:50` writes
  *"`truth` run 5 … no cluster"* — but ticket 03 is `Status: resolved`, and the two other
  tickets naming an ephemeral cluster (16, 52) are resolved too. No **open** ticket proposes
  provisioning one.

**Consequence.** ~14% of the surface (12 of 84) can never move off SKIP on the clock as
configured, so a regression in any of those twelve is undetectable from the citable number.
Three more are stuck because `versions.yaml` declares one version — a consequence of the
retirement decision, honestly reported, and a separate architectural question.

**Ownership.** Recorded, not owned. Orphan for the purposes of a fix.

**Remedy.** Either install kind and stand up one ephemeral cluster in `truth.yml` (the e2e lib
already knows how to create and tear one down), or state in `NORTH-STAR.md` §5 that the clock
grades offline only and that live tails are graded on a separate, named lane — so a permanent
SKIP is a declared property rather than an unexplained gap.

---

### EQ-07 (major) — `selfcheck` is a monolith, not a suite

**Claim.** The estate's substitute for unit tests is one enormous function per module, which
cannot report per-assertion results, cannot be run selectively, and fails all-or-nothing.

**Evidence (AST, longest function per module).**

```
platform/computed-semver/gate.py        selfcheck = 597 L of 1134 (53%)
platform/compose/composition.py         selfcheck = 1009 L of 3654 (28%)  [compose() itself = 298 L]
platform/computed-semver/coverage.py    selfcheck = 374 L of 976 (38%)
platform/computed-semver/cage_engine.py selfcheck = 343 L of 1492 (23%)
platform/wargamer/tier_pr.py            selfcheck = 248 L of 792  (31%)
platform/party/party_artefact.py        selfcheck = 237 L of 793  (30%)
verify/schedules/schedules.py           selfcheck = 213 L of 890  (24%)
twin/invariants/harness.py  longest check = 282 L (_netflix_runs_both_paths…)
```

- `verify-gate.out` on `origin/main` shows the consequence: the entire selfcheck's result is a
  single ~1,500-character sentence with 20 semicolon-separated claims, printed as one line. A
  reader cannot tell which of the 20 was exercised or which would fail first.

**Consequence.** Not a correctness defect — the assertions are real and they run — but it makes
the code hostile to incremental change: a one-line edit to `gate.py` can only be validated by
running 597 lines of assertions that report one bit.

**Remedy.** Because each `selfcheck` is already a sequence of independent `assert`/`print("ok …")`
blocks, splitting it into `def check_<name>()` functions with a driver loop is mechanical, and
gives per-check reporting for free. Do `gate.py` first (highest ratio).

---

### EQ-08 (major) — Bus factor 1, with no second reader anywhere in the record

**Claim.** All 9 repos have exactly one human author, no branch protection, and no PR that a
second person reviewed.

**Evidence.**
- `git shortlog -sne --all` (hub): 408 `Chris Nesbitt-Smith`, 17 `truth surface` bot. No other
  human.
- Per-unit author counts (§1.8): one human plus a release/sampler bot in every repo.
- Corroborated by the `github-live` map: zero rulesets and 404 on `branches/main/protection` in
  all 9 repos; every closed non-Renovate PR across 46 examined was authored and merged by the
  same account.

**Consequence.** This is the honest state of a solo research estate and I do not read it as
negligence. But it bears on fitness: the codebase has never been read by a second engineer, so
its legibility is untested by the very audience the thesis wants (a client's platform team
adopting it). The high comment density (§1.9, §3) is the mitigation, and it is a real one.

**Remedy.** No code change. The decision is the owner's: whether "a second engineer can pick
this up" is a claim the estate should test (by having someone else try) or a claim it should
stop making.

---

### EQ-09 (minor) — `graded/README.md` names a resolved ticket as the owner of unbuilt work

**Claim.** At exactly the run-21 platform commit, `graded/README.md:39-43` says the Kyverno half
of the cage ladder is *"Not yet served"* and that *"eco-system ticket 26 lands"* it. Ticket 26 is
`Status: resolved`.

**Evidence.**
- `git -C units/platform show 46cd775:graded/README.md` lines 39-43: *"**Not yet served:**
  `graded/policies/cage-tier.yaml` still carries only the first three rungs and its per-tier
  reach is still one flat egress lockdown, so `verify-graded.sh` step 4 reports the drift;
  eco-system ticket 26 lands the Kyverno half (dial map, `cage-isolated` PriorityClass, per-tier
  reach, and the unknown-tier fallback flipping from `baseline` to `isolated`)."*
- `.scratch/ecosystem/issues/26-the-cage-ladder-lands.md:4` → `Status: resolved`.
- The *served* copy is not the stale one: `platform/distribution/policies/v4.0.0/cage-tier.yaml`
  carries all four ORDER rungs (`baseline`, `restricted`, `quarantine`, `isolated` each appear
  twice in its `dial` map), matching `graded/cage.py:127` `ORDER = ["baseline","restricted",
  "quarantine","isolated"]`. So `graded/policies/cage-tier.yaml` is the divergent one.

**Consequence.** Honest in the code, wrong in the tracker. A reader who trusts the tracker
believes the ladder shipped; a reader who trusts the README goes looking for an open ticket that
is closed. This is a specific instance of REVIEW-2026-08-31's M14 (status not derived from a
check, ticket 59, still open).

**Remedy.** Either reopen 26 or move the residue to a new ticket, and change the README to name
it. Do not silently edit the README green — `verify-graded.sh` step 4 still reports the drift
every run, which is the correct behaviour.

---

### EQ-10 (minor) — An unreadable workflow file makes the identity-regexp cross-check silently not fire

**Claim.** `drift/five-facts.py` swallows `OSError` when reading the CI workflow to extract
`EXPECTED_IDENTITY_REGEXP`, returns empty strings, and the caller then skips the comparison
because the value is falsy — turning "could not look" into "nothing to check".

**Evidence.**
- `driftwood/drift/five-facts.py:165-175`: `found = {"regexp": "", "issuer": ""}` … `except
  OSError: pass` … `return found`.
- Caller, same file line 406 (driftwood) / 393 (tuppence): `if party == "driftwood" and
  ci.get("regexp") and regexp != ci["regexp"]:` — an empty `ci["regexp"]` short-circuits the
  check.

**Consequence.** A renamed or unreadable workflow file removes a falsifier without any signal.
This is the estate's own cardinal sin (absence reading as a pass) in miniature.

**Ownership.** Plausibly already owned: REVIEW-2026-08-31's minor list includes *"five-facts
falsifier 1 can silently not fire"*, folded into tickets 54/55/59/64/66/67. I did not trace
which ticket carries it and cannot say it is closed; the code at the run-21 SHA still has the
swallow.

**Remedy.** Return `None` on `OSError` and make the caller record a could-not-look rather than
skipping the comparison.

---

### EQ-11 (minor) — `currency.py`'s fallback invents policy versions the estate has retired

**Claim.** `platform/currency-controller/currency.py:64-83` falls back to the literal
`"1.0.0,2.0.0"` when it cannot read `distribution/versions.yaml`. That array today declares only
`4.0.0`; `2.0.0` was retired as unsafe.

**Evidence.**
- `currency.py:81-83`: `except OSError: pass` … `return "1.0.0,2.0.0"`.
- `currency.py:233`: this is the default for `plan --supported`.
- `platform/distribution/versions.yaml` declares one version, `4.0.0` (corroborated by three
  run-21 SKIP reasons quoting *"declares one version (4.0.0)"*).
- The docstring is honest about the mechanism ("falls back to the old literal only if the file
  can't be found") — the defect is that "the old literal" was never updated when the array was.

**Consequence.** Small. `plan` run outside a checkout reports a supported-window that names a
retired version. It is a stale-constant hygiene issue, not a live wrong number.

**Remedy.** Raise instead of defaulting, consistent with ADR-0020's missing-instrument doctrine;
or, minimally, change the literal to `"4.0.0"`.

---

### EQ-12 (minor) — 152 known gaps are marked with an undefined private word, and the estate has zero TODOs

**Claim.** `TODO`/`FIXME`/`XXX`/`HACK` appear **zero** times in 66k lines of Python and 14k of
shell. Known gaps are instead marked `ponytail:` — 152 occurrences across at least 24 modules —
a term that is not in `CONTEXT.md` and appears once in the ADRs, in passing.

**Evidence.**
- `grep -rniE '\b(TODO|FIXME|XXX|HACK)\b'` across hub `twin verify talk` and the eight units → 0.
- `grep -rn 'ponytail'` same scope → 152 hits across `twin/{feed_signal,detector,credibility,
  causal_claims,options,ingest,pert,evolution_judge,constraints,substrate_eval,cli,sign,severity,
  enact_guard,enforcement,corroboration,propagate,market_signals,blast}.py`,
  `verify/{schedules,pound-seam}`, `talk/build_deck.py`, `platform/verify-publisher-gate.sh` and
  others.
- `grep -ci ponytail CONTEXT.md` → 0. Only ADR mention:
  `docs/adr/0015-adopter-runs-the-proposer-and-it-opens-the-pr.md:94`.

**Consequence.** A second engineer's first instinct — `grep -r TODO` — returns nothing and
suggests a codebase with no known gaps. 152 of them are hidden behind a word only this project
uses. The `CONTEXT.md` glossary is the project's own stated remedy for exactly this
(`CLAUDE.md`: "read this to speak precisely") and it does not carry the term.

**Remedy.** One glossary entry in `CONTEXT.md`. Two lines.

---

### EQ-13 (minor) — The README does not tell a new engineer how to build, test or run anything

**Claim.** `README.md` has no mention of `pytest`, `.venv`, `clone-estate.sh`, `verify-all.sh`,
or the truth surface; it names the ADRs as "ADR-0001…0010" when 24 exist; there is no
`CONTRIBUTING`/`DEVELOPING` file.

**Evidence.**
- `grep -icE 'pytest|\.venv|clone-estate|verify-all|truth surface|how to run|installation'
  README.md` → 0.
- `ls docs/adr/*.md | wc -l` → 24; README table row reads *"The **decisions** and why
  (ADR-0001…0010)"*.
- `ls CONTRIBUTING* DEVELOP*` → no matches.
- The README's "Start here" table points at PRD, NORTH-STAR, twin, CONTEXT, HISTORY, ADRs,
  research — all narrative, none operational. `talk/`, `verify/`, `tests/` and the eight unit
  repos are absent from it.

**Consequence.** The operating instrument — the daily clock, the 86 verify scripts, the 1,551
tests — is invisible from the front door.

**Remedy.** Six lines in the README: how to make the venv, `python -m pytest -q`,
`bash clone-estate.sh && bash talk/verify-all.sh`, what a TRUTH line is, and where the eight
unit repos live. Fix the ADR range while there.

---

### EQ-14 (minor) — The developer environment is not the CI environment, and the local suite is 6× slower

**Claim.** `.venv` is Python 3.14.6; `twin.yml` pins 3.12. The same suite takes 693.95 s locally
and 115.13 s in CI.

**Evidence.**
- `.venv/bin/python -V` → `Python 3.14.6`; `.github/workflows/twin.yml:32,47,60`
  → `{python-version: '3.12'}`.
- Local: `1 failed, 1550 passed in 693.95s`. CI (`gh run view 33615039125 --log-failed`):
  `1 failed, 1550 passed in 115.13s`.
- `pytest.ini` has no `python_requires`/version pin, and there is no `pyproject.toml`,
  `requirements.txt` or lockfile anywhere in the hub (`ls pyproject.toml` → not found).

**Consequence.** Small today (results agreed). But nothing pins the interpreter or the
dependency set outside the CI workflow's inline `pip install`, so a laptop and the clock can
diverge silently — which is the failure mode this estate exists to prevent.

**Remedy.** A `requirements.txt` (or `pyproject.toml`) holding the four pins that
`twin.yml:33` already names, and a `python_requires` line.

---

### EQ-15 (minor) — 345 MB of tracked audio and video inflate the hub's history

**Claim.** The hub tracks 170 `.wav`, 76 `.mp4` and 143 `.png` files under
`.scratch/talk-spec/`, totalling ~345 MB; `.git` is 257 MB and the working tree 1.7 GB.

**Evidence.**
- `git ls-files .scratch | sed 's/.*\.//' | sort | uniq -c` → `170 wav`, `143 png`, `76 mp4`.
- `git ls-files .scratch | grep -E '\.(wav|mp4|png)$' | xargs du -ck | tail -1` → `345432`
  (KB) ≈ 345 MB.
- `du -sh .git` → `257M`; `du -sh .` → `1.7G`.
- For scale: `.scratch` holds 1,553 tracked files against 336 in `twin/`+`talk/`+`tests/`+
  `verify/` combined (`git ls-files | awk -F/ '{print $1}' | sort | uniq -c`).

**Consequence.** Every clone of the hub — including `clone-estate.sh`'s full (non-shallow, by
design) clones in CI — pays for pitch recordings. Not a correctness problem; a friction and
cost one, and it makes the repo's shape misleading (a reader's `git ls-files` is 82% scratch).

**Remedy.** Move the media to a release asset or LFS. Not urgent; note it before the history
grows further.

---

## 3. Strengths (measured, not asserted)

1. **1,550 of 1,551 tests pass, locally and in CI, and the one failure is a pre-registered,
   documented finding.** `1 failed, 1550 passed in 693.95s` locally; byte-identical verdict in
   CI. The failing assertion is `flux_coverage_floor_is_still_reachable`, owned by build ticket
   70. The invariant suite is `70 passed, 1 failed, 3 skipped` — better than the twin map's
   recorded 70/2.
2. **Determinism is real and enforced on three architectures.** Every stochastic path is seeded
   (§1.5); `fair.py summary` reproduced byte-identically across two runs including a
   16-significant-figure float; the `determinism` matrix job passed on aarch64-linux,
   x86_64-linux and arm64-darwin in the same CI run where three other jobs failed, and
   `reproduce-elsewhere` passed too.
3. **No dead code.** I checked every Python module in the hub's `twin/` and in all eight units
   for any reference outside itself (`.py .sh .yml .yaml .md`). **Zero orphans** in either. For
   a 66k-line estate built over two months by one person, that is unusual.
4. **No bare exception handlers.** 261 `except` clauses, zero bare `except:`. Of the 45 that
   swallow, 29 are the negative-test idiom in `twin/invariants/`, and I examined the four
   production ones individually (EQ-10, EQ-11 are the two that matter, both minor).
5. **`compose()` is a genuinely deep module.** `platform/compose/composition.py:2005` — two
   arguments (`adopter_dir`, `parent_trees`), returns `(evidence dict, path→content mapping)`,
   and its docstring's last clause is *"Writes nothing to disk — that is the CLI's job."*
   Verified by reading the body: the whole pipeline is pure. That is a small interface over deep
   semantics, exactly the property the codebase should be judged on.
6. **`fair.py` is the best-shaped module in the estate.** 390 lines, pure stdlib, three CLI verbs
   (`summary`/`compare`/`selfcheck`), one file read, no writes, deterministic, and its selfcheck
   asserts four real properties including that a mixed-currency sum *refuses* rather than adding.
   Its own docstring names it "the load-bearing seam for the whole risk thesis" and the code
   earns that.
7. **Structural guards, not name-matching ones.** `wargamer/tier_pr.py`'s `disposing_calls()`
   does an AST walk after a real planted regression (a rewritten `_open_or_update_pr` calling
   `gh pr merge --squash --admin`) passed the old attribute-name check — recorded in the module's
   own docstring at lines 82-203.
8. **The generated artefacts really are generated.** All three adopters' `composed/policies/
   v4.0.0/*.yaml` are byte-identical to `platform/distribution/policies/v4.0.0/` modulo the
   `composed-for` label and two provenance annotations (`inherited-from: platform@2.0.1`,
   `source-path: distribution/policies/v4.0.0/cage-tier.yaml`), and `render_composed.py` is
   byte-identical across the three after name normalisation. Where the estate says "rendered",
   it is rendered.
9. **No code vendoring.** `driftwood/twin/` is 62 files / 1,446 lines of *data and config only*
   — no hub `twin/*.py` module appears in it (checked by basename against the hub's `twin/`).
   The pin is declared in `PIN.yaml`/`VENDORED.md`.
10. **High and useful comment density.** Measured prose:code ratios of 0.37–0.82 across the core
    engines (`gate.py` 0.82, `verbs.py` 0.80, `composition.py` 0.73, `tier_pr.py` 0.63). The
    comments are not restatements: 180 of them name a specific past defect, often with a date and
    an incident reference. 48 READMEs across the estate.
11. **Type discipline.** 88% return-annotation coverage in the hub, 69% in the units; mypy runs
    over 159 source files in CI and is one stale `type: ignore` away from clean.
12. **Tool supply chain is pinned by checksum.** `truth.yml:39-49` pins gitsign 0.17.1, kyverno
    1.18.2 and cosign 3.1.3 each with an explicit SHA256 — a discipline most estates skip, and
    one that is currently the only reason EQ-02's latent false-pass is not live.
13. **The instrument grades its own honesty, and the one green-while-red case is correct.**
    `verify-e2e-step7-honesty.sh` PASSed in run 21 while step 4 FAILed, and that is right: its
    claim is "every claim above is reported honestly", not "every claim above is true"
    (lines 12-15). Its docstring also states out loud what it cannot catch — a fabricated claim
    with no hedge word. That kind of self-limiting statement is rare and worth crediting.

---

## 4. Corrections to the reader maps

- **`truth-series.md` is wrong about the platform semver suite.** It reports "Platform
  semver/gate suite (7 scripts: verify-comparison-window, verify-coverage, verify-gate,
  verify-rederive-bumps, verify-release-integrity, verify-composition) all FAIL every run 10–21".
  In run 21's own gate log (`gh run view 33616685427 --log`) every one of the ten
  `computed-semver/verify-*.sh` scripts, plus `verify-composition.sh`, grades **PASS**. The full
  run-21 FAIL set is exactly seven: `driftwood/twin/verify-twin-scenarios`,
  `driftwood/verify-reconcile`, `driftwood/verify-twin-overlay`, `ludlow/verify-reconcile`,
  `tuppence/verify-reconcile`, `verify/demo/verify-demo`, `verify/e2e/verify-e2e-step4`.
- **`verify-scripts-units.md`'s open question is now answered.** The three `drift/five-facts.py`
  copies were not byte-diffed by that reader. They are: tuppence and ludlow are identical after
  party-name normalisation; driftwood differs by 61 lines with substantive behaviour differences
  in both directions (EQ-03).
- **`platform-engines.md`'s "3 of 5 tiers" is right about `graded/` but should not be read as
  the served state.** `graded/policies/cage-tier.yaml` carries three rungs; the *served*
  `distribution/policies/v4.0.0/cage-tier.yaml` carries all four of `cage.py`'s `ORDER`.

## 5. REVIEW-2026-08-31 items I can now report on

- **M4 (`verify-corpus-generator`'s SIGPIPE red) is fixed.** Its run-21 capture ends
  `PASS: corpus generator selfcheck ok, spine regenerates byte-identical, sample entry is a real
  Pod` and the gate grades it PASS.
- **Minor "Silent-PASS-on-missing-kyverno in render-version-tree" is fixed** —
  `verify-render-version-tree.sh:23-27` now exits 3 with an explanatory comment — **but six
  sibling scripts in `computed-semver/` still carry the identical defect** (EQ-02). The minor was
  closed on one file, not on the class.
- **M14's "saturated signal" problem has spread.** It named the TRUTH line; it is now also true
  of `twin.yml`, red for 25 runs, where a new typecheck regression arrived unnoticed (EQ-04).
  Ticket 59 remains open.
- I re-raise none of the ten refuted claims.

---

## 6. Verdict

**Maintainable by a human team: not as it stands, but the distance is short and specific.**
The blockers are EQ-01 (no test runner, no types, no lint anywhere outside `twin/`) and EQ-03
(three hand-maintained copies of the adopter surface). Both are structural, both are fixable
without redesigning anything, and the estate already contains the mechanism for EQ-03 — it
publishes and pins signed artefacts for a living. EQ-13 (the README says nothing about how to
run it) is a half-hour fix that materially changes a newcomer's first day.

**Maintainable by an agent alone: yes, and demonstrably so — it is what happened.** The
codebase's strongest maintainability property is agent-legibility: 0.37–0.82 prose-to-code, 180
dated in-code incident notes, 48 READMEs, zero dead modules, 88% type annotation, a self-checking
seam in every module, and a daily gate that grades the whole estate by exit code. An agent can
navigate this well. What an agent cannot supply is the thing EQ-08 measures: a second reader.

**Fit for the purpose the thesis and NORTH-STAR state?** For the purpose of *demonstrating the
thesis on a citable clock* — yes, with two named instrument faults (EQ-02 latent false-pass,
EQ-06 a sixth of the surface unobservable on the clock) and one diagnosability gap (EQ-05). For
the purpose NORTH-STAR §2 implies — an eco-system that other organisations adopt and operate —
no, not yet: an adopting platform team would inherit 28,490 lines of untested Python across
three divergent copies, with 13 tools and no build instructions. The gap between those two
purposes is the real finding of this dimension, and which one is the target is the owner's call.
