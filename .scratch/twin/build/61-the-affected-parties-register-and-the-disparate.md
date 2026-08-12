# 61 — The affected-parties register and the disparate-impact channel

**What to build:** People outside the contracting org bear consequences without holding the perspective. The
**register** makes them visible; the **disparate-impact audit channel** gives differential harm a
route to surface.

Neither solves the underlying asymmetry — the spec is explicit that no constraint here constrains
power — but invisibility is a separate harm from powerlessness and this one is addressable.

**Blocked by:** 27, 60

**Status:** done (2026-08-11)

**Reading list:** Decision ticket 15. Spec stories 69, 70.

- [x] Register of parties affected by modelled consequences who do not hold the perspective.
      `twin/schema.py`'s `scenario` schema carries a new required `affected_parties` field (a
      mini-schema of `id`/`who`/`consequence`, optional `note`); `twin/affected_parties.py`'s
      `register()` flattens every scenario's own declarations in an overlay into one list
      (`tests/test_affected_parties.py::test_register_flattens_every_scenario_in_the_overlay`).
      All ten scenario fixtures (`twin/fixtures.py`) now name real, dated outsiders — Carillion's
      ~30,000 unpaid subcontractors and pension-scheme members, Enron's 401(k) holders and
      California ratepayers, NMC Health's patients and workforce, Wirecard's prepaid cardholders
      and merchants, and so on.
- [x] The register is populated as a required step of scenario authoring, not optionally.
      `affected_parties` is required, and `list_of` is already non-empty-only — the same rule
      `components`/`world_models` carry — so a scenario cannot satisfy this with an empty list
      either (`tests/test_affected_parties.py::test_a_scenario_with_no_affected_parties_field_is_refused`,
      `test_a_scenario_with_an_empty_affected_parties_list_is_refused`). An entry naming a
      protected characteristic is refused by the same `refuse_special_category` every other field
      is already subject to (`test_an_affected_party_naming_a_special_category_is_refused`).
- [x] A disparate-impact audit channel exists with a defined route and respondent role.
      `twin/disparate_impact.py` — `twin disparate-impact-audit --finding F --source S --out O`
      raises a finding (sealed to the same `refuse_special_category` refusal the model repository
      itself carries: a finding naming the protected characteristic is refused, never just the
      differential outcome); `twin disparate-impact-respond --audit A --response R --role
      disparate-impact-respondent --out O` closes it, and refuses any role but that one — a new
      role in `twin/roles.yaml` (version 2 → 3) — even when the role supplied is itself registered
      (`tests/test_disparate_impact.py`, harness guard
      `disparate_impact_audit_channel_is_sealed_and_role_gated`).
- [x] The register is published alongside the constraint set.
      `affected_parties.published()` carries `constraints.pin()` — the identical version/digest
      `twin constraints` itself reports — so a reader of `twin affected-parties --repo R --org O
      --out F` can tell which published constraint set it sits beside
      (`tests/test_affected_parties.py::test_published_carries_the_constraint_sets_own_pin`).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`disparate_impact_audit_channel_is_sealed_and_role_gated`), zero
      weakened, zero of the constitution's sixteen touched. Cites decision ticket 15.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No capability file ticks against this ticket: it closes decision ticket 15's carried-forward
      item, but decision ticket 15 has no tracked capability file among the seven in
      `twin/capabilities/` — the identical situation build tickets 60 and 62 record against the
      same decision ticket. The register's own artefact (`verbs.affected_parties`) and the audit
      channel's artefacts (`twin/disparate_impact.py`) both declare `depth.grade: None` rather than
      fabricate a capability to fill the slot. Landed and ticked nothing.
