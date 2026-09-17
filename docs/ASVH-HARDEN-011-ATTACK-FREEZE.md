# ASVH-HARDEN-011 — Execution Route Closure / Non-Bypassability Attack Freeze

Status: ATTACK FREEZE — PRE-REMEDIATION

Base: HARDEN-010 final evidence-bounded closure at `6ff631858a255a037b8ff4228b41db7d6402f65a`.

## Purpose

HARDEN-010 deliberately left HC-H10-FR-041 / HR56 open: a complete validated consequence bind can reach an arbitrary Python callback which can ignore the bind and still return `COMMITTED`.

HARDEN-011 moves that residual into its own hardening stage. It does not reopen HARDEN-010's bounded reference-model conclusion.

## Frozen proposition

> A consequence-forming route MUST be structurally incapable of committing the protected consequence unless that exact execution attempt passes through the authoritative execution gateway and the gateway successfully consumes a complete, current, matching consequence bind.

Corollaries:

1. No direct protected commit route may exist outside the gateway.
2. Possession of a bind is not enough; the gateway must validate and consume it.
3. A bind for one execution attempt must not authorise another attempt.
4. A bind must not be reusable after successful consequence formation unless explicitly designed as multi-use authority and independently evidenced as such.
5. Failure, unavailability or ambiguity at the enforcement boundary must fail closed.
6. A callback, adapter or downstream writer must not be able to turn an unvalidated or unconsumed bind into a protected commit.
7. Reference-model route closure must not be described as production EPR non-bypassability without evidence from a concrete integration boundary.

## Attack classes

### H11-001 — Direct-route bypass
Attempt protected commit without invoking the authority gateway.

### H11-002 — Ignored-bind commit
Pass a valid bind to a downstream writer that ignores it and commits anyway.

### H11-003 — Missing-bind commit
Invoke the protected writer with no bind.

### H11-004 — Incomplete/forged-bind commit
Attempt commit with incomplete or fabricated binding material.

### H11-005 — Cross-attempt replay
Use a valid bind from attempt A to commit attempt B.

### H11-006 — Post-success replay
Reuse a previously consumed bind for a second protected consequence.

### H11-007 — Gateway failure/open bypass
Make gateway validation unavailable or raise an exception and test whether consequence formation remains possible.

### H11-008 — Alternate writer/adapter route
Introduce a second route to the protected sink which does not share the authoritative enforcement boundary.

### H11-009 — Check/consume split race
Validate a bind, mutate/revoke relevant authority before sink formation, then attempt commit without an atomic or equivalent revalidation/consumption boundary.

### H11-010 — Sink identity substitution
Use valid authority for one protected sink/target to form a different protected consequence.

## Evidence rule

First failure is evidence. No hostile proposition is to be weakened or rewritten merely to obtain green results. Any remediation must be added after the failure record is preserved.

## Claim boundary

A Python reference gateway can demonstrate route-closure properties only for routes represented inside that model. It cannot by itself demonstrate absence of unmodeled EPR APIs, administrator paths, vendor integrations, database writes or other production bypass routes.

Production non-bypassability requires evidence from the actual integration topology and protected consequence-forming interface.
