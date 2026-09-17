# ASVH-HARDEN-010 — Recovery Record Attack Freeze

Status: FROZEN BEFORE RECOVERY-INTEGRITY REMEDIATION

## Proposition

A recovered authority record set MUST NOT become trusted merely because its individual records are structurally plausible. Recovery must establish integrity, completeness and provenance sufficient for the declared authority dependency basis.

## Frozen hostile cases

- HR11: empty recovery record set must not be trusted.
- HR12: recovery missing a required dependency must not allow later positive observations to manufacture a complete trusted basis.
- HR13: same source/subject/revision with contradictory status makes recovery untrusted.
- HR14: malformed negative revision makes recovery untrusted.
- HR15: a forged/arbitrary higher positive revision is not self-authenticating merely because it is monotonic.
- HR16: an incomplete history that omits a newer revocation must not be trusted solely from an older positive record.

## Failure condition

The candidate fails this pass if `recover(records)` marks recovery trusted without independent integrity/completeness/provenance evidence and that trust can contribute to ACTIVE consequence-time standing.

## Claim boundary

These tests define reference-model requirements. They do not claim a production durable store, cryptographic signing service, TPM/HSM protection, external timestamp authority, consensus, crash consistency, or NHS/EPR integration.
