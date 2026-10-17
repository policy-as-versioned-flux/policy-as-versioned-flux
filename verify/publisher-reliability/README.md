# Publisher reliability report observation

Ticket46's first slice observes NIST's binary forecast diagnostic, independently
of any price. The scorer decision is recorded in the ticket. An empty population
is unmeasured, with null losses; Brier and log loss do not measure publisher-price
accuracy. No threshold, widening target or compiler price effect is supplied here.

`verify-publisher-reliability.sh` reads the canonical NIST clone under
`.estate-clone`, chooses its highest `publisher-reliability/v<semver>` tag, requires
that annotated tag on served main's first-parent history, and verifies its Git
signature, Rekor inclusion and exact cut-release certificate identity offline.
Catalogue `v*` tags do not qualify. It exports the immutable verified tag object,
runs that source's native provenance/recomputation checker on the committed
`publisher-reliability/v1/feed.json`, and preserves its binary-only claim boundary.
The mutable checkout is not report evidence. The caller does not fetch or sign.

Before the first signed report tag, or with an authentic report having no eligible
independent pairs, the estate observation exits3/SKIP. A nonempty authenticated
report can pass binary recomputation; its verdict still establishes no
publisher-price accuracy. Invalid provenance, wrong identity, changed tag,
recomputation failure and a false numeric empty result fail. Missing instruments
exit3 with a distinct reason that the manifest deliberately does not declare.

`verify-publisher-reliability-contract.sh` runs the actual consumer over temporary
Git repositories, synthetic reports and an explicitly labelled verifier fixture.
Its pass proves local consumer behavior only. It never verifies a genuine
certificate or supplies a world outcome. Genuine signed publication, independent
registrations and resolutions remain separate requirements; ticket46 stays open.
