# ASVH-HARDEN-010 — Trust-Policy Lifecycle Attack Freeze

Status: FROZEN BEFORE TRUST-POLICY LIFECYCLE REMEDIATION

## Proposition

A recovery trust policy is itself an authority dependency. A policy that was once valid MUST NOT remain sufficient merely because an old policy object can still validate old evidence. Recovery and consequence formation must depend on the policy's present standing, monotonic policy position, current trusted-verifier set, current required-authority set, and binding between evidence and the policy under which it was verified.

## Frozen attacks

- HR30: trust policy lacks monotonic policy revision/epoch.
- HR31: an older once-valid policy/context is replayed after a newer policy exists.
- HR32: a verifier withdrawn by current policy remains usable through an old policy object.
- HR33: old authority-set policy silently drops a dependency required by current policy.
- HR34: policy has no explicit present standing/revocation state.
- HR35: recovery evidence is not bound to the exact trust policy under which verification occurred.
- HR36: successful recovery creates durable `recovery_trusted` state that can outlive a subsequent trust-policy change before consequence formation.

## Failure condition

If historical policy material can independently establish or preserve trusted recovery without re-establishing current trust-policy standing, HARDEN-010 fails this pass.

## Claim boundary

This is a reference-model lifecycle requirement. It does not claim a production policy distribution system, external policy authority, key revocation service, certificate infrastructure, consensus, durable configuration store, NHS deployment, or atomic EPR commit.
