# platform / computed-semver — ticket cs-01: can the premise be rederived?

Before designing a release gate that computes a policy version's bump from
observed verdict movement, this proves the idea works on answers already
known. The old faithful-floor estate (now the sibling `policy` org repo) cut
a real, signed release line and **live-proved** each bump by hand:

- `2.0.0` — major: `require-department-label` promoted Audit → Deny.
- `2.1.1` — the enum on `require-known-department-label` widened `+legal`
  (patch in isolation), and `require-owner-annotation` was added (minor).

`corpus/` holds those policy bodies and fixtures as **fixed input**, copied
verbatim from `policy-as-versioned-flux/policy` at `v1.0.0` / `v2.0.0` /
`v2.0.1` / `v2.1.1` (each file's header cites its exact source path and tag;
two fixtures — `legal-department.yaml` and `no-owner.yaml` — are authored
here, not copied, because no committed fixture in that repo exercises them;
see their headers for why). `rederive_bumps.py` evaluates adjacent version
pairs offline with the real `kyverno apply` CLI — the same primitive
[`../shift-left/verify-shift-left.sh`](../shift-left/verify-shift-left.sh)
already runs — and derives major/minor/patch from observed admission
movement, per `CONTEXT.md`'s "Policy version" definition as sharpened by
[ticket 02](/.scratch/computed-semver/issues/02-what-counts-as-a-verdict.md)
(compliant == admitted; an Audit rule that fires reports but does not
refuse).

## Run it

```sh
./verify-rederive-bumps.sh
```

SKIPs (exit 0) if the `kyverno` CLI isn't installed, matching
`verify-shift-left.sh`'s convention.

## Result

All three known-good bumps rederive exactly, per named policy. At the
whole-body level (`CONTEXT.md`: "a policy version covers the whole body"),
the real `v2.0.1 → v2.1.1` release bundles a minor addition and a patch
widening into one tag; combining rules take the more significant change, so
the release-level bump is **minor**, not the "patch" label the ticket's own
bullet points attach to `2.1.1` in isolation — see the script's own printed
"honest finding" for the full account, including that the real tag's decimal
(minor bumped, patch held instead of reset) doesn't follow textbook
bump-and-reset semver, which `CONTEXT.md` doesn't actually specify either way.

**The one bump this method cannot get from verdict movement alone: minor.** A
brand-new Audit-only policy produces zero admitted/refused transitions for
any fixture by construction (Audit never refuses) — there is nothing to
observe on a fixed corpus. It is detectable only by a **structural diff**
(a policy name present in the new version, absent in the old) combined with
reading its `validationActions`. The script's `demo_pooled_exit_is_not_admission`
step proves the trap empirically: a plain, pooled `kyverno apply` exit code
across a mixed Audit+Deny policy set disagrees with the real admission
outcome whenever the only CEL failure is on an Audit policy.
