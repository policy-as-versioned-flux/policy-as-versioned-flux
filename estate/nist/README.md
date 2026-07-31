# policy-as-versioned-nist

**Regulator (real).** Publishes the genuine NIST 800-53 OSCAL controls catalog
as a versioned, signed, machine-readable artifact that institutions pin as an
upstream dependency. A regulatory change propagates down the graph as a
dependency bump PR. Controls-as-code, already real today.

Consumed by: `platform` (OSCAL/c2p plumbing) → institutions. *(ticket 04)*
