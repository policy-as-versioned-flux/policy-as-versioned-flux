# estate — the six-org talk demo

Monorepo-style working tree for the six `policy-as-versioned-*` repos the talk
tours. Each top-level directory below becomes its **own GitHub repo** at split
(the prefix `policy-as-versioned-` is the impersonation guardrail — every org
carries it). Built fresh; the old `policy-as-versioned-flux` estate is
research-only (archived last, ticket 27).

| Dir | Repo | Role |
|---|---|---|
| [`platform/`](platform/) | `policy-as-versioned-platform` | The shared discipline (Flux templates, FAIR engine, ledger→PolicyException render, shift-left, OSCAL, war-gamer). Institutions pin it as a signed dependency. |
| [`driftwood/`](driftwood/) | `policy-as-versioned-driftwood` | Institution — e-comm, PCI+GDPR, **teaching default**. Audit-heavy (loosest £). Owns a KinD cluster; the provenance base (this ticket). |
| [`tuppence/`](tuppence/) | `policy-as-versioned-tuppence` | Institution — fintech, FCA+PCI+GDPR. Toward-strict. |
| [`ludlow/`](ludlow/) | `policy-as-versioned-ludlow` | Institution — US health, HIPAA. Deny-heavy (strictest £), long-life data. |
| [`nist/`](nist/) | `policy-as-versioned-nist` | Regulator — real 800-53 OSCAL controls catalog. |
| [`ico/`](ico/) | `policy-as-versioned-ico` | Regulator — small signed penalty schema from real public fine magnitudes. |

Dependency direction (every hop is a signed, versioned, Renovate-bumpable
dependency): `nist`/`ico` → `platform` → `{driftwood,tuppence,ludlow}`.

Two cross-cutting dirs (not repos): [`verify/`](verify/) holds the
cross-institution money-shot beats (proportionality, provenance);
[`talk/`](talk/) holds the Marp deck + demo runbook that tour the whole estate.

## Touring the talk

```sh
estate/talk/verify-all.sh    # the deck's honesty gate: every LIVE beat -> a passing verify
estate/talk/up.sh            # idempotent, offline-safe, audience-modular bring-up
```

See [`talk/deck.md`](talk/deck.md) (Marp) and [`talk/RUNBOOK.md`](talk/RUNBOOK.md).

## Quick start (driftwood — the live one)

```sh
estate/driftwood/scripts/up.sh      # idempotent: KinD + Flux + reconcile healthy
estate/driftwood/verify-reconcile.sh
estate/driftwood/scripts/reset.sh   # tear down
```

See [`docs/the model`](../.scratch/talk-spec/the-whole-model.md) and
[`spec.md`](../.scratch/talk-spec/spec.md) for the full thesis.
