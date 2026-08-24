# 18 — The seam, the evidence document and version legality

Type: task
Status: done (2026-08-24)
Blocked by: none

Source: [`spec.md`](../spec.md), *Testing Decisions*, *Version legality*, and *Module shape*.

## What to build

A publisher runs one command with a repository state and a declared version. They get back the
evidence document. This ticket builds that seam and makes it refuse an illegal version number.

There is **one seam**. A single entry point takes a repository state and a declared version. It returns
the evidence document as a dictionary. Everything reports through it. A test that reaches past it into
the corpus generator, the pairing helper or the renderer asserts on an implementation detail that the
next ticket will move.

The command-line interface is a thin wrapper. It prints the document and exits non-zero on refusal.
Signing happens outside the seam, because signing needs an identity CI holds and a test does not.

The document carries these fields, and none of them is optional. Later tickets fill them.

| Field | Content |
| --- | --- |
| `outcome` | `passed` or `refused`, and the reason on refusal |
| `bump.declared` / `bump.computed` | the stated class and the measured class |
| `movement[]` | per-policy verdict movement, naming entries and expressions |
| `counts` | old subject, new subject, union |
| `generator_version` | the generator's own version |
| `corpus_checksum` | the checksum of the generated spine |
| `wall_clock` | measured, published, never enforced |
| `not_looked_at[]` | holes and proved exclusions, each with a stable id |
| `limits[]` | derived limits with counts, open and closed |
| `matrix` | the per-institution result |

The version-legality rule follows semver 2.0.0 and adds nothing:

1. The base is the highest existing tag lower than the declared version.
2. Find the leftmost component that increased against that base.
3. Every component to the right of it must be zero.
4. The declared version must not already exist.
5. A gap is legal.

The module lives beside the existing rederive work, in the platform repo. Split the two meanings the
current corpus directory conflates. A corpus directory holds generated pods plus a manifest. A subject
directory holds the policy bodies and the version array.

Follow `verify-rederive-bumps.sh`. It runs the real Kyverno CLI offline and SKIPs with exit 0 when the
CLI is absent. Keep that convention.

## Acceptance criteria

- [x] One entry point takes a repository state and a declared version and returns a dictionary.
- [x] The document carries every field in the table above, on pass and on refusal.
- [x] A refusal still populates every field the run reached.
- [x] The command-line wrapper prints the document and exits non-zero on refusal.
- [x] The historical `2.1.1` refuses under the reset-on-bump rule, and the document names the base `2.0.1`.
- [x] A version gap passes.
- [x] A declared version that already exists refuses.
- [x] The corpus directory and the subject directory are separate.
- [x] The offline twin SKIPs with exit 0 when the Kyverno CLI is absent.

## Comments

Shipped in `platform` at `9cae333` + `8d33b44` (cs-18).
