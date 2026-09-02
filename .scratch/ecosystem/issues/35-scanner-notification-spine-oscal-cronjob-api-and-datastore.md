# 35 — scanner, notification spine, OSCAL CronJob, api and datastore

Type: grilling (HITL)
Status: open
Blocked by: 16, 21, 33

## Question

Lift or retire trivy-operator, the Flux Alert/Provider/Receiver spine and the OSCAL CronJob on the adopter cluster; place api and datastore; sequence per-repo archiving.

## Notes

Graduated 2026-08-28 from ticket 13's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Comments

**2026-09-02, review.** Ordering from the review: composition prices exactly two feed names and reads no workload, image, SBOM or dependency, so lifting the apps (ticket 33) cannot make a feed re-price anything until the cve and eol converters exist. Ticket 84 item 1 carries the converters. Put 84 before or with 33, and restate 33's definition of done as a price check. Record: REVIEW-2026-09-02.md, legacy/L1 (refuted as stated, ordering survives).
