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

**Narrowed upstream.** The remedy is wrap-or-shim, never exempt and never deny — so option (ii),
the ledger-and-priced-exception route, is disfavoured before this ticket starts: an exception is
precisely the thing the owner ruled out. The live question is whether conditional policy can carry
the whole load.

**The mechanism already exists and is unreachable.** `may-run-root-if-attested` implements exactly
the right shape — `nonroot || (attested && hardened)` — but its `matchConditions` require
`policy-version == '1.0.0'`, so it is gated behind the label this population cannot wear. The wrap or
shim must deliver these workloads *to* that policy rather than around it.

**Decide:** is a non-compliant-by-construction COTS workload (i) a conditional-policy case, (ii) a
ledger-and-priced-exception case, (iii) a cage-harder case, or (iv) a genuinely new state the estate
does not yet model? And critically — **does its residual risk land in the institution's £, and whose
tolerance band does it consume?**

The estate's strongest existing answer is that exemptions dissolve into conditional policy. Test
whether that holds when the thing being exempted cannot ever meet the condition.
