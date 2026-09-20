# ASVH-AIRP-004 — ORCHA Demonstration Protocol

**Status:** Pre-beta demonstration protocol  
**Audience:** ORCHA Head of Partnerships / COO / AiRP stakeholders  
**Duration:** 10–15 minutes  
**Scenario:** Synthetic NHS ambient-scribing clinical-record commit  
**Purpose:** Demonstrate the tested runtime-authority property, show the evidence boundary, and ask ORCHA to test the hypothesis against the actual AiRP.

> This is not an official ORCHA AiRP assessment, score, certification, endorsement, partnership statement or production-EPR demonstration.

## 1. Meeting objective

Do not try to prove that FlowSignal solves AiRP.

Demonstrate one narrow proposition:

**When a consequential AI-assisted action depends on authority that can change between earlier approval and execution, the FlowSignal reference model can require and enforce present standing at the modeled pre-consequence boundary.**

Repository artefacts and CI retain engineering provenance of the observed results. This is not a claim that the AIRP executable cases themselves produce a durable production authority receipt.

Then show exactly where the current evidence stops and invite ORCHA to determine whether that control is relevant to any actual AiRP feature block / activated risk.

## 2. Demonstration sequence

### 00:00–01:30 — The problem

Use the ambient-scribing example.

A clinical note can be generated correctly and the workflow can have been legitimate when initiated. The narrower question is whether the conditions authorising the proposed clinical-record commit still hold when that consequence is about to occur.

State:

**Earlier validity is evidence of earlier validity. It is not automatically evidence of present standing.**

Do not discuss hallucination, transcription quality, bias or clinical efficacy as FlowSignal capabilities.

### 01:30–03:00 — Show the execution boundary

Display the simple control sequence:

**WHO → WHAT → NOW → MATCH → ALLOW / ESCALATE / REFUSE**

Explain:
- WHO — who is acting;
- WHAT — what action is authorised;
- NOW — whether the relevant authority still holds;
- MATCH — whether the action about to occur matches what was authorised.

Locate the check at the modeled pre-consequence boundary for the represented clinical-record commit.

Say explicitly that the current demonstration is a reference-model boundary, not a claim of universal production-EPR non-bypassability.

### 03:00–05:00 — AIRP-002: establish the state-change proposition

Use the executable worked case in:

`tests/test_asvh_airp_002_worked_case.py`

Scenario:

**T0**
- synthetic workflow legitimately initiated;
- relevant modeled condition = VALID, revision 1;
- result = ACTIVE.

**State change**
- before represented consequence formation, the relevant authoritative condition changes.

**T1**
- same modeled condition = WITHDRAWN, revision 2;
- result = PREVENTED;
- no consequence bind returned;
- represented clinical-record commit not formed.

The key demonstration point is not simply that a rule returned PREVENTED. It is that the earlier legitimate state is retained as historical evidence but is not substituted for present standing.

### 05:00–08:30 — Show the strengthened execution evidence

Use AIRP-006, AIRP-008 and AIRP-009 as the execution evidence sequence:

- **AIRP-006:** composition plus reachable-sink positive control; final aligned run 35500425335 recorded **2 passed**.
- **AIRP-008:** direct protected-boundary invocation exposed the first enforcement gap; failure was preserved, the gateway was strengthened to obtain current standing itself, and the final run recorded **1 passed**.
- **AIRP-009:** challenged whether current standing was mandatory and exact-typed. The first run exposed permissive string equality and legacy no-reader behavior; both failures were preserved. After remediation and fixture alignment, final run 35500425335 recorded **7 passed**.

Do not present AIRP-006 alone as protected-boundary enforcement. Its original orchestration weakness is part of the evidence history that led to AIRP-008.

### 08:30–09:30 — Show the comparator

Explain what happens if only the earlier observation is retained.

The T0 VALID observation proves what was observed at T0. It contains no evidence that the same condition still holds at T1.

Do **not** say:

“Without FlowSignal the EPR would have committed the note.”

That has not been demonstrated.

Say:

**“Without consequence-time revalidation, the earlier observation alone does not establish present standing.”**

### 09:30–11:00 — Show the evidence

Open:

- `docs/ASVH-AIRP-002-EXECUTION-RESULT.md`
- `docs/ASVH-AIRP-003-EVIDENCE-GAP-MATRIX.md`

Show the final reference verification, GitHub Actions run **35500425335**:
- baseline verification — PASS;
- H11 third-order durable boundary — PASS;
- AIRP-002 — PASS;
- AIRP-006 — 2/2 PASS;
- AIRP-008 — 1/1 PASS;
- AIRP-009 — 7/7 PASS;
- H11 fourth-order trust boundary — FAIL / deliberately preserved external-boundary RED.

Explain that the workflow-level FAILURE is intentional evidence: the fourth-order tests identify properties the self-contained reference model cannot legitimately prove.

Do not bury or apologise for the RED result.

### 11:00–12:30 — Show where FlowSignal stops

Put the four unresolved properties on screen:

1. correlated rollback resistance across all relevant trust domains;
2. independently administered production executor identity/key trust;
3. safe behavior when the independent consumption anchor is lost/recreated;
4. actual external consequence confirmation, including CONFIRMED versus UNRESOLVED outcome.

State:

**“We could add more local simulation until everything turns green. We have deliberately not done that, because it would not prove these external properties.”**

This is the transition from laboratory evidence to the need for an actual integration boundary.

### 12:30–14:00 — Connect to AiRP

Open:

`docs/ASVH-AIRP-001-PRE-BETA-EVIDENCE-MAPPING.md`

Then state the hypothesis, without strengthening it:

**For a subset of AI Risk Profiler feature blocks where a consequential action depends on authority that can change between approval and execution, FlowSignal may provide an externally reproducible/testable-in-principle runtime control and evidence mechanism relevant to the mitigation stage, with resulting evidence potentially informing residual-risk/gap analysis.**

Explain that the public-framework work deliberately does not infer ORCHA's proprietary questionnaire, risk-activation logic or scoring.

### 14:00–15:00 — Hand the question to ORCHA

The preferred closing question is:

**“How would AiRP decompose or classify this ambient-scribing capability into AI feature(s)? For any risk AiRP then activates, does it recognise this kind of consequence-time runtime control as a mitigation — and, if it does, what evidence would AiRP require from us?”**

Then use the six beta falsification questions:

1. Does AiRP recognise runtime execution controls as a structural mitigation for any activated risk in this feature?
2. Which exact AiRP risk(s), if any, can WHO / WHAT / NOW / MATCH evidence legitimately mitigate?
3. Does AiRP require evidence FlowSignal does not produce?
4. Does FlowSignal produce evidence AiRP does not currently consume or recognise?
5. Do the four preserved external-boundary gaps appear in AiRP residual-risk/gap analysis?
6. Does the actual questionnaire falsify or materially narrow the FlowSignal hypothesis?

## 3. What to have open before the call

Keep the demonstration deliberately small:

1. AIRP-010 cycle closure;
2. AIRP-003 evidence/gap matrix;
3. AIRP-001 pre-beta mapping;
4. final CI run 35500425335;
5. AIRP-002/006/008/009 only as needed to walk the evidence progression.

Do not lead with the complete architecture, 246 checks, repository history or every hostile verification result. Those are supporting evidence if challenged.

## 4. Evidence available if challenged

If ORCHA asks how deep the testing goes, explain that the reference-model verification chain reached **246 underlying ASVH reference-model verification checks (not 246 AiRP checks)** before the deliberate fourth-order external-boundary probes.

Relevant tested themes include:
- present authority standing;
- exact execution-attempt identity;
- consequence binding;
- action/payload substitution;
- executor binding in the modeled trust architecture;
- route closure at the represented sink;
- shared single-use execution authority;
- rollback behavior;
- fail-closed cases;
- retained failure/remediation evidence.

Immediately follow that statement with the reference-model claim boundary.

## 5. Claims to avoid

Do not say:
- “FlowSignal passes AiRP.”
- “ORCHA has validated FlowSignal.”
- “FlowSignal solves the ten AiRP risks.”
- “FlowSignal prevents unauthorised EPR writes in production.”
- “The EPR cannot bypass FlowSignal.”
- “246 tests prove production safety.”
- “ORCHA and FlowSignal are partners.”

Use:
- “pre-beta mapping”;
- “reference-model evidence”;
- “tested property”;
- “represented clinical-record commit”;
- “SUPPORTED WITH BOUNDARY”;
- “NOT DEMONSTRATED”;
- “hypothesis for ORCHA to test.”

## 6. Success criteria for the meeting

The meeting is successful if ORCHA can answer one or more of these with concrete next steps:

- which actual AiRP feature block/question should receive the evidence;
- which activated risk, if any, the runtime control could mitigate;
- what additional evidence AiRP needs;
- whether FlowSignal can be tested in the AiRP beta/test group;
- whether an external EPR integration would resolve a residual gap AiRP considers material.

A commercial agreement is not required for this technical demonstration to be useful.

## 7. Next experiment if AiRP supports the hypothesis

Only if the actual AiRP indicates relevance, propose a controlled non-production integration:

**synthetic note → FlowSignal runtime determination → execution bind → test EPR commit endpoint → confirmed / failed / unresolved outcome → retained evidence**

This experiment should use synthetic patients/encounters/notes and a narrow test consequence path.

Its purpose is to move selected properties currently classified NOT DEMONSTRATED across the external boundary. It must not be described in advance as proving production non-bypassability.

## 8. Final line

**“We have taken the mechanism as far as we think we can legitimately take it inside our own reference environment. We would now like AiRP to tell us whether the control is relevant — and, if it is, what the next evidence boundary should be.”**
