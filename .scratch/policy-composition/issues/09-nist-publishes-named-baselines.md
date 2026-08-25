# 09 — `nist` publishes named baselines

Type: task
Status: resolved
Blocked by: none

Source: [`spec.md`](../spec.md), *Baselines, control ids and holes* and *Changes in other repos*.
Decision: [ADR-0013](../../../docs/adr/0013-regulator-publishes-baselines-adopter-selects.md).

## What to build

An adopter selects a baseline by name, and the name resolves to a real signed file. The `nist` party
publishes the three baselines NIST already ships, LOW, MODERATE and HIGH, as OSCAL profiles beside its
catalogue, under the same signed tag.

Every control id in a profile is the bare id the catalogue writes. Each profile names the catalogue
once, by `href`. A verify beat in the `nist` repo resolves every id in every profile against the
catalogue, exact-string, walking nested controls. An id the catalogue does not carry fails the beat.

This is a new `nist` release. Cut it through that repo's ordinary release path, so the tag is
gitsign-signed and Renovate can pin it.

## Acceptance criteria

- [ ] `nist` ships LOW, MODERATE and HIGH as OSCAL profile files under its release tag.
- [ ] MODERATE resolves 287 controls, and holds `ac-6`, `cm-6` and `ac-6.10`.
- [ ] LOW does not hold `ac-6`. The beat proves the fact the estate's selection rests on.
- [ ] Every id in every profile is bare. No upper case, no prefix.
- [ ] The verify beat resolves every profile id against the catalogue with no case-folding and no prefix-stripping, and walks nested controls.
- [ ] A profile carrying an id absent from the catalogue fails the beat. A fixture proves it.
- [ ] The release is a gitsign-signed tag that a Renovate `customManager` can pin.

## Answer

**Built.** LOW, MODERATE and HIGH now sit beside the catalogue in the `nist` repo
(`.estate-clone/nist` locally; `policy-as-versioned-nist/nist` upstream), as OSCAL profiles fetched
verbatim from `usnistgov/oscal-content` rev 5.2.0 and re-hosted so the party's own tag is the pin:

- `catalog/NIST_SP-800-53_rev5.2.0_{LOW,MODERATE,HIGH}-baseline_profile.json`
- `catalog/BASELINE_VERSIONS.json` — provenance (upstream URL template, fetch date, per-baseline
  file/controlCount/sha256), same shape as `CATALOG_VERSION.json`.
- `CATALOG_VERSION.json` bumped 1.0.0 → 1.1.0 (catalogue file itself unchanged).
- `scripts/verify_baselines.py`, wired into `scripts/verify-catalog.sh`, walks every profile's
  `imports[].include-controls[].with-ids` (nested groups included) and resolves each id against the
  catalogue by exact string, no case-fold, no prefix-strip. `scripts/fixtures/profile-with-unknown-id.json`
  carries `zz-999`; the beat fails on it as required.
- `README.md` documents the baselines and points at ADR-0013 for why selection is the adopter's act.

Verified locally (`bash scripts/verify-catalog.sh`): LOW resolves 149 controls and excludes `ac-6`;
MODERATE resolves 287 and holds `ac-6`, `cm-6` and `ac-6.10`; HIGH resolves 370. All ids bare, all
profiles name the catalogue once by `href`.

**Outstanding — the review gate did not fully pass.** The acceptance criterion that the release be
cut through the `nist` repo's ordinary path as a gitsign-signed tag is **not met**. `scripts/publish.sh`
only seeds and tags a local `.work` clone (an offline pin, per its own comment) — it neither pushes
to the real `policy-as-versioned-nist/nist` remote nor produces a Sigstore/gitsign signature, and
this environment holds no signing identity or CI to do either. The `nist` repo's changes above
(README, `CATALOG_VERSION.json`, `verify-catalog.sh`, and every new baseline/provenance/fixture file)
are still **uncommitted** in that repo — verified locally only. Cutting `v1.1.0` for real needs
someone with push access to `policy-as-versioned-nist/nist` to commit there and run its release
workflow so the tag comes out gitsign-signed and pinnable by Renovate.

No new ADR — this implements the selection-by-name decision ADR-0013 already recorded; nothing new
to decide.
