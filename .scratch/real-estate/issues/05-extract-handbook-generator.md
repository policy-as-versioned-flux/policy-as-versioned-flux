# 05 — Extract the handbook generator into its own component repo

**What to build:** The handbook generator (tag-driven handbook + agent-authored plain-language summaries + freshness gate) moves out of the policy repo into its own component, invoked against any policy checkout/tag. The policy repo keeps only what belongs to policy content (the summary cache stays wherever the freshness-gate contract needs it — implementation's call, but the "stale summaries cannot ship" property must survive the move intact). Component carries its own self-check.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Component repo; handbook regenerates from a given policy tag via the component, output equivalent to today's
- [ ] The freshness gate still fails loudly when a rationale changes without a regenerated summary
- [ ] Policy repo slimmed accordingly; its README points at the component
