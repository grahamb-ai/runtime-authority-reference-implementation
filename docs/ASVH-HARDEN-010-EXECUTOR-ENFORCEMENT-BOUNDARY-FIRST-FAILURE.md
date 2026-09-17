# ASVH HARDEN-010 — Executor Enforcement Boundary First-Failure

## Status

OPEN ARCHITECTURAL RESIDUAL — FAILURE PRESERVED

## Hostile proposition

HR56 asks whether a complete, canonical, successfully revalidated consequence bind can nevertheless be ignored by the injected downstream executor.

Unlike historical HR52, this isolated test does not use an incomplete legacy bind. The policy position includes source identity, attestation, observation context and execution-attempt identity; the verifier expects the same attempt identity; and the bind is produced through `bind_from_position()`.

## Executable result

Test:

`tests/test_asvh_harden_010_executor_enforcement_boundary_attack.py`

Local command:

`python -m pytest tests/test_asvh_harden_010_executor_enforcement_boundary_attack.py -v`

Observed result: **1 failed**.

An independent probe immediately before the frozen test also established:

```text
bind complete = True
result = COMMITTED
```

The executor callback deliberately ignored the bind it received and returned `COMMITTED`.

## Finding

### HC-H10-FR-041 — Reference callback boundary cannot demonstrate executor bind enforcement

The reference implementation can verify that the policy position is acceptable at final bind, construct a complete consequence bind, reread and compare that bind immediately before callback invocation, and pass the verified bind to the executor.

It cannot, through the current arbitrary callback interface, demonstrate that the downstream consequence-forming component actually enforces that bind or that no alternate commit path exists.

This is therefore an execution-boundary / non-bypassability property, not a further policy-position hashing problem.

## Required claim boundary

HR56 must not be made green by weakening the hostile proposition, by making the test use an invalid bind, or by adding a reference-only assertion that an arbitrary callback 'used' its argument.

Closing this finding requires evidence from a structurally enforced execution gateway or concrete EPR integration boundary in which consequence formation is conditional on the validated bind and bypass routes are excluded or independently tested.

Until such evidence exists, HARDEN-010 may claim final-bind verification within the Python reference model, but must not claim production EPR non-bypassability or enforced downstream bind consumption.

## Evidence scope

This is local executable evidence on the reported Windows / Python 3.13.7 / pytest 9.1.1 environment. It is not GitHub Actions/CI evidence and is not evidence from a live NHS EPR integration.
