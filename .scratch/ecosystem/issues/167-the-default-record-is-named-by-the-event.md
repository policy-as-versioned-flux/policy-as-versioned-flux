# 167 — The default record is named by the event

Type: task
Status: resolved

Claimed 2026-10-26 before source/test edits in a new ordinary canonical HTTPS clone at 3f317062.

## Question

Does the actual init/full-fetch/SHA-checkout caller preserve renamed-default discovery when
origin/HEAD is absent? Diagnose with actual production stranded CLI, immutable source and real
TEST_ONLY Git history. Preserve currentmain, original466/468 evidence and all recording boundaries.

## Required delivery

Use the existing trusted workflow guard after event default validation and branch-specific fetch
to verify the already-fetched explicit remote default commit, then bind only origin/HEAD to that
exact ref. Never guess main, move a commit ref, change the reader, add a network request on the
recording path or change provenance/grades/controller/clock authority. Regression must use real
init + remote add+full fetch+SHAcheckout and actual extracted guard, not gitclone ambient metadata.
Protect main/trunk, genuine missing lines, missing expected default and a decoy main reference.

## Answer — 2026-10-26, source capability verified privately

The unchanged named gate check is `verify/can-record/verify-can-record.sh`.

A fresh init/full-fetch/SHA-checkout on a default named `trunk` can have no
`origin/HEAD`, even when the remote advertises its correct default and the recorded line is
present. The reader then cannot find the default, or selects an unrelated `main` if one exists.
The original minimal CLI control passes with the hint, fails when only that symbolic ref is
removed, and passes again when only that hint is restored. Actual init/fetch replay with the
same Git 2.55.0 as the captured runner reproduces the missing hint; it does not rely on clone
metadata or claim every Git configuration has this behavior.

The existing trusted workflow guard now verifies the already-fetched explicit
`refs/remotes/origin/${DEFAULT_BRANCH}^{commit}` and binds only `refs/remotes/origin/HEAD`
to that exact ref. It runs after event default validation and the existing branch-specific
fetch, before exporting the verdict. There is no main/master guess, new network request on
the recording path, commit-ref move or change to measured HEAD. The reader, recording/cage
shell, event authority and reviewed delivery controller are unchanged.

The regression initializes and fetches real TEST_ONLY Git history, consumes the actual gate
checkout input and executes the actual extracted guard and unchanged stranded CLI. Main/trunk,
a genuine missing line, a decoy main and a missing expected default are covered. Existing
feature/forged-feature and detached recording/cage controls remain strict. The old workflow
produces four failures; the fix passes all 81 targeted tests; restoring the original workflow
reproduces those four failures. The original graph replay also changes from CLI failure to
success without moving source/default commits or changing the recorded line. A restoration
reporter's initial missing-ref exit-code assertion was corrected separately and retained as
a harness STOP; it is not credited as the production failure.

These are private TEST_ONLY scripted Git/guard controls, not live execution of the external
Action on a hosted renamed default, signer issuance or a new primary. Validation is based on
source 3f317062. The later genuine primary468 measured that same public source before this
private fix; it supplies no 167 coverage. Its recorded observation-only merge e3411606 is a
separate prospective delivery-base advance. No policy, price, genuine financial replay,
controller permission, observation, capture, historical grade or signing operation changed.

## Recorded-check qualification

**Qualification, 2026-10-26.** At the private validation base 3f317062,
`verify/can-record/verify-can-record.sh` still grades FAIL in original recorded run466
(116 PASS / 1 FAIL / 26 SKIP / 8 EXCLUDED). That original remains unchanged. The subsequent
reported primary468 PASS measured source3f317062 without this private 167 fix, so neither
that PASS nor these TEST_ONLY controls proves hosted renamed-default execution of this
capability. Normal reviewed source delivery, configured CI and a genuine primary containing
167 remain separate. The unchanged reader's Git-history check ownership still belongs to
ticket100; naming the check does not manufacture a PASS or transfer that ownership.

## First configured CI and fixture follow-up

**Follow-up, 2026-10-26.** Public source074adc5e was published through PR279 on accepted
observation-only basee3411606. Its original configured CI40403152221/attempt1 completed with
3,535 PASS, 267 passed subtests, 24 SKIP and 2 FAIL: the retained historical coverage-floor
failure and a new cloud-selector fixture failure. Invariants retain 72 PASS / 1 historical
FAIL / 2 SKIP; the other six jobs succeeded. This original failure is not rerun or relabelled.

The cloud-selector test initialized a local trunk repository and self-remote but never fetched
its default tracking ref before invoking the actual guard. The default-path guard correctly
failed at the explicit-ref check with exit128, "Needed a single revision". Adding only the
actual checkout-equivalent full heads/tags fetch to that local fixture lets both guards pass
and preserves all 12 selector cases and 24 prepare/cleanup assertions, source HEAD and the
default tip. The fixture now performs that real filesystem-only fetch before the guard;
no guard, reader, selector, permission, cage, controller or expected assertion is changed.

The exact failing node was RED before the edit, the whole cloud-contract file passes
13 tests and 53 subtests, and test-file typing passes. Restoring only the original fixture
reproduces the same exit128 failure; the corrected fixture is restored exactly. The prior
81-test source capability proof is retained without a new run or change to its tested workflow,
reader or checkout test bytes. This follow-up changes only fixture setup and this dated record.
Its normal fast-forward publication, new configured CI and a genuine primary containing167
remain separate; original466, genuine pre167 run468 and all observation/capture bytes remain
unchanged. These local fixtures run no hosted Action, Kind/provider, financial replay or signer.
