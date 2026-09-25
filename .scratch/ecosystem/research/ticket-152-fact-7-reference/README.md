# Ticket 152: where a reference workload lands under the served cage

Measured 2026-09-25, offline, with the kyverno CLI **1.18.2**. The homebrew 1.19.1 cannot
compile the served 5.0.0 `cage-tier` body, so it was not used.

## What was measured

The served cage of each adopter, read at `origin/main`:

| Adopter | `origin/main` | Pinned composed tag |
|---|---|---|
| ludlow | `b8e14f7` | v3.0.0, `45b3fbd` |
| driftwood | `155db9e` | v3.0.0, `bf9889a` |
| tuppence | `5deffe6` | v3.0.0, `3d64a4d` |

At each pinned commit, `composed/` differs from `origin/main` only in `composed/HEADER.yaml`. The
served policy files differ between adopters only in the `policy-as-versioned.dev/composed-for`
label. All three adopters gave the same result for each candidate.

The probe objects copy `_cage_objects` in each adopter's `drift/five-facts.py` (ludlow
`:464-482`). Each candidate changes only the Namespace labels or the pod's version claim.

## Result

| Candidate | Namespace labels | Pod claims | Rung | NetworkPolicy that selects the pod | Reach |
|---|---|---|---|---|---|
| F, fall-closed, as today | governed, no tier | 5.0.0 | `isolated` | `cage-reach-isolated`, no rules | none |
| OLD, control, as today | none | 5.0.0 | `isolated` | `cage-reach-isolated`, no rules | none |
| RA | governed, tier `baseline` | 5.0.0 | `baseline` | none | both targets |
| RB, the chosen reference | none | nothing | not caged | none | both targets |
| RC | tier `baseline`, not governed | 5.0.0 | `baseline` | none | both targets |

"Reach" is predicted from the generated NetworkPolicies. It is not a live connection. The lane
measures live reach.

- OLD reproduces the live samples of 2026-09-25 (ludlow `drift/samples.jsonl:78`: both tiers
  `isolated`). So the harness matches what the lane saw.
- RA and RC give identical objects. The `governed` label does not change the rung under 5.0.0
  (`cage-tier.yaml:31-34`). Ticket 159 holds that finding.
- At the `baseline` rung the cage writes the app container's `runAsNonRoot: false`, over a pod
  that declared `true` at pod level (`cage-tier.yaml:40`). Ticket 158 holds that finding. It
  does not touch RB, because the cage does not mutate RB.
- Each adopter serves every PriorityClass that the mutations name: `cage-baseline-5-0-0` (-10),
  `cage-restricted-5-0-0` (-100), `cage-quarantine-5-0-0` (-1000), `cage-isolated-5-0-0` (-10000)
  and `cage-isolated` (-10000). So the API server does not refuse RA or RC for a missing class.
- Both generators write into the pod's own Namespace (`generator.Apply(variables.nsName, ...)`).
  So a NetworkPolicy in the fall-closed Namespace cannot select a pod in the reference Namespace.

## Controls on the harness

- `SANE-quirk`: the RA pod with its Namespace given as `--resource` lands on `isolated`, while
  the Namespace declares the `baseline` rung. A Namespace reaches `namespaceObject` only through
  a Values file `namespaces:` list. `run.sh` does not run this case. The command and its output
  are in `harness/out/ludlow-SANE-quirk.txt`.
- `SANE-govnoclaim`: a governed Namespace with an unclaimed pod gets `cage-isolated` and
  `cage-reach-bottom-rung-isolated`. So the Namespace selector works in the CLI.
- `SANE-RA-nonsobj`: a Values file with `namespaceSelector:` only still gives RA `baseline`.

## How to run it again

Copy `harness/` to a scratch directory first. The runner writes its outputs beside itself.

1. Set `KYVERNO` to a kyverno 1.18.2 CLI.
2. Set `PROVE` to a directory, and extract each adopter's served tree into it:
   `git -C .estate-clone/<adopter> archive origin/main composed gitops | tar -x -C $PROVE/<adopter>`.
3. Run `python3 gen.py` to write each candidate's `pod.json` and `values.json` again. The
   committed inputs are already in the candidate folders.
4. Run `bash run.sh <adopter> <candidate>` for each pair.
5. Run `python3 summ.py <adopter>`. The committed summaries are in `harness/out/`.

A re-run from a copy on 2026-09-25 gave the same lines for F, OLD, RA, RB and RC as `harness/out/ludlow.summ`.

## The draft registration

- `cage-behaviour-sample.draft.yaml` is the section that ticket 161 builds.
- `cage-behaviour-sample.diff` compares it with ludlow's registered section.

Fact 6's text is byte-identical. Facts 6 and 7 share one section, so the new registration
restarts both.
