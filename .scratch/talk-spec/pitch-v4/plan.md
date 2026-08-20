# Pitch v4 — plan

**To:** Andy, CEO of Control Plane, the funder. **Ask:** back the next stretch of runway.
**Format:** 6:40 (400s ± 10s). Flexible slide count, paced to the script — not locked to a
per-slide timer. Every fact below is verified live today (2026-08-19), not carried forward from
any prior draft. **Source of truth for content:** `estate/talk/deck.md` + `estate/talk/RUNBOOK.md`
(the current, real, 35–40 min conference deck) compressed to its sharpest beats, reframed for a
funder instead of an engineering room. **Source of truth for numbers:** live command output,
captured fresh in `.scratch/talk-spec/pitch-v4/captures/`.

## Verified facts this script is allowed to state as true

- 3 real KinD clusters up (`driftwood`, `ludlow`, `tuppence`), Flux reconciling, real signed commits.
- FAIR engine, `driftwood`'s cart-PII scenario: ALE £19,559 · VaR₉₅ £30,948 · TVaR £34,087 ·
  £ carried £34,958 (TVaR + risk-load, never the mean).
- Proportionality: identical control, identical £21,107.29 risk-bought, three institutions —
  `driftwood` (tolerance £40k) → **Audit**; `ludlow` (£5k) and `tuppence` (£15k) → **Deny**. One
  number, three verdicts, driven only by the appetite band.
- Graded enforcement is real: a workload that falls behind keeps running, caged by degree
  (limits/NetworkPolicy/dropped caps/read-only-fs), never a cliff-edge Deny.
- Shift-left CI genuinely catches a version flip offline, before merge (v1.0.0 passes, v2.0.0 fails
  on `readOnlyRootFilesystem`).
- The living loop (signed feeds → war-gamer → signed PR, never auto-merged) is real code, not a
  stub — not executed live in this capture pass because it would open a real PR (a side effect this
  session must not cause); this is stated honestly, not hidden.
- `estate/talk/verify-all.sh --live`: **27 pass, 1 fail**, today, live. The fail is real and named:
  `tuppence`'s posture-gated reach + secrets check, because the identity stack (SPIRE+Istio+OpenBao)
  is stood up on `driftwood` only — not yet on `ludlow`/`tuppence`. This is not hidden; it is the
  clearest, most concrete thing the next round of funding buys.
- `policy/` and `fleet/` are already split into their own org repos (real org-of-repos structure,
  not a monorepo pretending to be one) — evidence the platform/institution boundary is real, not
  aspirational.

## What this script does NOT claim

No OSCAL upflow live run, no NIST catalog live pull, no ICO penalty-feed live run demoed — named as
real-but-not-demoed-live where it matters, never asserted as proven today. EUD device trust on
Windows/Linux is virtual (UTM vTPM), narrated as such — the one live hardware root is the Mac
Secure Enclave. The war-gamer's signed-PR loop is real code, shown as code/diagram, not run live
this session (side-effecting). Balance-sheet/underwriting consumption is vision, framed as vision,
not claimed as built.

## Narrative arc (funder framing — vision + proof + ask, not an engineering tour)

A CEO backing a second round wants three things a principal-engineer audience doesn't need spelled
out: **is it real, is it ours to own, and what does the next cheque buy.** The arc:

1. **Hook** — the number a breach actually costs, live, in one line.
2. **Thesis** — governance as a priced, versioned, continuously re-tuned judgement, not a checkbox.
3. **Proof of life** — not slideware: real repo, real signed commits, real clusters, on screen.
4. **The money shot** — same control, three institutions, opposite verdicts, because the £ differs.
5. **Not a cliff-edge** — graded response, a spectrum of consequence.
6. **The economics** — Total Cost of Risk: staying current is the cheap path, provably.
7. **The maths is real** — actuarial-grade FAIR engine, the self-check, live.
8. **Exemptions, dissolved** — conditional policy replaces the favour economy.
9. **The living loop** — the estate war-games itself; AI proposes, never disposes.
10. **Provenance** — every actor, human or machine, cryptographically attestable.
11. **The honest red** — 27 of 28, live, and I'm showing you the one that's red — because that's
    the thesis working on itself, and it's also exactly what the next stretch of work closes.
12. **What got built** — the scale and pace of execution so far (the ROI argument).
13. **Why Control Plane, why now** — Flux load-bearing, the AI-governance moment, nobody else
    telling this story end to end.
14. **The vision** — risk becomes one £ line on the balance sheet, insurance-grade.
15. **The ask** — specific: close the identity rollout, tour the deck, land a design partner.
    Give me the runway.

## Segment budget

~2.3–2.6 words/sec measured pace (TTS voice `andy3`) → target **~950–1000 spoken words** across
**16 segments**, averaging ~60 words (~23–25s) each, hook and ask longer/shorter by design. Final
sizing is decided empirically: draft script → generate real audio per segment → sum real durations
→ trim or expand specific segments → regenerate only those → repeat until 400s ± 10s. Slide count
and cut points follow the script, not a fixed timer, per instruction.

## Visual plan (real, per segment)

Prefer a real captured terminal screenshot wherever a beat has one; a Mermaid diagram wherever the
beat is structural/systemic (the living loop, the hourglass, provenance's one-root chain); a clean
built mockup (table/stat block) where raw terminal output would be noisy; one restrained, original
visual for the "checkbox is a binary lie" beat rather than a stock meme image (no external image
fetch — build it as a small original graphic, in keeping with "no URLs unless the user gave them").

| # | Beat | Visual |
|---|---|---|
| 1 | Hook — breach cost | real terminal: `fair.py summary` |
| 2 | Thesis | typographic slide + one original "binary lie" graphic |
| 3 | Proof of life | real terminal: `kind get clusters` + `kubectl get nodes` |
| 4 | Money shot | built table (3 institutions × £ × verdict) + real terminal snippet |
| 5 | Graded response | original tier diagram (spectrum, not cliff-edge) |
| 6 | TCoR economics | built stat block / simple cost-curve mockup |
| 7 | The maths is real | real terminal: `fair.py selfcheck` |
| 8 | Exemptions dissolved | real terminal: `verify-conditional.sh`/`verify-exemption.sh` |
| 9 | Living loop | Mermaid: feeds → war-gamer → signed PR → human → merge → £ moves |
| 10 | Provenance | Mermaid: commit / workload / human / device → one root |
| 11 | Honest red | real terminal: `verify-all.sh --live`, the FAIL line visible |
| 12 | What got built | built stat block: orgs, files, verify scripts, commits |
| 13 | Why Control Plane / why now | Mermaid: the hourglass (from `deck.md`, reused verbatim — it's
   the project's own current canonical diagram) |
| 14 | The vision | same hourglass, balance-sheet line highlighted |
| 15 | The ask | clean closing slide, 3-line "what this buys" |

(15 visual beats, 16 spoken segments — segment 1's hook and segment 2's thesis can share slide 1/2
1:1, adjusted once the script is final; exact slide-to-segment mapping finalised at slide-build
time once segment durations are known.)

## Pipeline (this run)

plan (this file) → script → adversarial review (fact-check against captures + funder-fit + honesty
check) → fix → generate real audio per segment (`echo "<line>" | python3 tts.py`, confirmed working
non-interactively) → sum durations, trim/expand + regenerate to hit 400±10s → build slides (HTML +
headless Chrome render, reusing `demo/`'s render mechanics, new content) → assemble segment clips
(image + trimmed audio, reusing `demo/assemble.sh`'s ffmpeg mechanics) → concat → final video →
send to user.
