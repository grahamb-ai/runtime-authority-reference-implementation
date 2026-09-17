# ASVH-HARDEN-010 — Trust-Policy Lifecycle First-Failure Matrix

Status: PRESERVED SEMANTIC FAILURE ANALYSIS — BEFORE POLICY-CONTINUITY REMEDIATION

This matrix is derived from frozen HR30–HR36 and the current reference implementation. It is not GitHub Actions evidence.

| Test | Candidate behaviour | Expected |
|---|---|---|
| HR30 | `RecoveryTrustPolicy` has no monotonic policy revision/epoch | FAIL |
| HR31 | an old policy object and matching old evidence can establish trusted recovery | FAIL |
| HR32 | an old policy object can continue trusting a verifier later withdrawn elsewhere | FAIL |
| HR33 | an old policy requiring only a reduced authority set can establish trusted recovery | FAIL |
| HR34 | trust policy has no explicit present standing/revocation state | FAIL |
| HR35 | recovery evidence is not bound to an exact trust-policy digest | FAIL |
| HR36 | successful recovery persists as `recovery_trusted=True` without consequence-time policy revalidation | FAIL |

Expected matrix: 7 FAIL / 0 PASS.

## Preserved findings

- HC-H10-FR-020 — trust-policy rollback is not detectable.
- HC-H10-FR-021 — withdrawn verifier can remain effective through historical policy material.
- HC-H10-FR-022 — required-authority-set downgrade can silently reduce recovery dependencies.
- HC-H10-FR-023 — trust-policy present standing is not represented.
- HC-H10-FR-024 — recovery evidence is not bound to the policy that authorised verification.
- HC-H10-FR-025 — recovered trust can outlive the policy basis that created it.
