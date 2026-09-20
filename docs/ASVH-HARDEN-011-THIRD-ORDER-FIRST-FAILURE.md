# ASVH HARDEN-011 — Third-Order First-Failure Record

Status: OPEN / RED
Run: 35494859318

Preceding verification remained green in the same workflow dependency chain:
- HARDEN-010 frozen baseline: 225 passed.
- HARDEN-011 route closure: 10 passed.
- HARDEN-011 second order: 6 passed.

Third-order result: 3 passed / 2 failed.

Preserved failures:
- TO01 storage snapshot rollback: restoring the execution-authority SQLite database to a pre-consumption snapshot resurrected a consumed capability and returned COMMITTED.
- TO03 executor-secret substitution: an executor configured with a wrong secret could generate a proof that its own verifier accepted, returning COMMITTED.

Findings:
1. Durable local storage is not rollback-resistant when the entire authority store is inside the rollback domain.
2. Self-verification of executor credentials is not an independent identity trust boundary.

Claim boundary: Python reference-model evidence only; no claim about a deployed NHS EPR.

Remediation targets:
- an independent monotonic consumption anchor outside the execution-authority DB rollback domain;
- an independently configured executor identity registry/verifier, separate from the caller/executor secret.
