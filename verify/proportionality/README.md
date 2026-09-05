# verify/proportionality — the money shot

> *The same workload lands on **baseline in driftwood** and **quarantine in ludlow**, because
> their £ differ.* Proportionality proven by comparison, not asserted.

The load-bearing live beat of the talk (spec user story 12; ticket 09). One workload, one FAIR
scenario, one shared cage body — priced against each institution's own signed risk-appetite band.
**The band alone moves the rung.**

> **Re-pointed 2026-09-05 (eco-system ticket 89).** Until that day this beat derived `Audit` for
> driftwood and `Deny` for ludlow from the same two bands, and rendered a per-institution
> Deny-shaped `ValidatingPolicy` to prove it. That derivation had no shipped subject: nothing in
> the estate selects an *enforcement action* from a band any more. `graded/cage.py select_tier`
> selects a **rung** from the same band, `wargamer.select_party_tier` folds a party's priced lines
> onto one, and `tier_pr.py` lands the result as a pull request against the governed Namespace
> manifest. And the owner ruled the old shape out (2026-09-02, ticket 75 Q5): nothing is denied; a
> workload that does not fit its cage does not run. So the beat grades the mechanism that ships,
> and the hub stops carrying a Deny of its own. `policies/`, `control/encrypt-at-rest.tmpl.yaml`
> and `tests/encrypt-at-rest/` are deleted; the shared control body is now the estate's real
> `cage-tier` MutatingPolicy, which is a stronger subject than a bespoke demo policy was.

## What's here

| file | role |
|------|------|
| `scenarios/encrypt-at-rest.json` | the ONE shared workload + FAIR triples, identical for both institutions |
| `control/governed-namespace.tmpl.yaml` | the SHARED governed Namespace body; `posture.acme.io/tier` is the only field the £ stamps |
| `render.py` | stamps the £-selected rung into the body per institution (reuses `platform/graded/cage.py`, fetched by [`../../clone-estate.sh`](../../clone-estate.sh) into `../../.estate-clone/platform/`); `--check` guards drift |
| `namespaces/proportionality-driftwood.yaml` | rendered: **baseline** (a baseline cage leaves £14,952 ≤ the £40,000 band) |
| `namespaces/proportionality-ludlow.yaml` | rendered: **quarantine** (baseline leaves £14,952 > the £5,000 band; quarantine leaves £1,709 ≤ it) |
| `verify-proportionality.sh` | the beat — asserts the divergent rungs, the £ that drives them, and that the shared cage body really produces two different cages |

## The mechanism

```
scenarios/encrypt-at-rest.json  (the `behind` triples, SAME for both)
        │
        ▼  platform/fair/fair.py  →  uncaged residual ALE ≈ £21,360
        │
        ├── driftwood band £40,000  →  baseline leaves £14,952 ≤ band  →  baseline  ┐
        └── ludlow    band  £5,000  →  baseline leaves £14,952 >  band,             ├─ render.py
                                       quarantine  leaves  £1,709 ≤ band → quarantine┘  stamps each
                                                                                        Namespace
        │
        ▼  the SAME graded/policies/cage-tier.yaml, both Namespaces in one `kyverno apply`
   driftwood's pod: 500m/256Mi, cage-baseline, no WAF   |   ludlow's: 100m/64Mi, cage-quarantine, WAF
```

The two Namespace declarations are **byte-identical except the tier and the org labels** — and
that tier is not hand-authored, it is whatever `cage.py` selects from the £. Change the band,
re-render, the rung moves. That is proportionality made mechanical.

Neither outcome is a refusal, and there is no rung that is one: the bottom of the ladder is
`isolated`, a running cage with no ingress and no egress (ADR-0022).

## Run it

```sh
./verify-proportionality.sh      # offline core: python3 (+ kyverno for the shared cage proof)
```

Exits non-zero if the beat would fail on stage, and exits 3 naming what it could not look at
rather than passing over it. The optional live tail dry-runs the rendered Namespaces against
`kind-driftwood` / `kind-ludlow` when those clusters are reachable.

Reuses `platform/graded/cage.py` (→ `platform/risk/enforce.py` → `platform/fair/fair.py`) as the
single source of the £ maths and of the tier table — no risk engine and no second selection rule
is reimplemented here. (Post-split: that's the real `policy-as-versioned-platform` repo, fetched
locally by `../../clone-estate.sh`.)
