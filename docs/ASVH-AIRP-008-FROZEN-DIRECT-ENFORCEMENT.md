# ASVH-AIRP-008 — Frozen Direct Enforcement Challenge

**Status:** FROZEN BEFORE EXECUTION  
**Origin:** RED2-01, ASVH-AIRP-007  
**Date:** 2026-09-20

## Proposition

A capability that was exact and valid while T0 current standing was ACTIVE must not remain sufficient to form the represented consequence after T1 current standing becomes PREVENTED.

## Attack

1. T0 synthetic runtime condition VALID -> ACTIVE.
2. Issue exact existing H11 capability for attempt/payload.
3. T1 synthetic runtime condition WITHDRAWN -> PREVENTED.
4. Ignore AIRP-006's cooperative outer branch.
5. Call the existing H11 `gateway.commit` directly with the previously valid capability.
6. Assert that no represented COMMITTED consequence forms.

## Failure condition

If the gateway returns COMMITTED or the protected sink receives the consequence, current-standing enforcement is not composed into the protected execution boundary. The AIRP-006 PASS would then remain valid only as an orchestration/composition result, not enforcement against a direct caller.

No gateway change is permitted before first execution.

## Boundary

Synthetic Python reference-model test only. No NHS legal/consent rule and no ORCHA/AiRP finding is asserted.
