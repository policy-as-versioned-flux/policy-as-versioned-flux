# 05 — Extract the handbook generator into its own component repo

**What to build:** The handbook generator (tag-driven handbook + agent-authored plain-language summaries + freshness gate) moves out of the policy repo into its own component, invoked against any policy checkout/tag. The policy repo keeps only what belongs to policy content (the summary cache stays wherever the freshness-gate contract needs it — implementation's call, but the "stale summaries cannot ship" property must survive the move intact). Component carries its own self-check.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Component repo; handbook regenerates from a given policy tag via the component, output equivalent to today's
- [x] The freshness gate still fails loudly when a rationale changes without a regenerated summary
- [x] Policy repo slimmed accordingly; its README points at the component

## Comments

Done 2026-07-16 (status header missed updating at the time — caught and backfilled during the
epic's final sweep). `policy-as-versioned-flux/handbook-generator` v1.0.0.
`generate.sh`/`verify-fresh.sh` generalized to take an explicit `<policy-checkout-path>` instead
of assuming they run inside the policy repo's own worktree; `.cache/` moved with the generator (a
derived artifact of rationale content, not policy content itself). Component's own `verify.sh`
proves both the handbook structure and the freshness-gate contract against a real signed tag from
the real policy repo, without ever calling `claude -p`. Policy repo's `handbook/` directory
removed, README updated to point at the component — shipped as `policy#8`.
