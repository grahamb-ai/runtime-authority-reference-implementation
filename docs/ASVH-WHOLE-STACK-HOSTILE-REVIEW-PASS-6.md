# ASVH Whole-Stack Hostile Review — Pass 6

## Scope

Pass 6 attacked whether the whole-stack execution coordinator actually composed the Protected Clinical Bind guarantees already demonstrated by HARDEN-001, rather than merely checking the bind's visible fields.

## Preserved hostile failure

Workflow run `34615747863` preserved the pre-remediation result.

HARDEN-001 through HARDEN-009 and whole-stack passes 1–5 remained green. Pass 6 failed 4 of 5 frozen attacks; the valid unused SINGLE_USE bind positive control passed.

Observed failures showed that simulated consequence formation could occur with:

- a forged Protected Clinical Bind integrity reference;
- a bind whose use semantics had been changed to `MULTI_USE`;
- sequential reuse of the same exact bind through the same coordinator; and
- concurrent reuse of the same exact bind, where both executions returned `FORMED`.

## Finding

**WS-FR-006 — Whole-stack execution bypassed Protected Clinical Bind integrity and single-use semantics.**

HARDEN-001 already provided bind integrity verification and single-use execution semantics in its protected executor, but those properties had not been composed into the whole-stack coordinator. Field-level exact-consequence and temporal checks alone were therefore insufficient.

## Remediation

Commit `4adfe84732a6bad36b0f8ae85362499e2bcb934c` added the HARDEN-001 bind-integrity verification to the normal whole-stack ALLOW path and introduced an atomic coordinator-instance claim over each `bind_id` before deployment enforcement.

The ALLOW path now requires:

- an integrity-valid Protected Clinical Bind;
- `SINGLE_USE` semantics; and
- successful first claim of the bind identifier within the coordinator instance.

The claim happens before deployment enforcement. This is deliberately conservative inside the reference harness: if a later downstream check prevents execution, the claimed bind remains burned rather than becoming silently reusable.

## Re-verification

Workflow run `34615947705` completed successfully.

Result:

- HARDEN-001 through HARDEN-009: PASS
- WS-001 through WS-016: PASS
- WS2-001 through WS2-008: PASS
- WS3-001 through WS3-011: PASS
- WS4-001 through WS4-011: PASS
- WS5-001 through WS5-009: PASS
- WS6-001 through WS6-005: PASS

## Bounded conclusion

Within a single declared ASVH reference-harness coordinator instance, the normal ALLOW path requires an integrity-valid `SINGLE_USE` Protected Clinical Bind and atomically claims that bind identifier before deployment enforcement, preventing sequential or concurrent replay through that coordinator instance.

## Explicit non-claims

The replay fence introduced by Pass 6 is in-memory and coordinator-instance local. It is not durable across process restart, is not shared between separate coordinator instances, and does not establish distributed single-use, production transaction atomicity, production cryptographic key management, or real EPR non-bypassability. Those remain separate properties requiring further evidence.
