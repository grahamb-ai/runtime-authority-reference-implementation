# ASVH-HARDEN-005 — Deployment Enforcement, Route Closure & Contract Authority

Status: FROZEN SPECIFICATION — implementation not yet hostile-verified

## Purpose
HARDEN-005 tests the bounded claim that a governed clinical consequence cannot form inside the declared reference deployment boundary through an execution route that has not passed the protected authority path.

It also tests that the ControlContract and deployment-boundary profile used to decide what is permitted cannot be silently substituted, downgraded or bypassed inside the harness.

## Boundary
This work concerns the ASVH reference harness and simulator only. It does not establish real NHS/EPR non-bypassability, network isolation, supplier route closure, production key management, or production break-glass governance.

## Core invariants
H5-I01 Every route capable of forming the governed simulator consequence is declared in the deployment boundary profile.
H5-I02 Every declared governed route must traverse the protected executor before consequence formation.
H5-I03 An undeclared route cannot form the governed consequence inside the harness boundary.
H5-I04 Route identity is bound to its target capability, not merely a caller-supplied route label.
H5-I05 The active deployment-boundary profile is versioned and authoritative.
H5-I06 A stale/downgraded boundary profile cannot silently replace the active profile.
H5-I07 The active ControlContract set is version-bound to the deployment profile.
H5-I08 A caller cannot expand permitted evidence sources by substituting a permissive contract.
H5-I09 Break-glass is a separate authority domain and never rewrites the original Runtime Authority decision.
H5-I10 Break-glass capability has explicit scope, expiry and reuse semantics.
H5-I11 Break-glass execution produces separate evidence identifying the override authority and original decision.
H5-I12 A protected execution capability remains exact-consequence bound under the deployment profile.
H5-I13 Alternate simulator commit APIs are either protected or demonstrably outside the governed consequence boundary.
H5-I14 Enforcement failure is explicit; it never silently becomes permission.
H5-I15 Route closure claims identify the exact interfaces covered.

## Reference deployment profile
The harness profile SHALL identify:
- profile_id
- profile_version
- deployment_id
- governed_consequence_type
- active_control_contract_version
- protected_routes
- target_capability bindings
- break_glass_policy_version
- profile_integrity/authenticity state

## Frozen conformance vectors
H5-001 protected primary route with valid protected capability -> consequence may form.
H5-002 undeclared route -> PREVENTED.
H5-003 declared route without protected bind -> PREVENTED.
H5-004 declared route with mismatched exact commit -> PREVENTED.
H5-005 route label correct but target capability differs -> PREVENTED.
H5-006 target capability correct but route label undeclared -> PREVENTED.
H5-007 stale deployment profile version -> PREVENTED.
H5-008 wrong deployment_id profile -> PREVENTED.
H5-009 wrong active ControlContract version -> PREVENTED.
H5-010 permissive substituted ControlContract not authorised by active profile -> PREVENTED.
H5-011 boundary profile integrity/authenticity failure -> PREVENTED.
H5-012 enforcement component unavailable -> PREVENTED/INDETERMINATE according to frozen failure mode; never FORMED by fallback.
H5-013 break-glass absent -> normal REFUSE remains non-executable.
H5-014 valid scoped break-glass may form only the authorised exact consequence.
H5-015 break-glass for different patient/commit -> PREVENTED.
H5-016 expired break-glass -> PREVENTED.
H5-017 break-glass replay after single use -> PREVENTED.
H5-018 break-glass evidence preserves original REFUSE and override identity.
H5-019 alternate target API capable of same governed consequence but not routed through enforcement -> test MUST fail the route-closure claim until brought inside boundary or explicitly excluded.
H5-020 route-closure evidence lists exact protected interfaces and observed consequence count.

## Exit criteria
HARDEN-005 is not verification-evidenced unless all frozen tests pass, hostile testing passes, HARDEN-001..004 regressions stay green, failures are preserved, and the permitted claim remains explicitly boundary-relative.

## Permitted claim after PASS
Within the declared ASVH reference-harness deployment boundary, every interface declared capable of forming the governed simulated clinical documentation consequence is required to traverse protected enforcement or is demonstrated unable to form that governed consequence. Deployment profile and ControlContract versions are bound to enforcement, and break-glass is represented as a separate, scoped authority domain with preserved original decision evidence.

## Non-claims
A PASS does not establish real NHS EPR route closure, supplier integration closure, production network enforcement, production IAM, production cryptographic trust, production break-glass governance, or external non-formation beyond the simulator boundary.
