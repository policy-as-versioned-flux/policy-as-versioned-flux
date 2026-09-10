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


Platform v3.0.0 is published: both workflows passed, release resolves to reviewed3602142,
published 16:52:01Z. Adopter rollout is unblocked. Sensor fixture repair is signed commitc69f048;
local TruffleHog scan completed without errors and found zero secrets. Ticket86's review P2 is
fixed; both review axes pass. Its integration remains in the isolated worktree, not published.
