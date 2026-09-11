# ASVH-HARDEN-003 — Consequence Evidence & Reconciliation

Status: FROZEN v1.0

## Purpose
HARDEN-003 tests whether the reference harness can distinguish a protected execution attempt from evidence that the governed consequence formed, was prevented, or remains indeterminate.

It extends HARDEN-001 exact-consequence binding and HARDEN-002 present-standing continuity. It does not claim production EPR transaction atomicity or real NHS consequence observability.

## Core rule
Authority Receipt != Consequence Evidence.
Executor success return != independently established consequence.
Transport failure/timeout != proof of prevention.

## Consequence states
- FORMED — target simulator contains the exact commit under the stable consequence identity.
- PREVENTED — target simulator can authoritatively establish that the governed consequence did not form.
- INDETERMINATE — available evidence cannot yet establish either FORMED or PREVENTED.

## Stable identity
Every protected execution uses a consequence_key derived from the exact clinical commit identity. Retries for the same protected consequence must use the same key and must not create duplicate consequences.

## Reconciliation
If execution acknowledgement is lost, the harness must query the authoritative target simulator by consequence_key before making a final consequence claim.

## Invariants
HC3-I01 Receipt does not prove consequence.
HC3-I02 A timeout is never mapped directly to PREVENTED.
HC3-I03 Stable consequence identity survives retry.
HC3-I04 Duplicate retry cannot create a second governed consequence.
HC3-I05 Authoritative read-back may resolve INDETERMINATE to FORMED.
HC3-I06 If target absence is authoritative within the simulator boundary, reconciliation may resolve to PREVENTED.
HC3-I07 Conflicting consequence evidence remains INDETERMINATE.
HC3-I08 Consequence evidence binds bind_id, receipt_id, exact commit hash and target record.
HC3-I09 Evidence provenance level is explicit.
HC3-I10 Executor crash after target formation must not be reported as PREVENTED.

## Permitted claim after PASS
Within the ASVH reference-harness boundary, consequence evidence is represented separately from authority determination and protected execution. Lost acknowledgement, timeout and retry are reconciled against the target simulator using a stable consequence identity; duplicate retries do not create a second simulated governed consequence; unresolved states remain INDETERMINATE rather than being misclassified as prevented.

## Non-claims
No claim is made about production EPR idempotency, external transaction atomicity, real NHS target audit integrity, real distributed reconciliation, or production-grade consequence provenance.
