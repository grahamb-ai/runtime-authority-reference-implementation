# ASVH-HARDEN-010 — Executable First Run

Status: PRESERVED FIRST EXECUTABLE FAILURE

Candidate tested: `8117bb9` (`asvh-harden-010-remediation-candidate`)
Environment reported by operator: Windows; Python 3.13.7; pytest 9.1.1.
Command: `python -m pytest tests/test_asvh_harden_010_final_bind_remediation.py -v`
Result: **1 failed, 9 passed**.

Failure: `test_r11_valid_final_bind_executes` expected `COMMITTED` but received `ConvergenceResult.INDETERMINATE`.

## Analysis

This is a remediation-verification fixture drift, not a reason to weaken the final bind. The positive-test helper constructs `ConsequenceBind` using the earlier four-field binding shape. The implementation was subsequently hardened so the canonical bind also covers policy source identity, attestation digest and attempt identity. The final re-read therefore correctly produces a different digest and fails closed.

The failure is preserved before correction. The correction must update only the positive remediation fixture to construct the canonical bind from the policy position. Frozen hostile tests are not to be altered.
