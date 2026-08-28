# 04 — The feed contract

Type: grilling (HITL)
Status: resolved
Blocked by: none

## Question

What is a feed, as a contract? One envelope (kind, version, published_by, published_at, signature, payload) with a JSON Schema beside `platform/party/schema.json`; an open parent-kind enum; keyless signing in each publisher's release workflow; a subscription record in the adopter's party artefact (which feed, at which pin, since when); a discovery record so a party can declare itself a publisher; revocation. Also: how a regulator's penalty schema and a prediction-market move fit the same envelope.

## Notes

Re-grills 26 and reversal 6. Findings H4-03, H4-04, H4-05, H4-16.

## Answer

Resolved 2026-08-28. Grilled in one round of five questions. The owner answered "Agree", then, asked for reasons, "These are all sound". No reason was stated. Under the map's process rule the five decisions are recorded with the owner's words verbatim and the recommendation's reasoning as the recorded rationale. Anyone who wants them reopened needs a reason the owner did not give.

1. **The envelope.** Every feed is one JSON object: `kind`, `name`, `version`, `published_by`, `published_at`, `payload_schema`, `payload`. JSON Schema at `platform/feeds/schema.json`, beside `platform/party/schema.json`. No in-band `signature`: a signature cannot cover itself, and the signature is the gitsign tag. `payload_schema` is a repo path or URL so a consumer validates the payload as well as the envelope. The five live feeds and the ico penalty schema migrate into it. A regulator's penalty schema and a prediction-market move differ only in `kind`, `name` and `payload`.
2. **Kind.** Two levels. A closed parent kind: `controls` (a catalogue plus named baselines), `implementations` (policy bodies plus control claims), `feed` (anything that prices and carries no rules). A free `name` under `feed`, so a new publisher declares a new feed with no platform PR. `inherits[].kind` in the party schema opens to this shape; today's `pricing` and `threat` become `feed` with names `penalty-schema` and `threat-register`.
3. **Signing and the bump.** A feed release is a gitsign-signed semver tag on the publisher repo (ADR-0012, no second mechanism). Consumers pin the tag and read the file from it. No cosign bundle until a non-git consumer appears. The publisher declares the bump in a versioned file reviewed in the PR (re-grill 13). A `payload_schema` change is always major.
4. **Subscription and discovery.** The subscription record is the adopter's existing `inherits[]` entry, which gains `name` and `since` (date of first pin) and is signed with the party artefact. The discovery record is a `publishes[]` list on the publisher's `party.yaml`: `{kind, name, path, payload_schema}`. `platform`, `nist`, `ico`, `feeds` and `insurer` each get a `party.yaml` with `roles: [publisher]`. No central catalogue: the set of publisher `party.yaml` files is the catalogue (re-grill 26).
5. **Revocation.** A publisher withdraws by publishing a new version whose payload marks the entry withdrawn, and by listing the version under `revoked[]` in its `publishes[]` record. Tags are never deleted. An adopter still pinned to a revoked version holds a priced hole: the cage tightens, it is never refused.

Not decided here: what a feed costs. That is the £ seam (ticket 08). Recorded in CONTEXT.md (Feed, Subscription, Discovery record, Revocation) and [ADR-0019](../../../docs/adr/0019-one-feed-envelope-signed-by-the-tag.md). Graduated into tickets 21 (build the contract), 22 (prediction-market feed) and 23 (news feed).
