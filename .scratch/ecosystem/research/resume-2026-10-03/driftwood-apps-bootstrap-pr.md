The proposed digest inventory reads the immutable apps source, so the new manifests must first exist in a real signed adopter release. This PR records the application image digests for nginx, storefront and the newly listed API while retaining the published compiler v4.0.0, all policy/feed parent pins, policy 5.0.0 claims and the current apps self-pin.

Composition was regenerated with the exact published v4.0.0 source and replays byte-for-byte. The ordinary adopter grader reports none (no added/retired policy versions), and every served workload plus deploy/pod.yaml passes the actual declared Kyverno 1.18.2 shift-left gate. Prospective adopter release v3.0.1 is unused in the inspected local tag namespace.

After this reviewed change is merged, the existing cut-release workflow must authenticate the compiler and create the real signed tag. Only then can the final policy 7/tools 5/feed 3 adoption move the apps tag+SHA and bind the full scanned inventory to that tagged graph. The unchanged authenticated compiler wrapper now passes genuine Sigstore/Rekor identity verification. Source commits use the configured ordinary SSH signature; no verification gate, signing setting or hook was changed.

Images in this release candidate:

- `nginx@sha256:abe47724e466aeab9a345d8e46a221c2fa8953c7848bb4a3bd9976a7199f8cf2`
- `ghcr.io/policy-as-versioned-driftwood/storefront:v1.0.1@sha256:6affc441f4181ec9e43976ab4115e8b239fe5a73ba30de8f61f5ff691de303d6`
- `ghcr.io/policy-as-versioned-driftwood/api:v1.0.1@sha256:90ccb85d903b8137863695681c2cf6b8cb85ba59835be5e24857e72895b977a3`
