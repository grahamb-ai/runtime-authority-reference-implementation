# ASVH-HARDEN-008 — Policy Transition & Outstanding Authority

Status: FROZEN SPECIFICATION — implementation pending

## Purpose

HARDEN-008 tests what happens to already-issued authority artefacts when the active policy/rule/profile state changes before consequence formation.

The objective is to prevent outstanding authority from silently surviving a material policy transition merely because it was valid when originally issued.

## Core model

A protected authority artefact binds to:

- policy_id
- policy_version
- ruleset_version
- deployment_profile_id/version
- exact consequence binding
- issue time / expiry
- transition disposition

A PolicyTransition records:

- transition_id
- from_policy_version
- to_policy_version
- effective_at
- transition_class
- outstanding_authority_semantics
- reason

Transition classes:

- NON_MATERIAL: outstanding authority may remain valid if explicitly declared compatible.
- REVALIDATE: outstanding authority cannot execute until revalidated under new state.
- INVALIDATE: outstanding authority is no longer executable.
- INDETERMINATE: transition semantics unavailable/ambiguous; execution must not proceed.

No implicit backward compatibility is permitted.

## Invariants

PT-I01 active policy identity/version is externally supplied to the transition gate.
PT-I02 an outstanding artefact cannot choose its own transition semantics.
PT-I03 exact version equality alone does not prove compatibility after a transition event.
PT-I04 material transition requires explicit REVALIDATE or INVALIDATE handling.
PT-I05 absent transition semantics fail explicitly.
PT-I06 a future-effective transition does not affect pre-effective execution, but applies at/after effective_at using trusted time.
PT-I07 malformed or contradictory transition state cannot become permissive.
PT-I08 revalidation creates a new authority basis; it does not mutate historical determination evidence.
PT-I09 invalidated artefacts cannot be resurrected by replaying the old policy version.
PT-I10 policy rollback cannot silently restore previously invalidated outstanding authority.
PT-I11 transition applies to exact bound deployment/profile and declared scope.
PT-I12 incompatible ruleset change is material even if policy version string is unchanged.
PT-I13 expiry remains independently enforceable.
PT-I14 transition decision is reconstructable from evidence.
PT-I15 break-glass is a separate authority domain and does not inherit normal transition compatibility automatically.

## Frozen tests H8-001..H8-020

H8-001 unchanged active policy allows still-valid outstanding authority.
H8-002 NON_MATERIAL explicitly compatible transition allows outstanding authority.
H8-003 NON_MATERIAL without explicit compatibility does not allow.
H8-004 REVALIDATE transition blocks old artefact pending revalidation.
H8-005 successful revalidation produces new authority basis bound to new policy state.
H8-006 INVALIDATE transition prevents old artefact.
H8-007 missing transition semantics returns INDETERMINATE/PREVENTED, never ALLOW.
H8-008 future-effective transition does not apply before effective_at.
H8-009 transition applies exactly at effective_at.
H8-010 caller-supplied time cannot bypass trusted transition time.
H8-011 ruleset change with same policy version requires transition handling.
H8-012 deployment/profile mismatch rejects transition reuse.
H8-013 old policy replay after invalidation cannot resurrect artefact.
H8-014 policy rollback after accepted newer state cannot resurrect artefact.
H8-015 expired authority remains prevented even if transition says compatible.
H8-016 contradictory transition records fail explicitly.
H8-017 malformed transition timestamp fails explicitly.
H8-018 historical Authority Receipt remains immutable after revalidation.
H8-019 break-glass does not inherit normal policy compatibility without separate semantics.
H8-020 deterministic same inputs/state/time produce same transition outcome.

## Hostile targets

- same policy version but changed ruleset
- downgrade/rollback to old policy
- duplicate transition IDs with different payloads
- transition effective-time manipulation
- broad transition scope replayed into another deployment
- compatibility asserted by requesting AI
- invalidated artefact replay after restart
- break-glass inheritance from normal authority

## Exit gate

HARDEN-008 is verification-evidenced only after H8-001..H8-020 pass, hostile review passes, H1-H7 regressions remain green, failures are preserved, and non-claims remain explicit.

Permitted bounded claim after successful completion:

> Within the declared ASVH reference-harness boundary, outstanding authority does not silently survive a material policy/ruleset transition. Compatibility, revalidation or invalidation semantics are explicit, time-bound and deployment-bound; rollback or replay of an older policy state cannot by itself resurrect previously invalidated authority.
