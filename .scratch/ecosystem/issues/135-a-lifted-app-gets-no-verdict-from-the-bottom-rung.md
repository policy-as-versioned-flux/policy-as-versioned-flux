# 135 — A lifted app gets no verdict from the bottom rung

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. Truth run 314 graded `verify/lifted-apps/verify-lifted-apps.sh`
FAIL for the first time, after each adopter moved to platform tools v3.3.0 and its composed set
to v2.0.0 with the array 4.0.0 and 5.0.0 (tickets 111, 130). Its capture:

```
FAIL ledger: tuppence's composed set does not admit tuppence/gitops/apps/ledger.yaml -- policy
cage-baseline-4-0-0 produced no verdict at all (no row in the kyverno table) (pass: 8, fail: 0, ...)
```

and the same for driftwood's storefront and ludlow's reports. Run 310 graded it PASS.

What this ticket owes:

1. Establish which is true: the served set really fails to cage these workloads at CREATE, or the
   check asks a policy for a verdict that the new composition no longer gives, for example
   because the rung moved, a policy was renamed, or the check renders the set differently from
   how the adopter's ResourceSet serves it. Measure under kyverno 1.18.2 with each adopter's
   served set at v2.0.0.
2. If the cage is wrong, fix it where it is wrong and say which release carries the fix. If the
   check is wrong, make it ask the question the adopter's served set answers today, and keep a
   planted failure that it still catches.

## Done

`verify-lifted-apps.sh` grades each lifted app by what the served set does to it, and the reason
for run 314's FAIL is recorded.

## Build, 2026-09-22

### Answer: the check was stale, the cage is sound

The served set admits and cages all three lifted apps at CREATE. The check asked a
PriorityClass for a verdict.

How I measured it. Kyverno CLI 1.18.2. Each adopter's clone was fetched with tags. I read the
served set from each adopter's own `gitops/composed/composed-set.yaml`: tag v2.0.0 at tuppence
d5a4bfe, driftwood c26d95c and ludlow ab89691. Each tag resolves to the commit the file pins
(`git rev-parse v2.0.0^{commit}`).

1. Platform v3.3.0 puts four PriorityClasses in each version directory. At v2.0.0 each
   adopter's `composed/policies/v4.0.0/` holds nine files. Four are `kind: PriorityClass`
   (cage-baseline, cage-isolated, cage-quarantine, cage-restricted). Before the rollout commit
   (tuppence 664967a, driftwood 4d04ac0, ludlow b7c1f36) the directory held five files, all
   policies.
2. The check read every `metadata.name` in the directory as a policy. It then required a Pass
   row for each one in `kyverno apply --table`. Kyverno does not evaluate a PriorityClass, so
   it prints no row for one. `cage-baseline-4-0-0` sorts first, so run 314 named it.
3. Over the old check's own inputs (v4.0.0 plus the orphan guard), each of the three apps gets
   six table rows, all Pass: cage-tier, stamp-posture, posture-trust-boundary, require-nonroot,
   the orphan guard and cage-netpol. Each summary is `pass: 8, fail: 0, warn: 0, error: 0,
   skip: 0`, the same line run 314 printed. Ledger's mutated pod names
   `priorityClassName: cage-baseline-4-0-0`.
4. Over the whole served set (both versions plus the machinery route), each of the three apps
   gets `pass: 10, fail: 0, warn: 0, error: 0, skip: 8`. It gets 13 table rows. The six 4.0.0
   policies and the orphan guard pass. The 5.0.0 policies and `policy-version-orphan-cage` skip.
   The cage writes `cage-baseline-4-0-0`, and v4.0.0 serves that class.

So no repository other than the hub has to change. No platform release is involved.

### What changed in the hub

- `verify/lifted-apps/lifted_apps.py`: a new `served_set()` reads the adopter's
  `composed-set.yaml`. It checks the GitRepository's tag against its commit. It renders the
  ResourceSet template (only `range` over `versions`, `$v.version` and `$v.version | slugify`),
  then reads each Kustomization path at the pinned commit. A path with a `kustomization.yaml`
  serves its `resources[]`. A path without one serves every manifest under it, as Flux does.
  `kyverno_plan()` writes every served policy into a work directory. It names the policies that
  must pass (the claimed version's plus the orphan guard) and lists the served PriorityClasses.
- `verify/lifted-apps/verify-lifted-apps.sh`: step 3 applies the whole served set. Every
  must-pass policy needs a Pass row of its own. Every other row must be Pass or Skip. A skip
  count above 0 is allowed, because other versions skip by design. A new `class_served` step
  requires the mutated pod's `priorityClassName` to be a class the set serves. It also fails
  when no policy writes one.
- `talk/verify-manifest.txt`: the row for this check now says what step 3 measures.

### Decisions

- Delegated: only objects in the `policies.kyverno.io/` or `kyverno.io/` API groups are asked
  for a verdict. Anything else a route serves is an object, not a voter. Reason: kyverno
  evaluates only policies, so any other kind can never produce a row.
- Delegated: a served PriorityClass is graded by what admission does with it. The class the
  cage writes must be one the set serves, and a pod with no class fails as uncaged. Reason:
  Kubernetes' Priority admission refuses a pod that names a missing PriorityClass. So this is
  a real CREATE fact, and dropping the class from the grade would have hidden it.
- Delegated: the check applies every route the ResourceSet renders, read at the tag that
  `composed-set.yaml` pins, not the checkout. Reason: that is what a cluster gets. A policy of
  another version, or a machinery policy, could refuse the pod, and the old input would not see
  it. The pin and the checkout differ today only in `HEADER.yaml` and `evidence.json`
  (`git diff --stat v2.0.0 HEAD -- composed/`).
- Delegated: any `<< >>` expression the renderer does not know is named as a failure, never
  guessed. Reason: a guessed route would grade a set nobody serves.
- Delegated: a pin the clone cannot read is a FAIL, not a could-not-look. Reason:
  `clone-estate.sh` makes full clones with tags, so an unreadable pin is a defect. The check's
  own rule is that a gate which has lost its instrument goes red.

### Tests, red then green

- `tests/test_lifted_apps.py`: I added nine tests for the plan and the served set. With the
  plan unchanged, all nine failed and 37 passed. After the change, 46 passed
  (`.venv/bin/python -m pytest tests/test_lifted_apps.py -n0 -q`).
- The selfcheck fixture now serves a `composed-set.yaml` at v2.0.0, with both versions, the
  machinery route and a PriorityClass in the v4.0.0 directory (run 314's shape). I added the
  same PriorityClass to origin/main's old selfcheck fixture. The old check then failed with
  `policy cage-baseline-4-0-0 produced no verdict at all`. The new selfcheck passes. It still
  catches eight planted failures, each by name: a class the set does not serve, no cage at all,
  another version refusing the pod, a refusal only at the pin, a claimed version the array does
  not serve, no orphan guard, no composed set, and a tag and commit that disagree. The 9.9.9
  pod, a silent policy and a skipping must-pass policy still fail.
- `verify-lifted-apps.sh` over the estate clone exits 0: three `ok` rows in step 3 and PASS.
- `mypy twin tests conftest.py` is clean. `mypy verify/lifted-apps/lifted_apps.py` is clean.
  `tests/test_truth_manifest.py`: 18 passed.

### Observed, not changed

- The four `governed-namespace-*` machinery policies give no row. They select on a namespace
  label, and `kyverno apply` has no namespace object. They match only pods that claim no
  version, so they cannot touch a lifted app. That is a limit of the CLI, not of this check.
- The CLI printed Pass for `cage-netpol-5-0-0` on a pod claiming 4.0.0, even though the policy's
  `only-this-policy-version` condition is false. So a GeneratingPolicy's Pass row in the CLI is
  not evidence that its conditions held. The check requires Pass from `cage-netpol-4-0-0` only as
  "it gave a verdict". It does not read that row as proof of reach.

### What remains

- A scheduled truth run must grade this check PASS on main after the merge. That needs the clock,
  not the owner.
- Nothing waits on the owner.
