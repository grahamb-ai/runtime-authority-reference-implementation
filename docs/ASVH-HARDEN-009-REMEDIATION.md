# ASVH-HARDEN-009 — Hostile Review & Remediation Record

Status: VERIFICATION-EVIDENCED WITHIN DECLARED REFERENCE-HARNESS BOUNDARY

## 1. Scope

HARDEN-009 tests distributed execution-authority fencing, stale-replica promotion, split-brain conflict handling, failover and pre-consequence re-establishment of authority inside the ASVH reference harness.

It does not demonstrate production consensus, linearizability, real network-partition tolerance, quorum durability, cloud failure-domain independence or real EPR non-bypassability.

## 2. Frozen baseline

The frozen H9-001 through H9-020 conformance suite passed on the first executable workflow run while HARDEN-001 through HARDEN-008 regressions remained green.

Baseline / first hostile workflow run: `34611995061`
Commit under test: `7909dd8185168ac0596492f2812db6ac012c4a11`

## 3. Preserved hostile findings

### HC-H9-FR-001 — Pre-consequence observation node substitution

A node that had legitimately established distributed execution authority could pass an observation belonging to a different node into `pre_consequence_check` and still receive `ACTIVE`.

Risk: consequence formation could rely on state evidence not bound to the execution-authoritative node.

### HC-H9-FR-002 — Pre-consequence lease substitution

A node could pass an observation carrying a different lease identity while the grant itself matched the current distributed fence and still receive `ACTIVE`.

Risk: stale or unrelated lease evidence could be mixed with a currently valid grant immediately before consequence formation.

### HC-H9-FR-003 — Impossible negative replica age accepted

A negative replica age such as `-999` seconds was treated as fresher than the maximum-age threshold and therefore allowed activation.

Risk: malformed freshness evidence could become permissive.

### HC-H9-FR-004 — Pre-consequence observation authority-epoch substitution

The pre-consequence path checked the grant against the accepted distributed authority epoch but did not verify that the accompanying observation carried the same epoch.

Risk: evidence from a different distributed authority generation could be mixed into a current consequence-formation check.

All four failures were preserved in workflow run `34611995061`.

## 4. First remediation

Commit: `0711e13473aa4c414b8e055d1de1d29f59e41dca`

Changes:

- bound pre-consequence observations to the executing node identity;
- bound pre-consequence observations to the grant lease identity;
- bound pre-consequence observations to the grant authority epoch;
- added strict freshness/counter validation;
- rechecked observation freshness and future time at consequence formation.

Re-verification run: `34612112352`

Result:

- HARDEN-001 through HARDEN-009 conformance: PASS;
- three of four hostile findings: PASS;
- HC-H9-FR-003 remained unresolved because negative replica age became `INDETERMINATE` rather than the frozen hostile expectation `PREVENTED`.

The residual failure was preserved rather than reclassified away.

## 5. Final remediation

Commit: `217a2e6978da26232b0d658e9eacc25a0d3db4b3`

Impossible negative replica age is now explicitly rejected as `PREVENTED` before general malformed-evidence handling. The same rule is applied at activation and pre-consequence fencing.

Final verification run: `34612238586`

Result:

- HARDEN-001 regression: PASS
- HARDEN-002 regression: PASS
- HARDEN-003 regression: PASS
- HARDEN-004 regression: PASS
- HARDEN-005 regression: PASS
- HARDEN-006 regression: PASS
- HARDEN-007 regression: PASS
- HARDEN-008 regression: PASS
- HARDEN-009 frozen H9-001 through H9-020: PASS
- HARDEN-009 hostile review: PASS

## 6. Resulting bounded claim

> Within the declared ASVH reference-harness boundary, execution authority is fenced by a monotonic distributed authority epoch and current lease identity. A stale, superseded or conflicting Runtime Authority node cannot remain execution-authoritative solely because it is locally healthy or holds a cached prior grant. Leadership promotion does not override stale state or policy position, and node, lease, authority-epoch and freshness evidence are re-bound immediately before consequence formation.

## 7. Explicit non-claims

This evidence does not establish:

- a production consensus algorithm;
- linearizable distributed storage;
- quorum-based fencing in a real cluster;
- Byzantine fault tolerance;
- real cloud-region or availability-zone isolation;
- real network partition behaviour;
- production cryptographic lease issuance;
- external timestamp authority;
- NHS deployment;
- real EPR route closure or non-bypassability.

HARDEN-009 therefore demonstrates reference-model distributed authority semantics, not production distributed-systems proof.
