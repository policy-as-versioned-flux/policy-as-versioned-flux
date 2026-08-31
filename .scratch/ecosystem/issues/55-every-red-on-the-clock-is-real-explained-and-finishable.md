# 55 — Every red on the clock is real, explained, and finishable

Type: task (AFK)
Status: prepared
Blocked by: none

## Question

Three of run 13's reds are instrument faults, not estate state. (a) verify-corpus-generator: replace the ls|head pipeline with a glob so SIGPIPE cannot red a healthy generator. (b) verify-publisher-gate: set VERIFY_TIMEOUT for the scheduled run or split the four parts into separately graded scripts, and make each part flush incremental output so a timeout still leaves evidence. (c) verify-source-verification: teach verify_gitsign.py to print trust-material failures ("unable to get local issuer certificate") as could-not-look exit 3, never REJECTED, and fix the CI runner's chain build so the real tag verifies (it verifies locally against only the pinned roots). Also stop discarding stderr in render-version-tree and change its exit-0-on-missing-kyverno to exit 3. Done = each script either passes, or reds with its observed-false named, on a scheduled run.

## Notes

**The owner's two commands.** The patch is
`.scratch/ecosystem/0001-Every-red-on-the-clock-is-real-explained-and-finisha.patch`.

    git -C .estate-clone/platform push -u origin ticket-55-instrument-faults
    gh pr create -R policy-as-versioned-platform/platform --head ticket-55-instrument-faults --fill

The gate clones each unit fresh from its default branch (`clone-estate.sh`), so these four repairs
stay invisible to the truth surface until they land on platform `main`.


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
