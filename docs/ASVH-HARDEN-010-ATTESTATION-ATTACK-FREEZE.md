# ASVH-HARDEN-010 — Recovery Attestation Attack Freeze

Status: FROZEN BEFORE ATTESTATION-BINDING REMEDIATION

## Proposition

A recovery-evidence declaration MUST NOT establish trusted recovery solely because caller-controlled booleans are true or authority identity strings match. Evidence must be bound to the exact recovered record set, an identified verifier and a recovery context/epoch, and that binding must itself be independently verifiable before it can contribute to ACTIVE standing.

## Frozen attacks

- HR17: caller self-asserts integrity/completeness/provenance flags.
- HR18: evidence is replayed after recovered records are mutated.
- HR19: evidence lacks verifier identity.
- HR20: evidence lacks an exact recovered-record digest/binding.
- HR21: evidence lacks recovery context/epoch binding.
- HR22: exact authority identity strings are forged; coverage equality alone is not source authentication.

## Failure condition

Any caller-constructed `RecoveryEvidence(True, True, True, ...)` that causes `recover()` to mark arbitrary structurally valid records trusted demonstrates the attestation gap.

## Claim boundary

This pass does not require or claim production PKI, HSM/TPM, KMS, certificate validation, transparency logs, distributed consensus or external timestamping. It asks only whether the reference boundary distinguishes a declaration of verification from verifiable evidence binding.
