# Show & Tell — Policy as Versioned Code, on Flux

A live-demo runbook. The thesis in one line: **treat a body of governance policy like a software
dependency** — semantically versioned, signed, pinned, distributed, unit-tested, and updated by
reviewed PR — *not* primarily a deploy-time gate. The talk's scorecard is the seven **-ables**:
visible · communicable · consumable · testable · usable · updatable · measurable. Every beat
below maps to one.

Everything here runs **live** against the local KiND estate — no slides standing in for a thing
that doesn't work. Commands are copy-paste ready.

---

## 0. Pre-flight (do before the audience is watching)

```sh
kubectl config use-context kind-cluster1
# Grafana is anonymous-Viewer (no login mid-demo). Leave this running in a spare pane:
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80
# open http://localhost:3000  -> Dashboards: "Estate staleness", "Flux policy versions"
```

Reset check — the estate should show three versions and four apps, all Ready:

```sh
kubectl get gitrepository -n flux-system | grep policy      # policy-1.0.0 / -2.0.0 / -2.2.0, all True
kubectl get pods -n default | grep -E 'ledger|reports|api|storefront'   # 4x Running
```

If `verify-*.sh` scripts were run recently, they self-clean; if anything looks off, re-run
`fleet/up.sh` (idempotent).

---

## 1. The move: policy *is* a dependency  (visible)

> "This isn't a policy engine with some git on the side. It's a dependency graph. Three versions
> of the policy 'library' are installed on this cluster right now, side by side."

```sh
kubectl get gitrepository -n flux-system | grep policy
```

Three `GitRepository` objects, each pinned to a **signed tag + commit** of the same policy repo —
`v1.0.3`, `v2.0.3`, `v2.2.0`. On screen: Grafana **"Supported policy versions on this cluster"**
stat panel shows the same three, read straight from `gotk_resource_info` (a policy version is just
another dependency Flux reports on).

Show the pins are real and signed:

```sh
kubectl get gitrepository policy-2.2.0 -n flux-system \
  -o jsonpath='{.spec.ref.tag}  @  {.spec.ref.commit}{"\n"}'
# the tag object itself carries a gitsign (keyless, Rekor-logged) signature — ADR-0001
```

---

## 2. Coexistence & consumption: teams opt in, per-version  (consumable)

> "Four teams, four repos, four cadences. Each pins the version it's ready for — nobody is
> force-marched to the latest."

```sh
kubectl get pods -n default -L mycompany.com/policy-version \
  -l 'app in (ledger,reports,api,storefront)'
```

- `ledger` → **1.0.0** (the deliberate laggard: Log4Shell-era deps, oldest policy)
- `reports` → **2.0.0**
- `api`, `storefront` → **2.2.0** (the good citizens)

Each is its own `GitRepository`+`Kustomization`, reconciled independently. The policy version is a
label the workload chooses — the exact "opt in from your own repo, on your own cadence" the thesis
is about.

---

## 3. The gate is real, not theatre  (the mea-culpa's lane-keeping-vs-gate distinction)

> "Two tiers. A *lane-keeping* Audit policy nudges and reports. A *gate* Deny policy refuses at
> admission. Watch the door actually lock."

Reproduce a real admission verdict **offline, on a laptop** (this is the *usable* -able —
`docs/shift-left-dev-workflow.md` is the full walkthrough):

```sh
# a Pod pinned to 2.2.0 with a bad department label — the gate refuses it
cat <<'EOF' | kubectl apply --dry-run=server -f -
apiVersion: v1
kind: Pod
metadata: {name: demo-bad, namespace: default, labels: {mycompany.com/policy-version: "2.2.0", department: not-a-real-dept}}
spec: {containers: [{name: app, image: nginx:latest}]}
EOF
# -> denied by require-known-department-label-2.2.0
```

Then the **orphan guard** — the catch-all that turns the gate tier into a *locked door* rather than
an opt-in door. A workload with **no** policy-version label at all:

```sh
cat <<'EOF' | kubectl apply --dry-run=server -f -
apiVersion: v1
kind: Pod
metadata: {name: demo-orphan, namespace: default}
spec: {containers: [{name: app, image: nginx:latest}]}
EOF
# -> denied by orphan-guard: "must carry a mycompany.com/policy-version label matching a currently-installed version"
```

> "It denies at admission, but it never evicts what's already running — governance debt stays
> visible and only bites at the next churn. That's a deliberate ADR-0003/0006 choice."

Cloud plane, same engine: the orphan guard now also covers Crossplane CRs (a wave-1 audit fix).
Optional beat — an unlabelled RDS `Instance` is refused the same way a Pod is.

---

## 4. Updatable, safely: signed releases + Renovate + the PR gate  (updatable)

> "Updates arrive the way any dependency update does: a Renovate PR that bumps a pinned tag. And
> the PR gate refuses to let a bump lie about what version it actually is."

```sh
cd ../pavf-policy && git tag -l | sort -V | tr '\n' ' '; echo
# 11 real, gitsign-signed tags — including the honest thrash (v1.0.0's failed CI, v2.0.0's
# SSH-signing mistake, v1.0.2/v2.0.2's go-git resolution bug) kept as evidence the gates work
```

The money shot — the gate catching a **spoofed** bump (declares 2.2.1 but the tag still renders
2.2.0). This is reproducible from the `pr-gate-action` repo's `pr-gate-check.sh`; the canned result:

```
FAIL: 2.2.1/require-department-label renders mycompany.com/policy-version=2.2.0, array declares 2.2.1
== PR gate: FAIL ==   (exit 1)
```

> "The signature proves *who* cut the tag; the gate proves the tag *is what it says it is*. Both
> are in CI, pinned by digest — the gate that verifies pins is itself pinned."

---

## 5. Measurable: dashboards + real compliance attestation  (measurable · visible)

Flip to Grafana (already open, anonymous):

- **Estate staleness** — per-team policy-version *and* CVE axes. `ledger` is the laggard on
  version; the live trivy scan shows the real CVE counts (honestly: `ledger` is *not* worst on
  CVEs — `reports`/`storefront` are higher; kept as the genuinely-interesting finding it is).
- **Flux policy versions** — the supported-versions panel + admission-only-semantics text panel.

Real OSCAL/NIST compliance attestation, generated on-cluster every 15 min (ADR-0009, C2P):

```sh
kubectl get configmap oscal-assessment-results -n monitoring \
  -o jsonpath='{.data.assessment-results\.json}' \
  | jq '.["assessment-results"].results[0].findings[] | select(.target["target-id"]=="cp-10_smt") | .target.status'
# -> not-satisfied, attributed to datastore's own non-compliant RDS claim (a wave-2 audit fix:
#    it used to mis-attribute to an unrelated fixture)
```

---

## 6. Sunset: scheduled *proposals*, never scheduled *application*  (ADR-0010)

> "Retirement is a business decision framed as a PR a human merges — never a machine silently
> pulling the rug. The governance agent watches the sunset dates and escalates."

```sh
gh issue view 30 --repo policy-as-versioned-flux/fleet   # live escalation issue for 1.0.0's 2026-08-15 sunset
```

A daily GitHub Actions workflow runs the escalator unattended (three real runs on the record).
**Known caveat, state it plainly:** the retirement-*PR* path (fires on the sunset date itself) is
fixed end-to-end except for one org setting — "Allow GitHub Actions to create and approve pull
requests" — which is OFF org-wide and needs an admin toggle. The daily *escalation-issue* path
works unattended today. (See `.scratch/real-estate/issues/09-*.md` for the full, honest diagnosis.)

---

## 7. The honest footer: what an adversary found, and the one real known-issue

This estate survived repeated adversarial multi-agent audits (5 waves this session). Worth saying
out loud, because it *is* the thesis in action — the gates and the audit trail catch real bugs:

- Real bugs found & fixed live: OSCAL mis-attribution, the orphan guard not covering cloud CRs, a
  vacuously-passing verify script, a 3-years-latent broken rationale-link in every policy, a spike
  leaking test resources onto the shared cluster (now hard-guarded).
- One honestly-recorded **known upstream issue**: `flux-operator`'s ResourceSet controller
  occasionally flaps `policy-1.0.0`'s derived objects (self-heals, never observed to admit a
  non-compliant workload). Documented, not papered over — `.scratch/real-estate/issues/16-*.md`.
- One **needs-an-admin** step: the sunset retirement-PR org toggle above.

> "Nothing here is rounded up to 100%. The parts that work, work live; the two things that don't
> are named, scoped, and one toggle / one upstream bug away — which is exactly the honesty the
> whole thesis is arguing for."

---

### Appendix — reset / teardown

```sh
./up.sh     # idempotent bring-up (fleet repo)   — ~3-5 min cold
./down.sh   # kind delete cluster
```
Grafana anonymous access, the port-forward, and all four apps come back automatically on `up.sh`.
