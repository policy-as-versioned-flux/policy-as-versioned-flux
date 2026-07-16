# How this got here

A newcomer's guide to the project's story, not its architecture — see [CONTEXT.md](../CONTEXT.md)
and [docs/PRD.md](PRD.md) for that. Every episode below links to the real commits, PRs, and tags
that lived it. The raw history — including the thrashing, the wrong turns, the fixes to the
fixes — is untouched and stays that way (see [Deferred decisions](#deferred-decisions) below):
this document is a map drawn over it, not a replacement for it.

## Why this exists

Chris Nesbitt-Smith's 2022 conference talk, *Policy as [Versioned] Code*, and the "mea culpa"
follow-up blog post argued a specific, narrow thing: policy — the rules that mitigate risk — should
be treated like any other software dependency: versioned, distributed, tested, updated by reviewed
pull request. The mea culpa corrected the talk's own overreach: not everything should be a hard
admission gate ("a locked door"); most of an enterprise's real policy surface is *lane-keeping*,
continuous corrective guidance, and a system that only knows how to say "no" repeats the original
mistake. This repo re-implements that corrected thesis faithfully, on Flux CD, as a real,
runnable, live-verified system — not a slide deck. `research/` holds the source material this all
traces back to.

## Episode 1: the floor (faithful-floor epic)

The first phase proved the mechanism itself: one Kyverno-engine cluster, multiple policy versions
coexisting side by side, adopted via a reviewed Renovate PR, retired without a flag day. Twenty-six
tickets, `.scratch/faithful-floor/issues/` in this repo.

**The webhook-flattening discovery.** The original design self-scoped each policy version to its
own workloads via `matchConstraints.objectSelector`. It looked right in isolation and was wrong in
production: Kyverno flattens every installed `ValidatingPolicy`'s `objectSelector` onto one shared
Kubernetes `ValidatingWebhookConfiguration` — only the most-recently-reconciled version's selector
survived, silently. Single-version deployments never surface this; multi-version coexistence (the
whole point) breaks immediately. Found live, fixed by moving version-scoping into a `matchConditions`
CEL expression evaluated *inside* Kyverno instead of the shared webhook:
[`policy@1466fdc`](https://github.com/policy-as-versioned-flux/policy/commit/1466fdc). See
[ADR-0003](adr/0003-kyverno-validatingpolicy-cel.md).

**The go-git tag-resolution saga.** Two tags (`v1.0.2`/`v2.0.2`) were cut, signed, and correct —
and Flux's `source-controller` (built on `go-git`) refused to resolve them:
`unable to resolve commit object ... object not found`, even though `git clone --branch` resolved
the identical tag fine. Root-caused live (not from documentation) by a delete/restore test: the
commits, made via `git worktree` from an older tag's detached HEAD, were never reachable from any
branch — a documented `go-git` shallow-fetch-by-tag limitation
([fluxcd/source-controller#1166](https://github.com/fluxcd/source-controller/issues/1166)), not a
broken tag. Fixed two ways at once in `v1.0.3`/`v2.0.3`: a fresh commit plus a permanent branch ref
(`policy`'s `release-pins/v1.0.3`/`release-pins/v2.0.3` — load-bearing infrastructure, confirmed by
testing that deleting either branch breaks resolution again, not cleanup candidates). See
[`fleet@99971a8`](https://github.com/policy-as-versioned-flux/fleet/commit/99971a8).

**A signing mistake, corrected in the open.** The first fix attempt's own commit message
misdiagnosed the cause as SSH-signed commits (a real, but secondary, difference in those two
tags). Once the actual branch-reachability cause was confirmed live, the wrong comment was fixed
in a follow-up PR rather than quietly rewritten:
[`fleet#11`](https://github.com/policy-as-versioned-flux/fleet/pull/11), "Correct root-cause
comment: branch reachability, not SSH signing, confirmed live." Kept as an honest record, not
squashed away — the same "dated, reviewed, corrected in a PR" pattern this project asks of policy
itself.

By the end of this epic: three policy versions live simultaneously on one cluster, an orphan guard
making the gate tier a locked door (not an opt-in one), a cloud plane riding the same coexistence
matrix as the workload plane, a real Renovate `customManager` bumping the `{tag, commit}` pin, and
a CIO dashboard reading live PolicyReport + OSCAL data — proof the mechanism itself works.

## Episode 2: the show+tell, and the cardboard cutout

A narrated demo walkthrough (`.scratch/demo-feedback/`) surfaced the gap the mechanism-proving
phase couldn't see from the inside: the *estate* around the mechanism was a cardboard cutout.
Three consumer apps were identical `nginx` pods in one monorepo — no real dependency trees, no
real teams, no real cadences. The trust chain had one confirmed hole (a bump PR's declared version
was never cross-checked against what its tag actually rendered). The CIO dashboard could say what
*is* but not what's *coming*. Sixteen pieces of real feedback, captured raw
(`.scratch/demo-feedback/NOTES.md`), then grilled branch-by-branch into confirmed decisions
(`.scratch/real-estate/spec.md`) — the mattpocock-skills `grilling` → `to-spec` → `to-tickets`
pipeline, including one process correction along the way (tickets were drafted before the spec was
written; caught, the premature work discarded, redone in the right order).

## Episode 3: making the estate real (real-estate epic)

Fifteen tickets, five passes, `.scratch/real-estate/issues/`. The thesis's own logic pointed the
way: *a component is a dependency like any other*, so the pieces that had grown organically inside
`fleet` and `policy` — the PR gate, the OSCAL collector, the handbook generator — became their own
versioned, pinned repos:
[`pr-gate-action`](https://github.com/policy-as-versioned-flux/pr-gate-action),
[`c2p-collector`](https://github.com/policy-as-versioned-flux/c2p-collector),
[`handbook-generator`](https://github.com/policy-as-versioned-flux/handbook-generator),
[`readiness-collector`](https://github.com/policy-as-versioned-flux/readiness-collector) — the
gate that verifies pins is itself pinned.

The three identical `nginx` pods became five real teams, each its own repo, own reconcile cadence,
deliberately mixed dependency hygiene:
[`storefront`](https://github.com/policy-as-versioned-flux/storefront) (old Angular/npm),
[`ledger`](https://github.com/policy-as-versioned-flux/ledger) (Log4Shell-era `log4j` 2.14, the
roster's deliberate laggard), [`reports`](https://github.com/policy-as-versioned-flux/reports)
(moderately old Flask), [`api`](https://github.com/policy-as-versioned-flux/api) (current Go
deps, the good citizen), [`datastore`](https://github.com/policy-as-versioned-flux/datastore)
(Crossplane claims, team-requested instead of platform-planted). The old
[`apps`](https://github.com/policy-as-versioned-flux/apps) monorepo is archived, not deleted —
its README points forward to the five repos that replaced it.

New capability followed the new roster: a version-cross-check closing the trust-chain hole
([`fleet#19`](https://github.com/policy-as-versioned-flux/fleet/pull/19)); [ADR-0010](adr/0010-sunset-scheduled-proposals-not-application.md), sunset as a *scheduled proposal*, never a
scheduled *application* — extending [ADR-0006](adr/0006-deterministic-policy-no-time-conditions.md)'s determinism boundary deliberately, leaning on
[ADR-0002](adr/0002-adoption-pinned-plus-renovate-pr.md)'s existing "machine-opened, human-merged"
precedent; a governance-agent extension opening real escalation issues and (on the date) real,
machine-opened, never-machine-merged retirement PRs; an offline readiness collector answering "would
the estate pass the next policy version today?" without ever touching admission; a vulnerability
scanner giving the roster's dependency staleness a real Prometheus signal; and a second dashboard
joining both kinds of staleness — policy version and dependency version — into one estate view per
team, because a policy version *is* just another dependency.

Several real bugs were found and fixed live along the way, not glossed over in hindsight:
`kyverno apply` silently producing nothing against a `kind: List`-wrapped resource file; a
`trivy-operator` scan job OOMKilled on a shaded Java jar and a single-node cluster's concurrent
scan jobs colliding on a cache lock; a Kubernetes `subPath` mount colliding with a sibling
ConfigMap's own directory mount; a bash-only `<<<` heredoc silently crashing a container whose real
shell was busybox `ash` *after* its actual work had already succeeded. Each is recorded in its
ticket's own comments, not smoothed over.

## Deferred decisions

Two decisions were named explicitly during grilling and deliberately not acted on in this epic:

- **The two-org split** (a components org holding the reusable pieces, separate from a model org
  that only consumes them) — the componentization above is real, but both live in the same
  `policy-as-versioned-flux` org for now. Splitting them is a real, separate decision, not
  free-standing scope creep to fold into an epic about the estate.
- **The fresh-org redeploy** — the "clean history" a viewer asked for during the demo. The answer
  isn't a rewrite of *this* history (git history is the audit trail; see the signing-mistake
  episode above for why that's a feature, not a bug to hide). It's this whole project's eventual
  sequel: a from-scratch redeploy into a fresh org, proving reproducibility by actually doing it
  again, with this org kept as the record of how it was actually built — thrashing included.

No history rewrite happens *in place*, ever. If a newcomer wants the raw, unfiltered story — the
real commit-by-commit thrashing this document summarizes — it's still all there, unrewritten, one
`git log` away.
