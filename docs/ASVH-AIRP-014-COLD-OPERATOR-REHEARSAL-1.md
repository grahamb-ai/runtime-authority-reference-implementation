# ASVH-AIRP-014 — Cold Operator Rehearsal 1

**Status:** COMPLETED — DOCUMENTARY DEFECTS FOUND  
**Date:** 2026-09-20  
**Operator posture:** reviewer following AIRP-013 without relying on undocumented navigation knowledge  
**Reference run:** 35500425335

## Method

Follow AIRP-013 in order and verify that every required repository artefact and every named CI job can be reached and that the displayed evidence supports the spoken script.

This is a documentation/usability rehearsal, not a new runtime-authority engineering test.

## Verified

All required repository artefacts exist on branch `asvh-harden-011-from-225-baseline`:

- AIRP-010 closure;
- AIRP-003 evidence/gap matrix;
- AIRP-002 executable case;
- AIRP-006 executable case;
- AIRP-008 executable case;
- AIRP-009 executable case;
- AIRP-001 mapping;
- AIRP-012 runbook;
- AIRP-013 operator pack.

Reference run 35500425335 is complete and contains:

- verify — success;
- third-order-durable-boundary — success;
- airp-002-worked-case — success;
- airp-006-composition-challenge — success;
- airp-008-direct-enforcement — success;
- airp-009-standing-dependency — success;
- fourth-order-trust-boundary — failure, intentionally preserved.

## Finding OP-01 — navigation still assumes GitHub familiarity

AIRP-013 gives paths and tab order but not direct browser links. A genuinely cold operator must know how to navigate repository branches, file paths and Actions runs.

**Classification:** usability defect.

**Correction:** add direct branch-pinned links for every required tab and the reference Actions run.

## Finding OP-02 — AIRP-003 is stale relative to the final evidence chain

AIRP-013 asks the operator to open AIRP-003, but AIRP-003 still foregrounds AIRP-002/run 35496406525 and predates the final AIRP-006/008/009 evidence.

It is not false, but a cold operator could reasonably wonder why the matrix does not reflect the evidence later presented as final.

**Classification:** documentary consistency defect.

**Correction:** update AIRP-003 with the final reference run and distinguish:
- AIRP-002 state-change evidence;
- AIRP-006 composition evidence;
- AIRP-008 protected-boundary enforcement after preserved failure/remediation;
- AIRP-009 mandatory/exact-typed standing dependency after preserved failure/remediation.

## Finding OP-03 — operator needs a fixed screen-state cue before speaking

The pack says what to point to but does not consistently identify a heading or stable visual anchor before each spoken segment.

**Classification:** minor usability defect.

**Correction:** add direct links plus heading/job-name anchors. Screenshots are deliberately not frozen because GitHub UI presentation can change while repository paths and run/job names remain the evidential identifiers.

## Rehearsal decision

**NOT YET HANDOVER-COMPLETE.**

No runtime-control defect was found. Correct OP-01 through OP-03 and repeat the cold navigation check.

The first rehearsal finding is preserved rather than silently editing the operator pack.
