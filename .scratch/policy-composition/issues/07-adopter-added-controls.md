# 07 — What fills a control the adopter adds itself

Type: grilling
Status: open
Blocked by: none

Surfaced by ticket [`03`](03-baseline-and-catalogue-ids.md). That ticket settled that an adopter may
**add** a control to its selected baseline and may never remove one. It did not settle what happens
next. The estate's adopters ship no implementations: `driftwood` "authors no policy today" and pins
`platform` and `nist`. So an adopter-added control is a hole the moment it is added, with no
publisher able to fill it.

## Question

When an adopter adds a control to its own baseline, what may fill it? Does an adopter-added hole
behave differently from an inherited one under ticket `03`'s new-hole rule, given that the adopter
created it deliberately in the same commit? And if an adopter can also ship an implementation, does
it become an implementations **publisher**, with the versioning and signing obligations that role
carries?
