# ASVH Whole-Stack Hostile Review — HARDEN-001 through HARDEN-009

Status: FROZEN HOSTILE REVIEW SPECIFICATION

## Purpose

This review tests the interaction of controls already demonstrated separately in HARDEN-001 through HARDEN-009. It is specifically designed to find failures that are invisible when each hardening layer is tested in isolation.

The review does not expand the external claim boundary. It remains a reference-harness exercise and does not demonstrate production NHS/EPR non-bypassability, consensus, external truth, production cryptographic trust, or deployment security.

## Whole-stack safety rule

A simulated governed consequence may form only when all decisive layers required for that consequence remain simultaneously admissible at the execution boundary. A lower layer SHALL NOT silently convert an upstream PREVENTED, REVALIDATE or INDETERMINATE condition into execution.

## Cross-layer invariants

WS-I01 — A valid Protected Clinical Bind is necessary but not sufficient for whole-stack execution.

WS-I02 — A fenced or non-current distributed execution authority cannot form a consequence through a locally healthy deployment enforcer.

WS-I03 — A policy transition requiring REVALIDATE or INVALIDATE prevents use of authority issued under the old policy basis.

WS-I04 — Failed or indeterminate present standing prevents consequence formation.

WS-I05 — The exact commit presented at the deployment boundary must remain the same commit bound by the outstanding authority context.

WS-I06 — Bind temporal validity must still hold at the final whole-stack execution decision.

WS-I07 — Deployment profile and route validity cannot override an upstream authority failure.

WS-I08 — Break-glass replay protection must survive a local enforcer replacement within the declared reference process when a shared replay authority is configured.

WS-I09 — A missing decisive upstream result is INDETERMINATE/PREVENTED, never implicitly ALLOW.

WS-I10 — Whole-stack evidence must preserve which decisive layer prevented or admitted execution.

## Frozen hostile scenarios

WS-001 — Locally valid bind + distributed authority PREVENTED => whole-stack PREVENTED.
WS-002 — Locally valid bind + distributed authority INDETERMINATE => whole-stack PREVENTED/INDETERMINATE, never FORMED.
WS-003 — Locally valid bind + policy transition INVALIDATE => whole-stack PREVENTED.
WS-004 — Locally valid bind + policy transition REVALIDATE => whole-stack PREVENTED until fresh authority exists.
WS-005 — Locally valid bind + present standing PREVENTED => whole-stack PREVENTED.
WS-006 — Locally valid bind + present standing INDETERMINATE => no consequence.
WS-007 — Expired bind presented to otherwise-valid deployment route => no consequence.
WS-008 — Bind/commit policy basis mismatch => no consequence.
WS-009 — Missing distributed authority result => no consequence.
WS-010 — Missing policy-transition result where policy transition checking is required => no consequence.
WS-011 — Missing present-standing result where continuity checking is required => no consequence.
WS-012 — Upstream failures must be reflected in whole-stack evidence rather than reported as deployment success.
WS-013 — A newer distributed authority epoch fences an older execution context even if the old bind remains locally valid.
WS-014 — Break-glass override is not allowed to bypass distributed fencing.
WS-015 — Break-glass override is not allowed to bypass an incompatible policy transition.
WS-016 — Same exact commit under a superseded policy basis requires fresh authority rather than reuse of the previous bind.

## Baseline discipline

The first executable whole-stack run is retained. Any failures are evidence. Remediation must not delete, rename away, or silently weaken a hostile scenario.

## Exit gate

The whole-stack review is complete only when:

1. HARDEN-001 through HARDEN-009 regression suites remain green;
2. all frozen WS scenarios pass;
3. first-run failures and remediation are documented;
4. no claim is made beyond the declared reference-harness boundary.

Permitted claim after successful completion:

> Within the declared ASVH reference-harness boundary, independently demonstrated controls from exact-consequence binding, continuity, consequence evidence, evidence contracts, deployment enforcement, recovery, evidence integrity, policy transition and distributed authority are composed so that an upstream PREVENTED, REVALIDATE or INDETERMINATE condition cannot be silently converted into a simulated governed consequence by a lower execution layer.
