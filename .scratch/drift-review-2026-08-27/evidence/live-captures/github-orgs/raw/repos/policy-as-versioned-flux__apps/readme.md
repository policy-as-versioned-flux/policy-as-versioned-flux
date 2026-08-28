# apps (archived)

**Archived 2026-07-16, real-estate epic ticket 08.** Superseded by five real team repos, each
with its own real dependency tree, own reconcile cadence, own tags:
[storefront](https://github.com/policy-as-versioned-flux/storefront),
[ledger](https://github.com/policy-as-versioned-flux/ledger),
[reports](https://github.com/policy-as-versioned-flux/reports),
[api](https://github.com/policy-as-versioned-flux/api),
[datastore](https://github.com/policy-as-versioned-flux/datastore). `fleet` no longer references
this repo. Kept as history, not deleted — see the hub's curated history narrative (ticket 15) for
the fuller story of why three identical nginx pods in one monorepo stopped being enough.

---

Consumer workloads (PRD §5.1 — "the original's `app1..3`"). Each carries exactly
one `mycompany.com/policy-version` label — that's the whole onboarding cost
(the **consumable** "-able").

```
app1/   pins policy v1.0.1, department=platform
app2/   pins policy v2.0.1, department=finance
app3/   pins policy v2.1.1, department=security + an owner annotation
```

Three versions, three consumers -- proves issue 08's coexistence claim:
each app is judged only by the version it opted into, live and
simultaneously on one cluster (`fleet`'s `ResourceSet`, PRD §6.4).

Deployed by the `fleet` repo's `clusters/cluster1` Flux `Kustomization`
(path `./`, so all three apps here are picked up as one aggregating
`kustomization.yaml`).
