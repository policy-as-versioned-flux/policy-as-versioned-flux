# Demo feedback — reasoned conclusions (pre-grilling)

My own verdicts on NOTES.md, formed before grilling. Per-item verdict + rationale, then the
synthesis into themes and a sequence. Items marked *(research pending)* have a background
fact-check in flight; conclusions there are provisional on the stated assumption.

## Per-item verdicts

**1. Split apps into per-app repos — ENDORSE, medium priority (as part of Theme A).**
The apps monorepo is a demo shortcut that misrepresents the topology the thesis is *about*:
"consumable" means each team opts in from their own repo, on their own cadence. A monorepo hides
the coordination cost the design claims to survive. Splitting gives three independently-reconciled
GitRepositories and — decisive once item 14 lands — three distinct Renovate dependency surfaces,
one per team, which is the realistic signal shape. Cost is small (2 repos, 2 GitRepository
objects, apps.yaml becomes three entries).

**2. Signed-message block in release notes — ENDORSE, but STRIP rather than fence.**
Fencing preserves noise. The signature's home is the tag object (that's what `gitsign verify-tag`
checks) and the release page already shows Verified; the PEM block in prose is pure clutter.
Fix in `release.yml`: take `%(contents)` only up to the `-----BEGIN SIGNED MESSAGE-----` marker
(or use subject+body formats). One-line sed. Trivial.

**3. Release artifacts — ENDORSE-SMALL, tightly scoped, low priority.**
Tension: ADR-0001 makes git-the-tag the *only* transport; release assets risk becoming a second,
divergent consumption path. But "regenerable ≠ recorded" (ADR-0008): a rendered-manifests bundle +
SHA256SUMS, generated in the same CI run that verified the tag, is audit *evidence*, not transport.
Scope: rendered per-policy kustomize output + checksums, with an explicit "not for consumption —
consume the tag" note. SBOM is overkill for YAML. Reject anything beyond that.

**4. History rewrite / repo recreation — RECOMMEND AGAINST. Offer alternative.**
Three reasons, in strength order:
- It contradicts the project's own load-bearing ethos, applied consistently all session: v1.0.0's
  failed CI kept, v2.0.0's SSH-signing mistake kept, v1.0.2/v2.0.2 kept. The "thrashing" commits
  ARE the evidence that the gates catch real bugs. ADR-0001's audit-trail property rides on
  history being append-only.
- Practical breakage: the dashboard's adoption-velocity panel literally displays fleet PR history
  from GitHub's API — recreating the repo empties it. Hub-tracker comments reference PR numbers
  that would dangle. And any temptation to extend the rewrite to the *policy* repo is a hard no:
  fleet pins policy by commit SHA and Rekor tlog entries attest those exact commits.
- The legitimate need underneath ("presentable/learnable for newcomers") is served better by a
  curated `docs/HISTORY.md` narrative + the squash-merge discipline already in place.
If the user still wants it after grilling: fleet-only, never policy, and it needs its own
dedicated confirmation. My recommendation remains no.

**5. Gate version cross-check — ENDORSE, DO FIRST. Highest priority item on the list.**
A correctness hole in the exact trust chain ADR-0001 exists to protect. Fix (~10 lines in
`pr-gate-check.sh`): after cloning the tag, `kustomize build` one policy and assert the rendered
`mycompany.com/policy-version` label equals the array's declared `version`. Subtlety that makes
this correct for CI-only-fix patches (where version ≠ tag by design, e.g. 1.0.0 @ tag v1.0.3):
the assertion compares against the *rendered content's* internal version — which is exactly what
stays `1.0.0` — not the tag string. Cheap, closes a real spoofing path, no design questions.

**6. Extract gate into reusable Action — DEFER (YAGNI today).**
Exactly one consumer exists (fleet; cluster2 lives in the same repo; apps repos don't pin tags so
they'd never use it). An extracted action also becomes its own governed dependency needing its own
release/pinning discipline — philosophically consistent with the thesis, and a nice story *when
there's a second consumer*, but premature now. Revisit when a second config repo appears.

**7. Checkbox follow-through Action — ENDORSE, medium priority.**
Design: Action in the policy repo on `issues.edited` for `agent-governance-review` issues; detect
which box got ticked; react with comment + label only (`awaiting-defence-pr` / `awaiting-change-pr`
/ `needs-discussion`). Never touches policy content — preserves the ADR-0007 invariant by token
scope, same as the agent itself. A periodic stale-reminder is fine too: ADR-0006 rejects timed
*enforcement changes*, not timed *nudges to humans*. Natural growth of issue 24's demonstrator.

**8. Grafana anonymous auth — ENDORSE, trivial.** `grafana.ini` auth.anonymous in the
HelmRelease values. Viewer role suffices for the dashboard; it's localhost KiND either way.

**9. "Supported versions" panel — ENDORSE, trivial.** One stat/table panel off
`gotk_resource_info{customresource_kind="GitRepository", name=~"policy-.*"}`. High demo value
per unit effort.

**10. Update-readiness view — ENDORSE, real design work, high strategic value.** *(research pending)*
The subtlety: Kyverno background scans only evaluate *installed* policies against *opted-in*
workloads — a 1.0.0-labelled pod is never evaluated by 2.2.0's policies (matchConditions excludes
it), so readiness data doesn't exist for free. Two options considered:
- (a) Shadow-install candidate policies with broadened matchConditions, Audit-only — rejected:
  adds a fourth hand-synced literal and pollutes live PolicyReports with hypotheticals.
- (b) **A readiness-collector CronJob** (same idiom as `c2p-collector`): dump live workloads,
  render the candidate version's policies with the version-scope matchCondition *stripped*
  ("evaluate everyone as if opted in"), run `kyverno apply` offline, publish counts to a
  ConfigMap → infinity panel. Chosen, pending one fact-check: kyverno CLI's support for
  `ValidatingPolicy` (policies.kyverno.io/v1) in `apply` against dumped cluster resources.
This answers the CIO question the current dashboard actually can't: "when can we retire X /
adopt Y" — arguably the missing fourth answer, and it operationalizes the thesis's payoff.

**11. Admission-only semantics doc — ENDORSE, trivial, with the good framing.**
State it as: retirement never evicts; a retired-version workload keeps running until its next
recreation, at which point the orphan guard refuses it — *governance debt becomes visible at the
next churn*. README + a text panel on the dashboard.

**12. Sunset times — RECONCILABLE with ADR-0006 via one reframe: scheduled *proposals*, never scheduled *application*. Needs a new ADR.**
ADR-0006 rejects timed enforcement changes (no bot flips Audit→Deny, no expiry deletes). But
ADR-0002 already sanctions a bot (Renovate) *opening PRs* that change the fleet array — the
preserved invariant is "never automerged", not "never machine-initiated". So: a `sunset:` field on
the **fleet array entry** (adoption-scoped — NOT in the immutable policy release, since sunset is
a fleet's adoption decision, not a property of the version itself), dashboards show
time-to-sunset, the governance agent opens escalating issues as it nears, and at the date a
machine opens a *retirement PR* that a human must merge. Nothing timed ever applies. This needs a
short ADR because it deliberately extends ADR-0006's boundary — do not slip it in as a feature.

**13. Renovate now live — three follow-ups.** *(research pending)*
(a) Verify whether `config:recommended` already includes the dependency dashboard (believed yes in
current Renovate — if so it appears on first scan, nothing to do); (b) expect onboarding PRs on
the repos without a renovate.json (policy, apps, governance-agent, hub, cloud) — decide per-repo
config rather than letting defaults sprawl, possibly via an org-level config repo; (c) **the free
win**: the next signed policy tag now produces a real, live Renovate PR against fleet — closing
the one checklist item in issue 11 that was only ever fixture-proven. Watch for it; no work needed.

**14+15. Real apps, real stale dependencies, aggregate staleness dashboard — STRONG ENDORSE. The biggest and best new workstream.**
This *strengthens the core metaphor* rather than bolting on scope: the thesis says a policy
version is a dependency like any other — so put real dependencies next to it and show both kinds
of staleness in one estate view. Shape: per-app repos (item 1) each with a small real app on
deliberately old deps (old Angular for one, a Log4Shell-era Java app for another — it's KiND on
localhost, running it is the point); Renovate gives per-team update signal; an in-cluster scanner
(trivy-operator, believed to emit Prometheus metrics natively — *(research pending)*) gives
vulnerability/staleness metrics; one aggregate dashboard joins app-dependency staleness with
policy-version staleness. Items 1, 14, 15 are one workstream, not three tasks.

**16. Flux vs Renovate — CLOSED.** Answered live, app installed. One residual: confirm live
Renovate doesn't fight the design (config already pins exact + never automerges — it won't).

## Synthesis — themes and sequence

- **Theme B — trust-chain gaps (first, cheap):** item 5 now; item 13's live-PR proof arrives free.
- **Theme D — polish trio (first, trivial):** items 2, 8, 9 (+11's doc note).
- **Theme A — make the consumer story real (biggest value):** items 1+14+15 as one workstream.
- **Theme C — operationalize retirement (most strategic):** items 10 (readiness CronJob),
  12 (sunset ADR), 11 (semantics framing). This is where the thesis pays off for the CIO.
- **Theme E — governance follow-through:** item 7.
- **Pushback:** item 4 (recommend against, alternative offered), item 6 (defer, YAGNI).

Sequence: B+D (one short pass) → A → C → E. Item 4 only ever moves with its own explicit
confirmation; item 12 only via a new ADR.
