# ASVH-HARDEN-007 — Evidence Pack Integrity & Reproducibility

Status: FROZEN DESIGN — IMPLEMENTATION PENDING

## 1. Purpose

HARDEN-007 tests whether a third party can establish what code, tests, policy/profile inputs and evidence artefacts were used in a verification run, detect subsequent mutation or omission, and reproduce the recorded suite result within the declared reference-harness boundary.

This hardening stage does not strengthen the clinical decision logic itself. It strengthens the evidential basis for claims made from verification runs.

## 2. Non-claims

HARDEN-007 does not demonstrate production notarisation, external timestamping, hardware-backed signing, NHS deployment, real EPR consequence formation, long-term archival durability, or independence of the evidence repository from the repository owner.

## 3. Evidence Run Identity

Every evidence-producing run SHALL have a unique `run_id` and SHALL bind at minimum:

- repository identifier;
- git commit SHA;
- git ref;
- workflow identifier/version;
- Python/runtime version;
- conformance suite identifier/version;
- applicable policy/rule/profile versions;
- start/completion timestamps supplied by the harness evidence clock;
- declared claim boundary;
- ordered test inventory;
- final suite status.

## 4. Per-test Evidence Pack

Each test SHALL produce a directory keyed by stable test ID. The pack SHALL contain, where applicable:

- `test-definition.json`
- `inputs.json`
- `observations.json`
- `result.json`
- `artefact-manifest.json`

Absent expected artefacts SHALL be represented explicitly as `null`/`ABSENT`; they SHALL NOT silently disappear from the evidence contract.

## 5. Artefact Manifest

Each evidence file SHALL be represented by:

- relative path;
- media/type identifier;
- byte length;
- SHA-256 digest.

The manifest SHALL use deterministic ordering and deterministic JSON serialisation. The manifest itself SHALL have a SHA-256 digest recorded in the run manifest.

## 6. Run Manifest

The run manifest SHALL contain the per-test manifest digests and an aggregate evidence-root digest. The aggregate digest SHALL be deterministically derived from the ordered `(test_id, manifest_digest)` pairs.

A change to any protected evidence artefact, test manifest, test inventory, or ordering SHALL change the aggregate evidence-root digest.

## 7. Completeness

A suite SHALL NOT be reported as `VERIFICATION-EVIDENCED` if:

- a required test pack is absent;
- a required evidence artefact is absent without explicit representation;
- a digest does not verify;
- the executed test inventory differs from the frozen expected inventory;
- duplicate test IDs exist;
- a test result is missing or malformed;
- the run commit/ref or suite version is unknown.

Permitted suite evidence statuses are:

- `COMPLETE`
- `INCOMPLETE`
- `INTEGRITY_FAILURE`
- `REPRODUCTION_MISMATCH`

## 8. Reproduction Record

A reproduction run SHALL record:

- source evidence run ID;
- source git SHA;
- reproducing git SHA;
- suite version;
- environment/runtime facts;
- observed ordered test inventory;
- observed per-test outcomes;
- observed aggregate evidence-root digest;
- comparison status.

A reproduction SHALL NOT be described as identical merely because all tests pass. It must distinguish outcome reproduction from byte-for-byte evidence reproduction.

## 9. Failure Preservation

A failed baseline, hostile test, integrity check or reproduction attempt SHALL remain preserved. Later successful evidence SHALL reference rather than replace the earlier failure.

## 10. Frozen Conformance Tests

H7-001 valid complete evidence pack verifies.
H7-002 mutation of a protected evidence file is detected.
H7-003 deletion of a required evidence file produces INCOMPLETE.
H7-004 silently omitted null/absent artefact produces INCOMPLETE.
H7-005 changed test result changes test-manifest digest.
H7-006 changed test inventory changes evidence-root digest.
H7-007 reordered inventory cannot silently preserve evidence root.
H7-008 duplicate test ID is rejected.
H7-009 missing expected test ID is rejected.
H7-010 unexpected test ID is explicitly surfaced.
H7-011 wrong git SHA is detected during reproduction comparison.
H7-012 wrong suite version is detected.
H7-013 malformed manifest is rejected.
H7-014 unsupported digest algorithm is rejected.
H7-015 digest comparison is performed over bytes actually stored.
H7-016 passing JUnit with incomplete evidence cannot become COMPLETE.
H7-017 failed test remains represented in aggregate evidence.
H7-018 reproduction with same outcomes but different evidence root is REPRODUCTION_MISMATCH, not identical.
H7-019 deterministic rebuild of the same synthetic evidence produces the same manifest/root digest.
H7-020 aggregate COMPLETE requires every frozen conformance test to have a complete, integrity-valid evidence pack.

## 11. Hostile Review Targets

The hostile suite SHALL attempt at least:

1. evidence mutation after result generation;
2. manifest substitution;
3. omitted failing test;
4. duplicate-ID shadowing;
5. JUnit/result disagreement;
6. forged aggregate root assembled from unverified child manifests;
7. path traversal or evidence path escaping the declared run directory;
8. outcome-only reproduction incorrectly represented as identical evidence reproduction.

## 12. Exit Gate

HARDEN-007 may be described as `VERIFICATION-EVIDENCED` only when H7-001 through H7-020 pass, hostile review passes, all evidence is retained, and the claim boundary remains explicit.

Permitted claim after successful completion:

> Within the declared ASVH reference-harness boundary, verification runs produce deterministic, integrity-checkable evidence manifests binding the executed test inventory and per-test evidence artefacts to the source commit and suite version. Mutation, omission and reproduction mismatch are explicitly detectable.
