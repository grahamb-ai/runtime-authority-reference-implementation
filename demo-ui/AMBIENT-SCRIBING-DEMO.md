# Ambient Scribing Runtime Authority Demo

Open `ambient-scribing.html` in a browser. It is a visual companion to AIRP-002/006/008/009, not a replacement for the executable tests.

## Evidence contract

The UI mirrors the current protected-gateway contract in `asvh/execution_authority.py`:
- consequence-time standing reader is mandatory;
- reader failure/absence fails closed;
- only exact typed `ConvergenceResult.ACTIVE` permits the represented commit;
- PREVENTED, INDETERMINATE, null and plain string `"ACTIVE"` are blocked.

The scenario labels and preserved-history panel are grounded in the frozen AIRP tests/evidence. The UI does **not** claim to execute against a production EPR, prove external source authenticity/freshness, prove independently administered identity/key trust, or prove physical consequence non-formation.

## Demo path

1. Current standing ACTIVE → attempt commit → represented sink COMMITTED.
2. Standing withdrawn → attempt commit → BLOCKED; represented EPR unchanged.
3. Earlier capability → show that the T0 capability remains present but T1 PREVENTED blocks the protected path (AIRP-008 current behavior).
4. Standing dependency → select each AIRP-009 case; only exact typed ACTIVE commits.
5. Point to preserved engineering history and the external-boundary RED.

For evidential review, return to AIRP-012/013 and the preserved GitHub Actions run 35500425335.
