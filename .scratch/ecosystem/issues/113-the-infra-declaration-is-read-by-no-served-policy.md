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
