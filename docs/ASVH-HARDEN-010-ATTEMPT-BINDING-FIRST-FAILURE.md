# ASVH HARDEN-010 — Execution-Attempt Binding First-Failure

## Status

FAILURE PRESERVED — REMEDIATION NOT YET APPLIED

## Hostile proposition

A non-empty `attempt_id` must not be treated as sufficient evidence that a policy position belongs to the current consequence-forming execution attempt.

Where the verifier has no expected execution-attempt identity configured, an arbitrary non-empty attempt identity must not be accepted merely because it is present.

## Executable observation

Local probe on the HARDEN-010 remediation candidate produced:

```text
verifier expected_attempt_id = ''
position attempt_id = 'attacker-attempt'
verifier accepts = True
```

The position therefore satisfies the current presence check while remaining unbound to an independently expected execution-attempt identity.

## Finding

### HC-H10-FR-042 — Non-empty attempt identity can substitute for exact attempt binding

`PolicyPositionVerifier.verify()` currently rejects an empty position `attempt_id`, but only compares the position attempt to an expected attempt when `expected_attempt_id` is itself configured.

Consequently, a verifier with an empty expected-attempt configuration can accept an arbitrary non-empty position attempt identity. Presence is therefore not equivalent to binding.

## Security significance

HARDEN-010 requires consequence-time authority evidence to be bound to the execution attempt for which the consequence is being formed. An arbitrary non-empty identifier does not establish that relationship.

This leaves a cross-attempt ambiguity at the reference-model verification boundary whenever the verifier is instantiated without an expected attempt identity.

## Remediation constraint

Do not remediate by removing attempt identity, accepting a default identifier, or weakening the hostile proposition. The verification path must fail closed when an expected execution-attempt identity is absent at a boundary that requires attempt binding, and must require exact equality between the observed and expected attempt identities.

Before changing generic verifier semantics, inspect all `PolicyPositionVerifier` construction sites to determine whether the type is used outside consequence-time final binding and avoid accidentally breaking an earlier recovery/lifecycle contract.

## Evidence scope

This is local executable evidence on the reported Windows / Python 3.13.7 / pytest 9.1.1 environment. It is not GitHub Actions/CI evidence and does not establish a production EPR exploit.
