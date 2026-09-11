# ASVH Whole-Stack Hostile Review — Pass 7

## Scope

Pass 7 attacked the explicit limitation left by Pass 6: the single-use replay fence was coordinator-instance local and therefore did not survive coordinator replacement or protect two separate coordinators from claiming the same bind.

## Preserved hostile failure

Workflow run `34616103727` preserved the pre-remediation result.

HARDEN-001 through HARDEN-009 and whole-stack passes 1–6 remained green. Pass 7 failed 2 of 3 frozen attacks; the distinct-bind positive control passed.

Observed failures showed that:

- the same Protected Clinical Bind could return `FORMED` again after constructing a new coordinator; and
- two separate coordinators could concurrently use the same bind and both return `FORMED`.

## Finding

**WS-FR-007 — Coordinator-local replay state did not provide cross-instance or restart-safe single-use semantics.**

The Pass-6 in-memory claim closed replay only inside one coordinator instance. That was intentionally bounded, but it remained insufficient for a deployment in which execution coordinators can restart or run concurrently.

## Remediation

Commit `d1a4a26eadd2f0b160a7099e35993d65cec9334a` added an optional shared `BindStore` to the whole-stack coordinator. When configured, the normal ALLOW path verifies that the supplied bind exactly matches the durable stored bind and uses the existing SQLite `BEGIN IMMEDIATE` / conditional `ISSUED -> CLAIMED` transition as the atomic single-use claim.

Commit `df5c1d3c4784d181da3f55d92bb80eec75f11851` updated the Pass-7 tests to exercise that configured shared state directly:

- a new `BindStore` object and new coordinator over the same database model coordinator restart;
- two separate coordinators use separate `BindStore` objects over the same database to test concurrent claim; and
- two distinct binds remain independently usable.

The earlier failing run remains preserved and was not rewritten.

## Final re-verification

Workflow run `34616323598` completed successfully.

Result:

- HARDEN-001 through HARDEN-009: PASS
- Whole-stack Passes 1–6: PASS
- WS7-001 through WS7-003: PASS

## Bounded conclusion

Within the declared ASVH reference-harness boundary, when multiple whole-stack coordinators are configured against the same durable `BindStore`, the same Protected Clinical Bind cannot be successfully claimed twice across coordinator replacement or concurrent coordinator instances. Distinct valid binds remain independently claimable.

## Explicit non-claims

The demonstrated shared claim store is SQLite reference-harness persistence. It does not establish production distributed consensus, replicated-store durability, protection against coherent rollback or replacement of the claim database, external cryptographic anchoring, multi-region linearizability, production transaction atomicity, or real EPR non-bypassability. Those remain separate properties requiring further evidence.
