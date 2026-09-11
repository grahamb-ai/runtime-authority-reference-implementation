# ASVH-HARDEN-006 — Hostile Review & Remediation Record

## Frozen baseline

Workflow run `34609918722` completed successfully. HARDEN-001 through HARDEN-005 regressions and frozen HARDEN-006 H6-001..H6-020 all passed.

## Hostile review failure

Workflow run `34610008845`, head `dd905747ee4c7f43ccea926f1d246262d67d2ffd`, preserved four failures:

1. **HC-H6-FR-001 — Durable high-watermark read failure escaped as exception.**
   Recovery uncertainty was not represented explicitly.

2. **HC-H6-FR-002 — Local recovery store replacement resurrected stale authority.**
   After accepting sequence 50, replacing the local watermark database allowed a favourable sequence 2 to become ACTIVE.

3. **HC-H6-FR-003 — Unsupported independence level accepted.**
   A profile declaring level 99 was accepted as ACTIVE despite the harness only supporting bounded reference independence.

4. **HC-H6-FR-004 — Boolean authority counter accepted as integer.**
   Python boolean values were accepted as numeric authority positions.

The hostile suite result was 0 PASS / 4 FAIL. The failures are preserved in GitHub Actions and were not removed or weakened.

## Remediation

Commit `3a1c35c1fd19a2a27ad94ab0874370e131e2ab6e` introduced:

- explicit handling of high-watermark read failure as `INDETERMINATE`;
- dual reference persistence: a local recovery watermark plus a stable sibling anchor database;
- conservative anchor-first writes, so an interrupted local update may leave the anchor ahead but cannot silently restore older authority;
- recovery-store replacement protection inside the reference boundary;
- a maximum demonstrated independence level of L2;
- exact integer type validation for epoch and sequence, excluding booleans;
- local/anchor same-position fingerprint disagreement treated as recovery uncertainty.

The anchor database is a **reference-harness model of an external recovery anchor**. It is not evidence of production isolation, cross-domain cryptographic anchoring, distributed consensus, KMS/HSM trust, or organisational independence.

## Re-verification

Workflow run `34610159244`:

- HARDEN-001 regression — PASS
- HARDEN-002 regression — PASS
- HARDEN-003 regression — PASS
- HARDEN-004 regression — PASS
- HARDEN-005 regression — PASS
- HARDEN-006 frozen CTS — PASS
- HARDEN-006 hostile review — PASS

## Current bounded claim

Within the declared ASVH reference-harness boundary, recovery authority cannot become ACTIVE solely because a local recovery store presents a favourable state. Activation is conditioned on exact active trust-profile identity, authorised authority-service identity, bounded declared independence, valid authority position, and state that is not behind or equivocal with the strongest accepted reference high-watermark. Local recovery-store replacement cannot silently resurrect an older authority state while the reference anchor remains available.

## Non-claims

This does not demonstrate production external cryptographic anchoring, independent infrastructure failure domains, NHS resilience, distributed consensus, production HA, production key management, or organisational independence beyond the bounded reference-harness topology.
