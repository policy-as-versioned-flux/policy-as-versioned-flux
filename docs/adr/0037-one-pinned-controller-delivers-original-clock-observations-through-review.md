---
status: accepted
---

# One pinned controller delivers original clock observations through review

Decided 2026-10-17 by the assistant, delegated under ADR-0025. This extends ADR-0024's
October 5 delivery amendment to the six adopter observation clocks and preserves ADR-0031's
separation between read-only twin execution and the inline producer writer.

Required review protects each adopter's main, while all six producer workflows still sign an
observation and push main directly. Their October 16 runs signed genuine observation-only
commits and received GH013. Removing required review or granting bypass would discard the
second identity. Copying the hub reviewer six times would distribute the same authority bugs.

The hub and the six adopter clocks therefore share one deep delivery module. Its closed profiles
bind the repository, workflow, author/committer, subject, event and observation paths. Adopter
samplers append three source-fact rows, one served-workload row and one OSCAL row; the two twin
sweep formats each append one row. The controller verifies exact historical prefix bytes and
source/run attribution, regular lane-only Git blobs, the original gitsign object and certificate
claims, official completed run/attempt facts, the proposing clock identity and a stable PR head.
It reads pending Git objects as data, executes none of their code and consumes no run artifact.
It conserves measurements without changing prices, grades, policy or instrument declarations.

A producer publishes its original signed object to `observations/{clock}/{run_id}-{attempt}`
before integration. Existing-ref checks plus an explicitly empty ref lease prevent updates to
any existing ref, including an ancestor created during push advertisement. An identical existing
ref is also refused by the precheck; Git can otherwise call it up to date without updating it.
The producer opens a PR and reports pending. It never reviews, merges, rebases or force-updates a
pending original. A conflict preserves the durable original for separate reviewed integration.

Adopters pin a deterministic bundle by full hub commit and SHA256, independently of their twin,
composition and policy pins. The bundle contains the one controller and exact existing App mint
helper and enact-mode validator, with a source hash manifest. Its thin workflow callers install
pinned dependencies, check out only their trusted default branch, and complete a read-only
preflight before the App-key step. They use a default-branch-restricted environment. The existing
App identity must match both bot login and numeric user ID. It mints a token for only the caller
repository with contents/PR write; Actions facts use a separate read-only token. There is no new
identity, grant, main-rule exception or bypass. The App private key itself remains the existing
multi-installation authority; narrowing the issued token does not narrow that private key.

Adopters have no local enact-mode record. The immutable controller fetches current hub main as
**data only**, copies regular mode/acknowledgement/cited-prose blobs into a disposable data tree,
and applies the bundled validator. This keeps the owner's existing development mode and expiry;
a code pin freezes implementation, never permission. Both the adopter default tip and hub mode
authority tip are re-read immediately before each approval and merge. A changed tip or an
expired/invalid owner record leaves delivery pending for a fresh trusted invocation. Neither an
adopter file nor an environment override can replace hub authority. No freshly fetched hub code
executes with the key or token.

During a valid development window, the separate App approves the exact original head and uses an
ordinary merge commit. The original remains an unchanged ancestor; squash and rebase would erase
that proof and are excluded. Recorded is reported only when the original object is an ancestor
of published main and the exact appended bytes remain there once. The previously strict missing
observation checks remain strict while delivery is pending, and a delivered red measurement
remains red. Local synthetic signer/API fixtures prove transport and conservation, not live
GitHub permissions or genuine signature issuance; those require the actual clock/reviewer run.
