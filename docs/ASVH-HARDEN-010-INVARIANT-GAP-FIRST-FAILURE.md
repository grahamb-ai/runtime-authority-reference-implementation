# ASVH HARDEN-010 — Invariant Gap First-Failure Record

## Status

FAILURE-FIRST EVIDENCE PRESERVED — REMEDIATION NOT YET APPLIED

## Candidate under test

Branch: `asvh-harden-010-remediation-candidate`

Initial executable candidate commit: `47f3a4cbf41907148234006e10b01d5b1d2f15a6`

Local environment reported by operator:

- Windows (`win32`)
- Python 3.13.7
- pytest 9.1.1

## Trigger

After the final-bind positive remediation suite passed 10/10, the frozen second-order hostile suite was executed:

`python -m pytest tests/test_asvh_harden_010_final_bind_second_order_attack.py -v`

Observed result: **4 passed / 3 failed**.

The failures were HR53, HR54 and HR55. HR52 passed, but inspection showed that result is not evidence that executor non-bypassability has been demonstrated: the frozen helper constructs an incomplete bind, causing rejection before the injected executor is reached.

## HC-H10-FR-039 — Missing attempt identity accepted

An independent executable probe constructed an otherwise valid `TrustPolicyPosition` without an `attempt_id` and verified it using a `PolicyPositionVerifier` with no `expected_attempt_id` configured.

Observed output:

```text
attempt_id = ''
verifier accepts = True
```

### Finding

The reference verifier can accept a consequence-time policy position that is not bound to a specific execution attempt. Because `bind_from_position()` propagates `p.attempt_id`, an accepted empty attempt identity can propagate into the consequence bind.

## HC-H10-FR-040 — Incomplete consequence bind is digestible

An independent executable probe directly constructed:

`ConsequenceBind(8, 'd8', 20, 'c')`

Observed output:

```text
source_id = ''
attestation_digest = ''
attempt_id = ''
digest = 15808bf8ac3c852d70ebb5a870adb1a4f190b21b05bcb824ec06bb29c0e4a9b1
```

### Finding

The reference type permits a consequence bind with no source identity, no attestation binding and no attempt identity, while still producing a deterministic cryptographic digest. The digest therefore demonstrates integrity of the represented fields, not semantic completeness of the authority bind.

## Construction-path inspection

Repository search showed only two direct `ConsequenceBind` construction paths at this point:

1. `asvh/authority_convergence.py::bind_from_position()` — populates source identity, attestation digest and attempt identity.
2. `tests/test_asvh_harden_010_final_bind_second_order_attack.py::binding()` — frozen hostile helper deliberately uses the older four-field construction.

Repository search for `TrustPolicyPosition` showed the current positive remediation fixture supplies an attempt identity, while frozen hostile/earlier attack fixtures omit it.

## Interpretation

These findings must not be closed by merely editing the frozen hostile fixtures. They expose an invariant distinction between a hardened factory path and permissive underlying object/verifier semantics.

The remediation target is therefore the implementation invariant: consequence-time policy positions and consequence binds used for execution must not be accepted as complete when security-critical binding fields are absent.

## HR52 limitation

The observed HR52 PASS is **not** evidence of production executor-bind enforcement or EPR-route non-bypassability. In the frozen test, the incomplete expected bind is rejected before the arbitrary executor callback is invoked. The previously declared architectural residual therefore remains open unless a later isolated test demonstrates otherwise.

## Claim boundary

This record is local executable evidence against the declared Python reference model only. It is not GitHub Actions/CI evidence and does not demonstrate production EPR non-bypassability, atomic policy-read/EPR-write, production PKI/KMS/HSM, trusted time, distributed consensus or NHS deployment behaviour.
