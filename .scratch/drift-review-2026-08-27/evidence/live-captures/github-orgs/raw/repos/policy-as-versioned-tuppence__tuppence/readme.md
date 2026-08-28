# policy-as-versioned-tuppence

**GitHub org:** [`policy-as-versioned-tuppence`](https://github.com/policy-as-versioned-tuppence) ·
**Role:** institution — risk-bearer, adopter · **Licence:** [Apache-2.0](LICENSE)

Part of the *Policy as Versioned Code* estate: a shared platform, two regulators, three regulated
institutions, each its own independent GitHub organisation, exchanging signed, versioned
dependencies. Full thesis, design decisions (ADRs) and the other five parties:
[policy-as-versioned-flux](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux).

**Institution — fintech, FCA + PCI + GDPR.** Risk skin: *toward-strict* (scary £,
availability/fraud flavour). Same internal shape as `driftwood`: pins `platform`
(signed), pins `nist` controls + `ico` penalties @version, owns Kyverno CEL
policies (versioned, conditional), own apps, own KinD cluster. Workload-identity
flagship (`customer-accounts-reset`, posture-gated reach + secrets). *(tickets 08, 14–17)*
