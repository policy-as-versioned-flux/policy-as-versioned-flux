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
comment: branch reachability, not (only) SSH signing" — its own title conceding SSH signing was a
real, secondary factor, not fabricating a clean single cause. Kept as an honest record, not
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
pipeline.

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

**A second wave: turning "done" into "provably done."** Once all fifteen tickets were marked
done, an explicit ask — prove it, adversarially — ran an independent multi-agent audit against
every checkable claim across the whole epic: real commands against the live cluster and GitHub,
not a re-read of the tickets' own narrative. It found five real gaps hiding behind "done" status,
and a second, follow-up audit pass (after fixing those) found more — this is that same "fixes to
the fixes, kept not hidden" pattern Episode 1 already established, one level up.

The most structurally significant finding: `clusters/cluster1/policy-versions.yaml` and
`apps.yaml` — the files that install/retire policy versions and team apps — were never actually
wired into continuous Flux reconciliation. They were one-shot `kubectl apply`'d by `up.sh` at
bring-up and never touched again by any controller. Two real consequences, both caught live: the
cluster's `ResourceSet` had quietly drifted out of band (a hand-edited `version` field, no
matching tag/commit change), which was actively denying two running apps at admission when the
audit found it; and ticket 09's "merging a retirement PR retires the version" claim had never been
tested against a *continuously-reconciling* cluster — the closest real precedent,
[`fleet#7`](https://github.com/policy-as-versioned-flux/fleet/pull/7), had genuinely merged and
removed an array element back on 2026-07-15, but at that point `clusters/cluster1/*.yaml` wasn't
wired into Flux at all, so the merge changed git without touching the live cluster. (A second
adversarial pass caught an earlier draft of this very paragraph repeating the wrong, broader
claim — "never actually merged" — even after ticket 09's own file had already corrected it; fixed
here to match.) Fixed for real, not patched around: a new `cluster-state` Flux Kustomization
([`fleet#55`](https://github.com/policy-as-versioned-flux/fleet/pull/55)) gives these files the
same self-healing git-drives-cluster guarantee every other resource here already had, and the
"merging retires the version, live, with zero manual steps" claim was re-proven with two PRs
([`fleet#56`](https://github.com/policy-as-versioned-flux/fleet/pull/56)/[`#57`](https://github.com/policy-as-versioned-flux/fleet/pull/57))
— install a throwaway version, watch Flux install it with zero manual steps; remove it, watch Flux
prune it back out just as automatically.

The other four gaps were smaller but real: Renovate's `kubernetes` manager needs explicit
enablement (unlike the `github-actions` manager, it isn't default-on) — the c2p-collector and
readiness-collector image pins weren't actually bumpable dependencies as claimed, now fixed
([`fleet#49`](https://github.com/policy-as-versioned-flux/fleet/pull/49)); the same
"repo lacks a local `renovate.json`" root cause ticket 06 diagnosed for four app repos turned out
to apply to three more repos nobody had checked (`c2p-collector`, `readiness-collector`, and
`policy` itself via its own day-old dormant onboarding PR — this project's entire history spans
2026-07-14 to 2026-07-18; nothing in it is a year old, an earlier draft of this line said "year-old"
and a later adversarial pass caught it); the weekly governance nag's "skips
already-actioned issues" checkbox was ticked with no code behind it, now genuinely implemented and
proven live, including the case where it correctly *doesn't* skip
([`fleet#50`](https://github.com/policy-as-versioned-flux/fleet/pull/50)); and eight of nine
tagged repos had no forge-level tag-immutability protection at all, contradicting
[ADR-0001](adr/0001-transport-signed-git-tags-gitsign.md)'s own stated requirement, now matching
the one repo (`policy`) that already had it right.

Two corrections came from the audit turning the same skepticism on itself. A prior fix's own
"correction" claiming two governance-issue checkbox templates use identical wording was itself
wrong — re-checked directly against both scripts, only one of the three lines actually matches,
and the other two don't just differ in wording, they swap which answer means what. And ticket 12's
headline claim that `ledger` (the roster's deliberately old-`log4j` laggard) would be
"worst-in-class on both staleness axes" turned out, once its real vulnerability scan finally
landed, to be true on the policy-version axis and **false** on the vulnerability axis — `ledger`
has fewer live CVEs (22) than either `reports` (188) or `storefront` (146). Left as the genuinely
interesting, slightly inconvenient finding it is, not reshaped to fit the original thesis.

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
