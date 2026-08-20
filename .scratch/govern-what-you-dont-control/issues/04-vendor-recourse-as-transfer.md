# 04 — Vendor recourse is a second transfer channel the £ engine cannot express

Type: grilling
Status: open
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
