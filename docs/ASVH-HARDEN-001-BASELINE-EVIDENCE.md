# ASVH-HARDEN-001 Baseline Evidence Record

Status: preserved baseline evidence

Branch: `asvh-harden-001-baseline`

## 1. Frozen CTS baseline

The initial frozen HARDEN-001 conformance suite (`tests/test_asvh_harden_001.py`) completed successfully in GitHub Actions before the hostile-review tests were added.

Initial workflow run:
- workflow: `ASVH HARDEN-001`
- run ID: `34604095680`
- head SHA: `7ab47a98de5be0f09e48d6bd5d3b3707e5b9cadb`
- result: SUCCESS

This result is retained as evidence of what the original frozen CTS established at that point in time.

## 2. Evidence-instrumented rerun

After evidence artifact generation and independent hostile tests were added, the frozen CTS was rerun unchanged as a separate job.

Evidence-instrumented workflow run:
- run ID: `34604659841`
- head SHA: `ef21246363861376a4d1590efbb8564c9747ed3c`
- frozen-conformance job: SUCCESS
- generated evidence: JUnit XML plus machine-readable run manifest

The frozen CTS therefore remained green after evidence instrumentation.

## 3. Hostile review result

The hostile review was run separately from the frozen CTS so that a new challenge could not rewrite the historical baseline result.

Hostile-review job result:
- tests executed: 3
- passed: 2
- failed: 1
- overall hostile-review result: FAIL

### Passed hostile challenges

1. Stronger concurrent double-use challenge using two independent `ProtectedExecutor` instances and independent `BindStore` connections against the same durable SQLite bind state.
   - result: PASS
   - observed property: exactly one governed simulated consequence formed.

2. Changed clinical document challenge confirming document hash is derived from the actual attempted document content and the altered content cannot reuse the old exact-action authority.
   - result: PASS

### Failed hostile challenge

`test_hostile_h1_014_fabricated_persisted_bind_is_rejected`

Expected:
- `BIND_INVALID` or `BIND_INTEGRITY_FAILURE`
- simulated consequence count = 0

Observed:
- executor result = `EXECUTED`

Meaning:

A structurally valid fabricated `ProtectedClinicalBind` inserted into the bind store, containing a forged receipt identifier but a matching Exact Clinical Commit binding, was accepted as execution authority.

This demonstrates that the original H1-014 test proved rejection of an unknown bind identifier only. It did not prove authenticated bind provenance or integrity.

## 4. Failure register

### HC-H1-FR-001 — Fabricated persisted bind accepted

Severity: CRITICAL

Affected properties:
- HC-I34 ALLOW is not itself execution authority
- HC-I44 enforcement independence
- protected-bind provenance/integrity requirement

Observed consequence:
- fabricated stored bind reached `EXECUTED`
- a simulated consequence formed

Root cause at this checkpoint:
- `ProtectedClinicalBind` has no authenticated integrity field;
- `BindStore.issue()` accepts a structurally valid bind without proof it originated from authorised bind issuance;
- `ProtectedExecutor` verifies stored state, expiry, profiles and exact-commit hash, but does not authenticate bind provenance before consumption.

Status: OPEN

## 5. Evidence preservation

The failure is not removed or reclassified.

The following evidence remains distinct:

1. original frozen CTS PASS;
2. evidence-instrumented frozen CTS PASS;
3. hostile review FAIL exposing HC-H1-FR-001.

Any remediation must preserve all three checkpoints and must be followed by:

1. targeted rerun of the failed hostile challenge;
2. complete hostile-review rerun;
3. complete frozen H1-001 through H1-020 regression rerun.

## 6. Current claim boundary

Permitted:

> The frozen HARDEN-001 CTS passes within the reference-harness boundary, including exact-action substitution, expiry, sequential replay and atomic concurrent bind-consumption tests as implemented.

Also permitted:

> A subsequent hostile review identified a critical gap in authenticated Protected Clinical Bind provenance: a fabricated bind persisted directly into the bind store could be accepted as execution authority.

Not permitted:

> Protected Clinical Binds are authenticated or cryptographically provenance-bound.

Not permitted:

> HARDEN-001 is verification-evidenced as complete.

Current status:

`PARTIALLY DEMONSTRATED — CRITICAL HOSTILE-REVIEW FINDING OPEN`
