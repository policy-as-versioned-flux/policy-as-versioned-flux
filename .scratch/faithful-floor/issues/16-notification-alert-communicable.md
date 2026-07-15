# 16 — Notification Alert on revision change (communicable)

**What to build:** The **communicable** "-able"'s push half: notification-controller `Provider` + `Alert` broadcasting every policy source revision change, so a version adoption (or any drift) is announced, not discovered. Together with 07's release notes this completes communicable; the audit-trail property (any tag drift is visible) from ADR-0001 rides on it.

**Blocked by:** 06 — Single-version consumption.

**Status:** in-progress, blocked on PR review

- [ ] Merging a version bump fires an alert naming the new revision within one reconcile
- [ ] The alert carries enough context to find the release notes for the new version

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
`allowPrivilegeEscalation: false`/capability drop/non-root on the echo receiver). Deliberately did
NOT `kubectl apply` this live pre-merge: this project's whole model is GitOps reconciliation, and
auto-mode correctly flagged a direct live-cluster mutation outside that path as needing explicit
user sign-off, which wasn't sought since a dry-run gave equivalent confidence. Both acceptance
checkboxes need `verify-notifications.sh` run for real, which needs the PR merged and Flux to
actually reconcile the new Kustomization first -- same "PR open, not self-merged" pattern as
issues 11/12/14/15.
