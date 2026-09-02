# Gate Mechanics: The Truth Surface

## How a Run Is Produced on the Clock

### Scheduled Trigger
The `truth` workflow runs on a fixed schedule: **05:47 UTC daily** (`.github/workflows/truth.yml:21`), defined as `cron: '47 5 * * *'`.

The run is triggered by GitHub Actions under these conditions:
- Scheduled: daily at 05:47 UTC
- On-demand: `workflow_dispatch` (manual trigger)
- On push: when any of these paths change:
  - `talk/verify-all.sh`
  - `talk/verify-exclusions.txt`
  - `clone-estate.sh`
  - `verify/**`
  - `.github/workflows/truth.yml`

### Unit Repos' Independent Clocks
Eight unit repositories publish on their own UTC schedules (`.github/workflows/truth.yml:16-18`):
- 01:23 platform
- 02:41 nist
- 03:17 feeds
- 04:09 ico
- 05:31 insurer
- 06:11, 06:47, 07:05 driftwood (three separate clocks)
- 08:13, 08:49 tuppence (two separate clocks)
- 09:07, 09:43 ludlow (two separate clocks)

**No cross-org ordering is promised.** The hub's 05:47 truth run grades whatever state it finds in those units at that moment.

### Execution Sequence

1. **Checkout** (`.github/workflows/truth.yml:65-66`): `persist-credentials: false` — no persisted token in git config. This is intentional (see **Observation Cage** below).

2. **Dependencies** (`.github/workflows/truth.yml:67-69`): Install Python 3.12, pyyaml 6.0.3, jsonschema 4.23.0

3. **Clone units** (`.github/workflows/truth.yml:32`): `bash clone-estate.sh` fetches or reuses `.estate-clone/{platform,nist,feeds,ico,insurer,driftwood,tuppence,ludlow}`

4. **Install tools** (pinned by version AND checksum, see next section)

5. **Run the gate** (`.github/workflows/truth.yml:98`, `talk/verify-all.sh`): Discovers and runs every `verify*.sh` script

6. **Record TRUTH line** (`.github/workflows/truth.yml:100-102`): Extract the final TRUTH line from gate output and append to `talk/truth.log`

7. **Observation cage** (`.github/workflows/truth.yml:108-163`): Validate and commit only paths in `OBSERVATION_LANE`

8. **Push** (`.github/workflows/truth.yml:162-163`): Signed push to `HEAD:main` with gitsign

---

## Tools Installed and Version Pinning

Every tool the gate observes with is **pinned by version AND checksum** (`.github/workflows/truth.yml:79-80`).

### gitsign (for signing the commit)
```
GITSIGN_VERSION: 0.17.1
GITSIGN_SHA256: 69213a8a0813a151e5a47d0060862952ff833a845d57309dff76f7ba6600abae
```
**Lines:** `.github/workflows/truth.yml:39-40`, installed at `.github/workflows/truth.yml:70-76`

Installation: Downloads binary from `https://github.com/sigstore/gitsign/releases/download/v${GITSIGN_VERSION}/gitsign_${GITSIGN_VERSION}_linux_amd64`, verifies SHA256, moves to `/usr/local/bin/gitsign`

### kyverno CLI (for offline policy checks)
```
KYVERNO_VERSION: 1.18.2
KYVERNO_SHA256: cb2feb8356149fd2fe774c894ccf0969f4a60a83867dd913af724f74ffbbc18b
```
**Lines:** `.github/workflows/truth.yml:46-47`, installed at `.github/workflows/truth.yml:84-86`

Installation: Downloads tarball from `https://github.com/kyverno/kyverno/releases/download/v${KYVERNO_VERSION}/kyverno-cli_v${KYVERNO_VERSION}_linux_x86_64.tar.gz`, verifies SHA256, extracts `kyverno` binary to `/usr/local/bin/`

**Critical context** (`.github/workflows/truth.yml:41-47`): The estate is authored and specified against kyverno 1.18.2 (documented in `.scratch/ecosystem/research/kyverno-1.18-cage-facts.md`). An unpinned `latest` download became 1.19.0 and reddened three checks for two recorded runs. 1.19 compatibility is real work with its own ticket, not an instrument fix.

### cosign CLI
```
COSIGN_VERSION: 3.1.3
COSIGN_SHA256: 4629c757b7618056f8ddd7e2625ae9fdd94c0372a65049520bc7d9df9efc7f71
```
**Lines:** `.github/workflows/truth.yml:48-49`, installed at `.github/workflows/truth.yml:88-90`

Installation: Downloads binary from `https://github.com/sigstore/cosign/releases/download/v${COSIGN_VERSION}/cosign-linux-amd64`, verifies SHA256, makes executable, moves to `/usr/local/bin/`

### flux CLI
**Lines:** `.github/workflows/truth.yml:91`

Installation: `curl -s https://fluxcd.io/install.sh | sudo bash` — **UNPINNED**. Downloads the latest version from fluxcd.io install script.

### Standard tools
- **git** (pre-installed in GitHub Actions runner)
- **python3** (installed via `actions/setup-python@v5`)
- **openssl** (pre-installed in GitHub Actions runner)
- **jq** (pre-installed in GitHub Actions runner)

### Python dependencies (pyyaml, jsonschema)
**Lines:** `.github/workflows/truth.yml:69`
- `pyyaml==6.0.3` (pinned exact)
- `jsonschema==4.23.0` (pinned exact)

### Installed on local machines (not by workflow)
Per `talk/RUNBOOK.md:58-59`, these CLIs are required:
- `git`, `kind`, `kubectl`, `flux`, `kyverno`, `python3`, `openssl`, `jq`

The offline gate needs: `git`, `python3`, `kyverno`, `openssl`
The live estate also needs: `kind`, `flux`

---

## What the Observation Cage Allows to Be Committed

### The OBSERVATION_LANE
Defined once in the workflow (`.github/workflows/truth.yml:38`):
```
OBSERVATION_LANE: "talk/truth.log drift/samples.jsonl talk/captures observations"
```

These are the only paths the truth workflow may ever commit to `main`.

### Cage Implementation: Three Layers (ADR-0024, section on "The observation lane is a cage")

#### Layer 1: Workflow Cage Step (`.github/workflows/truth.yml:108-162`)
The `observation cage` step:
1. **Reset the index first** (`.github/workflows/truth.yml:118`): `git reset -q` — ensures the index is clean before the cage builds it, preventing staged files from previous steps from being committed silently.

2. **Stage only OBSERVATION_LANE paths** (`.github/workflows/truth.yml:119-123`):
   - For each path in `$OBSERVATION_LANE`, if it exists on disk, `git add -Af -- "${path}"`
   - Force-adds because `talk/captures/` is gitignored for local runs

3. **Assert staged set matches OBSERVATION_LANE** (`.github/workflows/truth.yml:126-138`):
   - For every file in `git diff --cached --name-only`, verify it matches one of the OBSERVATION_LANE paths
   - Fail if any file is staged outside the lane

4. **Assert tree outside lane is clean** (`.github/workflows/truth.yml:140-145`):
   - Check `git status --porcelain --untracked-files=all` for anything unstaged outside the lane
   - Fail if anything exists

5. **Commit with gitsign** (`.github/workflows/truth.yml:149-163`):
   - Set git config to use gitsign for x509 signature
   - **Critical:** signing config in LOCAL config, not on commit command, so `git pull --rebase` replay stays signed
   - Commit message: `truth: record run ${GITHUB_RUN_NUMBER} [skip ci]`
   - Pull rebase (reconcile if remote moved)
   - Push with explicit token credential (not persisted in git config)

#### Layer 2: Server-Side Ruleset (not yet in force)
**ADR-0024, AMENDED 2026-08-28:** `.github/rulesets/observation-lane.json` in each unit repo is **prepared but not in force** because:
- GitHub rulesets do not support per-identity path grants (only deny lists)
- The complement (deny everything except OBSERVATION_LANE) plus admin bypass is possible but
- GitHub allows push rulesets only on private/internal repos, and these are all public

Status: awaiting repositories to go private or a required status check on the default branch.

#### Layer 3: Gate Verification (`verify/schedules/verify-schedules.sh`)
Discovered by `talk/verify-all.sh`, this script:
- Parses every workflow's YAML
- Asserts no scheduled job can `git tag`, `gh release create`, or `gh pr merge`
- Reads inline `run:` shell steps (but not calls to external programs or marketplace actions)
- **Ceiling (named 2026-08-28):** Does not see pushes from inside called programs or from marketplace actions
- Reports capability violations (non-inert `uses:` in a job with `contents: write`)

### What Cannot Be Committed
The cage strictly forbids committing:
- Tiers (control cage assignment decisions)
- Pins (dependency versions)
- Floors (risk appetite constraints)
- Overlays (configuration selections)
- Priced evidence files (computed pricing)
- Published feeds (feed artifacts)

---

## How the TRUTH Line Is Built

### Location and Format
The TRUTH line is printed by `talk/verify-all.sh` as its final line and recorded in `talk/truth.log`.

### Construction (`.talk/verify-all.sh:72-73`)

```bash
echo "TRUTH $(date -u +%Y-%m-%dT%H:%MZ) run=${GITHUB_RUN_NUMBER:-local} hub=$(git rev-parse --short HEAD) units=[${units# }] pass=$pass fail=$fail skip=$skip excluded=$excluded total=${#SCRIPTS[@]}$([ "$REQUIRE_LIVE" = 1 ] && echo " live=1")"
```

Fields:
- **TRUTH**: Literal marker
- **Date**: UTC timestamp in ISO 8601 format (e.g., `2026-09-02T10:11Z`)
- **run**: GitHub Actions run number, or `local` for manual runs
- **hub**: Short SHA of the hub repo's HEAD commit
- **units**: Space-separated `name=sha` pairs for all eight unit repos (e.g., `driftwood=6cf0671 feeds=69c89b0 ...`)
- **pass**: Count of scripts exiting 0 (observed true)
- **fail**: Count of scripts exiting non-zero (observed false, errored, or timed out)
- **skip**: Count of scripts exiting 3 (could not look)
- **excluded**: Count of scripts in `talk/verify-exclusions.txt` not run
- **total**: Total number of discovered scripts (pass + fail + skip + excluded)
- **live=1**: Only present if `--live` flag was used (SKIP becomes FAIL)

### Example (latest from origin/main, run 21)
```
TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 units=[driftwood=6cf0671 feeds=69c89b0 ico=9d09222 insurer=632db22 ludlow=ede531a nist=96154b8 platform=46cd775 tuppence=19cd508] pass=57 fail=7 skip=18 excluded=2 total=84
```

### The Unit Commits Are Snapshots
Each unit's SHA is captured by `talk/verify-all.sh:71` at the moment the script runs:
```bash
for u in .estate-clone/*/; do units="$units ${u#.estate-clone/}"; units="${units%/}=$(git -C "$u" rev-parse --short HEAD 2>/dev/null || echo none)"; done
```

The TRUTH line is citable and dated because **it is committed to `git` with its date alongside it** (`.github/workflows/truth.yml:100-102`), not because it is rebuilt.

### Grading Three Outcomes (`.talk/verify-all.sh:61-68`)

Every script exits with one of four codes:
- **0 (PASS)**: Observed true
- **3 (SKIP)**: Could not look (script's last line must be `SKIP: <reason>`)
- **124 (timeout)**: Script ran longer than `VERIFY_TIMEOUT` (default 300s, overridden to 900s in `.github/workflows/truth.yml:97`)
- **Any other code (FAIL)**: Observed false, errored, or exited with non-standard code

```bash
case $rc in
  0) printf '%-70s PASS\n' "$s"; pass=$((pass+1));;
  3) if [ "$REQUIRE_LIVE" = 1 ]; then printf '%-70s FAIL (live required)  %s  capture: %s\n' "$s" "$last" "$caprel"; fail=$((fail+1))
     else printf '%-70s SKIP  %s\n' "$s" "$last"; skip=$((skip+1)); fi;;
  124) printf '%-70s FAIL (timeout %ss)  capture: %s\n' "$s" "$TIMEOUT" "$caprel"; fail=$((fail+1));;
  *) printf '%-70s FAIL (exit %s)  %s  capture: %s\n' "$s" "$rc" "$last" "$caprel"; fail=$((fail+1));;
esac
```

---

## How the Deck Is Generated and Graded

### The Three Files
1. **Generator:** `talk/build_deck.py` (Python script)
2. **Checker:** `talk/verify-demo.sh` (bash script, discovered by gate as `verify/demo/verify-demo.sh`)
3. **Prose and narration:** `talk/narration.json` (JSON with slide definitions and narration)

### Generation: `talk/build_deck.py`

**Declared rule (`.talk/build_deck.py:1-26`):** GENERATED, NOT AUTHORED. Hand editing `talk/deck.md` is not an option; the next build overwrites it.

**What it reads at build time:**
- `talk/narration.json`: Slide definitions, titles, narration, script references
- `talk/captures/` (one `.out` file per script): The actual output of each verify script
- `talk/truth.log`: To quote the TRUTH line for this exact commit

**What it produces:**
- `talk/deck.md`: A Marp markdown presentation with seven numbered steps (the NORTH-STAR section 4 steps)

**Build order caveat (`.talk/build_deck.py:45-59`):** 
Inside a scheduled gate run, a script that sorts after `verify/demo/` has not rewritten its capture yet, so its beat quotes the **previous run's capture**. The deck says "built during run N" and not "run N produced every figure here."

### Beat Status Determination (`.talk/build_deck.py:169-193`)

For each beat, the generator determines `(tag, reason, rows, cited)`:

1. **Read the capture** from disk (`talk/captures/<script-slug>.out`)
2. **Grade the last line**: Parse the capture's last non-empty line for:
   - `PASS: <reason>` → tag="PASS"
   - `SKIP: <reason>` → tag="SKIP"
   - `FAIL: <reason>` → tag="FAIL"
   - No valid prefix → tag="FAIL" with message "the capture's last line does not carry a PASS:, SKIP: or FAIL: verdict"

3. **Apply `scheduled_only` downgrade** (`.talk/build_deck.py:186-191`):
   - If a beat has `"scheduled_only": true` in `narration.json` AND this is a **local build** (not `GITHUB_RUN_NUMBER`), downgrade PASS to SKIP with a reason explaining the deck doesn't show it green on a local run
   - SKIP and FAIL are **never** downgraded — a green that couldn't look is not a soft pass

### Verification: `talk/verify-demo.sh`

This script **refuses the deck** when any of these conditions hold (`.talk/verify-demo.sh:6-20`):

#### Build Phase (runs everywhere)
1. **Rebuild** from captures: `python3 talk/build_deck.py --out "$TMP/deck.md"`
   - Fails if the build fails

2. **Rebuild survives its own checks**: `python3 talk/build_deck.py --check "$TMP/deck.md"`
   - Every check below is run on the rebuilt deck

3. **Committed file is generated**: `grep -q "GENERATED FILE" talk/deck.md`
   - The file must carry the generated-file marker

4. **Seven steps in order**: Steps 1-7 of NORTH-STAR section 4, in order
   - `.talk/verify-demo.sh:62-70`: All seven step check scripts must exist on disk and must have captures

5. **Figure check** (`.talk/build_deck.py:310-379`):
   - Every money amount, percentage, or count on a beat body must appear verbatim in that beat's capture
   - Set membership check: `"8,269.23"` is inside `"58,269.23"` and does not pass
   - Figures may **only** appear on beat slides, never on prose slides
   - Headers, dates, tags, ticket numbers, ADR references, step numbers, command lines (`$ bash ...`), and marp directives are **outside** the check

6. **Phrase lint** (`.talk/build_deck.py:278-387`):
   - Four refused phrases (exact, case-insensitive): exemption, hourglass, admission gate, deny gate
   - Fail if any appears anywhere in the deck
   - Every other use of "gate" is printed for human review but doesn't fail

#### Scheduled-Run-Only Phase (`.talk/verify-demo.sh:82-130`)
**Two checks are graded ONLY on the scheduled run** (when `GITHUB_RUN_NUMBER` is set):

1. **Committed deck's beats match a rebuild** (`.talk/verify-demo.sh:100-103`):
   - Compares `beat step=N status=X` markers in committed file vs. rebuild
   - Fails if they differ (hand edited or stale)

2. **Committed deck survives figure and status checks** (`.talk/verify-demo.sh:124-125`):
   - Runs the full check suite on the committed `talk/deck.md` itself
   - A local gate run has just overwritten `talk/captures/`, so the figures would be from a different run
   - On the scheduled run, the captures are the ones the deck was built from

**Why scheduled-only?** (`.talk/verify-demo.sh:82-88`)
- A local gate run overwrites `talk/captures/` with its own results
- Comparing the committed deck against a rebuild here compares two different runs
- The deck was rebuilt and committed three times on 2026-08-31 and was "stale" again within the hour off the clock
- The scheduled truth workflow writes the captures and commits the deck in one lane, where the comparison is honest

#### Optional: Marp Rendering (`.talk/verify-demo.sh:132-137`)
If `DECK_RENDER=1` is set, the script also checks:
- `npx @marp-team/marp-cli@latest --html` can render the deck to HTML
- This fetches from the network and is not run by the gate (offline constraint)

### Selfcheck
`talk/build_deck.py --selfcheck` (invoked by `.talk/verify-demo.sh:74`) validates:
- Slug computation
- Grade parsing
- Figure detection (set membership)
- Line selection and wrapping
- Downgrade behavior (PASS can downgrade to SKIP, others cannot)
- Beat rendering logic

---

## The Two Exclusions

### Definition
Located in `talk/verify-exclusions.txt` (`.talk/verify-all.sh:30`), which lists scripts that are discovered but not run, with their reasons.

**Format:** One line per exclusion, `path | reason`, with comment support (`#`)

**Validation** (`.talk/verify-all.sh:34-43`):
- Every listed path must still exist on disk (if removed, the gate FAILs)
- Every path must have a reason (if missing, the gate FAILs)
- Any path not listed but discovered is itself a FAIL

### The Two Exclusions (from `talk/verify-exclusions.txt`)

#### 1. `.estate-clone/ico/schema/verify.sh`
```
.estate-clone/ico/schema/verify.sh | takes a version-dir argument; run twice by .estate-clone/ico/verify-penalty-feed.sh (v1, v2)
```

**Reason:** This script takes a version-dir argument and cannot be called without one. The parent script `verify-penalty-feed.sh` calls it twice (for versions v1 and v2) with the correct arguments. Running it standalone by the gate would fail.

#### 2. `.estate-clone/platform/feeds/verify.sh`
```
.estate-clone/platform/feeds/verify.sh | takes feed/version/file arguments; run by .estate-clone/platform/honesty/verify-honesty.sh
```

**Reason:** This script takes feed, version, and file arguments and cannot be called without them. The parent script `verify-honesty.sh` calls it with the correct arguments. Running it standalone by the gate would fail.

### Validation Loop (`.talk/verify-all.sh:45-52`)
The gate discovers scripts by glob: `find .estate-clone verify -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*'`

For each discovered script, if its path is in the exclusions map, it is marked EXCLUDED and not run. Any path in the exclusions file that no longer exists causes the gate to FAIL.

---

## The Timeout

### Default and Override
**Default:** `VERIFY_TIMEOUT=300` (5 minutes, `.talk/verify-all.sh:29`)

**Scheduled run override:** `VERIFY_TIMEOUT=900` (15 minutes, `.github/workflows/truth.yml:97`)

### Timeout Behavior (`.talk/verify-all.sh:58`)
```bash
timeout "$TIMEOUT" bash "$s" >"$cap" 2>&1; rc=$?
```

When a script runs longer than the timeout:
- `timeout` sends SIGTERM and the script exits with code 124
- The gate grades this as FAIL (timeout) (`.talk/verify-all.sh:65`)
- The table row shows: `FAIL (timeout 900s)  capture: <path>`

### Slowest Scripts Reporting (`.talk/verify-all.sh:75-79`)
After the TRUTH line, the gate reports the slowest five scripts by wall-clock time so drift toward the timeout is visible before it happens:
```bash
echo "SLOWEST 5 (seconds, wall-clock; timeout is ${TIMEOUT}s):"
printf '%s\n' "${durs[@]}" | sort -rn | head -5 | awk '{printf "  %4ss  %s\n", $1, $2}'
```

---

## Every Way the Number Could Be Wrong

The TRUTH line's counts (`pass`, `fail`, `skip`, `excluded`, `total`) can be wrong in the following ways:

### Script-Level Misclassification

#### 1. A Script Counted as PASS That Observed Nothing
**Scenario:** A script exits 0 but produces no actual check output or verification.

**How it happens:**
- The script writes no output but succeeds
- The gate only checks the exit code, not the output content (`.talk/verify-all.sh:61-62`)

**Detection:** Would not be caught by the gate itself, but:
- `talk/verify-demo.sh` checks that every seven-step script produces a capture with a valid verdict line
- `talk/build_deck.py` reads the last line and grades it; if empty or malformed, tags as FAIL

#### 2. A SKIP That Hides a Permanent Inability
**Scenario:** A script returns 3 (SKIP) with a reason that sounds temporary but is actually permanent.

**How it happens:**
- Example: `SKIP: no Running pod to carry the cage` (from `.talk/build_deck.py:437`)
- The check cannot observe its target because the cluster is not running or the cage is not in place
- On the scheduled run with `--live`, this would become a FAIL (`.talk/verify-all.sh:63`)
- On an offline run, it silently counts as a SKIP, so a broken check appears as "could not look" rather than "observed false"

**Design rule** (`.talk/RUNBOOK.md:226-227`): "a green that could not look is a red." The gate enforces this with `--live` (used in `.github/workflows/truth.yml`).

#### 3. A FAIL That Is the Instrument, Not the Estate
**Scenario:** A check fails because a tool is misconfigured, unpinned, or incompatible with the check.

**Examples from the codebase:**
- Unpinned kyverno upgrading from 1.18.2 to 1.19.0 reddened three checks (`.github/workflows/truth.yml:41-47`)
- A tool like `flux` being unpinned (`.github/workflows/truth.yml:91`) could silently shift behavior

**Mitigation:**
- Every observation tool is pinned by version AND checksum (gitsign, kyverno, cosign)
- `flux` is **not** pinned (design choice trade-off)
- The TRUTH line records the hub commit and unit commits, not tool versions

#### 4. A Script Timing Out When It Shouldn't
**Scenario:** A script runs longer than 900s on the scheduled run.

**How it happens:**
- Network latency, slow image pulls, or a quadratic algorithmic issue in a check
- The timeout is wall-clock time, not CPU time
- The slowest five scripts are printed, so creep toward the timeout is visible

#### 5. An Excluded Script That Shouldn't Be
**Scenario:** A script is listed in `talk/verify-exclusions.txt` with a stale reason.

**How it happens:**
- The parent script that was supposed to call it is deleted or renamed
- The reason becomes obsolete but the exclusion remains

**Detection:**
- The gate FAILs if a script in the exclusions file no longer exists (`.talk/verify-all.sh:41`)
- The gate FAILs if a script has no reason (`.talk/verify-all.sh:40`)

#### 6. A Script Discovered That Shouldn't Be
**Scenario:** A new script is checked in to the estate, the gate discovers it, but no one added it to the exclusions.

**How it happens:**
- A helper script is committed with a name matching `verify*.sh`
- It's not a standalone gate script but a library or dependency
- The gate treats it as a gate script and runs it, causing an unexpected FAIL or including an unexpected PASS

**Detection:** No automatic detection. This requires human review of discovered scripts.

### Gate-Level Miscounting

#### 7. Off-by-One in Script Count
**Scenario:** A script that fails to execute (not found, permission denied) is miscounted.

**How it happens:**
- The glob in `.talk/verify-all.sh:45` finds it
- But it exits non-zero with a system error (not caught by the shell)
- Unlikely because the loop runs `bash "$s"`, which would exit non-zero and be counted as FAIL

#### 8. Exclusion File Rot Not Caught
**Scenario:** A path in `talk/verify-exclusions.txt` is deleted but the validation in `.talk/verify-all.sh:41` is skipped or broken.

**How it happens:**
- The check exists: `[ -e "$p" ] || { echo "FAIL exclusions: '$p' no longer exists, remove it"; fail=$((fail+1)); }`
- If this check is removed or the file is not parsed correctly, stale exclusions would silently remain

#### 9. Unit Commits Not Captured Correctly
**Scenario:** A unit's SHA is captured incorrectly in the TRUTH line.

**How it happens:**
- The loop in `.talk/verify-all.sh:71` reads `git -C "$u" rev-parse --short HEAD 2>/dev/null`
- If a unit repo fails to clone or is corrupted, it returns `none` and records that
- An incomplete or shallow clone could return the wrong commit

**Mitigation:** `clone-estate.sh` does a **full clone**, not a shallow or partial one (`.clone-estate.sh:40-56`), ensuring tag history and files are present.

### Deck-Level Miscount

#### 10. Deck Cites a Missing Capture
**Scenario:** `talk/build_deck.py` generates HTML referencing a capture that doesn't exist.

**How it happens:**
- A beat in `narration.json` references a script that did not produce a capture in this run
- `beat_status()` returns `("NOCHECK", "owned by ticket NN", [], False)`

**Detection:** `talk/verify-demo.sh` catches this:
- (`.talk/verify-demo.sh:62-70`) asserts all seven step checks exist on disk and have captures
- (`.talk/verify-demo.sh:79`) asserts every cited capture exists before the check passes

#### 11. Deck Figure Check Passes a Hand-Typed Number
**Scenario:** A figure on a beat slide is hand-typed, not read from the capture.

**How it happens:**
- A presenter edits the deck and types a number that matches one in the capture by coincidence
- Or a number from a different section of the capture is quoted

**Detection:**
- `talk/build_deck.py` implements a set membership check (`.talk/build_deck.py:355-358`)
- `talk/verify-demo.sh --check` runs this check on the committed deck on the scheduled run (`.talk/verify-demo.sh:124`)

#### 12. Deck Quotes a TRUTH Line from a Different Commit
**Scenario:** The deck quotes `TRUTH 2026-09-01T...` but this deck was built at a different commit.

**How it happens:**
- The presenter manually edits the deck and quotes a stale TRUTH line from an earlier run
- The deck was rebuilt but a TRUTH line was manually added from a different commit

**Detection:** (`.talk/build_deck.py:388-400`)
- The generator reads the deck's quoted TRUTH line
- It searches `talk/truth.log` for that exact line
- It extracts the hub SHA from the line and compares to the current commit
- Fails if the TRUTH line was recorded at a different hub commit

---

## Summary: The Critical Path

A TRUTH line is **citable and correct** when:

1. **All tools are pinned and installed correctly** — gitsign, kyverno, cosign, flux, python, openssl, jq
2. **All eight units are cloned fully** and at their current default-branch commits
3. **Every discovered script runs and exits** with 0 (PASS), 3 (SKIP with reason), or non-zero (FAIL)
4. **Exclusions are current** — no stale paths, every path has a reason
5. **Captures are committed** — the observation cage ensures only OBSERVATION_LANE paths are staged
6. **The TRUTH line is recorded with its date** — appended to `talk/truth.log` and committed to git
7. **The deck is generated and checked** — `talk/build_deck.py` reads captures, `talk/verify-demo.sh` verifies them
8. **The deck carries generated-file marker** — not hand-edited
9. **Every figure on the deck is in its capture** — set membership, verbatim match
10. **Quoted TRUTH line matches this commit** — `hub=` in the TRUTH line is this deck's own commit

The gate graces the estate with three outcomes (PASS, SKIP, FAIL), names the reason, and records them all in git on the hour.
