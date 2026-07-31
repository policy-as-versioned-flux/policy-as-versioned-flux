# verify/proportionality — the money shot

> *The same control resolves to **Audit in driftwood** and **Deny in ludlow**,
> because their £ differ.* Proportionality proven by comparison, not asserted.

The load-bearing live beat of the talk (spec user story 12; ticket 09). One
control, one FAIR scenario, one policy body — evaluated against each
institution's risk-appetite band. **The band alone flips the verdict.**

## What's here

| file | role |
|------|------|
| `scenarios/encrypt-at-rest.json` | the ONE shared control + FAIR triples, identical for both institutions |
| `control/encrypt-at-rest.tmpl.yaml` | the SHARED Kyverno control body; `validationActions` is the only field the £ stamps |
| `render.py` | stamps the £-derived action into the body per institution (reuses `platform/risk/enforce.py`); `--check` guards drift |
| `policies/encrypt-at-rest-driftwood.yaml` | rendered: **Audit** (risk_bought £21k ≤ £40k band) |
| `policies/encrypt-at-rest-ludlow.yaml` | rendered: **Deny** (risk_bought £21k > £5k band) |
| `tests/encrypt-at-rest/` | `kyverno test`: the body is a real, self-scoping policy (pass/fail/unversioned) |
| `verify-proportionality.sh` | the beat — asserts the divergent verdicts **and the £ that drives them** |

## The mechanism

```
scenarios/encrypt-at-rest.json  (warn/deny triples, SAME for both)
        │
        ▼  platform/fair/fair.py  →  risk_bought = ALE_warn − ALE_deny ≈ £21,107
        │
        ├── driftwood band £40,000  →  £21k ≤ band  →  Audit  ┐
        └── ludlow    band  £5,000  →  £21k >  band  →  Deny   ┘  render.py
                                                                stamps each
                                                                policy body
```

The two policy bodies are **byte-identical except `validationActions` and the
org label** — and that action is not hand-authored, it is whatever
`enforce.py` computes from the £. Change the band, re-render, the verdict
flips. That is proportionality made mechanical.

## Run it

```sh
./verify-proportionality.sh      # offline core: python3 (+ kyverno for the body proof)
```

Exits non-zero if the beat would fail on stage. The optional live tail
dry-runs the rendered policies against `kind-driftwood` / `kind-ludlow` when
those clusters have Kyverno's CRDs installed; otherwise it skips and the
offline proof stands.

Reuses `platform/risk/enforce.py` (→ `platform/fair/fair.py`) as the single
source of the £ maths — no risk engine is reimplemented here.
