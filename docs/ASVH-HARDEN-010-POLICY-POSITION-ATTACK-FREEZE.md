# ASVH-HARDEN-010 — Policy Position / Final-Bind Attack Freeze

Status: FROZEN BEFORE POLICY-POSITION REMEDIATION

## Proposition

Consequence-time trust-policy revalidation is only meaningful if the policy-position observation is itself authoritative, fresh, source-bound and context-bound, and if a successful observation cannot survive an adverse policy change before consequence formation.

## Frozen attacks

HR37–HR44 attack policy-position evidence: source identity, freshness, impossible age, same-revision equivocation, forged higher revision, unavailable authority, source substitution and observation-context binding.

HR45–HR48 attack the final bind: revocation after check, policy mutation after check, authority unavailability at final bind, and commit without a policy-position binding token/receipt.

## Failure condition

HARDEN-010 fails if an unverified/stale/substituted policy-position observation can satisfy current-policy revalidation, or if successful revalidation creates a durable commit grant that is not re-bound immediately before consequence formation.

## Claim boundary

These tests define reference-harness requirements. They do not demonstrate production source authentication, trusted time, atomic external policy read plus EPR commit, hardware-backed tokens, real NHS integration or production route non-bypassability.
