# Execution ledger — 2026-09-10

Authorization: the owner requested implementation of the remaining work, dependency-aware
workflows, review gates, incremental pushes and merges to main, with low concurrency.
Baseline: hub `7e3f0a1`, platform `5b88f1d`. The initial local hub was 139 commits behind;
that checkout was fast-forwarded before implementation. Existing untracked skills and pitch
assets are not part of these batches.

## Gates and order

Each batch goes through focused behavior tests, applicable type checks, independent Standards
and Spec reviews, correction of blocking findings, then a checkpoint commit and PR. Merge only
after checking the committed diff and relevant CI. A code merge does not manufacture the
scheduled or live evidence a ticket requires. Keep at most two builders active; reviews take
priority over starting more work. Re-read remote main and active branches before each batch.

| Work | Depends on | State / completion gate |
|---|---|---|
| 104 truth queue isolation and loss report | current hub | Implemented; review correction applied; live run proof and scheduled capture pending |
| 109 map transcription and deck checks | current hub | Implemented; Standards and Spec reviews pass after malformed-prefix correction |
| 110 offline supersede provenance | current platform | Implemented; Standards and Spec reviews pass after malformed-tag correction |
| 86 cage observation | existing ticket-86 branch and adopter changes | Existing eight-commit hub branch discovered; inspect/review/reuse, do not rebuild |
| 107 sampler proof | real scheduled samples | Complete: ludlow run 34483506093 confirms named waits before its 13:36Z sample, joining driftwood and tuppence |
| 34 / 45 / 79 / 84 rollout | 110 → platform software release → adopter pin/recompose | Confirm actual software release, retain held tuppence PR27/ludlow PR24 until prerequisites hold |
| Insurer quote rollout | adopter exposure releases → insurer pins → scheduled quote → signed quote → adopter pins | Inspect live refs; old tag-wait prose is historical |
| 74 real crossing | genuine scheduled price movement, proposal and observed tier change | Observation-dependent; never plant a citable crossing |
| 93 real scoring | derived preregistered forecast → outcome date | Existing recorded horizons are 2027-08-28; no future outcome is fabricated |
| 27 / 30 / 35 / 37 / 46 / 71 | existing resolved design parents | Reconcile architectural portions under ADR-0025; retain owner-reserved purpose/money choices |
| 87 / 97 | second identity from 88; authorization record choices | Coordinate forge enforcement with the owner-reserved acknowledgment decision |

## Validation and dependency checkpoint

The owner approved a local secret scan and per-commit bypass of the exhausted ggshield hook.
TruffleHog local scans reported zero secrets for the hub and platform changes. Commit signing
remains enabled; no global Git configuration was changed.

Ticket 86 audit located four unmerged branches at hub f0f8ea7, driftwood 35e46ee,
tuppence 40f05bb and ludlow a4cb73b, all named `ticket-86-the-cage-enters-the-citable-number`.
No PRs existed at audit. Preserve newer adopter sample commits; integrate hub map/deck changes
with ticket 109, then review/merge adopters and wait for actual samples. Old served pins still
prevent a green cage.

Both independent review axes pass for tickets 104, 109, 110 and the committed test-fixture
repairs. The full local suite finished with 2506 passed, 56 failed and 1 error. Its loaded
fixture code predates the repairs: can-record's two failures and all 52 local-clock cases have
subsequent passing focused runs. Sensor-admission has the same inherited signing problem and
is being repaired separately. Misuse checked a stale platform clone; rerun against the current
isolated estate. The remaining invariant failure is the preregistered coverage shortfall.

Remote CI's full suite has 2562 passed and one failure, the same standing coverage shortfall.
No full-suite green result is claimed. This ledger is an execution record, not a TRUTH
observation or a declaration of completion.

## Publication checkpoint

The owner explicitly approved local scans in place of the exhausted hook. Signed hub commits
8775692 (104), 22b5bd0 (109), and 1abb816 (fixtures) were pushed in PR77. Platform commit
41761fa was reviewed by pavc-other-hand and merged through PR24 as 3602142. Repository access
was verified via GitHub: chrisns has admin/push rights on both destinations; that cleared an
auto-review rejection of the first push. No force push or global hook change was used.

Hub CI typecheck, demo, determinism across three architectures, reproduce-elsewhere and clock
collector pass. Invariants are 71 pass/1 fail/3 skip: the known preregistered flux coverage floor
is unreachable (3/1966 samples, ceiling 62.0%). Do not alter that historical observation or lower
the threshold to make CI green. The remote test job has only that same invariant failure. The truth gate is still running.


Sensor-admission fixture signing isolation passed both review axes, all 196 focused tests and
mypy. Misuse's unchanged test passes when its process reads the isolated current estate; its
original failure was the preserved stale local clone, not a code defect.

Platform v3.0.0 pre-release checks pass, including Kyverno shift-left and all eight tag-mechanics
fixtures. Automatic approval review rejected the dispatch because immutable software publication
was not explicitly named in the user's authorization. Approval is pending; no tag was created.

Ticket 86's existing hub branch is integrated in an isolated temporary worktree, preserving
109 and regenerating the deck. 159 focused tests pass; independent review is in progress.


The owner explicitly approved v3.0.0 publication. Signed cut workflow 34504582573 was dispatched;
its result and identity-pinned release verification remain pending. The prior auto-review block
is cleared by this explicit authorization.


Platform v3.0.0 is published: both workflows passed, release resolves to reviewed 3602142,
published 16:52:01Z. Adopter rollout is unblocked. Sensor fixture repair is signed commit c69f048;
local TruffleHog scan completed without errors and found zero secrets. Ticket 86's review P2 is
fixed; both review axes pass. Its integration remains in the isolated worktree, not published.


## Integration checkpoint

Hub PR77 merged as e214bed after truth run 240 matched recorded 235's exact eight failed paths
and counts (80 pass/8 fail/29 skip). This branch result is not citable. PR78 holds signed follow-up
commits c69f048,218deb3,a5576bc; its full CI suite reports 2563 passes and the same sole coverage
invariant failure, while the other completed jobs pass. Its truth gate remains in progress.

The three cage integrations passed both review axes after fixing unsupported-selector false
attribution and stale registration prose. Signed heads: driftwood 5aab7da (PR 36), tuppence 4d3bede
(PR 31), ludlow 98b811c (PR 28). All selfchecks and wait-order checks pass; samples are unchanged;
local scans found zero secrets. These PRs are held behind hub 78 and actual scheduled proof.

The first prepared software migration exposed a composed-major addition of policy 5.0.0. It is
held and unpublished. The composer already supports separating its executable from implementation
inputs, so a delegated architectural correction is being implemented with independently pinned
v3 tools and unchanged accepted v2.0.1 implementation, money, dates and deployed policy pins.


## Reviewed rollout checkpoint

Hub PR78 merged as 0647a55. Branch truth run 241 has 81 pass/7 fail/29 skip, with only the
acknowledged derived-status red removed from the previous failed-path set; it is not citable.
The full current-head CI suite has 2563 passes and the standing coverage invariant failure.
Main run 242 is citable and recorded by 5ebeba4: 80 pass/8 fail/29 skip. Its real overlap with
the branch gate and recorded LOST RECORDING count=19 satisfy ticket104's original Done.

All three ticket86 implementations merged: driftwood PR36 as77c1cde, tuppence PR31 as65acf4c,
ludlow PR28 as7fb6338. Actual scheduled facts6/7 remain a completion gate. Insurer PR6 merged
as d1c1844: only its verifier software pin moved to released v3.0.0; economic inputs are unchanged.

The independent compiler boundary preserves platform implementation v2.0.1 and the accepted
policy4 window while using signed software v3.0.0. Driftwood PR37 merged as4cfd952 and Ludlow
PR29 as416a2a3 after both reviews and CI passed. Tuppence PR32 also merged after CI passed at
2c714b1. Its CI exposed a depth-one adopter checkout losing signed-tag history; the exact CI
checkout reproduced the changed historical ramp. Restoring only history made unchanged tests
pass. The reviewed fix fetches full adopter history; no price or evidence was edited.

Platform PR25 merged as332ab19 with replayable floor-change evidence (ticket27's bounded
portion). Both reviews and release checks pass; v3.1.0 publication is awaiting separate explicit
approval. Missing Tuppence/Ludlow twin clocks are implemented and reviewed, with integration
onto current main pending. They record actual missing-input results and remain non-green;
they supply no feed, valuation, forecast or publishing contract.

These are implementation and validation records. None substitutes for scheduled observations,
owner monetary declarations, or an immutable publication approval.


A follow-up production schedule-grader audit found a new containment-check regression in the
merged tools rollout: propose-tier has two opaque local-action findings and Renovate one in
each adopter; their pre-tools baselines have none. Ordinary PR CI did not cover this boundary.
A focused correction is in progress, preserving the shared authoritative pins and signature
runner and leaving the grader unchanged. The rollout is not declared complete.


## Publication and clock correction checkpoint

The owner approved v3.1.0; signed cut 34512212053 and identity-pinned release 34512281836 passed.
The release was published at 18:06:47Z from reviewed 332ab19. Existing adopter compiler pins
still name v3.0.0; publication alone does not move them.

Tuppence clock PR33 merged as ffb0418; Ludlow PR30 as 8ef36c7. Their first scheduled result remains
outstanding. All three schedule-tool corrections passed both reviews and CI and merged through
Driftwood38, Tuppence34 and Ludlow31. The unchanged production containment grader shows nine
new opaque-action findings before correction and zero after; pre-tools baselines also show zero.
No permissions, observation lanes, signature checks or generated evidence were weakened.

Hub PR79 merged as e436d11 and includes the clock-written run 243 from its main parent:
81 pass/6 fail/30 skip at 17:52Z. This is citable, but its captured adopter SHAs precede the compiler
and clock corrections. It is not evidence that those later changes have run on a real schedule.
