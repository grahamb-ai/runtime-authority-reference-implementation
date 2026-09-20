# ASVH-AIRP-001 — ORCHA AiRP Pre-Beta Evidence Mapping

**Status:** Working assessment against ORCHA's publicly described AI Risk Profiler methodology  
**Date:** 2026-09-20  
**Scope:** NHS ambient-scribing clinical-record commit boundary  
**Not an official ORCHA AiRP assessment.**

## 1. Purpose

Test the frozen hypothesis that, for a subset of AI Risk Profiler feature blocks where a consequential action depends on authority that can change between approval and execution, FlowSignal may provide an independently testable runtime control and evidence mechanism relevant to the mitigation stage, with resulting evidence potentially informing residual-risk/gap analysis.

This document does not reproduce or infer ORCHA's proprietary questionnaire, taxonomy, scoring or risk-activation logic.

## 2. Public AiRP framework used

ORCHA publicly describes six stages:
1. Clinical Context / Clinical Risk Severity
2. Computational Function
3. Inference Technique and Model Architecture
4. Risk Activation
5. Structural and Governance Mitigations
6. Gap Analysis / Residual Risk

ORCHA also states that each AI feature is assessed separately, that structural and governance mitigations are assessed separately, and that the resulting profile is not a simple pass/fail result.

## 3. Feature under examination

**Feature:** AI-assisted ambient-scribing documentation proposed for commitment to a clinical record.

**Represented consequence:** clinical-record commit.

**FlowSignal boundary:** immediately before represented consequence formation, after the proposed action and relevant runtime context are known.

The reference implementation does not assess transcription accuracy, hallucination, bias, model quality, clinical efficacy, model drift, medical-device classification, or general product assurance.

## 4. Pre-beta mapping

| AiRP stage | FlowSignal contribution | Evidence position | Classification |
|---|---|---|---|
| Clinical Context | Identifies the protected consequence and runtime actors/target | Represented clinical-record commit is explicit in the harness | PARTIALLY SUPPORTED |
| Computational Function | Does not assess the AI's computational function; consumes a proposed consequential action | Function is context for the authority check, not evaluated by FlowSignal | OUT OF SCOPE |
| Inference Technique / Model Architecture | No model/inference assurance | No evidence claim | OUT OF SCOPE |
| Risk Activation | FlowSignal does not reproduce AiRP's proprietary activation logic | Runtime conditions may correspond to risks identified elsewhere, but FlowSignal does not decide which AiRP risks activate | OUT OF SCOPE |
| Structural & Governance Mitigations | Independent runtime authority checks, exact action/executor binding, current-standing validation, route-closure controls and retained evidence can operate as structural controls for applicable execution-time risks | HARDEN-010 + HARDEN-011 evidence chain | SUPPORTED WITH BOUNDARY |
| Gap Analysis / Residual Risk | Preserved failures and NOT DEMONSTRATED properties can expose remaining execution-boundary gaps | Fourth-order boundary explicitly preserves four unresolved external properties | PARTIALLY SUPPORTED |

## 5. Runtime control evidence relevant to mitigation analysis

For the represented clinical-record commit, the reference implementation has evidence for:
- current/present authority standing checks;
- exact execution-attempt identity;
- consequence binding;
- action/payload substitution resistance within the tested boundary;
- executor binding within the tested identity model;
- single-use consumption across tested shared SQLite instances;
- represented route closure through the modeled gateway;
- fail-closed behavior for several missing/mismatched authority conditions;
- retained evidence and replay/reconstruction properties already covered by the verification chain.

The complete H11 verification chain reached 246 passing checks before the fourth-order boundary probes.

## 6. Preserved residual gaps

The following remain **NOT DEMONSTRATED** beyond the self-contained reference model:

1. **Correlated rollback resistance** — rollback of both modeled execution-state and consumption-anchor domains can resurrect consumed authority.
2. **Independent production executor trust** — replacement/mutation of the modeled identity trust registry can change which credentials are accepted.
3. **Anchor-loss semantics** — loss/recreation of the modeled consumption anchor does not yet establish safe behavior for outstanding capabilities.
4. **External consequence confirmation** — the reference model cannot prove that local authority consumption corresponds to an actual EPR commit, nor reliably distinguish externally confirmed consequence formation from an unresolved external outcome.

These are not converted to PASS by further local simulation.

## 7. AiRP hypothesis result at this stage

**SUPPORTED IN PART, NOT YET VALIDATED BY ORCHA.**

The evidence supports a narrower proposition: FlowSignal can provide testable runtime structural-control evidence for some authority-dependent execution risks at a represented clinical-record commit boundary. The evidence may be relevant to AiRP's mitigation and residual-gap stages.

The evidence does **not** establish:
- coverage of all ten AiRP standard risks;
- equivalence between FlowSignal rules and AiRP risk activation;
- satisfaction of the proprietary AiRP questionnaire;
- an ORCHA assessment, certification, endorsement or partnership;
- production EPR non-bypassability;
- physical non-formation of an unauthorised external consequence.

## 8. Beta falsification questions

When access to the actual AiRP is available, test:

1. Does AiRP recognise runtime execution controls as a structural mitigation for any activated risk in this feature?
2. Which exact AiRP risk(s), if any, can evidence from WHO / WHAT / NOW / MATCH legitimately mitigate?
3. Does AiRP require evidence FlowSignal does not produce?
4. Does FlowSignal produce evidence that AiRP does not currently consume or recognise?
5. Do the four preserved external-boundary gaps appear in AiRP residual-risk/gap analysis?
6. Does applying the actual questionnaire falsify or materially narrow the hypothesis above?

## 9. Decision rule

Do not change the hypothesis to obtain a favourable AiRP result. Classify each actual AiRP finding as SUPPORTED, PARTIALLY SUPPORTED, NOT SUPPORTED, FALSIFIED or OUT OF SCOPE, retaining contradictory evidence.
