# The truth surface (NORTH-STAR §5) as an instrument

Auditor assessment, 2026-09-02. Citable base: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 units=[driftwood=6cf0671 feeds=69c89b0 ico=9d09222 insurer=632db22 ludlow=ede531a nist=96154b8 platform=46cd775 tuppence=19cd508] pass=57 fail=7 skip=18 excluded=2 total=84` (`talk/truth.log`, last line on `origin/main`).

Method: I read `talk/verify-all.sh`, `.github/workflows/truth.yml`, `clone-estate.sh` and `talk/verify-exclusions.txt` in full; pulled the complete run-21 CI log (`gh run view 33616685427 --log`) and extracted all 84 grade rows; extracted all 82 run-21 capture files from `origin/main:talk/captures/` and read every one of them (3,838 lines); read the scripts behind every claim I make; and re-derived the live half independently with read-only `gh`. Where I could not look, I say so.

---

## 1. What the instrument is, measured

### 1.1 The grade table, re-derived

```
$ gh run view 33616685427 --log | grep -oE '(\.estate-clone|verify)/[^ ]*verify[^ ]*\.sh +(PASS|SKIP|FAIL|EXCLUDED)' \
  | awk '{print $2}' | sort | uniq -c
   2 EXCLUDED
   7 FAIL
  57 PASS
  18 SKIP
```
84 rows; matches the TRUTH line exactly. `total` is `${#SCRIPTS[@]}` (`talk/verify-all.sh:72`), i.e. discovered-including-excluded, so `pass+fail+skip+excluded = total`.

By owning repository:

| repo | PASS | SKIP | FAIL | EXCLUDED | total |
|---|---|---|---|---|---|
| platform | 29 | 15 | 0 | 1 | 45 |
| hub (`verify/`) | 13 | 1 | 2 | 0 | 16 |
| driftwood | 1 | 0 | 3 | 0 | 4 |
| feeds | 3 | 0 | 0 | 0 | 3 |
| ico | 3 | 0 | 0 | 1 | 4 |
| insurer | 1 | 1 | 0 | 0 | 2 |
| ludlow | 2 | 0 | 1 | 0 | 3 |
| nist | 3 | 0 | 0 | 0 | 3 |
| tuppence | 2 | 1 | 1 | 0 | 4 |

**Platform owns 45 of 84 rows and contributes 29 of the 57 passes (51%) and 15 of the 18 skips (83%).**

### 1.2 Observation vs self-proof vs simulation — my own classification

Rule used: a script is an **eco-system observation** if its verdict depends on the current content of an artefact published by a party *other than the one that owns the script*, or on live external state (a real remote, Rekor, the GitHub API). It is a **self-proof** if the owning party is grading its own code, fixtures or artefacts. It is a **simulation** if the verdict depends only on synthetic material the script constructs in a temp dir.

Of the 57 passes on run 21:

| class | count | examples (verified from the run-21 capture) |
|---|---|---|
| eco-system observation (cross-party or live) | **20** | `verify/feed-contract` (22 real cross-party pins resolved against real remotes); `verify/e2e/step6` (7 real Fulcio certs + Rekor); `platform/compose/verify-composition` (the real driftwood composed against its 5 real pinned parents, £3,704,381.74 exposure); `verify/renovate` (driftwood's real merge record for PR #20); `ico/verify-penalty-feed` §8 (`git ls-remote` against nist's real remote); `verify/party`, `verify/pound-seam`, `verify/proportionality`, `platform/oscal/verify-claims`, `platform/distribution/verify-infra-declaration` |
| self-proof (own code/fixtures/artefacts) | **31** | all 10 `computed-semver/verify-*.sh`; `fair`, `tcor`, `honesty`, `wardley`, `wargamer`, `risk`, `party-artefact`, `break-glass`, the four cert-identity-regexp scripts, `twin-evals` |
| simulation (synthetic material only) | **5** | `platform/verify-cut-release-tags` (throwaway repos under `/tmp/tmp.lnaTmCv8ez`); `ludlow/verify-adopter-gate` (throwaway platform+ludlow repos); `platform/oscal/verify-upflow` (self-generated PolicyReports); `verify/e2e/step3` (its own capture: "a SYNTHETIC residual ... not driftwood's real priced position"); `verify/provenance` (a narrative chain over committed fixtures) |
| meta (grades other steps' reporting honesty) | **1** | `verify/e2e/step7` |

**Honest recount: 20 of 84 discovered scripts (24%) both passed and observed a fact spanning more than one party or reaching live external state.** The remaining 37 passes are a party grading itself, a simulation, or a meta-check. That is not a fraud: those checks are real regression tests and several are excellent. It is a statement about what `pass=57` means.

### 1.3 Live runtime: zero

Every mention of a cluster in all 82 run-21 captures is either a SKIP reason or a *replay* of a JSONL line another repo's CI recorded earlier:

```
$ grep -h "five-fact sample 20" talk/captures/*   # run-21 captures
   five-fact sample 2026-09-01T21:04:18Z on cluster dsample-33558858820 (run 33558858820), 3 sources
   five-fact sample 2026-09-01T21:04:23Z on cluster dsample-33558854558 (run 33558854558), 3 sources
   five-fact sample 2026-09-01T21:07:22Z on cluster dsample-33558850420 (run 33558850420), 3 sources
```
The gate ran at 2026-09-02T10:11Z. **No script in the whole run read a live Kubernetes API.** NORTH-STAR §4 step 4's evidence is a thirteen-hour-old recording, and by declared cron it will always be at least a day old (see F-05).

---

## 2. The pass ceiling is structurally below 84 — compute

`.github/workflows/truth.yml` contains no `kind create`, no `docker`, no cluster bring-up of any kind (`grep -n "kind create\|kind get clusters\|docker" .github/workflows/truth.yml` → no matches). The gate step also carries no `GH_TOKEN` (only the later cage step does, lines 121-123). Both absences are deliberate and documented.

Consequence, from run 21's own SKIP reasons:

| class | count | scripts |
|---|---|---|
| needs a persistent `kind` cluster named `driftwood` the runner never has → can only be SKIP or FAIL, never PASS | **11** | `platform/{access,currency-controller,engine,eud,graded,posture/posture-projection,verify-source-verification}`, `platform/distribution/verify-declared-versions-admit`, `platform/identity/{verify-identity,verify-federation}`, `tuppence/reset/verify-reach-secrets` |
| needs cross-org GitHub auth the gate step deliberately withholds → `exit 3` always | **1** | `verify/schedules/verify-schedules.sh` |
| excluded, never graded | **2** | the two parameterised scripts |
| blocked by the estate declaring exactly one policy version (4.0.0) | **5** | `distribution/verify-coexistence`, `distribution/verify-retirement`, `shift-left/verify-shift-left`, `policy/verify-conditional` (its subject 2.0.1 is retired), `verify-publisher-gate` (part C: "needs at least three declared versions and distribution/versions.yaml declares ['4.0.0']") |

```
structural ceiling  = 84 − 2 excluded − 11 cluster-bound − 1 schedules = 70
reachable today     = 70 − 5 one-version                              = 65
                      (− 1 more for insurer's honest quote-staleness SKIP = 64)
observed run 21     = 57
```

`pass=57 … total=84` therefore invites `57/84 = 68%`. The defensible ratios are **57/64 of what is reachable today** and **57/70 of the structural maximum**. Nothing in the instrument, the deck, the map or any ticket states a ceiling, and nothing checks one. This is why `fail=0` has never happened in 18 recorded runs and, for the 11+1 group, cannot be read as a health signal at all.

---

## 3. The seven reds: estate or instrument?

| # | script | verdict line (run-21 capture) | class | owner |
|---|---|---|---|---|
| 1 | `driftwood/verify-reconcile.sh` | fact 2 false: "certificate is not yet valid" at tagger time 1787677714 | **estate** (verifier clock-skew) | ticket 73, open |
| 2 | `verify/e2e/step4` | *the same sample line*, same cluster `dsample-33558850420` | **estate**, duplicate of #1 | ticket 73 |
| 3 | `ludlow/verify-reconcile.sh` | facts 2,3,4,5 false; "16 of 16 rendered objects are in no Flux inventory" | **estate** | ticket 62/74 |
| 4 | `tuppence/verify-reconcile.sh` | same shape | **estate** | ticket 62/74 |
| 5 | `driftwood/verify-twin-overlay.sh` | "twin/forward-intel/v1/feed.json is not what the overlay renders" | **estate** | ticket 72, open |
| 6 | `driftwood/twin/verify-twin-scenarios.sh` | 2 fails: the same feed re-render, plus a pin/signal mismatch (`no row for: feeds/feed/threat-register/v2`) | **estate**, shares a root cause with #5 | ticket 72 |
| 7 | `verify/demo/verify-demo.sh` | "talk/deck.md has been hand edited or is stale" | **instrument/process** — structurally unfixable on the clock | ticket 66, open |

So: **6 of 7 reds are real estate faults with named owning tickets; 1 is an instrument fault.** The seven rows collapse to **four distinct defects** (cert skew; ludlow/tuppence objects absent; the twin feed re-render; the stale deck) — the tally double-counts. That is honest but it means "fail=7" overstates the number of things to fix and understates how much of it is one bug.

A note in the estate's favour: `verify/e2e/step7` PASSes in the same run while step 4 FAILs. That is correct by design — step 7 only checks that each step reported *honestly* (`verify/e2e/verify-e2e-step7-honesty.sh:12-15`), and its own output reads `verdicts: PASS PASS PASS FAIL PASS PASS PASS`. It is not a contradiction.

---

## 4. Scripts that can PASS while a named part could not look

NORTH-STAR §5 bullet 2: "Every live tail has exactly three outcomes." Principle 6: "A green that could not look is a red." Both are violated, in at least seven scripts, in three different shapes.

### 4a. Demonstrated: `exit 0` after printing its own SKIP

```
$ cd units/platform/computed-semver
$ env PATH=/usr/bin:/bin bash verify-cage-engine.sh; echo "EXIT=$?"
SKIP: kyverno CLI not found -- cage_engine's Track 1 (ValidatingPolicy admission) needs it
EXIT=0
$ bash verify-cage-engine.sh >/dev/null 2>&1; echo "EXIT=$?"
EXIT=0
```
Both branches exit 0. `talk/verify-all.sh:64` grades 0 as PASS. The gate cannot distinguish "observed true" from "could not look".

Six scripts carry the whole-script form (`grep -n "command -v kyverno" -A4 verify-*.sh`): `verify-cage-engine.sh:12-15`, `verify-comparison-window.sh:11-14`, `verify-gate.sh:11-14`, `verify-rederive-bumps.sh:9-12`, `verify-generator-standing-check.sh:18-21`, and `verify-corpus-generator.sh:34-37` (step 3 only). `verify-witness-set.sh:68-71` prints the SKIP text for step 5 and falls through to PASS.

Run 21 had kyverno 1.18.2 present, so today's six PASSes are real. The defect is latent, not active — but it is exactly the class the estate itself named a "2026-08-25 incident" and fixed in `distribution/verify-render-version-tree.sh`. The 2026-08-31 review recorded it as a minor **scoped to render-version-tree alone**; ticket 55's text names only that script. The six siblings are unowned.

### 4b. Scripts with no `exit 3` path at all

`verify/proportionality/verify-proportionality.sh` and `verify/provenance/verify-provenance.sh` both use `set -euo pipefail` and have no could-not-look branch. Their run-21 captures:

- proportionality: `==> 5. live dry-run tail skipped (no cluster with Kyverno CRDs reachable) — offline proof stands` → `PASS`.
- provenance: section 3 (`rekor-cli present — searching the transparency log`) and section 4 (SPIRE) both degrade to a printed note → `PASS: … Provenance for every actor, end to end.`

Two of five sections in `verify-provenance` are structurally unobservable on the runner and it PASSes with a maximal claim every single run.

Minor sub-finding: that capture prints "gitsign present … but no rekor-cli/cosign to query the log", yet truth.yml installs cosign 3.1.3 to `/usr/local/bin`. The detection at `verify/provenance/verify-provenance.sh:55` tests `have rekor-cli` only; the message about cosign is wrong.

### 4c. Unchecked checks reported as NOTE, not SKIP

`insurer/verify-insurer-party.sh` → PASS, with four lines it did not check:
```
NOTE: driftwood/feed:exposure@v1.1.0: no Flux/Renovate pin exists for this kind in this estate today -- declared version not checked here
NOTE: tuppence/feed:exposure@v1.1.0: … NOTE: ludlow/feed:exposure@v1.1.0: … NOTE: baseline mirror not checked
OK: … every check that could run agrees (any it could not is a NOTE above)
```
Source: `platform/party/party_artefact.py:369-379` appends a note and `continue`s; the caller exits 0. The same pattern appears in `platform/party/verify-party-artefact.sh`. It is honest in the transcript and invisible in the number. `verify/feed-contract` does compensate (it checks those tags against the real remotes and PASSed), so the risk here is presentational, not a hidden falsehood.

Also in this class, both honestly named: `feeds/verify-news-headline-skill.sh` → "no adopter repo carries a claim file yet -- the skill has not been run for real" → PASS; `platform/oscal/verify-upflow.sh` → "schema-validation tail skipped: compliance-trestle CLI not installed" → PASS.

---

## 5. The two exclusions

`talk/verify-exclusions.txt` holds exactly two entries, both parameterised scripts run by a parent:

- `.estate-clone/ico/schema/verify.sh` — proven run by its parent in the same run: the `ico/verify-penalty-feed` capture shows `Signature Verified Successfully` twice, once for v1 and once for v2.
- `.estate-clone/platform/feeds/verify.sh` — proven run by `platform/honesty/verify-honesty.sh`: its capture shows `ok live feed signature verifies; a forged feed is rejected`.

The list is self-checking in both directions (`talk/verify-all.sh:39-45`): a missing reason fails the gate, and a listed path that no longer exists fails the gate. **This mechanism is sound and I found nothing wrong with it.** It is a strength.

---

## 6. The unpinned flux install vs "every tool pinned"

`.github/workflows/truth.yml:76-91`, one step:

```yaml
      - name: kyverno, cosign, flux CLIs the offline proofs call
        # Every tool the gate observes with is pinned by version AND checksum, like gitsign
        # above. An unpinned tool makes the number unreproducible: the same estate grades
        # differently on two days for a reason no TRUTH line records.
        run: |
          set -euo pipefail
          curl … kyverno.tgz … ; echo "${KYVERNO_SHA256}  kyverno.tgz" | sha256sum -c -
          curl … cosign      ; echo "${COSIGN_SHA256}  cosign"       | sha256sum -c -
          curl -s https://fluxcd.io/install.sh | sudo bash
```

The claim and its counter-example are fifteen lines apart in the same step. `flux` is fetched unversioned and unchecksummed from a third-party URL and executed as root. Three consequences, in increasing order of seriousness:

1. The comment is false as written; the reproducibility argument it makes applies to flux exactly as to kyverno.
2. Whoever controls `fluxcd.io/install.sh` gets root on the runner that also holds `contents: write` for the hub.
3. It appears to be a real availability risk already: **run 14 died in this step**.
   ```
   $ gh run view 33435351306 --log | grep "kyverno, cosign, flux"
   … kyverno.tgz: OK
   … Version: 1.18.2
   … ##[error]Process completed with exit code 141.
   ```
   Exit 141 is SIGPIPE; the step contains three pipelines and died after `kyverno version` printed. `talk/truth.log` has no `run=14` line — it jumps 13 → 15 — and nothing in the estate notices. (Runs 1, 2 and 3 are missing too.)

I could not find any ticket, ADR, GAPS row or map line naming the flux install. The 2026-08-31 review's minor list names "cosign unpinned on the clock" — that one is now fixed (`COSIGN_VERSION: 3.1.3`, `COSIGN_SHA256: 4629c757…`) — but flux was never named. **This is an orphan.**

---

## 7. "A fall is a blocking event" and "Status derived from a named check"

Neither exists.

- **A fall is a blocking event.** `grep -rn "truth.log" talk/ verify/ .github/` returns only writers (`truth.yml:5,38`, the record step) and the deck builder, which quotes the newest line. Nothing reads two lines and compares them. Run 17 → 18 fell `pass=59 fail=1` → `pass=57 fail=3` and the workflow's conclusion was `failure` on both runs, exactly as on every other run — the fall was invisible because the signal is saturated. Across the 21 CI runs, 17 failed at `fail if the gate failed` and there has never been a run with `fail=0`.
- **Status derived from a named check.** Concrete, checkable instance found today: ticket 55's fixes are *merged into platform main* —
  ```
  $ git -C units/platform log --oneline -2
  46cd775 Merge pull request #8 from policy-as-versioned-platform/ticket-55-instrument-faults
  04184df Every red on the clock is real, explained, and finishable (ticket 55)
  ```
  `46cd775` is the exact platform SHA in run 21's TRUTH line, and the fixes are visibly working (source-verification now prints "it ACCEPTS the real signed tag"; corpus-generator's `ls|head` is gone, replaced by a glob with a comment explaining why). Yet `.scratch/ecosystem/issues/55-*.md` still reads `Status: prepared`, and its Answer still says "They are NOT on the platform repo."

Both are owned by **ticket 59 (open)**, charted by the 2026-08-31 review as M14. Not orphans. Still unbuilt after two days and eight runs.

---

## 8. `verify-demo` red on every scheduled run — the mechanism

Run-21 capture:
```
  the committed deck's beats differ from a rebuild:
    < beat step=1..6 status=SKIP        (the committed talk/deck.md)
    > beat step=1 PASS  2 PASS  3 PASS  4 FAIL  5 PASS  6 PASS   (this run's captures)
FAIL: talk/deck.md has been hand edited or is stale; run python3 talk/build_deck.py
```
Grade history, read from the capture at each `truth: record run N` commit:
```
run 10,11,12  PASS
run 13,15,16,17,18,19,20,21  FAIL   (eight consecutive runs, since 2026-08-31T17:22Z)
```

Why it cannot be fixed on the clock, from primary sources:

1. `.github/workflows/truth.yml:38` — `OBSERVATION_LANE: "talk/truth.log drift/samples.jsonl talk/captures observations"`. `talk/deck.md` is not in it, and the cage step fails the run on anything outside the lane. The clock **may not** commit a rebuilt deck.
2. `grep -rn "build_deck\|deck" .github/workflows/` → **no matches**. There are exactly two workflows (`truth.yml`, `twin.yml`) and neither builds the deck. Yet `verify/demo/verify-demo.sh:33-36` asserts: "The committed deck is built by the scheduled workflow AFTER verify-all.sh finishes, which is where 'the live run id is the scheduled one' is kept." **That workflow step does not exist.**
3. Run 21's commit `a209496` changed 12 capture files. So any deck a human rebuilds and commits goes stale on the next run whose grades or figures move — which is most runs.

The check itself is good and its refusals are precise. The fault is that its premise names machinery nobody built. Owned by **ticket 66 (open)**; my contribution is the direct evidence that the named scheduled build does not exist anywhere and that the lane forbids it.

Reader-facing consequence: the committed `talk/deck.md:27` currently says "`talk/truth.log` records no run of the truth surface at this commit, so this deck quotes no headline number", and every beat reads SKIP. The shipped deck therefore shows nothing green — a *pessimistic* stale artefact, not an optimistic one.

---

## 9. `verify-schedules` cannot see the clocks — and the clocks are red

`verify/schedules/verify-schedules.sh:38-48`: any per-clock SKIP makes `schedules.py check` return 3 and the wrapper `exit 3`. `schedules.py` needs `gh auth status` plus cross-org read on eight separate GitHub orgs; the gate step in `truth.yml` carries no credential at all. Run-21 capture: **14 SKIP lines**, every one `GitHub unreachable (Command '['gh', 'auth', 'status']' returned non-zero exit status 1.)`. This is structural: `verify-schedules` can never PASS from inside a scheduled truth run.

Worse, the server-side-cage half **vanishes rather than SKIPping**: `verify/schedules/schedules.py:561` guards the ruleset check with `if live and …`, and `live` is false, so nothing prints at all —
```
$ grep -c -i ruleset talk/captures/verify_schedules_verify-schedules.out
0
```
That is a fourth outcome — *not evaluated, not reported* — which §5 bullet 2 does not allow.

What the blindness costs, verified independently by me with read-only `gh`:
```
$ gh run list --repo policy-as-versioned-feeds/feeds     --event schedule --limit 2
2026-09-02T07:54:14Z failure fetch      2026-09-01T08:37:50Z failure fetch
$ gh run list --repo policy-as-versioned-insurer/insurer --event schedule --limit 2
2026-09-02T09:45:30Z failure fetch      2026-09-01T10:16:02Z failure fetch
$ gh run list --repo policy-as-versioned-driftwood/driftwood --event schedule --limit 6
2026-09-02T12:04:10Z failure twin-sweep …
$ gh run list --repo policy-as-versioned-tuppence/tuppence  --event schedule --limit 6
2026-09-02T12:59:15Z failure propose-tier   2026-09-01T13:32:59Z failure drift-sample
$ gh run list --repo policy-as-versioned-ludlow/ludlow      --event schedule --limit 3
2026-09-01T14:17:44Z failure propose-tier   2026-09-01T14:07:55Z failure drift-sample
```
**Six of the eco-system's scheduled clocks failed on their most recent run.** NORTH-STAR principle 5 ("intelligence re-prices on a clock") is materially broken today, and the truth surface graded that fact as one SKIP among eighteen.

Owned by **ticket 56 (open)**, charted as M6 on 2026-08-31. Still true, and my evidence is that the consequence has now landed.

---

## 10. The observation cage on public repos

The estate documents this itself, precisely and self-critically, at `units/driftwood/.github/rulesets/README.md`: "**Amended 2026-08-28: this leg is NOT in force, and cannot be until the repos are private** … GitHub only allows push rulesets on private or internal repositories … today the cage's load-bearing halves are the client-side cage step in each scheduled job and the gate that parses it." It also records that `required_signatures` would refuse gitsign commits outright.

I re-verified: `gh api repos/policy-as-versioned-{platform,driftwood,feeds}/…/rulesets` → `[]` on all three plus the hub; `.visibility` → `public` on all four.

Two things follow. First, **the client-side half genuinely works**: across all 21 truth runs, not one failed at the cage step —
```
$ for r in <21 run ids>; do gh run view $r --json jobs -q '[…select(.conclusion=="failure").name]'; done
run 21..15,13..5 → "fail if the gate failed";  run 14 → tool install;  run 3,2 → record the TRUTH line
```
No run has ever failed with "left a change outside the observation lane". (The `github-live` reader's note that truth.yml fails 17 times with that error is **not supported**; every recent failure is the gate's own reds.)

Second, the *absence* of the server-side half is not visible in the number at all (§9 above). The decision is owned by ticket 58 (M11(4)); the reporting gap is not.

---

## 11. Is 57/7/18 a meaningful health measure?

Partly. Here is the honest split.

**What the number does measure well.** The platform's own engines are under real, biting regression tests, and several of them are excellent (the £ engine, composition, the semver gate, the identity-regexp anchoring, the adopter gates against real cosign). The cross-party contract layer is genuinely observed: `verify/feed-contract` resolves 22 real pins against 8 real remotes, `step6` verifies 7 real Fulcio certs in Rekor, `verify/party` checks all 8 parties' own signed artefacts, `verify/renovate` reads a real merged PR. Those 20 checks are the eco-system, observed.

**What it does not measure.** Of the four questions a reader of NORTH-STAR would actually ask —

| question | what the gate says today |
|---|---|
| Do the eco-system's clocks run? | SKIP (structurally blind). Truth: 6 are failing. |
| Is the composed set in force on a cluster? | FAIL ×4, off a 13-hour-old replay; no live read at all. |
| Do ≥3 policy versions coexist? | SKIP ×5, because the estate declares one. |
| Has step 3 (a price crossing a band, a PR, a human merge) happened? | PASS — on an explicitly SYNTHETIC residual. Ticket 74 says it has never happened for real. |

— none is answered green, and two are structurally unanswerable. Meanwhile roughly **26 of the 57 passes are the platform grading its own modules against its own fixtures**, and a further 5 are simulations. A reader who takes `57/84` as "68% of the eco-system works" is being misled by the instrument's own framing, not by any single script lying.

---

## 12. Findings

Severities: **critical** = the instrument reports something materially untrue or unfit for its stated purpose; **major** = a §5 property is absent or a headline number is misleading; **minor** = polish.

### C1 (critical) — Seven scripts exit 0 after printing their own "could not look"
Evidence, remedy and demonstration in §4a. `units/platform/computed-semver/verify-cage-engine.sh:12-15` and five siblings; `verify-witness-set.sh:68-71`. Owned only for a sibling script (ticket 55, which names `render-version-tree` alone). Violates §5 bullet 2 and principle 6.

### C2 (critical) — The pass ceiling is 70 (65 today), not 84, and nothing says so
§2. `pass=57 … total=84` is published with a denominator no run can reach; 12 scripts can never exit 0 on the clock. No ticket, ADR or map line states a ceiling; `fail=0` is treated as the done bar and is unreachable for a different reason.

### M1 (major) — `verify-demo` is structurally red on the clock and its premise names a workflow step that does not exist
§8. Eight consecutive red runs. `grep -rn "deck" .github/workflows/` → no matches; `truth.yml:38` excludes `talk/deck.md` from the lane. Owned: ticket 66, open.

### M2 (major) — `verify-schedules` can never PASS, and six real clocks are failing unseen
§9. 14 SKIPs every run; the ruleset check prints nothing at all (`schedules.py:561`). Independently verified: feeds/fetch, insurer/fetch, driftwood/twin-sweep, tuppence/propose-tier, ludlow/propose-tier, ludlow/drift-sample all failed most recently. Owned: ticket 56, open.

### M3 (major) — The flux CLI is installed by `curl -s … | sudo bash` under a comment claiming every tool is pinned
§6. `truth.yml:76-91`. Orphan: no ticket, ADR or GAPS row names it. Run 14 died in this step (exit 141) and lost a TRUTH line silently.

### M4 (major) — Neither §5 bullet ("a fall blocks", "Status derived from a check") exists; ticket 55 is merged and still reads `prepared`
§7. Owned: ticket 59, open. New evidence: `46cd775` is both the merge of ticket 55 and the platform SHA in run 21's TRUTH line.

### M5 (major) — The truth surface is one day behind the estate, by declared cron, permanently
Hub cron `47 5 * * *` (`truth.yml:20`). Adopter sample crons: driftwood `20 6`, tuppence `22 8`, ludlow `16 9` (`units/*/.github/workflows/drift-sample.yml:33`). The hub fires before all three, every day, so steps 3/4 and the three `verify-reconcile` checks can only ever grade *yesterday's* sample. Confirmed empirically: run 21 at 10:11Z graded samples timestamped 2026-09-01T21:0x, while driftwood's own sample lane for 09-02 succeeded at 11:20Z. Ticket 10 D2 records "no cross-org ordering is promised" — but this ordering is not merely unpromised, it is deterministically adverse. A fix landing today cannot show green until tomorrow. Consequence unowned.

### M6 (major) — Half the headline pass count is the platform grading its own fixtures
§1.1, §1.2, §11. 29 of 57 passes are platform's; ~26 of those are self-proofs. Only 20 of 57 passes rest on a cross-party or live fact.

### M7 (major) — The denominator moves silently and no two runs are comparable
`talk/truth.log`: `total` = 56 (runs local–8), 68 (run 9), 73 (10–11), 83 (12–15), 84 (16–21); `excluded` went 0 → 2 at run 4; `skip` went 0 → 7 at run 9. Nothing records why a total moved, nothing asserts an expected script count, and nothing compares two lines. Quoting "pass=57" against "pass=43" is not a like-for-like comparison and no reader is told.

### M8 (major) — `verify/e2e/step5` PASSes on file presence while the artefact it names is provably wrong in the same run
Step 5's capture is a list of `ok <path> … (present)` lines plus a re-run of the twin evals → PASS. In the *same run*, `driftwood/verify-twin-overlay.sh` and `driftwood/twin/verify-twin-scenarios.sh` both FAIL on `twin/forward-intel/v1/feed.json is not what the overlay renders` — the very feed step 5 lists as `ok`. The deck's beat 5 therefore renders green over a broken artefact. (The 2026-08-31 review recorded "step 5 grades file presence not the scheduled forecast" as a minor; the live contradiction is new.)

### M9 (major) — Five checks are dark because the estate declares one policy version, so the thesis's central claim is unobservable
§2. `verify-coexistence`, `verify-retirement`, `verify-shift-left`, `policy/verify-conditional`, `verify-publisher-gate` part C. The 2022 thesis and the talk make ≥3 coexisting versions the crux; the truth surface cannot currently look at it at all. Owned as a *decision* by ticket 58 (M11(1)); no ticket owns restoring observability.

### m1 (minor) — Two `verify*.sh` are neither run nor excluded
`.scratch/multi-org-estate/verify-08-filter-repo-split.sh` and `verify-09-repoint-flux-sources.sh`. `talk/verify-all.sh:47` globs `.estate-clone` and `verify` only, so §5 bullet 1's "every `verify*.sh`" is scoped to two directories in practice. (`talk/verify-demo.sh` is fine — `verify/demo/verify-demo.sh` is a symlink to it, confirmed with `ls -la`.)

### m2 (minor) — `clone-estate.sh`'s own pinning precondition has fired and was not acted on
`clone-estate.sh:35-38`: "No signed tag exists yet … Once a signed v1.0.0 lands, pin it here (`--branch v1.0.0`) so the offline harness matches what Flux actually runs." All eight units now carry signed tags (`gh api repos/…/tags`: platform 11, driftwood/tuppence/ludlow/nist 2 each, ico 2, feeds 2, insurer 1). The gate still clones unpinned default branches, so a unit's author can move a red to green between two TRUTH lines and the only record is the short SHA.

### m3 (minor) — `verify-provenance` misreports which tools are present
`verify/provenance/verify-provenance.sh:55,68` tests `have rekor-cli` but prints "no rekor-cli/cosign"; cosign 3.1.3 is installed by `truth.yml:87-89`.

### m4 (minor) — Four TRUTH lines are missing and nothing detects the gaps
`talk/truth.log` has no `run=1`, `run=2`, `run=3` or `run=14`. Runs 2 and 3 failed at "record the TRUTH line"; run 14 at the tool install (§6). A clock whose record can silently skip a day is a weaker instrument than its own §5 bullet 5 promises.

### m5 (minor) — Unchecked checks are printed as NOTE and graded green
§4c. `platform/party/party_artefact.py:369-379`, `insurer/verify-insurer-party.sh`, `platform/party/verify-party-artefact.sh`.

### m6 (minor) — `map.md` still publishes a health claim the truth surface never recorded
`.scratch/ecosystem/map.md:61-62`: "went from 40 pass, 16 fail of 56 to 65 pass, 0 fail, 16 could-not-look of 83. … Nothing is red." The 2026-08-31 correction beneath it (lines 64-66) cites run 13 — now two days and eight runs stale, and it still leaves the false sentence standing as body text. Owned: ticket 67, open.

---

## 13. Findings from REVIEW-2026-08-31 that are now fixed (verified today)

- **C1 (kyverno pin).** `truth.yml:44-47` now pins `KYVERNO_VERSION: 1.18.2` with a sha256 and a written reason. `verify-graded`, `verify-shift-left` and `verify-render-version-tree` no longer red on the CEL; run 21 grades them SKIP (cluster), SKIP (one version) and PASS respectively.
- **M2 (signature spine red).** `platform/verify-source-verification` run-21 capture now reads "== 4. it ACCEPTS the real signed tag under the release.yml pins == VERIFIED: signed by …/cut-release.yml@refs/heads/main". The OpenSSL chain fix landed.
- **M3 (publisher-gate timeout).** `truth.yml:96` sets `VERIFY_TIMEOUT: '900'`; the script completed in 358s and SKIPped honestly on part C.
- **M4 (corpus SIGPIPE).** `verify-corpus-generator.sh:40` now uses a glob, with the reason in a comment. PASS.
- **M5 (jsonschema missing).** `truth.yml:63` installs `jsonschema==4.23.0`; step1, step6, feed-contract and the twin-overlay reach their checks.
- **M7 (reconcile SKIPped before reading the sample).** All three `verify-reconcile` scripts now grade the five-fact sample first; they FAIL on real facts rather than SKIPping.
- **Minor "cosign unpinned".** Now pinned by version and sha256.

I did not re-raise any claim on the review's "Refuted" list.

---

## 14. Strengths, with evidence

1. **One command, on a clock, in CI, writing one dated, signed, committed number.** The TRUTH commit for run 21 verifies for real:
   ```
   $ git -c gpg.format=x509 -c gpg.x509.program=gitsign log -1 --show-signature a209496
   gitsign: Good signature from […/truth.yml@refs/heads/main] (token.actions.githubusercontent.com)
   Validated Git signature: true      Validated Rekor entry: true
   ```
   The number lives in git with its date and the nine commits it read. That is a genuinely rare thing to have built.
2. **The exclusions mechanism is sound and cannot rot** (§5), and both entries are provably executed by their parents in the same run.
3. **The observation cage works.** 21 CI runs, zero cage-step failures; the workflow's `git reset -q` before staging, the staged-set assertion against the same `OBSERVATION_LANE` variable the checker reads, and the `persist-credentials: false` reasoning are all careful and each carries a dated reproduction of the bug it fixes.
4. **The toolchain is pinned by version *and* checksum for gitsign, kyverno and cosign,** with the kyverno pin carrying its own written reason and a citation to the incident that motivated it. Flux is the one exception (M3).
5. **SKIP reasons are specific and actionable, not boilerplate** — "distribution/versions.yaml declares one version (4.0.0); coexistence needs two declared versions", "cs-16's cut-in-the-middle shape needs at least three declared versions". A reader can act on every one.
6. **The reds are real.** Six of seven are estate faults, each with an owning ticket (72, 73, 62/74) that names the mechanism, not a symptom.
7. **The five-fact grader refuses to be fooled**: it will not credit a sample unless the run field is a real Actions run id and the appending commit is authored and signed by the lane's own identity — closing a documented 2026-08-29 incident where hand-typed lines graded PASS.
8. **The estate documents its own instrument's limits in its own words**, and does so against interest: the rulesets README's "this leg is NOT in force, and cannot be until the repos are private"; `verify-e2e-step3`'s "a SYNTHETIC residual … not driftwood's real priced position"; `verify-adopter-gate`'s "NOT exercised here (CI-only, confirmed)". Most of my findings are extensions of self-criticism the estate had already written down.
9. **The 2026-08-31 review's remediation actually landed.** Five confirmed findings and one critical are verifiably fixed on run 21 (§13). The instrument is improving run over run, not drifting.

---

## 15. Fitness verdict

As the *only citable source for what works*, the truth surface is **fit in mechanism and unfit in framing**. The mechanism is real, signed, dated, self-checking and improving: glob discovery, three graded outcomes, a working cage, a pinned toolchain, an exclusions list that cannot rot, and a number committed to git under a verifiable Sigstore identity. Nothing about it is fake, and every serious limit I found was already written down somewhere in the estate's own hand.

It is unfit as a *health measure* for three reasons that compound. First, the denominator is a fiction: 12 of 84 scripts can never pass on the clock and 5 more are dark because of an estate decision, so `pass=57 … total=84` is measured against a ceiling of 70 that nobody states and 65 that nobody can beat today. Second, the composition is not what the framing implies: about half the passes are the platform grading its own fixtures, only 20 of 57 rest on a cross-party or live fact, and the four questions NORTH-STAR actually poses — do the clocks run, is the set in force, do versions coexist, has step 3 happened — are answered SKIP, FAIL (on a day-old replay), SKIP, and PASS-on-synthetic. Third, the surface cannot see its own instrument failing: seven scripts pass after printing their own "could not look", six real clocks are red today with the gate reporting one SKIP, a fall in the number blocks nothing, and four TRUTH lines have gone missing unnoticed.

What would make it fit, in order and mostly cheaply: (1) fix the seven `exit 0`-after-SKIP scripts to `exit 3` — a one-line change each, and the class is already fixed in a sibling; (2) publish a ceiling alongside the number, so `pass=57 of 64 reachable, 12 structurally unobservable on this runner` is what a reader sees; (3) either give the gate a cross-org read token or move `verify-schedules` to a job that has one, so the clocks stop being invisible; (4) pin the flux install; (5) move the hub cron after the adopters' sample lanes so step 4 grades today; (6) build ticket 59's two §5 bullets so a fall is loud and a ticket's Status comes from a check. None of those is architecture. All six together would turn a well-built instrument that currently flatters its subject into one whose number a skeptic could act on.
