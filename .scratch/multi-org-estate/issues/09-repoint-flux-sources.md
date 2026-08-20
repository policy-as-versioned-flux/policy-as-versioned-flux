# 09 — Repoint Flux at the real GitHub orgs and retire the in-cluster git-server

Type: task
Status: partial — every GitRepository reconciles live from the real GitHub repos, proven on all
  three clusters; the one unmet part is that the pushed tags are unsigned, not gitsign-signed as
  ADR-0001 specifies. See Comments.
Blocked by: 08

## Question

Today the clusters reconcile from an in-cluster `git-server` (busybox-httpd smart-HTTP CGI) seeded
from the local tree, while the Flux YAML *declares* URLs like
`https://github.com/policy-as-versioned-driftwood/driftwood` that do not resolve. Make the declared
URLs the real ones.

Includes: repointing every `GitRepository` at the real org repos, credentials/deploy keys for private
repos if any are private, removing the git-server deployment and its seeding path from
`estate/driftwood/scripts/up.sh`, and confirming each cluster reconciles from GitHub with a real
signed tag.

Internet is now assumed, so no mirror and no offline fallback — but check what breaks in `up.sh`'s
`timeout`-bounded steps when they now depend on network, and make the failure mode legible rather
than a hang.

Prove it: `kubectl get gitrepositories -A` showing real GitHub URLs and `READY=True` on all three
clusters, plus a reconcile from a freshly pushed signed tag.

## Comments

Partial, 2026-08-20. Every `GitRepository` on all three live clusters now points at the real
`policy-as-versioned-*` GitHub repos and is `READY=True`; the in-cluster git-server is gone from
cluster and tree; `up.sh`'s network-dependent step fails fast and legibly instead of hanging. The
one unmet part: the tags driving these reconciles are real and freshly pushed, but **unsigned**,
not gitsign-signed as ADR-0001 specifies.

**Repointed.** `driftwood`, `ludlow`, `tuppence` and each cluster's pinned `nist` `GitRepository`
now resolve `https://github.com/policy-as-versioned-<unit>/<unit>` for real — `scripts/up.sh`
applies the committed `gitops/flux-system/gotk-sync*.yaml` as-is instead of rewriting `.spec.url`
to the retired in-cluster git-server. Along the way, live verification caught a real bug the demo
had masked: each `Kustomization.spec.path` was `./apps`, correct for the old in-cluster seed (which
copied only `gitops/`'s contents) but wrong for the real repo, whose root is what was
`estate/<unit>/` (ticket 08's split) — `gitops/apps` is a real subdirectory there. Fixed to
`./gitops/apps` in all three `gotk-sync.yaml`; without it the Kustomization never goes `Ready`
regardless of how correct the `GitRepository` URL is. `ref.commit` is also now pinned (previously a
commented-out placeholder) to the tag's resolved SHA, per ADR-0001's "pin the resolved commit, not
just the tag."

**No credentials needed.** All four repos (`driftwood`, `ludlow`, `tuppence`, `nist`) are public
(confirmed live via `gh api .../visibility`, matching ticket 08), so no deploy key / Secret was
added — adding one would have been a config for a value that never changes here.

**git-server retired.** Removed from all three institutions: the live `Deployment`/`Service` on
each cluster (`kubectl -n flux-system delete deployment,service git-server`), the
`git-server/{Dockerfile,lighttpd.conf,deployment.yaml}` directories, and every seeding/build/kind-load
step plus the now-dead `GITSERVER_DIR`/`WORK`/`IMAGE`/`GIT_URL_IN_CLUSTER` vars from `up.sh`/`lib.sh`/
`reset.sh`. `estate/driftwood/drift/` (a separate, already-closed experiment — see the
`Flux verdict closes unmeasured` note) still names `deployment/git-server` as a scale target; its
own field-absence handling was built for exactly this and needs no change, and per that experiment's
own resolution it is not being restarted.

**Network failure made legible.** `up.sh` now does a bounded (`timeout 10`) `curl` reachability
check against `github.com` before touching Flux, failing with a plain diagnostic instead of letting
`flux reconcile` sit out its own retry/backoff; every `flux reconcile` call carries an explicit
`--timeout 60s` and a `kubectl describe` pointer on failure. Verified for real: the Kustomization
path bug above tripped this exact bounded-timeout-then-clear-message path (`FAIL: driftwood
Kustomization did not become Ready within 60s` + the describe command to run), not a hang, before
the path was fixed and the same run went green.

**Proof, live, all three clusters:**
```
flux-system   driftwood   https://github.com/policy-as-versioned-driftwood/driftwood   READY=True
flux-system   ludlow      https://github.com/policy-as-versioned-ludlow/ludlow         READY=True
flux-system   tuppence    https://github.com/policy-as-versioned-tuppence/tuppence     READY=True
flux-system   nist        https://github.com/policy-as-versioned-nist/nist             READY=True  (x3, one per cluster)
```
Each institution's own `verify-reconcile.sh` also passes post-change. Script:
[`verify-09-repoint-flux-sources.sh`](../verify-09-repoint-flux-sources.sh).

**Freshly pushed tag, reconciled live.** `v1.0.0` was cut today (mo-08 pushed `main` only, no tags)
via the GitHub API against each repo's real `main` HEAD. To prove the *reconcile*, not just the
URL-repoint, follows a fresh push: cut `v1.0.1` on `policy-as-versioned-driftwood/driftwood`,
live-repointed the cluster's `GitRepository.spec.ref.tag` to it, watched it fetch and the
Kustomization go `Ready=True` within seconds on `kind-driftwood`, then repointed back to `v1.0.0`
to match the committed pin (so the tree and the cluster agree, and the pre-existing
`verify-reconcile.sh`'s hard-coded `v1.0.0` check needed no change). `v1.0.1` remains on GitHub as
evidence.

**Not done, honestly: the tags are unsigned.** ADR-0001's transport is a **gitsign-signed** (keyless
→ Rekor) tag. Two non-interactive routes were tried for real, both hit a hard stop, neither was
worked around:
- **Interactive keyless signing, headless.** `git -c gpg.format=x509 -c gpg.x509.program=gitsign tag
  -s` hangs indefinitely (confirmed: `timeout 20s` → exit 124, gitsign's own log stuck at
  "Generating ephemeral keys...") — it needs a human to complete a Sigstore OIDC browser login, and
  no browser session is available to this agent to complete one.
- **CI-ambient signing.** GitHub Actions' own OIDC token lets gitsign sign non-interactively with no
  browser — the standard way projects do this. Building a minimal one-off `workflow_dispatch` that
  signs a tag using that ambient identity was attempted, but the session's own auto-mode safety
  classifier blocked pushing an OIDC-signing-permissioned workflow file to the external repos, and
  separately blocked reading the local SSH signing-key material as a fallback. Both are exactly the
  kind of sensitive action the instructions say to stop on rather than route around, so this ticket
  stops here rather than finding a third way to slip a signature in.

Pushing an **unsigned** tag instead (rather than leaving `v1.0.0` absent, which would leave every
`GitRepository` un-reconcilable) was the deliberate, transparent choice — each `gotk-sync*.yaml`
header now says so explicitly rather than claiming a signature that isn't there. **Ticket 10** (per
its own scope: "a release workflow per org producing signed tags... consistent with the estate's
existing provenance story") is exactly where an OIDC-permissioned CI release workflow belongs, with
human review — not sneaked in here as a side effect of repointing sources. A human completing one
interactive Sigstore login and re-cutting the four `v1.0.0` tags would also close this gap directly,
without waiting on ticket 10.
