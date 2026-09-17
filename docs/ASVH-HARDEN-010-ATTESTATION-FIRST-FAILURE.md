# ASVH-HARDEN-010 — Attestation First-Failure Matrix

Status: PRESERVED SEMANTIC FAILURE ANALYSIS — BEFORE ATTESTATION-VERIFIER REMEDIATION

The matrix is derived from the frozen HR17–HR22 assertions and the candidate implementation. It is not GitHub Actions evidence.

| Test | Candidate behaviour | Expected |
|---|---|---|
| HR17 | caller-created `RecoveryEvidence(True, True, True, coverage)` is accepted | FAIL |
| HR18 | evidence is not bound to record content/revision, so mutated records are accepted | FAIL |
| HR19 | `RecoveryEvidence` has no verifier identity | FAIL |
| HR20 | `RecoveryEvidence` has no exact record-set digest | FAIL |
| HR21 | `RecoveryEvidence` has no recovery context/epoch | FAIL |
| HR22 | exact source strings plus self-asserted evidence can establish trust | FAIL |

Expected matrix: 6 FAIL / 0 PASS.

## Preserved findings

- HC-H10-FR-011 — verification flags are caller assertions, not independently verified evidence.
- HC-H10-FR-012 — attestation is not bound to exact recovered bytes/semantic record set.
- HC-H10-FR-013 — verifier identity is absent.
- HC-H10-FR-014 — recovery context/epoch is absent, enabling cross-recovery replay in the model.
- HC-H10-FR-015 — authority identity equality is not source authentication.

No remediation should rewrite the historical frozen tests or this expected first-failure record.
