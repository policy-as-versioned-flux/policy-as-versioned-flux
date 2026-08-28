# policy

The versioned policy source (PRD §5.1). Tagged semver releases of this repo
*are* the dependency consumers pin — see the hub repo's
[CONTEXT.md](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/CONTEXT.md) and
[ADR-0001](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/docs/adr/0001-transport-signed-git-tags-gitsign.md)/[ADR-0002](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/docs/adr/0002-adoption-pinned-plus-renovate-pr.md).

```
workloads/kyverno/<policy-name>/   workload plane: ValidatingPolicy (CEL) + kustomization.yaml
cloud/<policy-name>/                cloud plane (issue 17, ADR-0004): same pattern, targeting
                                    Crossplane v2 AWS provider-family CRDs instead of Pods
                                    (nameSuffix + policy-version self-selector,
                                    substituted from one value — PRD §6.4)
rationale/<policy-name>/            the "why": rationale.md (+ NIST 800-53r5 control mapping
                                    and harvest provenance, for cloud/ policies)
tests/<policy-name>/                kyverno test fixtures (pass/fail/skip =
                                    worked examples — the "testable" -able)
```

Workload plane, three worked examples (CONTEXT.md, lane-keeping vs gate):

- `require-department-label` — `validationActions: Audit` at launch (v1.0.x),
  promoted to `Deny` at v2.0.0 (an Audit→Deny promotion — CONTEXT's
  semver-major example).
- `require-known-department-label` — `validationActions: Deny` from launch,
  the gate. Its known-department set widened at v2.1.1 (a patch).
- `require-owner-annotation` — `validationActions: Audit`, new at v2.1.1 (a
  minor addition).

Cloud plane (issue 17), same engine and coexistence pattern, no cloud-special
versioning, harvested from [`controlplaneio/collie`](https://github.com/controlplaneio/collie)
(Apache-2.0 -- intent only, rebuilt for Crossplane's current namespaced,
upjet-generated AWS provider-family; see each rationale.md for exactly what
was kept vs. rebuilt, and the [`cloud`](https://github.com/policy-as-versioned-flux/cloud)
repo for the harvested OSCAL catalogue):

- `require-s3-bucket-encryption` — `validationActions: Deny`, the cloud
  plane's gate (NIST sc-28).
- `require-rds-multi-az` — `validationActions: Audit`, the cloud plane's
  lane-keeper (NIST cp-10).

Run `./verify.sh` to check out every policy currently in the tree
end-to-end (`kyverno test` fixtures + kustomize version substitution, and
that every policy in the release agrees on one version) — no cluster
needed. Run `./verify-live.sh` against a live cluster (`fleet/up.sh`) to
see the enforcement-action difference for real: the Audit policy reports a
failure but admits the pod, the Deny policy refuses admission outright.

## Releases

| Tag | Bump | What changed |
|---|---|---|
| `v1.0.1` | — | `require-department-label` (Audit) + `require-known-department-label` (Deny) launch. (`v1.0.0` exists but its own release run failed — see its CI log — content is identical to `v1.0.1`.) |
| `v2.0.1` | major | `require-department-label` promoted Audit → Deny. (`v2.0.0` exists but was accidentally SSH-signed, not gitsign-signed — content is identical to `v2.0.1`.) |
| `v2.1.1` | minor + patch | new `require-owner-annotation` (Audit); `require-known-department-label`'s known-department set widened (`+legal`). |
| *(pending)* `v2.2.0` | minor | not yet tagged, blocked on a gitsign re-auth (see issue 08's comments). On `main`: the `matchConditions` fix (issue 08, zero verdict impact, would be patch alone) bundled with the new cloud-plane policies `require-s3-bucket-encryption` + `require-rds-multi-az` (issue 17, minor -- new policies can't fail an existing compliant workload) -- minor wins when both land in one release. |

Two tags per "real" release exist for `1.0` and `2.0` because of bootstrap
mistakes (a CI bug, then a signing-config regression) on a repo with no
external consumers yet at the time — each is left in place, not deleted,
because the tag-immutability ruleset (below) means fixing forward is the
only option once *anyone* might depend on a tag, so the pattern is
established honestly from the start rather than special-cased later.

## Releasing

`.github/workflows/release.yml` runs on every `v*.*.*` tag push — see
ADR-0001 in the hub repo. Release tags are additionally protected by a
[repository ruleset](https://github.com/policy-as-versioned-flux/policy/rules)
blocking deletion and force-updates on `refs/tags/v*` (immutability, defence
in depth alongside the commit pin).

## Governance (issue 22)

[`ADVISORY-METADATA.md`](ADVISORY-METADATA.md) — the `created`/`lastReviewed`/`rationale`/`risk`/
`ethos` schema every policy carries, where each field lives, and why the engine structurally
cannot read any of it (`./verify-determinism.sh` checks this). [`EDITORIAL-REVIEW.md`](EDITORIAL-REVIEW.md) —
review, defence, and removal, each a reviewed PR, never time-triggered; `demo-removal/run.sh`
proves removal is a real structural deletion, not an archive/deprecate flag.

## Handbook (issues 25, 26)

Extracted into its own component, [`handbook-generator`](https://github.com/policy-as-versioned-flux/handbook-generator)
(ticket 05, real-estate epic) — it reads every policy straight out of a given checkout+tag's tree
(version, enforcement action, advisory metadata, full rationale) and renders a human-readable
handbook, generic against *any* policy checkout, not bound to living in this repo. Regenerate from
a different tag and you get that version's own policy set; nothing here is hand-maintained or
committed as a snapshot (a committed handbook would itself drift the moment the next tag lands,
the exact problem this exists to avoid).

`--with-summaries` additionally weaves in a plain-language per-policy summary for a non-technical
reader, generated by a real `claude -p` call against that policy's rationale — this is the
last-mile attempt's human half (issue 26), framed honestly as an attempt at an acknowledged open
problem (CONTEXT.md), not a claimed solution: it's a summary of the rationale a human wrote, not a
substitute for a human deciding whether the policy still holds. Summaries are cached in that
component's own `.cache/` (moved with it — a derived artifact of rationale content, not policy
content itself) keyed by a hash of the rationale that produced them, so unchanged policies don't
re-cost an LLM call on every regeneration, and a changed `rationale.md` has no matching cache
entry — the component's `verify-fresh.sh` fails loudly if any policy's summary is stale, so a
stale summary can't ship silently.

CI-wiring (e.g. as a release asset) needs an `ANTHROPIC_API_KEY` secret provisioned in this repo's
Actions settings, which only the org owner can add — not done here, left as a documented next step
rather than silently skipped.
