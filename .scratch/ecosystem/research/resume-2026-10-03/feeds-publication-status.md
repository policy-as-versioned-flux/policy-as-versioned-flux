# Feeds publication checkpoint — 2026-10-03

Superseded by `feeds-merge-status.md`: root's independent public-data review resolved the push rejection, the source branch was pushed and PR10 was created and approved by pavc-other-hand. The current blocker is the separately recorded automatic merge approval rejection.

Local branch: `resume/2026-10-03-primary-cve-fx-threat-feeds`, based on current remote main `ff3ac9ab00bdc73e1bbf83cabf91c767d35b8e88`. Ordinary-config source commit: `37dfe4a2de50f1a1fd7aeb6348d819373188e0e6`. Working tree clean; final corrections mirrored into `.estate-clone/feeds`.

Both real offline release gates pass against their exact platform v2.0.1 ruler. Exact primary CVE/HMRC rebuilds, dated EPSS replay, release bumps, nine frozen major payload comparisons, model-credential negative probe and high-confidence secret scan pass. Public GitHub metadata confirms the destination is public and the account has admin/push permissions.

Proposed cuts after independent review/merge: `cve/v3.0.0`, `fx/v1.1.0`, `threat-register/v4.0.0`. Cut workflows require a subsequent release.yml dispatch because their default Actions token does not trigger the release push event.

**Publication blocked:** automatic approval review rejected this agent's branch push before execution. It stated that trusted user content did not specifically authorize exporting this 19-path payload to this public destination and could not independently verify its sensitivity. This agent performed no push, draft PR, merge or tag cut. The rejection forbids workaround or indirect execution; root must resolve the explicit destination/payload approval condition.

The exact PR body, full source patch, hashes and validation logs are retained beside this file and in the resume patch directory.
