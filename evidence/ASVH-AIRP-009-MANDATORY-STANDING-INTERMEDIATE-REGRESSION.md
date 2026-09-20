# AIRP-009 — Mandatory Standing Intermediate Regression

**Run:** 35499553798  
**Status:** PRESERVED INTERMEDIATE REGRESSION

After making consequence-time standing mandatory at the protected commit path, the existing H11 second-order restart positive-control path failed because its legacy fixture constructed an ExecutionGateway without the newly required standing reader.

Observed result:
- second-order job: 1 failed, 5 passed;
- failing test: `test_h11_so04_restart_must_not_resurrect_consumed_capability`;
- expected legacy positive control: COMMITTED;
- observed under strengthened contract: BLOCKED.

This does not establish failure of the restart/single-use property. The positive-control fixture no longer satisfies the strengthened gateway precondition.

AIRP-009 did not execute in this run because the workflow dependency stopped after the earlier regression.

## Required alignment

Update legitimate H11 positive-control fixtures to provide exact typed ACTIVE current standing. Do not weaken the mandatory standing requirement and do not alter the frozen AIRP-009 acceptance conditions.
