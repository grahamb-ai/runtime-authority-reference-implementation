# ASVH Whole-Stack Hostile Review — Pass 12

## Purpose

Pass 12 tested whether an integrity-valid break-glass artefact could weaken its own replay semantics by declaring `single_use=False` and still be accepted by the deployment boundary.

This is a reference-harness test only. It does not assert production IAM, NHS emergency-authority semantics, external identity truth, production key management, or distributed consensus.

## Frozen hostile scenarios

The frozen Pass 12 suite is `tests/test_asvh_whole_stack_hostile_v12.py`.

- WS12-001 — an integrity-valid break-glass authority carrying `single_use=False` must not form the consequence.
- WS12-002 — a non-single-use authority must not become an open-ended replayable override.
- WS12-003 — a valid integrity-bound single-use break-glass authority remains a positive control.

## Preserved failure

Initial whole-stack run: `34620855647`

The full HARDEN-001 through HARDEN-009 regression suite passed. Whole-stack hostile Passes 1 through 11 also passed. Pass 12 failed 2 of 3 scenarios:

- WS12-001 failed: the signed `single_use=False` authority returned `FORMED`.
- WS12-002 failed: the same non-single-use authority could be accepted as an open-ended override.
- WS12-003 passed.

### Finding

**HC-WS12-FR-001 — Signed replay-semantics downgrade**

The integrity profile correctly bound the `single_use` field, but the deployment enforcer treated `single_use=False` as permission to skip replay consumption rather than as an inadmissible emergency-authority semantic. A validly signed artefact could therefore downgrade the enforcement invariant from one-shot emergency authority to reusable authority.

This was not an integrity failure. It was a policy-composition failure: the verifier proved what had been signed, but the enforcement boundary did not require the signed semantics to satisfy the break-glass policy invariant.

## Remediation

Remediation commit: `90bb4d2002c71627f8533fec832d56bb87ae48fc`

The deployment enforcer now requires `break_glass.single_use is True` before temporal validation or consumption. A signed authority that declares any weaker use semantic is explicitly `PREVENTED`.

For valid break-glass authority, consumption is now unconditional after the explicit single-use check:

- shared `BreakGlassUseStore` when configured; or
- bounded in-instance atomic replay tracking otherwise.

This preserves the distinction between cryptographic/integrity validity and admissible authority semantics: a correctly integrity-bound artefact is not automatically executable if its declared use semantics violate the active break-glass invariant.

## Re-verification

Full re-verification run: `34620970527`

Result:

- HARDEN-001 through HARDEN-009: PASS
- Whole-stack hostile Passes 1 through 11: PASS
- Whole-stack hostile Pass 12: PASS
- Pass 12: 3/3 PASS

## Bounded conclusion

Within the declared ASVH reference-harness boundary, integrity-valid break-glass authority cannot weaken the required single-use execution invariant by declaring reusable semantics. Break-glass authority must be integrity-valid **and** explicitly single-use before it may form the simulated governed consequence.

## Explicit non-claims

Pass 12 does not demonstrate:

- production emergency-access policy;
- external truth that the named authority holder is entitled to invoke break-glass;
- production signing-key isolation;
- resistance to coherent compromise of issuer and verifier;
- production distributed replay protection;
- external monotonic anchoring;
- real NHS/EPR non-bypassability or consequence formation.
