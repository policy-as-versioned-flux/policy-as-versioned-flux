# verify/engine-pairing — composition prices an unsupported engine pairing (eco-system ticket 148)

Hub ADR-0033 point 3. An adopter declares its engine in its own `gitops/engine/kyverno.yaml`. A
composed policy line supports exactly the engines its element of platform
`distribution/versions.yaml` lists in `tested_engines`, and the machinery the engines in
`distribution/machinery.yaml`, in the platform tree the adopter composes against. On an engine a
line does not support, its claims do not count: every control it claims is a hole, priced as
ADR-0026 prices one, and an `unsupported-engine` delta names the pairing. No declaration is
priced the same way under `undeclared-engine`, and a declaration that does not read refuses.

`verify-engine-pairing.sh` runs the platform composer the estate serves through its own CLI (the
operation each adopter's compose-check runs) on copies of the adopters' committed trees:

- **planted**, on a copy of driftwood: its own declaration (no engine delta); an engine from the
  platform engine table that the composed line does not list (one `unsupported-engine` delta whose
  amount is the sum of the hole prices of the controls the line claims); the same with a planted
  platform claim of a weighted control on a line body, so the price is a number, and the regime
  entry's open amount must rise by exactly that hole; no declaration (`undeclared-engine` for the
  line and the machinery); and a malformed declaration (a `missing-instrument` refusal naming the
  file);
- **forward**, each real adopter's committed tree composed now against the served platform tree:
  what its artefact will say once its tools pin and its implementations pin move to a tag cut from
  that tree;
- **served**, each real adopter's committed `composed/`: the header's `declared-engine` equals its
  file, and the engine deltas are exactly the pairings the platform tree at its pinned
  implementations commit does not support.

Every expected figure is derived here: the bodies from the objects the composer rendered, the
claims from the platform's own `oscal/component-definition.json`, the support from each
`tested_engines` value read by this check's own reading of ADR-0033 point 1, and each hole's price
from the regulator's partition on the feed entry, which a pairing does not move.

Measured on 2026-09-26: the regulator's weights name pl-2, ra-3, ca-2 and ir-8, and the estate's
two claims are ac-6 (5.0.0's `require-nonroot`) and cm-6 (the machinery's
`governed-namespace-requires-claim`). So on the real claims an unsupported pairing carries
`amount: null`, and only the planted weighted claim shows a number move.

The served case reads could-not-look until each adopter recomposes under a platform composer that
carries ticket 148: an artefact composed before it carries no `declared-engine`.

```sh
./verify-engine-pairing.sh               # the estate in .estate-clone/ (or PAVC_ESTATE_CLONE)
./verify-engine-pairing.sh --selfcheck   # planted evidence: each grading rule bites
```
