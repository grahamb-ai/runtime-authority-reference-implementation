# ASVH-HARDEN-010 — Authority Dependency Convergence

Status: ATTACK FREEZE — PRE-REMEDIATION

Parent baseline: `asvh-harden-009-baseline` @ `ef7d752575e47e1e22716c71656cf99bc08ef315`

Working branch: `asvh-harden-010-authority-convergence`

## Proposition under test

A technically fresh aggregate standing snapshot MUST NOT be sufficient for consequence formation where a required underlying authoritative dependency has advanced to a conflicting, withdrawn, superseded, or indeterminate state.

A successful convergence check MUST NOT itself create durable authority to commit if authoritative standing changes before consequence formation.

## Attack classes

1. Fresh aggregate / changed authoritative dependency.
2. Multiple individually fresh authority sources disagree.
3. Positive aggregate or lower-precedence source attempts to outvote prohibition or indeterminacy.
4. Aggregate sequence is newer than dependency sequence but does not represent dependency standing.
5. Authority changes after convergence verification but before consequence formation (TOCTOU).

## Frozen hostile cases

- H10-001 fresh aggregate vs product SUSPENDED.
- H10-002 fresh aggregate vs product REVOKED.
- H10-003 fresh aggregate vs product UNKNOWN.
- H10-004 higher aggregate sequence vs product REVOKED.
- H10-005 product REVOKED + deployment VALID + aggregate AUTHORISED.
- H10-006 product SUSPENDED + deployment VALID + aggregate AUTHORISED.
- H10-007 product UNKNOWN cannot be outvoted by two positive sources.
- H10-008 very high aggregate sequence cannot outvote authoritative revocation.
- H10-009 revocation after convergence and before commit.
- H10-010 suspension after convergence and before commit.
- H10-011 indeterminate/unknown standing after convergence and before commit.

## Failure condition

HARDEN-010 fails if any tested path permits ALLOW/COMMITTED solely because an aggregate or other positive observation is fresh while a required authoritative dependency is prohibitive, indeterminate, unresolved, or has changed after the last authoritative bind.

## Evidence discipline

These hostile tests are frozen before remediation. Failure-first results are to be preserved. Remediation must not rewrite the hostile assertions to obtain green. HARDEN-001 through HARDEN-009 remain unchanged.

## Claim boundary

HARDEN-010 is a reference-implementation attack. It does not demonstrate production NHS deployment, real EPR non-bypassability, regulator acceptance, completeness of any real-world authority-source hierarchy, or atomic integration with an external registry. Any later green result is bounded to the implemented test model and evidence produced by the repository CI.
