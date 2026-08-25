# 11 — The party artefact, and the three adopters declare themselves

Type: task
Status: resolved
Blocked by: 09

Source: [`spec.md`](../spec.md), *The party artefact*, *Governed namespaces*, *Changes in other
repos*. Decisions: [ADR-0012](../../../docs/adr/0012-composed-artefact-self-signed-pinned-sha.md),
[ADR-0013](../../../docs/adr/0013-regulator-publishes-baselines-adopter-selects.md),
[ADR-0018](../../../docs/adr/0018-the-namespace-manifest-is-the-governed-declaration.md).

## What to build

Each adopter declares itself once, in a signed file, and the composition has something to read.

The party artefact format is the shape the prototype proposed in its per-party material, promoted to
a real format. It carries the party name, the roles, the parents as party plus kind plus version, the
selected baseline name, and an overlay with `add` and `restate` lists. The parent kinds are
`controls`, `implementations`, `pricing` and `threat`. The parent version is the tag the adopter
already pins in its Flux and Renovate files. A schema and a check that the declared tags match the
pinned tags live with the format, in `platform`, because the adopters call it through their pin.

Each of `driftwood`, `tuppence` and `ludlow` then gains three things. A party artefact selecting
MODERATE. The `policy-as-versioned.dev/governed: "true"` label on its `Namespace` manifest. A
`baselineName` key in its existing `nist` pin ConfigMap, as an advisory mirror.

From the prototype, the decision-rich part of the shape:

```yaml
party: driftwood
roles: [risk-bearer, adopter]
baseline: MODERATE            # selected by name; may add, never remove
inherits:
  - { party: platform, kind: implementations, version: "0.1.0" }
  - { party: nist,     kind: controls,        version: "1.0.0" }
  - { party: ico,      kind: pricing,         version: "1.0.0" }
  - { party: platform, kind: threat,          version: "v1" }
overlay:
  add: []
  restate: []
```

## Acceptance criteria

- [ ] A party artefact schema exists in `platform`, with a self-check.
- [ ] A check fails when a declared parent version disagrees with the tag the adopter's Flux or Renovate files pin.
- [ ] A check fails on a parent kind outside the four.
- [ ] Each of the three adopters commits a party artefact selecting MODERATE.
- [ ] Each adopter's `Namespace` manifest carries `governed: "true"`.
- [ ] Each adopter's `nist` pin ConfigMap carries `baselineName`, and a check fails when it disagrees with the party artefact.
- [ ] Each adopter's shift-left check runs the party artefact check on every pull request.

## Answer

**Built**, in `platform` and all three adopters (`.estate-clone/{platform,driftwood,tuppence,ludlow}`
locally; `policy-as-versioned-platform/platform` and the three adopter repos upstream):

- `platform/party/schema.json` (new) — the single source of truth for the four parent kinds
  (`controls`, `implementations`, `pricing`, `threat`) and the three roles; `party_artefact.py` reads
  its enums from this file rather than re-declaring them, so the two can never drift apart.
- `platform/party/party_artefact.py` (new) — `validate_schema()` checks structural shape against
  `schema.json` (missing field, kind outside the four, role outside the three, unknown top-level
  field, non-mapping document, all refused, not crashed on); `check_tags()` compares each declared
  `(party, kind)` version against the tag the adopter's own Flux files actually pin
  (`gitops/platform/platform-pin.yaml` for `platform/implementations`,
  `gitops/flux-system/gotk-sync-nist.yaml` for `nist/controls`), and names `ico/pricing` and
  `platform/threat` as `NOTE: … unchecked` rather than silently skipping them, since neither has a
  Flux/Renovate pin anywhere in this estate today; `check_baseline_mirror()` compares
  `party.yaml`'s `baseline` against the adopter's `nist-pin-configmap.yaml`'s `data.baselineName` and
  refuses a disagreement or a missing key. `check()` composes all three, in order, against a real
  `party.yaml` on disk. A `check` CLI subcommand takes `party_yaml`, `--adopter-dir` and
  `--nist-configmap`. `--selfcheck` runs 15 asserts covering every negative path the acceptance
  criteria name (tag mismatch, bad parent kind, bad role, missing field, missing pin file, disagreeing/
  missing baseline mirror) plus the two end-to-end paths (a real party.yaml passing, a structurally
  invalid one refused before touching any pin file).
- `platform/party/README.md` — documents the format and the check, with the `NOTE:` convention for
  the two currently-unpinned kinds called out plainly.
- Each of `driftwood`, `tuppence` and `ludlow` gained:
  - `party.yaml` (new) — `party`, `roles: [risk-bearer, adopter]`, `baseline: MODERATE`, and
    `inherits` naming `platform/implementations@0.1.0`, `nist/controls@1.0.0`, `ico/pricing@v1` and
    `platform/threat@v1`, matching the prototype's shape from `spec.md`.
  - `gitops/apps/namespace.yaml` — gained the `policy-as-versioned.dev/governed: "true"` label
    (ADR-0014/ADR-0018's governed declaration).
  - `gitops/apps/nist-pin-configmap.yaml` — gained `data.baselineName: "MODERATE"`, the advisory
    mirror of `party.yaml`'s `baseline`.
  - `.github/workflows/shift-left.yml` — gained a "party artefact check (ticket 11)" step, running
    `platform/party/party_artefact.py check <adopter>/party.yaml --adopter-dir <adopter>` through the
    job's already-checked-out pinned `platform` dependency, positioned after that checkout and before
    `ci-check.py`.

Verified locally: `party_artefact.py --selfcheck` passes all 15 asserts. The real `check` subcommand
run against each of driftwood's, tuppence's and ludlow's actual `party.yaml`, Flux pin files and
`nist-pin-configmap.yaml` passes end to end for all three, each correctly emitting
`NOTE: ico/pricing@v1: … unchecked` and `NOTE: platform/threat@v1: … unchecked` (not failures, since
neither kind is Flux/Renovate-pinned in this estate) before `OK: <adopter>/party.yaml is a valid party
artefact; pinned tags and the baseline mirror agree`.

**Outstanding.** As with tickets 09 and 10, everything above is verified locally only — not committed
in any of the four repos. `platform/party/` is untracked; each adopter shows modified
`shift-left.yml`, `namespace.yaml` and `nist-pin-configmap.yaml` plus an untracked `party.yaml` in
`git status`. Landing this for real needs someone with push access to
`policy-as-versioned-platform/platform` and to each of the three adopter repos to commit there and
merge, the same open question tickets 09 and 10 already recorded for `nist` and `platform`.

No new ADR — this implements ADR-0012 (self-signed, no new mechanism), ADR-0013 (baseline selected by
name) and ADR-0018 (the namespace manifest is the governed declaration) already recorded; nothing new
to decide.
