# 03 — The truth surface

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Make one command the only citable source of what works, and make it green or honest. `talk/verify-all.sh` discovers every `verify*.sh` by glob and fails on any script neither run nor listed in a committed exclusions file with a reason. Every live tail has exactly three outcomes (observed-true, observed-false, could-not-look as SKIP with reason). Every live-claiming script asserts its substrate first (`docker info`, `kind get clusters`, Flux Ready). Split `.github/workflows/twin.yml` into independent jobs and put the gate on a schedule. Fix the known reds: `twin verify` VerbError and hang; invariant 42 (commit the drift window and forced-campaign files in driftwood); ci-check.py ±1 window by semver distance; `verify-retirement.sh` absence-as-positive; `verify-coexistence.sh` offline fail; `verify-governed-namespace-guard.sh` missing renderer; `verify-coverage.sh` assertion; stale nist 1.0.0 assertions; tuppence and ludlow commit pins. Re-attribute pitch-v6's six reds. Write the 2026-08-25 Docker post-mortem into HISTORY.md. Record the number and date on every run.

## Notes

GAPS.md Tier 2. This runs in parallel with the thin slice; it is what grades it.

## Answer

Resolved 2026-08-28. Hub commits `ebe1757` and `db47f88` on main. Five PRs open in the unit repos, none merged. The owner merges them.

### The gate

- `talk/verify-all.sh` discovers every `verify*.sh` under `.estate-clone/` and `verify/` by glob. It grades each by exit code: 0 PASS, 3 SKIP with a reason, other FAIL. A script neither run nor listed in `talk/verify-exclusions.txt` with a reason fails the gate. A listed path that no longer exists fails the gate. Two helpers that take arguments are excluded with their callers named.
- Every run ends with one line: `TRUTH <date> run=<n> hub=<sha> units=[...] pass= fail= skip= excluded= total=`. That line is the only citable number. `.github/workflows/truth.yml` runs the gate daily and appends the line to `talk/truth.log`.
- First run, local, clusters up: `TRUTH 2026-08-28T04:00Z run=local hub=2326f31 ... pass=40 fail=16 skip=0 excluded=0 total=56`. The denominator is 56, not 28.
- The 16 fails on that run: 3 reconcile scripts (pins and nist assertion, PRs below), 6 live tails on real absent objects (`require-nonroot-3-0-0`, `cage-tier-2-0-1`, `stamp-posture-2-0-1` absent; Pomerium pod absent; istio sidecar not injected; reach `000ERR`), shift-left and war-gamer (window, PR below), publisher gate B3 (PR below), governed-namespace guard cwd (PR below), tuppence adopter gate scenario E (cosign identity, not fixed, see below), and the two argument-taking helpers (now excluded).

### Three outcomes and substrate first

- platform PR 3: https://github.com/policy-as-versioned-platform/platform/pull/3. `lib.sh` gives `skip`, `substrate_ok`, `require_substrate`, `live_tail_skip`, `pass_line`. Substrate order: `docker info`, `kind get clusters`, Flux Kustomizations Ready. Ten live scripts gate their tail on it. A script whose tail could not look exits 3. `verify-retirement.sh` never claims pruning it did not observe. `verify-coexistence.sh` reads every version from `versions.yaml` and SKIPs when the ResourceSet is absent. `verify-governed-namespace-guard.sh` is cwd-independent.
- driftwood PR 11, tuppence PR 8, ludlow PR 7: https://github.com/policy-as-versioned-driftwood/driftwood/pull/11, https://github.com/policy-as-versioned-tuppence/tuppence/pull/8, https://github.com/policy-as-versioned-ludlow/ludlow/pull/7. `verify-reconcile.sh` reads tag, commit and configmap values from the repo's own gitops tree at the pinned tag, never from a literal. `gotk-sync.yaml` carries `commit:` beside `tag: v1.0.0` (driftwood `92034b0`, tuppence `9862d84`, ludlow `7bd9973`). `scripts/lib.sh` carries `need_substrate`, identical text in all three.

### The known reds

- shift-left window: platform PR 4, https://github.com/policy-as-versioned-platform/platform/pull/4. The window is now every declared version on the target's major line plus the nearest lower and higher major lines. A second root cause surfaced: every policy self-scopes on the version label, so the window evaluated nothing against neighbours; `ci-check.py` now relabels a temp copy per window version. `verify-coverage.sh`'s `cel_pass` read any kyverno exit as "refused"; it now parses the summary and raises on an error. Publisher gate B3 locates the array block structurally.
- `twin verify`: bare run today took under 15 minutes and exited 1 with 4 fails, no hang. The `VerbError` lines were stderr from a deliberate refusal inside a guard. The harness now keeps a check's stderr only when the check fails, and fails a check that overruns `TWIN_CHECK_TIMEOUT` (600 s). Invariants 42 and 45 pass: the first-commit date is read from the driftwood repository and the hub's pre-split path (window 2026-08-07, forced campaign 2026-08-14, all samples later). 43 and 44 stay red by the owner's recorded decision.
- `twin.yml` is split into `invariants`, `tests`, `typecheck`, `demo`, `determinism`, `reproduce-elsewhere`, on a daily schedule. First split run: typecheck, demo, determinism, reproduce green; invariants red on 43 and 44 only; tests red on 12 `test_enact.py` cases that assert the `operations` refusal while `ENACT_MODE` is `development`, plus the suite mirror.
- pitch-v6 `plan.md` re-attributes the six reds to what the 2026-08-27 review observed: incomplete fan-out, spire-agent CrashLoopBackOff, Pomerium absent. Eight real reds, none local.
- `docs/HISTORY.md` carries the 2026-08-25 Docker post-mortem.

### Left open, named

- tuppence adopter gate scenario E: `cosign verify-blob` identity mismatch against `policy/v2.0.0` evidence. Not touched.
- The six live-object reds are estate state, not verifier defects: fan-out of 2.0.1 and 3.0.0, spire-agent, Pomerium. They belong to the thin-slice build and GAPS 2.8.
- v3.0.0 `require-nonroot` cannot be satisfied by a baseline-tier pod because `cage-tier` sets `readOnlyRootFilesystem=false` first. Recorded on ticket 09.
- The 12 `test_enact.py` failures assert a mode the checked-in `ENACT_MODE` does not select. They need an owner decision on which mode the tests assert. Not changed.
- driftwood `scripts/up.sh` seeds the in-cluster git server at a fresh commit, so the new verifier FAILs the commit comparison on a locally seeded cluster until up.sh seeds the pinned commit.
- The `docker down` and `Flux not Ready` branches of the substrate helpers were not exercised live. Clusters existed on the host and were not touched.
