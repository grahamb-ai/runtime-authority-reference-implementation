# ASVH Whole-Stack Hostile Review — Pass 10

## Scope

Pass 10 tests break-glass single-use semantics across enforcer replacement and concurrent enforcer instances. It follows Pass 9, which established integrity binding for the break-glass authority artefact itself.

This pass is intentionally bounded to the ASVH reference harness. It does not claim production distributed consensus, external monotonic storage, NHS identity authority, or real EPR non-bypassability.

## Frozen hostile scenarios

- WS10-001: the same integrity-valid single-use break-glass authority must not form twice after enforcer/coordinator replacement.
- WS10-002: two enforcer instances concurrently attempting the same single-use break-glass authority must not both form the consequence.
- WS10-003: two distinct integrity-valid break-glass authorities with different override identifiers may each be consumed once.

## Preserved failure

Baseline workflow run: `34618439111`

HARDEN-001 through HARDEN-009 and whole-stack passes 1 through 9 remained green. Pass 10 failed 2 of 3 scenarios:

- `WS10-001` failed because a fresh enforcer had an empty in-memory consumed-override set and accepted the same override again.
- `WS10-002` failed because two independent enforcers each had private replay state and both accepted the same override concurrently.
- `WS10-003` passed.

### Finding HC-WS10-FR-001 — break-glass single-use state was instance-local

The break-glass artefact was integrity-bound after Pass 9, but its consumption state lived only in the `DeploymentEnforcer` process instance. Restart/replacement therefore reset replay protection, and independent enforcers could simultaneously treat the same override as unused.

This demonstrates again that artefact authenticity and single-use enforcement are separate properties.

## Remediation

### Durable reference replay state

`BreakGlassUseStore` was added as a SQLite-backed reference replay store. It atomically inserts a consumed `override_id` under `BEGIN IMMEDIATE` and rejects duplicate consumption.

Implementation commit:

`7ab6febbe71f8cb9a1f24664a64940bdef7b6d7a`

### Enforcer integration

`DeploymentEnforcer` now accepts an optional shared `BreakGlassUseStore`. When supplied, single-use break-glass consumption is performed against that shared store. Store failure fails closed. Without a supplied store, the older instance-local reference behaviour remains available and must be claimed only at instance scope.

Implementation commit:

`24d231e1a43f118070b3ee011970ca51b2a316d3`

### Hostile test exercised against shared state

The frozen Pass-10 scenarios were then exercised using independent enforcer/coordinator instances sharing the same durable replay database.

Test commit:

`817e161435f2d18c12ac540c0b60a91a21d94571`

## Final verification

Workflow run: `34618609203`

Results:

- HARDEN-001 through HARDEN-009: PASS
- whole-stack hostile passes 1 through 9: PASS
- whole-stack hostile pass 10: PASS

Observed Pass-10 result: 3 passed.

## Permitted bounded claim

Within the declared ASVH reference-harness boundary, an integrity-valid single-use break-glass authority can be consumed through shared durable replay state so that coordinator/enforcer replacement and concurrent enforcer instances do not silently permit the same override to form the simulated consequence twice.

## Explicit non-claims

Pass 10 does **not** demonstrate:

- production distributed consensus or linearizability across independent infrastructure;
- resistance to coherent rollback or replacement of the break-glass replay database itself;
- an external monotonic or cryptographically anchored consumption register;
- production KMS/HSM-backed break-glass signing;
- proof that the named authority identity is entitled to exercise emergency authority;
- closure of all real NHS/EPR alternate execution routes.

A coherent rollback of both the operational replay state and any colocated local state remains outside this claim. Demonstrating that property would require a genuinely independent monotonic trust source or external failure domain rather than another local database layer.
