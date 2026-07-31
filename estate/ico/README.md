# policy-as-versioned-ico

**Regulator (real magnitudes, repackaged).** A small, signed, versioned penalty
schema — `regime → violation-type → fine formula/cap` — sourced from real public
UK fine magnitudes. It feeds the FAIR loss-magnitude directly and is deliberately
**not** force-fit into OSCAL (which models controls/assessment, not fine
schedules).

Consumed by: `platform` FAIR engine (loss magnitude). *(ticket 07)*

## What's here

```
schema/
  v1/penalty-schema.json(.sig)   versioned schema + detached signature
  v2/penalty-schema.json(.sig)   a real bump: +1 real fine (Doorstep Dispensaree, £275k, 2019)
  keys/ico-signing-key(.pub).pem ed25519 keypair (ponytail: repo-local demo key, see sign.sh)
  sign.sh / verify.sh            offline sign / verify a version dir
  to_fair_scenario.py            schema entry -> fair.py scenario (unmodified fair.py consumes it)
verify-penalty-feed.sh           the whole beat: sign+verify, tamper rejection, £ moves on a bump
```

Four regimes, each `regime -> violation-type -> fine formula/cap`, grounded in real public
enforcement notices with cited sources: `uk-gdpr` (ICO), `pci-dss` (card-scheme acquiring banks),
`hipaa` (US HHS OCR), `fca` (UK FCA). Run `./verify-penalty-feed.sh` (offline, no cluster) to see
a schema-version bump move the £ that `platform/fair/fair.py` reports, with no edit to `fair.py`.

