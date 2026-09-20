# ASVH-AIRP-012 — Point-and-Click Demonstration Runbook

**Status:** Reproducible demonstration script  
**Audience:** ORCHA / assurance reviewers / technical evaluators / FlowSignal demonstrators  
**Duration:** 15–20 minutes  
**Reference run:** GitHub Actions 35500425335  
**Scenario:** synthetic ambient-scribing clinical-record commit  
**Important:** this is a reference-model demonstration, not an official ORCHA AiRP assessment and not a production-EPR demonstration.

## 1. Purpose

This runbook lets a person who did not build the harness follow the evidence from proposition to executable result without needing to infer the intended sequence.

The demonstration answers one narrow question:

> When standing can change between earlier validity and consequential execution, does the reference-model protected commit path require current standing rather than accepting the earlier state as sufficient?

It does not ask the demonstrator to explain or defend properties outside the evidence.

## 2. Before the meeting

Open these browser tabs in this order:

1. Repository branch `asvh-harden-011-from-225-baseline`.
2. `docs/ASVH-AIRP-010-ENGINEERING-CYCLE-CLOSURE.md`.
3. `docs/ASVH-AIRP-003-EVIDENCE-GAP-MATRIX.md`.
4. `tests/test_asvh_airp_002_worked_case.py`.
5. `tests/test_asvh_airp_006_composition.py`.
6. `tests/test_asvh_airp_008_direct_enforcement.py`.
7. `tests/test_asvh_airp_009_standing_dependency.py`.
8. GitHub Actions run **35500425335**.
9. `docs/ASVH-AIRP-001-PRE-BETA-EVIDENCE-MAPPING.md`.

Do not start with the architecture or the full test history.

## 3. Opening — 60 seconds

### Point to
AIRP-010, **Purpose** and **Final observed verification state**.

### Say
“FlowSignal is testing a narrow runtime question. A workflow may have been valid earlier, but a consequential action can occur later. We want to know whether the conditions that permit that action still hold at the point represented here as the pre-consequence boundary.”

“Everything I am showing is a Python reference model using synthetic clinical data. I am not claiming this proves production EPR behavior.”

### Do not say
- FlowSignal has passed AiRP.
- ORCHA has validated the control.
- This proves a real EPR cannot be reached another way.
- This is an NHS legal or universal consent rule.

## 4. Step 1 — Earlier validity versus present standing

### Click
`tests/test_asvh_airp_002_worked_case.py`

### Point to
The T0 VALID/revision 1 evaluation and T1 WITHDRAWN/revision 2 evaluation.

### Say
“At T0 the modeled condition is VALID and standing evaluates ACTIVE. Before the represented consequence, that condition changes. At T1 it is WITHDRAWN and evaluates PREVENTED.”

“The important proposition is simply that earlier validity is historical evidence. It is not automatically evidence of present standing.”

### Evidence expected
T0 = ACTIVE.  
T1 = PREVENTED.  
No T1 consequence bind.  
No local represented commit branch.

### Boundary
AIRP-002 is a state-change/determination case. Do not present it as proof of protected execution enforcement.

## 5. Step 2 — Connect standing to the protected execution path

### Click
`tests/test_asvh_airp_006_composition.py`

### Point to
1. T0 ACTIVE;
2. the exact represented attempt/payload capability;
3. T1 WITHDRAWN/PREVENTED;
4. the ACTIVE positive control.

### Say
“AIRP-006 connects the state-change proposition to the existing protected execution path. Its positive control matters because it shows that the protected sink is reachable when current standing is ACTIVE.”

### Click
GitHub Actions run **35500425335** → job **airp-006-composition-challenge**.

### Confirm on screen
**2 passed.**

### Boundary
“AIRP-006 originally depended on cooperative orchestration. We did not hide that weakness. The next case tested the protected boundary directly.”

## 6. Step 3 — Show why the evidence history matters

### Click
`tests/test_asvh_airp_008_direct_enforcement.py`

### Say
“This test was created because AIRP-006 was not enough. It deliberately calls the protected gateway with an earlier valid capability after current standing has changed.”

“The first execution of this property failed: the old capability could still produce the represented commit. We preserved that failure before changing the implementation.”

### Point to
`evidence/ASVH-AIRP-008-DIRECT-ENFORCEMENT-FIRST-FAILURE.md`, if the reviewer wants the original observation.

### Say
“The correction moved the consequence-time standing check into the protected gateway itself. The caller can no longer make the earlier standing sufficient simply by calling the gateway directly.”

### Click
Run **35500425335** → **airp-008-direct-enforcement**.

### Confirm
**1 passed.**

### Classification
PASS AFTER REMEDIATION — reference-model boundary only.

## 7. Step 4 — Challenge whether standing is genuinely mandatory

### Click
`tests/test_asvh_airp_009_standing_dependency.py`

### Point to the seven cases
- PREVENTED;
- INDETERMINATE;
- no standing;
- plain string `"ACTIVE"`;
- standing-reader exception;
- no standing reader;
- exact typed `ConvergenceResult.ACTIVE` positive control.

### Say
“We then challenged our own correction. Could the protected gateway still operate with an absent or weakly represented standing dependency?”

“The first run exposed two gaps. A plain string ACTIVE was accepted, and a gateway with no standing reader retained legacy commit behavior. Both observations were preserved before correction.”

### Click
`evidence/ASVH-AIRP-009-STANDING-DEPENDENCY-FIRST-RESULT.md`.

### Point to
**2 failed, 5 passed.**

### Say
“The correction made consequence-time standing mandatory and requires exact typed ACTIVE. That stronger contract also broke some old positive-control fixtures. We preserved that regression and aligned those fixtures rather than weakening the new requirement.”

### Click
Run **35500425335** → **airp-009-standing-dependency**.

### Confirm
**7 passed.**

## 8. Step 5 — Show the complete final run

### Click
GitHub Actions run **35500425335**.

### Point to each job

- verify — PASS;
- third-order durable boundary — PASS;
- AIRP-002 — PASS;
- AIRP-006 — PASS, 2/2;
- AIRP-008 — PASS, 1/1;
- AIRP-009 — PASS, 7/7;
- fourth-order trust boundary — FAIL.

### Say
“The red result is deliberate. We stopped where our own reference environment can no longer establish the property.”

Do not describe the overall workflow as “all green.”

## 9. Step 6 — Show the remaining RED

### Click
`docs/ASVH-AIRP-010-ENGINEERING-CYCLE-CLOSURE.md` → **Deliberately NOT DEMONSTRATED**.

### Say
“The remaining questions require evidence outside this reference model.”

### Point to
1. production standing-source authenticity/freshness/availability/rollback resistance;
2. independently administered executor identity/key trust;
3. correlated rollback across external trust domains;
4. external anchor loss/recovery;
5. atomicity between standing evaluation and actual EPR write;
6. actual production route closure;
7. physical consequence non-formation;
8. confirmed versus unresolved external consequence;
9. actual ORCHA/AiRP recognition.

### Say
“We could model more of these locally, but that would prove properties of another model. It would not prove the external system.”

## 10. Step 7 — Hand the question to ORCHA

### Click
`docs/ASVH-AIRP-001-PRE-BETA-EVIDENCE-MAPPING.md`.

### Point to
The separate columns **FlowSignal evidence status** and **AiRP relevance status**.

### Say
“Notice that the technical evidence status and AiRP relevance are deliberately separate. AiRP relevance is still UNTESTED PENDING ACTUAL AiRP.”

### Ask
“How would AiRP decompose or classify this ambient-scribing capability into AI feature or features? For any risk AiRP then activates, does it recognise this kind of consequence-time runtime authority control as a mitigation? If it does, what evidence would AiRP require from us?”

Then stop. Let ORCHA answer.

## 11. Optional reviewer drill-down

If asked **‘Did you only test the happy path?’**:
Show AIRP-008 and AIRP-009 first-result evidence. Explain that the first observations were retained and the same properties were rerun after correction.

If asked **‘Why is there still a red job?’**:
Show AIRP-010. Explain that the remaining proposition crosses into external trust/EPR behavior and has deliberately not been simulated into a pass.

If asked **‘Does this stop hallucinations or prove note accuracy?’**:
“No. Model quality, hallucination, bias, clinical efficacy and model drift are outside this control.”

If asked **‘Does this prove a real EPR cannot bypass FlowSignal?’**:
“No. Production EPR route closure is NOT DEMONSTRATED. That requires an external integration.”

If asked **‘Is this an ORCHA assessment?’**:
“No. This is a pre-beta evidence package for ORCHA to assess against the actual AiRP.”

If asked **‘What happens next if AiRP sees relevance?’**:
“A controlled non-production experiment using synthetic data and an actual external consequence endpoint, with confirmed, failed and unresolved outcome handling.”

## 12. Demonstrator stop conditions

Stop and correct the presentation if any demonstrator starts to imply:
- official ORCHA validation;
- AiRP pass/certification;
- universal NHS clinical/legal semantics;
- production EPR non-bypassability;
- physical non-formation outside the reference model;
- all tests are green;
- the fourth-order RED is a defect to hide;
- AIRP-002 alone proves enforcement;
- AIRP-006 alone proves protected-boundary enforcement.

## 13. One-minute version

If time is cut short:

“Earlier validity is not automatically present standing. AIRP-002 demonstrates the state change. AIRP-006 connects that to the protected path. AIRP-008 exposed and then corrected a direct protected-boundary weakness. AIRP-009 exposed and then corrected optional/weak standing dependency. In the final reference run, 006 is 2/2, 008 is 1/1 and 009 is 7/7. We deliberately retain a red external-boundary result because production source trust, actual EPR route closure and external consequence confirmation cannot be proved inside our Python model. The question for ORCHA is whether AiRP recognises this class of runtime control for any risk it activates, and what external evidence it would require.”

## 14. Completion criterion

A person following this runbook should be able to:
- reproduce the narrative directly from repository evidence;
- distinguish initial failure from post-remediation result;
- distinguish technical evidence from AiRP relevance;
- show the final run without concealing the external-boundary RED;
- state precisely what has and has not been demonstrated;
- hand the classification question to ORCHA rather than answering it for them.
