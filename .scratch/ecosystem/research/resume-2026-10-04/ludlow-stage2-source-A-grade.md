<!-- cs-29:adopter-gate:start -->
### computed-semver adopter gate

platform pin: `v4.0.0` -> `v5.0.0`

| | declared (publisher's tag) | composed (this institution) |
|---|---|---|
| bump | **major** | **major** |

**Composed major, admitted: every major this pull request adds is accepted** (records under `accepted-majors/`):
- 6.0.0 is a major, accepted for ludlow by chrisns (owner); decision delegated to the implementing assistant on 2026-10-03: "you tell me, you control them all, you don't need me to answer"; recorded by the integrator on 2026-10-03 (accepted-majors/platform-6.0.0.yaml at 4f81da7eca50)
- 7.0.0 is a major, accepted for ludlow by chrisns (owner); decision delegated to the implementing assistant on 2026-10-03: "you tell me, you control them all, you don't need me to answer"; recorded by the integrator on 2026-10-03 (accepted-majors/platform-7.0.0.yaml at 4f81da7eca50)

#### policy `6.0.0`

| | declared | computed |
|---|---|---|
| bump | major | **major** |

**Per-policy verdict movement:**
- `cage-tier.yaml` -- **major** -- entries: ns-declares-59829f76d3b29fcf, ns-declares-cd63cae85c704526, ns-declares-e26bc608d993079b, ns-declares-e8aeacb70872dd4f, pin-ns-8193685ebe9e7df6, pin-ns-cd63cae85c704526, tier-ns-1d7cc48d73927cc4, tier-ns-416fc5dec79317c2, tier-ns-7822fc1973cd9a67, tier-ns-cd63cae85c704526, tier-ns-dcd899efe48bd12d -- via `{'baseline':  {'cpu':'500m','mem':'256Mi','pc':'cage-baseline-6-0-0',  'prio':'-10',   'harden':'false','wafCpu':'0',   'wafMem':'0'},
 'restricted':{'cpu':'250m','mem':'128Mi','pc':'cage-restricted-6-0-0','prio':'-100',  'harden':'true', 'wafCpu':'100m','wafMem':'128Mi'},
 'quarantine':{'cpu':'100m','mem':'64Mi', 'pc':'cage-quarantine-6-0-0','prio':'-1000', 'harden':'true', 'wafCpu':'250m','wafMem':'256Mi'},
 'isolated':  {'cpu':'100m','mem':'64Mi', 'pc':'cage-isolated-6-0-0',  'prio':'-10000','harden':'true', 'wafCpu':'250m','wafMem':'256Mi'}}[variables.tier]; namespaceObject != null && namespaceObject.metadata.?labels['policy-as-versioned.dev/governed'].orValue('') == 'true'
  ? namespaceObject.metadata.?labels['posture.acme.io/tier'].orValue('')
  : ''; variables.nsTier in ['baseline', 'restricted', 'quarantine', 'isolated']
  ? variables.nsTier
  : 'isolated'`
- `posture-trust-boundary.yaml` -- **none** -- entries: (structural, no fixture moved) -- via `variables.posture == variables.claimed`
- `require-nonroot.yaml` -- **none** -- entries: (structural, no fixture moved) -- via `variables.nonroot || (variables.attested && variables.hardened)`

**Counts:** old=174 new=168 union=180 -- coverage cells=36 pairs=180 pairwise_gap=axes were combined pairwise (predicate-expression x version-pin, predicate-expression x tier-label, and every pair among version-pin, tier-label, namespace and workload-declares), so no three-way interaction was built; predicate-expression x namespace was not built because no subject predicate reads a Namespace (corpus_generator fails generation the day one does), and predicate-expression x workload-declares was not built because the declared-hardening axis writes the same container securityContext fields the expression axis's own probes already write

**Not-looked-at (holes):**
- (none)

**Derived limits:**
- cage-ratchet-one-way (open, count=0) -- the cage only ever tightens or holds under this rule -- nothing widens it back automatically once a workload's posture recovers, a structural one-way ratchet (cage_engine.py's RANK table). Kept open by decision, not by this count reaching zero.
- cage-removal-scores-patch (open, count=0) -- the rule reads only the workload's own side of the comparison, so removing or loosening enforcement classifies no higher than patch even though it widens what is admitted. Kept open by decision.
- cage-not-priced-residual (open, count=6) -- nothing in this corpus maps a pod to a priced residual -- the tier axis is synthetic (corpus_generator.TIER_VALUES), so the cage half of Track 2 is proved on synthetic input, never a real infrastructure capture. The check that would remove it: witness_set's real-infrastructure witnesses.

**Per-institution matrix:**
- (none recorded)

**Corpus checksum:** `sha256:4c8a1112fc472cd19c550a2aa9b193bfc00491dea5bc25062b17021bca158da2` -- **generator_version:** `0.3.0`

#### policy `7.0.0`

| | declared | computed |
|---|---|---|
| bump | major | **major** |

**Per-policy verdict movement:**
- `cage-tier.yaml` -- **major** -- entries: ns-declares-28955523c77f855d, ns-declares-531316544e990e91, ns-declares-93c210e53bf892ee, ns-declares-c901ace43256a7aa, pin-ns-531316544e990e91, pin-ns-8193685ebe9e7df6, tier-ns-0c49faad75bc25ee, tier-ns-531316544e990e91, tier-ns-5ae980404530734f, tier-ns-74cb718cb9db0321, tier-ns-bf9ac596bfe8bff4 -- via `{'baseline':  {'cpu':'500m','mem':'256Mi','pc':'cage-baseline-7-0-0',  'prio':'-10',   'harden':'false','wafCpu':'0',   'wafMem':'0'},
 'restricted':{'cpu':'250m','mem':'128Mi','pc':'cage-restricted-7-0-0','prio':'-100',  'harden':'true', 'wafCpu':'100m','wafMem':'128Mi'},
 'quarantine':{'cpu':'100m','mem':'64Mi', 'pc':'cage-quarantine-7-0-0','prio':'-1000', 'harden':'true', 'wafCpu':'250m','wafMem':'256Mi'},
 'isolated':  {'cpu':'100m','mem':'64Mi', 'pc':'cage-isolated-7-0-0',  'prio':'-10000','harden':'true', 'wafCpu':'250m','wafMem':'256Mi'}}[variables.tier]; namespaceObject != null && namespaceObject.metadata.?labels['policy-as-versioned.dev/governed'].orValue('') == 'true'
  ? namespaceObject.metadata.?labels['posture.acme.io/tier'].orValue('')
  : ''; variables.nsTier in ['baseline', 'restricted', 'quarantine', 'isolated']
  ? variables.nsTier
  : 'isolated'`
- `posture-trust-boundary.yaml` -- **removed** -- entries: (structural, no fixture moved) -- via `variables.posture == variables.claimed`
- `require-nonroot.yaml` -- **none** -- entries: (structural, no fixture moved) -- via `variables.nonroot || (variables.attested && variables.hardened)`

**Counts:** old=174 new=140 union=180 -- coverage cells=27 pairs=180 pairwise_gap=axes were combined pairwise (predicate-expression x version-pin, predicate-expression x tier-label, and every pair among version-pin, tier-label, namespace and workload-declares), so no three-way interaction was built; predicate-expression x namespace was not built because no subject predicate reads a Namespace (corpus_generator fails generation the day one does), and predicate-expression x workload-declares was not built because the declared-hardening axis writes the same container securityContext fields the expression axis's own probes already write

**Not-looked-at (holes):**
- (none)

**Derived limits:**
- cage-ratchet-one-way (open, count=1) -- the cage only ever tightens or holds under this rule -- nothing widens it back automatically once a workload's posture recovers, a structural one-way ratchet (cage_engine.py's RANK table). Kept open by decision, not by this count reaching zero.
- cage-removal-scores-patch (open, count=1) -- the rule reads only the workload's own side of the comparison, so removing or loosening enforcement classifies no higher than patch even though it widens what is admitted. Kept open by decision.
- cage-not-priced-residual (open, count=6) -- nothing in this corpus maps a pod to a priced residual -- the tier axis is synthetic (corpus_generator.TIER_VALUES), so the cage half of Track 2 is proved on synthetic input, never a real infrastructure capture. The check that would remove it: witness_set's real-infrastructure witnesses.

**Per-institution matrix:**
- (none recorded)

**Corpus checksum:** `sha256:488de902f1feeb73b0a5efd9dd5c5cca04bc9ba29ec342f9724c603d21e45977` -- **generator_version:** `0.3.0`
<!-- cs-29:adopter-gate:end -->
