# 03 — Who declares the baseline, and against which catalogue ids

Type: grilling
Status: resolved
Blocked by: none

Graduated from the map's Not yet specified: "Who declares the baseline, and against which catalogue
ids." Ticket [`01`](01-does-composition-hold-up.md) found the id-form mismatch as latent: the
prototype's `nist-800-53:AC-6` form matches neither the catalogue's case nor its lack of a prefix.

## Question

Who declares the baseline, a regulator, a publisher, or an adopter, and in which document does that
declaration live? Against which catalogue id form must a control id be checked, so the resolver
ticket `01` proposes stops failing silently on a case or prefix mismatch?

## Answer

**The regulator publishes named baselines. The adopter selects one. Both are keyed by the bare
catalogue id.** Recorded as
[ADR-0013](../../docs/adr/0013-regulator-publishes-baselines-adopter-selects.md), with two new terms
in `CONTEXT.md`.

### Facts the decision rests on

Gathered before the grilling, from the committed estate and the vendored c2p test data.

| Fact | Evidence |
|---|---|
| The catalogue id form is bare and lowercase: `ac-6` | `estate/nist/.work/seed/NIST_SP-800-53_rev5.2.0_catalog.json`, OSCAL `id` |
| The same catalogue ships `AC-6` and `AC-06` as `props[name=label]` display labels | same file, control `ac-6` |
| The estate's own mapping uses a fourth form, `nist-800-53:AC-6` | `estate/platform/oscal/component-definition.json` |
| The `cs-06b` prototype invented a fifth form, `nist-800-53:ac-6` | `material/parties/nist.yaml`, branch `cs-06-cross-party-composition` |
| NIST already publishes baselines as OSCAL **profiles**: they import the catalogue by `href` and list bare ids under `include-controls[].with-ids` | `spikes/c2p-real-job/.work/c2p/internal/oscal/testdata/NIST_SP-800-53_rev5_*-baseline_profile.json` |
| LOW holds 149 controls, MODERATE 287, HIGH 370 | same three files |
| **The estate's two claimed controls straddle two baselines.** `cm-6` is in LOW. `ac-6` is not, and starts at MODERATE | same three files |
| **`ac-6.10` is already in the real MODERATE baseline.** Ticket `01` modelled it as a hypothetical `nist` `v2.0.0` addition | same files, and `material/parties/nist.yaml` |

That last row corrects ticket `01`. The `ac-6.10` scenario needs no catalogue bump to become live. It
is a hole the moment a baseline is selected.

### Who declares it

**The regulator publishes named baselines. The adopter selects one by name.** The declaration is
split, because the two halves answer different questions.

- The **regulator** knows the catalogue. It does not know the system, so it cannot pick.
- The **publisher** knows what it implemented. If it declared the baseline, coverage would be
  tautological: the set of required controls would be defined as the set already covered, and the
  gap ticket `01` calls "the one that needs composition" could never be found.
- The **adopter** pays the £ when a control is missing. Selection is the risk-bearing act, so it
  belongs to the risk-bearer.

The split also preserves ticket `01`'s finding that a regulator's addition is a downstream build
break. A regulator can add a control to a **named** baseline, and every adopter that selected that
name breaks. An adopter that enumerated its own control list would never see the addition.

Baselines are OSCAL profiles. No new format, and the shape NIST already ships.

### Which baseline, and where the selection lives

**MODERATE**, and the selection lives in the adopter's own party artefact, the input it
gitsign-signs under [ADR-0012](../../docs/adr/0012-composed-artefact-self-signed-pinned-sha.md).

LOW is wrong on the facts: `ac-6` falls outside it, so selecting LOW would drop one of the two
controls the estate implements. A bespoke baseline sized to what is implemented is the same
tautology, moved to the regulator. MODERATE means **285 recorded holes on day one**, which the
new-hole rule below makes shippable, and which the map's standing preference calls for saying out
loud.

The selection is a claim the adopter makes about itself, so it belongs in the artefact the adopter
signs. `gitops/apps/nist-pin-configmap.yaml` gains a `baselineName` key and stays what its own
comment says it is: a human and audit readable **mirror**. No new file.

### The adopter may add to the baseline. It may never remove.

OSCAL profiles compose in both directions, so removal had to be ruled out explicitly. A removal is
an exemption by another name, and the map's standing preference says there is never an exemption. A
control the adopter cannot meet goes to the cage and is priced against its own band. It never leaves
the baseline. An addition is allowed, because the adopter is claiming more than it inherited.

### The id form

**The bare catalogue id, exactly as the catalogue writes it.** `ac-6`, never `AC-6`, never
`nist-800-53:AC-6`. `AC-6` stays a display label and is never a key.

The catalogue is identified by the `source` or `href` on the enclosing block, which is what OSCAL
already does and what the real NIST baseline profiles do. The `nist-800-53:` prefix names the
catalogue a second time. Duplicated state is what disagreed in the first place, so the prefix goes.
Two artefacts change: `nist-800-53:AC-6` becomes `ac-6`, and the prototype's `nist-800-53:ac-6`
becomes `ac-6` too.

The `source` href does **not** gain a SHA. The parent pin already carries it, and ADR-0012 records
it once at the top of the composed file. A second copy in the href would re-introduce exactly the
duplication this decision removes. What the href does gain is the **parent party**: today
`estate/platform/oscal/component-definition.json` reads
`estate/nist/catalog/NIST_SP-800-53_rev5.2.0_catalog.json`, a path into another repo written as if
it were local and carrying no version. It must resolve as `nist` plus a path inside `nist`, and the
pin says which `nist`.

### The resolver

**Resolve by exact string against the catalogue. Never case-fold. Never strip a prefix.** An id
absent from the catalogue is a hard failure with the id printed. Forgiving normalisation is how the
mismatch stayed latent, so the cure must not be more of it.

One further requirement, which the catalogue's own shape forces: the resolver must walk **nested**
`controls`. `ac-6.10` is a child of `ac-6`, so a group-level scan misses every enhancement. The
prototype's own case-folding is checked against a hand-authored baseline in the prefixed form, so
that check is void and must be rewritten against the real catalogue.

### A hole refuses only when it is new

MODERATE holds 287 controls and the estate implements 2. A plain refusal on the absolute hole count
would deny the whole estate on day one and for ever, which is not a gate, it is a wall.

So the composition **refuses on a new hole and records a pre-existing one**. The comparison is
against the adopter's last signed composed artefact, which ADR-0012 already makes published,
versioned and signed. This adds no store, and it makes the hole list signed evidence rather than a
scratch file anyone could edit. The output is a count plus a list of ids, which is what
[`computed-semver` ticket 04](../../computed-semver/issues/04-coverage-stated-not-implied.md) already
settled for coverage, and the control id is a stable id already.

Two edges, both stated because a reader would otherwise assume the opposite:

1. **The first composition has no prior artefact.** Treat the prior hole set as empty, so every hole
   is pre-existing. The first composition records all 285 ids and refuses on none. That first signed
   artefact becomes the comparison point for every run after it.
2. **The adopter widening its own selection refuses, and gets no override.** MODERATE to HIGH adds 83
   controls at once, nearly all of them new holes. The refusal is the point: the adopter is claiming
   more, and the composition prices that claim before it lands. It clears the same way any refusal
   clears, in a reviewed PR that either supplies the implementations or accepts the holes onto the
   debt list. There is no "I meant it" flag, because that is an exemption branch.

### What this ticket did not do

The `nist` party ships no baseline today, and the two id-form corrections are edits to the `nist`,
`platform` and adopter repos. That is gap 4 and gap 3 of ticket `01`, and the map already rules
repairing those gaps out of scope. This ticket decided the shape. It shipped no repair.
