# TASK: onboard Renovate (Mend) across the six orgs

Type: task
Status: claimed
Blocked by: 11
<!-- app-install part done early at the human's request (2026-07-23, at keyboard); the renovate.json
     + observed-bump-PR part still waits on repos (11's build). -->


## Question

Get Renovate running across `policy-as-versioned-{platform,driftwood,tuppence,caldera,nist,ico}` so
the dependency-bump story (regulator artifact bumps, policy-version bumps, app deps) is live.

**Two real caveats that shape *how* and *when* this is done:**

1. **It's a permission grant, not a config commit.** Installing the Mend/Renovate GitHub App on an
   org is an OAuth/app authorisation the **org owner** grants — a sensitive, per-org consent. It is
   *not* something to auto-click across six orgs via an unattended background browser subagent. The
   safe shape: drive the browser to each org's install page, but the human clicks *Authorize*
   per org (or explicitly confirms proceeding). `renovate.json` files (which *are* just commits) can
   be automated once repos exist.
2. **Sequence: after repos exist.** The six orgs are currently empty. Renovate onboards *repos*, so
   there's nothing to bump until the platform + institution repos land (the refactor build,
   downstream of 11). Installing the app org-wide ("all repositories") is valid early prep, but the
   value only appears once repos with dependencies exist.

**Done when:** the Mend app is authorised on all six orgs (human-approved), org config set to all
repos, and — once repos exist — `renovate.json` is present and a real bump PR has been observed
(reuse the patterns already proven in the current `policy-as-versioned-flux` estate).

Record in the Answer: which orgs were authorised, any billing/consent notes, and the config used.

## Progress (2026-07-23)

- **`caldera` fully onboarded** as the template: Renovate Only · Silent **off** · Require config
  file **off** · Automated PRs on · Create onboarding PRs on. (Silent defaulted on via the wizard's
  "Scan Only"; fixed in Settings → Dependencies.)
- **`driftwood`/`ico`/`nist`/`platform`/`tuppence`** — GitHub app installed (all-repositories), but
  the Mend onboarding + un-silence config still needs applying (they'll default to Silent like
  caldera did). Deferred at the human's request; harmless while the orgs are empty, apply
  before/at the build.
- **Update:** the human fixed the un-silence config on the other five, so **all six orgs are now
  onboarded, Renovate Only, non-silent**. Remaining for full resolution: `renovate.json` present +
  a real bump PR observed — still waits on repos (11's build).
