# ASVH-AIRP-006 — Frozen Composition Challenge

**Status:** FROZEN BEFORE EXECUTION  
**Date:** 2026-09-20  
**Origin:** RED-03 in ASVH-AIRP-005  
**Scope:** synthetic engineering condition at the modeled pre-consequence boundary.

## Challenge

AIRP-002 demonstrated consequence-time state change but did not exercise the existing HARDEN-011 protected execution sink.

AIRP-006 asks whether the existing consequence-time determination and the existing H11 execution boundary can be composed **without changing either mechanism to obtain a pass**.

## Frozen propositions

1. T0 synthetic runtime condition is VALID and evaluates ACTIVE.
2. Existing H11 execution authority is issued for the exact represented attempt and payload.
3. Before represented consequence formation, T1 condition changes to WITHDRAWN.
4. T1 consequence-time evaluation returns PREVENTED.
5. PREVENTED cannot be promoted into a call that forms the represented H11 consequence.
6. The protected sink remains empty.
7. A separate positive control proves that the unchanged H11 sink is reachable and can COMMIT when current standing is ACTIVE.

## Failure condition

The challenge is RED if any of the following occurs:
- T1 WITHDRAWN is not PREVENTED;
- the protected sink receives a represented commit after T1 PREVENTED;
- the composition requires weakening or special-casing either existing mechanism;
- the positive control cannot reach the existing H11 sink under ACTIVE current standing.

## Claim boundary

This is a composition test inside the Python reference model. It does not demonstrate actual EPR non-bypassability, physical non-formation, production trust, or ORCHA/AiRP recognition.

The modeled condition is deliberately named **synthetic runtime condition**. It is not asserted to be a universal NHS consent or legal-authority rule.
