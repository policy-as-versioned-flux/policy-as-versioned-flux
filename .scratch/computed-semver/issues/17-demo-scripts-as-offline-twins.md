# 17 — Rewrite the two demo scripts as offline twins

Type: task
Status: ready-for-agent
Blocked by: 12

Source: [`spec.md`](../spec.md), *The repair release*, step 7. Split from
[ticket 09](09-repair-release-and-pinned-delivery.md).

## What to build

`graded/up.sh` and `posture/up.sh` are a delivery path today. They run `kubectl apply -f`, not even
`-k`. After [ticket 15](15-the-repair-release.md) the version trees deliver those policies, so the two
scripts must stop delivering and start demonstrating.

Rewrite each as an offline twin. It renders the version trees as the ResourceSet would, then applies
that. The demo then runs without Flux, and there is still one truth.

Every comparable check in this estate already has an offline twin. Follow that pattern.

## Acceptance criteria

- [ ] `graded/up.sh` renders the version trees and applies the rendered output.
- [ ] `posture/up.sh` does the same.
- [ ] Neither script applies an unrendered authoring copy.
- [ ] The demo runs with no Flux in the loop.
- [ ] The rendered output matches what the ResourceSet produces, and a check proves it.
- [ ] The scripts are documented as demo paths, not delivery paths.
