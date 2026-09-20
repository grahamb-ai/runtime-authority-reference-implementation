# ASVH-AIRP-008 — Direct Enforcement First Failure

**Result:** FAIL / RED  
**Run:** 35497730694  
**Job:** airp-008-direct-enforcement  
**Execution commit:** 4bb0ea29e203f30beb442bc0ebd360363bcb4819  
**Frozen test:** 5aaac462ec2f4cae80f8b9de4562f9769f76e1a1  
**Frozen specification:** d712ad40e2a8a739a8b1b0a807c25282810816cd

## Exact observed failure

The frozen challenge produced:

`AssertionError: ENFORCEMENT COMPOSITION FAILURE: stale T0 capability committed after T1 PREVENTED`

Observed result:

`assert 'COMMITTED' != 'COMMITTED'`

Pytest result:

`1 failed in 0.11s`

## Sequence

1. T0 synthetic runtime condition evaluated VALID -> ACTIVE.
2. An exact H11 capability was issued for the represented attempt/payload.
3. T1 synthetic runtime condition changed to WITHDRAWN -> PREVENTED.
4. The caller deliberately ignored AIRP-006's cooperative outer branch.
5. The caller invoked the existing H11 `gateway.commit` directly using the still-valid T0 capability.
6. The gateway returned **COMMITTED** and the represented consequence was formed.

## Finding

The existing H11 protected execution boundary does not independently bind the current-standing determination used by AIRP-006.

AIRP-006 remains a valid orchestration/composition result: a cooperative caller that respects PREVENTED does not invoke the sink. It is **not** evidence that the protected sink itself enforces the later current-standing change against a direct caller holding an earlier valid capability.

## Classification

**RED — enforcement composition failure.**

This is a reference-model finding. It does not establish anything about a production EPR because no production EPR is integrated.

## Required remediation property

A correction must ensure that the protected execution boundary independently obtains/verifies consequence-time current standing, or consumes a cryptographically/bound verifiable determination whose validity cannot survive a relevant standing change.

A stale T0 execution capability must not be sufficient after T1 becomes PREVENTED.

The frozen AIRP-008 test must be rerun after remediation. This first failure is retained unchanged.
