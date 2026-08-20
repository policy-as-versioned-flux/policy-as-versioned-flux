# 05 — Where the gate runs, and what happens when it disagrees with the human

Type: grilling
Status: open
Blocked by: 02, 03

## Question

The mechanism exists (`kyverno apply` offline, as `verify-shift-left.sh` proves). This ticket decides
what it *is* once wired into releasing.

**Decide:**

1. **Refuse, warn, or correct.** A release declares `2.1.0`; the evidence says the change can fail a
   currently-compliant workload, so the bump is major. Does the gate (a) fail the release, (b) warn
   and proceed, or (c) rewrite the tag to `3.0.0`? (c) is seductive and probably wrong — ADR-0002
   makes the *reviewed* upgrade non-negotiable, and a gate that silently renames the thing under
   review erodes exactly that. But a gate that only warns is a gate that gets ignored.
2. **The override path.** There will be a legitimate case where the human is right and the corpus is
   misleading. Is there an override, what evidence must it carry, and is it logged the way this
   estate logs every other constraint removal?
3. **When it runs.** Pre-tag in CI, at release, or as a check on the Renovate bump PR at the
   consuming end? These are different audiences: the publisher deciding what to call the release, and
   the adopter deciding whether to take it. Possibly both, with different consequences.
4. **What it costs.** Evaluating a corpus against two versions on every release must be fast enough
   not to be routed around.

Note the interaction recorded in the map's fog: after the six-org split the publisher and the adopter
are different repos in different organisations, so "where it runs" may have two answers.
