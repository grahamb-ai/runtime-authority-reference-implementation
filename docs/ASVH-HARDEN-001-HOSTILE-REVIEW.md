# ASVH-HARDEN-001 Hostile Review

Status: active review record

Branch: `asvh-harden-001-baseline`

## Purpose

This review challenges whether the current HARDEN-001 test suite actually proves the properties it claims, rather than merely producing green tests.

## Baseline fact

The original frozen CTS implementation (`tests/test_asvh_harden_001.py`) completed successfully in GitHub Actions on 2026-09-11.

That result is preserved. It is not rewritten or withdrawn.

## HR-001 — Concurrent double-use test strength

### Observation

The original H1-012 uses two threads against one shared `ProtectedExecutor` instance. The durable SQLite claim operation is atomic, but the test does not force both workers to begin from independent executor instances or deliberately synchronise their start.

### Risk

A passing test could overstate concurrency resistance if thread scheduling serialises the attempts before durable claim contention occurs.

### Review action

A stronger hostile test now uses two independent `ProtectedExecutor` instances, two independent `BindStore` connections to the same SQLite database, a shared consequence target, and a `threading.Barrier` to align execution start.

### Required property

Exactly one attempt may return `EXECUTED`; exactly one simulated consequence may form; durable final bind state must be `CONSUMED`.

## HR-002 — Forged bind test was too weak

### Observation

The frozen H1-014 only supplies an unknown bind identifier. That demonstrates rejection of a non-existent identifier, but it does not demonstrate authenticity or integrity of a persisted bind.

The current `ProtectedClinicalBind` model contains no signature, MAC, or integrity field, and `BindStore.issue()` accepts any structurally valid `ProtectedClinicalBind` object.

### Attack

An attacker with the ability to insert a fabricated but structurally valid bind into the bind store can supply:

- an invented bind ID;
- an invented receipt ID;
- the correct exact-commit binding hash;
- compatible versions and profiles;
- a valid lifetime.

The current executor validates existence, status, expiry, profiles and commit hash, but does not validate bind provenance or cryptographic/authenticated integrity before claim and execution.

### Expected hostile result

The fabricated stored bind must be rejected as `BIND_INVALID` or `BIND_INTEGRITY_FAILURE` and must not form a consequence.

### Current architectural status

This property is not established by the original green CTS result. The hostile test is intentionally designed to determine whether the current implementation fails this stronger interpretation of H1-014.

## HR-003 — Exact payload recomputation

The document hash is a derived property of `document_content`, and the executor compares the attempted commit's recomputed binding hash with the bound hash. A hostile test retains this property explicitly to ensure a changed clinical document cannot reuse the original authority.

## Evidence discipline

A hostile-review failure is preserved as evidence. It must not be relabelled as success or removed after remediation.

If remediation is introduced, both the failing run and subsequent full regression run must remain identifiable.

## Claim boundary

Until hostile review completes, the permitted claim remains limited to:

> The frozen HARDEN-001 CTS passed on the initial reference implementation.

It is not yet permissible to state that the implementation demonstrates authenticated bind provenance or that the concurrency property has survived the stronger independent-executor challenge.
