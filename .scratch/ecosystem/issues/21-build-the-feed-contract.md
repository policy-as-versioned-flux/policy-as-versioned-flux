# 21 — Build the feed contract

Type: task (AFK)
Status: open
Blocked by: 04

## Question

Make ticket 04 real in the estate. Write `platform/feeds/schema.json` and one payload schema per existing feed. Migrate the five live feeds and the ico penalty schema into the envelope. Open `inherits[].kind` to `controls | implementations | feed` plus `name`, and add `since`. Add `party.yaml` with `roles: [publisher]` and `publishes[]` to platform, nist, ico, feeds and insurer. Move threat, CVE, EOL and market intel out of platform into the `feeds` repo, released by gitsign tag from its workflow. Rename `signing_key_present` to `verification_key_present` and add a real `can_publish`. Definition of done: a `verify-feed-contract.sh` that the gate discovers, which validates every published feed against the envelope, checks every adopter subscription resolves to a signed tag, and reports could-not-look when a repo is unreachable.

## Notes

Findings H4-03, H4-04, H4-05, H4-16. GAPS 1.8, 3.20. ADR-0019.

## Build notes (fixer pass, 2026-08-28)

Decisions taken while applying the review of the first build. Each is provisional; reopen with a reason.

1. **Bare-major pins resolve to the newest signed tag of that major.** Adopters keep `version: "v1"`; the hub verifier (`verify/feed-contract/feed_contract.py`) matches `^(<name>/)?v1\.\d+\.\d+$` on the publisher's real remote and names the tag it matched (`v1.0.0` on ico today). No workflow can cut a literal `v1`, so the brief's "v1 -> tag v1" reading is replaced by this one. Full-semver pins still match exactly. `policy/vX.Y.Z` and bare `vX.Y.Z` are both accepted for every publisher, so the platform's `policy/v3.0.0` line resolves.
2. **One sidecar location: `<feed-name>/rule.yaml` and `<feed-name>/bump.yaml`**, beside `payload.schema.json`, not under each `v<MAJOR>/`. The brief said "beside feed.json"; per-major files made "the declared bump for the next release" ambiguous (ico had three) and `feeds/fetch/lib.py` already reads the per-feed path. ico moved; nist carries `catalog/{rule,bump}.yaml` beside its published path. The hub verifier accepts only this path now. ico's rule.yaml carries `entries: regimes`, `numeric_tolerance: 0` so `feeds/bump.py` computes it (v1->v2 patch, v2->v3 major).
3. **Sizes dropped.** No party.yaml carries `size`: the numbers had no source and the owner's gitsign tag would have signed them. `appetite` stays where it was copied from `platform/risk/appetite.json`; `reporting_currency` stays. Ticket 25 adds sizes from a stated source.
4. **Insurer is `roles: [publisher, insurer]` with `publishes: [quote]`** as 04 A4 says. `quote/` has no `v*/feed.json` until ticket 36, so the hub verifier reports it SKIP (could not look), never PASS. Its `inherits[]` is empty: a platform pin is a Flux pin `party_artefact.py` checks against `gitops/platform/platform-pin.yaml`, and the insurer has no Flux yet (ticket 36).
5. **The feeds move out of platform is deferred, deletion only.** The `feeds` repo is the publisher of threat-register, cve and eol (envelopes, tags, clock). The platform copies, `feeds/keys` and `wardley/intel/market-intel.json` stay because `honesty/verify-honesty.sh`, `wargamer/`, `wardley/wardley.py`, hub `verify/provenance`, `twin/fixtures.py` and the composer's `feed_file()` bridge still read them; deleting now breaks four gate scripts for no consumer gain. market-intel is not yet a `feeds` feed: its payload's entry list (`components`, a list keyed by `id`) is not the entry map `bump.py` computes over, so the bump rule cannot be written honestly until the engine accepts keyed lists (twin, ticket 29). `honesty/reflexive.py` no longer keys on the .pem: `verification_key_present` and `can_publish` come from `party_artefact.publish_capability`.
6. **Rollout order for the adopters' new party.yaml.** driftwood and ludlow's `shift-left.yml` run `party_artefact.py check` from the platform checkout at the pinned tag (`v1.1.1`), whose schema refuses `reporting_currency`, `kind: feed`, `name`, `since`. Order: (a) merge platform's PR and cut the next platform tag (`policy/` line); (b) each adopter's party.yaml change rides the same PR as its `gitops/platform/platform-pin.yaml` bump to that tag; tuppence, which checks out platform `main`, is green once (a) merges. Until then those PR checks are red by design, not by defect.
7. **Not changed, owner's call.** `composition.py` still refuses an unreadable envelope (`invalid-feed`) and an unknown feed name (no converter). Brief rule 4 allows only a missing instrument; whether a feed that cannot be read is a missing instrument, and whether an unknown feed prices as a hole of zero, is the £-seam's decision (ticket 25). ico's v1/v2 envelopes point at the historic `penalty-schema/payload.schema.v2.json`; it is the pre-weights shape those majors were signed with, kept by name so the v2->v3 `payload_schema` change reads as the major it is.
