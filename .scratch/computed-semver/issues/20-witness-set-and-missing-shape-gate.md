# 20 — The witness set and the missing-shape gate

Type: task
Status: ready-for-agent
Blocked by: 19

Source: [`spec.md`](../spec.md), *The corpus*.

## What to build

The generator proves itself against real workloads. Two populations exist. The **generated spine**
decides bumps. The **witness set** proves the generator.

The witness set is the five rederive fixtures plus the six real unlabelled infrastructure workloads the
COTS effort named. Witness entries test shape, never residual.

A **shape** is the tuple of outcomes each subject expression gives on a pod, plus whether its pin is
inside the array. This is the coverage vocabulary that
[ticket 23](23-coverage-as-counts-and-holes.md) builds on.

**A witness shape missing from the generated spine fails the build.** The repair is always the
generator, never the fixture. That is what stops curation toward a wanted bump.

## Acceptance criteria

- [ ] The witness set holds the five rederive fixtures and the six real infrastructure workloads.
- [ ] A shape is computed as the tuple of per-expression outcomes plus the in-array flag.
- [ ] A witness shape absent from the generated spine fails the build.
- [ ] The failure names the witness and the shape it carries.
- [ ] No witness entry carries a residual.
- [ ] The manifest records per-witness provenance.
- [ ] A test proves that removing an axis value from the generator makes a witness shape fail.
