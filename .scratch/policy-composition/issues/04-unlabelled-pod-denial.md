# 04 — Whether an unlabelled pod is denied

Type: grilling
Status: open
Blocked by: none

Graduated from the map's Not yet specified: "Whether an unlabelled pod is denied." `CONTEXT.md:129`
says the orphan guard denies a pod with a *missing* label. The committed guard's `matchConditions`
skip unlabelled pods entirely, and nothing else denies them. One of the two is wrong.

## Question

Should an unlabelled pod be denied by the orphan guard? Decide which side is correct, `CONTEXT.md`'s
description or the committed guard's behaviour, and what must change to bring the other into line.
