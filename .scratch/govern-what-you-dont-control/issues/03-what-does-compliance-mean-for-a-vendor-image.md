# 03 — What does compliance mean when the vendor image cannot comply?

Type: grilling
Status: resolved
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

## Answer

Resolved by grilling, 2026-08-20. Owner: *"it runs in a cage that simulates it, nothing runs without
a cage even if they're permissive."*

**1. Compliance is achieved by the cage, not by the image — the composite complies.** This is the
key reframe. The question assumed a vendor image that cannot satisfy a rule presents a compliance
*problem* to be exempted, priced or denied. It doesn't: the cage **implements the control on the
workload's behalf**. The image never becomes compliant; the pod-as-deployed does.

**This is already how the code behaves.** `cage-tier.yaml` stamps
`securityContext.readOnlyRootFilesystem: variables.dial.harden`, drops ALL capabilities, sets cpu/mem
limits and injects a WAF sidecar; `cage-netpol.yaml`'s `GeneratingPolicy` locks caged pods to
egress-DNS-only. A vendor image that cannot set read-only root **gets it set by the cage**. So
"a cage that simulates it" is not a new mechanism to build — it is the existing mechanism, named
correctly for the first time.

**2. Nothing runs uncaged; the permissive cage is still a cage.** Consistent with the verdict model
settled on the computed-semver map. The gap remains the same one: `cage-tier.yaml:41` states *"a pod
in currency is never caged by this policy"*, so the permissive default does not yet exist. Tracked
there as *Every workload is always caged, and the code disagrees*.

**3. Conditional policy decides admission; the cage decides how tightly it runs.** Two mechanisms,
two questions. `may-run-root-if-attested`'s shape (`nonroot || (attested && hardened)`) answers *may
this run at all*; the tier answers *how constrained*. Exemption and denial stay ruled out.

**4. The residual lands in the institution's own band, tagged.** One band keeps the £ honest — a
pound of breach is a pound of breach regardless of who wrote the code — but tagged so *"how much of
our appetite is spent on software we cannot fix, only cage"* is an answerable question. A separate
budget was rejected as where uncontrollable risk goes to be quietly tolerated.

**5. New, and not previously modelled: using COTS may *outsource* some risk.** Owner: *"in the book
balancing there may be opportunity to recover via litigation — in effect by using the COTS you may
have outsourced some of the risk."* Buying software buys a counterparty: indemnities, warranties, SLA
credits and a party to sue. That is a genuine **transfer**, and the £ engine models transfer only as
insurance (`costs.transfer.load`, `deductible`). Vendor recourse is a second transfer channel with
different properties — recovery uncertain, slow, contractually capped, and correlated with vendor
solvency. Raised as its own ticket; it is an argument that can favour COTS on the balance sheet,
which no part of the current model can express.
