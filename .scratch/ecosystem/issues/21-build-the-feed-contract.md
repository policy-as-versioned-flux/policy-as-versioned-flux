# 21 — Build the feed contract

Type: task (AFK)
Status: open
Blocked by: 04

## Question

Make ticket 04 real in the estate. Write `platform/feeds/schema.json` and one payload schema per existing feed. Migrate the five live feeds and the ico penalty schema into the envelope. Open `inherits[].kind` to `controls | implementations | feed` plus `name`, and add `since`. Add `party.yaml` with `roles: [publisher]` and `publishes[]` to platform, nist, ico, feeds and insurer. Move threat, CVE, EOL and market intel out of platform into the `feeds` repo, released by gitsign tag from its workflow. Rename `signing_key_present` to `verification_key_present` and add a real `can_publish`. Definition of done: a `verify-feed-contract.sh` that the gate discovers, which validates every published feed against the envelope, checks every adopter subscription resolves to a signed tag, and reports could-not-look when a repo is unreachable.

## Notes

Findings H4-03, H4-04, H4-05, H4-16. GAPS 1.8, 3.20. ADR-0019.
