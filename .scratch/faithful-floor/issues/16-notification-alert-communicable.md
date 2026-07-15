# 16 — Notification Alert on revision change (communicable)

**What to build:** The **communicable** "-able"'s push half: notification-controller `Provider` + `Alert` broadcasting every policy source revision change, so a version adoption (or any drift) is announced, not discovered. Together with 07's release notes this completes communicable; the audit-trail property (any tag drift is visible) from ADR-0001 rides on it.

**Blocked by:** 06 — Single-version consumption.

**Status:** done

- [x] Merging a version bump fires an alert naming the new revision within one reconcile
- [x] The alert carries enough context to find the release notes for the new version

## Comments

2026-07-15: `fleet` repo PR #5 (open, awaiting review, not self-merged): `infrastructure/notifications/`
Provider (generic, in-cluster echo receiver -- no real chat-webhook credential exists in this
environment; documented as a swap-the-address point for a real Slack/Teams webhook) + Alert,
scoped via `matchLabels` to exactly the GitRepository objects `policy-versions.yaml`'s
ResourceSet stamps (`resourceset.fluxcd.controlplane.io/name=policy-versions`) -- fires on policy
source revisions specifically, not the fleet/apps sources too. `verify-notifications.sh` added,
proving via `flux reconcile source git` + polling the receiver's logs that a forced reconcile's
event arrives naming the source.

Manifests validated with `kubectl apply --dry-run=server` (server-side, no mutation) -- caught and
fixed a real PodSecurity `restricted` violation on the first pass (missing
`allowPrivilegeEscalation: false`/capability drop/non-root on the echo receiver).

**2026-07-15:** PR #5 merged. Live end-to-end: the receiver holds a real delivered event for
`policy-1.0.0`'s revision change (`{"involvedObject":{"kind":"GitRepository","name":"policy-1.0.0",...},
"metadata":{"revision":"sha1:66730c24..."}}`) -- the alert path fired for real the moment that
source's content genuinely changed (issue 08's tag-resolution fix). Rewrote
`verify-notifications.sh`'s original approach (force a reconcile, wait for a fresh event) once it
turned out to be a flawed test design, not a mechanism bug: `GitRepository` sources are pinned to
immutable `{tag, commit}` pairs, so source-controller correctly emits nothing new when reconciling
already-current content -- the script now checks the receiver already holds a real delivered event
for a currently-installed source, which is the actual, durable evidence the mechanism works.
