---
status: accepted
---

# The source verifier chains at the later of the tagger time and the certificate's issue, within a declared bound

Decided 2026-09-03 by the assistant under ADR-0025, labelled delegated. Ticket 73.

## Context

Platform's `identity/gitsign-verifier` (ticket 41, ADR-0023 D3) verifies a gitsign-signed tag at
the Flux source boundary. Its check 2 chained the Fulcio signer certificate to the pinned root
"at the tag's own tagger timestamp", on the reasoning that the timestamp is inside the signed
payload and cannot be moved without breaking the signature. That reasoning is sound about the
timestamp and wrong about the instant.

git writes the tag object, tagger line included, and only then hands the payload to gitsign,
which requests an OIDC token and asks Fulcio for a certificate. Fulcio's `notBefore` is its own
clock at issue. So `notBefore` is never earlier than the tagger time and is one second later
whenever the second boundary falls between the two: on the seven newest signed tags of
2026-09-02, one second later in three (driftwood v1.1.0, ludlow v1.1.0, ico v3.0.0), equal in the
rest. `openssl verify -attime <tagger time>` on the later three answers "certificate is not yet
valid". The first real five-fact samples (runs 33556795181 and 33556801679, 2026-09-01) recorded
fact 2 false for driftwood-composed and ludlow-composed on exactly this; tuppence's tag escaped
by landing inside the same second. The 2026-09-02 review named it a structural fault in the
verifier's trust instant, not machine clock skew, and the skeptic proposed the Rekor signed-entry
timestamp as the correct instant. `gitsign verify-tag` accepts all three tags, Rekor entry
included.

## Decision

1. **The instant is the later of the tagger time and the certificate's `notBefore`.** The
   tagger time is a floor on when the signature was made, not the instant itself; the signature
   cannot predate the certificate that made it. The chain is evaluated at
   `max(tagger_time, notBefore)`.
2. **Allowed only within a declared bound.** `notBefore - tagger_time` must be at most
   `GITSIGN_TAGGER_SKEW_SECONDS`; past that the tag is rejected with a reason naming the gap and
   the knob. The bound is **60 seconds**, declared in `deployment.yaml` with its reason, and the
   gate's proof reads that declaration rather than carrying a number of its own. Reason for 60:
   the observed gap is one second; the honest causes of a larger one are the runner's clock
   against Fulcio's plus the OIDC-token and Fulcio round trips with retries, seconds not minutes;
   and the one thing the bound buys is a limit on how far a tag may claim to predate the
   certificate that signs it, so it stays an order of magnitude above the observed gap and an
   order of magnitude under the certificate's own ten-minute life. A gap the other way (tagger
   time after `notBefore`) needs no bound: the chain is evaluated at the tagger time as before,
   and a tagger time past `notAfter` still fails.
3. **No declaration means strict.** The program's default is 0, the pre-ADR behaviour; the
   tolerance exists only where a manifest declares it. A declaration that is not a whole number
   is could-not-look, never a verdict, and moves no gate.
4. **Both instants are recorded.** The facts carry `signed_at` (the tagger time, what the tag
   says), `chained_at` (the instant check 2 used) and `cert_not_before`; the reason written on
   the GitRepository reads `at <tagger> (certificate issued <gap>s later; chained at <instant>)`
   when they differ, so a reader of the annotation sees why.
5. **Re-cutting the affected tags is rejected as not a fix.** A re-cut tag lands on the wrong
   side of a second boundary about half the time; it would have re-rolled the dice, not removed
   them.
6. **The Rekor integrated time is the next instant, under ticket 90, not this one.** It is the
   log's clock at upload, seconds after signing, and would be the best available instant. Reading
   it honestly means verifying the signed entry timestamp against a pinned Rekor key, which is
   the transparency check the verifier's docstring already names as its ceiling; the controller
   runs a stock `python:3.13-alpine` with no gitsign binary and no Rekor material. That is the
   identity lane's work (ticket 75 Q12, delegated "b"; ticket 90), and the bounded tolerance is
   what stands until it lands or Flux #1068 deletes the controller.

## Consequences

- `platform/verify-source-verification.sh` section 4b proves a real racy tag
  (`identity/gitsign-verifier/testdata/driftwood-v1.1.0.tag`, byte-equal to driftwood's own
  `git cat-file tag v1.1.0`) verifies at the declared bound, is rejected at 0 naming the knob,
  stays rejected when tampered, and that `gitsign verify-tag` agrees on the same bytes. Section 7
  proves the arithmetic and the controller path, including the strict default and a
  mis-declared bound.
- The forgery case in section 5 now waives the bound explicitly so the pinned root chain is what
  refuses it; a freshly minted forgery would otherwise be refused by the bound first, which is
  correct but proves the wrong thing.
- Fact 2 on the lane goes true for driftwood-composed and ludlow-composed only once the owner
  pushes platform's `ecosystem/build-2026-09-03` and the new ConfigMap reaches the cluster a
  fresh sample reconciles (ticket 74). Until then the observation stands unmade.
- Reversal: a dated note here. Setting `GITSIGN_TAGGER_SKEW_SECONDS` to 0 in `deployment.yaml`
  restores the strict instant without a code change, and the gate goes red on it, on purpose.
