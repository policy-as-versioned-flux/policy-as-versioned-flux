# 19 — The generated corpus spine and its manifest

Type: task
Status: ready-for-agent
Blocked by: 18

Source: [`spec.md`](../spec.md), *The corpus*.

## What to build

Nobody curates the population toward a wanted bump. The corpus is generated, never hand-picked. A
reviewer sees the entry count, the checksum and the wall-clock in the evidence document.

The generator enumerates **per predicate expression**, across satisfied, violated and absent. The field
space is infinite. The expression space is finite and grows with the policy body.

Two more axes join it. The **version pin** goes inside and outside the platform version array, so the
orphan guard is exercised. The **tier label** spans absent, `baseline`, `restricted` and `quarantine`.
Absent is a real case, because the tier policy defaults it rather than skipping it.

**Combine the axes pairwise, not fully.**

**Generate from both subjects and union the result.** A rule only the old policy can distinguish does
not exist in a corpus generated from the new one. A retirement is exactly the case a release must see.

An entry is a plain pod carrying a version pin. It carries no band and no residual. A residual for an
infrastructure workload would manufacture the assertion the corpus exists to prevent. Claim source
lives in the manifest, not on the entry, so the entry stays a plain pod the Kyverno CLI reads
unchanged.

The corpus is not signed. It is generated deterministically. CI regenerates it and fails on any diff.
That proves the same property more cheaply than a signature. The evidence output is what gets signed.

The generator is versioned and is not part of the subject, so it cannot bump the policy version.

There is no size ceiling. A ceiling truncates silently. Publish the entry count and the wall-clock
instead.

## Acceptance criteria

- [ ] The generator enumerates each predicate expression across satisfied, violated and absent.
- [ ] The version-pin axis covers inside and outside the array.
- [ ] The tier axis covers absent, `baseline`, `restricted` and `quarantine`.
- [ ] The axes combine pairwise, never fully.
- [ ] The generator runs against both subjects and unions the result.
- [ ] The document reports the old count, the new count and the union count.
- [ ] Each entry is one plain pod file, with no band and no residual.
- [ ] The manifest carries the checksum, the entry count and per-witness provenance.
- [ ] Claim source lives in the manifest, never on the entry.
- [ ] CI regenerates the spine and fails on any diff.
- [ ] The generator carries its own version, and the document reports it as `generator_version`.
- [ ] `wall_clock` is measured and published, and no check enforces it.
- [ ] No size ceiling exists anywhere.
