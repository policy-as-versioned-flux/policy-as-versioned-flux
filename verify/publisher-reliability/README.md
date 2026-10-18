# Publisher reliability report observation

Ticket46 observes NIST's signed publisher diagnostic. Version1 is a binary
forecast diagnostic: Brier and log loss do not measure publisher-price accuracy.
Version2 contains separate monetary cohorts using `money-empirical-crps/v1`.
Each cohort retains its unit, annual horizon, target, generator, resolver and
registered cases. Scores are never pooled across cohorts. An empty population
remains unmeasured, with null loss and score.

`verify-publisher-reliability.sh` reads the canonical NIST clone under
`.estate-clone`, chooses its highest `publisher-reliability/v<semver>` tag, requires
that annotated tag on served main's first-parent history, and verifies its Git
signature, Rekor inclusion and exact cut-release certificate identity offline.
Catalogue `v*` tags do not qualify. The object is captured before history checks
and copied into a private regular Git repository with its own temporary ref, so
the verifier and exporter select the same object even if the source ref moves.
It exports that immutable verified tag object,
runs that source's native provenance/recomputation checker on the committed
`publisher-reliability/v1/feed.json` or `publisher-reliability/v2/feed.json`, and
preserves that major's claim boundary. The checker receives the estate's full
canonical source clones to authenticate and reconstruct nonempty input records.
The mutable checkout is not report evidence. The caller does not fetch or sign.

Before the first signed report tag, or with an authentic report having no eligible
independent pairs, the estate observation exits3/SKIP. A nonempty authenticated
report can pass its native recomputation. A binary report still establishes no
publisher-price accuracy; a monetary report establishes only its separate
measured cohort diagnostics. It does not supply an adopter's bar, minimum sample
size or automatic acceptance. An adopter's explicit policy and the publisher's
authenticated widening target belong to the platform composition contract.
Invalid provenance, wrong identity, changed private verification ref,
recomputation failure and a false numeric empty result fail. Missing instruments
exit3 with a distinct reason that the manifest deliberately does not declare.
The two monetary waits name either no declared cohorts or no eligible pairs;
neither wait admits a missing instrument or a failed native check.

`verify-publisher-reliability-contract.sh` runs the actual consumer over temporary
Git repositories, synthetic reports and an explicitly labelled verifier fixture.
Its pass proves local consumer behavior only. It never verifies a genuine
certificate or supplies a world outcome. Genuine signed publication, independent
registrations and resolutions remain separate requirements; ticket46 stays open.

`verify-publisher-price-vertical.sh` exercises the complete actual source path:
publisher forecast generation, independent resolution, NIST scoring, native
release proof, publisher conversion and platform composition. It proves a worse
distribution selects the publisher-owned wider target before pricing, an equal
bar is accepted, an insufficient sample supplies no score cause, and a degraded
native release still widens when no case has resolved. It also verifies a saved
composition using captured Git evidence without the original monetary clones,
rejects altered evidence and rejects an unauthenticated native predecessor.
Controlled local file edits also require the bar, appetite, comparison identity
and current adopter's self-controls catalogue to use one captured declaration.
The tier and its recorded source cannot come from different file versions.

This source proof uses disposable histories, synthetic monetary declarations and
an explicitly labelled external signature fixture. It grants no genuine
certificate, observed price or financial credit. By default its production
modules come from `.estate-clone/{platform,nist,feeds}`; an isolated source run can
set `PAVC_PRICE_TEST_SOURCES` to a JSON object mapping those names to exact source
directories. Missing production modules fail this self-proof. The registered
estate observation independently requires genuine signed records and real
independent outcomes; no profile, threshold, target or case is invented to make
the current estate nonempty.
