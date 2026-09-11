# ASVH-HARDEN-004 — Hostile Review & Remediation Record

Status: REMEDIATED IN REFERENCE HARNESS — bounded verification only

## Baseline chronology

1. The HARDEN-004 specification and H4-001..H4-020 conformance vectors were frozen before hostile review.
2. BASELINE-004 passed H4-001..H4-020 and retained green regressions for HARDEN-001, HARDEN-002 and HARDEN-003.
3. A separate hostile test file was then introduced. It did not replace or rewrite the frozen CTS.
4. The first hostile run failed 4/4 tests. These failures are preserved in workflow run 34608368645 at commit `f42784b9724c2a5ffd008df3c9c5f448cff120ca`.
5. Remediation was applied in commit `010f2f0ff996024931790746416a8c0d5edc74c5`.
6. The full regression + frozen HARDEN-004 CTS + hostile review then passed in workflow run 34608454543.

## Preserved hostile findings

### HC-H4-FR-001 — Future observation timestamp accepted as current evidence

Severity: HIGH

Observed result before remediation: `VALID` / `ALLOW` for evidence whose `observed_at` was ten minutes ahead of the harness trusted clock.

Root cause: freshness logic only rejected evidence older than `max_age_seconds`; a future observation produced a negative age and therefore bypassed the stale check.

Remediation: `observed_at > trusted_now` is explicitly `INVALID` within the reference harness.

### HC-H4-FR-002 — Malformed temporal evidence escaped as an exception

Severity: HIGH

Observed result before remediation: malformed `observed_at` caused `ValueError` to escape the evaluator rather than producing an explicit evidence status.

Root cause: ISO timestamp parsing was not converted into evidence failure semantics.

Remediation: malformed or non-comparable temporal values resolve to `INVALID` rather than crashing the evaluator.

### HC-H4-FR-003 — Evidence identity collision accepted as valid

Severity: HIGH

Observed result before remediation: two different evidence payloads carrying the same `evidence_id` were accepted as `VALID` because their asserted states were the same.

Root cause: evidence identity was recorded but uniqueness/identity consistency was not enforced inside one evaluation.

Remediation: one `evidence_id` may denote only one payload within an evaluation. Reuse of an ID with materially different payload produces `INVALID`.

### HC-H4-FR-004 — Exact duplicate evidence counted more than once

Severity: MEDIUM

Observed result before remediation: an identical repeated evidence item appeared twice in the evaluation evidence identifiers.

Root cause: transport-level duplicate delivery was not de-duplicated.

Remediation: exact duplicate items with the same stable evidence identity and identical payload are de-duplicated before evaluation and receipt reconstruction.

## Re-verification result

Commit: `010f2f0ff996024931790746416a8c0d5edc74c5`

Workflow run: `34608454543`

Result:

- HARDEN-001 regression — PASS
- HARDEN-002 regression — PASS
- HARDEN-003 regression — PASS
- frozen HARDEN-004 H4-001..H4-020 CTS — PASS
- HARDEN-004 hostile review — PASS

## Current bounded claim

Within the ASVH reference-harness boundary, a contracted runtime fact is not treated as valid solely because a value is present. The evidence evaluator applies permitted-source checks, subject/deployment/product-version binding, explicit temporal semantics, provenance presence, integrity status, revocation state, contradiction handling and stable evidence identity. Future-dated or malformed temporal evidence is invalid, conflicting reuse of an evidence identity is invalid, and exact duplicate delivery is de-duplicated rather than counted as independent authority evidence.

## Non-claims

This remediation does not establish:

- factual truth of an external evidence assertion;
- real NHS authoritative-source integration;
- production PKI, KMS, HSM or source identity assurance;
- cryptographic authenticity of provenance references;
- organisational AI readiness;
- clinical competence;
- clinical safety or effectiveness;
- regulatory compliance;
- production distributed-time guarantees;
- real-world EPR non-bypassability.

## Remaining hostile-review boundary

The following remain later-stage concerns rather than demonstrated properties of HARDEN-004:

- authorisation and lifecycle control of ControlContract versions themselves;
- production source identity and credential compromise;
- authoritative source quorum/precedence models where multiple independent authorities are intentionally permitted;
- cryptographic verification of external provenance artefacts;
- cross-system evidence retrieval outage and recovery semantics beyond the bounded evaluator.
