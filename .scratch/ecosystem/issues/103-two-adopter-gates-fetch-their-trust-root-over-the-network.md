# 103 — Two adopter gates fetch their trust root over the network on every CI run

Type: task (AFK)
Status: open
Blocked by: none

## Question

ludlow's gate verifies platform's real published evidence with a cold Sigstore TUF cache and every
route to the network blocked. driftwood's and tuppence's cannot. Both of them said they could.

Measured 2026-09-06 while building ticket 101, with the real binary against platform's real
committed bundle for policy 2.0.1 at tag `v2.0.1`:

    HOME=<empty> TUF_ROOT=<empty> HTTPS_PROXY=http://127.0.0.1:1 \
      cosign verify-blob --bundle=2.0.1.json.bundle \
        --certificate-identity-regexp=<that repository's own constant> ... 2.0.1.json

    driftwood  exit 1   tuf: failed to download 13.root.json ... connection refused
    ludlow     exit 0   (through its own gate, which pins its trust material)
    tuppence   exit 1   tuf: failed to download 13.root.json ... connection refused

The same invocation on a machine whose `~/.sigstore` cache is already warm returns `Verified OK`
in about a second, which is why nobody noticed: **the estate's evidence for "offline" was measured
on warm laptops.** A GitHub Actions runner is cold on every run, so every real `shift-left` run of
driftwood's and tuppence's gates reaches Sigstore's TUF CDN before it can check a signature.

## Why it matters, stated without inflation

It is not a correctness hole today: the fetched root is the genuine Sigstore root and the
verification that follows is real. It is three other things.

1. **An availability dependency in a required status check.** When the CDN is slow or unreachable,
   two adopters cannot merge a Renovate bump, and the failure reads as a signature problem.
2. **A trust-distribution difference nobody chose.** ludlow's root is a reviewed, committed file
   that changes only by pull request. The other two take whatever TUF serves at verification time.
   Which of those the estate wants is an architectural question; having both by accident is not an
   answer to it.
3. **It was written down as the opposite.** driftwood's gate said it "verifies the bundle's cosign
   signature offline"; tuppence's said verifying "needs no ambient credential and no network at
   all". Ticket 101 replaced both sentences with a number each harness prints on every run, but the
   underlying difference is still there.

## What ticket 101 already did, so this ticket does not redo it

* ludlow's gate pins the trust material for the legacy bundle shape platform actually publishes
  (`SIGSTORE_ROOT_FILE` / `SIGSTORE_REKOR_PUBLIC_KEY` / `SIGSTORE_CT_LOG_PUBLIC_KEY_FILE`, all
  written out of its one committed `trusted_root.json`, the per-log keys selected by the log
  identifiers the artefact itself names), with `TUF_ROOT` pointed at an empty directory so a warm
  cache cannot stand in for the pin. That code is the pattern this ticket copies.
* Every adopter's harness now prints its own cold-cache exit code on every run
  (ludlow Part E5, driftwood scenario G, tuppence scenario G), and the hub's
  `verify/real-signature/verify-a-real-signature-is-checked.sh` prints one line per adopter. So
  the day this ticket lands, four checks say so by themselves.

## Done

driftwood's and tuppence's gates verify platform's real published evidence with a cold TUF cache
and egress blocked, and the four measurements above print 0 instead of 1.

## What has to be decided, not just typed

1. **Whether each institution commits its own `trusted_root.json`, or whether that is the same
   file three times.** Copying ludlow's bytes into two more repositories is the smallest diff, and
   it also means three copies of a pin that must be refreshed together — with nothing grading that
   they agree. NORTH-STAR §2 says the publisher sets nothing inside an adopter's repository, so a
   platform-served root is not obviously right either. This is an architectural call under
   ADR-0025 and belongs in the ticket that makes it.
2. **What refreshing a pinned root costs.** ludlow's gate refuses BY NAME when the committed root
   carries no key for the log an artefact names, which is the correct failure and a real
   maintenance obligation: Sigstore rotating a CT or transparency log turns three required checks
   red until three pull requests land. A staleness report on the truth surface — "the committed
   root's newest log is N months old" — would turn that from a surprise into a schedule, and
   probably belongs with this work.
3. **Whether the publisher should move to new-format bundles anyway** (ticket 101 remedy 2). If
   platform re-signs, `--trusted-root` works directly and the per-log key selection ludlow needs
   becomes unnecessary for new tags — though already-published bundles on cut tags are immutable,
   so both shapes coexist until every pinned tag has moved. A tag is cut only by `cut-release.yml`
   and dispatched only by the owner, so this half waits on the owner whatever else is decided.

## Notes

Charted 2026-09-06 from ticket 101's build. The finding is ticket 101's, not this ticket's: it is
recorded here because a finding that points at no ticket anyone can pick up is not reported, it is
mentioned.
