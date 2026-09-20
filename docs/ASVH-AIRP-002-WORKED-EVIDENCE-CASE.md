# ASVH-AIRP-002 — Worked Evidence Case

**Status:** Executable pre-beta evidence case  
**Scope:** synthetic NHS ambient-scribing clinical-record commit boundary  
**Important:** not an official ORCHA AiRP assessment.

## Question

Can an earlier legitimate documentation state remain sufficient when a relevant authority condition changes before the represented clinical-record commit?

## Scenario

At **T0**, a synthetic ambient-scribing workflow is legitimately initiated while the modeled consent/authority dependency is VALID at revision 1.

Before the represented EPR commit, the authoritative dependency changes.

At **T1**, the same dependency is WITHDRAWN at revision 2.

The test deliberately preserves the earlier legitimate state. The proposition is that historical validity must not substitute for present standing at the consequence boundary.

## Executable evidence

`tests/test_asvh_airp_002_worked_case.py`

The test uses the existing HARDEN-010 consequence-time convergence mechanism rather than a special AiRP-only implementation.

Expected observations:

1. T0 evaluates ACTIVE.
2. T1 evaluates PREVENTED.
3. No consequence bind is returned for the prevented T1 state.
4. The represented clinical-record commit list remains empty.
5. The comparator demonstrates only that an earlier VALID observation is historical evidence; it does **not** claim what a real EPR would do without FlowSignal.

## AiRP interpretation

This case is relevant only if the actual AiRP identifies an activated risk for which loss/change of runtime authority is material and recognises an execution-time structural control as a mitigation.

It therefore tests the narrower FlowSignal hypothesis:

**earlier approval/validity is not treated as evidence of present standing when the relevant state has changed before consequence formation.**

It does not establish that FlowSignal mitigates every AiRP risk, nor does it reproduce ORCHA's proprietary risk-activation logic.

## Evidence and residual gap

If the executable test passes, it supports the represented reference-model control property.

It does **not** demonstrate:
- that a production EPR cannot be reached by another route;
- that a real EPR write was physically prevented;
- that ORCHA will classify this control as an AiRP mitigation;
- external rollback-resistant trust;
- production executor identity trust;
- externally confirmed versus unresolved consequence outcome.

Those remain subject to the preserved HARDEN-011 boundary and, where applicable, actual AiRP/EPR integration testing.

## Decision rule

A passing reference test is **SUPPORTED WITH BOUNDARY**, not an AiRP pass. If the actual AiRP does not recognise this control for the activated risk, the AiRP mapping must be narrowed or falsified rather than changing the test or framework interpretation.
