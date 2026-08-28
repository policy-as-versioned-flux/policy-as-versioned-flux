# 05 — Research cedar for composition

Type: research (AFK)
Status: open
Blocked by: none

## Question

Does Cedar's sound-and-complete permissiveness analysis (more-permissive / less-permissive between two policy sets) fit cross-party composition? Specifically: can a composed set (nist -> platform -> driftwood, with a restatement and a cage tier floor) be lowered to Cedar so that 'is the adopter's composed set strictly stricter than its publisher's' is a decidable check, and can a cage spec (CPU, memory, netpol, WAF) be expressed on the same lattice? What does the lowering lose? Compare with `platform/computed-semver/cage_engine.py` Track 2, which already compares cage specs on a partial order.

## Notes

Re-grill 41. The twin's ticket 27 note is the prior art. Output: a research note with a go/no-go recommendation and a minimal lowering example.
