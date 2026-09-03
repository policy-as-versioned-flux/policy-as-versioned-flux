# 55 — Every red on the clock is real, explained, and finishable

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Three of run 13's reds are instrument faults, not estate state. (a) verify-corpus-generator: replace the ls|head pipeline with a glob so SIGPIPE cannot red a healthy generator. (b) verify-publisher-gate: set VERIFY_TIMEOUT for the scheduled run or split the four parts into separately graded scripts, and make each part flush incremental output so a timeout still leaves evidence. (c) verify-source-verification: teach verify_gitsign.py to print trust-material failures ("unable to get local issuer certificate") as could-not-look exit 3, never REJECTED, and fix the CI runner's chain build so the real tag verifies (it verifies locally against only the pinned roots). Also stop discarding stderr in render-version-tree and change its exit-0-on-missing-kyverno to exit 3. Done = each script either passes, or reds with its observed-false named, on a scheduled run.

## Notes

**The owner's two commands** (done 2026-09-01; see the Answer of 2026-09-03). The patch file
`.scratch/ecosystem/0001-Every-red-on-the-clock-is-real-explained-and-finisha.patch` was the
carrier until then and is deleted: platform commit `04184df`, merged as `46cd775`, is the record.

    git -C .estate-clone/platform push -u origin ticket-55-instrument-faults
    gh pr create -R policy-as-versioned-platform/platform --head ticket-55-instrument-faults --fill

The gate clones each unit fresh from its default branch (`clone-estate.sh`), so these four repairs
stayed invisible to the truth surface until they landed on platform `main`.


Charted by the ambition review of 2026-08-31. Closes review findings: M2 (source-verification, 3 confirmed findings), M3 (publisher-gate, 2 confirmed findings), M4 (corpus SIGPIPE), minors render-red-carries-no-reason and skip-graded-as-pass.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Answer (2026-08-31) — built and proved, waiting on the owner

All four repairs are built, tested and committed to branch `ticket-55-instrument-faults` in
`.estate-clone/platform` (commit `04184df`). **They are NOT on the platform repo.** `enact_guard`
refused the push, correctly: it writes to an enactment repository directly, "disposal without
even the pull request". The guard's own text says the owner pushes and merges. I did not flip
`twin/ENACT_MODE` to get around a control that had just refused me.

**1. The signature spine (the important one).** The gate rejected this repo's own genuine signed
tag. The cause is not the signature. The Fulcio leaf embeds no intermediate, and
`openssl cms -verify -certfile` feeds the chain builder on OpenSSL 3.6 (local) but NOT on 3.0.13
(the CI runner). Reproduced exactly: the same bytes and the same command give
`CMS Verification failure ... unable to get local issuer certificate` under 3.0.13 in an
`ubuntu:24.04` container.

The fix is two explicit steps instead of one. It is portable, more auditable, and it keeps the
ROOT as the only trust anchor, because `openssl verify` takes the intermediate as *untrusted*
chain material. Proved under the runner's own OpenSSL 3.0.13:

| case | before | after |
|---|---|---|
| the genuine tag | REJECTED | rc=0 VERIFIED |
| tampered payload | — | rc=1 REJECTED |
| tampered signature | — | rc=1 REJECTED |
| wrong identity | — | rc=1 REJECTED |
| wrong issuer | — | rc=1 REJECTED |
| anchored on the intermediate alone | — | refused (rc=2) |
| trust material absent | REJECTED | rc=3 COULD-NOT-LOOK |

`-noverify` skips the chain, which step one already did, but still verifies the signature over the
content. `-no_content_verify` is never used, and the code says why: it would drop the payload
binding and accept any content under a valid signature.

**2. `verify-corpus-generator`** died of SIGPIPE (`ls | head -1` under pipefail). A glob sorts the
same way and cannot break. Proved: rc=0 under `bash -o pipefail`.

**3. `verify-render-version-tree`** exited 0 when kyverno was absent, so a could-not-look graded as
PASS. It exits 3 now. That is the check-passes-on-absence class the 2026-08-25 incident came from.

**4. `verify-publisher-gate`** printed nothing until `wait` returned, so a timeout left a two-line
capture and an undiagnosable red. A TERM/INT trap now prints what every part had written. Proved
by running it under a deliberate 25s timeout: the trap fired and the partial output printed.

## Answer (2026-09-03) — landed, on the clock, resolved

The 2026-08-31 answer is superseded by events. The owner ran the two commands: branch
`ticket-55-instrument-faults` (platform commit `04184df`, +68/-11 across the four named files)
became platform PR #8 and was merged to platform `main` as `46cd775` on 2026-09-01T04:09:42Z by
the owner. Every scheduled gate run since has cloned platform at `46cd775`.

**The done condition is met on a scheduled run.** Run 22 (`talk/truth.log`,
`2026-09-03T10:24Z run=22 hub=14cc731 ... platform=46cd775`, Actions run 33742398518) graded the
four scripts:

| script | run 22 grade | what the line names |
|---|---|---|
| `computed-semver/verify-corpus-generator.sh` | PASS | — |
| `distribution/verify-render-version-tree.sh` | PASS | — |
| `verify-publisher-gate.sh` | SKIP (exit 3) | `part(s) c could not look -- the reason is on their own SKIP line above; every other part of the publisher gate was observed true`; part C's own line: versions.yaml declares only `['4.0.0']`, there is no middle to cut |
| `verify-source-verification.sh` | SKIP (exit 3) | `offline proof holds; live tail could not look: kind cluster 'driftwood' is not listed by kind get clusters` — the genuine tag verified on the runner's OpenSSL 3.0 |

None of the four is a red any more, and every could-not-look names its reason on the line. The
seven reds that remain on run 22 belong to other tickets, not to these scripts:
`driftwood/twin/verify-twin-scenarios`, `driftwood/verify-reconcile`, `driftwood/verify-twin-overlay`,
`ludlow/verify-reconcile`, `tuppence/verify-reconcile`, `verify/demo/verify-demo` (stale deck) and
`verify/e2e/verify-e2e-step4-flux-reconciles-cage` (the reconcile family, tickets 56/60; the deck,
ticket 67's surface).

**Re-verified locally on 2026-09-03** from the hub root against the merged code
(`.estate-clone/platform` at `46cd775`, OpenSSL 3.6.4, kind cluster `driftwood` present):

- `verify-corpus-generator.sh` under `bash -o pipefail`: rc=0, `PASS: corpus generator selfcheck ok, spine regenerates byte-identical, sample entry is a real Pod`.
- `verify-render-version-tree.sh`: rc=0 PASS; with kyverno off PATH: rc=3, `SKIP: kyverno CLI not found`.
- `verify-source-verification.sh`: rc=0 PASS here, because the live tail can look (`gitsign-verifier is running on kind-driftwood`).
- `verify_gitsign.py verify-object` on the real fixture: `--roots /nonexistent` rc=3 COULD-NOT-LOOK; `--intermediates /nonexistent` rc=3 COULD-NOT-LOOK; with the pins, rc=0 VERIFIED.
- `verify-publisher-gate.sh`: rc=3, the same part-C SKIP as run 22; under `timeout 25`, the TERM trap printed every part's partial log and the cut-short FAIL line.

One observation for the record, not a repair: `verify-publisher-gate.sh` Part A asserts
`corpus_generator.DISTRIBUTION == repo / "distribution"` without resolving symlinks, so it reds when
the hub root reaches `.estate-clone/platform` through a symlink (a builder's worktree). The clock
never does; it clones a real directory. Left as is: the ticket's done condition is the scheduled
run, and a symlink-tolerant assertion is a different ticket's diff if anyone ever needs it.

**Decisions**

- Delete the patch file `0001-Every-red-on-the-clock-is-real-explained-and-finisha.patch` — delegated
  (ADR-0025). Its body is byte-identical to `git format-patch -1 04184df` (checked with `diff`), and
  the commit is on platform `main`, so keeping it would give the record two sources of truth for one
  change. The commit and the PR are cited above in its place.
- Option (b) of the question ("split the four parts into separately graded scripts") was not taken;
  the trap-and-flush repair was, and the part-C could-not-look is graded SKIP with its reason on
  its own line — delegated (ADR-0025). That satisfies "reds with its observed-false named". Splitting
  the publisher gate's parts, and the live tail of `verify-source-verification`, into scripts that
  can PASS on their own belongs with whichever ticket brings a live cluster to the clock (the 56/60
  family), not here.

**Which check grades it:** the four platform scripts above, discovered by `talk/verify-all.sh`.

Map line: 55 landed: PR #8 merged as platform 46cd775 on 2026-09-01; run 22 grades corpus-generator PASS, render-version-tree PASS, publisher-gate and source-verification SKIP with the reason named; the patch file is deleted.

## Waits on the owner

Nothing. The push and the merge were the only owner parts, and both are done.
