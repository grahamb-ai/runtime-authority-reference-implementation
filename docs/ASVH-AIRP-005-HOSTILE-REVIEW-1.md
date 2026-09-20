# ASVH-AIRP-005 — Hostile Review 1: AiRP 001–004 Package

**Status:** RED findings preserved before remediation  
**Date:** 2026-09-20  
**Object under test:** ASVH-AIRP-001 through ASVH-AIRP-004  
**Method:** claim-by-claim challenge for source fidelity, evidence provenance, falsifiability, internal consistency and boundary inflation.

## Result

**PACKAGE NOT YET READY FOR EXTERNAL PRESENTATION.**

The package is directionally disciplined, but this first hostile review found material weaknesses that should be corrected before it is shown as a technical evidence package to ORCHA.

This finding is preserved before remediation.

## RED-01 — AiRP public-source provenance is missing

AIRP-001 states current facts about ORCHA's public methodology but does not record the exact source URL, access date or quoted/source-controlled wording used to derive the six-stage mapping.

This creates an avoidable provenance gap. A later ORCHA wording change could make it impossible to reconstruct what public material the mapping was based on.

**Failure condition:** a reviewer cannot reproduce the external-framework input from the artefact alone.

**Classification:** FAIL — documentary provenance.

**Required correction:** freeze the exact public ORCHA source references and access date; distinguish ORCHA wording from FlowSignal shorthand.

## RED-02 — “independently testable” is stronger than the current evidence

AIRP-001/004 use “independently testable runtime control and evidence mechanism.”

The repository is public/testable, but AIRP-002 was executed in FlowSignal's own GitHub environment. No independent third party has yet executed or verified AIRP-002.

**Failure condition:** wording can be read as independent verification rather than testability in principle.

**Classification:** FAIL — claim ambiguity.

**Required correction:** use “externally reproducible/testable in principle” or equivalent until an independent party actually runs it.

## RED-03 — AIRP-002 does not exercise the H11 protected execution sink

AIRP-002 evaluates T0 and T1 with `consequence_time_converge`, then conditionally appends to a local Python list only if T1 is ACTIVE.

That proves the state-change determination property, but it does not itself pass through the H11 execution gateway/protected sink.

Therefore “represented clinical-record commit not formed” is true only for the AIRP-002 local representation, not evidence that AIRP-002 exercised route closure or execution consumption.

**Failure condition:** AIRP-002 may be presented as an end-to-end execution-boundary test when it is currently a determination-to-local-list test.

**Classification:** FAIL — evidence composition gap.

**Required correction:** either narrow AIRP-002 wording to “no local represented commit branch was reached” or create a second executable case that composes the state-change determination with the existing protected execution boundary without changing either mechanism to obtain a pass.

## RED-04 — Clinical “consent/authority dependency” is semantically conflated

AIRP-002 models one dependency as `consent-authority` and describes it as “consent/authority.” Consent status and delegated execution authority are not automatically the same concept.

Without a frozen NHS guidance trace for this exact rule, the example risks implying that WITHDRAWN consent maps directly and universally to loss of authority to commit documentation.

**Failure condition:** clinical/legal semantics are inferred from a synthetic engineering state.

**Classification:** FAIL — domain-semantics overreach.

**Required correction:** label it explicitly as a **synthetic guidance-derived runtime condition** and avoid asserting a universal NHS consent rule unless traced to the exact source.

## RED-05 — AIRP-001 says “all ten AiRP standard risks” without freezing the ten-risk taxonomy

Current ORCHA public material says the profiler determines which of 10 standard/canonical risks are activated, but AIRP-001 does not name or source those risks.

The package correctly avoids claiming coverage, but the phrase still depends on an external taxonomy that is not frozen in the evidence package.

**Failure condition:** reviewer cannot determine what “all ten” refers to from the artefact.

**Classification:** FAIL — incomplete external reference.

**Required correction:** either source/freeze the taxonomy if publicly available or simply say “the risks activated by AiRP” and avoid implying knowledge of proprietary detail.

## RED-06 — 246 passing checks can be misread as AIRP evidence volume

AIRP-001/004 mention 246 passing checks. Those checks belong to the broader ASVH hardening chain, not 246 AiRP tests.

The documents mostly qualify this, but in a live demonstration the number is vulnerable to accidental inflation.

**Failure condition:** a listener can reasonably infer “246 checks against AiRP.”

**Classification:** FAIL — presentation ambiguity.

**Required correction:** always say “246 reference-model verification checks in the underlying ASVH hardening chain; not 246 AiRP checks.”

## RED-07 — AIRP-003 mixes evidence classifications with framework-fit classifications

The matrix uses SUPPORTED WITH BOUNDARY / PARTIALLY SUPPORTED for technical evidence rows while also discussing potential AiRP relevance.

A reader can confuse “FlowSignal technically demonstrated this property” with “AiRP recognises this property as a mitigation.”

**Failure condition:** technical evidence status and AiRP fit status are not orthogonal.

**Classification:** FAIL — classification design.

**Required correction:** split into two columns:
1. **FlowSignal evidence status**;
2. **AiRP relevance status** = UNTESTED / pending actual AiRP unless ORCHA evidence exists.

## RED-08 — AIRP-004 closing question presupposes an AiRP “feature” already under assessment

The closing question says “risks it activates in this feature.” The package has defined a FlowSignal feature under examination, but ORCHA has not yet accepted that exact feature decomposition.

**Failure condition:** FlowSignal silently imposes its feature boundary on AiRP.

**Classification:** FAIL — framework assumption.

**Required correction:** ask ORCHA first how AiRP would decompose/classify the ambient-scribing capability, then ask whether runtime consequence-time control is recognised for any activated risk.

## RED-09 — “immediately before” remains an architectural assertion, not an external timing proof

AIRP-001/004 describe FlowSignal as operating immediately before the represented consequence. That is accurate for the modeled boundary, but no production EPR integration establishes actual temporal/transactional adjacency.

**Failure condition:** modeled placement is heard as deployed placement.

**Classification:** FAIL — deployment-boundary ambiguity.

**Required correction:** consistently say “at the modeled pre-consequence boundary” until an external integration proves placement.

## RED-10 — The comparator is too weak to test incremental control value

AIRP-002 correctly refuses to claim that a real EPR would write without FlowSignal. However, its comparator simply evaluates the earlier and current states separately. It does not model a defined baseline architecture lacking consequence-time revalidation.

That means AIRP-002 demonstrates the FlowSignal property, but not the incremental difference against a specific alternative control architecture.

**Failure condition:** comparator is used to imply superiority over an undefined baseline.

**Classification:** FAIL — counterfactual insufficiency.

**Required correction:** keep the current nonclaim and, if useful, define a separate explicit baseline experiment whose architecture and limitations are frozen before execution.

## What survived the attack

The following package disciplines held:
- AIRP-002 did not claim a real EPR would write without FlowSignal.
- AIRP-002's dedicated CI result is correctly separated from the intentionally RED H11 fourth-order job.
- AIRP-001/003/004 explicitly deny official AiRP assessment/certification/endorsement.
- The four external-boundary gaps are preserved rather than simulated away.
- Model quality, hallucination, bias, efficacy and drift are kept outside the FlowSignal claim.
- Actual AiRP is given authority to narrow or falsify the hypothesis.

## Remediation order

1. Freeze external ORCHA source provenance.
2. Correct “independently testable” language.
3. Separate technical evidence status from AiRP relevance status.
4. Correct synthetic clinical-condition semantics.
5. Narrow “immediately before” to modeled placement.
6. Decide whether AIRP-002 should remain a narrow determination test or be followed by an unchanged-mechanism composition test through the H11 protected sink.
7. Re-run hostile review against the corrected package.

No finding above should be deleted after remediation. Link each correction back to this preserved RED record.
