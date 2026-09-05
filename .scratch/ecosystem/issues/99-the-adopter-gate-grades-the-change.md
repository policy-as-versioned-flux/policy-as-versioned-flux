# 99 — The adopter gate grades the change, not the window

Type: task (AFK)
Status: open
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
