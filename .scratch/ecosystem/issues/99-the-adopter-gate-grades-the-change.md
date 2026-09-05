# 99 — The adopter gate grades the change, not the window

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Three adopters read ADR-0011's adopter gate two different ways, and only one can be the estate's.
driftwood and ludlow fold the composed bump over the versions a pull request ADDS or RETIRES.
tuppence folds it over every version in its whole current supported window. All three refuse on a
composed major. So once a major sits in tuppence's window, every pull request composes major and is
refused, whatever it changes. Its last green `shift-left` was 2026-08-28 and it has failed twelve
consecutive runs since.

Change the losing reading to match, and make the property tuppence's reading was protecting a
standing report rather than a per-pull-request refusal. Done = tuppence's `shift-left` grades the
change a pull request makes, an unreviewed major in the window is reported by name and does not
depend on anyone opening a pull request to be seen, and a check in the gate refuses the day two
adopters diverge on this again.

## The decision (delegated, ADR-0025, 2026-09-05)

**The delta fold is the estate's reading. tuppence changes.** Four reasons, in order of weight.

1. **ADR-0011 scopes the gate to the movement.** It runs "on the Renovate bump pull request" and
   "computes that institution's own composed bump". A bump is a movement. tuppence reports `major`
   for a pull request whose declared bump is `none`, because its pin does not move — so it is
   answering a question about the window, not about the change in front of it.
2. **The refusal names a remedy the gate cannot accept.** "refusing to adopt v2.0.1 without human
   review" has no input by which a review can be recorded, no flag and no other path: line 593 is
   `if composed == "major": print(FAIL...); return 1`, unconditional. A refusal that cannot be
   satisfied is not strict, it is non-terminating.
3. **A check that fails on every pull request has stopped discriminating.** It can no longer signal
   a regression, which is what a gate is for. Twelve consecutive failures carry exactly as much
   information as none.
4. **Two of three adopters read it the other way and are green** on the same platform tag and the
   same signed evidence. ludlow's `shift-left` passed twice on 2026-09-04, once on the very
   Renovate branch tuppence failed.

**What tuppence's reading was protecting, and how it survives.** It is a real property: an
institution should not quietly carry a major nobody reviewed. Keeping it as a per-pull-request
refusal is what broke, and it is also the wrong shape — the fact does not depend on anyone opening
a pull request, so a gate that only speaks on a pull request is the wrong place to say it. Report
it instead: an unreviewed major in the composed window is a standing, named line the truth surface
carries, red or could-not-look on its own terms and on every run. Then it is visible on a day
nobody proposes anything, which is exactly when it matters.

**Not an override.** ADR-0011's "No override" section bans a carve-out for a named workload at any
scope. This is not one. Nothing is exempted and no refusal is weakened for a subject: the gate is
pointed at the question ADR-0011 asks it, and the question it was answering instead is moved to a
place that answers it continuously rather than incidentally.

**What is NOT decided here, because it is the owner's.** Whether platform policy version 4.0.0's
major is reviewed and accepted for tuppence is an authorisation, and ADR-0025 keeps those with the
owner. This ticket does not record a review and must not invent one. It makes the absence of one a
standing, honest line instead of a refusal that blocks everything else.

## Notes

Charted 2026-09-05 from ticket 64's build and its adversarial review. The diagnosis is recorded in
tuppence's own `.github/scripts/adopter-gate.py` docstring with the run identifiers, and the builder
correctly declined to change behaviour there: choosing between the readings is an architectural call
and did not belong in a build that came to author a twin overlay.

**The evidence, all measured rather than argued.**

* tuppence `compose()` iterates `for version in sorted(new_array)`, and `main()` fills `new_array`
  from `versions_from_composed_evidence(--head-ref)` — the whole window. driftwood's
  `compose(added, retired, evidence_by_version)` and ludlow's `compose(retired, changed, ...)` fold
  deltas.
* tuppence's composed window has been exactly `['4.0.0']` since 2026-08-29: `6e9aab6` added 4.0.0,
  then `f7b4501` retired 2.0.0, 2.0.1 and 3.0.0.
* platform tag v2.0.1's `computed-semver/evidence/4.0.0.json` records
  `bump: {declared: major, computed: major}` — the publisher's own signed evidence.
* Runs 33884942977 (14:38Z, before ticket 62's pin landed) and 33915621021 (20:19Z, after) carry
  the identical FAIL with identical numbers, so the pin is not the cause. `checkout_tag()`'s own
  docstring says it checks platform out at the pinned tag "never the branch `actions/checkout` left
  it on", so the workflow's `ref:` never reached that decision.
* All three adopters refuse on a composed major (driftwood `adopter-gate.py:720`,
  tuppence `:593`). The refusal is not the divergence. The fold is.

**Add the check that stops it recurring.** Three adopters carrying three hand-written gates that
answer the same question differently is the underlying fault, and nothing graded it. A check that
asserts the three folds agree on a planted case belongs with this ticket, or the next divergence is
found the same way: by one of them going red for a fortnight.

## Comments

**2026-09-05.** An earlier record of mine said the pin revealed the major and that the fix "found
the defect". That was wrong in both halves and is corrected in ticket 62. The pin is a real
improvement and it is not the cause of this red.

## Answer

Built 2026-09-05. Three things, in the order the ticket asks for them.

**1. tuppence's fold is the delta.** `.github/scripts/adopter-gate.py`'s `compose()` now folds
`added = new_window - old_window` and `retired = old_window - new_window`, exactly the shape
driftwood (`compose(added, retired, ...)`) and ludlow (`compose(retired, changed, ...)`) already
had. The summary it writes carries `added` beside `retired`, and the composed line names what the
pull request moves as well as the window at the head. `render-evidence-comment.py` renders a
bump that moves nothing as moving nothing instead of an empty section.

*Not an override (ADR-0011's "No override").* Nothing is exempted and no refusal is weakened for
any named subject: a composed major still refuses (`adopter-gate.py:593` is untouched in that
respect), a retirement is still a forced major, and an added version's evidence is still verified
against tuppence's own identity constant with real cosign and re-read rather than recomputed. The
gate answers the question ADR-0011 asks it. ADR-0011 carries a dated note recording the reading.

**2. The property becomes a standing report.** `verify/unreviewed-major/verify-unreviewed-major-in-window.sh`
(+ `unreviewed_major.py`) names every major standing in an adopter's composed window, on every
truth-surface run, on a day nobody opens a pull request. It records no review and invents none: it
says what is CARRIED, which it observed, and never what was or was not reviewed, which it cannot
see. Its first real run names all THREE adopters carrying policy 4.0.0 -- a fact the estate had
nowhere before, because driftwood and ludlow were green and silent about it.

**3. A check that the three folds agree.** `verify/fold-agreement/verify-fold-agreement.sh`
(+ `fold_agreement.py`) plants four movements of a composed window (standing, arrival, quiet
arrival, retirement) and runs all three adopters' own committed gate scripts over them, each
through the flag shape its own `shift-left.yml` spells -- the flags are read out of that workflow's
`adopter gate` step and only the values are substituted, so an argument the workflow grows that the
grader has no planted value for stops the run rather than being dropped.

### What was measured against what

| | served artefact | operation that reaches it |
|---|---|---|
| the fold | each adopter's committed `.github/scripts/adopter-gate.py` (`adopter_gate.py` in ludlow) | that repository's own `shift-left.yml` `adopter gate` step, its flags read from the workflow |
| the window | each adopter's `composed/evidence.json` at the commit it SERVES (`git show HEAD:`) | the same read its own gate makes with `--head-ref` |
| the bump | platform's `computed-semver/evidence/<v>.json` + bundle AT THE TAG THAT ADOPTER PINS | real `cosign verify-blob`, offline, under the identity constant that repository itself holds |

No proxy is used anywhere: not platform's `main` (the pin's tag is read per adopter), not a
working-tree copy (every read is `git show` of a served commit or tag), not a file's existence (a
bump is reported only from evidence that really verified in this run), and not a record's prose.

### Decisions

1. **The delta fold is the estate's reading; tuppence changes** -- `owner-instructed` in effect,
   since the ticket records it under "The decision" before the build began, and the build executed
   it rather than re-arguing it. The reasons stand in the ticket and are now in ADR-0011.
2. **The standing report is a verify script in the hub gate, not a field in anyone's evidence**
   (`delegated`, ADR-0025). A field would have to be written by something, and the only honest
   writer of "this major is accepted" is the owner; a check that READS is not the same object as a
   record that CLAIMS. A hub check also sees all three adopters at once, which is where the
   comparison lives.
3. **The report grades what is CARRIED, not what is "unreviewed"** (`delegated`). Claiming a review
   is absent would require a place where one would be recorded, and inventing that place is exactly
   what the ticket forbids. So the sentence graded is "no adopter carries a policy version whose
   publisher-signed evidence computes major", which this run can and does observe, and the line says
   who can dispose of it (the owner, ADR-0025). Named limit: if the owner later authorises a
   carried major, this check gains an input; until such a record exists it has none.
4. **The agreement check compares a gate that refused without stating a composed bump, rather than
   excusing it** (`delegated`). Its exit code is what its own required check grades, so it has
   answered; only a gate that could not be invoked at all is unknown. This is what surfaced the
   ludlow finding below.
5. **The agreement check is classed `estate-observation`, not `simulation`** (`delegated`). Its
   material is planted, but its verdict turns entirely on the content of three other parties'
   committed gates and workflows and changes the day one of them changes.
6. **ludlow's cosign defect is reported, not fixed here** (`delegated`). Choosing how ludlow
   verifies a legacy-format bundle offline without falling back to a live TUF fetch is an
   architectural call in ludlow's repository, exactly the kind ticket 64 correctly declined to make
   in tuppence. It gets its own ticket.

### What this found that nobody had

`verify-fold-agreement.sh`'s first run named a second, previously invisible divergence.
**ludlow's gate cannot verify platform's real published evidence with the cosign version it pins.**
Its `verify_evidence()` passes `--trusted-root` with `--new-bundle-format=true`, and cosign v3.1.3
-- the version ludlow's own `shift-left.yml` installs by checksum -- answers
`Error: --trusted-root only supported with --new-bundle-format` and exits 1; platform's committed
bundles are the legacy shape (`base64Signature`/`cert`/`rekorBundle`), not the new Sigstore bundle
that flag declares. Observed directly against the real binary and the real bundle, not read out of
the code.

It is LATENT, not currently firing: `diff_versions()` only classifies a version "changed" when the
composed member set changes, so ludlow's gate reaches `verify_evidence()` for the first time on the
next real policy adoption -- and refuses it. Its own `verify-adopter-gate.sh` never caught this
because it fabricates bundles and stubs cosign; nothing in the estate had run ludlow's gate against
a real signature until this check did.

Pull requests: hub policy-as-versioned-flux/policy-as-versioned-flux#39, tuppence
policy-as-versioned-tuppence/tuppence#19. Neither merged.

### How it is graded

* `verify/fold-agreement/verify-fold-agreement.sh` -- the three folds, on four planted movements.
* `verify/unreviewed-major/verify-unreviewed-major-in-window.sh` -- the standing report.
* `tuppence/.github/scripts/adopter-gate.py --selfcheck` -- the three delta cases, red first.
* `tuppence/scripts/verify-adopter-gate.sh` -- Scenario A (a bump that moves nothing composes none
  and passes), new Scenario A2 (an arrival composes by re-reading the publisher's own real signed
  evidence), Scenario B (a retirement still refuses), Scenario F (an untouched pin reads no
  standing version's evidence at all).
* `tests/test_fold_agreement.py`, `tests/test_unreviewed_major.py` -- the pure seams, red first.

Both new hub checks are RED in the estate as it stands, and both reds are real: three adopters
carry an unauthorised major, and ludlow's gate answers two planted movements differently from the
other two. Neither red is cleared by anything this ticket could honestly write.

## Waits on the owner

1. **Whether platform policy 4.0.0's major is accepted for driftwood, for ludlow and for tuppence.**
   An authorisation, ADR-0025, one per institution. Until it is made (or the version leaves a
   window), `verify-unreviewed-major-in-window.sh` names that institution on every run. This ticket
   deliberately records no review and invents no place to record one; if the owner wants the
   acceptance to be recordable, the shape of that record is the owner's call and this check gains
   an input from it.
2. Nothing else. The hub branch and the tuppence branch are pushed, and `twin/ENACT_MODE` is
   `development`, so no push waits on the owner.

Map line: Ticket 99 (2026-09-05): the adopter gate grades what a pull request MOVES, not the window
it leaves standing -- tuppence's fold now matches driftwood's and ludlow's, ADR-0011 records the
reading, the property it was protecting is a standing truth-surface report
(`verify-unreviewed-major-in-window.sh`, naming all three adopters' carried 4.0.0 major), and
`verify-fold-agreement.sh` runs all three real gates over four planted movements and refuses the
day two of them diverge -- which it did on its first run, finding that ludlow's gate cannot verify a
real bundle with the cosign it pins.
