# 90 — Identity is shelved for this build

Type: task (AFK)
Status: open
Blocked by: none

## Question

Ticket 75 Q12 decided (b): the identity and attestation substrate is designed and shelved for this build. Artefact attestation is real (24 of 24 tags verify against Rekor). Actor attestation has never been observed on a citable run, all six identity scripts skip, and federation is one trust domain with no peer. The claim in NORTH-STAR §1 must become true rather than aspirational.

1. Move the six identity-plane verify scripts to `talk/verify-exclusions.txt`, each with a reason that names what it waits for (an identity lane that grades the actor half), so the gate stops printing six could-not-looks that no ticket on this map will clear.
2. NORTH-STAR §1 reads "every artefact is attestable". Principle 6 keeps "every actor is attestable" as the design, marked as shelved for this build with the date and this ticket.
3. The map's note "identity is spine, not cut" is amended by ticket 75. Ticket 12's Answer gains a dated comment. Ticket 68 (federation gets its peer) is ruled out of scope for this map and closed; it returns with the identity lane.
4. `verify-demo.sh` and the deck must not narrate actor attestation as observed.

Done = the six scripts are excluded with reasons on the next citable run, the §1 sentence is true on that run, and ticket 68 is closed with a line in the map's Out of scope.

## Notes

Charted by ticket 75 (Q12). Overlaps ticket 86 item 3, which this ticket now owns. The identity lane is fog: it is the first thing after this map.

## Comments

**2026-09-03, ticket 73.** ADR-0027 item 6 hands the identity lane one more instant: the source
verifier now chains at the later of the tagger time and the certificate's notBefore within a
declared 60s bound, and records the Rekor integrated time (the signed entry timestamp, verified
against a pinned Rekor key) as the instant it would ideally use. That is the transparency check the
verifier's docstring names as its ceiling, so it belongs here, with the actor half, not to 73.
