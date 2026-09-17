# ASVH-HARDEN-010 — Restart/Recovery First-Failure Record

Status: PRESERVED SEMANTIC FAILURE ANALYSIS — EXECUTABLE CI EVIDENCE PENDING

This record is frozen before restart/recovery remediation. It derives the expected results directly from the remediation-candidate implementation and the frozen HR06–HR10 assertions. It is not represented as GitHub Actions evidence.

## Candidate state at attack

The candidate `AuthorityConvergenceState` stores high-watermarks only in an in-memory dictionary. A newly constructed state has no recovery trust marker, no persisted revision floor and no persisted same-revision status binding.

## Expected first-failure matrix

| Test | Frozen proposition | Candidate semantic result | Expected test result |
|---|---|---|---|
| HR06 | restart must not erase revision floor | new state forgets revision 100; replayed 99 evaluates ACTIVE | FAIL |
| HR07 | missing recovery state must not fail open | empty state accepts positive revision 1 and establishes watermark | FAIL |
| HR08 | source alias after restart cannot satisfy declared authority | requirements compare exact source identity; alias mismatches | PASS |
| HR09 | replayed positive cannot override recovered revocation | same in-memory state records revision 110; revision 109 is PREVENTED | PASS |
| HR10 | contradictory status at same authority revision is unresolved | state stores revision only, not status; second revision 120 REVOKED reaches status evaluation and returns PREVENTED | FAIL (expected INDETERMINATE) |

Expected matrix: 3 FAIL / 2 PASS.

## Preserved findings

### HC-H10-FR-004 — Restart erases rollback resistance
Rollback resistance is process-lifetime only. Reconstructing `AuthorityConvergenceState()` erases the revision floor, allowing an older otherwise-positive observation to become ACTIVE.

### HC-H10-FR-005 — Untrusted recovery state can establish authority
The candidate cannot distinguish a legitimate first observation from a process that should have recovered prior authority state but did not. Absence of recovery evidence therefore fails open for a positive dependency.

### HC-H10-FR-006 — Same-revision status equivocation is not remembered
The high-watermark records only revision. If the same authoritative source/subject presents a different status at the same revision, the prior status is unavailable to identify equivocation. A later REVOKED observation becomes PREVENTED rather than explicitly identifying the evidence conflict as INDETERMINATE.

## What already resists the attack

Exact declared source matching prevents the HR08 alias from satisfying the authority requirement. A retained in-process high-watermark prevents HR09 rollback below a newer revocation revision.

## Claim boundary

This analysis demonstrates a reference-model recovery gap. It does not demonstrate a production persistence failure, cryptographic source authentication, durable storage correctness, crash consistency, external registry atomicity, or EPR non-bypassability.
