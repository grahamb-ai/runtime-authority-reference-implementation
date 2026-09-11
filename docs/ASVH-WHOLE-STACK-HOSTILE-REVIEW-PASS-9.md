# ASVH Whole-Stack Hostile Review — Pass 9

## Scope

Pass 9 attacks the authenticity and integrity of break-glass authority at the composed whole-stack execution boundary.

This pass does not claim production IAM, hardware-backed signing, HSM/KMS protection, external identity proof, or distributed replay protection. The integrity mechanism is a bounded reference-harness HMAC used to test whether break-glass material can be mutated or fabricated without detection.

## Frozen hostile scenarios

- WS9-001 — unsigned break-glass authority cannot form a consequence.
- WS9-002 — bogus break-glass integrity reference cannot form a consequence.
- WS9-003 — authority identity changed after signing cannot form a consequence.
- WS9-004 — temporal validity changed after signing cannot form a consequence.
- WS9-005 — valid integrity-bound break-glass authority remains usable within the declared reference boundary.

## Preserved failure

Workflow run: `34617754904`

Commit under test: `feb497597d2becefae425af53f6464526a4a17b7`

Result:

- Full HARDEN-001 through HARDEN-009 regression: PASS.
- Whole-stack hostile Passes 1 through 8: PASS.
- Pass 9: **FAIL — 4 failed, 1 passed**.

Observed failures:

1. `WS9-001` — unsigned break-glass authority returned `FORMED`.
2. `WS9-002` — a bogus `BG-HMAC-SHA256-1:deadbeef` integrity value returned `FORMED`.
3. `WS9-003` — changing `authority_identity` after signing returned `FORMED`.
4. `WS9-004` — changing `expires_at` after signing returned `FORMED`.

Positive control `WS9-005` formed as expected.

### Root cause

`BreakGlassAuthority` carried an `integrity_reference` field, but `DeploymentEnforcer` did not verify it. The enforcement path validated deployment, policy version, consequence binding, identity presence and temporal validity, but accepted those fields as caller-supplied structure. Therefore an attacker able to construct or alter the object could fabricate or mutate the break-glass authority and still reach `FORMED`.

Finding: **HC-WS9-FR-001 — BREAK-GLASS AUTHORITY WAS STRUCTURALLY VALIDATED BUT NOT AUTHENTICITY-BOUND.**

## Remediation

Reference-harness remediation added:

- deterministic canonical payload covering:
  - `override_id`
  - `authority_identity`
  - `commit_binding_hash`
  - `deployment_id`
  - `issued_at`
  - `expires_at`
  - `policy_version`
  - `single_use`
- reference HMAC integrity profile `BG-HMAC-SHA256-1`;
- `compute_break_glass_integrity`;
- `sign_break_glass_authority`;
- `verify_break_glass_integrity`;
- fail-closed verification before break-glass authority is accepted by `DeploymentEnforcer`.

The earlier HARDEN-005 conformance fixtures were updated to use integrity-bound break-glass authorities so the strengthened condition is exercised without weakening the prior tests.

Implementation commit: `221da5651cb3574edbcae8d5a2f0fbc92efca3d0`

Fixture updates:

- `e53338b2b5a314b0a3364feb4b7a4a3d216020ad`
- `6e797e9627a8d1767bf620e65a68a7de01382079`

## Final verification

Workflow run: `34618074700`

Head commit: `6e797e9627a8d1767bf620e65a68a7de01382079`

Result:

- HARDEN-001: PASS
- HARDEN-002: PASS
- HARDEN-003: PASS
- HARDEN-004: PASS
- HARDEN-005: PASS
- HARDEN-006: PASS
- HARDEN-007: PASS
- HARDEN-008: PASS
- HARDEN-009: PASS
- Whole-stack hostile Pass 1: PASS
- Pass 2: PASS
- Pass 3: PASS
- Pass 4: PASS
- Pass 5: PASS
- Pass 6: PASS
- Pass 7: PASS
- Pass 8: PASS
- Pass 9: PASS

## Permitted claim

Within the declared ASVH reference-harness boundary, break-glass authority used by the deployment enforcement path is integrity-bound to its authority identity, exact consequence binding, deployment, policy basis, temporal validity and single-use semantics. Unsigned, incorrectly signed, or post-signature-mutated break-glass authority is prevented from silently forming the simulated consequence.

## Explicit non-claims

This pass does **not** demonstrate:

- production cryptographic key management;
- HSM/KMS-backed signing;
- external identity-provider assurance;
- that the claimed break-glass identity is objectively entitled or clinically appropriate;
- cross-service/distributed replay protection for break-glass authority;
- resistance to coherent compromise of both verifier and signing key;
- real NHS EPR route closure or consequence prevention.

Those remain outside the demonstrated claim surface unless separately implemented and verified.
