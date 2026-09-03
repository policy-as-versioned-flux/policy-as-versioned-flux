# 88 — The second identity

Type: task (HITL)
Status: resolved
Blocked by: none

## Question

Ticket 75 Q6 and Q14 decided that principle 5 binds for the demonstration and that, for the development window, the assistant reviews and merges as a second identity while the owner authors and pushes. Today one identity exists (chrisns) and the only app installed on the org is Renovate. Nothing can require a review from a different identity until a second identity exists.

The owner does, in this order:

1. Create one machine identity for the assistant. Preferred: a GitHub App owned by the org, named so a reader of any PR sees it is the assistant (for example `fable-reviewer`), with `contents: write`, `pull_requests: write` and `metadata: read`, installed on all nine repositories. Second choice: a machine user account with the same reach. Record the choice and the identity's name here.
2. Put the credential where the assistant's shell can read it without it entering any file in any repo. Record the location, not the value, here.
3. Tell the assistant. The assistant then verifies the identity by reading its own login through the API and records the result here.

After 1 to 3, the assistant does:

4. Flip `twin/ENACT_MODE` to `development` and add a dated line to the `enact_guard.py` docstring that cites ticket 75 Q6 and Q14 and names the identity. The guard's `operations` behaviour stays tested by the harness invariant.
5. Update the memory note on push and merge authorisation so a later session does not refuse what this ticket permits.

Done = a PR authored by chrisns is approved and merged by the second identity on one repo, and the merge is recorded here with its URL. Ticket 87 then applies the protection that requires it.

## Progress

- **2026-09-03, step 1 done.** The owner chose a GitHub App and the name `pavc-other-hand` (the assistant's first two names were rejected as unfit to be seen on every merge). Registered through the owner's browser after the owner confirmed sudo mode: owner `@policy-as-versioned-flux`, App ID `4819564`, client ID `Iv23lib7FFTihXttcXNX`, homepage the hub repo, webhook off, permissions Contents read and write, Pull requests read and write, Metadata read, installable on any account (the estate is nine orgs with one repo each). Settings page: https://github.com/organizations/policy-as-versioned-flux/settings/apps/pavc-other-hand
- **Code.** `twin/other_hand.py` mints the app JWT with `openssl` (no new dependency) and installation tokens; `tests/test_other_hand.py` covers the JWT shape, the signature against the public key, the HTTP calls against a fake opener, and the settings. Key path: `PAVC_OTHER_HAND_KEY`, default `~/.config/pavc-other-hand/app.pem`.
- **2026-09-03, step 2 done.** The owner approved the download in chat. The private key (fingerprint `SHA256:V5cL15DaLS+DBw504YaDho2c0YA+kKDKlz07qDAC9fA=`, shown on the app page) was downloaded once through the owner's browser and moved to `~/.config/pavc-other-hand/app.pem`, mode 600, directory mode 700. It is in no repository and no shell history prints it.
- **2026-09-03, step 3 done.** `python -m twin.other_hand whoami` prints `pavc-other-hand`. Installed on all nine orgs through the owner's browser (hub org: only the hub repository; the eight unit orgs: all repositories, each holds one). Installation ids: flux 158816951, driftwood 158817106, feeds 158818023, ico 158818204, insurer 158818318, platform 158818695, nist 158818847, ludlow 158819003, tuppence 158819386. `token --org` minted and listed the reachable repository for flux and driftwood.
- **2026-09-03, step 4, decided differently from the ticket text (ADR-0025: decide and record).** Not `development`. That mode admits enactment pushes too, and the owner's instruction split the hands: the owner pushes, the assistant merges. So `twin/enact_guard.py` gains a third mode, `other-hand`, now checked in: every refusal of `operations` stands, and one shape is admitted, a disposition command that mints the app's token in the same command string, because that merge is attributed to `pavc-other-hand[bot]`. A bare merge is refused with a reason naming the mode; a merge-shaped MCP tool and every push to an enactment repository stay refused. Docstring carries the dated paragraph; four tests pin the behaviour and one pins the checked-in file.
- **2026-09-03, step 5 done.** The memory note on push and merge authorisation now names the app, the mode, the admitted command shape, and says never to flip to `development`.
- **2026-09-03, code review.** Standards axis: no hard violations; two smells fixed (a shared `_set_mode` test helper; a cross-reference comment tying the `token` subcommand name to the guard's pattern). Spec axis: one real hole, the token pattern matched anywhere in the command string, so `echo "twin/other_hand.py token"; gh pr merge 42` would have been admitted under the owner's token. Fixed: the guard now checks per shell segment that every disposing segment sets `GH_TOKEN` from the minter inline; four smuggling shapes are pinned red by test.

## Notes

Charted by ticket 75 (Q6, Q14). Blocks 87 and 74. The guard's own docstring already names this shape: "a credential that cannot merge" was the upgrade path; the owner chose the reverse for the development window, and the narrative still says a human merges. Ticket 95 records the theatre in NORTH-STAR §6.

## Answer

Resolved 2026-09-03. The second identity exists and has merged.

- **Identity:** GitHub App `pavc-other-hand`, App ID 4819564, owned by `@policy-as-versioned-flux`, installed on all nine estate orgs (installation ids in Progress). The owner chose the name in chat after rejecting two of the assistant's. Permissions: Contents read and write, Pull requests read and write, Metadata read. No webhook.
- **Credential:** private key at `~/.config/pavc-other-hand/app.pem`, mode 600, outside every repository. Fingerprint `SHA256:V5cL15DaLS+DBw504YaDho2c0YA+kKDKlz07qDAC9fA=`. Downloaded once through the owner's browser with the owner's approval in chat.
- **Verification:** `python -m twin.other_hand whoami` prints `pavc-other-hand`; `installations` lists nine; `token --org` reaches the one repository in each org tested.
- **Guard:** `twin/ENACT_MODE` is `other-hand` (a third mode, not `development`, because the owner pushes and the assistant merges; see Progress step 4 and the dated docstring paragraph). A merge is admitted only when the disposing shell segment sets `GH_TOKEN` inline from `twin.other_hand token`. Pushes to enactment repositories, merge-shaped MCP tools and bare merges stay refused.
- **Done criterion met:** https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/pull/2, authored by `chrisns`, reviewed `APPROVED` by `pavc-other-hand[bot]`, merged by `app/pavc-other-hand` as merge commit `c1c87fd`. The PR carried this ticket's own code, so the first merge by the other hand is the change that lets it merge.
- **Review:** standards axis clean with two smells fixed; spec axis found the per-command match hole, fixed before the merge (commit 77da842). Full suite 1546 passed, one standing red (invariant 43, the drift window, unrelated).

Consequences: ticket 87 is unblocked and applies the ruleset that requires this identity's review; ticket 74's definition of done can now be written; the memory note on merge authorisation is updated; NORTH-STAR §6 gets the theatre line from ticket 95.
