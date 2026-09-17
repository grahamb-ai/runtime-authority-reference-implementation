# ASVH HARDEN-010 — Post-Remediation Executable Verification

## Status

REFERENCE-MODEL REMEDIATION VERIFIED WITH DECLARED OPEN ARCHITECTURAL RESIDUAL

## Candidate

Branch: `asvh-harden-010-remediation-candidate`

Relevant implementation remediation commit: `fb57f8338c1ea723b06759a5952cce4281b9a57c`

## Environment

Reported local execution environment:

- Windows / win32
- Python 3.13.7
- pytest 9.1.1
- pluggy 1.6.0
- anyio 4.14.2
- pytest-asyncio 1.4.0

These results are local executable evidence. They are not GitHub Actions/CI evidence.

## Post-remediation regression

HARDEN-001 through HARDEN-009 normal and hostile regression suites were rerun after the FR-042 remediation.

Observed result:

```text
199 passed in 2.90s
```

No H1-H9 regression was observed in this local run.

## HARDEN-010 positive verification

`tests/test_asvh_harden_010_final_bind_remediation.py`

Observed after exact-attempt remediation:

```text
10 passed
```

The legitimate complete-bind path and the bounded fail-closed cases represented by that suite remain green.

## HC-H10-FR-039 — Missing attempt identity accepted

Independent pre-remediation evidence showed an empty `attempt_id` was accepted.

Post-remediation probe:

```text
attempt_id = ''
verifier accepts = False
```

Status: REMEDIATED within the reference-model verifier boundary.

## HC-H10-FR-040 — Incomplete consequence bind is digestible

Pre-remediation evidence showed a bind lacking source identity, attestation digest and attempt identity could still produce a digest.

Post-remediation probe:

```text
complete = False
source_id = ''
attestation_digest = ''
attempt_id = ''
ValueError: incomplete consequence bind
```

Status: REMEDIATED within the reference-model bind construction/digest boundary.

## HC-H10-FR-042 — Non-empty attempt identity can substitute for exact attempt binding

First-failure evidence was preserved before remediation. The focused frozen attack suite initially produced:

```text
1 failed, 2 passed
```

The implementation was then changed so `PolicyPositionVerifier` fails closed when `expected_attempt_id` is absent and requires exact equality between observed and expected attempt identity.

The unchanged focused attack suite was rerun:

```text
3 passed
```

The positive final-bind suite subsequently remained 10/10 green and H1-H9 remained 199/199 green.

Status: REMEDIATED within the reference-model verifier boundary.

## HC-H10-FR-041 — Reference callback boundary cannot demonstrate executor bind enforcement

This finding remains deliberately OPEN.

The isolated HR56 attack uses a complete canonical bind, matching source/context/attempt identity and a successful verifier. An executor callback that ignores the supplied bind can still return `COMMITTED`.

Observed isolated hostile result:

```text
bind complete = True
result = COMMITTED
```

and the frozen HR56 pytest remains RED (`1 failed`).

This is not being patched inside the arbitrary Python callback model because doing so would manufacture non-bypassability evidence. Closure requires a structurally enforced execution gateway or concrete EPR integration boundary where consequence formation is conditional on the validated bind and alternate commit routes are excluded or independently tested.

## Claim boundary

The current evidence supports the statement that HARDEN-010 reference-model controls now fail closed on missing/incomplete consequence-time binding material and require exact execution-attempt binding, while preserving H1-H9 regression behaviour in the reported local environment.

It does **not** demonstrate:

- production EPR non-bypassability;
- enforced downstream consumption of a consequence bind;
- absence of alternate EPR commit paths;
- production distributed-system consensus or linearizability;
- real network-partition tolerance;
- cloud failure-domain independence;
- GitHub Actions/CI verification for these reported local runs.

The open HR56/HC-H10-FR-041 result is therefore part of the evidence, not an omitted failure.
