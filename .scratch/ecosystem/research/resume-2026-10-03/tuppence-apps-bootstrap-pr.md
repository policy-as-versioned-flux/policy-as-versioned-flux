The proposed digest inventory reads the immutable apps source, so the new manifests must first exist in a real signed adopter release. This PR records the application image digests for ledger while retaining the published compiler v4.0.0, all policy/feed parent pins, policy 5.0.0 claims and the current apps self-pin.

Composition was regenerated with the exact published v4.0.0 source and replays byte-for-byte. The ordinary adopter grader reports none (no added/retired policy versions), and every served workload plus deploy/pod.yaml passes the actual declared Kyverno 1.18.2 shift-left gate. Prospective adopter release v3.0.1 is unused in the inspected local tag namespace.

After this reviewed change is merged, the existing cut-release workflow must authenticate the compiler and create the real signed tag. Only then can the final policy 7/tools 5/feed 3 adoption move the apps tag+SHA and bind the full scanned inventory to that tagged graph. The unchanged authenticated compiler wrapper now passes genuine Sigstore/Rekor identity verification. Source commits use the configured ordinary SSH signature; no verification gate, signing setting or hook was changed.

Images in this release candidate:

- `ghcr.io/policy-as-versioned-tuppence/ledger:v1.0.1@sha256:4c769ab891a1e1b19b4f5f6884cf9a6ac37ef1cbc0f4aaeae02fdd7c2004d4c5`
