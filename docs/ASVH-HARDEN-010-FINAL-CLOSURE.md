# ASVH-HARDEN-010 — Final Evidence-Bounded Closure Record

Status: CLOSED WITHIN DECLARED PYTHON REFERENCE-MODEL BOUNDARY; EXECUTOR/EPR ENFORCEMENT RESIDUAL REMAINS OPEN

This document supersedes `ASVH-HARDEN-010-CLOSURE.md` only as the current status record. Earlier attack freezes, first-failure records, remediation-candidate documents and closure statements are retained unchanged as chronological evidence and must not be read as later verification results.

## Hardened proposition

A technically fresh aggregate standing snapshot is not sufficient for consequence formation where a required underlying authoritative dependency has advanced to conflicting, withdrawn, superseded or indeterminate standing.

A successful convergence result is not itself durable authority to form a consequence. Within the reference model, current policy standing, exact execution-attempt identity and consequence-binding material must remain valid at the modeled consequence boundary.

## Preserved failure-first evidence

HARDEN-010 preserves the hostile record rather than rewriting failed propositions to obtain green results. The preserved findings cover aggregate convergence, multi-source conflict, convergence-to-consequence races, rollback/restart, recovery completeness and provenance, attestation binding, trust-root circularity, trust-policy lifecycle, policy-position provenance/freshness, final-bind continuity and consequence callback enforcement limits.

Later remediation does not erase those first-failure records.

## Current bounded reference controls

The current candidate includes modeled controls for:

- required authoritative-source and subject matching;
- prohibitive and indeterminate fail-closed semantics;
- freshness and impossible-negative-age handling;
- revision high-watermarks and same-revision equivocation handling;
- explicit recovery state/evidence and record-set binding;
- recovery attestation verification and configured trust policy;
- trust-policy revision, standing and digest continuity;
- policy-position source, freshness, context, attestation and exact attempt identity;
- complete consequence-bind construction over policy revision, policy digest, authority epoch, source, attestation digest, context and attempt identity;
- fail-closed verifier/read/bind exceptions; and
- final policy-position reread and bind comparison before invoking the reference consequence callback.

## Executable verification evidence

Reported local environment:

- Windows / win32
- Python 3.13.7
- pytest 9.1.1
- pluggy 1.6.0
- anyio 4.14.2
- pytest-asyncio 1.4.0

These are local executable results, not GitHub Actions/CI evidence.

### H1–H9 post-remediation regression

Observed after the exact-attempt remediation:

```text
199 passed in 2.90s
```

### H10 final-bind remediation verification

```text
10 passed
```

### H10 exact-attempt hostile verification

The focused frozen attack first produced:

```text
1 failed, 2 passed
```

After remediation, the unchanged focused suite produced:

```text
3 passed
```

### H10 whole-chain hostile verification

`tests/test_asvh_harden_010_whole_chain_hostile.py` (HR60–HR72) exercises the bounded chain across authoritative dependency observation, convergence, current policy standing, exact attempt identity, consequence binding, final policy reread and the reference consequence callback.

Observed:

```text
13 passed
```

### Combined bounded positive verification

The H1–H9 normal/hostile regression suites, H10 final-bind remediation suite, H10 exact-attempt suite and H10 whole-chain hostile suite were executed together:

```text
225 passed in 2.81s
```

The deliberately open HR56 executor-enforcement attack is not included in this green aggregate.

## Remediated late findings

- `HC-H10-FR-039` — missing attempt identity accepted: REMEDIATED within the reference verifier boundary.
- `HC-H10-FR-040` — incomplete consequence bind digestible: REMEDIATED within the reference bind boundary.
- `HC-H10-FR-042` — non-empty attempt identity could substitute for exact attempt binding: REMEDIATED and verified by the unchanged focused hostile suite.

## Open architectural residual

`HC-H10-FR-041` / HR56 remains deliberately OPEN and RED.

The isolated attack demonstrates that a complete canonical bind can be supplied to an arbitrary Python consequence callback which ignores that bind and nevertheless returns `COMMITTED`.

Therefore HARDEN-010 does **not** demonstrate that a real EPR executor is structurally forced to consume the validated bind, that alternate commit routes are absent, or that the authority read and EPR write form an atomic/non-bypassable production boundary.

This residual is not to be made green by weakening the hostile proposition, supplying an invalid bind, or asserting callback argument use inside the reference model. It requires evidence at a structurally enforced execution gateway or concrete EPR integration boundary.

## Claim-boundary review

The evidence supports this bounded conclusion:

> Within the tested Python reference-model boundary, HARDEN-010 has executable evidence that required authority dependencies are evaluated fail-closed, current policy standing and exact execution-attempt identity participate in consequence-time binding, and modeled policy/bind changes are detected before the reference consequence callback. The reported combined bounded verification run is 225/225 green.

The evidence does **not** support claims of:

- production EPR non-bypassability;
- enforced downstream consumption of the consequence bind;
- absence of alternate EPR commit routes;
- atomic external authority-read-to-EPR-write semantics;
- production PKI/KMS/HSM trust;
- trusted production time;
- production durable high-watermark storage or crash consistency;
- distributed consensus or linearizability;
- real network-partition tolerance;
- cloud failure-domain independence;
- NHS deployment effectiveness;
- completeness/authenticity of real authority-source hierarchies; or
- GitHub Actions/CI verification for the reported local runs.

## Closure decision

HARDEN-010 is closed as a **bounded reference-model hardening stage**, not as proof of production execution non-bypassability.

Future work on HR56/HC-H10-FR-041 belongs at the execution-gateway/EPR integration boundary. If later work changes the reference mechanism or its claim boundary, HARDEN-010 must be reopened or superseded with new failure-first evidence rather than retroactively altering this record.
