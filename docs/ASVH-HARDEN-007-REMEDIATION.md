# ASVH-HARDEN-007 — Baseline Failure & Remediation Record

## Status

VERIFICATION-EVIDENCED within the declared reference-harness boundary, subject to the non-claims in ASVH-HARDEN-007-SPEC.

## Preserved baseline run

Workflow run: `34610483182`

Commit under test: `3458dd0e557285dd363add7f56ede3c206bd0a0e`

Result:
- HARDEN-001 regression: PASS
- HARDEN-002 regression: PASS
- HARDEN-003 regression: PASS
- HARDEN-004 regression: PASS
- HARDEN-005 regression: PASS
- HARDEN-006 regression: PASS
- HARDEN-007 frozen CTS: FAIL
- hostile review: SKIPPED because conformance job failed

### Failure H7-FR-001

Test: `H7-019 deterministic rebuild same digest`

Observed failure: the synthetic evidence-pack fixture attempted to create `<tmp>/one/A` and `<tmp>/two/A` without creating parent directories first. Python raised `FileNotFoundError` before the deterministic evidence comparison executed.

Classification: TEST-HARNESS / FIXTURE FAILURE.

This did not demonstrate a failure of the evidence digest algorithm. It demonstrated that the frozen CTS itself was not yet executable for H7-019 under the nested fixture path.

## Remediation

Commit: `c8a9a9f1ebdf59332eced8a195c9feaf3355280a`

Change: the evidence-pack fixture now creates its synthetic test directory with parent creation enabled. No evidence-integrity production logic was altered by this remediation.

## Re-verification

Workflow run: `34610838030`

Results:
- HARDEN-001 regression: PASS
- HARDEN-002 regression: PASS
- HARDEN-003 regression: PASS
- HARDEN-004 regression: PASS
- HARDEN-005 regression: PASS
- HARDEN-006 regression: PASS
- HARDEN-007 frozen H7-001..H7-020 CTS: PASS
- HARDEN-007 hostile review: PASS

Hostile review covered manifest substitution, omission of a failing test from the aggregate root, duplicate-ID shadowing, and path escape from the declared evidence directory.

## Claim boundary

Permitted claim:

> Within the declared ASVH reference-harness boundary, verification evidence can be represented using deterministic SHA-256 manifests that bind protected per-test evidence artefacts and the executed test inventory to an aggregate evidence root. Mutation, omission, duplicate identity, path escape and reproduction mismatch are explicitly detectable by the reference verifier.

Not demonstrated:
- external notarisation or independent timestamping;
- production signing/HSM/KMS custody;
- repository-owner independence;
- long-term archival durability;
- NHS or supplier evidence-store integration;
- proof that external facts captured in an evidence artefact are objectively true.
