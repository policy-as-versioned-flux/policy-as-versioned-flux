# policy-as-versioned-ludlow

**GitHub org:** [`policy-as-versioned-ludlow`](https://github.com/policy-as-versioned-ludlow) ·
**Role:** institution — risk-bearer, adopter · **Licence:** [Apache-2.0](LICENSE)

Part of the *Policy as Versioned Code* estate: a shared platform, two regulators, three regulated
institutions, each its own independent GitHub organisation, exchanging signed, versioned
dependencies. Full thesis, design decisions (ADRs) and the other five parties:
[policy-as-versioned-flux](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux).

**Institution — US health, HIPAA.** Risk skin: *Deny-heavy (strictest)* —
decades-confidential data, HNDL/PQ real. Same internal shape as `driftwood`:
pins `platform` (signed), pins `nist` + `ico` @version, owns versioned Kyverno
CEL policies, own apps, own KinD cluster. The Deny end of the proportionality
comparison (same control → Audit in `driftwood`, Deny here, because the £ differs).
*(tickets 08, 09)*
