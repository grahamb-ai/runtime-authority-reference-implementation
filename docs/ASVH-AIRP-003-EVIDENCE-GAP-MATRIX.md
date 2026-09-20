# ASVH-AIRP-003 — Evidence & Gap Matrix

**Status:** Pre-beta evidence matrix  
**Date:** 2026-09-20  
**Scope:** synthetic NHS ambient-scribing clinical-record commit boundary  
**Important:** this is not an official ORCHA AiRP assessment, score, certification or endorsement.

## Purpose

Bring the public-framework mapping, executable AIRP-002 worked case, underlying runtime-authority verification evidence, and preserved external-boundary gaps into one reviewable artefact.

The matrix asks a narrow question:

> Where can FlowSignal currently provide testable runtime-control evidence relevant to an AiRP mitigation/gap discussion, and where does the evidence stop?

## Evidence matrix

| Area | FlowSignal proposition | Evidence | FlowSignal evidence status | AiRP relevance status | Residual gap / next evidence |
|---|---|---|---|---|---|
| Protected consequence | The represented consequence is a synthetic clinical-record commit | ASVH-AIRP-002 scenario and H11 route-closure harness | SUPPORTED WITH BOUNDARY | UNTESTED PENDING ACTUAL AiRP | Actual EPR consequence path not yet integrated |
| Earlier validity vs present standing | Earlier VALID state is not accepted as evidence that authority still holds at consequence time after relevant state changes | AIRP-002 executable case: T0 ACTIVE; T1 WITHDRAWN/PREVENTED; no bind; no represented commit | SUPPORTED WITH BOUNDARY | UNTESTED PENDING ACTUAL AiRP | Actual AiRP must determine whether this control is relevant to an activated risk |
| Current authority / NOW | Present standing is re-evaluated at the modeled consequence boundary | HARDEN-010 convergence/final-bind evidence | SUPPORTED WITH BOUNDARY | UNTESTED PENDING ACTUAL AiRP | Production authoritative source and external atomicity not demonstrated |
| Exact action / MATCH | Consequence binding and payload/attempt substitution checks protect the represented path | HARDEN-010/HARDEN-011 tests | SUPPORTED WITH BOUNDARY | UNTESTED PENDING ACTUAL AiRP | External EPR enforcement of the same binding not demonstrated |
| Executor / WHO | Tested executor identity/binding prevents several modeled substitutions | H11 second-/third-order evidence | PARTIALLY SUPPORTED | UNTESTED PENDING ACTUAL AiRP | Production IAM/KMS/HSM trust and registry lifecycle not demonstrated |
| Route closure | Direct and alternate represented writers meet the modeled protected sink boundary | H11 route-closure tests | SUPPORTED WITH BOUNDARY | UNTESTED PENDING ACTUAL AiRP | Universal external EPR non-bypassability not demonstrated |
| Single-use execution authority | Shared modeled execution authority is consumed once across tested instances | H11 second-/third-order evidence | SUPPORTED WITH BOUNDARY | UNTESTED PENDING ACTUAL AiRP | Correlated rollback of all modeled trust domains can resurrect authority |
| Rollback resistance | Separate modeled consumption anchor resists rollback of the primary store alone | H11 third-order evidence | PARTIALLY SUPPORTED | UNTESTED PENDING ACTUAL AiRP | Correlated rollback of primary + anchor remains NOT DEMONSTRATED |
| Trust-anchor availability | Some missing/mismatched trust conditions fail closed | H11 third-order evidence | PARTIALLY SUPPORTED | UNTESTED PENDING ACTUAL AiRP | Loss/recreation of the consumption anchor for an outstanding capability remains NOT DEMONSTRATED |
| Consequence outcome | Local model can record represented COMMITTED outcome | H11 model | PARTIALLY SUPPORTED | UNTESTED PENDING ACTUAL AiRP | Cannot distinguish actual external consequence CONFIRMED from UNRESOLVED without external protocol |
| Evidence/reconstruction | Verification chain retains explicit test outcomes and failure/remediation history | HARDEN evidence documents and CI history | SUPPORTED WITH BOUNDARY | UNTESTED PENDING ACTUAL AiRP | Production evidence custody/provenance depends on deployment architecture |
| AiRP risk activation | FlowSignal can consume runtime context but does not determine ORCHA's proprietary AiRP risk activation | No official AiRP questionnaire available | OUT OF SCOPE | UNTESTED PENDING ACTUAL AiRP | Requires actual AiRP beta/test access |
| Model quality, hallucination, bias, clinical efficacy, model drift | No FlowSignal assurance claim | Explicit scope boundary | OUT OF SCOPE | UNTESTED PENDING ACTUAL AiRP | Must be addressed by other assurance controls/framework elements |

## Executable AIRP-002 result

GitHub Actions run **35496406525**:

- baseline verification: PASS;
- H11 third-order durable boundary: PASS;
- **AIRP-002 worked evidence case: PASS**;
- H11 fourth-order trust-boundary: FAIL, intentionally preserved as the external-boundary finding.

The workflow-level failure must not be reported as an AIRP-002 failure. AIRP-002's own job completed successfully.

## Preserved external-boundary findings

Four properties remain deliberately unresolved rather than being simulated into a green result:

1. correlated rollback resistance across all relevant trust domains;
2. independently administered production executor identity/key trust;
3. safe semantics when the independent consumption anchor is lost/recreated;
4. external consequence confirmation, including explicit CONFIRMED versus UNRESOLVED outcome.

Classification for these properties: **NOT DEMONSTRATED beyond the reference-model boundary**.

## What this can support in an ORCHA discussion

The evidence supports investigating whether runtime authority controls could be relevant as a structural mitigation for a subset of AiRP-activated risks where authority may change between approval and consequential execution.

It also supplies explicit residual-gap evidence rather than treating a successful local control test as complete assurance.

## What this cannot support

**No FlowSignal evidence status in this table is an AiRP finding. AiRP relevance remains UNTESTED until actual ORCHA/AiRP evidence exists.**

This matrix must not be represented as:
- an official AiRP assessment;
- an ORCHA pass, certification or endorsement;
- evidence that FlowSignal addresses all AiRP risks;
- evidence of production EPR non-bypassability;
- proof of physical non-formation in a real clinical system;
- proof that ORCHA will recognise any specific FlowSignal control as a mitigation.

## Beta decision rule

When the actual AiRP is available, replace assumptions with the real feature blocks/questions. For each applicable item record:

**AiRP item → activated risk → required/recognised mitigation → FlowSignal evidence → observed result → residual gap → SUPPORTED / PARTIALLY SUPPORTED / NOT SUPPORTED / FALSIFIED / OUT OF SCOPE.**

Contradictory results are retained. The FlowSignal hypothesis is narrowed or falsified if the actual AiRP evidence requires it.
