# ASVH Whole-Stack Hostile Review — Pass 4

## Scope

Pass 4 attacked the evidential basis of whole-stack composition. Passes 1–3 had established status composition and cross-layer identity coherence, but the final coordinator could still accept caller-supplied upstream status and identity values without requiring integrity-bound, producer-bound, fresh evidence for those values.

## Preserved hostile failure

Workflow run `34614682966` preserved the pre-remediation result.

HARDEN-001 through HARDEN-009 remained green. Whole-stack passes 1, 2 and 3 also remained green. Pass 4 failed 10 of 11 frozen attacks; the valid positive control passed.

Observed failures showed that simulated consequence formation could still occur with:

- no layer evidence;
- forged layer-evidence integrity;
- a signed layer status contradicting the naked context status;
- one required layer omitted while other layers were present;
- duplicate/shadowing evidence for the same layer;
- producer substitution by the requesting AI;
- signed evidence bound to a different consequence;
- stale signed composition evidence;
- future-dated composition evidence; or
- break-glass combined with forged layer evidence.

## Finding

**WS-FR-004 — Caller-asserted upstream status could bypass composition-evidence integrity.**

The whole-stack coordinator had become status-aware and identity-aware, but not evidence-authoritative. That left a gap between “the context says this layer is green” and “the layer produced current, integrity-valid evidence that it is green for this exact consequence.”

## Remediation

Commit `14a824c8ff7e99e28c490cc35b0ddca46f884be5` added reference-harness `LayerAuthorityEvidence` records and final-boundary verification.

The coordinator now requires an exact set of layer records for distributed authority, recovery authority, evidence contract, policy transition and present standing. Each record must be:

- unique by layer;
- produced by the expected reference producer;
- integrity-valid under the harness HMAC mechanism;
- bound to the active deployment;
- bound to the Exact Clinical Commit hash;
- status-consistent with the composed context;
- temporally parseable;
- not future-dated; and
- no older than the declared 30-second reference freshness window.

The HMAC is a reference-only tamper-detection mechanism. It is not a production cryptographic trust claim.

## Fixture adaptation discovered during re-verification

The first remediation re-run, workflow `34614813589`, kept HARDEN-001 through HARDEN-009 green but exposed a legacy pass-2 fixture inconsistency. Two break-glass tests changed naked recovery/evidence statuses with `dataclasses.replace()` while leaving their newly signed layer evidence at the previous status. The coordinator correctly stopped at `COMPOSITION_EVIDENCE` rather than the older expected decisive layer.

This did not require weakening the production logic. Commit `472dde3a9a5de5c9445c6c5aac2514069da8e388` aligned those frozen test fixtures with the signed evidence model by constructing the requested recovery/evidence status through the shared context helper.

## Final re-verification

Workflow run `34614985980` completed successfully.

Result:

- HARDEN-001 through HARDEN-009: PASS
- WS-001 through WS-016: PASS
- WS2-001 through WS2-008: PASS
- WS3-001 through WS3-011: PASS
- WS4-001 through WS4-011: PASS

## Bounded conclusion

Within the declared ASVH reference-harness boundary, upstream layer results accepted by the whole-stack execution coordinator must be complete, unique, producer-bound, deployment-bound, exact-consequence-bound, fresh, status-consistent and integrity-valid before they can contribute to simulated consequence formation.

## Explicit non-claims

This does not establish production PKI, HSM-backed signing, external attestation, independent trust-domain isolation, NHS deployment identity, real EPR route closure, distributed transaction atomicity, or objective truth of the underlying evidence. Those remain outside the demonstrated claim surface.
