# 101 — No adopter gate has ever verified a real published signature, and ludlow's cannot

Type: task (AFK)
Status: open
Blocked by: none

## Question

The adopter gate's whole job is to verify the publisher's signed evidence against an identity the
institution holds itself (ADR-0011). Three institutions run one, and until ticket 99's
`verify/fold-agreement/verify-fold-agreement.sh` ran on 2026-09-05, **not one of them had ever been
observed verifying a signature platform actually published.** The first check that tried found that
ludlow's gate cannot: with the cosign version ludlow itself pins, its own invocation refuses every
bundle platform publishes, before it looks at the signature at all.

Three findings, all measured. Done = ludlow's gate verifies platform's published evidence (or
refuses it for a reason about the signature, not about a flag), driftwood's gate is exercised by
something, and no harness in the estate claims a pass over a refusal or discloses a limit that has
since stopped being true.

## Finding 1 — ludlow's gate refuses every bundle platform publishes (the blocking one)

`ludlow/.github/scripts/adopter_gate.py:verify_evidence()` calls

    cosign verify-blob --bundle=... --trusted-root=<committed trusted_root.json> \
        --new-bundle-format=true --certificate-identity-regexp=... --certificate-oidc-issuer=... <doc>

Against platform's real committed evidence (`computed-semver/evidence/4.0.0.json.bundle` at tag
`v2.0.1`) and cosign v3.1.3 — the version `ludlow/.github/workflows/shift-left.yml` installs by
checksum — that returns

    Flag --new-bundle-format has been deprecated, this will be the only supported format in future versions
    Error: --trusted-root only supported with --new-bundle-format
    error during command execution: --trusted-root only supported with --new-bundle-format

exit 1. `run()` turns that into `REFUSE: policy 4.0.0: cosign verify-blob refused the evidence
signature (...)`, which is a refusal about a command line wearing the words of a refusal about a
signature.

**The mechanism, measured both ways.** Platform's published bundles are the LEGACY cosign shape
(`base64Signature` / `cert` / `rekorBundle`). A bundle cosign signs today is the new Sigstore shape
(`mediaType` / `verificationMaterial` / `messageSignature`). With a NEW-format bundle the exact same
flag combination verifies fine — confirmed here with a locally key-signed blob, `Verified OK`. So
the flags are not wrong in themselves; they are wrong for the artefact platform actually publishes.

**It is LATENT, not currently firing.** `diff_versions()` only classifies a version `changed` when
ludlow's own composed member set changes, so the gate reaches `verify_evidence()` for the first time
on the next real policy adoption — and refuses it. ludlow's last two green `shift-left` runs
(2026-09-04) never entered this path.

Three candidate remedies, with their trade-offs. None is chosen here; this is an architectural call
in ludlow's repository and it belongs in ludlow's own reviewed pull request.

1. **Drop `--trusted-root` (and the format flag) and verify the legacy bundle the way driftwood and
   tuppence do.** Cheapest, and it demonstrably works: both other adopters verify platform's real
   bundles offline in about a second with no trust-root flag at all. The cost is the property
   ludlow's own harness Part E was built to prove — without `--trusted-root`, cosign fetches its
   trust root from Sigstore's TUF CDN, so verification acquires a network dependency and fails
   closed when egress is blocked. That is a real regression against a real, tested property, and it
   would need a note saying so.
2. **Re-sign platform's evidence in the new bundle format.** Fixes it at the source and lets ludlow
   keep its offline trust root, and every adopter gains a modern bundle. The cost is that it is a
   publisher change with an estate-wide blast radius: `cut-release.yml` signs, driftwood and
   tuppence verify legacy bundles today and would have to accept both shapes through a transition,
   and the already-published bundles on cut tags are immutable, so the two formats coexist until
   every pinned tag has moved. Also the largest piece of work.
3. **Pin a cosign version whose `--trusted-root` accepts a legacy bundle**, if one exists.
   Smallest diff if true, and it keeps both properties. The cost is that it has not been shown to be
   true — it needs someone to find the version and check it — and it pins the estate to an older
   binary, which is a security posture decision, not a convenience.

## Finding 2 — driftwood has no adopter-gate harness at all

driftwood carries `verify-reconcile.sh` and `verify-twin-overlay.sh` and no `verify-adopter-gate.sh`.
tuppence and ludlow each have one in the gate (`talk/verify-manifest.txt` places both). So until
ticket 99's fold-agreement check, **nothing in the estate had ever run driftwood's gate**, and the
one thing that grades it now is a hub check whose subject is agreement between three gates, not
driftwood's own behaviour in depth. driftwood's gate is the one whose reading the other two were
changed to match, which makes the hole worse than it looks.

## Finding 3 — tuppence's harness prints a pass claim over a refusal

`tuppence/scripts/verify-adopter-gate.sh` Scenario E tolerates the designed composed-major refusal
(correctly: it exists to prove `parse_pin()` walks a multi-document stream and that real cosign
ACCEPTS platform's real bundles). Two lines after the gate returns exit 1 it prints

    ok  E: the gate PASSES against the real, currently-committed platform-pin.yaml -- ...

That sentence is false as written on every run where the estate composes a major, which is every run
since 2026-08-31. What the scenario observed is that the checkout, the commit match and every
element's signature verification succeeded and the refusal that followed was the designed one. It
should say that.

## The lesson worth carrying (delegated, ADR-0025, 2026-09-05)

**A disclosed limit is an assertion, and it goes stale like any other.** ludlow's harness header
says it "does NOT prove, and cannot, offline: that cosign verify-blob ACCEPTS a genuinely valid
bundle" and that "the accept-path here is exercised in real GitHub Actions runs, never locally".
Both are now false: tuppence's Scenario E proves an offline accept against platform's real bundles
in about a second, and ludlow's own accept path has never run in CI either, because its gate only
reaches `verify_evidence()` when the member set changes. The disclosure was true when written and
nothing re-read it, so it went on excusing a gap that had become a defect. The estate grades its
PASS lines; it grades none of its "cannot" lines.

## Notes

Charted 2026-09-05 from ticket 99's build and its review. Ticket 99's own record carried a wrong
diagnosis of finding 1 for a few hours — it said ludlow's harness "stubs cosign", which it never
does — and that is corrected in ticket 99's Answer. The harness runs the real binary in Parts C and
E; what hid the defect is that Part E proves the offline property against a locally key-signed
fixture in the NEW bundle format, a shape that happens to match the flag the served artefact does
not have, and that E1/E2/E3 invoke cosign directly rather than through `adopter_gate.py`.
