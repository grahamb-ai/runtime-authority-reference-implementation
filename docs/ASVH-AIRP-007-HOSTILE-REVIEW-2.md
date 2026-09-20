# ASVH-AIRP-007 — Hostile Review 2: Remediated Package

**Status:** RED findings preserved before remediation  
**Date:** 2026-09-20  
**Object under test:** remediated AIRP-001–004 plus AIRP-006  
**Reviewer posture:** ORCHA technical reviewer / independent assurance reviewer

## Result

**PACKAGE IMPROVED, BUT NOT YET TECHNICALLY CLOSED.**

The first hostile-review findings were materially reduced. The second pass found five remaining weaknesses. Two are especially important because they affect whether the demonstration actually proves enforcement rather than orchestration.

## RED2-01 — AIRP-006 blocks by orchestration, not by enforcement inside the H11 gateway

AIRP-006 obtains a valid H11 execution capability before T1. At T1, consequence-time convergence returns PREVENTED. The test then uses an outer Python `if` to decide not to call `gateway.commit`.

Therefore the H11 gateway itself is not shown to consume or independently verify the T1 current-standing result.

An attacker or alternate caller already holding the previously issued valid capability could bypass that outer branch and call the unchanged gateway directly.

**Failure condition:** current-standing prevention depends on cooperative caller orchestration rather than being bound into the protected execution enforcement point.

**Classification:** FAIL — enforcement composition.

**Required next test:** after T1 becomes PREVENTED, deliberately call the existing H11 gateway directly with the previously valid capability. If it COMMITs, preserve RED. Do not modify the gateway before observing the result.

## RED2-02 — AIRP-004 still says “immediately before” in one demonstration instruction

Although the meeting proposition was narrowed to “modeled pre-consequence boundary,” section 01:30–03:00 still instructs the presenter to “Locate the check immediately before the represented clinical-record commit.”

Within a reference model this can still be misunderstood as demonstrated transactional adjacency.

**Classification:** FAIL — residual wording inconsistency.

**Correction:** “Locate the check at the modeled pre-consequence boundary.”

## RED2-03 — AIRP-001 mapping table still gives AiRP-stage classifications

AIRP-003 now correctly separates FlowSignal evidence status from AiRP relevance status, but AIRP-001 still labels the Structural & Governance Mitigations row “SUPPORTED WITH BOUNDARY” and Gap Analysis “PARTIALLY SUPPORTED.”

Because those rows are explicitly AiRP stages, the classifications can still be read as AiRP relevance findings, contradicting the later statement that relevance is UNTESTED.

**Classification:** FAIL — internal classification inconsistency.

**Correction:** separate “FlowSignal evidence position” from “AiRP relevance = UNTESTED PENDING ACTUAL AiRP” in AIRP-001 as well.

## RED2-04 — AIRP-004 demo sequence omits the stronger AIRP-006 evidence

The protocol still tells the presenter to run AIRP-002 and show AIRP-002 evidence, while AIRP-006 now provides the stronger composition evidence and positive control.

This is not an overclaim; it is an evidence-selection weakness. However, showing AIRP-002 as the primary execution demonstration after RED-03 was discovered risks recreating the original ambiguity live.

**Classification:** FAIL — stale demonstration design.

**Correction:** use AIRP-002 to explain the state-change proposition, then AIRP-006 as the execution-composition demonstration. Explicitly preserve the distinction.

## RED2-05 — “retain evidence of the resulting determination” is not demonstrated by AIRP-002/006 themselves

AIRP-004's meeting proposition combines two claims:
1. re-evaluate present standing; and
2. retain evidence of the resulting determination.

The repository has broader retained evidence/history, but AIRP-002/006 do not themselves generate a durable authority receipt or independently persisted evidence record for the T1 determination.

**Classification:** FAIL — evidence provenance/composition.

**Correction options:** either narrow the live proposition to the determination/enforcement property, or add a separate frozen test for durable evidence generation tied to the exact T1 determination. Do not imply AIRP-002/006 alone demonstrate durable evidence retention.

## Findings that survived Review 2

- Public ORCHA source provenance is now frozen.
- Technical evidence status and AiRP relevance are separated in AIRP-003.
- No independent third-party execution claim remains.
- Synthetic clinical semantics are explicit.
- 246 is clearly underlying ASVH verification, not AiRP checks.
- Feature decomposition is handed to ORCHA.
- AIRP-006 positive control prevents a vacuous unreachable-sink PASS.
- Four external-boundary REDs remain visible.
- No real-EPR non-bypassability or physical non-formation claim is made.

## Priority

**RED2-01 is the next engineering challenge.**

Do not repair the gateway first. Freeze a direct-call test in which:
- an exact valid H11 capability exists from T0;
- T1 current standing becomes PREVENTED;
- the caller nevertheless invokes `gateway.commit` directly;
- expected safety property: no represented COMMITTED consequence.

This distinguishes a true protected execution enforcement boundary from cooperative orchestration.
