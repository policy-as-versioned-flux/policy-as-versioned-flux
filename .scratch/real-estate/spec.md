# real-estate — making the estate real

**Status:** ready-for-agent

Born from the show+tell demo feedback (2026-07-16): raw notes in
[`../demo-feedback/NOTES.md`](../demo-feedback/NOTES.md), pre-grilling analysis in
[`../demo-feedback/CONCLUSIONS.md`](../demo-feedback/CONCLUSIONS.md). Every decision below was
grilled with the user branch-by-branch and confirmed.

## Problem Statement

The faithful-floor epic proved the *mechanism* — versioned policy, coexistence, retirement, both
planes, measurable/communicable/updatable — but the demo exposed that the estate around the
mechanism is a cardboard cutout. The consumer apps are three identical nginx pods in one monorepo,
so nothing demonstrates real teams on real cadences with real dependencies; the cloud resources
are planted by the platform rather than requested by a team; reusable machinery (the PR gate, the
OSCAL collector, the handbook generator) is buried inside the repos it happens to have grown in;
the CIO dashboard can say what *is* but not what's *coming* (no update-readiness, no sunset
horizon); the trust chain has one confirmed hole (declared version vs rendered content never
cross-checked); the governance loop's human decision (the issue checkboxes) has no follow-through
tracking; and Renovate — the entire "updatable" story — only ever ran against local fixtures until
the user installed the real app mid-demo. A viewer can't tell whether this design survives contact
with a realistic estate, because there isn't one.

## Solution

Make the estate real and let the existing mechanism prove itself against it. Five real app teams
in five repos, with real stacks, deliberately mixed dependency hygiene, and one team owning the
cloud-plane claims. Extract every reusable component into its own versioned, pinned repo — the
componentization the thesis itself implies (a component is a dependency like any other). Close the
gate's version cross-check hole. Give the CIO the forward-looking answers: an update-readiness
view and a sunset story that schedules *proposals*, never *application* (a new ADR extending
ADR-0006's boundary deliberately, not silently). Wire the live Renovate service in behind an
org-level preset. Add follow-through tracking to the governance checkboxes without ever touching
policy content. One new dashboard joins the two kinds of staleness — policy versions and app
dependencies — into a single per-team estate view, which *strengthens* the core metaphor: a policy
version is just another dependency.

## User Stories

1. As a CIO, I want one dashboard row per team showing policy-version staleness and dependency staleness together, so that I can see which teams are behind on everything at a glance.
2. As a CIO, I want an explicit "supported policy versions on this cluster" stat, so that I don't have to infer it from a revision table.
3. As a CIO, I want an update-readiness view showing which workloads would fail under the next policy version, so that I know when the estate can move before anyone flips anything.
4. As a CIO, I want each adopted policy version to carry a visible sunset horizon, so that retirement is a plan with a date rather than an event that surprises teams.
5. As a platform engineer, I want the sunset date to produce escalating governance issues and, on the day, a machine-opened retirement PR that a human must merge, so that retirement is prompted on schedule but never applied on schedule.
6. As a platform engineer, I want the PR gate to reject a bump whose declared version doesn't match the tag's rendered content, so that the array can't silently lie about what a tag contains.
7. As a platform engineer, I want the PR gate consumed as a versioned, pinned Action, so that the gate itself is governed like any other dependency.
8. As a platform engineer, I want the OSCAL collector as a prebuilt, digest-pinned image instead of a build-from-source-each-run job, so that collection is fast and its supply chain is pinned.
9. As a platform engineer, I want an org-level Renovate preset with onboarding suppressed, so that fourteen repos share one update policy without onboarding noise.
10. As an app team developer, I want my app in my own repo with my own reconcile cadence, so that my adoption decisions are mine and visible as mine.
11. As an app team developer, I want Renovate PRs against my repo's real dependencies, so that staleness is surfaced to me where I work.
12. As an app team (datastore), I want to request cloud infrastructure by committing Crossplane claims in my own repo under my policy version, so that cloud resources are team-requested, not platform-planted.
13. As a policy author, I want release notes without a wall of PEM, so that the narrative is readable at a glance.
14. As a policy author, I want each release to carry a rendered-manifests bundle and checksums as evidence, so that an auditor can see exactly what the tag renders to without running kustomize.
15. As an auditor, I want the evidence bundle explicitly marked non-consumption ("consume the tag"), so that no second transport path emerges beside ADR-0001's.
16. As a security engineer, I want a scanner surfacing vulnerability counts for the deliberately-stale apps (Log4Shell-era ledger, old-Angular storefront), so that dependency risk is measured, not anecdotal.
17. As a compliance owner, I want to reach the dashboards without a login on demo clusters, so that a walkthrough never stalls at an auth screen.
18. As a reviewer of governance issues, I want ticking a checkbox to produce a label and an acknowledging comment, so that my decision is tracked without any bot touching policy content.
19. As a reviewer, I want a weekly nag on checked-but-unactioned governance issues, so that decisions don't silently rot — a timed nudge to humans, never a timed enforcement change.
20. As a newcomer, I want the admission-only semantics stated prominently (retirement never evicts; governance debt surfaces at next churn), so that I don't assume policy updates stop running workloads.
21. As a newcomer, I want a curated history narrative, so that I can learn the project's story without archaeology through the thrashing commits — which stay, as the audit trail.
22. As the governance agent, I want sunset proximity as a signal source, so that my escalating issues extend the existing ADR-0007 contract rather than needing a new one.
23. As a fleet operator, I want retiring a version from a cluster's array to remain a one-line reviewed change, so that everything new in this epic preserves the retirement-without-a-flag-day property.
24. As the project owner, I want the eventual two-org separation (components org / model org) and fresh-org redeploy recorded as deferred decisions, so that today's single-org choice doesn't harden into an accident.

## Implementation Decisions

- **Five app repos, descriptive names, replacing the `apps` monorepo (archived, never deleted):**
  `storefront` (old Angular static build behind nginx, npm ecosystem, very stale, policy 2.2.0);
  `ledger` (Java with Log4Shell-era log4j 2.14, run live on KiND — deliberate; policy 1.0.0, the
  laggard whose old deps correlate with old policy); `reports` (Python/Flask, moderately old,
  policy 2.0.0); `api` (Go, current, policy 2.2.0 — the good citizen); `datastore` (owns the
  Crossplane claims, which move out of fleet's platform-planted c2p directory; policy 2.2.0).
  Fleet gains one GitRepository+Kustomization pair per app.
- **Full componentization now:** the PR gate becomes a composite GitHub Action in its own repo,
  versioned and pinned by fleet; the c2p-collector gets its own repo and a real container image
  (org registry, digest-pinned in the CronJob, Renovate-maintainable); the readiness-collector is
  born as its own component; the handbook generator moves out of the policy repo. Each component
  carries its own runnable self-check. Two-org separation (components org / model org) is
  deferred and recorded.
- **Gate version cross-check:** the gate renders the fetched tag and asserts the rendered
  policy-version value equals the array's declared `version` — rendered content, not tag string,
  so CI-only-fix patches (version ≠ tag by design) remain valid.
- **Sunset = scheduled proposals, never scheduled application (new ADR before implementation):**
  a `sunset:` date on fleet array entries (adoption-scoped, never in the immutable release);
  dashboard countdown; governance-agent escalation issues as it nears; on the date a machine
  opens a retirement PR that a human must merge. Nothing timed ever applies. The ADR states this
  as a deliberate extension of ADR-0006's boundary, leaning on ADR-0002's precedent
  (machine-opened PRs are sanctioned; the invariant is "never automerged").
- **Checkbox follow-through:** an Action on governance-review issue edits reacting with comment +
  label only (`awaiting-defence-pr` / `awaiting-change-pr` / `needs-discussion`), plus a weekly
  stale nag. Never writes policy content — ADR-0007's invariant preserved by construction.
- **Release evidence assets:** rendered per-policy manifests + SHA256SUMS, generated in the same
  CI run that verifies the tag, explicitly marked non-consumption. No SBOM. Release notes strip
  the PEM signed-message block (the tag carries the signature).
- **Renovate:** org-level preset repo (pin exact, no automerge, dependency dashboard on),
  onboarding suppressed org-wide; repo-specific managers (fleet's git-refs customManager) stay
  local. The Mend-hosted app is already installed on the org.
- **Estate staleness = a new, second dashboard** (same ConfigMap/sidecar mechanism): one row per
  team joining policy-version staleness (+ sunset countdown), dependency staleness, and
  vulnerability counts. The existing CIO dashboard stays one-question-shaped and gains only the
  supported-versions stat and the admission-semantics note.
- **Update-readiness (mechanism parked on in-flight research):** an offline collector that
  evaluates live workloads against a candidate version's policies with the version-scope
  matchCondition stripped ("as if opted in"), publishing per-team pass/fail counts. Primary
  mechanism `kyverno apply` if it supports the CEL ValidatingPolicy kind; fallback is
  programmatically-generated `kyverno test` fixtures (known to work). Never touches admission; no
  shadow policies installed.
- **Scanner (choice parked on in-flight research):** trivy-operator if it natively emits
  Prometheus vulnerability metrics with ServiceMonitor support; otherwise nearest equivalent.
- **Grafana anonymous auth** on demo clusters.
- **No history rewrite, ever, in place:** the endgame for "clean history" is a from-scratch
  redeploy into a fresh org when the epic completes — a replay proving reproducibility, with the
  current org kept as the audit trail. A curated history narrative document serves newcomers
  meanwhile.

## Testing Decisions

Good tests here assert externally-observable behaviour at the four established seams, never
implementation details: (1) **live-cluster verify scripts** — the highest seam; every new
behaviour (gate rejection, sunset proposal PR, readiness counts, estate dashboard rows) gets a
runnable check against the real KiND clusters, in the style of the existing `verify-*.sh` suite;
(2) **PR-gate CI** — the cross-check is proven by a synthetic mismatched PR being rejected, the
same proof pattern the gate's original force-moved-tag test used; (3) **per-component
self-checks** — each extracted repo carries its own runnable check, the established spike idiom;
(4) **Grafana query API** — dashboards are verified by querying panels through `/api/ds/query`
and asserting real rows, the pattern established when the CIO dashboard shipped. One new seam is
accepted: **live Renovate**, observable but not controllable (trigger by pushing tags/deps, then
poll for the PR); anything not provable there falls back to the existing fixture dry-run seam.

## Out of Scope

- The two-org separation (components org / model org) — recorded, deferred until the epic is done.
- The fresh-org redeploy itself — it's the epic's *sequel*, not a ticket in it.
- Any history rewrite or repo deletion (old `apps` repo is archived, not deleted).
- SBOM generation.
- Automatic application of anything timed — sunset produces proposals only.
- Cross-cluster Prometheus (Thanos/federation) — unchanged from faithful-floor's open question.
- Real cloud credentials — the cloud plane stays KiND-only, admission + claims, no reconciliation.

## Further Notes

- Two in-flight fact-checks gate two decisions: `kyverno apply` support for CEL ValidatingPolicy
  (readiness mechanism), and trivy-operator's native Prometheus metrics (scanner choice). Both
  tickets carry the fallback so the research result resolves them without another decision round.
- The live Renovate install means the next signed policy tag should produce the first real
  Renovate PR against fleet — closing the one faithful-floor checklist item (issue 11) that was
  only ever fixture-proven. Free win; watch for it.
- Passes agreed at grilling: (1) opening pass + sunset ADR → (2) extractions + Renovate preset →
  (3) app repos + fleet wiring → (4) readiness + scanner + estate dashboard → (5) checkbox
  Action + release assets + history narrative.
