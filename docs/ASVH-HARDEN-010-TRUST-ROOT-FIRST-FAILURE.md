# ASVH-HARDEN-010 — Trust-Root First-Failure Matrix

Status: PRESERVED SEMANTIC FAILURE ANALYSIS — BEFORE TRUST-ROOT REMEDIATION

This matrix is derived from the frozen HR23–HR29 assertions and current reference implementation. It is not GitHub Actions evidence.

| Test | Candidate behaviour | Expected |
|---|---|---|
| HR23 | caller supplies verifier with always-true callback | FAIL |
| HR24 | caller supplies its own trusted-verifier set including `evil` | FAIL |
| HR25 | caller chooses both evidence context and verifier expected context | FAIL |
| HR26 | canonical digest is independent of record ordering | PASS |
| HR27 | status mutation changes canonical digest | PASS |
| HR28 | duplicate identical records are accepted if attested/digested | FAIL |
| HR29 | mismatched prior recovery context is rejected | PASS |

Expected matrix: 4 FAIL / 3 PASS.

## Preserved findings

- HC-H10-FR-016 — circular trust: recovery caller can inject the verifier that validates recovery.
- HC-H10-FR-017 — caller can redefine the trusted verifier set.
- HC-H10-FR-018 — caller can select the recovery trust domain/context.
- HC-H10-FR-019 — duplicate record injection is not rejected as malformed recovery history.

Existing controls already demonstrate deterministic order canonicalisation, semantic-status digest binding, and rejection of an evidence/verifier context mismatch.
