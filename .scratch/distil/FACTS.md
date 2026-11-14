# Facts brief from the mapping pass (2026-11-14)

> **Superseded in part.** This brief was written between the mapping pass and the design pass, and the four keystone checks (`keystones/K1` to `K4`) then corrected it. Read `DISTILLATION.md` for the checked account. The corrections:
>
> - **Fact 1.** 2026-08-28 is a branch commit. The rung label reached `main` on 2026-08-31, a signed tag on 2026-09-24 and the Flux pin on 2026-10-04. That first write was itself the only move: one jump by hand to the top rung. The floor is not what stops the proposer; the top rung plus tighten-only does that alone (K1).
> - **Fact 2.** "Tightening the cage does not change the number that is compared" is wrong as arithmetic. The compared total follows the rung the code *selects*, which a typed floor can move. It never follows the rung declared on the Namespace or enacted on a cluster. Three feedback paths are built and none has delivered a number (K2).
> - **Fact 3.** Only driftwood's twin publishes different reductions. Tuppence and ludlow copy the platform's four figures (K2).
> - **Fact 5.** Driftwood's and ludlow's totals are partial sums with no verdict. Driftwood's margin of GBP 3,850 is smaller than a line left out of the sum (K3).
> - **Fact 7.** The ICO line dominates driftwood (98.9%) and ludlow (99.5%) but not tuppence, where a twin forward-intel line is 81.8% (K3).
> - **Off the loop.** Computed semver is not off today's chain: the composer loads its engine rule on every run and refuses to compose without it. The hub twin's model code also feeds tuppence's largest priced line. The owner did choose the calibration programme's purpose, by the letter "A" on 2026-10-30 (K4).
> - **November commits.** The hub's `main` holds 20 commits dated November, not 22: 10 by the app identity and 10 by the truth surface, none by a person.

Twenty-six read-only readers mapped the estate against one loop. Their full maps, with file:line citations, are in the `maps/` directory beside this file. This brief is the digest. Where a fact matters to your work, open the map and the code and check it.

## The yardstick

The owner's statement of the original mission, 2026-11-14:

> "quantified risk and a reactive ratcheting process cage to mitigate the quantified risk until the risk is within financial tolerance of the organisation"

Read as a control loop: Q quantify exposure in money; T the organisation's declared financial tolerance; C compare; R ratchet the cage a notch; E enact it on the running system; X react when the world changes, and repeat until exposure is within tolerance.

## Where things are

- `fresh/<repo>`: clones of the remote default branches taken 2026-11-14: hub, platform, driftwood, tuppence, ludlow, nist, ico, feeds, insurer.
- `maps/*.md`: one map per area. Mission maps: A1 owner's words, A2 original thesis, A3 accretion timeline, A4 does the loop run, A5 Codex and calibration. Hub: H1 to H15. Platform: P1 to P3. Adopters: D1, D2. Publishers: F1.
- `backup/.scratch/`: planning text recovered from the owner's backup after the mapping pass started: the calibration programme's spec, design proposal, interview, tickets, issues and review, and October Codex resume notes. No reader had this.

## What the readers found

### The loop has never run end to end (A4, confirmed independently by A3, H13, H15, D1, D2, P2, P3)

1. Every adopter's Namespace has declared the tightest rung, `isolated`, since 2026-08-28 (`*/gitops/apps/namespace.yaml`, one commit each, never changed). On 2026-10-23 each adopter's `party.yaml` also set `floor: isolated`. The proposer only tightens. So there is no notch left and no tier proposal has ever been opened on any adopter.
2. The loop is open. The priced exposure never reads the enacted tier (`platform/compose/composition.py` around 3832 to 3845 and 5207 to 5215). Tightening the cage does not change the number that is compared.
3. The number each rung is said to buy is unsourced. `platform/graded/cage.py:71-72`: "self-declared, evidenced by nothing but this comment". Reductions 0.30, 0.70, 0.92, 0.98; costs 500, 2000, 6000, 15000. The adopter's own twin publishes different reductions (0.05, 0.30, 0.65, 0.90) at an evidence grade that earns no credit.
4. Selection is one lookup, not a ratchet: `cage.py:343-347` picks the loosest rung whose residual fits, else the last rung, then clamps up to the floor. There is no step-wise tightening, no loosening path and no stop condition written anywhere in code, ADRs or glossary.
5. Exposure is not within tolerance for two of three adopters at the tightest rung: tuppence £2,057,390 against £15,000 (`breaches_band: true`, nothing reacts); ludlow £61,725,982 against £5,000 (verdict null); driftwood £36,150 against £40,000 (verdict null because the CVE line is unpriced), and inside tolerance only because of the unsourced 0.98.
6. The tolerances (40,000, 15,000, 5,000 GBP) date from an automated build commit of 2026-07-31. Maximum reduction is 0.98, so no rung can fit a line whose uncaged loss is more than 50 times tolerance.
7. Quantify does run daily and for real (`driftwood/.github/workflows/propose-tier.yml`, cron 06:47). 98.9% of driftwood's priced subtotal is one ICO fine line at an editorial frequency; that line is 2.0781% of turnover for all three adopters, so it depends only on size.
8. React stalls at a merge: the publisher's fetch clock proposes, nothing merges; one Renovate feed bump has ever merged (2026-09-01) and it moved no money. Four of six feed clocks re-read a committed fixture.
9. Enact has five breaks: an unautomated merge, a manual tag cut, a self-pin 164 commits behind main, no persistent cluster, and admission that fires once so running pods are never re-caged. The cage is observed daily, but as a static state at one rung on a throwaway cluster, with a placeholder for a WAF image that exists in no registry.
10. The chain as found is 67 files, 24,636 lines: 7.4% of the estate's code.

### Whose idea each part is (A1, A2)

- Owner's own dated sentences back: money-denominated risk and the balance sheet (2026-07-23); the cage as graded constraint, not go or no-go (2026-07-31); always caged, the spec of the cage changes, no gate (2026-08-20, 08-22, 09-02); tightening costs more and partly mitigates risk; proportionate to the organisation's size (2026-08-19); continuous refresh and re-proportioning when a regulator's fine changes.
- No owner sentence before 2026-11-14 backs: the word "ratchet"; the word "tolerance" or any figure, band or unit for appetite; the compare step; the stop condition "until within tolerance". "Ratchet" appears in the record only as the assistant's name for a defect or a rejected design (ADR-0015:68; `platform/computed-semver/coverage.py:508-513`, open limit `cage-ratchet-one-way`).
- The cage ladder, the appetite band, FAIR Monte-Carlo, the ordinal £, the north-star principles and the truth surface all trace to the assistant on bare agrees or on ADR-0025 delegation. The owner said bare agrees were often fatigue.
- Tension: the record made the £ ordinal ("not an expected annual loss") on a one-word reply, but "within financial tolerance" needs a figure that can be compared with a tolerance.
- The June 2026 PRD has no money, tolerance or compare step. It is a delivery design: policy as a signed, versioned dependency, adopted by reviewed pull request, on Flux. It lists a risk-intelligence agent as a non-goal. The loop entered on 2026-07-23, inside a talk spec.
- The 2022 thesis: policy as a versioned dependency, with the seven "-ables" (visible, communicable, consumable, testable, usable, updatable, measurable), and "purposeless policy is potentially practically pointless policy": policy must carry its why. Simplicity there meant one string doing two jobs and a one-line consumer gate.

### How the complexity accreted (A3, H13, H15)

- Tracked lines grew from 11k to 1.89M. 70.5% is October copies of other repos' diffs and agent records committed into `hub/.scratch`.
- Each of three reviews (2026-08-27, 08-31, 09-02) made the estate larger. None removed a directory.
- 80 of 169 eco-system tickets exist only to repair, record or verify an earlier ticket's output; 56 of the 72 from ticket 98 on.
- The truth surface answered an agent-process failure (claiming deployments while Docker was off), not a need of the loop. Its last runs print pass=117 unchanged; 61 of those passes are self-proof, 42 observe another party.
- Hub main in November is 22 commits, none by a person: daily truth records merged by the app identity.

### Duplicates

- Two risk engines: the hub twin (`hub/twin/pricing.py`, propagation over a causal graph, 11 real firms) and the platform (`platform/fair/fair.py`, PERT Monte-Carlo). No adopter calls the hub pricing engine; the adopters' published £ is about 25 lines of inline arithmetic per emitter.
- The compare and fold logic exists three times (`platform/wargamer/wargamer.py:251`, three adopter `selection_policy.py` copies, `platform/graded/cage.py:select_tier`) with hub gates that fail when they disagree.
- Three adopters are near-clones: about 600 lines of declaration each, the rest copied machinery with drift between copies.
- Two cage vocabularies: hub observe/warn/constrain/block; adopter baseline/restricted/quarantine/isolated.

### Off the loop

- Calibration programme (2026-10-30/31): about 49k lines to let a local 4B model earn permission for the twin's judgement skills (custody, instrumented Xpdf, ELF closure, Linux lease). No operational caller; the qualification registry is empty.
- Twin forecasting, scoring, skills, substrate, sensor admission, misuse catalogues, ethics gate: no forecast or score changes any adopter's money or tier.
- Computed semver (14.5k lines): feeds none of the loop steps; every real release computed major.
- Identity, access, posture, device plane: shelved.
- `talk/` is 11% presentation; the rest is the truth-gate harness and its captures.

### Line tallies (readers' classification, all repos, including specs and data)

By necessity: kernel 35,793; support 287,068; duplicate 64,435; ceremony 111,054; off mission 180,496; unknown 5,295. Total classified 684,141 (excludes the 1.3M-line October record dump).

### What each reader said the simplest replacement would be

- Platform money and cage: one `loop.py` of about 150 lines (closed-form PERT mean, a four-row rung table whose reduction column must name its basis, exposure summed over the party's lines, `next_rung(exposure, tolerance, current)`), plus one `cage.yaml` of about 150 lines.
- Adopter: about 235 lines: `party.yaml`, a Namespace with the tier label, one Flux source and Kustomization to a signed cage tag, one scheduled workflow, Renovate config.
- Publishers: about 450 lines of data and 120 of code.
- Checks: one loop check of about 150 to 250 lines that prints `exposure= tolerance= tier= within=` and appends it to a ledger.
- Records: one `LOOP.md` of about 150 lines.
