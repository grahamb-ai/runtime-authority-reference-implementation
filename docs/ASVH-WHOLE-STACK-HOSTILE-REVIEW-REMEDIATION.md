# ASVH Whole-Stack Hostile Review — Failure & Remediation Record

## Scope

This record covers the cross-layer hostile review of HARDEN-001 through HARDEN-009 on branch `asvh-whole-stack-hostile-review`.

The objective was to test whether independently passing hardening layers compose safely, rather than assuming that isolated conformance implies whole-system conformance.

## Baseline run

Workflow run: `34612640568`

Commit under test: `f149dc36b065bde4f3d4daffe812e8d8ad74da7b`

Regression result:

- HARDEN-001 through HARDEN-009: PASS

Whole-stack hostile result:

- 15 FAILED
- 1 PASSED

The failures were not failures of the individual hardening layers. They exposed a composition gap: the initial whole-stack coordinator delegated directly to DeploymentEnforcer and did not make upstream authority states decisive at the final consequence boundary.

## Preserved findings

### WS-FR-001 — Distributed PREVENTED was ignored

A locally valid protected bind and route could still produce `FORMED` even when distributed authority was `PREVENTED`.

### WS-FR-002 — Distributed INDETERMINATE was ignored

A lower deployment layer could convert unavailable/indeterminate distributed authority into simulated consequence formation.

### WS-FR-003 — Policy INVALIDATE was ignored

Outstanding authority could still reach the deployment layer after policy-transition semantics said it was invalidated.

### WS-FR-004 — Policy REVALIDATE was ignored

Authority requiring a fresh determination could still be used by the deployment layer.

### WS-FR-005 — Present-standing PREVENTED was ignored

A locally valid bind remained sufficient for deployment formation despite failed present standing.

### WS-FR-006 — Present-standing INDETERMINATE was ignored

Unknown current standing could be silently converted into execution.

### WS-FR-007 — Expired protected bind accepted by composition path

DeploymentEnforcer itself checks exact commit binding but does not own the complete bind lifecycle. The initial composition path failed to re-establish bind temporal validity before final enforcement.

### WS-FR-008 — Protected-bind policy basis mismatch accepted by composition path

A bind with a changed runtime policy version but the same commit binding hash could reach deployment formation because cross-layer policy-basis consistency was not re-established.

### WS-FR-009 / 010 / 011 — Missing decisive upstream results defaulted effectively to local execution

Absent distributed, policy-transition, or present-standing results did not prevent deployment formation.

### WS-FR-012 — Evidence named the wrong decisive layer

When upstream authority had failed, the evidence still reported `DEPLOYMENT` as decisive because upstream results were not part of the composed decision.

### WS-FR-013 — Newer distributed authority epoch did not fence the composed execution context

The old context could still reach deployment formation despite a newer current epoch.

### WS-FR-014 — Break-glass bypassed distributed fencing at composition level

A valid break-glass override could form a simulated consequence even when distributed execution authority was PREVENTED.

### WS-FR-015 — Break-glass bypassed incompatible policy transition at composition level

Break-glass deployment semantics were valid locally, but the whole stack had not first made policy-transition compatibility decisive.

### WS-016

The exact-commit binding already prevented reuse of an old bind against a materially changed policy-basis commit. This scenario passed in the baseline.

## Root cause

The isolated controls were individually effective, but there was no explicit final composition rule requiring all decisive authority layers to be simultaneously admissible immediately before deployment enforcement.

The core error was therefore architectural composition, not a defect in any one preceding hardening layer.

## Remediation

Commit: `87bf342213825e815f466992cfd947fb03b81785`

`WholeStackExecutionCoordinator` now makes the following conditions decisive before delegation to DeploymentEnforcer:

1. distributed execution authority must be present and `ACTIVE`;
2. distributed authority epoch must equal the current epoch;
3. policy-transition state must be present and `ALLOW`;
4. `REVALIDATE`, `INVALIDATE`, `INDETERMINATE` and absent policy states cannot fall through to execution;
5. present standing must be present and `ALLOW`;
6. normal ALLOW execution revalidates bind temporal validity;
7. protected bind, authority context and exact commit must agree on runtime policy and rule-catalogue basis;
8. break-glass does not bypass distributed fencing or incompatible policy-transition semantics;
9. whole-stack evidence records the actual decisive layer.

The coordinator remains a reference composition boundary. It is not claimed to be a production distributed transaction manager or real EPR enforcement mechanism.

## Re-verification

Workflow run: `34612758051`

Commit under test: `87bf342213825e815f466992cfd947fb03b81785`

Results:

- HARDEN-001 regression: PASS
- HARDEN-002 regression: PASS
- HARDEN-003 regression: PASS
- HARDEN-004 regression: PASS
- HARDEN-005 regression: PASS
- HARDEN-006 regression: PASS
- HARDEN-007 regression: PASS
- HARDEN-008 regression: PASS
- HARDEN-009 regression: PASS
- frozen whole-stack hostile review WS-001 through WS-016: PASS

## Bounded conclusion

The whole-stack review demonstrated an important distinction: passing component controls did not initially prove safe composition. Fifteen cross-layer failures were found despite all nine hardening suites remaining green.

After remediation, within the declared ASVH reference-harness boundary, upstream distributed authority, policy-transition and present-standing failures are decisive at the final composed execution boundary and cannot be silently converted into a simulated governed consequence by the deployment layer.

## Non-claims

This evidence does not demonstrate:

- production NHS/EPR non-bypassability;
- production consensus or linearizability;
- atomic commitment across external services;
- production cryptographic identity/trust;
- real NHS authoritative evidence sources;
- external clinical truth;
- production break-glass governance;
- network-partition correctness beyond the bounded reference model;
- real consequence formation in a clinical system.
