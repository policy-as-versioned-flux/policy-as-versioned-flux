---
status: accepted
---

# The twin emits a scenario; the estate annualises it and selects the tier

Two risk engines existed with no seam (findings H3-01, H1-13). The twin prices one shock under a
perspective and has no frequency. The estate's `fair.py` annualises loss and is wired to
`prices[]` and the proposer. Decided 2026-08-28 in `.scratch/ecosystem/issues/08`.

## The decision

- The twin emits a **forward-intel** feed (ADR-0019 envelope, `name: forward-intel`) from the
  adopter's own repo, signed by the adopter's twin agent. Its payload is a scenario: perspective,
  shock, horizon, frequency triple or null, magnitude triple or severity spec, currency, and the
  per-account trade-off curve. It carries no recommended action.
- The estate consumes it as one more pricing parent edge, `source: twin`, into `prices[]`.
  `fair.py` annualises it. A versioned, signed **selection policy** package, published by the
  adopter and pinned by Renovate, turns the curve into one tier. The PR names the policy version
  and the curve hash.
- Appetite is a signed fact on `party.yaml`, next to size. Every price carries `perspective` and
  `currency`. `fair.py` reports its `tail` and accepts a lognormal-GPD severity spec.

## Alternatives

- The twin computes the tier and the estate only enacts it. Rejected: the twin cannot annualise,
  and the selection would live in an unversioned place.
- One engine, the other deleted. Rejected: each answers a different question; the seam is small.

## Consequences

The verify script for ticket 25 must show one twin entry in `prices[]` that names its perspective,
currency, policy version and tail, and must fail if any sum crosses perspectives.
