# 67 — The record matches the surface

Type: task (AFK)
Status: open
Blocked by: none

## Question

One hygiene pass, every item dated, nothing rewritten in place. The map's false 65/0/16 citation and the stale fog list were corrected at charting time on 2026-08-31; this ticket owns the rest: (a) add the reversals-confirmed update line to the drift-review NORTH-STAR copy, or repoint the map's link at the root copy, so the two copies agree; (b) reset ico's penalty-schema bump.yaml to none now that v3.0.0 is cut; (c) trim the unit repos' OBSERVATION_LANE lists to paths each repo owns; (d) wire a small check into the gate: any pass/fail figure that map.md quotes must exist as a line in talk/truth.log. Done = a reader following the map meets no claim the truth surface contradicts, and the gate enforces it.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M13 (map cites uncited number / Nothing-is-red, 2 confirmed findings), minors: stale fog, NORTH-STAR copies disagree, stale ico bump, hub-only lane paths.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-02, review.** Sibling ticket 80 carries the ADR, ticket and glossary corrections the review found: fifteen build tickets cite run 7 as proof; ADR-0010 and ADR-0008 lack banners; ADRs 0019 to 0021 and 0023 do not mark their provisionality; CONTEXT.md contradicts ADR-0022's Deny addendum. Widen (d) so any TRUTH figure quoted in issues/*.md must resolve to a real line whose tree contains the named check. Record: REVIEW-2026-09-02.md R10.
