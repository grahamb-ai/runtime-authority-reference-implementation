# ASVH-HARDEN-010 — Trust-Root Attack Freeze

Status: FROZEN BEFORE TRUST-ROOT REMEDIATION

## Proposition

A verifier supplied by the same caller asking for recovery MUST NOT be able to manufacture the trust root by choosing its own trusted verifier identities, recovery context, or verification function. Trust configuration must be anchored outside the untrusted recovery request.

## Frozen attacks

- HR23: caller injects an always-true attestation verifier.
- HR24: caller replaces the trusted-verifier set with an attacker-controlled identity.
- HR25: caller chooses both evidence context and expected context.
- HR26: equivalent record-set ordering must canonicalise to the same digest.
- HR27: semantic status mutation must alter the digest.
- HR28: duplicate record injection must not become a distinct trusted history merely because its digest verifies.
- HR29: otherwise valid evidence from a previous recovery epoch/context must not replay into the current one.

## Failure condition

If the recovery caller can construct both the evidence and the verifier/configuration required to accept that evidence, the reference boundary has circular trust and fails this pass.

## Claim boundary

This pass does not require a particular production trust technology. It requires only an architectural separation between untrusted recovery input and preconfigured/trusted verification policy. PKI, KMS, HSM, TPM, certificate lifecycle, transparency logs and production key custody remain outside the demonstrated boundary.
