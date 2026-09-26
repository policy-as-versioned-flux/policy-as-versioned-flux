# 161 — Fact 7 is registered again with a reference workload

Type: task (AFK)
Status: open
Blocked by: none

## Question

Build what ticket 152 decided, in driftwood, tuppence and ludlow, and in the hub. Each decision below is delegated (ADR-0025, 2026-09-25) and its reason is in ticket 152.

1. **The grade change first.** In each adopter's `drift/five-facts.py`, a sample older than the newest commit that changed `cage_behaviour_sample` reads could-not-look on facts 6 and 7. The line names that commit. This lands before item 2, or in the same commit. It must never land after item 2, because then a pre-registration sample prints PASS on five facts (ticket 152 Q4).
2. **The new section.** Replace `cage_behaviour_sample` in each adopter's `drift/window.yaml` with [cage-behaviour-sample.draft.yaml](../research/ticket-152-fact-7-reference/cage-behaviour-sample.draft.yaml). Set `declared_on` to the day it lands. The three sections are identical except `declared_on`. Update the comment block above the section, which still says "refuses to score". Items 2 and 3 land in one commit on each adopter, because `grade` fails when the section and the code disagree on an id (ludlow `drift/five-facts.py:1391-1400`) and the selfcheck asserts they are equal (`:1583-1586`).
3. **The sampler.** In each adopter's `drift/five-facts.py`:
   - The reference Namespace is `cage-probe-reference`. It carries no governed label and no tier. The reference pod carries no version claim. Everything else about the pod stays as today.
   - Rename every "control" name and evidence key to "reference": `CAGE_CONTROL_NS`, `control_tier`, `control_namespace`, `control_before`, `control_after` and `networkpolicies_selecting_the_control_pod`. Include the delete at the end of the sample and the selfcheck fixtures.
   - Fact 7's id changes. Falsifier 3 gets its new name. Falsifier 4, `the_cage_puts_the_control_and_the_fall_closed_workload_on_the_same_rung`, is retired: a reference that the cage does not select carries no rung, so it can share the fall-closed pod's rung only if the cage stamps it, and `the_cage_selects_the_reference_workload` catches that. The `flat` selfcheck branch that asserts the retired id (ludlow `:1690-1693`) is replaced by one for the new falsifier.
   - The sentences the sample records change too, not only the names. Today the TRUE sentence says the control reached both "from the loosest rung" when its tier is empty (ludlow `:937-938`). For the reference it names no rung: "while the reference workload, which the cage did not select, reached both". Update the fact 7 `ceiling` string (`:817-824`) and the docstrings of `cage_facts`, `_cage_control_reads` and `_cage_reach_fact` the same way.
   - Falsifier `the_cage_selects_the_reference_workload` fires when the reference pod carries `posture.acme.io/tier` or `posture.acme.io/caged`, or a NetworkPolicy selects it.
   - Falsifier `the_fall_closed_rung_is_not_the_ladder_s_bottom` reads the PriorityClasses whose names start `cage-` live, as fact 4 already reads the cluster. It fires when the fall-closed pod's priority is above the lowest of them, or when the NetworkPolicy that selects the pod has a rule or does not declare both policy types. When it fires, facts 6 and 7 both read null.
   - Falsifier `the_cage_facts_stay_unmeasured` fires when fact 6 or fact 7 is null on each of the three newest samples in `drift/samples.jsonl` that were taken at or after the newest registration. `grade` then reports FAIL and names the fact and its reason. Samples from before the registration do not count. A lane run started by hand counts. So the rule can first fire on the third sample after the registration.
   - `grade`'s SKIP line names each null fact and its reason.
   - Add a selfcheck branch for each new falsifier, for item 1, and for the case that only one or two samples exist after the registration. The selfcheck assertion that the probe names no rung (ludlow `:1595-1600`) stays true: the reference Namespace declares nothing.
4. **The check, `verify-cage-probe.sh`, in each adopter.** It does these steps in order:
   1. It runs `five-facts.py selfcheck`. Nothing runs it today.
   2. It compares `kyverno version` with the engine that the adopter declares. When `gitops/engine/kyverno.yaml` exists (ticket 147), it reads the version there. Until then it reads `KYVERNO_VERSION` in the adopter's `drift-sample.yml`. If they differ, it exits 3 and names both versions. It runs the CLI named by the environment variable `KYVERNO_CLI`, and `kyverno` on the PATH when that variable is not set. So the hub can give each adopter its own CLI: ticket 150 item 4 supplies it from ticket 146's engine table when an adopter declares another engine.
   3. It proves that the CLI reads Namespace labels. A Namespace that declares `restricted`, given through a Values file `namespaces:` list, must land on `restricted`. If not, it exits 3 and names the CLI quirk.
   4. It reads the served versions from the ResourceSet array in `gitops/composed/composed-set.yaml`. It runs the sampler's own objects, imported from `_cage_objects`, against the served bodies at two points: the pinned composed tag and HEAD. It reports both.
   5. It fails when the fall-closed pod is not on the bottom (lowest `cage-` priority, and a selecting NetworkPolicy with no rules and both types), when any mutation or generated NetworkPolicy selects the reference pod, or when a PriorityClass that a mutation names is not served. It judges generation by the objects written, not by the CLI's result table.
   
   Its PASS and FAIL lines say that they are about the served documents. The lane's could-not-look on the same state is the behaviour claim, so the two do not conflict.
5. **The wiring.** Add one row per adopter script to `talk/verify-manifest.txt`, class `self-proof`, skip `-`. The row declares no skip, so on the hub an exit 3 is a fall. The total and the ceiling move by three. Add a step after the CLI install in each adopter's `shift-left.yml`, so the check runs on the recompose pull request. That workflow checks the adopter out without tags (ludlow `.github/workflows/shift-left.yml:91-97`), so the step first fetches the pinned tag named in `gitops/composed/composed-set.yaml`. If the tag is not present, the script exits 3 and names it.
6. **The documents.**
   - Each adopter's `drift/README.md` and the comment at `five-facts.py:133-142` describe the reference workload.
   - `talk/narration.json` and the regenerated `talk/deck.md:270` say "reference workload". `talk/verify-demo.sh` must still pass.
   - `tests/test_cage_ladder_holes.py` evaluates placement on platform's bodies (`:295`, `:350`, `:364`, `:468`). It stays, because the new script grades each adopter's served set, which is a different object. Its docstring names the adopter scripts, and "the control" at `:407` becomes "the reference".

## Notes

Graduated 2026-09-25 from ticket 152, Q12. Definition of done: the new section is on `main` in all three adopters. Each `verify-cage-probe.sh` passes under `talk/verify-all.sh` and has a manifest row. The first scheduled sample after the merge scores facts 6 and 7, as a PASS or as an observed FALSE. A could-not-look is not done.

The offline proof that an unclaimed pod in a Namespace that declares nothing is not caged, on all three adopters, is in [research/ticket-152-fact-7-reference/](../research/ticket-152-fact-7-reference/README.md). It is a document proof, not a cluster proof.

**Changed 2026-09-26, after ticket 71's round 5.** Ticket 71 no longer adds an engine fact to the drift lane, so no ticket from it edits `drift/five-facts.py` or `drift/window.yaml`. Ticket 147 creates `gitops/engine/kyverno.yaml` in each adopter, and item 4.2 reads it. The `KYVERNO_CLI` variable is decided here, delegated under ADR-0025, and was agreed with the session that owns ticket 71.

This ticket blocks ticket 151, and the fleet, policy and governance-agent row of ticket 156's register.
