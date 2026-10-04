**Composed bump: `major`** (publisher declared: `major`)

- added to the supported window: 6.0.0, 7.0.0

### `6.0.0`

| declared | computed | outcome |
| --- | --- | --- |
| `major` | `major` | passed |

**Verdict movement**

| policy | verdict | entries | expressions |
| --- | --- | --- | --- |
| cage-tier.yaml | major | ns-declares-59829f76d3b29fcf, ns-declares-cd63cae85c704526, ns-declares-e26bc608d993079b, ns-declares-e8aeacb70872dd4f, pin-ns-8193685ebe9e7df6, pin-ns-cd63cae85c704526, tier-ns-1d7cc48d73927cc4, tier-ns-416fc5dec79317c2, tier-ns-7822fc1973cd9a67, tier-ns-cd63cae85c704526, tier-ns-dcd899efe48bd12d | `{'baseline':  {'cpu':'500m','mem':'256Mi','pc':'cage-baseline-6-0-0',  'prio':'-10',   'harden':'false','wafCpu':'0',   'wafMem':'0'},
 'restricted':{'cpu':'250m','mem':'128Mi','pc':'cage-restricted-6-0-0','prio':'-100',  'harden':'true', 'wafCpu':'100m','wafMem':'128Mi'},
 'quarantine':{'cpu':'100m','mem':'64Mi', 'pc':'cage-quarantine-6-0-0','prio':'-1000', 'harden':'true', 'wafCpu':'250m','wafMem':'256Mi'},
 'isolated':  {'cpu':'100m','mem':'64Mi', 'pc':'cage-isolated-6-0-0',  'prio':'-10000','harden':'true', 'wafCpu':'250m','wafMem':'256Mi'}}[variables.tier]; namespaceObject != null && namespaceObject.metadata.?labels['policy-as-versioned.dev/governed'].orValue('') == 'true'
  ? namespaceObject.metadata.?labels['posture.acme.io/tier'].orValue('')
  : ''; variables.nsTier in ['baseline', 'restricted', 'quarantine', 'isolated']
  ? variables.nsTier
  : 'isolated'` |
| posture-trust-boundary.yaml | none | (structural, no fixture moved) | `variables.posture == variables.claimed` |
| require-nonroot.yaml | none | (structural, no fixture moved) | `variables.nonroot || (variables.attested && variables.hardened)` |

**Counts:** old=174 new=168 union=180

**Not looked at (0):**

**Derived limits**

| name | status | count |
| --- | --- | --- |
| cage-ratchet-one-way | open | 0 |
| cage-removal-scores-patch | open | 0 |
| cage-not-priced-residual | open | 6 |

**Corpus checksum:** `sha256:4c8a1112fc472cd19c550a2aa9b193bfc00491dea5bc25062b17021bca158da2` &nbsp; **Generator version:** `0.3.0`

### `7.0.0`

| declared | computed | outcome |
| --- | --- | --- |
| `major` | `major` | passed |

**Verdict movement**

| policy | verdict | entries | expressions |
| --- | --- | --- | --- |
| cage-tier.yaml | major | ns-declares-28955523c77f855d, ns-declares-531316544e990e91, ns-declares-93c210e53bf892ee, ns-declares-c901ace43256a7aa, pin-ns-531316544e990e91, pin-ns-8193685ebe9e7df6, tier-ns-0c49faad75bc25ee, tier-ns-531316544e990e91, tier-ns-5ae980404530734f, tier-ns-74cb718cb9db0321, tier-ns-bf9ac596bfe8bff4 | `{'baseline':  {'cpu':'500m','mem':'256Mi','pc':'cage-baseline-7-0-0',  'prio':'-10',   'harden':'false','wafCpu':'0',   'wafMem':'0'},
 'restricted':{'cpu':'250m','mem':'128Mi','pc':'cage-restricted-7-0-0','prio':'-100',  'harden':'true', 'wafCpu':'100m','wafMem':'128Mi'},
 'quarantine':{'cpu':'100m','mem':'64Mi', 'pc':'cage-quarantine-7-0-0','prio':'-1000', 'harden':'true', 'wafCpu':'250m','wafMem':'256Mi'},
 'isolated':  {'cpu':'100m','mem':'64Mi', 'pc':'cage-isolated-7-0-0',  'prio':'-10000','harden':'true', 'wafCpu':'250m','wafMem':'256Mi'}}[variables.tier]; namespaceObject != null && namespaceObject.metadata.?labels['policy-as-versioned.dev/governed'].orValue('') == 'true'
  ? namespaceObject.metadata.?labels['posture.acme.io/tier'].orValue('')
  : ''; variables.nsTier in ['baseline', 'restricted', 'quarantine', 'isolated']
  ? variables.nsTier
  : 'isolated'` |
| posture-trust-boundary.yaml | removed | (structural, no fixture moved) | `variables.posture == variables.claimed` |
| require-nonroot.yaml | none | (structural, no fixture moved) | `variables.nonroot || (variables.attested && variables.hardened)` |

**Counts:** old=174 new=140 union=180

**Not looked at (0):**

**Derived limits**

| name | status | count |
| --- | --- | --- |
| cage-ratchet-one-way | open | 1 |
| cage-removal-scores-patch | open | 1 |
| cage-not-priced-residual | open | 6 |

**Corpus checksum:** `sha256:488de902f1feeb73b0a5efd9dd5c5cca04bc9ba29ec342f9724c603d21e45977` &nbsp; **Generator version:** `0.3.0`

- 6.0.0: publisher declared 'major', computed 'major'
- 7.0.0: publisher declared 'major', computed 'major'
- acceptance: 6.0.0 is a major, accepted for driftwood by chrisns (owner); decision delegated to the implementing assistant on 2026-10-03: "you tell me, you control them all, you don't need me to answer"; recorded by the integrator on 2026-10-03 (accepted-majors/platform-6.0.0.yaml at aa923631de95)
- acceptance: 7.0.0 is a major, accepted for driftwood by chrisns (owner); decision delegated to the implementing assistant on 2026-10-03: "you tell me, you control them all, you don't need me to answer"; recorded by the integrator on 2026-10-03 (accepted-majors/platform-7.0.0.yaml at aa923631de95)
