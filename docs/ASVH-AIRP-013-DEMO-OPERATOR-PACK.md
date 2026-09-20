# ASVH-AIRP-013 — Demo Operator Pack

**Status:** Handover-ready operator guide  
**Companion:** ASVH-AIRP-012 Point-and-Click Demonstration Runbook  
**Reference run:** 35500425335  
**Audience:** any authorised FlowSignal demonstrator or technical reviewer  
**Target duration:** 15–20 minutes

## 1. Operator objective

Run the demonstration exactly from preserved repository evidence. Do not improvise claims.

The audience should leave understanding three things:

1. earlier validity is not automatically present standing;
2. the reference-model protected commit path now requires exact typed current standing;
3. important production/external properties remain deliberately NOT DEMONSTRATED.

## 2. Five-minute setup checklist

Before the audience joins:

- Sign in to GitHub and open `grahamb-ai/runtime-authority-reference-implementation`.
- Select branch `asvh-harden-011-from-225-baseline`.
- Set browser zoom so code and Actions results are readable.
- Open the tabs in the order below.
- Do not edit files during the demonstration.
- Keep AIRP-012 open as the detailed fallback script.

### Tab order

**TAB 1 — Closure**  
`docs/ASVH-AIRP-010-ENGINEERING-CYCLE-CLOSURE.md`

**TAB 2 — Evidence/gap matrix**  
`docs/ASVH-AIRP-003-EVIDENCE-GAP-MATRIX.md`

**TAB 3 — State-change case**  
`tests/test_asvh_airp_002_worked_case.py`

**TAB 4 — Composition case**  
`tests/test_asvh_airp_006_composition.py`

**TAB 5 — Protected-boundary case**  
`tests/test_asvh_airp_008_direct_enforcement.py`

**TAB 6 — Mandatory-standing case**  
`tests/test_asvh_airp_009_standing_dependency.py`

**TAB 7 — Final GitHub Actions evidence**  
Actions run **35500425335**

**TAB 8 — AiRP mapping**  
`docs/ASVH-AIRP-001-PRE-BETA-EVIDENCE-MAPPING.md`

**TAB 9 — Detailed operator fallback**  
`docs/ASVH-AIRP-012-POINT-AND-CLICK-DEMO-RUNBOOK.md`

## 2A. Direct navigation card

Use these branch-pinned links. If a link opens a different branch, stop and correct it before presenting.

- Repository branch: https://github.com/grahamb-ai/runtime-authority-reference-implementation/tree/asvh-harden-011-from-225-baseline
- AIRP-010 closure: https://github.com/grahamb-ai/runtime-authority-reference-implementation/blob/asvh-harden-011-from-225-baseline/docs/ASVH-AIRP-010-ENGINEERING-CYCLE-CLOSURE.md
- AIRP-003 matrix: https://github.com/grahamb-ai/runtime-authority-reference-implementation/blob/asvh-harden-011-from-225-baseline/docs/ASVH-AIRP-003-EVIDENCE-GAP-MATRIX.md
- AIRP-002 test: https://github.com/grahamb-ai/runtime-authority-reference-implementation/blob/asvh-harden-011-from-225-baseline/tests/test_asvh_airp_002_worked_case.py
- AIRP-006 test: https://github.com/grahamb-ai/runtime-authority-reference-implementation/blob/asvh-harden-011-from-225-baseline/tests/test_asvh_airp_006_composition.py
- AIRP-008 test: https://github.com/grahamb-ai/runtime-authority-reference-implementation/blob/asvh-harden-011-from-225-baseline/tests/test_asvh_airp_008_direct_enforcement.py
- AIRP-009 test: https://github.com/grahamb-ai/runtime-authority-reference-implementation/blob/asvh-harden-011-from-225-baseline/tests/test_asvh_airp_009_standing_dependency.py
- Reference Actions run: https://github.com/grahamb-ai/runtime-authority-reference-implementation/actions/runs/35500425335
- AIRP-001 mapping: https://github.com/grahamb-ai/runtime-authority-reference-implementation/blob/asvh-harden-011-from-225-baseline/docs/ASVH-AIRP-001-PRE-BETA-EVIDENCE-MAPPING.md
- AIRP-012 detailed runbook: https://github.com/grahamb-ai/runtime-authority-reference-implementation/blob/asvh-harden-011-from-225-baseline/docs/ASVH-AIRP-012-POINT-AND-CLICK-DEMO-RUNBOOK.md

### Stable visual anchors

Before speaking, make sure the following is visible:

- AIRP-010: heading **Final observed verification state**.
- AIRP-002: the T0/T1 assertions in the executable test.
- AIRP-006: test names for changed-standing prevention and ACTIVE positive control.
- AIRP-008: the direct-enforcement test function.
- AIRP-009: the parameterised invalid-standing cases and ACTIVE positive control.
- Actions: the job list containing AIRP-006, AIRP-008, AIRP-009 and fourth-order-trust-boundary.
- AIRP-001: section **Pre-beta mapping** with separate evidence/relevance columns.

Screenshots are not evidential artefacts: GitHub UI layout can change. These branch-pinned paths, headings, job names and run ID are the stable navigation cues.

## 3. Visual orientation

Use the repository headings and test names as the visual anchors. Do not scroll rapidly through implementation code.

At each step:
1. announce what question is being tested;
2. point to the relevant test/result;
3. state the observed evidence;
4. state the boundary;
5. move on.

The audience does not need to understand Python to follow the evidence chain.

## 4. Operator script

### SCREEN 1 — AIRP-010 closure

**Point to:** “Final observed verification state.”

**Say:**

“I'm going to show you the evidence in the order it was discovered, including the failures. This is a Python reference model using synthetic clinical data. It is not an official AiRP assessment and it does not claim production EPR behavior.”

Then:

“The question is whether an earlier valid state remains sufficient when standing changes before the represented consequential action.”

**Next:** Tab 3.

---

### SCREEN 2 — AIRP-002

**Point to:** T0 VALID / ACTIVE and T1 WITHDRAWN / PREVENTED.

**Say:**

“At T0 the modeled condition is valid. Before the represented clinical-record consequence, it changes. At T1 the current result is PREVENTED.”

“Earlier validity remains evidence of what was true earlier. It is not automatically evidence of present standing.”

**Do not say:** “FlowSignal stopped a real EPR write.”

**Next:** Tab 4.

---

### SCREEN 3 — AIRP-006

**Point to:** the state-change test and ACTIVE positive control.

**Say:**

“Next we connected that state-change proposition to the existing protected execution path. The positive control proves the represented sink is reachable when standing is ACTIVE.”

**Switch briefly to Tab 7** and select the AIRP-006 job.

**Expected visible result:** `2 passed`.

**Say:**

“But this test taught us something important. The prevention still depended on the caller following the orchestration correctly. So we challenged the protected boundary directly.”

**Next:** Tab 5.

---

### SCREEN 4 — AIRP-008

**Point to:** direct protected-boundary invocation after the state change.

**Say:**

“This was deliberately stronger. An earlier valid execution capability already exists. Current standing changes, and the caller nevertheless invokes the protected gateway.”

“The first run failed. The earlier capability could still produce the represented commit. We preserved that result before changing anything.”

If challenged, open:
`evidence/ASVH-AIRP-008-DIRECT-ENFORCEMENT-FIRST-FAILURE.md`.

Then say:

“The correction moved current-standing evaluation into the protected gateway.”

**Switch to Tab 7 → AIRP-008 job.**

**Expected:** `1 passed`.

**Say:** “This is PASS AFTER REMEDIATION, inside the reference-model boundary.”

**Next:** Tab 6.

---

### SCREEN 5 — AIRP-009

**Point to:** the seven standing-dependency cases.

**Say:**

“We then challenged the correction itself. Was current standing genuinely mandatory, or could configuration or representation weaken it?”

Point out:
- PREVENTED;
- INDETERMINATE;
- null;
- plain string ACTIVE;
- reader exception;
- absent reader;
- exact typed ACTIVE positive control.

**Say:**

“The first run found two weaknesses: plain-string ACTIVE was accepted, and absence of the standing reader retained legacy commit behavior.”

If challenged, open:
`evidence/ASVH-AIRP-009-STANDING-DEPENDENCY-FIRST-RESULT.md`.

**Expected first-result evidence:** `2 failed, 5 passed`.

Then:

“We corrected those properties. Standing is now mandatory at commit and must be exact typed ACTIVE.”

**Switch to Tab 7 → AIRP-009.**

**Expected:** `7 passed`.

**Next:** stay on Tab 7.

---

### SCREEN 6 — Final verification

Show the jobs slowly.

**Read exactly:**

- baseline verification — PASS;
- third-order durable boundary — PASS;
- AIRP-002 — PASS;
- AIRP-006 — 2/2 PASS;
- AIRP-008 — 1/1 PASS;
- AIRP-009 — 7/7 PASS;
- fourth-order trust boundary — FAIL.

**Say:**

“The final red is not hidden. It marks the point where this self-contained reference environment can no longer establish the external property.”

**Do not call the complete workflow green.**

**Next:** Tab 1, NOT DEMONSTRATED section.

---

### SCREEN 7 — Where the evidence stops

**Point to:** AIRP-010 “Deliberately NOT DEMONSTRATED.”

**Say:**

“These are the properties for which we now need external evidence: production standing-source trust and freshness, independent identity/key administration, external rollback behavior, relationship between the standing decision and an actual EPR write, production route closure, and confirmed versus unresolved external consequence.”

“We could simulate more of this locally, but that would demonstrate another simulation rather than the external system.”

**Next:** Tab 8.

---

### SCREEN 8 — AiRP handover

**Point to:** separate FlowSignal evidence status and AiRP relevance status columns.

**Say:**

“We have deliberately not converted technical evidence into an AiRP finding. AiRP relevance remains untested until ORCHA assesses it.”

**Ask exactly:**

“How would AiRP decompose or classify this ambient-scribing capability into AI feature or features? For any risk AiRP then activates, does it recognise this kind of consequence-time runtime authority control as a mitigation — and, if it does, what evidence would AiRP require from us?”

**Stop talking and allow the reviewer to answer.**

## 5. One-page operator cheat sheet

### The story
**002:** state changed.  
**006:** connected state to protected path.  
**008:** direct boundary challenge exposed weakness → preserved → corrected → PASS.  
**009:** correction challenged → two weaknesses preserved → corrected → 7/7 PASS.  
**Final:** external-boundary RED deliberately remains.

### Numbers to remember
- AIRP-006: **2/2**
- AIRP-008: **1/1**
- AIRP-009: **7/7**
- Reference run: **35500425335**
- Fourth-order: **RED / NOT DEMONSTRATED externally**

### Safe phrases
- “reference-model evidence”
- “modeled pre-consequence boundary”
- “represented clinical-record commit”
- “PASS AFTER REMEDIATION”
- “AiRP relevance remains untested”
- “NOT DEMONSTRATED beyond this boundary”

### Never say
- “FlowSignal passed AiRP.”
- “ORCHA validated FlowSignal.”
- “Everything is green.”
- “This proves a real EPR cannot bypass FlowSignal.”
- “This proves an unauthorised real-world consequence cannot form.”
- “This is a universal NHS consent rule.”
- “246 AiRP tests.”

## 6. Recovery instructions

### GitHub Actions page is slow/unavailable
Do not rerun anything live merely for presentation.

Use AIRP-010, which records the frozen reference result, and the preserved evidence documents. State that run 35500425335 is the reference execution.

### A reviewer asks to rerun tests live
Explain that the preserved run is the evidential reference. A fresh run can demonstrate reproducibility but does not replace the preserved first-failure/remediation history.

If a fresh run produces a different result, stop making the prior current-state claim and investigate the discrepancy before continuing.

### You open the wrong branch
Stop. Select `asvh-harden-011-from-225-baseline` before presenting evidence.

### A file has changed since rehearsal
Use AIRP-010 and the reference run rather than guessing. Verify the change after the meeting.

### Someone asks a question you cannot substantiate
Say:

“That isn't demonstrated by the evidence I'm showing. I don't want to extend the claim beyond the test.”

Then return to the documented boundary.

### Someone asks whether the remaining RED can simply be fixed
Say:

“Not honestly inside this reference model. The next useful evidence needs an external trust or EPR boundary.”

## 7. Reviewer question card

**What does FlowSignal actually test here?**  
Whether the represented protected commit path requires current standing and exact execution conditions rather than relying only on earlier validity.

**Does it assess the quality of the AI-generated note?**  
No.

**Does it prove production EPR enforcement?**  
No. That remains NOT DEMONSTRATED.

**Why preserve failures?**  
Because they show what the earlier implementation did not establish and make the remediation history falsifiable.

**Why is one job red?**  
Because the remaining questions require evidence outside the self-contained reference model.

**Is ORCHA involved in these test results?**  
No. The package is being prepared for ORCHA to assess relevance against the actual AiRP.

**What is the next experiment?**  
Only if external review establishes relevance: a controlled non-production integration using synthetic data and an actual external consequence endpoint.

## 8. Handover test for a new operator

Before presenting externally, a new operator should perform one rehearsal without assistance and demonstrate that they can:

- select the correct branch;
- navigate tabs 1–8;
- explain 002, 006, 008 and 009 without conflating them;
- show both preserved failures;
- show final run 35500425335;
- explain why fourth-order RED remains;
- state at least three explicit NOT DEMONSTRATED properties;
- distinguish FlowSignal evidence status from AiRP relevance;
- answer the reviewer question card without extending the claim.

If any of these cannot be completed, rehearse again before external use.

## 9. Handover completion

The operator is ready when they can deliver the 15-minute sequence using only this pack and the repository, without needing the original engineer/founder to explain what each result means.
