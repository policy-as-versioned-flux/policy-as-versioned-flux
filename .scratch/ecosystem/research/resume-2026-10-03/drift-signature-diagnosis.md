# Drift signature diagnosis, 2026-10-03

The evidence is from scheduled lane runs, not a hand-sampled cluster:

- driftwood [37120458169](https://github.com/policy-as-versioned-driftwood/driftwood/actions/runs/37120458169), 2026-10-03: composed source fact 2 null; platform and nist true. The verifier rolled out at 11:42:39.578Z; sample lines were recorded at 11:42:56.059Z. Its declared reconcile interval is 60 seconds. The missing annotation is consistent with sampling between controller cycles. The logs do not prove that every historical null had this cause.
- tuppence [37126409593](https://github.com/policy-as-versioned-tuppence/tuppence/actions/runs/37126409593), 2026-10-03: fact 2 true for all three sources.
- ludlow [37029256742](https://github.com/policy-as-versioned-ludlow/ludlow/actions/runs/37029256742), 2026-10-02: fact 2 true for all three sources.

The preserved sampled rows carry the signature verdict and its cause. Older local lane records
show FALSE on driftwood and ludlow's old v1.1.0 tags with `certificate is not yet valid` at
tagger time. That is the ADR-0027 certificate timing finding, distinct from a missing verdict.
The verifier at the current platform v4.0.0 pin already carries the declared tolerance.

The same scheduled rows show the independent CI falsifier was not checked on platform and nist:
the adopter lacked each publisher's release.yml checkout. Driftwood recorded this as null.
Tuppence and ludlow incorrectly turned `ci_accepts: null` into `fired: false`. The implementation
now reads each publisher's pinned identity and tag, and preserves unknown as unknown.

A bounded 180-second source verdict wait stops on true, false or unknown. It does not wait a
false signature away. The lane prints the verifier's own reasons for any remaining ceiling.
No post-change scheduled sample has been obtained, so ticket 157 remains claimed.
