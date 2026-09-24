# 113 — The `infra` declaration is read by no served policy

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-21 from [the Laya and loophole map](../../laya-loophole/map.md), ticket 08.
It is the first survivor of ticket 07's loophole round. Reproduced by
`tests/test_cage_ladder_holes.py`, measured under kyverno 1.18.2, the version `release.yml` pins.

ADR-0022 gives a `platform`-role party the right to declare a Namespace at `infra`, and
`platform/engine/namespaces.yaml` declares kube-system, flux-system and kyverno that way. Three
measured facts follow, and none of them is what the ADR describes.

1. **No served `cage-tier` body contains the word `infra`**, with comments stripped. Not the
   hub's v4.0.0 or v5.0.0, not `graded/`, not any adopter's composed copy. The rung is absent
   from `variables.tier`'s membership test, so an `infra` Namespace falls to that test's else
   branch.
2. **A pod that CLAIMS a policy version in one of those three Namespaces lands on `baseline`**,
   the loosest rung, under the body all three adopters serve today. The three Namespaces carry
   no `policy-as-versioned.dev/governed` label by design, and v4.0.0's else branch is
   `nsGoverned ? 'isolated' : 'baseline'`. So the substrate rung delivers the loosest cage:
   500m/256Mi, priority -10, no hardening, no WAF sidecar. Under v5.0.0 the same pod gets
   `isolated`. Neither is an `infra` cage, because no such cage exists.
3. **Pulling the declaration changes nothing for CoreDNS.** CoreDNS claims no policy version, so
   `cage-tier`'s own matchConditions skip it with the label and without it, under both bodies.
   `distribution/verify-infra-declaration.sh` calls its proof 3 a live tripwire, for "exactly
   what stops CoreDNS landing in isolated the moment the fail-closed default ships". That
   configuration is not one any served body produces. The tripwire guards a hazard that does not
   exist, and the real exposure it should guard is fact 2.

What this ticket owes:

1. Decide what `infra` means in a served body. Either it becomes a real rung with real dials, or
   the declaration is retired and the three Namespaces are protected by the mechanism that
   actually protects them, which is `cage-tier`'s claim matchCondition.
2. Re-aim `verify-infra-declaration.sh` at a property that is true. Its proof 1 and proof 2 read
   correctly; proof 3 does not.
3. Close fact 2. Anyone with deploy access to kube-system, flux-system or kyverno runs a claiming
   workload at the loosest rung and an unclaimed workload at no rung at all.
4. Decide whether `tier_binding.py` should tell an unentitled `infra` declaration from an
   entitled one. It grades both `bound`, because `rank("infra")` is the maximum, so any party can
   make its binding check pass unconditionally by writing `infra`. The cage still renders
   `isolated`, so no workload is under-caged today, and that is why this is item 4 and not item 1.

## Done

The three facts are false, or each is recorded as a decision with its reason. The reproduction
in `tests/test_cage_ladder_holes.py` becomes the repair's regression test rather than a standing
red. The `adopter-runs-uncaged-in-the-platform-substrate` row in `twin/ecosystem-misuse-catalogue.yaml` stops
waiting on this ticket and names the built mechanism by path.

## Build, 2026-09-22

Platform PR: https://github.com/policy-as-versioned-platform/platform/pull/28. Hub PR: https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/pull/85, branch
`ticket-113-infra-is-a-role-not-a-rung`. Merge the platform PR first.

### Decisions

1. **`infra` is a role declaration, not a rung. It stays out of every served body.**
   Delegated. An `infra` dial row would repeat `isolated` or be looser than it. A looser row is an
   exemption bought by choosing a Namespace. The declaration stays: it names the substrate, the
   `platform` role entitles it, and the truth surface reads it to know which Namespaces to guard.
   Retiring it would move no rendered cage and would touch the proposer, the binding check and
   the gate. Fact 1 is now this decision. `test_infra_stays_out_of_every_cage_tier_body_by_decision`
   holds it, and tripwire proof 4 fails by name on any body that starts reading the word.
2. **Proof 3 guards the hazard that exists.** Delegated. What keeps CoreDNS out of the cage is
   (a) the `claims-a-policy-version` matchCondition in every served body and (b) no substrate
   Namespace being governed, so `governed-namespace-requires-claim` skips them too. Proof 3 now
   checks both. The hub plants each break and the tripwire fires. The engine confirms the hazard
   is real: with the claim gate swapped for `true`, graded puts an unclaimed substrate pod on
   `isolated`. Fact 3 is closed as a finding and kept as a regression leg.
3. **Fact 2 is named by the gate, and closes by retirement.** Delegated. New proof 4 requires
   every delivered body (each line `versions.yaml` declares, graded, each adopter's composed
   copy) to cage a claiming substrate pod at `isolated`. It FAILS today on four bodies, all
   4.0.0. A signed version body cannot be edited, and a second mutating policy over the same pods
   is the incoherence ADR-0022 already measured. So it closes when the adopters recompose onto
   5.0.0 and 4.0.0 leaves `versions.yaml`. The gate grade for this script moves from PASS to FAIL
   on purpose: the old PASS was a tripwire passing over a live exposure.
4. **`tier_binding.py` grades `infra` as the `isolated` it renders.** Delegated. Admission cannot
   read a party's roles, so an entitled and an unentitled `infra` on a governed Namespace render
   the same rung. The engine shows `isolated` under every delivered body, both ways. Writing
   `infra` buys a party nothing that writing `isolated` does not, so no role lookup is added. The
   verdict still reads `bound`, and `effective` now says `isolated` instead of a rung no cage has.
5. **Rejected: govern the substrate Namespaces and exempt `infra` from the unclaimed-pod cage.**
   That would make 4.0.0 render `isolated` for claiming pods. But it is an exemption keyed on a
   label, which the doctrine bans, and it counts the platform as a governed party.

### What was measured, and how

- `kyverno version` of the CLI used: 1.18.2 (copied into this task's scratchpad; PATH kyverno is
  1.19.1 and the engine legs skip on it by name).
- `bash distribution/verify-infra-declaration.sh` over the estate, platform at this branch.
  Proof 4 printed `baseline` for platform v4.0.0 and the driftwood, ludlow and tuppence v4.0.0
  composed copies, and `isolated` for v5.0.0 and graded. Exit 1.
- The same script on platform origin/main before the change: exit 0, PASS.
- `git ls-tree origin/main composed/policies/` in each adopter: only `v4.0.0`, in all three.
- `distribution/versions.yaml` on platform origin/main declares 4.0.0 and 5.0.0.

### Tests

- `tests/test_cage_ladder_holes.py -n0 -q`, kyverno 1.18.2, platform at origin/main (red):
  5 failed, 11 passed.
- Same, platform at the branch (green): 16 passed.
- Same, kyverno 1.19.1: 10 passed, 6 skipped by name.
- `tests/test_misuse.py -n0 -q`: 41 passed.
- `verify/misuse/verify-misuse.sh`: PASS. The row now resolves 7 anchors and waits on nothing.
- `verify/tier-binding/verify-tier-binding.sh`: PASS, unchanged verdicts for all three adopters.
- `verify/adr-supersession/verify-adr-supersession.sh` and `verify/cited-truth/verify-cited-truth.sh`: PASS.
- mypy over `twin tests conftest.py`: no issues in 194 source files.
- Platform: tripwire `--selfcheck` ok; `tier_binding.py selfcheck` ok (case 12 red first);
  `shift-left/verify-shift-left.sh` passed; `kyverno test graded/tests/cage-tier` 13 passed.

### Waits on the owner

1. **Signed composed tags for driftwood, ludlow and tuppence on 5.0.0.** Each adopter recomposes
   onto platform policy 5.0.0 and cuts a signed composed tag. Until then all three serve 4.0.0
   and a claiming pod in their substrate lands on `baseline`.
2. **Retiring 4.0.0 from `distribution/versions.yaml`**, after step 1. Proof 4 then passes.

The gate reads FAIL for `verify-infra-declaration.sh` until both are done. That is the intended
verdict, not a regression.

### Review round, 2026-09-22

1. **Blocking: proof 3a matched the claim gate by prefix.** A gate loosened to
   `... .orValue('') != '' || true` passed proof 3, and the engine caged an unclaimed pod at
   `isolated` under it. Fix: `claim_gate_expressions` in `distribution/verify-infra-declaration.sh`
   now reads the whole expression scalar. It stops at the first non-blank line indented no deeper
   than the `expression:` key. `carries_claim_gate` then requires every
   `claims-a-policy-version` expression to EQUAL the gate, ignoring whitespace. Delegated: equality,
   not a CEL parser. Any added clause is a change to the gate and fails by name. The served bodies
   carry the gate exactly, so equality costs nothing today.
   - Red first. Four new selfcheck cases (`|| true` inline and on a continuation line, block and
     one-line forms) failed the selfcheck with an AssertionError. A fifth case checks that the next
     key after the gate is not read as part of it.
   - Hub: `LOOSENINGS` in `tests/test_cage_ladder_holes.py` plants three shapes (`true`,
     `<gate> || true`, `<gate>` then `|| true` on the next line). They go into the graded block
     scalar and into the rendered v5.0.0 one-line body. With kyverno 1.18.2 and the old platform
     script: 4 failed, 19 passed. The 4 were the two `|| true` shapes in both bodies. With the
     fix: 23 passed. `test_the_hazard_proof_3_guards_is_real` passes for all three shapes, so the
     engine does cage an unclaimed substrate pod at `isolated` under each one.
2. **Minor: the Tier glossary entry named `infra` as a rung.** Fixed in CONTEXT.md. The entry now
   lists four rungs and points at **Infra tier**. `grep -n 'isolated or infra' CONTEXT.md` returns
   nothing.
3. **Minor: a declared line with no body was silently dropped.** `served_cage_tier_files` now
   returns `(found, missing)`, and the script FAILS naming each missing version. It was red first:
   a new selfcheck case failed with a ValueError before the return shape changed.
4. **Minor: the body count depends on where the script runs.** It derives the estate from its
   own parent directory. Run as `.estate-clone/platform/distribution/verify-infra-declaration.sh`
   (the gate's path, measured here through the hub worktree's `.estate-clone` symlinks), it reads
   6 served bodies. It names 4 at `baseline` and exits 1. Run in place in
   `.estate-clone/platform/.work/ticket-113`, it reads 3 bodies and names only platform v4.0.0,
   because the adopters are not beside it. The "4 bodies" in this record is the first path.

After the fix, proof 3 still prints ok over all 6 real bodies. Checks rerun:
`tests/test_misuse.py` 41 passed, `verify-misuse.sh` PASS, `verify-adr-supersession.sh` PASS,
`verify-cited-truth.sh` PASS, mypy clean over 194 files. Platform: `--selfcheck` ok,
`tier_binding.py selfcheck` ok, `verify-shift-left.sh` passed under kyverno 1.18.2, and
`kyverno test graded/tests/cage-tier` 13 passed, 0 failed. Under the PATH kyverno 1.19.1,
`verify-shift-left.sh` fails to compile the v4.0.0 and v5.0.0 bodies. That is the known pin,
not this change.

### Review round 2, 2026-09-22

1. **Blocking: proof 3a was blind to placement.** It accepted the gate's text anywhere in the
   file. Two planted bodies showed it. One is the real graded body plus `---` and a copy named
   `cage-tier-shadow` whose one matchCondition is `'true'`. The other swaps the real
   matchCondition for `'true'` and parks the gate entry in a `metadata.annotations` string. Under
   kyverno 1.18.2 the engine cages an unclaimed substrate pod at `isolated` under both, and the
   tripwire at 6bd55c6 printed PASS for both. Fix: a new `claim_gate_problem` in
   `distribution/verify-infra-declaration.sh` reads the body's structure with regexes. The file
   must hold exactly one YAML document, of top-level `kind: MutatingPolicy`, with one top-level
   `spec:`. That spec must carry exactly one `matchConditions:` key, as a block list. The gate is
   read only from an item of that list, at the list's item indent. Each failure names its reason
   in the FAIL line.
   - Delegated: stay regex-only, no PyYAML. The script runs on the estate's plain python3.
     A shape the regexes cannot read fails. It is never taken on trust.
   - Delegated: extra matchConditions stay allowed. The engine ANDs them, so they only narrow.
   - Delegated: a duplicated `matchConditions:` key fails. The pinned CLI loads no policy from
     such a file (`Applying 0 policy rule(s)`), so what a cluster would do is not observed. The
     tripwire does not vouch for a gate it cannot read as one list.
   - Red first. The new selfcheck cases (second document, `--- ` with a trailing space,
     annotation text, duplicate key, gate nested under another key, flow-form list, a gate-shaped
     line nested inside another item, a non-MutatingPolicy kind) ran against the old functions and
     failed with `AssertionError: a second policy document without the gate matches every pod`.
     With the fix the selfcheck prints ok.
   - Hub: `MISPLACEMENTS` in `tests/test_cage_ladder_holes.py` plants both shapes in the graded
     body. Against the old platform script, with kyverno 1.18.2: 4 failed, 25 passed (the two
     misplacement tripwire legs, the duplicate-key leg, and the unclaimed-pod leg; see item 2).
     With the fix: 29 passed. `test_the_hazard_a_misplaced_gate_hides_is_real` shows the engine
     cages an unclaimed pod at `isolated` under both shapes.
2. **Minor: `_render` trusted the skip line.** It returned "skipped" whenever any policy in the
   file printed `skipped mutate policy`, even when another policy caged the pod. The fix compares
   what came back with the pod that was sent. A changed pod is a mutation. The "changed" part
   matters: kyverno 1.18.2 prints `applied to` with the pod unchanged, and then a skip line, for
   an unclaimed pod under the v4.0.0 body (measured by `kyverno apply` on the v4.0.0 body).
   Reading `applied to` as a mutation made
   `test_an_unclaimed_substrate_pod_is_outside_every_delivered_body` fail on v4.0.0, which is how
   that was found. Red first: the old `_render` fails
   `test_the_hazard_a_misplaced_gate_hides_is_real[second-policy-document]`. The new pure test
   `test_a_mutation_outranks_a_skip_line_in_the_engine_output` pins both output shapes.

After the fix, through the gate's path, the script reads 6 served bodies. Proof 3 prints ok.
Proof 4 still names the same 4 v4.0.0 bodies at `baseline` and exits 1. Checks rerun:
`tests/test_cage_ladder_holes.py` and `tests/test_misuse.py` 70 passed, mypy clean over 194
files. The reviewer's probe script now prints FAIL for all three plants and PASS for the control.

### Fix round, 2026-09-24: the release gate holds with one served line

Platform PR 44 (https://github.com/policy-as-versioned-platform/platform/pull/44, branch
`retire-policy-4-0-0`) retires 4.0.0 from `distribution/versions.yaml`. Owner-instructed
2026-09-24, knowing it leaves one live line against ticket 75 Q3. The three adopter claim-move
PRs are merged (driftwood 44, tuppence 42, ludlow 39; `gh pr view` gives MERGED for each).

**The problem.** `.github/workflows/release.yml` runs `./shift-left/verify-shift-left.sh` as a
plain step. On the branch at 4f45ae3 that script exited 3, because its flip beat found one major
line and no neighbour. Every release cut from that tree would fail.

**A second problem found on the way.** On main the flip fixture claimed 4.0.0 and failed at 4.0.0,
its own target. `ci-check.py` printed `FAIL @ v4.0.0` with no flip mark, and the old beat still
said "all offline proofs passed". It passed on a plain failure, not a caught flip. And on the
branch at 4f45ae3, `wargamer/propose-policy-pr.sh` printed "unexpected: the gate passed a
workload that should trip the flip" when run with the adopters beside it, because the fixture
now claimed 5.0.0 and passes a one-line window.

#### Decisions

1. **The flip beat runs against a planted two-line window while the served array has one major.**
   Delegated. New `shift-left/flip_window.py` returns `distribution/versions.yaml` when it
   declares two or more majors. Otherwise it prints `NOTHING-TO-FLIP` on stderr, naming the
   served versions, and returns `shift-left/fixtures/flip-window.yaml`. That file declares
   {4.0.0, 5.0.0} and nothing reconciles it. Both bodies are on disk and unedited:
   `git diff policy/v4.0.0 HEAD -- distribution/policies/v4.0.0` is empty, and the same holds
   for v5.0.0. So the beat still proves what it proves: the ±1 window catches, with the real
   kyverno CLI and the real signed bodies, a workload that passes its target and fails a
   neighbour. Reason: a could-not-look is honest for the served array, but the mechanism under
   test does not need the served array to have two lines. `release.yml` needs no change.
   Rejected: teach `release.yml` to accept exit 3 by name. That would ship releases whose gate
   observed nothing.
2. **The beat now requires a real flip.** Delegated. After the non-zero exit it reads the target
   off `ci-check.py`'s output. It fails if the target itself failed, and it fails if no line
   carries the `(Audit->Deny flip` mark. Reason: the main-shaped fixture passed on a plain
   failure, which is the "pass on a technicality" the script's own header warns about.
3. **One place picks the window.** Delegated. `verify-shift-left.sh` and
   `wargamer/propose-policy-pr.sh` both call `flip_window.py`, so they cannot pick different
   windows.
4. **`distribution/verify/gate.yaml` points at `policy/v5.0.0`.** Delegated. The worked example
   named the retired tag and path. `verify-source-verification.sh` reads only its two identity
   annotations, which did not change.

#### What was measured, and how

All with kyverno 1.18.2 (`kyverno version` printed 1.18.2).

- The exact `release.yml` gate step, `./shift-left/verify-shift-left.sh`, run with
  `bash -eo pipefail` in a clean `git archive` of each commit: exit 3 at 4f45ae3 (red), exit 0
  at 92eadf5 (green). The green run prints `NOTHING-TO-FLIP`, then
  `FAIL @ v4.0.0 (Audit->Deny flip: ...)` for the 5.0.0-claiming fixture, then
  "all offline proofs passed".
- Controls, each on a scratch copy of `shift-left/` and `distribution/` at the fix:
  - unchanged: exit 0, window read from the planted file.
  - fixture claims 4.0.0 (main's shape): exit 1, "fails its own target 4.0.0".
  - planted window holds 5.0.0 only: exit 1, "ci-check.py passed a workload ...".
  - planted neighbour renamed to a version with no body: exit 1, "at no neighbour of 5.0.0".
  - fixture made compliant at 4.0.0: exit 1, "ci-check.py passed a workload ...".
  - served array replaced by main's two-major array: exit 0, window read from
    `distribution/versions.yaml`. The same with the planted file corrupted: exit 0, so the planted
    file is not read when the served array has two majors.
- `wargamer/propose-policy-pr.sh`, run from a scratch estate of symlinks (platform at the branch,
  the other seven units at their local clones): at 4f45ae3 it printed "unexpected: the gate
  passed a workload that should trip the flip"; at the fix it printed `NOTHING-TO-FLIP` and
  "ok  gate runs (kyverno)".
- All 47 `verify*.sh` in platform, each run with `bash <script>` from that symlink estate,
  `PAVC_ESTATE_CLONE` at the shared estate and a 900 s timeout. Once with platform at origin/main
  (bfd5361), once at the branch (92eadf5). **Every exit code is the same on both sides.** The
  scripts at 0 on both: 29. At 3 on both: 13. At 1 on both: 5 (`distribution/verify-infra-declaration.sh`,
  `feeds/verify.sh`, `oscal/verify-claims.sh`, `oscal/verify-upflow.sh`,
  `verify-publisher-gate.sh`). `shift-left/verify-shift-left.sh` and
  `wargamer/verify-wargamer.sh` are 0 on both.
- `verify-infra-declaration.sh` stays at 1 on the branch. It names 3 bodies at `baseline` on
  the branch (the three adopters' `composed/policies/v4.0.0/cage-tier.yaml`) against 4 on main
  (those plus platform's own v4.0.0). After `git fetch`, each adopter's origin/main still carries
  `composed/policies/v4.0.0/`, so fact 2 stays open in the served adopter trees until each
  recomposes and drops that directory.

#### Waits on the owner, or on a later step

1. **Merge PR 44 and cut the tools tag.** The integrator merges; a signed tag is the owner's.
2. **Each adopter recomposes onto this platform tree, removes `composed/policies/v4.0.0/`, and
   cuts a signed composed tag.** The composer does not prune (measured in PR 44's body). Proof 4
   passes only after that.
3. **The adopter pin bump past this retirement is a forced major** that each adopter's own gate
   refuses (PR 44's body, "A retirement is a major for adopters"). That needs an owner decision
   before the pin bump.
