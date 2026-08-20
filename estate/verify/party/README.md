# verify/party — the roles: declaration, machine-checked

*(ticket 16; blocked-by 03 organisation glossary)*

`CONTEXT.md`'s *Role* section names three composable roles — **publisher**,
**risk-bearer**, **adopter** — and ticket 03 flagged that a `roles:` field
nothing validates would be the estate's fourth assertion that cannot fail.
`roles.json` declares each party's roles; `party.py` refuses any declaration
the filesystem does not back up.

| role | filesystem evidence |
|---|---|
| `risk-bearer` | an entry in [`../../platform/risk/appetite.json`](../../platform/risk/appetite.json) |
| `publisher` | a `*.sig` file, or a recorded `*VERSION*.json`, under the party's own directory |
| `adopter` | a reference — repo naming (`policy-as-versioned-<other>`) or in-repo path (`estate/<other>/`) — to another party, under the party's own directory |

**Institutions are derived, not hard-coded**: risk-bearer + adopter, but *not*
publisher. `platform` is also risk-bearer + adopter (it prices its own risk —
see `../../platform/honesty/reflexive.py`), but that third role, `publisher`,
is exactly what keeps it off the institution count. Ticket 16 part 2 merged
platform's separate strict £10k appetite band into the shared
`platform/risk/appetite.json` (marked `root_of_trust`); this derivation is
what keeps that merge from silently turning "three institutions" into four.

## Run it

```sh
python3 party.py check       # refuse (non-zero) any role the filesystem contradicts
./verify-party.sh            # + proves the guard bites: plants each violation, watches it fail
```

Exits non-zero if the beat would fail on stage.
