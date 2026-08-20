# 03 — What does compliance mean when the vendor image cannot comply?

Type: grilling
Status: open
Blocked by: 01

## Question

Some policy rules a COTS workload simply cannot satisfy. A vendor image that must run as root, or
writes to its own filesystem, will never pass `runAsNonRoot` or `readOnlyRootFilesystem` — and no
amount of shimming changes that, because the constraint is in the software.

The estate already has machinery pointed at this shape and it may fit without invention:

- **Conditional policy** — "you may do X **if** you meet conditions C" (`verify-conditional.sh`,
  `may-run-root-if-attested.yaml`). A COTS product could be admitted under declared compensating
  conditions rather than exempted.
- **The exemption ledger** — a git ledger entry renders a `PolicyException` with a TTL backstop, and
  the same entry generates the OSCAL risk object. `verify-exemption.sh` proves no ledger entry means
  no exception.
- **The cage** — if it cannot be fixed, it can be caged tighter, and the £ prices that.
- **Retain / transfer** — sometimes the honest answer is that this is accepted risk with a number
  against it.

**Decide:** is a non-compliant-by-construction COTS workload (i) a conditional-policy case, (ii) a
ledger-and-priced-exception case, (iii) a cage-harder case, or (iv) a genuinely new state the estate
does not yet model? And critically — **does its residual risk land in the institution's £, and whose
tolerance band does it consume?**

The estate's strongest existing answer is that exemptions dissolve into conditional policy. Test
whether that holds when the thing being exempted cannot ever meet the condition.
