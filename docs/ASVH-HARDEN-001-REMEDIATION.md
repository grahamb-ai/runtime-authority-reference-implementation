# ASVH-HARDEN-001 — Hostile Review Remediation Record

## HC-H1-FR-001 — Fabricated persisted bind accepted

**Original status:** CRITICAL / OPEN  
**Current status:** REMEDIATED IN REFERENCE HARNESS / RE-VERIFIED  
**Boundary:** ASVH-HARDEN-001 reference-harness boundary only

## Original hostile finding

The original frozen H1-014 test proved only that an unknown bind identifier was rejected. A stronger hostile test inserted a structurally valid `ProtectedClinicalBind` directly into the durable bind store using:

- a fabricated bind identifier;
- a fabricated Authority Receipt identifier;
- the correct Exact Clinical Commit binding hash;
- otherwise internally consistent metadata.

The pre-remediation Protected Executor accepted that record and returned `EXECUTED`. The simulated EPR consequence formed.

This failure is preserved in GitHub Actions run **34604659841**, where the hostile review result was **2 passed, 1 failed** and the failed test was `test_hostile_h1_014_fabricated_persisted_bind_is_rejected`.

The historical failure is not rewritten or reclassified.

## Root cause

The Protected Executor established only:

1. that the bind record existed in the store;
2. that the state was executable;
3. that the bind had not expired;
4. that materiality and canonicalisation profiles matched; and
5. that the Exact Clinical Commit binding hash matched.

It did **not** establish that the bind record had actually been issued by the reference Runtime Authority path or that its immutable contents had not been fabricated or altered after issuance.

Therefore persistence was incorrectly treated as provenance.

## Remediation

The reference harness now adds a versioned authenticated integrity envelope to every issued `ProtectedClinicalBind`.

Profile:

`PCB-HMAC-SHA256-1`

For the reference harness, the integrity reference is an HMAC-SHA256 over the canonical representation of all immutable bind fields except the integrity value itself.

The Protected Executor validates this integrity reference **before** treating a persisted bind record as execution authority.

An unsigned, fabricated or post-issuance modified bind now produces:

`BIND_INTEGRITY_FAILURE`

and no EPR simulator consequence may form.

## Additional hostile challenge

The hostile review was extended with a second integrity challenge:

- create a legitimately issued and authenticated bind;
- modify its `authority_receipt_id` after issuance while preserving the original integrity reference;
- persist the altered object;
- attempt execution.

Expected result: `BIND_INTEGRITY_FAILURE`; simulated EPR consequence count remains zero.

## Verification result

Remediation verification was performed on branch `asvh-harden-001-baseline` at commit:

`04664320cbfc3b89f928ba4c85c1e7195b095759`

GitHub Actions run:

`34605507834`

Results:

- frozen H1-001 through H1-020 conformance suite: **PASS**;
- hostile stronger concurrency test: **PASS**;
- hostile fabricated persisted-bind test: **PASS**;
- hostile signed-bind tamper test: **PASS**;
- hostile document-payload binding test: **PASS**;
- overall workflow: **SUCCESS**.

## Claim permitted after remediation

Within the ASVH-HARDEN-001 reference-harness boundary, a persisted Protected Clinical Bind is not accepted as execution authority solely because it exists in the bind store. The executor requires a valid reference-harness integrity envelope and rejects unsigned or altered bind records before the simulated EPR consequence is formed.

## Explicit non-claims

This remediation does **not** demonstrate:

- production cryptographic key management;
- HSM/KMS-backed signing;
- asymmetric trust between independent organisations;
- compromise resistance where the signing key itself is exposed;
- production EPR non-bypassability;
- production-grade certificate or secret rotation;
- independent third-party verification of bind issuance;
- production deployment security.

The HMAC key used in HARDEN-001 is explicitly a reference-harness key and must not be represented as a production key-management design.
