# 10 — Signed releases per org and cross-org Renovate bumping

Type: task
Status: open
Blocked by: 08, 09, 17

## Question

Make the dependency direction real on the wire: `nist`/`ico` → `platform` → `{driftwood, tuppence,
ludlow}`, every hop a signed, versioned, Renovate-bumpable dependency.

Includes: a release workflow per org producing signed tags (gitsign keyless → Rekor, consistent with
the estate's existing provenance story); Renovate configured to open cross-org bump PRs; and the
version cross-check gate (`estate/platform/shift-left/ci-check.py`) working when the target repo and
the policy repo are separate checkouts in separate orgs.

Relevant known fact: the org-level "Actions can create PRs" setting is **on** and overrides repo and
workflow permissions — it needs `admin:org` to read, so verify it per org rather than assuming.

Prove it end to end: cut a `platform` release, watch Renovate open a bump PR against one institution,
and watch the gate run on that PR.
