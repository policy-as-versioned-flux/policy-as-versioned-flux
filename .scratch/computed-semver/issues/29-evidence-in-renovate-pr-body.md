# 29 — Render the evidence into the Renovate pull request body

Type: task
Status: done (2026-08-24)
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

- [x] The pull request body carries the evidence document, rendered for a human.
- [x] The declared bump and the computed bump appear side by side.
- [x] Per-policy verdict movement appears, naming entries and expressions.
- [x] Counts and the not-looked-at list appear.
- [x] Each hole shows its stable id and its state: new, carried over, or closed.
- [x] Derived limits appear with their counts, open and closed.
- [x] The per-institution matrix appears.
- [x] The corpus checksum and the generator version appear.
- [x] No percentage appears anywhere.
- [x] The body stays diffable between releases.

## Comments

Implemented jointly with ticket 28 in the same commits — see [ticket 28](28-adopter-gate-in-shift-left.md)'s Comments for the full citation.
