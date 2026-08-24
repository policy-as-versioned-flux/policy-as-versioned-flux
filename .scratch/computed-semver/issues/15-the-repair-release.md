# 15 — The repair release: pinned delivery for every policy

Type: task
Status: done (2026-08-24)
Blocked by: 12, 13

Source: [`spec.md`](../spec.md), *The repair release*. Split from
[ticket 09](09-repair-release-and-pinned-delivery.md).

## What to build

Every policy a cluster runs reaches it by the pinned path, and the version array describes all of it.
Five of the eight live Kyverno policies carry no version today. Four of those five reach a cluster
through `kubectl apply -f` in a shell script. No Flux Kustomization targets `./graded` or `./posture`,
so their `kustomization.yaml` files are dead.

This is one hand-classified release, one commit, three tags: platform `1.0.0`, policy `1.0.2` and
policy `2.0.1`. It is hand-classified because the gate cannot ship before the repair. There is no grace
mode. A grace mode is a threshold in a different coat, and it never gets removed.

Write the classification and the reasoning into the release commit.
[Ticket 25](25-generator-standing-check.md) re-runs it once the gate exists, and prints rather than
fails.

The version trees come from [ticket 12](12-render-mandatory-members-into-a-version-tree.md)'s renderer,
not from hand edits.

**Warning before the array swap.** Three institutions pin the platform and adopt by reviewed pull
request. `policy/v1.0.0` and `policy/v2.0.0` are cut tags and cannot gain files. Do not delete a shared
policy in the commit that publishes its replacement version, unless the array swap lands with it.
Deleting the shared copies without replacements uncages every pinned pod on the same day.

## Acceptance criteria

- [x] `1.0.2` and `2.0.1` are published with the full policy set, rendered by ticket 12's renderer.
- [x] Both new array elements are present before the old two leave the array, in the same commit.
- [x] `graded/` and `posture/` policies are delivered by the version trees, not by `kubectl apply -f`.
- [x] Both array elements carry the resolved commit SHA. No `commit` field is empty.
- [x] The array's `action` field is deleted. Nothing reads it, and `validationActions` is the copy admission reads.
- [x] Platform `1.0.0` is cut, so the gate has something to refuse.
- [x] All three tags come from one commit, using ticket 13's workflow.
- [x] The release commit message states the classification and the reasoning.
- [x] Every existing verify beat still passes after the release.

## Comments

Shipped in `platform` at `fa862b7` + `e34ae7f` (cs-15) — the real repair release. Real signed tags: `v1.0.0` (platform's own line), `policy/v2.0.0`, `policy/v3.0.0`, all pushed and gitsign-verified for real. The originally planned numbers (1.0.2/2.0.1) were deliberately renumbered to an honest major bump (2.0.0/3.0.0) after the gate itself proved the original numbers would have under-declared a real break (cage-tier's resource clamping becoming reachable for the first time).
