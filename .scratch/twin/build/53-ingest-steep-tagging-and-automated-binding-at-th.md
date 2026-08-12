# 53 — Ingest, STEEP tagging, and automated binding at throughput

**What to build:** Binding **fully automated at volume**, trusted downstream rather than gated at entry — because
gating at entry cannot reach the throughput the twin needs. Use-gating, contestability and
calibration are what make that safe.

Blocked on the substrate recipe as well as the skill, because "at throughput" needs volume to be at
throughput *against*, and until substrate exists there is nothing to run at volume.

**Blocked by:** 43, 48

**Status:** ready-for-agent

**Reading list:** Decision ticket 11. Spec stories 12, 15.

- [ ] Ingest pipeline runs unattended at a declared throughput against substrate volume.
- [ ] Every ingested item is provenanced — which is what later makes the benchmark quarantine auditable.
- [ ] No human gate at entry; the safety argument rests on downstream gating and is documented as such.
- [ ] Throughput is measured and reported, not assumed.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
