# 40 — Driftwood proves the composed set in force from signed sources in CI

Type: task (AFK)
Status: resolved
Blocked by: 03, 10, 16

## Question

Build the Q1 sample, the Q2 pre-registered window, the Q3 scheduled ephemeral-KinD workflow under the caged observation lane, and the Q5 ResourceSet over the adopter's composed tag with platform and nist as verified sources, wired into verify-all.sh on driftwood.

## Notes

Graduated 2026-08-28 from ticket 16's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. Driftwood samples the five facts per source with the three falsifiers declared first, in a scheduled ephemeral-KinD run inside the observation lane. On a cluster reconciling the real remotes, four of five facts are observed true for every source; fact two is red until the controller lands, exactly as ADR-0023 D3 predicts. A hand-typed sample is refused: the grader checks the run id, the committing identity and the signature, because a hand-run sample is a rehearsal and is never cited.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.

> **Correction, 2026-09-01 (ecosystem ticket 60).** The paragraph above cites a four-of-five-facts
> observation that no citable record supports. `drift/samples.jsonl` on driftwood's main carries no
> five-fact record at all: its newest lines (2026-08-13) are the retired probe's, and
> `.github/workflows/drift-sample.yml` had not run on the remote when this Answer was written -- it
> only reached driftwood's default branch on 2026-08-31 (merge bd19e8c) and its first firing is
> still ahead. "The TRUTH line of 2026-08-29" was itself a local rehearsal (see the map's
> 2026-08-31 correction). The machinery this Answer describes is real and unchanged; the OBSERVED
> figure it reports is withdrawn until a lane-committed sample grades on a TRUTH line, which
> ticket 60 owns.
