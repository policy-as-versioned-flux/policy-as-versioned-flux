# 73 — The verifier rejects a tag whose certificate postdates its tagger time

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

The first real five-fact samples (2026-09-01, runs 33556795181 and 33556801679) record fact 2
false for driftwood-composed and ludlow-composed with the same error from platform's
identity/gitsign-verifier controller:

    v1.1.0: signature or certificate chain did not verify at tagger time <epoch>:
    CMS routines:cms_signerinfo_verify_cert: certificate verify error:
    Verify error: certificate is not yet valid

The controller verifies at the tag's tagger timestamp, and the Fulcio certificate's notBefore
falls AFTER that timestamp — clock skew between the runner's git clock and Fulcio issuance, a
few seconds at most. Tuppence's v1.1.0 tag escaped the skew and verified true, which shows the
pipeline itself is sound. Decide and build the fix: a bounded skew tolerance in the verifier
(verify at max(tagger_time, notBefore) when the gap is under a declared bound), or re-cut the
two affected tags. The tolerance bound is a security decision — record it with a reason.
Done = fact 2 true for all three composed sources on a fresh lane sample, and the tolerance (if
chosen) declared in the verifier's own config with the bound stated.

## Notes

Surfaced by ecosystem ticket 60's first dispatch samples. The verifier is platform's
identity/gitsign-verifier (ticket 41); the fix lands in platform, so the owner pushes and
merges. Related: ticket 55 fixed the gate-side OpenSSL 3.0 chain handling; this is the
cluster-side twin of that family.

## Comments

**2026-09-02, review.** Sharper than this ticket says. Across the seven newest signed tags the certificate's notBefore is never earlier than the tagger time and is one second later in three (driftwood v1.1.0, ludlow v1.1.0, ico v3.0.0). Git writes the tag before Fulcio issues the certificate, so chaining at tagger time rejects about half of correctly signed tags by construction. Not clock skew between machines: a design fault in the verifier's trust instant. The skeptic proposes the Rekor signed-entry timestamp as the correct instant. It is the sole cause of two of run 21's seven reds and contributory to a third. The security decision is ticket 75's Q12 neighbourhood; the fix is platform-side and the owner pushes. Record: REVIEW-2026-09-02.md §4 item 2.

## Answer (2026-09-03, built; ADR-0027)

Reproduced first: the verifier on `ecosystem/build-2026-09-03` (ticket 55's two-step chain
merged) rejects driftwood v1.1.0 with `certificate chain did not verify at tagger time
1787677714`; `gitsign verify-tag` on the same bytes answers good, Rekor entry included. Measured
on the local clones: driftwood v1.1.0 and ludlow v1.1.0 have `notBefore - tagger = 1s`;
tuppence v1.1.0, platform policy/v3.0.0 and policy/v4.0.0 have 0. The ico clone carries no
`policy/v3.0.0` tag, so its gap was not re-measured here.

**Built, in platform (commit `74e6af2` on `ticket-73-verifier-trust-instant`, from
`ecosystem/build-2026-09-03`; not pushed, the owner pushes):**

- `identity/gitsign-verifier/verify_gitsign.py`: check 2 chains at
  `max(tagger_time, notBefore)`, allowed only while `notBefore - tagger_time <=
  GITSIGN_TAGGER_SKEW_SECONDS`; past the bound, `Rejected` with a reason naming the gap and the
  knob. `trust_instant()` is pure; `certificate_not_before()` reads the leaf's `notBefore`;
  `declared_tagger_skew()` reads the env, 0 when unset, `CouldNotLook` when not a number. Facts
  carry `signed_at` (tagger time, unchanged), `chained_at` and `cert_not_before`; the reason on
  the object reads `at <tagger> (certificate issued <gap>s later; chained at <instant>)` when the
  two differ. `reconcile_one` now maps `CouldNotLook` to the `unknown` verdict rather than
  crashing the loop. The CLI gains `--tagger-skew-seconds`.
- `identity/gitsign-verifier/deployment.yaml`: `GITSIGN_TAGGER_SKEW_SECONDS: "60"` with the
  reason in the comment beside it.
- `identity/gitsign-verifier/testdata/driftwood-v1.1.0.tag`: a real racy tag, byte-equal to
  `git cat-file tag v1.1.0` in driftwood (tag object `1a88c34`). Kept beside the verifier, not
  in `distribution/verify/testdata/`, because that directory's refresh script re-derives from
  platform's own tags and this is another party's.
- `verify-source-verification.sh`: new section 4b reads the bound from `deployment.yaml` (fails
  if absent, not positive, or not under the certificate's ten-minute life), checks the fixture
  actually has `notBefore > tagger`, proves VERIFIED at the bound with both instants reported,
  REJECTED at 0 naming the knob, a tampered racy payload REJECTED, and `gitsign verify-tag`
  agreeing on the same bytes. Section 7 proves `trust_instant` on its own, the racy tag through
  `reconcile_one` (verified, reason carries both instants), the strict default (rejected, gate
  suspended) and a mis-declared bound (unknown, no gate moved). Section 5's forgery case waives
  the bound explicitly so the pinned root chain is what refuses it. Section 6 runs gitsign in a
  throwaway repo built from the fixture bytes: gitsign cannot resolve a ref inside a git
  worktree (`reference not found`, seen on this ticket's worktree), which read as falsifier b
  firing on a could-not-look.
- README and module docstring say what the instant is now and where the bound lives.

**Graded by:** `platform/verify-source-verification.sh` (offline sections 4b and 7; exit 0 on
2026-09-03 from the hub worktree root, live tail on kind-driftwood included). Fact 2 on the lane
is graded by `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh` through each adopter's
`drift/five-facts.py`, unchanged: it reads the verdict, the regexp and the reason, never
`signed_at`.

**Decisions, all delegated (ADR-0025), recorded in ADR-0027:**

1. *Trust instant:* the later of the tagger time and `notBefore`, within a bound, now; the
   Rekor integrated time is recorded as the next instant under ticket 90. Reason: the tagger time
   is a floor on the signing instant, not the instant; the Rekor time is the best instant but
   reading it honestly is the transparency check itself, and the pod has no gitsign binary and
   no Rekor material. Delegated.
2. *Bound:* 60 seconds, declared in `deployment.yaml`. Reason: observed gap 1s; honest causes
   are clock offset plus OIDC and Fulcio round trips, seconds; a bound limits how far a tag may
   claim to predate its certificate, so an order of magnitude above the observation and an order
   under the certificate's life. Delegated.
3. *Re-cut driftwood/ludlow v1.1.0:* rejected as not a fix; a re-cut lands on the wrong side of a
   second boundary about half the time. Delegated.
4. *Default:* strict (0) in the program; the tolerance exists only where declared. Reason: the
   proof reads the declaration, and a manifest with no bound gets the pre-ADR behaviour rather
   than a literal hidden in code. Delegated.
5. *Record:* ADR-0027 in the hub plus this Answer; ticket 90 gains a dated comment pointing at
   ADR-0027 item 6 so the identity lane picks up the Rekor instant. Ticket 75 Q12 text is left
   as it is: it already routes the substrate to 90. Delegated.
6. *`signed_at`:* stays the tagger time; `chained_at` and `cert_not_before` are added beside it,
   and the reason line carries both when they differ. Reason: downstream readers of the reason
   see why the instants differ, and nothing downstream reads `signed_at`. Delegated.

Map line: 73 — the source verifier chains at max(tagger time, notBefore) within a declared 60s
bound (ADR-0027); racy fixture proved, gitsign agrees; fact 2 waits on the platform push and a
fresh sample.

## Waits on the owner

- Push platform's `ecosystem/build-2026-09-03` (after the integrator merges
  `ticket-73-verifier-trust-instant` into it) and merge to `main`; the new ConfigMap only reaches
  a cluster from there.
- A fresh lane sample after that (ticket 74's machinery) to observe fact 2 true for
  driftwood-composed and ludlow-composed. Not observed as of 2026-09-03; the Done line's
  observation stands unmade until then.
