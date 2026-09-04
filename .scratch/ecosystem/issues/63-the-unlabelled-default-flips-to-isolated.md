# 63 — The unlabelled default flips to isolated

Type: task (AFK)
Status: resolved (platform half built; the cut, the adopter pins and the recompose wait on the owner and ticket 64)
Blocked by: 58 (resolved 2026-08-31; no wait remained as of 2026-09-02)

## Question

ADR-0022's ordering precondition is fully met (infra declared, entitled, asserted green by verify-infra-declaration) and REGRILL answer 28 binds the owner to the strictest-cage default, yet all 9 served cage-tier bodies still default an ungoverned Namespace to baseline. Make the one-line edit across the served copies, let the engine compute the bump (a major — coordinate with ticket 58's second-declared-version decision, since this cut can be the coexistence subject), and keep verify-infra-declaration as the gating check. Blocked by 58 only for the version-declaration interaction; the edit itself is ready.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M12 (unlabelled default still baseline).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

- 2026-08-31 (ticket 58, provisional): the flip cut IS the second declared line (the engine computes a major, so 5.0.0) and it re-carries the root-if-attested conditional branch (Q1a, Q2a). Blocker 58 is resolved; this ticket is ready to run.

**2026-09-02, review.** Header still says Blocked by 58; 58 is resolved provisional, so this ticket is on the frontier. Two things from the review: whether the estate needs a third declared line is ticket 75 Q3, because the thesis's 'at least three' is the transcriber's phrase and the Medium post could not be read; and the offline coexistence proof already passes over the retired trees, so what this cut restores is the live tail, the retirement subject, the ±1 window and the conditional arm. Ticket 84 carries the supersede pricing that makes an older line cost something. Record: REVIEW-2026-09-02.md R6.

**2026-09-02, ticket 75 resolved.** Q3 is (a): at least three coexisting versions binds, in the owner's own 2022 words (forward and back by one version). This cut is the second declared line. Ticket 84 supplies the third and sets the coexistence threshold to three. No wait remains on this ticket.

## Answer

**2026-09-04. The flip shipped in the platform's source and as the second declared line, 5.0.0.
The signed cut, the adopter pins and the recompose are the owner's and ticket 64's.**

Map line: the unlabelled default is `isolated` in graded and in the new 5.0.0 line; the gating
check that held it back grades it honestly again after two real blind spots were closed.

### What was built

**The flip itself** (`graded/policies/cage-tier.yaml`). The `tier` variable's else-branch went from
`nsGoverned ? 'isolated' : 'baseline'` to the single literal `'isolated'`. A Namespace nobody
governs no longer buys a nudge by saying nothing. `nsGoverned` went with it: the ternary was its
only reader, and the engine's own `tier_expressions()` walks the `tier` variable's transitive
reads, so an unreferenced variable is invisible to the engine anyway. The header prose that
promised the flip now records it, and says the gating check stays a tripwire rather than retiring.

**Test first, red then green.** `graded/tests/cage-tier`'s `ungoverned-ns` expectation was moved to
the isolated dials (100m/64Mi, `cage-isolated`, priority -10000, drop ALL, read-only fs, the WAF
sidecar) BEFORE the policy edit: `kyverno test tests/cage-tier` went 13/0 -> 12 passed 1 failed
("Resource diff") -> 13/0 after the flip. The fixture prose in `resources.yaml` and
`kyverno-test.yaml` records the change and the date.

**The 5.0.0 tree** (`distribution/policies/v5.0.0/`). Rendered from the graded source by the real
`render-version-tree.py` (eight mandatory members, versioned names, self-scope, PriorityClass
rewrite), plus a hand-authored `kustomization.yaml` and `require-nonroot.yaml` carrying the
re-carried root-if-attested arm.

**The array** (`distribution/versions.yaml`). `{ version: "5.0.0", tag: "policy/v5.0.0", bump:
"major" }` -- no `commit`, deliberately: `cut-release.yml` fills that when it cuts the signed tag,
and an agent never fakes one. The element carries the full reason in prose beside 4.0.0's.

**The engine computes the major on its own.** `cage_engine.classify_repo` over the real v4.0.0 and
v5.0.0 trees with a 178-entry generated corpus built by the real `corpus_generator.build_manifest`:

    generated corpus pods: 178
    COMPUTED BUMP: major
      cage-tier.yaml: major
        expr-pin-031548608dd6f60e (tier baseline->isolated): cpu, mem, priorityClass, dropAll,
        readOnlyRootFs, waf narrowed; [...150+ further entries...]
      posture-trust-boundary.yaml: none
      require-nonroot.yaml: none    <- the re-carried arm WIDENS, so it contributes no bump

### What this exposed (three real defects, all fixed here)

1. **`verify-infra-declaration.sh` read PROSE as a declaration.** Its `unlabelled_default()`
   matched the raw file, so the flip's own changelog comment -- which quotes the shape it
   replaced -- made an already-flipped body report as still `baseline`. The tripwire was wrong in
   the one direction it must never be wrong in. Comments are stripped now, exactly as
   `parse_namespace_docs` was repaired on 2026-08-28, one function down.
2. **The same check went blind to the collapsed shape.** With no ternary left, the flipped body
   read as an unknown shape (`None`), and `None` is not an offender. A third served shape is read
   now, with selfcheck legs for both the authoring block scalar and the rendered one-line `\n`
   form, plus a leg proving a body whose only match is a comment declares nothing.
3. **An UNCUT TAIL turned green beats red or blank.** A declared element with no `commit` has no
   signed tag, so Flux cannot deliver it and no cluster can carry it. Three checks treated that as
   a defect or let it suppress a real signal:
   - `verify-declared-versions-admit.sh` skipped ALL versions because 5.0.0's cage was not
     installed, hiding 4.0.0's genuine green. It now partitions cut/uncut, probes the cut lines
     for real, and names the tail. Selfcheck leg added.
   - `verify-posture-projection.sh` FAILED with "stamp-posture-5-0-0 not installed live". Same
     rule applied; it names the tail instead.
   - `verify-first-gate-determined-release.sh` FAILED because there is no `evidence/5.0.0.json`.
     The gate that writes evidence runs inside `cut-release.yml`, so that state is pre-dispatch,
     not a fault. It is now a could-not-look ONLY when the tag is also absent; evidence missing
     with a tag that EXISTS still FAILS by name, which is the defect the beat is for. Selfcheck
     leg added pinning that three-way decision.

**`verify-coexistence.sh` was passing about nothing.** Its offline matrix loaded
`policies/v2.0.0` and `v3.0.0` -- both RETIRED on 2026-08-29, frozen behind their tags, delivered
to nobody. "Two versions coexist" was true of two things that do not run. The fixture now loads the
two DECLARED lines, and a new step 1b asserts the fixture's `policies:` list is exactly the
declared array, so it cannot drift back. Red-proved: adding a third path made it FAIL by name. The
live tail applies the cut/uncut rule and could-not-looks for 5.0.0. Threshold stays two; ticket 84
raises it to three.

**`computed-semver/pairing.py`'s dial fixture worked by coincidence.** Its claimant pod had no
sibling Namespace, so `namespaceObject` was null and the tier fell to the unlabelled default --
which happened to be `baseline`, the rung the fixture tightens. The flip moved it to `isolated`,
both bodies agreed, and the assert read `none`. A real red, and the right one. The pod now has a
Namespace that DECLARES `baseline`, so the fixture says which rung it is about.

**`generated-corpus/` regenerated.** `corpus_generator.py` defaults to `supported[0]` ->
`supported[-1]`, which is now 4.0.0 -> 5.0.0, so the committed spine had to be rebuilt (196 files,
178 entries, checksum `sha256:a1ef0194...`). `verify-corpus-generator.sh`'s regenerate-and-diff,
`verify-witness-set.sh` and `verify-generator-standing-check.sh` are green on it.

### Checks, run from the hub worktree root

    verify-infra-declaration.sh                 0  PASS (10 served bodies; graded and v5.0.0 read
                                                   'isolated', the tripwire still armed)
    verify-declared-versions-admit.sh           0  PASS (4.0.0 admits on all four rungs; 5.0.0
                                                   named as the uncut tail, not looked at)
    verify-orphan-guard.sh                      0  PASS
    verify-render-version-tree.sh               0  PASS
    verify-coexistence.sh                       3  offline PASS over the two declared lines; live
                                                   tail could-not-look (5.0.0 uncut)
    verify-retirement.sh                        3  live tail could-not-look (unchanged from main)
    verify-gate / -rederive-bumps / -cage-engine 0  PASS
    verify-pairing / -coverage / -corpus-generator / -witness-set / -generator-standing-check
                                                0  PASS
    verify-posture-projection.sh                0  PASS
    verify-composition.sh                       3  the adopter pin does not carry v5.0.0 yet
                                                   (ticket 64); was 0 on main
    verify-first-gate-determined-release.sh     3  waiting for cut-release.yml to cut policy/v5.0.0
    kyverno test graded/tests/cage-tier         13 passed / 0 failed
    kyverno test distribution/tests/require-nonroot  14 passed / 0 failed

Two platform checks are RED on this machine and were red identically on `main` before this branch,
with the same last line: `graded/verify-graded.sh` (a live-cluster leg, flaky between the netpol
generate and the reach probe) and `verify-publisher-gate.sh` (`corpus_generator resolved the wrong
repo` -- it cannot run from a nested `.work/` worktree). `identity/verify-identity.sh` is red for a
stopped OpenBao. None of the three is this ticket's.

### Decisions (all `delegated`, ADR-0025)

1. **The ternary collapsed to a single literal, and `nsGoverned` was deleted** rather than left as
   `nsGoverned ? 'isolated' : 'isolated'` -- which is the shape `verify-infra-declaration.sh`'s own
   selfcheck already modelled, so it was the cheaper option. Reason: a released policy body is
   signed and frozen, and leaving deliberately dead CEL in one to satisfy a regex is the tail
   wagging the dog. The regex was taught the real shape instead, with selfcheck legs -- which is
   what the ticket's own test_seams anticipated ("add a served-shape assert if the regex changes").
2. **root-if-attested is folded INTO `require-nonroot@5.0.0`, not shipped as a separate
   `may-run-root-if-attested` policy.** Two reasons. Kyverno ANDs policies: two ValidatingPolicies
   that both match a pod must both pass, so a separate "may run root if attested" policy could not
   widen this one -- inert at best, a second refusal at worst. And ticket 22's pairing rule keys on
   (identity, name-with-version-stripped): a new member name would read as a brand-new unpaired
   policy AND make `require-nonroot@4.0.0` read as silently removed. This is exactly why the
   retired 2.0.1 folded it too, and its own header says so.
3. **The attestation predicate is 2.0.1's, unchanged**: a non-empty
   `policy-as-versioned.dev/root-attestation` label, plus every container dropping ALL caps and
   mounting a read-only root fs. It is a REFERENCE to a sign-off, never the sign-off. Verifying it
   needs a signature the cluster can check, which is ADR-0021's territory, not this cut's. The
   fixture carries both the attested pod (admitted) and a byte-identically-hardened UNattested one
   (still failed), so the arm is proved widening for the CONDITION and not otherwise.
4. **The retired v2.0.0 / v2.0.1 / v3.0.0 trees stay unedited** and still report `baseline` in
   `verify-infra-declaration.sh`'s scan. `versions.yaml` says a released tree stays on disk behind
   its signed tag unedited; their defaults are a fact about what those tags contain, not a live
   default, because no array element declares them and the orphan guard refuses pods claiming them.
5. **`vselfcheck/cage-tier.yaml` does NOT track the flip.** It is not a declared version -- no
   array element, no tag, and the orphan guard would refuse a pod claiming it -- so it serves
   nothing and flipping it would change no admission decision. It is now also the live example of
   the ternary shape the check must keep reading: once ticket 64 moves the adopters to 5.0.0, only
   4.0.0 and this fixture still carry it, and a regex with no live subject rots. A dated note in
   the file says so.
6. **4.0.0 stays declared beside 5.0.0.** That is the point: it is the coexistence subject, and
   ticket 75 Q3 binds the estate to at least three. Ticket 84 supplies the third.
7. **`verify-coexistence.sh`'s fixture/array comparison is order-insensitive** (both sides sorted).
   Which version a fixture lists first is not a fact about the estate, and failing over it would be
   a red with nothing behind it.
8. **`verify-composition.sh`'s stale hardcoded tag was fixed, not its grade.** It named
   `policy/v4.0.0` as the thing it waits for; 4.0.0 was cut and the pin moved, so that sentence had
   gone stale while still reading as current. It names the waited-on version generically now. Its
   move from PASS to could-not-look is the honest grade: the adopter's pin genuinely does not carry
   v5.0.0 yet, which is ticket 64.
9. **No ungoverned live workload was found that this breaks.** The three infra namespaces are
   declared infra and hold no version-claiming pods; `verify-declared-versions-admit.sh` creates
   its probe namespaces governed and tiered; `graded/verify-graded.sh`'s live namespaces are
   governed. The flip reaches an adopter only when that adopter pins 5.0.0 (ticket 64), so no
   running adopter workload moves today.

## Waits on the owner

- **Push of the platform branch** `ticket-63-the-unlabelled-default-flips-to-isolated` to
  `policy-as-versioned-platform`. The guard refuses every enactment-repo push; the commit is local.
- **Dispatch of `cut-release.yml` with tag `policy/v5.0.0`.** The signed tag, the evidence
  document (`computed-semver/evidence/5.0.0.json`) and the `commit:` field on the array element are
  produced only there, by that run's own ambient OIDC identity. Nothing local may fake a signature.
  Until it happens, `verify-coexistence.sh`, `verify-first-gate-determined-release.sh` and
  `verify-composition.sh` correctly read could-not-look, and they flip to green with no further
  edit. Watch one thing on that run: `release_integrity.empty_commit_refusal` refuses any array
  element with an empty/absent `commit`, and `cut-release.yml` fills 5.0.0's in before the gate --
  if the ordering is ever changed, 5.0.0's element is what would trip it.
- **Pushes of the three adopter branches and their cut-release dispatches** -- ticket 64's work,
  not started here (see below).
- Confirming the flip is wanted now is a RECORD, not a fresh authorisation: REGRILL answer 28
  already binds the owner to the strictest-cage default, and ticket 75 Q3 (2026-09-02) settled the
  version question.

## Not done, deliberately

- **The adopter pin bumps and the recompose are deferred to the final pass** (ticket 64): no
  `adopter-gate.py` run, no `composition.py` re-render, no `composed/policies/v5.0.0` tree in
  driftwood, tuppence or ludlow, and no `composed/` tree regenerated anywhere. The three adopters
  stay pinned to 4.0.0 and their served cage-tier bodies still read `baseline`, which
  `verify-infra-declaration.sh` prints truthfully.
- `policy/verify-conditional.sh`'s live fixtures still claim `2.0.1`. Its skip reason IMPROVED
  today (from "the branch lives only in retired 2.0.1" to "5.0.0 carries it, relabel the fixtures
  to 5.0.0 before trusting this tail") and it names its own next step. Relabelling belongs with the
  cut, not before it.
