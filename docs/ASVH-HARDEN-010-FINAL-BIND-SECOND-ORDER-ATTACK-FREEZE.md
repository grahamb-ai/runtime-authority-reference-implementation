# ASVH-HARDEN-010 — Final-Bind Second-Order Attack Freeze

Status: FROZEN BEFORE SECOND-ORDER REMEDIATION

The first final-bind remediation must itself be attacked.

## Frozen attacks

- HR49: same revision/digest but prohibitive standing at final bind.
- HR50: attestation verifier throws rather than returns false.
- HR51: policy-position reader throws/unavailable.
- HR52: executor receives the bind but ignores it; reference API alone does not prove enforcement.
- HR53: consequence binding omits policy source identity.
- HR54: consequence binding omits identity/digest of the verified policy-position attestation.
- HR55: policy observation has no attempt/nonce identity, leaving replay/cross-attempt ambiguity.

## Boundary

HR52 is intentionally architectural: passing a bind object to an arbitrary callback does not demonstrate that a real consequence path is non-bypassable or that the executor enforces the bind. Any remediation must keep that production non-claim explicit.
