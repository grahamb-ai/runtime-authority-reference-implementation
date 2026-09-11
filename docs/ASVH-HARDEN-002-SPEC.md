# ASVH-HARDEN-002 — Authority Continuity / Present Standing

Status: FROZEN v1.0

## Purpose

Extend the ASVH reference harness beyond one-time ALLOW plus exact-consequence binding. HARDEN-002 tests whether authority remains usable through the protected Consequence Formation Interval when relevant state may change after the original determination.

## Core proposition

A prior ALLOW and a valid ProtectedClinicalBind are insufficient if a control classified as PRESENT_AT_EXECUTION or CONTINUOUS is no longer in standing when the governed consequence is about to form.

## Non-claims

HARDEN-002 does not demonstrate production distributed consensus, external EPR atomicity, live NHS authoritative-source integration, production trusted-time infrastructure, organisational governance quality, or universal current-state truth.

## Continuity classes

- SNAPSHOT — evidence may be evaluated at determination and remain valid if bound to the unchanged exact consequence.
- PRESENT_AT_EXECUTION — current standing must be established immediately before consequence formation.
- CONTINUOUS — the material state must remain consistent through the protected interval; any detected change invalidates outstanding authority.

## Reference present-standing state

The harness uses a versioned authoritative state snapshot with:

- source_id
- state_epoch
- sequence
- observed_at
- product_authorised
- workflow_valid
- monitoring_clear
- policy_version
- available

The pair `(state_epoch, sequence)` is monotonic within the declared reference boundary.

## High-watermark rule

The executor maintains the highest accepted state position. A state snapshot behind the accepted high-watermark must never restore execution authority after restart, rollback or failover.

## Trusted-time rule

Bind expiry and state freshness are evaluated only against the harness-owned trusted clock abstraction. Caller timestamps do not extend authority.

## Execution sequence

1. Verify bind integrity.
2. Verify bind is ISSUED and unexpired.
3. Recompute exact clinical commit binding.
4. Read present standing from the authoritative state provider.
5. Reject unavailable or invalid standing.
6. Reject state behind the accepted high-watermark.
7. Atomically claim the bind.
8. Re-read present standing immediately before consequence formation.
9. Require no adverse standing change and no high-watermark regression.
10. Re-check bind expiry using trusted time.
11. Form the simulated EPR consequence or prevent it.
12. Preserve resulting bind state and continuity evidence.

## Executor outcomes

- EXECUTED
- PRESENT_STANDING_UNAVAILABLE
- PRESENT_STANDING_INVALID
- PRESENT_STANDING_CHANGED
- STATE_ROLLBACK_DETECTED
- BIND_EXPIRED
- BINDING_MISMATCH
- BIND_INTEGRITY_FAILURE
- BIND_ALREADY_USED
- ATOMIC_CLAIM_FAILED
- EXECUTION_INDETERMINATE

## Binding rule

The exact clinical commit remains governed by HARDEN-001. HARDEN-002 adds runtime state continuity; it does not weaken exact-consequence binding.

## Failure preservation

Any hostile failure discovered during HARDEN-002 must be preserved before remediation. A later passing run does not replace the original evidence.
