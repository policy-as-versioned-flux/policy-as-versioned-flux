# References — Citation Registry

The full, verified citation registry for *Policy as Versioned Code, on Flux*. URLs here are the
single source of truth; do not invent or alter them. Entries marked "(unverified — could not
confirm)" link anyway but could not be independently confirmed.

## CNS's own work

- [What is Policy As [versioned] Code? (Medium)](https://chrisns.medium.com/what-is-policy-as-versioned-code-306e0341290b) — the original Medium post, 11 Mar 2022 (canonical `chrisns.medium.com` form; the `medium.com/@chrisns` form 302-redirects here).
- [Policy as [Versioned] Code: A Mea Culpa, a Technical Argument, and a Lonely Experiment](https://blog.cns.me/posts/policy-versioned-code-mea-culpa-technical-argument-nesbitt-smith-pedef/) — the "mea culpa" blog post; credits Michael Brunton-Spall.
- [Policy as [versioned] Code (main talk)](https://talks.cns.me/PolicyAsVersionedCode.html) — slides/transcript page for the main talk.
- [Policy as [versioned] Code 1.2.0 (YouTube)](https://www.youtube.com/watch?v=YWQG_E7vgiQ) — recording of the main talk.
- [Policy as [versioned] Code (Lightning) talk](https://talks.cns.me/PolicyAsVersionedCodeLightning.html) — lightning-talk slides page.
- [Lightning Talk: Policy as [Versioned] Code - You're Doing It Wrong (YouTube)](https://www.youtube.com/watch?v=Nstv7OA4abo) — CNCF-hosted lightning talk recording.
- [Pod Security Policy is Dead, Long Live...? (predecessor talk)](https://talks.cns.me/PodSecurityPolicyIsDeadLongLive.html) — predecessor talk slides page.
- [talks.cns.me (talks index)](https://talks.cns.me/) — index of CNS's talks.
- [cns.me (CNS landing)](https://cns.me) — personal landing (302-redirects to LinkedIn).
- [github.com/chrisns (CNS GitHub)](https://github.com/chrisns) — Chris Nesbitt-Smith's GitHub.
- [GitHub org: example-policy-org](https://github.com/example-policy-org) — first reference org from the 2022 implementation.
- [example-policy-org/policy](https://github.com/example-policy-org/policy) — the versioned policy repo.
- [example-policy-org/policy-checker](https://github.com/example-policy-org/policy-checker) — the 2022 bespoke checker.
- [example-policy-org/policy-action](https://github.com/example-policy-org/policy-action) — CI action (present in `example-policy-org` only).
- [example-policy-org/e2e](https://github.com/example-policy-org/e2e) — KiND e2e (present in `example-policy-org` only).
- [GitHub org: policy-as-versioned-code](https://github.com/policy-as-versioned-code) — second reference org.
- [policy-as-versioned-code/policy](https://github.com/policy-as-versioned-code/policy) — versioned policy repo.
- [policy-as-versioned-code/policy-checker](https://github.com/policy-as-versioned-code/policy-checker) — checker.
- [policy-as-versioned-code/cluster1](https://github.com/policy-as-versioned-code/cluster1) — `cluster1` (all versions) profile.
- [policy-as-versioned-code/cluster2](https://github.com/policy-as-versioned-code/cluster2) — `cluster2` (`>=2.0.0`) profile.

## Intellectual lineage

- [Rugged: Being Secure & Agile — Michael Brunton-Spall, GOTO 2016](https://www.youtube.com/watch?v=txEWO4uyVnY) — the canonical origin talk (GOTO Amsterdam 2016); the credited lineage of the thesis.
- [The thoughts and musings of MBS (Michael Brunton-Spall's site)](https://www.brunton-spall.co.uk/) — Michael Brunton-Spall's personal blog/site.
- [bruntonspall (Michael Brunton-Spall) on GitHub](https://github.com/bruntonspall) — his GitHub account.
- [The Magic of Platforms — Gregor Hohpe (talk)](https://platformengineering.org/talks-library/the-magic-of-platforms) — the guardrails / lane-keeping-assist metaphor; cite alongside the book below.
- [Platform Strategy — Gregor Hohpe (book)](https://architectelevator.com/book/platformstrategy/) — conceptual home of the autonomy-within-boundaries argument.
- [The GDS Way](https://gds-way.digital.cabinet-office.gov.uk/) — the propose/review/retire governance model behind the human-governance layer.
- [Exploring the Map (Wardley Maps, Chapter 3)](https://medium.com/wardleymaps/exploring-the-map-ad0266fad59b) — Simon Wardley's chapter where climatic patterns are introduced (verified canonical source for climatic movement).
- [Wardley Maps — Chapter 1: On being lost](https://medium.com/wardleymaps/on-being-lost-2ef5f05eb1ec) — book entry point (unverified — could not confirm).

## Flux ecosystem

- [Flux — continuous delivery for Kubernetes](https://fluxcd.io/) — official Flux CD project homepage.
- [fluxcd/flux2](https://github.com/fluxcd/flux2) — Flux GitOps Toolkit repo.
- [GitRepository (Source Controller)](https://fluxcd.io/flux/components/source/gitrepositories/) — source object; `.spec.verify` (PGP/Git signature).
- [OCIRepository (Source Controller)](https://fluxcd.io/flux/components/source/ocirepositories/) — OCI source; `.spec.verify` cosign keyless.
- [Kustomization (Kustomize Controller)](https://fluxcd.io/flux/components/kustomize/kustomizations/) — `dependsOn`, `healthChecks`, `wait`.
- [Notification Controller](https://fluxcd.io/flux/components/notification/) — Provider, Alert, Receiver, Events.
- [fluxcd/source-controller](https://github.com/fluxcd/source-controller) — GitOps Toolkit source component.
- [source-controller #1068 — add gitsign as a Git signature verifier](https://github.com/fluxcd/source-controller/issues/1068) — the single upstream dependency (OPEN).
- [flux push artifact — CLI reference](https://fluxcd.io/flux/cmd/flux_push_artifact/) — Flux OCI artifacts.
- [controlplaneio-fluxcd/flux-operator](https://github.com/controlplaneio-fluxcd/flux-operator) — ControlPlane Flux Operator repo.
- [Flux Operator documentation](https://fluxoperator.dev/) — canonical Flux Operator docs.
- [FluxInstance CRD — Flux Operator docs](https://fluxoperator.dev/docs/crd/fluxinstance/) — `FluxInstance`.
- [ResourceSet CRD — Flux Operator docs](https://fluxoperator.dev/docs/crd/resourceset/) — input matrix + templated resources.
- [ResourceSetInputProvider CRD — Flux Operator docs](https://fluxoperator.dev/docs/crd/resourcesetinputprovider/) — GitHub/GitLab/Azure DevOps inputs.
- [Enterprise for Flux CD — ControlPlane](https://control-plane.io/enterprise-for-flux-cd/) — FIPS 140-3 compliant hardened distroless Flux images.
- [Renovate — Flux Manager docs](https://docs.renovatebot.com/modules/manager/flux/) — native Flux manager (HelmRelease, GitRepository, OCIRepository, Kustomization).

## Engines, cloud, compliance & supply chain

- [Kyverno — Kubernetes Native Policy Management](https://kyverno.io) — CNCF graduated policy engine.
- [ValidatingPolicy (CEL) — Kyverno docs](https://kyverno.io/docs/policy-types/validating-policy/) — CEL-based `ValidatingPolicy`; `validationActions` Audit/Deny/Warn.
- [Policy Reports — Kyverno docs](https://kyverno.io/docs/policy-reports/) — `PolicyReport` CRs and background scanning.
- [ClusterPolicy (Deprecated) — Kyverno docs](https://kyverno.io/docs/policy-types/cluster-policy/policy-settings/) — deprecated as of 1.13.
- [Crossplane — Cloud-Native Framework for Platform Engineering](https://crossplane.io) — CNCF project; cloud-as-CR.
- [controlplaneio/collie](https://github.com/controlplaneio/collie) — OSCAL and Kyverno policy demo for AWS (harvested for its catalogue + policy intent; rebuilt native — ADR-0004).
- [Collie: A toolkit for securing cloud controller provisioned infrastructure](https://control-plane.io/posts/collie-open-source-release/) — collie announcement (Apr 2023): NIST 800-53r5 Kyverno + OSCAL + Lula.
- [OSCAL — Open Security Controls Assessment Language](https://pages.nist.gov/OSCAL) — NIST-led control-catalogue standard.
- [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) — the US-federal control catalogue collie ships against.
- [OSCAL Compass — Compliance-to-Policy (C2P), Go](https://github.com/oscal-compass/compliance-to-policy-go) — CNCF Sandbox; `result2oscal` turns Kyverno PolicyReports into OSCAL assessment-results. The measurable pillar's OSCAL emitter (ADR-0009).
- [kyverno/policy-reporter](https://github.com/kyverno/policy-reporter) — PolicyReport → Prometheus/UI/dashboards; the live measurability layer.
- [Sigstore Documentation](https://docs.sigstore.dev) — supply-chain signing/verification.
- [sigstore/cosign](https://github.com/sigstore/cosign) — code signing for containers/OCI artifacts.
- [sigstore/gitsign](https://github.com/sigstore/gitsign) — keyless Git signing via Sigstore.
- [sigstore/rekor](https://github.com/sigstore/rekor) — supply-chain transparency log.
- [sigstore/fulcio](https://github.com/sigstore/fulcio) — Sigstore OIDC PKI (keyless signing CA).
- [kind — Kubernetes IN Docker](https://kind.sigs.k8s.io) — free, reproducible local clusters.
- [LocalStack — local AWS cloud emulator](https://localstack.cloud) — local cloud for provisioning proofs.
- [ControlPlane — Kubernetes, Cloud Native & OSS Security](https://control-plane.io) — company homepage.
