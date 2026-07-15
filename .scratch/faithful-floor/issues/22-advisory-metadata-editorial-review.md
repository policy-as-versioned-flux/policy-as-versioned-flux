# 22 — Advisory metadata schema + editorial-review process

**What to build:** The human-governance substrate (ADR-0006/0007): a schema for the advisory metadata each policy version carries — `created`, `lastReviewed`, rationale, risk, ethos (annotations + rationale doc, OSCAL-mappable) — read by humans and agents only, never by the engine; and the documented editorial process: every policy dated, regularly reviewed, and removed if no longer defensible ("Not archived. Not deprecated. Removed.") — always by reviewed PR, never time-triggered.

**Blocked by:** 03 — Gate VP + rationale layout.

**Status:** done

- [x] Both workload policies (and the cloud pattern) carry conformant advisory metadata
- [x] A check proves no policy body references any advisory field (determinism holds)
- [x] The editorial process doc covers review, defence, and removal — each as a PR
- [x] Removal is demonstrated as deletion in a version bump, not archival

## Comments

Done 2026-07-14. `policy` repo, `ADVISORY-METADATA.md`: the schema (`created`/`lastReviewed` as
`mycompany.com/*` annotations; `rationale`/`risk`/`ethos` in `rationale.md`, formalizing what was
already informally there as **Risk mitigated:**/**Intent:** into a consistent 3-section pattern
across all 5 policies, now with an explicit **Ethos:** section too) and the OSCAL mapping. Applied
to all 5 current policies (workload + cloud), not just the original two -- same schema, no reason
to special-case.

`verify-determinism.sh`: greps `spec.validations`/`spec.matchConditions` specifically (not the
whole file -- annotations legitimately point at `rationale.md` by path, that's for humans/agents
per ADR-0007, not a determinism violation) for the 5 field names plus `now(`/`timestamp(`.
Verified it actually works, not just trivially passes: injected a fake reference into a copy of a
real policy, confirmed FAIL, reverted, confirmed OK. Documented *why* this can only be a
defence-in-depth check, not the real guarantee: Kyverno's CEL context for these fields is
`object`/`oldObject`/`request`/`authorizer` only -- a `ValidatingPolicy` structurally cannot read
its own metadata from its own body, so the property already holds before any check runs.

`EDITORIAL-REVIEW.md`: review/defence/removal, each a reviewed PR, never time-triggered --
explicit that `last-reviewed` is a human-set date, not something CI bumps (that would make the
field lie about what it means). `demo-removal/run.sh`: a real, runnable add-then-remove sequence
in a throwaway git worktree (doesn't touch the 5 real policies) -- proves removal is a structural
git deletion: directory gone, `kustomize build` fails on the missing path, no lingering reference
anywhere in the tree, `git diff --stat` between the two commits is pure deletions. Ran green.
