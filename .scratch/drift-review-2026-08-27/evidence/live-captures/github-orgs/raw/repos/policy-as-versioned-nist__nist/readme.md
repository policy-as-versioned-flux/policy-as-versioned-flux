# policy-as-versioned-nist

**GitHub org:** [`policy-as-versioned-nist`](https://github.com/policy-as-versioned-nist) ·
**Role:** regulator — publisher · **Licence:** [Apache-2.0](LICENSE)

Part of the *Policy as Versioned Code* estate: a shared platform, two regulators, three regulated
institutions, each its own independent GitHub organisation, exchanging signed, versioned
dependencies. A regulator publishes controls or penalties as a signed, versioned artefact and bears
no risk of its own here. Full thesis, design decisions (ADRs) and the other five parties:
[policy-as-versioned-flux](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux).

**Regulator (real).** Publishes the genuine NIST 800-53 OSCAL controls catalog
as a versioned, signed, machine-readable artifact that institutions pin as an
upstream dependency. A regulatory change propagates down the graph as a
dependency bump PR. Controls-as-code, already real today.

Consumed by: `platform` (OSCAL/c2p plumbing) → institutions. *(ticket 04)*

## What's here

[`catalog/`](catalog/) is the genuine NIST SP 800-53 Rev 5.2.0 OSCAL catalog
(20 control families, 1196 controls — sourced verbatim from
[`usnistgov/oscal-content`](https://github.com/usnistgov/oscal-content),
checksum + provenance recorded in
[`CATALOG_VERSION.json`](catalog/CATALOG_VERSION.json)). Not a fixture — the
real controls-as-code artifact regulators already publish today.

Beside the catalogue, `catalog/` also carries the three baselines NIST
already ships — LOW, MODERATE and HIGH — as OSCAL profiles, sourced verbatim
from the same upstream and re-hosted so this party's own signed tag is the
pin (provenance in [`BASELINE_VERSIONS.json`](catalog/BASELINE_VERSIONS.json)).
Every control id is the bare catalogue id (`ac-6`, never `AC-6`, never
`nist-800-53:ac-6`); each profile names the catalogue once, by the `href` on
its one `imports` block. An adopter selects a baseline **by name** in its
party artefact — that is the risk-bearing act, not this repo's to make (see
[ADR-0013](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/main/docs/adr/0013-regulator-publishes-baselines-adopter-selects.md)
in the hub repo). MODERATE resolves 287 controls and holds `ac-6`, `cm-6`
and `ac-6.10`; LOW excludes `ac-6`.

```sh
scripts/publish.sh        # seed + tag a release (offline pin: tag + commit)
scripts/verify-catalog.sh # fast offline check: real OSCAL + baselines, checksums match, publishable
```

`driftwood` pins a specific tag+commit of this catalog as a Flux
`GitRepository` (see `estate/driftwood/gitops/flux-system/gotk-sync-nist.yaml`
and `driftwood-nist-pin` ConfigMap). A regulator change here — a new
`publishedVersion` in `CATALOG_VERSION.json`, re-run `publish.sh` — is
consumed as a version bump: `estate/driftwood/scripts/bump-nist-pin.sh
<new-tag>` produces the reviewable diff a human merges.

On the real `policy-as-versioned-nist` GitHub remote, releases are
gitsign-signed (keyless → Rekor) — same convention as `driftwood`'s own
source; verified out-of-band via `git verify-tag`/Rekor, not Flux's
OpenPGP-only `spec.verify`.
