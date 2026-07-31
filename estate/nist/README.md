# policy-as-versioned-nist

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

```sh
scripts/publish.sh        # seed + tag a release (offline pin: tag + commit)
scripts/verify-catalog.sh # fast offline check: real OSCAL, checksum matches, publishable
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
