# ASVH Whole-Stack Hostile Review — Pass 11

## Scope

Pass 11 attacks rollback and replacement of the durable break-glass replay database introduced after Pass 10. The objective is to test whether consumed emergency authority can be silently resurrected by restoring or replacing the operational replay state.

This remains a reference-harness exercise. It does not claim production external monotonic storage, distributed consensus, hardware-backed persistence, or resistance to coherent rollback of every persistence domain.

## Frozen hostile scenarios

- **WS11-001** — restore a coherent pre-consumption copy of the break-glass replay database after an override has formed a consequence; the same override must not form again.
- **WS11-002** — delete and recreate the break-glass replay database after an override has formed a consequence; the same override must not form again.
- **WS11-003** — positive control: untouched durable replay state rejects a second use.

## Failure-first result

Workflow run: **34619311089**

HARDEN-001 through HARDEN-009 and whole-stack hostile Passes 1 through 10 remained green. Pass 11 failed **2 of 3** hostile scenarios:

- **HC-WS11-FR-001 — replay-database rollback resurrected consumed emergency authority.** Restoring a pre-consumption SQLite replay database allowed the same integrity-valid single-use break-glass override to return `FORMED` again.
- **HC-WS11-FR-002 — replay-database replacement resurrected consumed emergency authority.** Deleting and recreating the replay database allowed the same override to return `FORMED` again.

The untouched-state positive control passed.

## Root cause

`BreakGlassUseStore` provided atomic shared consumption only inside one operational SQLite database. The database itself was therefore the sole replay high-watermark. Restoring or replacing that database removed the evidence that the override had already been consumed.

## Remediation

The reference store now pairs the operational replay database with a separate **consumption anchor** database. Consumption is recorded in the anchor before the operational replay record is written.

Properties inside the declared harness boundary:

1. a previously anchored override cannot be consumed again merely because the operational replay database is rolled back;
2. deleting and recreating only the operational replay database does not restore the override;
3. a failure after anchor consumption may conservatively burn the override rather than restore authority;
4. the anchor remains an explicitly bounded reference mechanism, not an external production trust service.

Remediation implementation commit: **004d0c0778952f152e056494bd2fc03116ec94f5**

## Re-verification

Workflow run: **34619405725**

Result:

- HARDEN-001 → HARDEN-009: PASS
- Whole-stack hostile Passes 1 → 10: PASS
- Whole-stack hostile Pass 11: **PASS (3/3)**

## Bounded claim

> Within the declared ASVH reference-harness boundary, rollback or replacement of the operational break-glass replay database alone does not silently resurrect a consumed single-use break-glass authority. Consumption is first recorded against a separate reference anchor, so the operational replay database is not the sole source of replay truth.

## Explicit non-claims

Pass 11 does **not** demonstrate:

- resistance to coherent rollback or replacement of both the replay database and its anchor;
- production external monotonic storage;
- cloud-region or independent administrative failure-domain separation;
- hardware-backed anti-rollback guarantees;
- distributed consensus or linearizability;
- production KMS/HSM break-glass signing;
- proof that the named emergency authority holder is objectively authorised in a real NHS organisation;
- real EPR non-bypassability or consequence formation.

The next meaningful trust-boundary test would require an actually independent monotonic trust source rather than another local SQLite layer. That should be treated as an external integration/property test, not simulated away by adding endless local anchors.
