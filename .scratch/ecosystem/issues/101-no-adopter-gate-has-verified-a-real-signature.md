# 101 — No adopter gate has ever verified a real published signature, and ludlow's cannot

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

The adopter gate's whole job is to verify the publisher's signed evidence against an identity the
institution holds itself (ADR-0011). Three institutions run one, and until ticket 99's
`verify/fold-agreement/verify-fold-agreement.sh` ran on 2026-09-05, **not one of them had ever been
observed verifying a signature platform actually published.** The first check that tried found that
ludlow's gate cannot: with the cosign version ludlow itself pins, its own invocation refuses every
bundle platform publishes, before it looks at the signature at all.

Three findings, all measured. Done = ludlow's gate verifies platform's published evidence (or
refuses it for a reason about the signature, not about a flag), driftwood's gate is exercised by
something, and no harness in the estate claims a pass over a refusal or discloses a limit that has
since stopped being true.

## Finding 1 — ludlow's gate refuses every bundle platform publishes (the blocking one)

`ludlow/.github/scripts/adopter_gate.py:verify_evidence()` calls

    cosign verify-blob --bundle=... --trusted-root=<committed trusted_root.json> \
        --new-bundle-format=true --certificate-identity-regexp=... --certificate-oidc-issuer=... <doc>

Against platform's real committed evidence (`computed-semver/evidence/4.0.0.json.bundle` at tag
`v2.0.1`) and cosign v3.1.3 — the version `ludlow/.github/workflows/shift-left.yml` installs by
checksum — that returns

    Flag --new-bundle-format has been deprecated, this will be the only supported format in future versions
    Error: --trusted-root only supported with --new-bundle-format
    error during command execution: --trusted-root only supported with --new-bundle-format

exit 1. `run()` turns that into `REFUSE: policy 4.0.0: cosign verify-blob refused the evidence
signature (...)`, which is a refusal about a command line wearing the words of a refusal about a
signature.

**The mechanism, measured both ways.** Platform's published bundles are the LEGACY cosign shape
(`base64Signature` / `cert` / `rekorBundle`). A bundle cosign signs today is the new Sigstore shape
(`mediaType` / `verificationMaterial` / `messageSignature`). With a NEW-format bundle the exact same
flag combination verifies fine — confirmed here with a locally key-signed blob, `Verified OK`. So
the flags are not wrong in themselves; they are wrong for the artefact platform actually publishes.

**It is LATENT, not currently firing.** `diff_versions()` only classifies a version `changed` when
ludlow's own composed member set changes, so the gate reaches `verify_evidence()` for the first time
on the next real policy adoption — and refuses it. ludlow's last two green `shift-left` runs
(2026-09-04) never entered this path.

Three candidate remedies, with their trade-offs. None is chosen here; this is an architectural call
in ludlow's repository and it belongs in ludlow's own reviewed pull request.

1. **Drop `--trusted-root` (and the format flag) and verify the legacy bundle the way driftwood and
   tuppence do.** Cheapest, and it demonstrably works: both other adopters verify platform's real
   bundles offline in about a second with no trust-root flag at all. The cost is the property
   ludlow's own harness Part E was built to prove — without `--trusted-root`, cosign fetches its
   trust root from Sigstore's TUF CDN, so verification acquires a network dependency and fails
   closed when egress is blocked. That is a real regression against a real, tested property, and it
   would need a note saying so.
2. **Re-sign platform's evidence in the new bundle format.** Fixes it at the source and lets ludlow
   keep its offline trust root, and every adopter gains a modern bundle. The cost is that it is a
   publisher change with an estate-wide blast radius: `cut-release.yml` signs, driftwood and
   tuppence verify legacy bundles today and would have to accept both shapes through a transition,
   and the already-published bundles on cut tags are immutable, so the two formats coexist until
   every pinned tag has moved. Also the largest piece of work.
3. **Pin a cosign version whose `--trusted-root` accepts a legacy bundle**, if one exists.
   Smallest diff if true, and it keeps both properties. The cost is that it has not been shown to be
   true — it needs someone to find the version and check it — and it pins the estate to an older
   binary, which is a security posture decision, not a convenience.

## Finding 2 — driftwood has no adopter-gate harness at all

driftwood carries `verify-reconcile.sh` and `verify-twin-overlay.sh` and no `verify-adopter-gate.sh`.
tuppence and ludlow each have one in the gate (`talk/verify-manifest.txt` places both). So until
ticket 99's fold-agreement check, **nothing in the estate had ever run driftwood's gate**, and the
one thing that grades it now is a hub check whose subject is agreement between three gates, not
driftwood's own behaviour in depth. driftwood's gate is the one whose reading the other two were
changed to match, which makes the hole worse than it looks.

## Finding 3 — tuppence's harness prints a pass claim over a refusal

`tuppence/scripts/verify-adopter-gate.sh` Scenario E tolerates the designed composed-major refusal
(correctly: it exists to prove `parse_pin()` walks a multi-document stream and that real cosign
ACCEPTS platform's real bundles). Two lines after the gate returns exit 1 it prints

    ok  E: the gate PASSES against the real, currently-committed platform-pin.yaml -- ...

That sentence is false as written on every run where the estate composes a major, which is every run
since 2026-08-31. What the scenario observed is that the checkout, the commit match and every
element's signature verification succeeded and the refusal that followed was the designed one. It
should say that.

## The lesson worth carrying (delegated, ADR-0025, 2026-09-05)

**A disclosed limit is an assertion, and it goes stale like any other.** ludlow's harness header
says it "does NOT prove, and cannot, offline: that cosign verify-blob ACCEPTS a genuinely valid
bundle" and that "the accept-path here is exercised in real GitHub Actions runs, never locally".
Both are now false: tuppence's Scenario E proves an offline accept against platform's real bundles
in about a second, and ludlow's own accept path has never run in CI either, because its gate only
reaches `verify_evidence()` when the member set changes. The disclosure was true when written and
nothing re-read it, so it went on excusing a gap that had become a defect. The estate grades its
PASS lines; it grades none of its "cannot" lines.

## Notes

Charted 2026-09-05 from ticket 99's build and its review. Ticket 99's own record carried a wrong
diagnosis of finding 1 for a few hours — it said ludlow's harness "stubs cosign", which it never
does — and that is corrected in ticket 99's Answer. The harness runs the real binary in Parts C and
E; what hid the defect is that Part E proves the offline property against a locally key-signed
fixture in the NEW bundle format, a shape that happens to match the flag the served artefact does
not have, and that E1/E2/E3 invoke cosign directly rather than through `adopter_gate.py`.

## Answer

Built 2026-09-06. All three findings, plus one the build found and one the build caused.

### Finding 1 — the remedy, and why not the other three

**None of the ticket's three remedies verifies the served artefact with the served tool under the
identity ludlow itself holds, offline. A fourth does, and it is what landed** (`delegated`,
ADR-0025).

**Chosen: pin the trust material the LEGACY verification path actually reads, selected by the log
identifiers the artefact itself names.** cosign's two verification paths take trust material
through different doors. A new-format bundle takes a whole trusted root through `--trusted-root`
with `--new-bundle-format=true`. A legacy bundle -- which is every bundle platform has published
-- refuses `--trusted-root` outright and reads `SIGSTORE_ROOT_FILE`,
`SIGSTORE_REKOR_PUBLIC_KEY` and `SIGSTORE_CT_LOG_PUBLIC_KEY_FILE` instead. Both doors are now fed
from the ONE committed `trusted_root.json` ludlow already holds, so nothing new is trusted and the
pin is still one reviewed file. The gate chooses the door by the bundle's own shape.

The measurement that decided it, taken with cosign v3.1.3 -- the version ludlow's own
`shift-left.yml` installs by checksum -- against platform's real committed bundle at `v2.0.1`:

| invocation | cold TUF cache, egress blocked |
|---|---|
| `--trusted-root` + `--new-bundle-format=true` (what ludlow shipped) | exit 1, `--trusted-root only supported with --new-bundle-format` |
| no flags at all (what driftwood and tuppence do) | exit 1, `tuf: failed to download 13.root.json` |
| no flags, WARM cache | `Verified OK` |
| pinned `SIGSTORE_*` material, cold cache | **`Verified OK`, exit 0** |

**Why not remedy 1** (drop the flags, verify as driftwood and tuppence do). Rejected on that third
and fourth row, not on preference. Those two verify offline *only where the cache is already warm*,
and a CI runner is cold on every run -- so remedy 1 would have traded a real, tested property for a
live network dependency in a required check, while appearing to work everywhere anyone tried it.
The ticket's own text called this cost "a real regression against a real, tested property"; the
measurement is what turns that from a worry into a fact.

**Why not remedy 2** (re-sign platform's evidence in the new bundle format). Not wrong -- it is the
right long-run shape -- but it is a publisher change with estate-wide blast radius, the bundles on
already-cut tags are immutable so both formats would coexist until every pinned tag moved, and it
needs a tag, which only `cut-release.yml` cuts and only the owner dispatches. Nothing here fakes
one. When it happens ludlow's gate already handles it: the `--trusted-root` door is still there and
the selfcheck exercises it.

**Why not remedy 3** (pin a cosign whose `--trusted-root` accepts a legacy bundle). Moot once
remedy 4 works with the version already pinned, and it would have traded a current binary for an
older one -- a security-posture decision taken for a convenience. It is also unfalsified rather
than false: nobody has found such a version, and ludlow's harness E1 now re-measures the flag
pairing on every run, so if a future cosign accepts it the harness says so instead of the estate
assuming it never will.

**What remedy 4 costs, said plainly.** cosign reads only the FIRST PEM block of the CT key file --
measured, the same two keys concatenated the other way round answer `ctfe public key not found for
payload` -- so the gate must select the right key, which means parsing the SCT extension out of the
certificate's DER (about 25 lines of pure code, graded in the selfcheck against bytes the test lays
down itself). And a trust root that goes stale now REFUSES LOUDLY AND BY NAME -- naming the log id
the certificate carries and the file that does not -- instead of silently fetching a fresh one.
Refreshing `trusted_root.json` becomes a real maintenance obligation, and Sigstore rotating a log
would turn ludlow's gate red until a reviewed commit lands. That is the correct failure and it is
a cost; ticket 105 proposes a staleness report so it arrives as a schedule rather than a surprise.

**A bundle shape the gate cannot read is refused before cosign is called** (`delegated`). Choosing
trust material means reading the bundle; calling cosign without it is exactly the live TUF fetch
the pin exists to prevent. The refusal names the shape. Part C's assertions were rewritten to grade
that refusal rather than a cosign refusal, and what Part C used to prove -- that cosign is really
invoked and really refuses -- moved to Part E, against bytes platform actually published, which is
a stronger place to prove it.

### Finding 2 — driftwood's gate is exercised, in depth

`driftwood/scripts/verify-adopter-gate.sh` is new: driftwood's own gate, in the shape its own
`shift-left.yml` spells it (`compose ... --adopter-dir/--base-ref/--head-ref`), against platform's
real published evidence at the tag driftwood pins, read from a real clone. Only the movement is
planted. A real ACCEPT (C), a real REFUSE on a changed signature byte (D), a real REFUSE under a
foreign identity constant (E, through the module's own `verify_evidence` because `compose` has no
identity flag -- which is the point), the pin made load-bearing (A), a movement of nothing reading
no evidence (B, asserted from the run's own output), a retirement forcing major (F), the gate's own
selfcheck (H).

### Finding 3 — the pass claim over a refusal is gone

tuppence's Scenario E now branches on the exit code. On the refusal path it says that everything
ahead of the refusal succeeded for real and that the refusal which followed was the designed one --
which is what it observed. It is not a pass and is no longer reported as one.

### The lesson, applied rather than repeated

Three "cannot" lines had stopped being true and nothing re-read them. Every one is now **a number
the run prints**, not a sentence:

* ludlow Part E5 -- the same real bundle without the committed trust material, cold cache: prints
  the exit code that makes E2's offline claim measured.
* driftwood scenario G and tuppence scenario G -- that repository's own cosign invocation, cold
  cache, egress blocked: prints `exit 1` today.
* the hub's new check -- one line per adopter, from that adopter's own gate.

Where a sentence remains it is dated (`confirmed 2026-09-06`) and it is about SIGNING, which is
genuinely out of reach without a live Actions credential. Verifying what platform already signed
never needed one, and every harness now does it.

### What the estate gained: a check that grades the sentence

`verify/real-signature/verify-a-real-signature-is-checked.sh` (+ `real_signature.py`) grades:
**every adopter's own gate, run the way its own `shift-left.yml` runs it, ACCEPTS platform's real
published evidence for a version arriving in its window AND REFUSES the same evidence with one byte
of the publisher's own signature changed.**

Both halves, because neither alone discriminates (`delegated`). ludlow's gate refused every bundle
platform publishes for weeks; a check grading only the refusal would have called that a PASS. A
check grading only the acceptance would pass a gate that accepts everything. Proved, not argued --
run against the estate as `main` has it, the check names the defect on both halves:

    FAIL: ludlow's gate did NOT accept platform's real published evidence for policy 2.0.1
          arriving in its window (exit 1): error during command execution: --trusted-root only
          supported with --new-bundle-format)
    FAIL: ludlow's gate refused the tampered evidence, but for a reason that names neither cosign
          nor the signature -- a refusal about something else is not evidence that the signature
          was checked

Nothing is signed in it: the refuse half CORRUPTS one byte of a real signature, and
`tamper_signature` refuses to run at all on a bundle whose signature it cannot reach, because a
tamper that changed nothing would make the refuse half a second accept and pass. The invocation is
read out of each repository's own workflow by `fold_agreement.py`, reused rather than re-derived --
one grader of "how does this repository invoke its gate" is enough and two would drift.

It also PRINTS, and does not grade, each adopter's own gate re-run with a cold TUF cache and every
proxy pointed at a closed port. Today: ludlow 0, driftwood 1, tuppence 1.

### The finding the build made, and the one the build caused

**Found: driftwood's and tuppence's gates fetch a Sigstore trust root over the network on every CI
run**, and both said the opposite in their own docstrings ("offline"; "no network at all"). Not a
correctness hole -- the fetched root is genuine -- but an availability dependency in a required
check, a trust-distribution difference nobody chose, and a false sentence. The sentences are
corrected and the number is printed; closing the difference is charted as **ticket 105**, with the
three things that have to be decided rather than typed.

**Caused, then fixed: this build's own first green run was false.** This machine's global
`core.hooksPath` hook ran out of API calls partway through the day, so `git commit` began failing
silently inside the planting -- and `fold_agreement._commit` returned `git rev-parse HEAD`'s stdout
unconditionally, which on a repository with no commits is the literal string `"HEAD"` with a
non-zero exit nobody read. Two of three gates then answered a question nobody had planted (ludlow
saw an unchanged pin and adopted); only tuppence's gate, which refuses an unreadable ref, said so
out loud, and that FAIL is what exposed it. Both graders are now hermetic against the operator's
global and system git configuration, `_commit` raises instead of returning `"HEAD"`, and
`real_signature.py` refuses to grade a planting whose shas are not shas. A grader somebody's laptop
hook can turn green is worse than no grader -- and this one nearly was, in the ticket about
checking that observations were really made.

### Decisions

1. **Remedy 4 for ludlow, not remedies 1-3** (`delegated`, ADR-0025). Reasons and the measurement
   above. The deciding fact is that "offline" was being evidenced on warm laptops.
2. **A bundle whose shape the gate cannot read is refused before cosign is invoked** (`delegated`).
   Reason above. It changes what Part C proves and Part C says so.
3. **driftwood's and tuppence's gates are NOT changed to pin their trust material here**
   (`delegated`). It is the same helper three times and it would have been easy, but it puts new
   pinned trust material into two more organisations and raises a real question -- one root or
   three, and who refreshes them -- that belongs in a ticket that decides it (105). What this
   ticket owed them was that their claim stop being false, and a printed number does that
   permanently where a corrected sentence would go stale again.
4. **The offline measurement is reported, never graded** (`delegated`). Grading it would make two
   adopters red on a property this ticket did not undertake to give them, and a red with no ticket
   behind it teaches readers to ignore reds. It is a number on every run, and ticket 105 flips it.
5. **The hub check re-runs each adopter's own gate for the offline measurement rather than calling
   cosign itself** (`delegated`). The first draft hand-rolled a flagless `cosign verify-blob` and
   reported ludlow as network-dependent when ludlow's own gate is not -- a proxy for the operation,
   in the ticket whose whole rule is to name the operation that reaches the served artefact. Caught
   by reading its own output, and recorded because the mistake is the instructive part.
6. **ludlow's manifest row is reclassified `simulation` -> `estate-observation`** (`delegated`):
   Part E's verdict now turns on the content of platform's artefact and changes the day platform
   re-signs. **tuppence's row is reclassified the same way, at review (F8, 2026-09-06)**: this
   ticket's first draft left it `simulation` and said so, on the ground that its Scenario E had
   already turned on platform's real bundles before today, so the misclassification predated the
   ticket and was not its change to make. The review asked for the inconsistency to be closed
   rather than recorded, and closing it is the smaller lie: the row now reads `estate-observation`
   with its one real could-not-look (no cosign) declared, and the manifest comment carries the
   same history so the reclassification is not mistaken for a claim that tuppence changed today.

### How it is graded

* `verify/real-signature/verify-a-real-signature-is-checked.sh` -- the new sentence, both halves,
  per adopter, plus the printed offline number.
* `verify/fold-agreement/verify-fold-agreement.sh` -- **now green on all four planted movements**;
  ludlow's two reds are cleared (see the exact before/after below).
* `verify/unreviewed-major/verify-unreviewed-major-in-window.sh` -- still red, entirely for the
  owner's carried-major reason (all three adopters carry policy 4.0.0), never for ludlow's.
* `ludlow/verify-adopter-gate.sh` Parts C and E; `driftwood/scripts/verify-adopter-gate.sh` A-H;
  `tuppence/scripts/verify-adopter-gate.sh` E and the new G.
* `ludlow/.github/scripts/adopter_gate.py --selfcheck` section 13, written red first.
* `tests/test_real_signature.py` (18 cases) and two added to `tests/test_fold_agreement.py`.

### Red before green, exactly

    # ludlow's pure seam, written before the code
    $ python3 .github/scripts/adopter_gate.py --selfcheck
    NameError: name 'bundle_shape' is not defined          <- red
    ... PASS: adopter_gate.py selfcheck (...)              <- green

    # the estate, before and after, same command, same planted movements
    $ bash verify/fold-agreement/verify-fold-agreement.sh
    FAIL: case 'arrival': ludlow's gate answered refuse (stating no composed bump at all: error
          during command execution: --trusted-root only supported with --new-bundle-format))
          where driftwood, tuppence answered refuse (composed 'major')
    FAIL: case 'quiet': ludlow's gate answered refuse (...same...) where driftwood, tuppence
          answered adopt (composed 'none')
    FAIL: 2 planted movement(s) were answered differently by two adopter gates    <- red
    ...
    PASS: on 4 planted movements ... the 3 adopter gates that answered (driftwood, ludlow,
          tuppence) ... returned the same verdict and the same composed bump                <- green

The hub grader's own two load-bearing rules were reverted in turn to record their reds
(`test_a_gate_that_refuses_both_halves_is_false` fails when `grade()` stops checking the accept
half; `test_a_bundle_whose_signature_cannot_be_reached_raises` fails when `tamper_signature`
returns an unreachable bundle unchanged; the planting rule fails when `_planted_or_none` accepts
anything). Said plainly rather than dressed up: `real_signature.py` was written before its tests,
and those reds are mutations, not a test-first sequence. ludlow's is the genuine test-first one.

### The exact green, quoted

    $ PAVC_ESTATE_CLONE=<estate with this ticket's three branches> \
        bash verify/real-signature/verify-a-real-signature-is-checked.sh
    ok: platform checked out at v2.0.1 (533dccb0a823); the served artefact is its own published
        evidence for policy 2.0.1
    ok: the same tag re-cut with one base64 character of policy 2.0.1's real signature changed
        (2c440612b7b7) -- nothing else moved, so a gate that adopts it adopted an unverified signature
    note: driftwood: its own gate cannot verify platform's real published bundle with a cold TUF
          cache and egress blocked -- exit 1 ... (eco-system ticket 105)
    note: ludlow: its own gate verifies platform's real published bundle with a cold TUF cache and
          every proxy pointed at a closed port -- exit 0, no network needed
    note: tuppence: ... exit 1 ... (eco-system ticket 105)
    ok: driftwood: real cosign accepted platform's own published signature for policy 2.0.1, and the
        gate adopted
    ok: driftwood: the same bundle with one signature byte changed was refused, naming the signature
    ok: ludlow: real cosign accepted platform's own published signature for policy 2.0.1, and the
        gate adopted
    ok: ludlow: the same bundle with one signature byte changed was refused, naming the signature
    ok: tuppence: real cosign accepted platform's own published signature for policy 2.0.1, and the
        gate adopted
    ok: tuppence: the same bundle with one signature byte changed was refused, naming the signature
    PASS: every adopter gate in this estate accepted platform's own published signature and refused
          the same evidence with one byte of it changed, each through its own workflow's own
          invocation and its own identity constant

**What the green unit CI does NOT say (review F5).** `shift-left` and `compose-check` pass on
all three unit pull requests, and that is worth exactly one thing: the path those workflows
already ran still passes. **No unit CI job runs `--selfcheck` or the harness.** ludlow's gate
change is not exercised by ludlow's own CI at all -- `shift-left` reaches `verify_evidence()`
only when the composed member set moves, which is the same latency that hid the original
defect for weeks. Everything that grades this ticket's work ran locally and in the hub gate:
the three harnesses, the two selfchecks, and `verify/real-signature/`. Wiring each adopter's
harness into its own CI is not done here and is not charted either; it is named so that a
reader does not read three green checkmarks as this ticket being covered by unit CI.

Pull requests, none merged: hub policy-as-versioned-flux#53, ludlow
policy-as-versioned-ludlow/ludlow#19, driftwood policy-as-versioned-driftwood/driftwood#28,
tuppence policy-as-versioned-tuppence/tuppence#22.

## Waits on the owner

1. **Whether platform policy 4.0.0's major is accepted for driftwood, for ludlow and for tuppence.**
   Unchanged from ticket 99, and untouched here: it is an authorisation (ADR-0025), one per
   institution, and it is the whole of `verify-unreviewed-major-in-window.sh`'s remaining red. This
   ticket records no review and invents no place to record one.
2. **Re-signing platform's evidence in the new bundle format** (remedy 2), if the owner wants the
   estate on modern bundles rather than on ludlow's per-log key selection. A tag is cut only by
   `cut-release.yml` and dispatched only by the owner; nothing here fakes one, and ludlow's gate
   already handles the new shape when it arrives.
3. Nothing else. All four branches are pushed and all four pull requests are open; none is merged.
   No unit change touches a workflow file, so no `workflows` grant is needed for any of them.

Map line: Ticket 101 (2026-09-06): the adopter gates now verify a signature platform really
published -- ludlow's gate could not verify ANY of them with the cosign it pins, and rather than
drop the flags (measured: the other two are only offline on a warm cache, and a CI runner is cold
every run) it pins the trust material the LEGACY path actually reads, out of the same committed
trusted_root.json, with the per-log keys selected by the log identifiers the artefact itself names
and a loud refusal by name when the pin goes stale; driftwood got the adopter-gate harness it had
never had, tuppence's harness stopped printing a pass over a refusal, every "cannot" line in all
three is now a number the run prints, and
`verify/real-signature/verify-a-real-signature-is-checked.sh` grades the sentence nothing graded --
every adopter's own gate accepts platform's real published evidence AND refuses it with one byte of
the signature changed -- which names the old ludlow defect on both halves when pointed at main.

## Follow-up

> **Follow-up, 2026-09-08 (eco-system ticket 59).** This ticket is `resolved` and one of the four
> checks its Answer names is RED on the newest recorded run.
> `talk/truth.log` records run 179 (2026-09-08T14:11Z, `hub=fbbb547`) as pass=78 fail=10 skip=22 excluded=8 total=118 ceiling=99, and on that run `verify/unreviewed-major/verify-unreviewed-major-in-window.sh` graded
> `FAIL: 3 line(s) observed false: a major carried in an adopter's composed window, or evidence at
> an adopter's own pin that did not verify -- each named above`, which is the last line of that
> run's committed capture. Ticket 59's derivation reads ownership from git, and `git log
> --full-history` on that script names tickets 99 and 101 -- but 101 only through ticket 99's own
> commit `721fd3b Review fixes: the resolver whitelists flags, and ticket 101 is charted`; none of
> this ticket's five commits (`7808746` to `aca7eca`) touched the script. A "charted" mention in a
> commit subject reading as ownership is the over-attribution ticket 59 accepts rather than works
> around, because it is loud (this paragraph is what it produced). The red itself is not anything
> this ticket built: it is the owner's carried-major authorisation -- all three adopters carry
> platform policy 4.0.0 -- which is Waits item 1 above, and it stays red until the owner records
> that review.
