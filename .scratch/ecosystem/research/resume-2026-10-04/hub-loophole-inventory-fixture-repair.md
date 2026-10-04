The root ADR-0026 test fixture now copies inventory only when the source actually contains it. Production composition and its missing-instrument refusal are unchanged.

The authentic apps3.0.1 archive reproduced CI exactly:14 failures/12 passes, with each failure at the unconditional inventory copy. After the conditional copy, the same14 cases reached a legitimate composer refusal: old tuppence still declares CVEv2 without inventory. Driftwood/ludlow's absence of a CVE subscription does not describe tuppence. This second red result is retained and not called a product defect.

Under root's explicit scope direction, the copied control-hole fixture now removes only its unrelated `feeds/feed/cve` edge when genuine inventory is absent. No empty inventory, fabricated scan, production source change or weakened composer guard is introduced. Inventory-bearing source keeps its real inventory and CVE edge. One added public-composer regression restores the exact source CVE edge with inventory absent and requires the ADR-0035 refusal.

Validation uses isolated archives of actual signed apps3.0.1 and signed inventory-bearing Stage2 candidates, with clean released tools5 `703eff6aee959843c4160aa54fd03413f62858cc` parents. All original26 cases plus the negative regression pass on both layouts: old scope-isolated27/27 in70.06s; native inventory-bearing27/27 in134.36s. The owned patch stayed byte-identical throughout verification. This fixture verification does not approve evolving Source A producer output or final rollout.

The initial parallel-worker run did not inherit the estate override and is excluded. The saved verifier now runs serially and requires every collected case to use the isolated estate. No selected test-file type-check gate is configured; the complete suite imports and executes the source.

Owned patch: `hub-loophole-inventory-fixture-repair.patch`; machine checkpoint: `hub-loophole-inventory-fixture-repair.json`; reproducible local runner: `loophole-inventory-layout-check.py`. Red and green logs remain adjacent. No root commit, external mutation or shared clone edit was made.
