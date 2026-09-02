# NORTH-STAR §3 — the seven principles, graded

Auditor pass, 2026-09-02. Citable base: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 pass=57 fail=7
skip=18 excluded=2 total=84` (`talk/truth.log`, origin/main). Unit clones at the run-21 SHAs under
`.../scratchpad/units/`. Every claim below is either a file:line I read, a command I ran with its
output, or a run-21 capture read from `origin/main:talk/captures/`.

Grading convention used throughout:
- **proven on a citable run** = graded PASS/FAIL/SKIP by run 21's gate;
- **proven locally** = I ran it or read the artefact it produced, off the clock;
- **asserted** = written down, nothing observes it.

---

## Method notes and corrections to the reader maps

I re-derived everything I rely on. Three reader claims did not survive:

1. `platform-engines.md`: "`graded/policies/cage-tier.yaml` self-admittedly only implements the
   first 3 of cage.py's 5 tiers (no `isolated` dial mapping in the live Kyverno body yet)". **False
   at platform 46cd775.** The dial map in both the authoring copy
   (`platform/graded/policies/cage-tier.yaml:181-185`) and the served copy
   (`platform/distribution/policies/v4.0.0/cage-tier.yaml:38`) carries four rungs including
   `'isolated': {...'pc':'cage-isolated-4-0-0','prio':'-10000'...}`. `graded/README.md:31` lists
   `isolated` in the table.
2. `truth-series.md`: "21 scripts have remained in FAIL across all mature runs, including
   ludlow/tuppence adopter gates, verify-party, verify-pound-seam, verify-provenance". **False for
   run 21.** I graded all 82 captures on origin/main: `verify_party`, `verify_pound-seam`,
   `verify_provenance` and `.estate-clone_tuppence_scripts_verify-adopter-gate` are all PASS. The
   seven fails are exactly: driftwood twin-scenarios, driftwood verify-reconcile, driftwood
   twin-overlay, ludlow verify-reconcile, tuppence verify-reconcile, verify-demo, e2e-step4.
3. `github-live.md`: "Hub truth.yml … the run immediately after the cited TRUTH run=21 10:11Z
   capture [failed with] 'the scheduled truth run left a change outside the observation lane'".
   **Not run 21's failure.** `gh run view 33616685427 --json jobs` shows step 9 "the observation
   cage" **success** and step 10 "fail if the gate failed" **failure** — the workflow reddened
   because the gate had seven reds, which is the designed behaviour, not a cage violation.

Also confirmed fixed since REVIEW-2026-08-31: none of run 21's seven reds is a kyverno-pin fault
(C1 closed by ticket 54); `verify-source-verification` is SKIP-with-reason, not a misclassified red
(M2 closed by ticket 55); `verify-publisher-gate` completes and grades SKIP rather than timing out
(M3); `verify-corpus-generator` is PASS (M4); step 1, step 6 and feed-contract all PASS, so
jsonschema is installed on the clock (M5); the three `verify-reconcile` checks now grade the sample
before the substrate check (M7); feeds and insurer have registered workflows and real signed tags
(M1 partly — see P6-2).

---

## Principle 1 — Everything is policy. No exemptions, under any name.

### Strongest evidence it holds

- **No exemption mechanism exists anywhere in the eight units.** `grep -rni
  "PolicyException|exemption"` over all eight clones returns 19 non-markdown hits and every one is
  a negation or a reference to the deleted `render-exemption.py`
  (`platform/graded/cage.py:30-33`, `platform/distribution/render-governed-namespace-guard.py:18`,
  `platform/graded/policies/cage-tier.yaml:17,149`,
  `platform/compose/composition.py:36,1119-1120`). No live carve-out list, no allow-by-name.
- **The coverage-exclusions file is disclosure, not an exemption, and is structurally add-only.**
  `platform/computed-semver/coverage-exclusions.yaml` ends `declared_holes: []`, and its header
  states only four keys are ever read and that no key in the file can promote an entry to a proved
  exclusion — proved exclusions are computed by `coverage.py`'s `static_proof` from the expression
  text. This matches REGRILL 10 ("No: it is disclosure, not an exemption. Keep it.").
- **The £-refusals are ADR-sanctioned instrument faults, not exemptions.** 85 `MissingInstrument`
  / "missing instrument" sites across the units; `enforce.py`'s selfcheck asserts
  `platform/risk/appetite.json` does not exist, so a party with no signed appetite refuses rather
  than defaulting (ADR-0021). REGRILL 11 explicitly permits this ("Instrument faults still refuse").
- **Composition calls its own weaker-restatement path a declared inability, priced, not an
  override** (`platform/compose/composition.py:1119-1120`).

### Strongest counterexamples

**P1-1 (major, owned).** The conditional-rule arm — the half of principle 1 that says an allowance
must be "a conditional rule anyone can meet" — has no living instance. `platform/policy/verify-conditional.sh:73`
prints, and run 21's capture records verbatim:

> SKIP (live tail): the root-attested conditional branch this beat proves lives only in
> require-nonroot-2-0-1, and 2.0.1 is retired (not in distribution/versions.yaml, 2026-08-29); the
> only currently-declared version (4.0.0) replaced it with a flat non-root+read-only-fs rule that
> has no root-if-attested branch

Owner: **ticket 63 (open, unblocked)** — ticket 58's recorded decision is that the isolated-flip cut
is the second declared line (5.0.0) and "re-carries the root-if-attested conditional branch".
This is an **update to REVIEW-2026-08-31 M11(2)**, which called it an orphan; it now has an owner.

**P1-2 (major, owned by build, orphaned in the record).** `CONTEXT.md:196-200` states as present
fact that "a composition **prices** every hole, new or pre-existing, and a new hole moves the tier,
never refuses". The shipped code does the opposite: `platform/compose/composition.py:1316-1323`
appends `{"kind": "new-hole" … "a new hole refuses (ADR-0013)"}`, and `composition.py:2290` turns
any refusal into `outcome: refused`. The build is owned (tickets **38** and **39**, both open); the
**record fault is not** — CONTEXT.md writes the destination in the present tense with no dated
"not yet" marker, which is the same class REVIEW-2026-08-31 M13 raised against `map.md`.

**P1-3 (minor).** The adopter-set tighten-only floor (REGRILL 23, ADR-0022) is implemented
(`platform/graded/cage.py:140-149` clamps up only; driftwood's `selection-policy/selection_policy.py`
does the same) but **no adopter declares one** — `grep -n floor` over all three `party.yaml` files
returns nothing. The mechanism is never exercised on real data.

**P1-4 (minor).** `revoked[]` exists in `party/schema.json:92-95` and is validated
(`party_artefact.py:295-298`) but is `[]` in every party artefact, so "a pin to a revoked version is
a priced hole, never a refusal" has never been exercised.

**Verdict: the principle holds in code and in the record with one arm dead (P1-1) and one arm
written as done before it is built (P1-2).**

---

## Principle 2 — Everything is always caged. There is no gate.

### Strongest evidence it holds

- **The cage ladder is real, served, and tighten-only in fact, not only in prose.**
  `platform/distribution/policies/v4.0.0/cage-tier.yaml` (the copy every adopter composes from)
  carries four rungs. The mutation is tighten-only by construction:
  `readOnlyRootFilesystem`/`runAsNonRoot` are **OR**ed with what the container declared;
  `allowPrivilegeEscalation`/`privileged` are written `false` (the tight end of both);
  cpu/memory are a **MIN** (`quantity(...).isLessThan(...) ? container's own : dial`).
  The authoring copy's header records that the MIN was a fix for a real tenfold loosening
  (`graded/policies/cage-tier.yaml:56-60`).
- **The bottom rung runs and reaches nothing, and the escape from it was found and closed live.**
  `hostNetwork`, `hostPID` and `hostIPC` are clobbered `false` at every rung, with the reason
  written in: "`hostNetwork: true` walked straight out of the `isolated` rung … the bottom rung
  reached the API server and the internet (observed live, 2026-08-28)". `cage-netpol.yaml`'s
  `reach` map gives `isolated` `{'ingress': [], 'egress': []}` and every other rung DNS-only egress.
- **Fail-closed is real, not narrated.** `variables.tier` is
  `nsTier in [...] ? nsTier : (nsGoverned ? 'isolated' : 'baseline')` — a governed namespace with no
  tier, or an unknown tier (`infra` included), renders `isolated`.
- **The live proof is a connection, not a YAML read.** `platform/graded/verify-graded.sh:480-505`
  execs `nc -w 4 -z <apiserver ClusterIP> 443` and `nc … 1.1.1.1 80` from the isolated pod and
  fails if either succeeds after 60s, then asserts the **baseline** pod still reaches, then asserts
  `kubectl label` on a running isolated pod is **not** refused ("an UPDATE to a running isolated pod
  was REFUSED — the cage denied a workload").
- **`deny` is retired structurally.** `cage.py:346`: `assert "deny" not in TIERS and "deny" not in
  LADDER`. `cage.py:352`: `select_tier(r, 1_000, floor="baseline") == "isolated"` — the floor can
  never loosen.
- **driftwood's own governed namespace declares the bottom rung.**
  `driftwood/gitops/apps/namespace.yaml:14,30`: `governed: "true"`, `posture.acme.io/tier: "isolated"`.

### Strongest counterexamples

**P2-1 (major, owned).** Humans and devices are on a **gate**, not a cage ladder.
`platform/access/README.md` heads the table row "The gate | `access.py` | graded ALLOW / STEP_UP /
DENY"; `access/access.py:78-80` returns `DENY` for a missing OIDC or a missing device SVID, and
`OP_TIER` (`access.py:36-44`) is a static table with no £ input — the README names wiring it to
`fair.py`'s crossover as an upgrade path. Owner: **ticket 27 (open)**, whose text says
"access.py retirement and break-glass bands per org appetite".

**P2-2 (major, owned).** The twin — which principle 2 names explicitly — has **no cage spec, no
tier, no price**. Across the whole `twin/` package only two files mention "cage"
(`enforcement-grades.yaml`, `README.md`); there is no tier declaration and no priced entry for the
twin's own operation. What exists is `twin/enact_guard.py`, a refusal boundary (`twin/ENACT_MODE`
= `operations`, `DEFAULT_MODE = "operations"`, `enact_guard.py:88,272`) — i.e. exactly the gate
principle 2 says there is none of. Owner: **ticket 30 (open)**.

**P2-3 (major, partly sanctioned, the uncaged half unowned).** The claiming population is caged;
the non-claiming population is either uncaged or refused. `cage-tier.yaml:36-42`, verbatim: "A pod
with no claim at all — kube-system, Kyverno's own pods, Flux's controllers, cert-manager, **any
COTS workload** — is not matched, and so is not caged." Inside a governed namespace the same pod is
**refused** by `governed-namespace-requires-claim` (`distribution/versions.yaml:155-157`,
`validationActions: [Deny]`), which ADR-0022 blesses as "the one refusal the doctrine allows".
So "everything is always caged" reads today as "every version-claiming pod is caged; everything
else is either outside policy or refused". The uncaged population is named in a code comment
("spun out to its own effort") with no ecosystem ticket owning it.

**P2-4 (major, orphan).** The orphan-guard is a **second** live refusal that ADR-0022's "one
refusal" clause does not cover. `distribution/versions.yaml:112-139` ships
`policy-version-orphan-guard` with `validationActions: [Deny]` and the message "…so it cannot run".
`distribution/verify-orphan-guard.sh:45-49` makes the **denial** its PASS condition
("orphan pod (9.9.9) was NOT denied — a version outside the array could run"), and run 21's capture
records `PASS: only versions the array declares can run`. Meanwhile `CONTEXT.md:218-228` says the
orphan guard "cages to **`isolated`** … the workload is **not denied**" and calls the shipped Deny
"the July record, superseded by ADR-0022". Neither `.scratch/ecosystem/issues/` nor `map.md`
carries a ticket for this; `grep -rn orphan` over the tracker returns only unrelated
release-chain-orphan discussion.

**P2-5 (major, orphan).** **No governed workload is reconciled by Flux anywhere in the estate**, so
"a workload … runs inside a cage" and §4 step 4's "the workload keeps running, caged tighter" cannot
be observed today.
- driftwood is the only adopter with a workload (`gitops/apps/pod.yaml`, `checkout-svc`, claiming
  `policy-version: 4.0.0`), but its Kustomization is `path: ./apps`
  (`driftwood/gitops/flux-system/gotk-sync.yaml:40`) and `./apps` **does not exist** — `ls apps`
  fails at HEAD and `git ls-tree --name-only v1.1.0` lists `composed deploy drift git-server gitops
  kind scripts …` with no `apps`.
- tuppence and ludlow have the fixed `path: ./gitops/apps` (ticket 42) but their `gitops/apps/`
  contains only `kustomization.yaml namespace.yaml nist-pin-configmap.yaml
  risk-appetite-configmap.yaml version-configmap.yaml` — **no pod**.
- Consequently the run-21 five-fact sample's "all 16 rendered objects" are policy objects from
  `composed/`; no workload is in the set.

**P2-6 (major).** The **only live proof of the cage has never been on a citable run.**
`verify-graded` is SKIP on run 21 ("kind cluster 'driftwood' is not listed by kind get clusters"),
and it was FAIL on runs 10–13 under the kyverno-1.19 skew. Every claim in the "strongest evidence"
list above about a pod actually running, actually failing to reach, actually accepting an UPDATE, is
**proven locally, never on the clock**. Related but distinct from ticket 56.

**P2-7 (minor, orphan).** Self-disclosed race: generation is a background controller, so
"the reach cage lands one round-trip AFTER the pod is admitted (about 10s on KinD). A brand-new
governed namespace's first caged pod therefore has full reach for that window"
(`graded/verify-graded.sh:275-280`). The named upgrade path is "tickets 40/42" — **both resolved**
without doing it.

**P2-8 (minor, orphan).** Self-disclosed hostPath hole: "a `hostPath` VOLUME cannot be clobbered the
same way (SSA merges the volume list by name and cannot remove an entry), so an isolated pod can
still mount the node filesystem. The cage's forced `runAsNonRoot` is the only bar on it today"
(`graded/policies/cage-tier.yaml:84-89`). No ticket.

**Verdict: pods are genuinely caged, tighten-only, and the bottom rung is a running cage — proven
locally to an unusually high standard and never proven on the clock. Humans, devices, model actions
and the twin are not on the ladder; two live Deny policies exist, one blessed and one not; and no
workload is under Flux at all.**

---

## Principle 3 — One £ currency, proportionate to the org.

### Strongest evidence it holds

- **One unit, one perspective per list, checked and PASS on the citable run.**
  `verify/pound-seam/pound_seam.py` check 5: "no list of amounts anywhere in the document mixes
  perspectives or currencies — a sum that crosses either is the live bug ADR-0020 was written
  against". Run 21's capture: `PASS: every price names its perspective, currency, source and
  per-customer share; no sum crosses either`.
- **Proportionality is computed, not asserted, and is PASS on the citable run.**
  `verify_proportionality`: `PASS: same control, same £ (risk_bought £21107) — Audit in driftwood,
  Deny in ludlow.` Size drives `per_customer`: driftwood declares `size:` and every `per_customer`
  is populated; tuppence and ludlow declare none and every `per_customer` is `null` — I confirmed
  this reading `driftwood/composed/evidence.json` directly (four `prices[]` entries, all with
  populated `per_customer`).
- **The platform's appetite fixture is genuinely retired.** ADR-0021; `enforce.py`'s selfcheck
  asserts `risk/appetite.json` does not exist; pound_seam check 6 asserts "no code left behind still
  reads it".
- **Two tier-selection engines, cross-checked to the band boundary.** pound_seam check 9 runs
  driftwood's own published `selection-policy` package and `platform/graded/cage.py` over the same
  residuals at each boundary and with every rung as a floor, and refuses any disagreement; check 8
  asserts the estate's recorded `curve_hash` equals the one the adopter's own package computes over
  its own published curve. Both PASS on run 21.
- **FX crosses through the publisher's own converter and refuses an unpublished date** (check 10).

### Strongest counterexamples

**P3-1 (major, orphan).** The twin's priced entry under **driftwood's** perspective is computed from
**platform's** self-declared reduction table, not from driftwood's own published response curve, and
the two differ materially. `driftwood/composed/evidence.json` `prices[3]`:
`{"source":"twin","perspective":"driftwood","currency":"GBP","amount":1897646.11,
"residual_basis":"platform-cage-tiers@1.0.0"}`. driftwood's own published curve
(`twin/orgs/driftwood/responses/*.yaml`) has mode reductions **0.05 / 0.30 / 0.65 / 0.90** at costs
£8k/£20k/£42k/£95k; platform's table (`graded/cage.py:82-111`) has **0.30 / 0.70 / 0.92 / 0.98** at
£500/£2k/£6k/£15k. Run 21's own capture measures the gap: "they differ by up to **171,600** on the
rungs themselves". This is honestly disclosed (`residual_basis` names the set) and honestly graded
(the check goes red if the two stop agreeing about which rung is cheapest), but it means REGRILL 33's
"each party prices under its declared perspective; no perspective privileged" is not true for the
twin line: the platform's perspective is privileged. `grep -rln "residual_basis|platform-cage-tiers"`
over `.scratch/ecosystem/` and `docs/` returns **nothing** — no ticket owns closing it.

**P3-2 (major, orphan).** There are **two independent implementations of the same severity model in
two repos with no equality check between them**. `platform/fair/severity.py` (80 lines) and
`twin/severity.py` (215 lines) both implement the lognormal-GPD splice; platform's header explains
why the code was duplicated rather than imported ("`twin/` is a python package in the HUB repo and
`fair.py` runs inside the `platform` repo … the seam the ticket wanted is the *payload* crossing").
That reasoning is sound, but nothing anywhere compares the two samplers' output on the same spec —
`grep -rn "fair/severity|severity.py"` over `verify/` returns nothing. The estate built exactly this
kind of drift guard for the two *selection* engines (pound_seam check 9) and did not build it for the
two *severity* engines, which are the numbers everything downstream is priced from.

**P3-3 (minor).** pound_seam's "two-implementations guard" cannot catch P3-1 by construction: check 9
runs both engines "over the SAME residuals" (its own docstring), and driftwood's
`selection_policy.select()` takes residuals "from the estate's own pricing" as an input. The question
of *whose curve produced the residual* is check `check_residual_basis`'s, and that check only compares
**which rung is cheapest**, explicitly not the per-rung reductions ("the per-rung reduction is not
[checkable], because the curve publishes one figure per rung … and two unknowns behind it").

**Verdict: one currency and one perspective discipline, enforced and green on the clock — the
strongest-built principle. But the twin's own £ and the estate's £ are two engines joined by a JSON
payload, and on the one line where they meet the platform's numbers win by up to £171,600 a rung.**

---

## Principle 4 — Policy is a versioned dependency, all the way up and down.

### Strongest evidence it holds

- **Semver has been COMPUTED on a real release.** Tag `policy/v4.0.0` on platform. Evidence file
  `platform/computed-semver/evidence/4.0.0.json` records
  `bump: {declared: major, computed: major}`, `outcome: {result: passed}`,
  `counts: {old: 153, new: 152, union: 164}`, `generator_version: 0.2.0`,
  `corpus_checksum: sha256:ae12308f64efd…`, `wall_clock: 88.78s`, `movement[0].policy:
  cage-tier.yaml, verdict: major` with 28 named corpus entries, plus a cosign `.bundle`. Run 21's
  `verify-first-gate-determined-release` capture:
  `ok policy/v4.0.0: declared 'major' == evidence 'major', computed 'major', outcome passed` and
  `ok policy/v4.0.0 -> 1d8cec2…, array names its parent 64635df…`.
- **I verified the tag against Rekor myself**: `git -c gpg.format=x509 -c gpg.x509.program=gitsign
  tag -v policy/v4.0.0` → tlog index 2664927495, "Good signature from
  …/policy-as-versioned-platform/platform/.github/workflows/cut-release.yml@refs/heads/main",
  "Validated Rekor entry: true".
- **The evidence is honest about its own limits.** `limits[]` carries three named, open limitations
  including "the cage half of Track 2 is proved on synthetic input, never a real infrastructure
  capture", and `not_looked_at: []`.
- **The COTS substrate the platform itself runs does wear a version.**
  `platform/identity/VERSION` = `1.1.0`; platform's `git tag -l` carries `v0.1.0 … v2.0.1` beside
  the `policy/v*` line, and `HEADER.yaml` pins `platform / implementations / 2.0.1 / 533dccb…`.

### Strongest counterexamples

**P4-1 (major, owned).** **No older line is patchable, because there is no older line.**
`distribution/versions.yaml` declares exactly one element: `{version: "4.0.0", tag: "policy/v4.0.0",
commit: 64635df…, bump: "major"}` (line 77). Run 21's captures record the consequence three times:
`verify-coexistence` → "distribution/versions.yaml declares one version (4.0.0)";
`verify-retirement` → "declares one version (4.0.0), so a retirement would leave an empty
allow-list"; `verify-shift-left` → "declares one major line (4.0.0), so a target has no ±1
neighbour". The thesis' ≥3-coexisting-versions requirement and the "older lines are patchable" clause
have no subject at all. Owner: **ticket 63 (open)** carries the 5.0.0 cut, and ticket 58's recorded
decision names it as the coexistence subject.

**P4-2 (major, orphan).** **What Flux actually installs on driftwood is the three RETIRED lines.**
`driftwood/gitops/composed/composed-set.yaml:85-87` declares `2.0.0`, `2.0.1`, `3.0.0`, with the
comment "4.0.0 — the cage release (ticket 26) — is NOT here yet on purpose. This array is reconciled
from the tree at tag v1.1.0, and v1.1.0 carries composed/policies up to 3.0.0 only." Run 21's
five-fact sample confirms the live shape: `last_applied_revisions: {composed-v2-0-0, composed-v2-0-1,
composed-v3-0-0}`. Those three lines were retired, not patched, because "pods forging their own
`posture.acme.io/tier` label via unread `namespaceObject`" reached the API server from an
`isolated` namespace (observed live 2026-08-28, `map.md`). A second consequence: driftwood's HEAD
orphan-guard allows `['4.0.0']` while the **installed** one at v1.1.0 allows
`['2.0.0','2.0.1','3.0.0']`, so the pod at HEAD (claiming 4.0.0) would be denied by the guard Flux
actually runs. No open ticket names the composed-set bump; `grep -l "composed set"` over the tracker
returns only resolved tickets 05, 12, 16, 40, 60.

**P4-3 (major, orphan).** REGRILL 6 is a recorded owner **override** — "Run the full set. Accept the
runtime cost" — and ticket 18's Notes even sized it ("432 per subject … roughly 15-45 minutes:
re-grill 6's 'accept the runtime cost' is affordable"). The shipped 4.0.0 evidence still says
`coverage.pairwise_gap: "axes were combined pairwise … so no three-way interaction was built"`.
Ticket 18 is resolved and its Answer's five items do not cover it; ticket 21 (resolved) was to
build it. Disclosed in the evidence, owned by nobody.

**P4-4 (minor, owned as a decision, unbuilt).** The COTS shim of principle 4's last sentence does not
exist. Ticket 13's own text: "(b) is the COTS shim (**GAPS 3.14: decided four times, built zero
times**)". The identity substrate package covers the platform's *own* COTS only; an adopter's COTS
pod claims no version and so is not matched by `cage-tier` at all (see P2-3).

**Verdict: the computed-semver machinery is the estate's best-proven engine and has cut one real,
Rekor-verified, gate-determined release. Everything downstream of that — coexistence, patchability,
what an adopter actually installs — is either absent or a year behind the release it proves.**

---

## Principle 5 — Intelligence re-prices on a clock; enactment only by reviewed PR.

### Strongest evidence it holds

- **Twenty clocks are named and every scheduled job is structurally cage-checked, PASS on the
  citable run.** Run 21's `verify_schedules` capture prints, for each of driftwood's
  drift-sample/propose-tier/renovate-run/twin-sweep, tuppence's and ludlow's equivalents, and the
  fetch clocks of feeds/ico/insurer/nist/platform plus hub truth and twin: `job <name>: caged — no
  shell step in this job stages a declaration or mints a signed artefact, and nothing it runs is
  opaque to this checker`.
- **The lane is declared as data and read by both sides.** `.github/workflows/truth.yml:38`
  `OBSERVATION_LANE: "talk/truth.log drift/samples.jsonl talk/captures observations"`;
  driftwood's `drift-sample.yml` declares `OBSERVATION_LANE: "drift/samples.jsonl"` and nothing
  else; `verify/schedules/verify-schedules.sh` parses the same list out of the workflow YAML.
- **The proposer commits nothing.** `driftwood/.github/workflows/propose-tier.yml` re-composes into
  `${RUNNER_TEMP}/recomposed`, and its cage step does `git reset -q` **first** — a fix for a real
  defect where "a declaration any earlier step had left in the index was committed and pushed while
  this step printed 'this clock declared nothing' (review, 2026-08-28)".
- **The clock reddens honestly.** Run 21's workflow failed at step 10 "fail if the gate failed" with
  step 9 "the observation cage" green — the number was still recorded and the run still went red.

### Strongest counterexamples

**P5-1 (major, owned).** The live half of the clock check — "did each clock run inside its period" —
**SKIPs for every clock on every citable run**, structurally: the gate step carries no GitHub
credential, so `gh auth status` fails. Run 21's capture has twelve consecutive
`SKIP: <unit>/<workflow>: GitHub unreachable … cannot look at whether this clock ran inside its
period`. The truth surface cannot see whether its own off-board observers are alive. Owner:
**ticket 56 (open)**.

**P5-2 (major, owned).** **No clock has ever changed a policy verdict, because no proposal has ever
opened.** `gh pr list --state all --limit 60` across all three adopters returns 22 + 14 + 12 PRs and
**zero** `wargamer/retune-*` branches; the only tier-related PRs are the three human
"policy-composition: … propose-tier workflow" merges. Ticket 60's own comment records the first
scheduled firing returning `[]`. Owner: **ticket 74 (open)**.

**P5-3 (major, orphan).** When step 3 does fire, **the proposal commit will be unsigned.**
`driftwood/.github/workflows/propose-tier.yml` contains no gitsign install, no
`gpg.x509.program`/`commit.gpgsign` config, and the only occurrence of "sign" in the file is in a
prose comment. `platform/wargamer/tier_pr.py:350` calls `_git("commit", "-q", "-m", …)` with no
signing. `driftwood/.github/scripts/adopter-gate.py:75-78` pins only `cut-release.yml`, so
propose-tier is in no expected-identity regexp. This contradicts **reversal 16** ("sign the proposal
commit with the workflow Actions identity; add it to the expected-identity regexp"), recorded as
decided in tickets 02, 10, 12 and 13. Meanwhile `platform/wargamer/wargamer.py:200,232` still
hardcodes `"signed": True` and `wargamer.py:324` asserts it in the selfcheck — a self-referential
green. GAPS 1.9's remedy ("gitsign in `tier_pr.py`; delete the literal `"signed": True`") is
unapplied and has no ecosystem ticket. Contrast: `driftwood/.github/workflows/twin-sweep.yml:116,212`
**does** install pinned gitsign and set `gpg.x509.program gitsign` for its observation commit — so
the estate knows how, and the proposer simply does not.

**P5-4 (minor, honest note, no defect).** A clock **does** change the truth surface's verdict without
review: the three adopters' `drift-sample` clocks append samples that the hub's
`verify-reconcile` grades, and that is what flipped three checks from SKIP (runs 13–20) to FAIL
(run 21). This is the designed behaviour under ADR-0024 D1 ("a clock appends observations, never a
declaration") and is consistent with principle 5's "nothing timed ever changes a *verdict* on its
own" read as *policy* verdict. Recording it so the distinction is deliberate rather than implicit.

**Verdict: the schedule and the cage around it are the second-best-built part of the estate and are
green on the clock. The clocks are half-blind (they cannot see each other), the enactment arm has
never fired, and the signature the proposal is supposed to carry is not wired.**

---

## Principle 6 — Every actor is attestable, and the record is falsifiable.

### Strongest evidence it holds

- **I verified four tags against Rekor myself**, in four separate orgs, with each repo's own pinned
  identity: platform `policy/v4.0.0` (tlog 2664927495), driftwood `v1.1.0` (tlog 2585920387), ico
  `v3.0.0` (tlog 2664928228), feeds `threat-register/v2.0.0` (tlog 2673492733). Every one:
  "Validated Git signature: true / Validated Rekor entry: true", subject
  `…/<org>/<repo>/.github/workflows/cut-release.yml@refs/heads/main`.
- **Forecasts are pre-registered with a first-commit guard and blind emission is structural, not
  promised.** `driftwood/drift/window.yaml` opens: "**This file is the declaration, and its first
  commit is the proof it was made up front.** The harness guard
  `drift_window_was_declared_before_it_was_measured` reads this file's git history and refuses if
  any sample in `samples.jsonl` predates it." `twin/capabilities/forecast-book.yaml` criterion 2
  records that `forecast_book.py` "exposes exactly `emit`, `score_resolution`, `is_blind` — no
  function that takes a stake, a side or an order", asserted as an allow-list by a harness guard.
- **A forecast has been scored against reality and the red survived to the surface.**
  `tests/test_royal_mail_beat.py` docstring: "brier 0.9025, worse than a coin flip … these tests
  assert the red result **survives to the surface** rather than asserting it is small";
  `test_the_score_lands_poor_and_says_so` asserts `worst["brier"] > 0.25` and
  `adjusted_brier > 0.25` ("the discount rescued a forecast it should not").
- **"A green that could not look is a red" is enforced in the sample grader.**
  `driftwood/drift/five-facts.py:665-668`: a `None` fact sets verdict 3; :690-693 print
  `SKIP: a fact could not be looked at, and a fact not looked at is never a pass`. The grader also
  refuses hand-taken samples by run id, committing identity and signature.
- **Honesty of reporting is graded separately from outcome.** Run 21: `verify-e2e-step7-honesty`
  PASS with `(verdicts: PASS PASS PASS FAIL PASS PASS PASS)` — a red step 4 and a green step 7 in
  the same tally is correct, not a contradiction.

### Strongest counterexamples

**P6-1 (major, orphan).** **A green that could not look rides inside a PASS in the five-fact
sampler, today.** `driftwood/drift/five-facts.py:522-528`:

```python
ok, why = gitsign_verifies(src["tag"], identity) if src["party"] == "driftwood" else (
    None, f"{src['party']}'s own release.yml is not in this checkout, so the identity it "
          f"pins cannot be read here")
f2 = {"id": FALSIFIER_IDS[1], "fired": (ok is False), "ci_accepts": ok, "why": why, …}
```

When `ok` is `None` (could-not-look), `fired` becomes `False` — "did not fire". `grade()`'s only
could-not-look branch tests `state.get("fired") is None` (:683). I read the newest sample
(`drift/samples.jsonl`, run `33624104359`) and confirmed it live: for **platform** and **nist**,
`fired: false` with `ci_accepts: null`. The code's own comment three lines above says this must
never happen: "`fired: null` is could-not-look, not 'did not fire' … a falsifier nobody ran is
exactly the state that must never ride along inside a PASS."

**P6-2 (major, orphan).** **The provenance check reports a real, Rekor-verified signature as
absent, and still passes.** Run 21's `verify-e2e-step6-provenance` capture ends
`ok no signed tag yet, honestly queued for cut-release.yml: feeds` and `PASS: … 7 of 8 anchored
identity regexps matched`. But feeds has two gitsign-signed tags and I verified one against Rekor
(above). Cause: `verify/e2e/verify-e2e-step6-provenance.sh:87` uses
`git -C "$ESTATE/$u" tag -l 'v*.*.*'`, a glob that cannot match feeds' namespaced
`threat-register/v2.0.0`. The same glob makes the check verify **platform's `v2.0.1`** rather than
the policy line's `policy/v4.0.0` — the tag the whole §4 story turns on. This is a **new** finding:
REVIEW-2026-08-31 M1 said feeds had zero tags, which was true then and is false now.

**P6-3 (major, owned).** driftwood's `twin/forward-intel/v1/feed.json` — whose numbers carry the
second-largest £ line in driftwood's signed evidence (`{"source":"twin", … "amount":1897646.11}`) —
is **in no tag at all**. `git ls-tree -r --name-only v1.1.0 | grep -c twin/forward-intel` → `0`;
`git tag --contains <the feed's commit>` → empty. Under ADR-0019 the tag *is* the signature, so the
feed is unsigned by the estate's only signing mechanism. Owner: **ticket 64 (open)**.

**P6-4 (minor).** Step 6's line `ok 80 published artefacts resolve to a tag on the publisher's real
remote; 0 honestly queued` is not what was observed. `verify-e2e-step6-provenance.sh:35-40` counts
**every** `^PASS:` line from `feed_contract.py`, which includes envelope-schema and payload-schema
passes. Three of the 81 PASS lines in run 21's `verify-feed-contract` capture are for
`driftwood/twin/forward-intel/v1/feed.json`, an artefact that resolves to no tag (P6-3).

**P6-5 (minor).** The falsifier record carries the **wrong** `ci_pinned_identity` for platform and
nist: driftwood's own regexp
(`^https://github\.com/policy-as-versioned-driftwood/driftwood/…`), while fact 2 in the same record
correctly names each publisher's own. Confirmed by reading the sample.

**P6-6 (minor).** In driftwood's own record, fact 2 says "the controller's verdict is 'false'" (the
controller ran and rejected) while the falsifier in the same record says "the cluster verified
**nothing** at this source boundary … (ticket 41 has not landed)". `_falsifier_state` treats any
non-`True` `SourceVerified` as "verified nothing", so the recorded reason is factually wrong
whenever the controller rejects.

**P6-7 (interpretive, not a defect).** §5 resolves "a green that could not look is a red" as a third
outcome (SKIP), not as a red. Run 21 has 18 SKIPs, i.e. 18 things the estate cannot look at that are
neither green nor red on the headline number. That is the estate's own written reading and I do not
grade it as a shortfall — but the principle's own words say "red", and only the owner can say which
governs.

**Verdict: the signature spine is real and I re-derived it independently in four orgs; the forecast
machinery is pre-registered, blind, scored, and honest about a red result. The falsifiability
apparatus has two live holes where an absence of evidence is recorded as evidence of absence, and
the provenance check under-reports the estate it is meant to prove.**

---

## Principle 7 — Flux is the distribution arm, held integral unless disproven.

### The falsification test, as re-scoped

REGRILL 1 (owner, 2026-08-27): "Re-scope: **can a publisher's signed policy be proven in force
inside a consumer org, continuously, across an org boundary.** Drop the drift-floor test."

That re-scope **is** written down and instrumented. `driftwood/drift/window.yaml` carries a second,
separate pre-registration under `five_fact_sample:` — `declared_on: '2026-08-28'`, five named facts,
three named falsifiers with their firing conditions, a coverage floor of 0.9, and an operation
section that says a hand-taken sample "is a REHEARSAL (ADR-0023, D4). It is not appended to this log
and it is never cited." It was committed before the first sample; the guard reading the file's first
commit still holds.

### Strongest evidence it holds

- **On run 21, all five facts are true for both publishers, across a real org boundary, on an
  ephemeral cluster reconciling the real remotes.** From
  `talk/captures/.estate-clone_driftwood_verify-reconcile.out`:
  `nist true fact_2 … verified at the source boundary against nist's own pinned identity
  ^https://github\.com/policy-as-versioned-nist/nist/…`; `platform true fact_2 … v2.0.1 …`;
  `fact_4 all 16 rendered objects are live and equal to the offline render`;
  `fact_5 all 16 rendered objects appear in a Flux inventory`.
- **Fact 5 is the fact that earns the claim.** `window.yaml`: "This is the fact that separates 'Flux
  put it there' from 'somebody ran kubectl apply', and it is the reason facts 4 and 5 are two facts
  and not one."
- **Fact 4 declares its own ceiling** (`declared_equal`, not byte identity, with `strict_equal`
  recorded per object for the reader) rather than quietly weakening.
- **The workflow refuses to look at the wrong cluster** and says why: the local `kind-driftwood`
  reconciles from an in-cluster seeded git server, "so fact 1 … is observed FALSE there by
  construction and the run would prove nothing about an org boundary"
  (`driftwood/.github/workflows/drift-sample.yml:11-17`).

### Strongest counterexamples

**P7-1 (major).** For the two publishers, **fact 3 is not a reconciliation observation at all**. The
sample's own text: "platform is a verified source only (ticket 16 Q5): no Kustomization reconciles
it, so the revision in force is the parent sha the composed set was built from. HEADER 533dccb0a823
vs pin 533dccb0a823." So the cross-org claim is a *chain* — publisher tag verified at the boundary,
composed set built from that sha, composed objects in force — not a direct observation of a
publisher's policy in force inside the consumer. This is honestly stated in the artefact and was a
deliberate design choice (ticket 16 Q5, provisional on a bare agree). Whether it satisfies REGRILL
1's sentence is the owner's call, not mine.

**P7-2 (major, orphan).** **The sample proves 16 policy objects in force and no workload inside
them.** See P2-5: driftwood's only pod is behind a `path: ./apps` that does not exist in its tree,
and tuppence/ludlow have no pod at all. §4 step 4's "The workload keeps running, caged tighter"
therefore has no subject on any citable run.

**P7-3 (minor).** The coverage failure mode of the retired instrument is accruing again on the new
one. The original state-drift window (opens 2026-08-07, closes 2026-11-06, cadence hourly) has
**3 samples** in `drift/samples.jsonl`, all from 2026-08-10/11/13 — the floor is unreachable and the
owner has recorded that rather than restarting it. The five-fact instrument declares a 1440-minute
cadence and the same 0.9 floor, and has **3 sample runs** (33556795181, 33558850420, 33624104359)
since declaring on 2026-08-28. Its falsifier 3 fires only "at the close of the measurement", so
nothing goes red today, and nothing warns.

**P7-4 (minor, owned).** The one FALSE fact on run 21 is driftwood's **own** composed tag signature,
not a Flux fault: `v1.1.0: … certificate verify error: certificate is not yet valid` — a verifier
clock-skew defect. Owner: **ticket 73 (open)**.

**Verdict: the re-scoped test exists, is pre-registered, is instrumented, refuses rehearsals, and
produced its first real cross-org green for both publishers on the citable run. It proves the
composed cage spec in force; it does not yet prove a publisher's own artefact reconciling, or any
workload running inside the cage, and its own coverage floor is quietly repeating the failure the
predecessor instrument recorded.**

---

## What is genuinely done and proven, in one list

1. `policy/v4.0.0` — a real release whose number the gate computed before the tag, with a signed
   evidence file naming its own coverage limits, verified by me against Rekor (tlog 2664927495).
2. The cage ladder, tighten-only, four rungs, in the served copy every adopter composes from, with
   `hostNetwork`/`hostPID`/`hostIPC` clobbered shut for a reason found live.
3. The five-fact cross-org sample: pre-registered before sample one, three falsifiers named,
   rehearsals refused by run id and signature, and both publishers observed five-of-five true on
   the citable run.
4. One currency, one perspective per list, proportionality computed (`£21107` Audit in driftwood,
   Deny in ludlow), and two independent selection engines cross-checked at every band boundary.
5. Twenty clocks, every scheduled job structurally proven unable to stage a declaration or mint a
   signed artefact, with the observation lane declared once as data and read by both sides.
6. A forecast scored against reality and reported red (Brier 0.9025) with tests that refuse to let
   the red be tuned away.
7. No exemption mechanism anywhere in eight repositories.

## Fitness

Against §3 as written, the estate is **fit in the two principles that have engines (3 and 4) and
in the honesty machinery of 6; partly fit in 5 and 7; not yet fit in 1's conditional arm and in 2
beyond pods.** The pattern is consistent and worth naming: wherever the estate built an *engine*, it
built it to an unusually high standard and instrumented its own drift; wherever the estate needed a
*subject* for that engine — a second policy line, a workload under Flux, a caged human, a fired
proposal — the subject is missing, and the number goes green anyway because the check honestly
SKIPs. The gate is not lying; it is measuring an estate whose engines outrun its inhabitants.
