# 90 — Identity is shelved for this build

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Ticket 75 Q12 decided (b): the identity and attestation substrate is designed and shelved for this build. Artefact attestation is real (24 of 24 tags verify against Rekor). Actor attestation has never been observed on a citable run, all six identity scripts skip, and federation is one trust domain with no peer. The claim in NORTH-STAR §1 must become true rather than aspirational.

1. Move the six identity-plane verify scripts to `talk/verify-exclusions.txt`, each with a reason that names what it waits for (an identity lane that grades the actor half), so the gate stops printing six could-not-looks that no ticket on this map will clear.
2. NORTH-STAR §1 reads "every artefact is attestable". Principle 6 keeps "every actor is attestable" as the design, marked as shelved for this build with the date and this ticket.
3. The map's note "identity is spine, not cut" is amended by ticket 75. Ticket 12's Answer gains a dated comment. Ticket 68 (federation gets its peer) is ruled out of scope for this map and closed; it returns with the identity lane.
4. `verify-demo.sh` and the deck must not narrate actor attestation as observed.

Done = the six scripts are excluded with reasons on the next citable run, the §1 sentence is true on that run, and ticket 68 is closed with a line in the map's Out of scope.

## Notes

Charted by ticket 75 (Q12). Overlaps ticket 86 item 3, which this ticket now owns. The identity lane is fog: it is the first thing after this map.

## Comments

**2026-09-03, ticket 73.** ADR-0027 item 6 hands the identity lane one more instant: the source
verifier now chains at the later of the tagger time and the certificate's notBefore within a
declared 60s bound, and records the Rekor integrated time (the signed entry timestamp, verified
against a pinned Rekor key) as the instant it would ideally use. That is the transparency check the
verifier's docstring names as its ceiling, so it belongs here, with the actor half, not to 73.

## Answer

**2026-09-04.** Built on branch `ticket-83-the-truth-line-says-what-it-measured` (shared with
ticket 83, which owns the exclusions/manifest machinery this ticket uses), hub only.

Map line: Identity is shelved and the record says so — §1 claims the artefact half, principle 6
keeps the actor half marked shelved, and the six identity scripts leave the gate with reasons.

### What was built

1. **`talk/verify-exclusions.txt`** gains the six identity-plane scripts, each with a reason that
   names what it waits for — an identity lane that grades the actor half — and what specifically is
   missing (a cluster where SPIRE is Istio's CA; a second trust domain; a reachable access plane;
   vTPM-backed nodes attesting; SVIDs being issued; a live workload identity to reach a secret
   with). `excluded=` goes from 2 to 8.
2. **`NORTH-STAR.md` §1** now reads "every artefact is attestable", with a paragraph under it
   recording what the clause said before, when it changed, on whose decision, and why: the sentence
   the estate is measured against may claim only what a citable run can be watched doing.
   **Principle 6** keeps "Every actor is attestable" as the design and carries an explicit
   `SHELVED for this build` marker naming the owner's decision (ticket 75 Q12, 2026-09-02), this
   ticket, today's date, both halves by name, and the exclusions file. The falsifiability half of
   principle 6 is called out as not shelved.
3. **`verify/record/verify-record-states-the-purpose.sh`** gains step 4b: §1 says "every artefact
   is attestable" and no longer says the actor clause, principle 6 carries the shelving marker with
   ticket and date, and `talk/verify-exclusions.txt` actually shelves six scripts with that reason —
   so the record cannot claim a shelving the gate does not perform. Its selfcheck gains two legs: a
   copy of NORTH-STAR with §1 reverted to the actor claim must FAIL, and a copy with the shelving
   marker struck out must FAIL.
4. **`talk/narration.json`** (and so `talk/deck.md`, regenerated): the twin-loop narration said the
   score card "is signed by an agent identity that attests the absence of a human", in the present
   tense of something observed. It now says that is the design, that the actor half is shelved for
   this build, that nothing on the run observed it, and what the run *did* observe — the artefact
   half. `talk/verify-demo.sh` had no actor narration to change.
5. **`talk/RUNBOOK.md`**: beats 5, 5b and 5c are relabelled `(shelved)` with a paragraph telling the
   presenter that the gate does not grade those rows, to narrate them as design and never as
   observed, and to say so plainly if one is demonstrated live. Beat 5 proper is now the artefact
   half, which stays graded. Break-glass is split out of 5c and stays in the gate: it passes
   offline. The runbook's thesis line changed from "every actor attestable" to "every artefact
   attestable" with the same note.

Item 3 of the ticket was already on disk (the map's spine note, ticket 12's dated comment, ticket
68 closed with its Out-of-scope line). Ticket 86's item 3, which this ticket owns, is answered with
a dated comment on ticket 86.

### Decisions (all delegated, ADR-0025, 2026-09-04)

1. **The six are the cluster-skipping identity-plane set, not the RUNBOOK beat list.** Ticket 12
   cited beats 5/5b/5c (identity, posture-projection, reach-secrets, access, break-glass, eud);
   ticket 75 Q12 and the run grades point at identity, federation, access, eud, posture-projection
   and reach-secrets. I took the second, for two reasons. **Break-glass passes** — it is graded
   offline and green on run 65, and excluding a green removes an observation the estate really
   has; the honest reason to exclude a script is that it never looks, not that it sits under an
   identity heading. **Federation belongs in** — one trust domain with no peer is the clearest case
   of the actor half being unbuilt, and it is exactly what ticket 68 was closed for. Six, not seven
   or eight.
2. **`verify-source-verification.sh` stays in the gate.** It is the gitsign source controller
   (ticket 41): it grades whether a signature on an artefact verifies against a pinned identity.
   That is artefact attestation — the half §1 now claims — and it is the wrong thing to shelve when
   the point of the edit is that this half is real. It skips today for want of a cluster, and that
   skip stays declared in `talk/verify-manifest.txt` as a `never`, which is honest: it is a
   could-not-look, not a shelved question.
3. **The twin-loop narration is reworded, not annotated.** It was actor attestation in the present
   tense of something the run watched, which is the exact shape ticket 90 exists to remove. An
   annotation beside a sentence still lets the sentence be read aloud. The certificate identity
   regexp narration (deck line 179) is untouched: that is artefact attestation and it is true.
4. **`verify-record-states-the-purpose.sh` was extended rather than a new script added.** One
   record gate, one place to look. The record and the gate are also cross-checked in the same
   script (the sixth check counts the shelved lines in the exclusions file), because a record that
   states a shelving the instrument does not perform is the failure mode worth catching.
5. **The RUNBOOK beats are relabelled, not removed.** It is a presenter document and the beats are
   what the July tour did; deleting them loses the record and the instruction. Labelling them
   `(shelved)` with a paragraph on how to narrate them is the smaller and more honest change, and
   it puts the warning where a presenter will actually read it.
6. **Principle 6 carries three dates, not one.** The owner's decision is 2026-09-02 (ticket 75
   Q12); the record edit is 2026-09-04. The brief suggested stamping 2026-09-03; I kept the
   decision date attached to the owner and the edit date attached to this ticket, because a date
   beside an owner attribution is the thing ticket 95's gate checks and a wrong one would be a
   quiet misattribution.

### Verified

- `bash verify/record/verify-record-states-the-purpose.sh` → PASS, with the five new §1 and
  principle-6 assertions and the exclusions cross-check all ok.
- `bash verify/record/verify-record-states-the-purpose.sh selfcheck` → PASS: a §1 reverted to the
  actor claim FAILs, and a principle 6 with the shelving marker struck out FAILs.
- `bash verify/demo/verify-demo.sh` → PASS after regenerating `talk/deck.md`.
- `python3 talk/build_deck.py --check talk/deck.md` → no bad rows.
- `bash verify/truth-line/verify-truth-line.sh` → PASS: the manifest still places all 99 discovered
  scripts with the six now excluded.
- Replaying run 65's real grade table against the new exclusions file and manifest gives
  `pass=59 [observed=13 self=37 simulated=6 meta=3] fail=11 skip=16 [never=9 waits=7] excluded=8
  total=94 ceiling=77` — the six leave `skip=` and land in `excluded=`, and the ceiling is
  unchanged, because a `never` and an exclusion are both outside it.

**The citable line comes from the next clock run.** The figures above are a replay of run 65 and
local runs of the two scripts; nothing was appended to `talk/truth.log` by hand.

### Not done

- The SKIP reason lines inside the six scripts themselves (ticket 86 item 4) are untouched. They
  are not run any more, so they print no reason; the reason now lives in the exclusions file, in
  the hub, which an agent may commit. Editing them would have meant a push to
  `policy-as-versioned-platform` and `-tuppence`, which is the owner's.
- Ticket 90's own done condition ("the six are excluded on the next citable run, the §1 sentence is
  true on that run") is observed after the clock runs, not asserted here.
- **Excluding the six also retires five offline proofs that were passing every run.** Five of the
  six printed `SKIP: offline proof holds; live tail could not look: ...` on run 65 — identity,
  federation, access, eud and posture-projection. Their offline halves were reached and true on
  every run; only `tuppence/reset/verify-reach-secrets.sh` had no offline half (it prints the bare
  cluster reason). So the exclusion is not free: the gate stops repeating six could-not-looks and
  loses five standing proofs with them, and nothing else grades those five today. The identity
  lane owes them back — a re-entry that restores the six must restore those five greens before
  the actor half is claimed to be new work. Recorded in `talk/verify-exclusions.txt`'s header so
  the price is visible where the exclusion is.

## Comments

**2026-09-04, review fixes.** Two findings, both fixed on this branch.

1. The consequence above was unrecorded. It is now in `talk/verify-exclusions.txt`'s header and in
   `## Not done`, with run 65's five `offline proof holds` SKIP lines as the citation.
2. Ticket 83's Answer stated pre-shelving figures on the same branch (`skip=22 ... excluded=2`).
   Corrected there; this ticket's replay (`skip=16 [never=9 waits=7] excluded=8`) was already
   right and is what run 70 confirms.
