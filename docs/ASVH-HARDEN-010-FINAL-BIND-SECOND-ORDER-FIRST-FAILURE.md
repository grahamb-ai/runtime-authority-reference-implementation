# ASVH-HARDEN-010 — Final-Bind Second-Order First-Failure Matrix

Status: PRESERVED SEMANTIC FAILURE ANALYSIS — BEFORE SECOND-ORDER REMEDIATION

| Test | Current candidate behaviour | Expected |
|---|---|---|
| HR49 | prohibitive standing is rejected by verifier | PASS |
| HR50 | verifier exception escapes | FAIL |
| HR51 | policy reader exception escapes | FAIL |
| HR52 | arbitrary executor can ignore bind and return COMMITTED | FAIL |
| HR53 | bind omits policy source identity | FAIL |
| HR54 | bind omits attestation identity/digest | FAIL |
| HR55 | policy position has no attempt identity/nonce | FAIL |

Expected matrix: 6 FAIL / 1 PASS.

Preserved findings: HC-H10-FR-033 verifier exception fail-closed gap; HC-H10-FR-034 policy-reader exception fail-closed gap; HC-H10-FR-035 reference callback does not demonstrate bind enforcement; HC-H10-FR-036 source omitted from bind; HC-H10-FR-037 attestation omitted from bind; HC-H10-FR-038 cross-attempt replay ambiguity.
