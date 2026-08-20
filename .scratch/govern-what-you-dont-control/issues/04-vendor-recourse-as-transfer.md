# 04 — Vendor recourse is a second transfer channel the £ engine cannot express

Type: grilling
Status: resolved
Blocked by: 03

## Question

Surfaced while resolving *What does compliance mean when the vendor image cannot comply*. Owner:
*"in the book balancing there may be opportunity to recover via litigation — in effect by using the
COTS you may have outsourced some of the risk."*

Buying software buys a counterparty. Indemnities, warranties, SLA credits and the ability to sue are
real recovery paths, and they are a form of **transfer** — but `tcor.py` models transfer as insurance
only: `costs.transfer` carries a `load` and a `deductible`, priced off the do-nothing ALE. There is
no way to express "some of this loss is recoverable from the supplier".

This matters beyond bookkeeping: it can be an argument **in favour** of COTS. A bought product with a
strong indemnity may carry less retained risk than an equivalent first-party build, and nothing in
the current model can say so — every existing lever makes COTS look strictly worse.

**Decide:**

1. **Is vendor recourse a fifth move, or a modifier on `retain`?** The four moves are fix / cage /
   transfer / deny. Recourse is not a decision the estate makes at war-game time — it is a property of
   a contract signed earlier — so it may be a *reduction applied to the retained residual* rather than
   a move to choose.
2. **How is it discounted?** Insurance pays reliably and quickly; litigation is slow, uncertain,
   contractually capped, and worthless if the vendor is insolvent. A naive credit would let a
   worthless indemnity erase real risk on paper. Does it need an evidence grade, as the twin grades
   mitigation credit — full credit only for a tested, enforceable, solvent counterparty?
3. **Where does the contract term live?** It is authored, not derived — a human read the contract.
   Same treatment as the exemption ledger, or a field on the procurement record settled in
   *Where does the shim sit*?
4. **Does it change the tag from the residual ticket?** If "how much appetite is spent on software we
   cannot fix" is answerable, is "how much of that is recoverable" answerable too?

**Guard against the obvious failure:** an unenforceable indemnity that makes the number look better
is exactly the unearned green this estate exists to refuse. Whatever is built must fail closed —
no credit without evidence the recourse is real.

## Answer

Resolved by grilling, 2026-08-20.

**1. One move, two instruments.** `transfer` gains a **counterparty** dimension — carrier or vendor —
rather than becoming a fifth move. Semantically it is transfer either way (loss ceded to a
counterparty), and a fifth move would break the four-move framing the balance-sheet story rests on. A
modifier on `retain` was rejected: recourse does not reduce the loss, it reduces the *net after
recovery*, which is what transfer already expresses.

The pricing formulas differ because the cash flows genuinely differ:

| | carrier (today) | vendor recourse (new) |
|---|---|---|
| up front | `premium = ale_warn × (1 + load)` | **zero** |
| recovery | near-certain, prompt | uncertain, slow, **contractually capped** |
| failure mode | carrier declines / excludes | counterparty insolvent |

Note the estate already models a transfer-only exposure: `driftwood-portfolio.json`'s
`third-party-fulfilment` carries `applicable: ["transfer"]` — *"Not a workload we admit, so
fix/cage/deny don't apply"*. What was conflated is that transfer meant **carrier**. This ticket
separates the counterparty from the move.

**2. Evidence-graded, and it fails closed.** Reuse the twin's `_credit()` shape
(`NOT_ENACTED = "the-option-this-claims-to-credit-has-no-corroborated-enactment"` — no credit without
corroboration). Ladder: *a clause exists* → *reviewed and enforceable* → *counterparty solvent* →
*a claim has actually been paid*. **Nothing below "reviewed and enforceable" earns a penny**, credit
is capped at the contractual cap, and solvency is a live input — an indemnity from a company about to
fold is worth its liquidation value, not its face value. This is the one place a counterparty's *own*
risk enters your book.

**3. The term lives on the procurement record.** One record per bought thing, carrying both the
declared policy version and the recourse it comes with — negotiated at the same moment, reviewable in
the same place, so the £ consequence of a weak contract is visible while someone is still deciding
whether to sign it.

**The exemption ledger was offered as an option here and is now banned outright** (see the map's
Notes). It is not where commercial terms live, and it is not where anything else lives either.
