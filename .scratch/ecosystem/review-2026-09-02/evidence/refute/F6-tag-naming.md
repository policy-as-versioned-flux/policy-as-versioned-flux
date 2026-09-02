# Skeptic pass on F6 — "Two tag-naming schemes coexist ... and the tooling models one"

Verdict: **REFUTED as stated.** The observable tag facts hold; four of the five load-bearing
inferences do not. A narrower, real defect survives (see "What survives").

## What I re-derived, and what held

Command: `git -C <clone> tag -l` in the eight fresh unit clones.

    feeds:    threat-register/v1.0.0, threat-register/v2.0.0
    platform: policy/v2.0.0 policy/v2.0.1 policy/v3.0.0 policy/v4.0.0 + v0.1.0 v0.1.1 v1.0.0 v1.1.0 v1.1.1 v2.0.0 v2.0.1
    insurer:  v1.0.0            (the only tag)
    ico:      v1.0.0 v3.0.0     nist: v1.0.0 v1.1.0     driftwood/tuppence/ludlow: v1.0.0 v1.1.0

HOLDS: feeds tags per-feed; platform runs two lines; insurer's only real tag is repo-level.
HOLDS: `insurer/quote/{driftwood,tuppence,ludlow}/bump.yaml:4` each say "cut-release.yml signs
the tag quote-<adopter>/vX.Y.Z". Stronger than the auditor found: `insurer/.github/workflows/
fetch.yml:323` puts the same instruction in the live PR body the clock opens.
HOLDS: `insurer/party.yaml:60-77` publishes three feeds. Citation is exact.
NEAR: the platform special case is `cut-release-gate.py:14-22`, not 16-23.

## Leg 1 — "the tooling models one". FALSE.

`verify/feed-contract/feed_contract.py:64-71`:

    def tag_forms(entry, version):
        """The tag shapes a publisher may sign this pin with. `<name>/vX.Y.Z` (feeds, and the
        platform's policy/vX.Y.Z line) or bare `vX.Y.Z` (single-feed repos: ico, nist). Both are
        tried and the PASS line says which one matched. ..."""
        return re.compile(rf"^(?:{re.escape(entry['name'])}/)?v{ver}$")

The prefix group is optional on purpose and the docstring names both schemes. Re-ran the two
functions standalone (jsonschema is absent, ticket 54's known gap, so I reimplemented the
6 lines verbatim rather than import):

    pattern for pin v1: ^(?:quote\-driftwood/)?v1\.\d+\.\d+$
    insurer real tag v1.0.0            -> v1.0.0
    hypothetical quote-driftwood/v1.2.0 -> quote-driftwood/v1.2.0
    feeds threat-register v2           -> threat-register/v2.0.0
    platform policy 2.0.1              -> policy/v2.0.1

The tooling models both, deliberately and documented.

## Leg 2 — "breaks the ESLint packaging model". CONTRADICTED by the estate's own ratified mapping.

The unit is the PARTY, not the feed. `.scratch/ecosystem/research/06-eslint-versioning-semantics.md:257`:
"npm package, its own semver | **A party's published artefact** at its own gitsign tag — `nist`,
`platform`, an adopter's composed set | Same. Re-grill 2 ratifies it." Part 3 rule 1: "**Every
party versions itself, on its own clock.**" Ticket 06 is Status: resolved.

Part 4 of that note is titled "Every place the estate disagrees today" and enumerates 17 rows.
Tag naming is not one of them. Under the estate's own ratified reading, insurer holding three
feeds under one party tag IS the model, not a break of it.

## Leg 3 — "no ownership found". FALSE. Ticket 14, answer 4 owns it explicitly.

`.scratch/ecosystem/issues/14-insurance-and-the-insurer-party.md:58` (Q4) states the baseline:
"ADR-0019 makes a release one gitsign-signed semver tag on the publisher repo, **so one tag
versions everything in the repo**" — then offers (a) one `quote` feed, (b) one feed name per
adopter with **one tag line**, (c) one repo per adopter. Line 85 records the owner picking (b),
with the rationale: "each adopter pins exactly its own cover; a foreign re-price lands as
`changed: false`."

So the repo-level tag is the decided scheme with a recorded rationale, and the exact harm the
finding predicts is the consequence that was weighed and accepted. `insurer/party.yaml:54-59`
restates it: "one tag line (ticket 14 answer 4) ... a tag that re-priced only another adopter
lands in its prices[] as an honest no-change."

This also inverts the finding's framing. Per ADR-0019 as ticket 14 reads it, repo-level is the
default; `feeds`' per-feed tag is the *departure*, and `feeds/.github/workflows/cut-release.yml:5-8`
is the only place in the estate that states the departure's rule: "this repo publishes MORE THAN
ONE feed, so the tag is `<feed-name>/vX.Y.Z` ... Single-feed repos like ico stay on plain
`vX.Y.Z`." (grep for that rule across the hub returns nothing; ADR-0019 itself says nothing about
tag naming beyond point 2, "The signature is the gitsign tag".)

## Leg 4 — "tuppence and ludlow pin the artefact". FALSE.

Only driftwood pins an insurer feed. `driftwood/party.yaml:61`:
`{ party: insurer, kind: feed, name: quote-driftwood, version: "v1" }`.
`tuppence/party.yaml:26-29` and `ludlow/party.yaml:27-30` list platform, nist, ico, feeds — no
insurer entry at all. The renumbering harm cannot obtain today, and the pin is bare-major ("v1"),
which resolves to any v1.x.y under either scheme.

## Leg 5 — the clock-failure causation. WRONG CAUSE.

`gh run list -R policy-as-versioned-insurer/insurer` — two scheduled runs, both failure
(33496526156 2026-09-01T10:16Z, 33615860064 2026-09-02T09:45Z). But `gh run view 33615860064`
shows the driftwood matrix leg **passing** ("ok  this clock proposed, and declared nothing").
The two failing legs are tuppence and ludlow, at "re-price and compute the bump under the feed's
own rule.yaml", with:

    REFUSED: missing instrument: .adopters/tuppence/composed/HEADER.yaml carries no `exposure`
    section -- there is no signed exposure to attach a layer to

That is a missing-instrument refusal, unrelated to tag naming. The re-quote leg that would
actually exercise the scheme is the one that passes.

## What survives (the corrected, narrower claim)

Inside insurer, two live instructions contradict the signed artefact and the decision it cites:
`quote/*/bump.yaml:4` (x3) and `fetch.yml:323` tell a human to dispatch `cut-release.yml` with
`quote-<adopter>/vX.Y.Z`, while `party.yaml:54-59` declares one tag line per ticket 14 answer 4
and the only real tag is `v1.0.0`. Unlike `feeds`' workflow (which validates the input and builds
the prefix itself, cut-release.yml:70-80), insurer's `cut-release.yml` takes a free-form `version`
and validates only that the tag does not already exist — so following the PR body opens a second
tag line with nothing to stop it. Latent consequence: `feed_contract.py:74-77` picks the highest
match by numeric version and ignores the prefix, so a repo running both lines could resolve a pin
across schemes silently. Nothing owns reconciling insurer's stale per-quote text with its decision.

Ticket 57's step-4 note ("insurer (version HAS a leading v — the two workflows differ)",
issues/57:69) does **not** evidence a naming-scheme divergence: it records the leading-v input
convention, because feeds' workflow refuses a leading v and adds it (feeds cut-release.yml:73-75)
while insurer's takes the whole tag string. Using it as scheme evidence overstates it.
