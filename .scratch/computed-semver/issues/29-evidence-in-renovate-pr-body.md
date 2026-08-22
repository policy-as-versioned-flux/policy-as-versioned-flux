# 29 — Render the evidence into the Renovate pull request body

Type: task
Status: ready-for-agent
Blocked by: 27

Source: [`spec.md`](../spec.md), *The reviewer* user stories.

## What to build

A reviewer reads the evidence at the moment ADR-0002 makes non-negotiable. ADR-0002 makes the reviewed
pull request the only way a new version lands. Today the reviewer sees a version string and a diff.
They cannot see which workloads change verdict, and cannot see which rules nobody tested.

Render the evidence document into the Renovate bump pull request body. This is the view that gets the
design effort.

The body shows the declared bump and the computed bump side by side, so the reviewer sees the
discrepancy the publisher accepted. It shows per-policy verdict movement, so they see which rule caused
the class. It shows counts and the not-looked-at list, so they know what the gate did not test. It
shows each hole marked new, carried over, or closed, so a new hole in a patch release stands out. It
shows the derived limits, open and closed with their counts. It shows the per-institution matrix. It
names the corpus checksum and the generator version, so the run reproduces.

**No coverage percentage appears anywhere.**

## Acceptance criteria

- [ ] The pull request body carries the evidence document, rendered for a human.
- [ ] The declared bump and the computed bump appear side by side.
- [ ] Per-policy verdict movement appears, naming entries and expressions.
- [ ] Counts and the not-looked-at list appear.
- [ ] Each hole shows its stable id and its state: new, carried over, or closed.
- [ ] Derived limits appear with their counts, open and closed.
- [ ] The per-institution matrix appears.
- [ ] The corpus checksum and the generator version appear.
- [ ] No percentage appears anywhere.
- [ ] The body stays diffable between releases.
