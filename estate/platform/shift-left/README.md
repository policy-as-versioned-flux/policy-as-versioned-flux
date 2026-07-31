# platform / shift-left — the CI ±1 check (ticket 12)

Catches an Audit→Deny flip **before merge**, not at deploy. Runs the real
`kyverno apply` offline against a workload manifest, no cluster required.

## What it does

1. Reads the workload's `policy-as-versioned.dev/policy-version` label — the
   version it targets.
2. Resolves that version's **supported window (±1)** off `distribution/versions.yaml`'s
   array — the *same* array [`render-orphan-guard.py`](../distribution/render-orphan-guard.py)
   renders the live orphan-guard from. No second source of truth.
3. Runs `kyverno apply` for every policy version in the window against the
   workload.

`kyverno apply` reports the CEL pass/fail verdict independent of whether
`spec.validationActions` says `Audit` or `Deny` — Audit only changes what a
*live* cluster does with a fail (report vs block). So a workload that fails
here would be denied the moment its version is promoted Audit→Deny (ADR-0006:
promotion is editorial, never a timer) — this check catches that flip pre-merge.

## Run it

```sh
python3 ci-check.py --resource fixtures/workload-compliant.yaml   # exit 0
python3 ci-check.py --resource fixtures/workload-flip.yaml        # exit 1 -- the flip
./verify-shift-left.sh                                            # all offline proofs
```

[`ci-workflow.example.yml`](ci-workflow.example.yml) shows the shape an
institution repo's own `.github/workflows/` wires this into — each
institution owns its own CI; this repo only owns the check it calls.
