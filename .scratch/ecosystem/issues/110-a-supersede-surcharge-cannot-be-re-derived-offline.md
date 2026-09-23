# 110 — A supersede surcharge cannot be re-derived offline, so a signed artefact stops re-rendering

Type: task
Status: open
Blocked by: none

## Question

Two features this estate built and signed now contradict each other, and the contradiction became
observable on 2026-09-10 the moment `ico v4.0.0` was tagged.

**Ticket 45's claim:** an adopter re-verifying its own signed composed tree OFFLINE gets the same
bytes. `verify()` is a byte comparison over every rendered file, so the vendored payload plus
`PROVENANCE.json` must be sufficient and the publisher's clone must not be needed.
`composition.py --selfcheck` asserts exactly that at the seam:
`assert rendered_absent == rendered_present`.

**Ticket 84's surcharge:** when a publisher supersedes the major an adopter pins, the composed
document carries a `supersede` price row, an EOL ramp of `+1x` per year behind capped at `+4x`,
where `since` is the day the newer major's SIGNING TAG was cut.

The surcharge is computed from the publisher's TAG DATES. A vendored copy of a payload cannot
carry the date of a tag that did not exist when it was vendored. So the row appears when the
publisher's clone is present and vanishes when it is absent, and ticket 45's assertion fails.

Measured first-hand in a private estate clone at platform `5b88f1d`, composing driftwood:

```
--- ico ABSENT
+++ ico PRESENT
 | ico | feed      | penalty-schema | driftwood | GBP | GBP 1,787,177.08 | no | isolated |
+| ico | supersede | penalty-schema | driftwood | GBP | GBP 0.00         | no | —        |
```

and, downstream of the extra row, every later price index shifts (`prices[6]` becomes `prices[7]`)
and the artefact's own footer count moves from 8 prices to 9. So the divergence is not one line: it
renumbers the named absences that cite price indices.

The amount is `GBP 0.00` **because the tag was cut that same day** and the ramp is zero on day zero.
It will not stay zero. Tomorrow it is a real number, and the two renders will differ by a priced
amount rather than by a zero.

## What has to be decided

1. **Which claim wins.** Portability and the surcharge cannot both hold in their current form. If
   portability wins, the surcharge has to be derived from something the adopter's own signed tree
   carries. If the surcharge wins, ticket 45's assertion and its promise have to be narrowed, and
   the deck and record that repeat the promise have to be narrowed with them.
2. **If portability wins, where does `since` come from?** The candidate is the vendored
   `PROVENANCE.json`: record the publisher's newest major and the date its tag was cut AT VENDOR
   TIME, so the ramp is a function of the artefact rather than of the world. That makes the number
   reproducible and stale by construction, which is a different honesty problem, and it needs
   saying out loud on the page.
3. **Whether a zero-valued row should render at all.** Today's difference is a row priced at zero.
   A rule that a zero surcharge is recorded but not rendered would postpone this exact failure
   rather than fix it, and would hide the day the clock starts. Decide deliberately, do not drift
   into it.

Done = `composition.py --selfcheck` passes with a publisher clone present and absent, and the
record states which of the two claims was narrowed and why.

## Notes

Charted 2026-09-10. The tag did not break this; it made it reachable. Ticket 84's own record
already names a related half: the supersede line vanished when a newer major's directory was
absent from the pinned checkout, and no adopter workflow passed `--as-of`, so a served line read
0.00 for a tag cut later. This is the same fault line seen from the portability side.

Two adopter pull requests are HELD on ticket 84 (tuppence 27, ludlow 24). Whatever is decided here
governs them, because both subscribe an adopter to a feed whose publisher can supersede it.

Record: ticket 45's `verify-portability`; ticket 84; `composition.py`'s selfcheck at the
`rendered_absent == rendered_present` assertion; `talk/verify-falls.txt` `run=234`.

## Build decisions, 2026-09-10

Implementation is under review; this ticket remains open until review and validation complete.
All choices below are delegated under ADR-0025 and the owner's instruction to implement the
remaining work with review gates.

1. **Portability wins.** A supersede surcharge describes the publisher tag state observed when
   this artefact was composed. It does not establish the publisher's current newest major. The
   handbook prints that limitation on each affected feed, including when the observation is
   current or unobserved, rather than hiding the qualification in a provenance file.
2. **Record the complete observation.** Each vendored `PROVENANCE.json` carries a versioned
   `publisher_observation`: feed identity, pinned version, resolved parent SHA, pin-signature
   observation, supersede observation, newest readable signed target, and oldest signed major's
   tag/date. Recording only `since` would still change the target, the observation and signature
   holes offline. The adopter's existing signature covers this record; it is an observation of
   the publisher's tags, not another publisher declaration or a claim of signature verification.
3. **Fresh composition and verification have different jobs.** Ordinary `compose` reads
   available publisher tags and records a new observation; with a publisher absent it reuses the
   vendored observation. `verify` explicitly replays the adopter's recorded observations even
   when a live publisher has acquired newer tags. The scheduled proposer's existing `compose
   --as-of` remains a fresh observation, so it can discover supersedes and grow the ramp. An
   explicit pricing date is also recorded in `HEADER.yaml` and replayed during verification.
4. **Zero rows remain.** They disclose the day the ramp starts; removing them would merely
   defer the discrepancy. The handbook prints the start and pricing dates beside the row,
   including the existing qualification when pricing precedes the signing date.
5. **Legacy behavior is explicit.** Provenance lacking the new observation cannot prove which
   tags were seen. Verification and offline composition refuse it as a named missing instrument;
   they do not backfill signed history from today's tags. Old signed artefacts remain verifiable
   with their pinned composer. Adopting this composer requires fresh composition with publisher
   clones present, followed by the ordinary reviewed release. Invalid observations, or those
   naming another feed/version/SHA, also refuse. Tuppence 27 and ludlow 24 retain ticket 84's
   release/pin/re-composition prerequisites.
6. **Preserve converter attribution offline.** The fixture exposed another byte difference:
   a converter originally copied from platform was re-labelled as publisher-owned on the next
   offline vendor pass. Re-vendoring preserves `converter_from` from the existing provenance.

### Validation, 2026-09-10

Red first at the `compose()`/`verify()` seam using a synthetic adopter, synthetic publisher git
repository, and the actual shipped converter: the signed newer major produced a different
render with the publisher absent. No fixture tag is placed on a real publisher. Five focused
cases now pass: byte-identical online/offline replay; nonzero pricing and later tags without
rewriting verification history; current/unobserved replay; legacy refresh; invalid identity and
tag dates. The handbook's 47 selfchecks pass. The full `composition.py --selfcheck` passes against an isolated estate assembled from cached
upstream refs: driftwood `a1817254`, nist `f83126f5`, ico `9653fd9f`, feeds `ca403965`, insurer
`61fba9db`, tuppence `bd15aaeb`, ludlow `2c2d740d`; platform is this implementation based on
`5b88f1d`. Its portability leg re-derives all 31 rendered files byte-identically with ico absent.
`pin_content.py --selfcheck`, Python compilation and shell syntax checks also pass.

The selfcheck needed `core.hooksPath=/dev/null` in its process environment because a pre-existing
fixture commit invokes the owner's global network hook otherwise. No persistent config changed.
The pre-existing installed-object invariance assertion excluded the header and handbook but
included provenance; it now excludes `PROVENANCE.json` too, because tag observations intentionally
change that record and no engine installs it.

Mypy reports the same 84 existing diagnostics on the base `5b88f1d` and this implementation;
comparing their messages and multiplicities finds no added or removed diagnostics. This is not a
claim of a clean typecheck. These are local validations, not a recorded TRUTH run, and at this validation checkpoint independent review and release were still pending. The gate wrapper now runs the
five fixture tests before the existing estate selfcheck.

### Independent review, 2026-09-10

Standards: no findings. Spec: one blocking finding was fixed red-first: a signed observation
without its tag and a supersede target tag naming another feed were accepted. Replay now checks
signature-tag presence by state, feed identity and pinned/target major, and start-major ordering.
The sixth focused test plants six malformed observations; all are refused. The reviewer reran
that regression test and confirmed the finding closed. Six focused tests now pass; the earlier
five-test count records validation before this review. Publication and rollout remain pending.


### Publication, 2026-09-10

Both review axes passed after the correction above. The signed implementation commit
`41761fa9747b63d73f52bbc8d9ac40bf3b28faf8` was merged through platform PR24 as
`3602142e5adb26945705c3dc3f86c1ab4ad66721` (the merge tree is identical to the reviewed tree).
The local secret scan reported zero secrets; the owner authorized a per-commit bypass of the
quota-exhausted network hook, with signing retained.

The proposed software release is **v3.0.0**, because the new composer requires a fresh
provenance observation when upgrading legacy compositions. The previous v2.0.1 is 82 commits
behind the implementation. In addition to the composition tests above, the Kyverno 1.18.2
shift-left proof and all eight release-tag fixture scenarios passed. The fixture scenarios
used process-scoped unsigned synthetic tags, not real publisher tags.

Publication is prepared but has not run: automatic approval review rejected the release
workflow dispatch because the authorization to implement, push and merge did not explicitly
name immutable software publication. Owner approval has been requested. After approval: cut
v3.0.0 from the reviewed main, run release.yml at ref v3.0.0 with tag input v3.0.0, verify the
release, then upgrade adopter pins and freshly compose before merging the held subscriptions.
No policy tag is re-cut and no adopter pin is advanced ahead of the software release.


**2026-09-10, publication authorized.** The owner explicitly approved publishing v3.0.0 through
the signed release workflows. The cut workflow is now running as
[34504582573](https://github.com/policy-as-versioned-platform/platform/actions/runs/34504582573).
The earlier automatic-approval block is cleared; signature verification and GitHub Release
publication remain gates before adopter upgrades.


**2026-09-10, published and verified.** The cut run 34504582573 and identity-pinned release run
34504674000 both succeeded. [Platform v3.0.0](https://github.com/policy-as-versioned-platform/platform/releases/tag/v3.0.0)
was published at 16:52:01Z and resolves to reviewed main
`3602142e5adb26945705c3dc3f86c1ab4ad66721`. Release verification checked the Actions signer
identity and issuer, the offline Rekor bundle, and the shift-left proof. Adopter migration is
now unblocked, but no adoption or recorded rollout result is implied by publication.

### Superseded map entry retained as history

- [110 — A supersede surcharge cannot be re-derived offline](issues/110-a-supersede-surcharge-cannot-be-re-derived-offline.md) — CHARTED, not built. Ticket 45 promises a signed composed tree re-renders byte-identically with the publisher's clone ABSENT; ticket 84's supersede surcharge is computed from the publisher's TAG DATES, which a vendored copy cannot carry. Cutting ico v4.0.0 made the contradiction observable: composing driftwood with ico present renders a `supersede` row priced GBP 0.00 that composing it with ico absent does not, which renumbers every later price index and moves the artefact's own footer count. `composition.py --selfcheck` fails on it today. The amount is zero only because the tag was cut that day; tomorrow the two renders differ by a priced amount. One of the two claims has to be narrowed, and the record has to say which.

Map line: `- [110 — A supersede surcharge cannot be re-derived offline](issues/110-a-supersede-surcharge-cannot-be-re-derived-offline.md) — open, implementation reviewed and merged in platform PR24; signed software v3.0.0 published and verified at 3602142. Composition now vendors identity-bound publisher observations and replays them offline; fresh composition observes current tags. Legacy provenance requires fresh composition when upgrading. Adopter pin upgrades, recomposition and recorded rollout proof remain outstanding.`

## Build, 2026-09-22

The rollout was measured first. It had already happened. The work left was one stale selfcheck
leg in platform and one hub check that read the wrong pin.

### Where each adopter stands, measured 2026-09-23

Each adopter was read at a detached worktree of its `origin/main`: driftwood `c96c412`,
tuppence `7009ea9`, ludlow `32d5696`. These are the SHAs the hub's TRUTH line for run 270 names.

- **Composer pin.** All three carry `.github/platform-tools-pin.yaml` at platform `v3.0.0`,
  commit `3602142`. The policy pin `gitops/platform/platform-pin.yaml` stays at `v2.0.1`. The
  compiler upgrade shipped through ordinary reviewed PRs on 2026-09-10: driftwood PR 37, tuppence
  PR 32, ludlow PR 29. Each merged as `pavc-other-hand`; `compose-check` and `shift-left` passed
  on each (read with `gh pr checks`).
- **Fresh observations.** Every vendored `PROVENANCE.json` on each `origin/main` carries a
  `publisher_observation` with `schema: 1` (driftwood 3, tuppence 2, ludlow 2; read with a
  Python one-liner over each file).
- **Fresh recompose with publisher clones present.** A scratch estate held local clones at each
  adopter's exact pins: platform `v2.0.1`, nist `v1.1.0`, ico `v3.0.0`, feeds
  `threat-register/v2.0.0` and `threat-register/v1.0.0` (one commit, `69c89b0`), insurer
  `v1.0.0`, and the tools at `v3.0.0`. `platform-tools.py check` verified the tools tag's
  release identity with gitsign 0.17.1. `platform-tools.py compose . --out .` exited 0 for all
  three, and `git status --porcelain` was empty afterwards. The committed trees are what the
  v3.0.0 composer writes today.
- **Verify, present and absent.** `platform-tools.py verify` exited 0 for all three with every
  clone present, with ico absent, and with feeds absent. That is ticket 45's byte claim, held on
  the served artefacts.
- **Offline compose differs only in `evidence.json`.** Composing with ico or feeds absent changed
  `composed/evidence.json` alone. The diff has two parts: the `publisher-clone-absent` limit
  opens and names the absent publisher, which is the intended disclosure, and the replayed
  observation prints its keys sorted where the live one prints them in insertion order.
  `evidence.json` is outside the rendered set that `verify()` compares, and the selfcheck says
  so. The key-order difference is cosmetic and is recorded here, not fixed.

No adopter repository needed a change. No adopter PR is opened.

### Done, measured

`composition.py --selfcheck` on platform `origin/main` (`3d7f098`) still failed at the gate.
The failure was no longer ticket 110's. The portability leg printed
`OK portability: with ico's clone ABSENT, driftwood re-derives every price it signed` in the
hub's own capture, and again here. The selfcheck then died on ticket 84's leg:
`assert len(sups) == 1`. That leg assumed tuppence was behind exactly one publisher, at
`threat-register/v2`. On 2026-09-10 ico cut `v4.0.0` and feeds cut `threat-register/v3.0.0`, so
the composer correctly priced two supersede rows, and the fixture's own assumptions went stale.

Reproduced red first in an estate built at the TRUTH line's refs (platform `3d7f098`, driftwood
`c96c412`, feeds `ff3ac9a`, ico `abcb3a8`, insurer `d1c1844`, ludlow `32d5696`, nist `f83126f`,
tuppence `7009ea9`): the same `AssertionError` at the same line. The fix reads the majors ahead
off the feeds clone's tags and directories. It asserts one supersede row per feed line observed
behind, the newest readable major as the target, and the oldest signed major ahead as `since`.
Green after: `composition.py --selfcheck` exited 0 with 89 `OK` lines, 84 before the failure.
The supersede line printed `threat-register/v3.0.0 (cut 2026-09-10), behind since
threat-register/v2.0.0 was cut 2026-09-01` and named both rows, `feeds/threat-register` and
`ico/penalty-schema`.

`compose/verify-composition.sh` then exited 3, not 1. Its steps 0, 0a and 0b ran 6, 9 and 9
tests, all OK. Step 1 (the selfcheck), 1a and 1b passed. Step 2 is a could-not-look:
`platform@2.0.1 (533dccb0) does not contain distribution/policies/v5.0.0`. That waits on each
adopter's policy pin moving to policy 5.0.0, which is ticket 113's owner step. So the gate row
should move from FAIL to SKIP, which is where it stood before run 234.

The record states which claim was narrowed and why: see the 2026-09-10 build decisions. The
surcharge was narrowed. It describes the publisher tags observed at composition. Portability won.

### The hub read the wrong pin

`verify/supersede/verify-supersede.sh` graded every adopter SKIP with "composed under platform
v2.0.1, which carries no supersede rule". That was false. It read the composer off the policy
pin, and since 2026-09-10 the composer runs from the compiler pin. `supersede.py` now reads
`.github/platform-tools-pin.yaml` at the served ref, and falls back to the policy pin only where
no compiler pin exists. Red first: a planted case in `supersede.py selfcheck` raised
`NameError: served_composer_tag`. Green: `OK 25 planted grades bite` (22 before).

Run against the real estate, the check now exits 1 with 4 FAILs and 2 PASSes:

- PASS: tuppence and ludlow `threat-register@v1` carry a supersede line, zero because `as_of`
  2026-08-28 precedes the 2026-09-01 tag day.
- FAIL: driftwood, tuppence and ludlow `ico/penalty-schema@v3` sit behind `v4.0.0` and carry no
  supersede line. FAIL: driftwood `threat-register@v2` sits behind `threat-register/v3.0.0` and
  carries no line.

Those 4 FAILs are real. Each served feed entry records `superseded.state: unobserved`, because
the publisher checkout at the adopter's pin carries no directory for any newer major, and
`newest_published_major()` then writes no line. Ticket 84's review F1 said a missing newer
directory must never make being behind free. It still does when no newer directory is readable
at all. That is ticket 84's composer rule, not ticket 110's replay, and fixing it needs a new
signed platform release. It is recorded here and not built.

Net effect on the gate if both PRs merge: `verify-composition.sh` FAIL to SKIP, and
`verify-supersede.sh` SKIP to FAIL. The false could-not-look becomes a true finding.

### Decisions (delegated, ADR-0025)

1. **No adopter PR.** The rollout the ticket asked for is on every adopter's `origin/main`, and
   a fresh recompose reproduces it byte for byte. Opening a PR to re-commit identical bytes
   would prove nothing. Reason: the measurement is the proof.
2. **Fix the fixture, not the composer.** The composer priced two rows because two publishers
   really superseded tuppence. The fixture assumed a world from before 2026-09-10. It now reads
   the tags instead of naming them.
3. **The hub reads the compiler pin.** Evidence is written by the composer the compiler pin
   names. A policy pin says which policy is accepted, not which program composed it.
4. **Let the hub check go red.** Softening it to accept `unobserved` would hide what ticket 84's
   review said must not be hidden. A false SKIP is worse than a true FAIL.
5. **Leave the `evidence.json` key order alone.** It sits outside the verified set and changes
   no price. It is recorded above.

### Held PRs: tuppence 27 and ludlow 24

Both still say HOLD until a platform tag carries the ticket-84 composer and the platform pin
moves. That condition is now met another way. The compiler pin on each `origin/main` is
`v3.0.0`, which carries the ticket-84 composer, and no policy pin move is needed. Measured in
scratch: each held branch's `party.yaml` on today's `origin/main`, composed with tools `v3.0.0`
and publisher clones present, gives outcome `composed` with 0 refusals. tuppence prices
`cve@v2` at 241,549.84 GBP with an `untagged-pin` hole and a `threat-register` supersede line of
4,268.55 GBP. ludlow prices `eol@v2` at 772,556.59 GBP with an `untagged-pin` hole and a
supersede line of 6,103.04 GBP. These match the figures in each PR body.

What they wait on now: a rebase onto `origin/main`, a recompose committed with the v3.0.0
compiler, and review. `git merge-tree` shows one conflict each, in `propose-tier.yml`. Main's
version already passes `--as-of` through the compiler pin, so the branch's guarded `--as-of`
is superseded and main's side should be kept. No feeds `cve/v*` or `eol/v*` tag exists on the
remote (`git ls-remote --tags`), so both pins stay priced holes. Neither PR was rebased or
merged here.

### A red the rollout made reachable

`propose-tier` has failed on every run in tuppence since 2026-09-10T17:55Z and in ludlow since
2026-09-10T17:53Z, the runs on the compiler PRs themselves. The last successes were
2026-09-10T13:08Z and 2026-09-10T13:48Z (read with `gh run list`). The log shows the proposer pushing
`wargamer/retire-<unit>-feeds-threat-register-v1-to-v2` and then `gh pr create` raising
`CalledProcessError`. The v3.0.0 composer now sees threat-register v1 as behind, so the
retirement path runs for the first time. The branches exist on each remote, 1 commit ahead
touching `party.yaml`. `tier_pr.py` captures `gh`'s stderr and drops it, so the exact error is
not in the log. What was measured: the repo-level `can_approve_pull_request_reviews` reads
`false` in all three adopter repos, and no PR by `app/github-actions` exists in any of them.
That fits the "Actions may not create pull requests" refusal, but the error text was not seen.

### Waiting on the owner

- Allowing GitHub Actions to create pull requests in the tuppence and ludlow orgs, or giving
  `propose-tier` an app token for that. This is an authorisation. Until then the retirement
  proposals ticket 84 designed cannot land.
- A signed platform release for any change to the supersede rule that prices a pin behind an
  unreadable newer major. That work belongs to ticket 84 and is not built.
- Policy 5.0.0 acceptance (ticket 113) turns `verify-composition.sh` step 2 from SKIP to PASS.
  Renovate's tuppence PR 30 and ludlow PR 27 move both pins to `v3.2.0` and fail `compose-check`.
  They were left alone.

### PRs

- platform: `ticket-110-selfcheck-derives-supersede`, the selfcheck fix.
- hub: `ticket-110-rollout-measured`, the supersede pin fix and this record.

Merge order: platform first, then the hub. No adopter PR is needed. The platform change is
selfcheck-only, so it needs no release: the gate reads platform at `main`.

### Tests run

- `composition.py --selfcheck` at the TRUTH refs: red (`assert len(sups) == 1`), then green (rc 0, 89 OK).
- `compose/verify-composition.sh`: rc 3; 6, 9 and 9 unittests OK; SKIP at step 2 only.
- `python3 -m py_compile compose/composition.py`: clean.
- `supersede.py selfcheck`: red (`NameError`), then green (25 plants).
- `verify/supersede/verify-supersede.sh` against `.estate-clone`: rc 1, 4 FAIL, 2 PASS, as above.
- `.venv/bin/python -m mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores`:
  `Success: no issues found in 198 source files`.
- Per adopter: `platform-tools.py check`, `compose` (clean tree after) and `verify` with every
  clone present, with ico absent and with feeds absent. All exit 0.
