# 97 — A flip nobody recorded goes red

Type: decision (HITL)
Status: open
Blocked by: none

## Question

`twin/ENACT_MODE` is one word in a checked-in file, and it decides whether the twin may merge and
may push to an enactment repository. Since 2026-09-04 nothing goes red when it moves. Pair the
switch with a companion record that names the mode, the commit that authorised it and the date,
and assert that the two agree. A recorded flip like `f959187` stays green. A flip nobody recorded
goes red, under a test whose name says which switch moved. Done = the owner has decided the shape
of the acknowledgement, one test asserts it, and flipping the mode without the record is proved
red.

## Notes

Charted 2026-09-04 from the round-2 review of the hub CI repair; the record is
`.scratch/ecosystem/CI-2026-09-04.md`.

**Why this is HITL and not delegated.** It invents an authorisation shape: a file whose content is
"the owner said so, here". ADR-0025 delegates architecture and keeps authorisations with the
owner. The assistant should not design the form in which the owner's permission is recorded.

**The history, because both previous positions were wrong and the third should not be a guess.**

1. Until 2026-08-29 an autouse fixture in `tests/test_enact.py` exported
   `TWIN_ENACT_MODE=operations`, so the suite asserted a guard nobody shipped and the shipped
   default was asserted by nothing.
2. From 2026-08-29 the fixture only cleared an ambient variable, and one test hard-coded the
   shipped word. The note there predicted that a flip to `development` would turn thirteen tests
   red, "because a weakening that shows in a test is the only kind anybody notices".
3. On 2026-09-04 the owner flipped it, standing, and the prediction came true at thirty-five. The
   same CI run carried two unrelated real defects, a missing `jsonschema` pin and a dead
   `type: ignore`, and both were invisible behind the wall. The fixture now arms the guard at a
   named mode, which the reviewer proved is a STRONGER capability test: mutating `decide()` to
   admit everything moves the armed count from 0 failures to 39, where on the old arrangement it
   moved 35 to 40.

So a permanently-red test is not a signal, and no signal is not the answer either. The property
worth having is narrower than both: not "the mode is X" and not "the mode never changes", but
"the mode and the record of who authorised it agree".

**What is already done, so this ticket does not redo it.** Invariant 48 reports the ambient mode
on its detail line (2026-09-04). Ticket 96 carries it on the TRUTH line. Both make the mode
VISIBLE. Neither makes an unrecorded flip FAIL, which is this ticket.

## Questions for the owner

1. What shape should the acknowledgement take? A sibling file (`twin/ENACT_MODE.why`), a header
   inside `ENACT_MODE` itself, or a signed commit trailer?
2. Should the record name an expiry? A development window that nobody closes becomes the default
   by silence, which is how position 1 above happened.
3. Should the assistant be able to write that record, or only the owner? If the assistant can
   write it, the alarm catches accident but not intent.
