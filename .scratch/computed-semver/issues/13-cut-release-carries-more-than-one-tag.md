# 13 — Cut-release carries more than one tag

Type: task
Status: ready-for-agent
Blocked by: none

Source: [`spec.md`](../spec.md), *The repair release*, step 8. Split from
[ticket 09](09-repair-release-and-pinned-delivery.md).

## What to build

A publisher dispatches one release and gets several signed tags from one commit. `cut-release.yml`
takes a single `version` input today. The repair release publishes platform `1.0.0`, policy `1.0.2` and
policy `2.0.1` from one commit, so the workflow must carry a list.

Make this a named change, not a silent one. The workflow still refuses to move an existing tag. It
still signs keyless with the run's own Actions identity.

## Acceptance criteria

- [ ] The workflow accepts more than one tag in one dispatch.
- [ ] Each tag is a gitsign-signed annotated tag on the same commit.
- [ ] The existing-tag refusal runs for every tag before any tag is created.
- [ ] A failure part way through does not leave some tags pushed and others not, or the workflow states plainly that it cannot promise this.
- [ ] Tags are pushed by `git push` and never by the git-data REST API.
- [ ] The single-tag dispatch still works.
