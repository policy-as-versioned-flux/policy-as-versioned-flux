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
      cage-tier.yaml: major  entries=148
        first entry: expr-pin-031548608dd6f60e
      posture-trust-boundary.yaml: none  entries=0
      require-nonroot.yaml: none  entries=0    <- the re-carried arm WIDENS, so no bump

(148 moved entries, not the "150+" an earlier draft of this Answer rounded to; the number is
`len(movement.entries)` for the cage-tier pair and it was re-counted on 2026-09-04.)

### What this exposed (four real defects, all fixed here)

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
   signed tag, so Flux cannot deliver it and no cluster can carry it. FOUR checks treated that as
   a defect or let it suppress a real signal:
   - `verify-declared-versions-admit.sh` skipped ALL versions because 5.0.0's cage was not
     installed, hiding 4.0.0's genuine green. It now partitions cut/uncut, probes the cut lines
     for real, and names the tail. Selfcheck leg added.
   - `verify-posture-projection.sh` FAILED with "stamp-posture-5-0-0 not installed live". Same
     rule applied; it names the tail instead.
   - `verify-first-gate-determined-release.sh` FAILED because there is no `evidence/5.0.0.json`.
     The gate that writes evidence runs inside `cut-release.yml`, so that state is pre-dispatch,
     not a fault. It is now a could-not-look ONLY when the element records no `commit` AND no tag
     is present; evidence missing on a RELEASED element still FAILS by name, which is the defect
     the beat is for. Selfcheck leg added pinning that decision. (The first cut of this fix keyed
     on the local tag alone; the 2026-09-04 review fixes below moved the key onto `commit`, where
     the other four checks have it, and red-proved the tagless-checkout case.)
   - a FOURTH check had the same fault and was missed on the first pass:
     `graded/verify-graded.sh` step 8 hard-failed on `cage-tier-5-0-0`. Same rule applied on
     2026-09-04; see the review-fixes section below, which also records both branches' runs.

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
    verify-first-gate-determined-release.sh --selfcheck
                                                0  PASS
    graded/verify-graded.sh                     0  PASS, after the fix of 2026-09-04 below. It was
                                                   0 on ecosystem/build-2026-09-03 and this ticket
                                                   turned it to 1 ("FAIL: cage-tier-5-0-0
                                                   MutatingPolicy not installed live"). A real
                                                   regression this ticket caused, and fixed.
    shift-left/verify-shift-left.sh             0  PASS -- and it was 3 on
                                                   ecosystem/build-2026-09-03 ("declares one major
                                                   line (4.0.0), so a target has no +/-1
                                                   neighbour"). The second declared line gives the
                                                   flip beat its first live subject: this change
                                                   moves that check from could-not-look to green.
    verify-governed-namespace-guard.sh          0  PASS
    kyverno test graded/tests/cage-tier         13 passed / 0 failed
    kyverno test distribution/tests/require-nonroot  14 passed / 0 failed

`identity/verify-identity.sh` is red on this machine, and not for this ticket: it prints `ok
OpenBao present` and then `FAIL: OpenBao has no jwt auth method enabled -- run identity/up.sh
(dev-mode OpenBao is in-memory: a pod restart wipes it)`. OpenBao is running; the auth method it
lost on restart is what is missing. Identity is shelved (ticket 90) and nothing here touches it.

`verify-publisher-gate.sh` is **exit 3, could-not-look, on BOTH branches** when run from its real
path, and the reason is the same on both: `SKIP (part C): cs-16's cut-in-the-middle shape needs at
least three declared versions and distribution/versions.yaml declares [...]; there is no middle to
cut`. On `ecosystem/build-2026-09-03` that list is `['4.0.0']`; on this branch it is `['4.0.0',
'5.0.0']` -- still two, still no middle, so the grade does not move. It FAILs only when it is
invoked through the hub worktree's `.estate-clone/platform` symlink, and that is an artefact of the
invocation, not of the repo: the script's `here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` is
the LOGICAL path (`.../wt/ticket-63/.estate-clone/platform`) while `corpus_generator.DISTRIBUTION`
is built from `Path(__file__).resolve()` (`.../platform/.work/ticket-63/distribution`), so its own
`assert DIST == repo / "distribution"` fires: `AssertionError: corpus_generator resolved the wrong
repo`. An earlier draft of this Answer said this check was red on `main` for the same reason "it
cannot run from a nested .work/ worktree". That comparison was not like-for-like -- the two runs
were not the same invocation -- and the claim was wrong on all three counts: it is not a FAIL from
its real path, it is not the same grade being compared, and the cause is the symlink, not the
nesting. Both runs are recorded below.

### 2026-09-04, review fixes

The spec review of this branch found two blocking defects and four smaller ones. All six are fixed
here; the two blocking ones were both about this Answer's honesty, and one of them was a real
regression this ticket had caused and then misattributed.

**BLOCKING 1 -- this ticket broke `graded/verify-graded.sh`, and the Answer blamed a flaky live
leg.** It was not flaky and it was not red on the integration branch. Step 8's live loop
(`graded/verify-graded.sh`, the `cage-tier-$v` / `cage-netpol-$v` existence loop) ranged
`mod.versions(versions.yaml)`, which this ticket had grown to `['4.0.0','5.0.0']`, and hard-failed
on the uncut 5.0.0 whose signed tag does not exist. Three of the four version-ranging checks got
the cut/uncut partition in this ticket; this one was missed. It has it now, keyed the same way, on
the array element's `commit` field:

- the existence loop ranges CUT elements only, and PRINTS the uncut tail by name (`uncut tail, not
  looked for: 5.0.0 (declared with no commit, so no signed tag and nothing for Flux to deliver)`);
- `DECLARED_COUNT` -- the pre-existing guard that skips the behavioural probes when more than one
  version is installed and selectable -- counts CUT elements too. Counting the uncut one would have
  tripped that guard and turned 4.0.0's real behavioural green into a blanket live-tail SKIP, which
  is the same fault in the other direction;
- `NEWEST` is the newest CUT version, because that is the copy the cluster actually carries. The
  probe banner says so: `the live copy under test is cage-tier-4-0-0 (newest CUT version)`.

Named, not closed, and printed by the check itself when an uncut tail exists: the orphan guard's
allow-list is ranged over the WHOLE array while a `cage-tier-<v>` only exists for a version whose
tag was cut. Between declaring a version and cutting its tag, a pod may claim it, pass the orphan
guard, and match no cage. Not reachable today (the live guard is still rendered from the
one-version array, and nothing is pushed). The repair is to range the allow-list over cut elements
in the ResourceSet and `render-orphan-guard.py`, which is a change to the fan-out, not to this beat.

**BLOCKING 2 -- the `verify-publisher-gate.sh` claim was false on all three counts.** Corrected in
the check section above: exit 3 on both branches from its real path, FAIL only through the hub
worktree's `.estate-clone/platform` symlink, and the earlier comparison was not like-for-like.

**Minor 1 -- `verify-first-gate-determined-release.sh` keyed the uncut-tail rule on a LOCAL TAG.**
Alone among the checks this ticket touched: the other four key on the array element's `commit`,
this one asked `git rev-parse --verify refs/tags/<tag>` with no observed/unobserved guard. On a
tagless or shallow checkout (`--depth`, `--no-tags`, an archive export) `refs/tags` is empty, so a
version RELEASED WITH NO GATE EVIDENCE read as "not yet gated" and skipped -- the one direction
this beat must never be wrong in. It is keyed on `commit` now, with the local tag kept as a second
signal so a tag appearing without a commit still refuses. The selfcheck's table grew the third
argument and pins the shallow case by name. Red-proved for real, not only in the selfcheck: a
`git clone --no-tags --depth 1` of this branch with `computed-semver/evidence/4.0.0.json` moved
aside gives `FAIL: policy/v4.0.0 is recorded as released by the array element's commit
64635dfd... (this checkout carries no refs/tags/policy/v4.0.0, so the tag itself was not observed
here) but there is no computed-semver/evidence/4.0.0.json`, exit 1 -- where the pre-fix script,
same clone, same missing evidence, printed `SKIP: waiting for the owner to let cut-release.yml cut
policy/v4.0.0 policy/v5.0.0 in Actions`, exit 3. Step 3 got the same guard: an element with a
commit whose tag this checkout cannot see is now reported as a fact about the CLONE (`SKIP: this
checkout cannot see the signed tag(s)...; fetch tags and re-run`), never as a wait on the owner for
a release that already happened.

**Minor 2 -- `identity/verify-identity.sh` is not "a stopped OpenBao".** Corrected above: OpenBao
is present; the jwt auth method is not enabled.

**Minor 3 -- "150+ further entries" was a rounding of a number that was to hand.** It is 148, and
the corpus block above now carries the re-counted figure.

**Minor 4 -- the check table omitted two lines.** `shift-left/verify-shift-left.sh` moves 3 -> 0 on
this change (a real improvement this ticket had not claimed) and `graded/verify-graded.sh` had no
grade line at all. Both are in the table now, with what they graded on the integration branch.

### The 2026-09-04 runs, from the hub worktree root

`graded/verify-graded.sh` on `ecosystem/build-2026-09-03` (its real checkout,
`.estate-clone/platform/graded/verify-graded.sh`) -- **exit 0**:

    ok   a running isolated pod accepts an UPDATE (kubectl label) — the mutation is idempotent
    ok   a pod claiming an undeclared version is refused live by the orphan guard
    ok   a pod with no claim at all is refused live in a governed Namespace — silence is not an exemption
    ok   all three rungs' reach cages are still present at the end of the run (nothing deleted them)
    PASS: the Namespace declares the tier and the pod wears it; the cage only tightens; the bottom rung runs and reaches nothing; TCoR booked

`graded/verify-graded.sh` on `ticket-63-...`, BEFORE the fix -- **exit 1**:

    that window. Upgrade path: render the three NetworkPolicies per governed
    Namespace from the composed artefact, so Flux has them in place before any pod
    is admitted (tickets 40/42).
    ==> 8. live: a REAL pod in a caged Namespace is admitted, RUNS, and wears its Namespace's cage
    FAIL: cage-tier-5-0-0 MutatingPolicy not installed live

`graded/verify-graded.sh` on `ticket-63-...`, AFTER the fix -- **exit 0**, and the uncut tail is
named at step 8 (`uncut tail, not looked for: 5.0.0`):

    ok   a running isolated pod accepts an UPDATE (kubectl label) — the mutation is idempotent
    ok   a pod claiming an undeclared version is refused live by the orphan guard
    ok   a pod with no claim at all is refused live in a governed Namespace — silence is not an exemption
    ok   all three rungs' reach cages are still present at the end of the run (nothing deleted them)
    PASS: the Namespace declares the tier and the pod wears it; the cage only tightens; the bottom rung runs and reaches nothing; TCoR booked

`verify-first-gate-determined-release.sh --selfcheck` -- **exit 0**:

    ok  selfcheck: evidence+no tag is a could-not-look; NO evidence with a RELEASED element (commit
    on the array, or a tag) is still a refusal, tagless checkout included; the
    gate-determines-the-number claim is not weakened

`verify-first-gate-determined-release.sh` -- **exit 3**:

    has not run for it either -- it runs inside the same dispatch, before the tag.
    A gitsign tag can only be cut by .github/workflows/
    cut-release.yml inside GitHub Actions, with that run's own ambient OIDC identity.
    Nothing here may fake one, so this check cannot look at the last step of the release.
    SKIP: waiting for the owner to let cut-release.yml cut policy/v5.0.0 in Actions

`distribution/verify-coexistence.sh` -- **exit 3**:

    ==> 1b. offline: the matrix's subjects are exactly the DECLARED array (4.0.0 5.0.0)
    ==>    the fixture and the array agree
    ==> 2. offline: the orphan-guard allow-list is exactly the version array (no drift)
    SKIP (live tail): distribution/versions.yaml declares [4.0.0 5.0.0] but only [4.0.0] has been cut (uncut, no signed tag yet: 5.0.0); coexistence needs two RELEASED versions to show side by side, and there is no second one on any cluster to prove against
    SKIP: offline proof holds; live tail could not look: ... — two signed versions coexist; each judges only what claims it

`distribution/verify-declared-versions-admit.sh` -- **exit 0**:

    ok   4.0.0 baseline: ADMITTED and caged — pc=cage-baseline-4-0-0 prio=-10 preempt=Never tier=baseline
    ok   4.0.0 restricted: ADMITTED and caged — pc=cage-restricted-4-0-0 prio=-100 preempt=Never tier=restricted
    ok   4.0.0 quarantine: ADMITTED and caged — pc=cage-quarantine-4-0-0 prio=-1000 preempt=Never tier=quarantine
    ok   4.0.0 isolated: ADMITTED and caged — pc=cage-isolated-4-0-0 prio=-10000 preempt=Never tier=isolated
    PASS: every CUT version distribution/versions.yaml declares admits a real pod on every rung of the ladder on kind-driftwood, and every pod came back wearing that rung's own cage (not looked at, uncut and unreleasable: 5.0.0)

`distribution/verify-governed-namespace-guard.sh` -- **exit 0**:

    ==> 1. render-governed-namespace-guard.py --selfcheck (structural: shape, Deny, CREATE-only, namespaceSelector)
    selfcheck ok: governed-namespace-requires-claim is platform-machinery, Deny, CREATE-only, scoped to governed:true namespaces, denies an unclaimed pod
    ==> 2. the validations expression itself, functionally, namespaceSelector stripped (kyverno CLI cannot evaluate it offline -- see this script's docstring)
    PASS: a governed namespace requires a claim at CREATE; the claim check itself is proved, and the namespace-scoping shape is proved structurally (kyverno CLI cannot evaluate namespaceSelector offline).

`distribution/verify-infra-declaration.sh` -- **exit 0**:

    driftwood/composed/policies/v4.0.0/cage-tier.yaml: 'baseline'
    ludlow/composed/policies/v4.0.0/cage-tier.yaml: 'baseline'
    tuppence/composed/policies/v4.0.0/cage-tier.yaml: 'baseline'
    ok   no served body defaults an unlabelled tier to isolated while infra is undeclared (currently: infra is fully declared, so this is a live tripwire, not a historical fact)
    PASS: the platform's infra declaration covers kube-system, flux-system and kyverno, entitled by the platform role on party.yaml, and no served policy body's unlabelled default can flip them to isolated before that declaration lands.

`distribution/verify-orphan-guard.sh` -- **exit 0**:

    ==> 1. render the orphan-guard from the version array (declares 4.0.0, ...)
    ==> 2. an undeclared version (9.9.9) is denied; a declared one (4.0.0) admits
    PASS: only versions the array declares can run; the allow-list is the array.

`distribution/verify-render-version-tree.sh` -- **exit 0**:

    ok   12 (tree, rung) dial entries match their own PriorityClass value and preemptionPolicy
    PASS: every mandatory member renders with a versioned name, the policy-version label, a
          matchConditions self-scope (never objectSelector); cage-tier names its own
          PriorityClasses and agrees with their value and preemptionPolicy; and two rendered
          versions coexist, each judging only its own claim.

`distribution/verify-retirement.sh` -- **exit 3** (unchanged from the integration branch):

    ==> 2. retire 4.0.0 from the array (one deletion) and re-render
    ==> 3. after retirement: the same pod is now DENIED (orphaned by the shrunk array)
    ==>    (live: dropping the array element prunes Kustomization policy-v4-0-0)
    SKIP (live tail): policy-v4-0-0 ABSENT on kind-driftwood but never observed present by this script; absence is not evidence of pruning
    SKIP: offline proof holds; live tail could not look: ... — retiring a version (one array deletion) prunes it and denies stragglers

`shift-left/verify-shift-left.sh` on `ticket-63-...` -- **exit 0**:

    shift-left: fixtures/workload-flip.yaml would be denied somewhere in its supported window ['4.0.0', '5.0.0']
    (non-zero above is expected -- the flip was caught)

    shift-left: all offline proofs passed

`shift-left/verify-shift-left.sh` on `ecosystem/build-2026-09-03` -- **exit 3**, for contrast:

    == a version the array doesn't declare is refused, not silently skipped ==

    == an Audit->Deny flip is caught pre-merge ==
    SKIP: distribution/versions.yaml declares one major line (4.0.0), so a target has no ±1 neighbour and there is no tightened rule for the window to catch a workload against; the flip beat has nothing to observe until a second major is declared again

`verify-publisher-gate.sh` from its REAL path on `ticket-63-...` -- **exit 3**:

    ok  D3: a degraded publish carries the suffix on the tag, the evidence names the computed
        bump it failed to reach, and the array element carries tier: quarantine -- a signed fact
        the ADOPTER prices (18 Answer 2), never a floor the publisher sets in someone else's repo

    SKIP: part(s) c could not look -- the reason is on their own SKIP line above; every other part of the publisher gate was observed true

(its part C line: `SKIP (part C): cs-16's cut-in-the-middle shape needs at least three declared
versions and distribution/versions.yaml declares ['4.0.0', '5.0.0']; there is no middle to cut`)

`verify-publisher-gate.sh` from its REAL path on `ecosystem/build-2026-09-03` -- **exit 3**, the
same grade, the same part, the only difference being the array it names (`['4.0.0']`):

    ok  D3: a degraded publish carries the suffix on the tag, the evidence names the computed
        bump it failed to reach, and the array element carries tier: quarantine -- a signed fact
        the ADOPTER prices (18 Answer 2), never a floor the publisher sets in someone else's repo

    SKIP: part(s) c could not look -- the reason is on their own SKIP line above; every other part of the publisher gate was observed true

`verify-publisher-gate.sh` THROUGH the `.estate-clone/platform` symlink -- **exit 1**, the
invocation artefact described above (`AssertionError: corpus_generator resolved the wrong repo:
.../platform/.work/ticket-63/distribution`):

    ok  the array element is now {'version': '9.0.0', 'tag': 'policy/v9.0.0-quarantine.1', 'commit': '21ec43c7...', 'bump': 'major', 'tier': 'quarantine'}
    ok  D3: a degraded publish carries the suffix on the tag, the evidence names the computed
        bump it failed to reach, and the array element carries tier: quarantine -- a signed fact
        the ADOPTER prices (18 Answer 2), never a floor the publisher sets in someone else's repo
    FAIL: a part above failed -- its own FAIL/assert line names which

`identity/verify-identity.sh` -- **exit 1**, not this ticket's and not a stopped OpenBao:

    ok   SPIRE pods present
    ok   spire-agent DaemonSet fully Ready (1/1)
    ok   istiod has an available replica
    ok   sidecar-injector webhook has a populated caBundle (serves)
    ok   OpenBao present
    FAIL: OpenBao has no jwt auth method enabled — run identity/up.sh (dev-mode OpenBao is in-memory: a pod restart wipes it)

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

10. **`graded/verify-graded.sh`'s `DECLARED_COUNT` and `NEWEST` count CUT versions, not declared
    ones** (2026-09-04). The sentence that guard defends is "every declared version is INSTALLED
    and SELECTABLE by any pod", and an uncut element is neither: no tag, so Flux delivers nothing
    and there is no `cage-tier-<v>` on the cluster to exercise. Counting it would have made the
    count two, tripped the skip, and thrown away 4.0.0's real behavioural green over a version that
    does not run -- a blanket skip standing in for a real result, which is the fault the cut/uncut
    rule exists to avoid. The guard still trips the day a second version is really cut.
11. **The orphan-guard/uncut-tail window is NAMED in `verify-graded.sh`'s output, not fixed here**
    (2026-09-04). The allow-list ranges the whole array; a cage exists only for a cut version; so a
    pod claiming a declared-but-uncut version passes the guard and matches no cage. It is not
    reachable today and the repair belongs in the ResourceSet and `render-orphan-guard.py` (the
    fan-out), not in a verify script. Naming it in the check's own output is what keeps the beat's
    green honest; silently passing over it would not be.
12. **`verify-first-gate-determined-release.sh` keys "released" on `commit`, and keeps the local
    tag as a second signal rather than replacing it** (2026-09-04). `commit` is committed content
    and survives every fetch depth, so it is the observable that cannot go missing; but a tag that
    appears with no `commit` on its element is also a release with no gate evidence, and dropping
    that leg to "key it the same way as the others" would have narrowed the refusal. Both are
    pinned in the selfcheck. Step 3 got the matching guard so a cut release whose tag this clone
    cannot see is reported as a fact about the clone, never as a wait on the owner.
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
- **The orphan guard still allows an UNCUT declared version** (found 2026-09-04 while fixing
  `graded/verify-graded.sh`, named there in the check's own output and in decision 11). Its
  allow-list ranges the whole array; a `cage-tier-<v>` exists only for a version whose tag was cut.
  So once this branch is pushed and before `cut-release.yml` cuts `policy/v5.0.0`, a pod could
  claim 5.0.0, pass the guard, and match no cage. Not reachable today -- nothing is pushed and the
  live guard is still rendered from the one-version array. The repair is in the ResourceSet
  template and `render-orphan-guard.py` (range the allow-list over CUT elements), which is a change
  to the fan-out and belongs with ticket 64 or its own ticket, not inside a verify script.
- `policy/verify-conditional.sh`'s live fixtures still claim `2.0.1`. Its skip reason IMPROVED
  today (from "the branch lives only in retired 2.0.1" to "5.0.0 carries it, relabel the fixtures
  to 5.0.0 before trusting this tail") and it names its own next step. Relabelling belongs with the
  cut, not before it.
