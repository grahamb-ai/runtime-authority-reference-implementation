# ASVH Whole-Stack Hostile Review — Pass 2

Status: REMEDIATED / RE-VERIFIED

## Purpose

After the first whole-stack review composed distributed authority, policy transition, present standing, protected-bind validity and deployment enforcement, a second hostile pass tested whether HARDEN-004 evidence-contract outcomes and HARDEN-006 recovery-authority outcomes were also decisive at the final execution boundary.

## Preserved failure

Workflow run `34613453173` preserved the first executable second-pass result.

HARDEN-001 through HARDEN-009 regressions remained green. The original whole-stack WS-001..WS-016 suite also remained green. The new second-pass hostile suite failed 8/8 scenarios:

- WS2-001 recovery PREVENTED was ignored and consequence FORMEd;
- WS2-002 recovery INDETERMINATE was ignored and consequence FORMEd;
- WS2-003 missing recovery result was ignored and consequence FORMEd;
- WS2-004 evidence-contract REFUSE was ignored and consequence FORMEd;
- WS2-005 evidence-contract ESCALATE was ignored and consequence FORMEd;
- WS2-006 missing evidence-contract result was ignored and consequence FORMEd;
- WS2-007 break-glass could form despite recovery PREVENTED;
- WS2-008 break-glass could form despite evidence-contract REFUSE.

### Finding HC-WS2-FR-001 — Incomplete whole-stack composition

The first WholeStackExecutionCoordinator did not consume HARDEN-004 or HARDEN-006 outcomes. Individually verified controls therefore remained non-decisive at the final execution composition point.

This was a composition failure, not a failure of the underlying HARDEN-004 or HARDEN-006 component tests.

## Remediation

The whole-stack authority context now explicitly carries:

- `recovery_authority_status`;
- `evidence_contract_status`.

The coordinator treats recovery authority as a prerequisite:

- ACTIVE may continue;
- PREVENTED blocks;
- INDETERMINATE remains indeterminate;
- missing result remains indeterminate.

The coordinator treats contracted evidence as a prerequisite:

- ALLOW may continue;
- ESCALATE prevents direct consequence formation;
- REFUSE prevents consequence formation;
- INDETERMINATE remains indeterminate;
- missing result remains indeterminate.

These prerequisites apply to both normal and break-glass paths. Break-glass remains a separate authority domain but does not erase missing or adverse recovery/evidence state.

The original whole-stack fixture was extended only to supply explicit valid recovery/evidence states (`ACTIVE` / `ALLOW`) for scenarios that were already intended to represent an otherwise-valid path; original WS assertions were not weakened.

## Re-verification

Workflow run `34613614946`:

- HARDEN-001 through HARDEN-009 regression: PASS;
- original whole-stack WS-001..WS-016: PASS;
- second-pass WS2-001..WS2-008: PASS.

Remediation implementation commit: `8fc10aabd4e4cd02274c539e10ec040458befa0f`.

## Bounded conclusion

Within the declared ASVH reference-harness boundary, recovery-authority and contracted-evidence outcomes are now composed as decisive execution prerequisites alongside distributed authority, policy transition, present standing, protected-bind validity and deployment enforcement. A lower execution layer or break-glass path cannot silently convert an adverse, missing or indeterminate recovery/evidence result into a simulated governed consequence.

## Non-claims

This does not demonstrate production NHS/EPR non-bypassability, production consensus, external evidence truth, external recovery-anchor isolation, production atomic transactions, or real clinical consequence formation.
