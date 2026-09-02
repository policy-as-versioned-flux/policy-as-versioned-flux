# 73 — The verifier rejects a tag whose certificate postdates its tagger time

Type: task (AFK)
Status: open
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
