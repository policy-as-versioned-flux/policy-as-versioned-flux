# 01 — Policy inherits across parties, not just across versions

Type: prototype
Status: resolved
Blocked by: none

Was `computed-semver`'s ticket 09. Moved here when that map's own warning applied to it: composition
is a compliance architecture, and only one line of it is release-gate business. It supersedes the
question [`computed-semver` ticket 06](../../computed-semver/issues/06-does-inheritance-earn-its-place.md)
wrote down. See that ticket's Correction.

## Question

Can a party's effective policy set be **inherited from other parties**, the way a class inherits, so
policy is a dependency you **extend and mash up** rather than only pin? Does the result still render
down to the flat, per-version, `matchConditions` self-scoping files Kyverno runs today?

## Answer

**Yes, and it is a real and missing layer.** Prototype: `spikes/cs-06b-cross-party-composition/` —
`./run.sh`, exit 0, self-checking.

Parents are of **different kinds**, and that is the part a flat pin model cannot express:

- `nist` publishes **controls**. The abstract base. It says what must hold, never how.
- `platform` ships **implementations**. The concrete class.
- `ico` publishes **pricing**. It prices the consequence and ships no rules.
- `feeds` publishes **threat**, CVE and EOL. It moves that price and ships no rules.
- `driftwood` is the **subclass**. It inherits several, and that is the **diamond**, live today:
  `driftwood -> platform -> nist` and `driftwood -> nist`.

**The render-down constraint holds, and is asserted rather than asserted about.** The whole inherited
body is carried. The composition adds one label and two annotations, all advisory. Strip them and the
committed file is what remains, checked for all three policies.

### Four gaps in the committed estate — but be exact about what composition adds

1. **`cm-6`'s only claimed evidence is `require-policy-version`. No `ValidatingPolicy` of that name
   exists.** The real guard is `policy-version-orphan-guard`. The name appears only in
   `oscal/component-definition.json` and in a hand-authored fixture `PolicyReport`, which is why the
   up-flow passes. **A plain lint finds this. Composition is not required.**
2. **`ac-6` claims `may-run-root-if-attested`, which Flux never installs.** It lives in
   `policy/policies/` and `versions.yaml` reconciles only `./distribution/policies/v<version>`.
   Reported as OVERCLAIMED, not uncovered: `require-nonroot` still covers `ac-6`. **A lint finds this
   too.**
3. **The component definition's control ids match neither the catalogue's case nor its lack of a
   prefix** (`nist-800-53:AC-6` against `ac-6`). **LATENT, not live**: nothing in the estate resolves
   one against the other today. It breaks the resolver this prototype proposes. And the prototype's
   own case-folding is checked against a baseline hand-authored in the prefixed form, so the cure is
   untested against the real catalogue.
4. **Nothing declares a baseline.** `nist` ships 1196 controls; the estate implements two. **This is
   the one that needs composition**: a baseline is what catches a required control nothing claims,
   which is the `ac-6.10` scenario.

Composition also surfaces `computed-semver`'s two-trees open question. Version `1.0.0` is declared by
both `distribution` and `policy`. Both self-scope on `policy-version: 1.0.0`, so both would judge the
same pod. Only one installs.

### A subclass never overrides. It gets an informed cage.

**There is no most-derived-wins branch, and there is never an exemption.** A subclass that cannot meet
an inherited rule declares the inability. The estate's own `graded/cage.py` prices the residual against
**that party's** band from `risk/appetite.json` and picks the loosest cage that fits. Deny is the
bottom rung, reached by the money. Priced from `policy/scenarios/driftwood-root-residual.json`:

| party | band £/yr | tier | residual | + controls | = TCoR |
|---|---:|---|---:|---:|---:|
| `driftwood` | 40,000 | `baseline` | 14,952 | 500 | 15,452 |
| `tuppence` | 15,000 | `baseline` | 14,952 | 500 | 15,452 |
| `ludlow` | 5,000 | `quarantine` | 1,709 | 6,000 | 7,709 |

The band is compared against the **residual**, not the TCoR: the cage's run-cost is a booked cost, not
retained risk. Same rule, same inability, three answers. That is proportionality.

Two caveats on that table. `tuppence` fits `baseline` by about £48 on a Monte-Carlo output. And the
rule it cannot meet is `may-run-root-if-attested`, which gap 2 proves is never installed.

### Caging settles one case, not the general one

Caging settles a **child that cannot meet a parent**. It says nothing about **two parents whose rules
disagree**, which is the case override semantics exist for. An earlier draft said "the diamond needs no
override rule: divergence is priced, not merged". That fused two mechanisms and is **withdrawn**: the
conflict is *refused*, and what is priced is not the conflict. The prototype now detects a rule
supplied by two sources with different content and refuses instead of taking the last silently. It is
**untested across parties**, because the estate has one implementations publisher.

### Informed, and the line it must not cross

The pricing and threat parents are genuinely consumed, through the publishers' own converters:

| source | uncaged exposure | decision |
|---|---:|---|
| `ico` penalty-schema `v1` (`uk-gdpr lower-tier`) | £16,901,472 | Deny |
| `ico` penalty-schema `v2` | £9,039,791 | Deny |
| `threat-register v1` (tuppence) | £222,574 | Deny |
| `threat-register v2` (tuppence) | £326,139 | Deny |

**The price moves. The decision does not.** On the estate's real feeds and real bands, no feed bump
changes a cage decision. The wiring is proved. The outcome claim is not.

The EOL feed is time-varying, so the same `python-3.9` workload prices `baseline -> restricted ->
quarantine` as it ages, with nothing edited at all. **An earlier draft called that a feature. It would
violate a decided ADR.** `ADR-0006`'s extension allows timed nudges only "as long as nothing timed ever
changes an admission verdict on its own, and every resulting change still lands via a reviewed,
human-merged PR". `ADR-0010` says the same. And `computed-semver` ticket 02 settled that the cage
**spec is** the verdict. So a self-tightening cage is a timed verdict change and is forbidden. Each row
is a **proposed** tier for the agent governance layer to raise as a PR. The prototype does not
implement the proposer.

## The one fact this owes `computed-semver`

**The bump is a property of a composition, not of a file**, so the gate computes it **after**
composition. A regulator's addition is a downstream build break. A retired array element is a
downstream major with **no policy diff at all**. `cs-01`'s method is **extended, not unchanged**: its
verdict-movement half works as-is on composed sets, but a composition also refuses on **coverage** with
zero verdict movement, which is a second structural axis. The publisher still tags **one** bump at the
strictest band with the per-institution matrix as evidence, exactly as `cs-02` settled; composition is
the mechanism behind that matrix.

## Not yet specified

Carried to [the map](../map.md): signing a composed artefact, who declares the baseline and in which
id form, whether an unlabelled pod is denied, the proposer, and composing the five unversioned live
policies the prototype does not reach.
