---
status: accepted
---

# The assistant decides architecture and records it; the owner's reason, where given, binds

## Context

The drift review of 2026-08-27 set a process rule: a bare "agree" or letter from the owner does not
ratify architecture, so a decision is recorded with the owner's reason or it stays open. By
2026-09-02 about 84 architectural items sat marked "provisional" on tickets marked resolved, because
the owner answers in batches and in single words. The one-page panel-verdict shape was the only
format that had drawn a reasoned reply. The 2026-09-02 fitness review put the question to the
owner directly (ticket 75 Q11): reopen seventeen tickets and re-put the items in panel rounds, or
record the recommendations as the architecture, as the assistant's, and retire the vocabulary.

## Decision

The owner answered: "ask fable to decide then record".

1. The assistant decides architecture and records each decision with its reason, in the ticket
   that holds it, at the time it is made.
2. A reasoned answer from the owner overrides the assistant's call and is recorded as the owner's,
   with the owner's words and the date.
3. A bare letter or "yes" from the owner is a delegation, not a ratification. It is recorded as the
   assistant's decision with the assistant's reason, labelled delegated. Nothing is re-asked on
   that account.
4. The word "provisional" retires. Items so marked are re-labelled delegated without re-asking
   (ticket 80).
5. When a build discovers a fact mid-run that forces an architectural call, the assistant decides,
   records and continues. It does not interrupt the owner.
6. What still goes to the owner, and only the owner: purpose, dates, identities, money,
   authorisations, and anything that names a real person. The limit of five such decisions per
   day stands for those.

## Consequences

- The record is now honest about who decided what: every decision carries owner-reasoned,
  owner-instructed or delegated.
- The risk moves from "nothing is ratified" to "the assistant is wrong and nobody noticed". The
  counterweights are the truth surface, which grades outcomes not opinions, and the adversarial
  reviews, which have twice overturned assistant decisions with evidence.
- A future reader who finds an architectural choice with no owner words should not assume the
  owner was asked. They should assume this ADR.
- Reversal: the owner writes a dated line in NORTH-STAR §8 restoring the earlier rule. Nothing
  decided under this ADR is undone by that; it is re-put from that date.
